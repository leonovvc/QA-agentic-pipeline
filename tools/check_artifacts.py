#!/usr/bin/env python3
"""Check the documents a QA pipeline run produced against the artifact contract.

The contract (skills/run-qa-pipeline/references/artifact-contract.md) fixes IDs,
sections, and case fields so that traceability can be verified by a program instead of
by reading. This script is that program. It checks whatever stages are present in a
task directory, or exactly the stages you ask for:

    python tools/check_artifacts.py docs/qa/<task-id>
    python tools/check_artifacts.py docs/qa/<task-id> --stages 1,2 --state docs/qa/pipeline-state/<task-id>.json
    python tools/check_artifacts.py <dir> --json

English and Russian headings / field labels are both accepted (see the contract).
Exit code 0 when every applicable check passes, 1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

# --- vocabulary ----------------------------------------------------------------------

HEADINGS = {
    # stage 1 — spec-gap-report.md
    "source": ["Source", "Источник"],
    "testability": ["Testability Score", "Оценка тестируемости"],
    "inventory": ["Requirements Inventory", "Перечень требований"],
    "blocking": ["Blocking Gaps", "Блокирующие пробелы"],
    "contradictions": ["Contradictions", "Противоречия"],
    "questions": ["Open Questions", "Открытые вопросы"],
    "assumptions": ["Assumptions Made to Proceed", "Assumptions", "Допущения"],
    "security": ["Security Lens", "Безопасность"],
    "ready": ["Ready-for-Test-Design Checklist", "Готовность к тест-дизайну"],
    # stage 2 — test-plan.md
    "scope": ["Scope", "Объём", "Объем"],
    "risk": ["Risk Assessment", "Оценка рисков"],
    "matrix": ["Traceability Matrix", "Матрица трассировки"],
    "pyramid": ["Pyramid Allocation", "Распределение по пирамиде"],
    "criteria": ["Entry and Exit Criteria", "Критерии входа и выхода"],
    "location": ["Case Location", "Где лежат кейсы"],
    # stage 3 — autotest-summary.md
    "stack": ["Stack Profile", "Профиль стека"],
    "mapping": ["Mapping", "Соответствие кейсов и тестов"],
    "commands": ["Commands Run", "Выполненные команды"],
    "defects": ["Suspected Product Defects", "Предполагаемые дефекты продукта"],
    "disagreements": ["Allocation Disagreements", "Несогласие с распределением"],
    # stage 4 — qa-review-report.md
    "trace_summary": ["Traceability Summary", "Сводка трассировки"],
    "findings": ["Findings", "Замечания"],
    "disputed": ["Disputed", "Спорное"],
    "readability": ["Readability", "Читаемость"],
}
REQUIRED_SECTIONS = {
    "spec-gap-report.md": ["source", "testability", "inventory", "blocking", "contradictions",
                           "questions", "assumptions", "security", "ready"],
    "test-plan.md": ["scope", "assumptions", "risk", "matrix", "pyramid", "criteria", "location"],
    "autotest-summary.md": ["stack", "mapping", "commands", "defects", "disagreements"],
    "qa-review-report.md": ["trace_summary", "findings", "disputed", "readability"],
}
CASE_FIELDS = {
    "traces": ["Traces", "Трассировка"],
    "technique": ["Technique", "Техника"],
    "level": ["Level", "Уровень"],
    "priority": ["Priority", "Приоритет"],
    "preconditions": ["Preconditions", "Предусловия"],
    "test_data": ["Test data", "Тестовые данные"],
    "steps": ["Steps", "Шаги"],
    "expected": ["Expected result", "Ожидаемый результат"],
}
LEVEL_WORDS = {
    "UNIT": ["unit", "юнит", "модульн"],
    "API": ["api", "integration", "интеграц"],
    "E2E": ["e2e", "end-to-end", "сквозн"],
    "MAN": ["manual", "exploratory", "ручн", "исследоват"],
}
LEVEL_FILES = {"UNIT": "test-cases-unit.md", "API": "test-cases-api.md",
               "E2E": "test-cases-e2e.md", "MAN": "test-cases-manual.md"}
STATUSES = {"passed", "failed", "not run", "manual"}
SEVERITIES = {"blocking", "major", "minor", "блокирующее", "блокирующий", "существенное",
              "существенный", "незначительное", "незначительный"}
VAGUE_EXPECTED = re.compile(
    r"verify it works|works correctly|looks right|is fine|everything works|no problems|"
    r"работает корректно|работает правильно|всё работает|все работает|отображается правильно|"
    r"отображается корректно", re.I)
CYRILLIC = re.compile(r"[А-Яа-яЁё]")

REQ = re.compile(r"\bREQ-(\d+)\b")
QID = re.compile(r"\bQ(\d+)\b")
AID = re.compile(r"\bA(\d+)\b")
TCID = re.compile(r"\bTC-(UNIT|API|E2E|MAN)-(\d{3})\b")


# --- result model --------------------------------------------------------------------

@dataclass
class Check:
    stage: int
    name: str
    passed: bool
    detail: str = ""


@dataclass
class Result:
    task_dir: str
    checks: list[Check] = field(default_factory=list)

    def add(self, stage: int, name: str, passed: bool, detail: str = "") -> bool:
        self.checks.append(Check(stage, name, bool(passed), detail))
        return bool(passed)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)

    def summary(self) -> dict:
        by_stage: dict[int, dict[str, int]] = {}
        for c in self.checks:
            s = by_stage.setdefault(c.stage, {"passed": 0, "failed": 0})
            s["passed" if c.passed else "failed"] += 1
        return {"task_dir": self.task_dir, "passed": self.passed,
                "total": len(self.checks), "failed": sum(not c.passed for c in self.checks),
                "by_stage": by_stage, "checks": [asdict(c) for c in self.checks]}


# --- markdown helpers ----------------------------------------------------------------

def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().strip("*").strip()).lower()


def sections(md: str) -> dict[str, str]:
    """Map of level-2 heading text -> body (until the next level-2 heading)."""
    out: dict[str, str] = {}
    parts = re.split(r"^## +(.+?)\s*$", md, flags=re.M)
    for i in range(1, len(parts), 2):
        out[parts[i].strip()] = parts[i + 1]
    return out


def find_section(secs: dict[str, str], key: str) -> str | None:
    for heading, body in secs.items():
        h = norm(heading)
        for alias in HEADINGS[key]:
            if h.startswith(alias.lower()):
                return body
    return None


def table_rows(body: str) -> list[list[str]]:
    rows = []
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("|") or re.match(r"^\|[\s:|-]+\|$", line):
            continue
        rows.append([c.strip() for c in line.strip("|").split("|")])
    return rows[1:] if rows else []  # drop header row


def ids(pattern: re.Pattern, text: str) -> set[str]:
    return {m.group(0) for m in pattern.finditer(text)}


def defined_ids(body: str | None, pattern: re.Pattern) -> set[str]:
    """IDs that open an entry: '**Q3** — …', '1. **Q3** …', '- **A2** …', '| Q3 |'."""
    if not body:
        return set()
    found = set()
    for line in body.splitlines():
        m = re.match(r"^\s*(?:[-*]|\d+\.)?\s*\**\s*\[?(" + pattern.pattern + r")\]?\**", line)
        if m:
            found.add(re.search(pattern, line).group(0))
        cells = [c.strip(" *") for c in line.strip().strip("|").split("|")] if line.strip().startswith("|") else []
        if cells and re.fullmatch(pattern, cells[0]):
            found.add(cells[0])
    return found


# --- per-stage checks ----------------------------------------------------------------

def check_sections(res: Result, stage: int, fname: str, md: str) -> dict[str, str]:
    secs = sections(md)
    missing = [HEADINGS[k][0] for k in REQUIRED_SECTIONS[fname] if find_section(secs, k) is None]
    res.add(stage, f"{fname}: required sections present", not missing,
            "missing: " + ", ".join(missing) if missing else "")
    return secs


def check_stage1(res: Result, d: Path) -> dict:
    ctx: dict = {"reqs": {}, "qs": set(), "as": set()}
    for f in ("spec-source.md", "spec-gap-report.md", "spec-annotated.md"):
        res.add(1, f"{f} exists", (d / f).exists())
    if not (d / "spec-gap-report.md").exists():
        return ctx
    report = (d / "spec-gap-report.md").read_text()
    secs = check_sections(res, 1, "spec-gap-report.md", report)

    score = re.search(r"^## .*?(?:Testability Score|Оценка тестируемости)\s*:?\s*(\d)", report, re.M)
    res.add(1, "testability score is 1-5", bool(score) and 1 <= int(score.group(1)) <= 5,
            score.group(0) if score else "no score in heading")

    inv = find_section(secs, "inventory") or ""
    rows = [r for r in table_rows(inv) if r and REQ.fullmatch(r[0].strip("* "))]
    reqs = {r[0].strip("* "): r for r in rows}
    ctx["reqs"] = reqs
    res.add(1, "requirements inventory has REQ rows", len(reqs) > 0, f"{len(reqs)} REQs")
    nums = sorted(int(k.split("-")[1]) for k in reqs)
    res.add(1, "REQ IDs are unique and sequential from 1", nums == list(range(1, len(nums) + 1)),
            f"found {nums}")
    bad_loc = [k for k, r in reqs.items() if len(r) < 5 or not r[1].strip(" -—")]
    res.add(1, "every REQ row has a spec location and all five columns", not bad_loc, ", ".join(bad_loc))

    qs: set[str] = set()
    for key in ("blocking", "contradictions", "questions"):
        qs |= defined_ids(find_section(secs, key), QID)
    as_ = defined_ids(find_section(secs, "assumptions"), AID)
    ctx["qs"], ctx["as"] = qs, as_
    q_in_blocking = defined_ids(find_section(secs, "blocking"), QID)
    q_in_contra = defined_ids(find_section(secs, "contradictions"), QID)
    res.add(1, "Q numbering is one global sequence (no ID reused across sections)",
            not (q_in_blocking & q_in_contra), ", ".join(sorted(q_in_blocking & q_in_contra)))

    dangling = []
    for k, r in reqs.items():
        testable = r[-1].lower()
        if re.search(r"\b(no|partly)\b|нет|частично", testable) and not re.search(r"\byes\b|^да\b", testable):
            refs = ids(QID, r[-1])
            if not refs or not refs <= qs:
                dangling.append(k)
    res.add(1, "every non-testable REQ points at an existing Q", not dangling, ", ".join(dangling))

    sec_body = find_section(secs, "security") or ""
    res.add(1, "security lens section is filled (findings or 'not applicable')",
            len(sec_body.strip()) > 10)

    if (d / "spec-annotated.md").exists():
        ann = (d / "spec-annotated.md").read_text()
        markers_q = {m.group(1) for m in re.finditer(r"\[(Q\d+)\b", ann)}
        markers_a = {m.group(1) for m in re.finditer(r"\[(A\d+)\b", ann)}
        res.add(1, "every Q in the report has an inline marker", qs <= markers_q,
                "missing markers: " + ", ".join(sorted(qs - markers_q)))
        res.add(1, "every inline Q marker exists in the report", markers_q <= qs,
                "unknown markers: " + ", ".join(sorted(markers_q - qs)))
        res.add(1, "every A in the report has an inline marker", as_ <= markers_a,
                "missing markers: " + ", ".join(sorted(as_ - markers_a)))
    return ctx


def parse_cases(md: str) -> dict[str, dict]:
    cases = {}
    blocks = re.split(r"^### +", md, flags=re.M)
    for b in blocks[1:]:
        head, _, body = b.partition("\n")
        m = TCID.search(head)
        if not m:
            continue
        fields: dict[str, str] = {}
        current = None
        for line in body.splitlines():
            fm = re.match(r"^\s*-\s+\*\*(.+?):?\*\*:?\s*(.*)$", line)
            if fm:
                label = norm(fm.group(1)).rstrip(":")
                current = next((k for k, al in CASE_FIELDS.items() if label in [a.lower() for a in al]), None)
                if current:
                    fields[current] = fm.group(2).strip()
                    continue
            if current and line.strip():
                fields[current] = (fields[current] + "\n" + line.strip()).strip()
        cases[m.group(0)] = {"title": head.strip(), "fields": fields, "level_code": m.group(1)}
    return cases


def check_stage2(res: Result, d: Path, ctx: dict) -> dict:
    reqs: dict = ctx.get("reqs", {})
    res.add(2, "test-plan.md exists", (d / "test-plan.md").exists())
    plan = (d / "test-plan.md").read_text() if (d / "test-plan.md").exists() else ""
    secs = check_sections(res, 2, "test-plan.md", plan) if plan else {}

    case_files = {lvl: d / f for lvl, f in LEVEL_FILES.items() if (d / f).exists()}
    res.add(2, "at least one test-cases-<level>.md exists", bool(case_files), ", ".join(p.name for p in case_files.values()))
    cases: dict[str, dict] = {}
    for lvl, path in case_files.items():
        parsed = parse_cases(path.read_text())
        res.add(2, f"{path.name} is not empty", bool(parsed))
        wrong_file = [c for c, v in parsed.items() if v["level_code"] != lvl]
        res.add(2, f"{path.name}: every case ID matches the file's level", not wrong_file, ", ".join(wrong_file))
        cases.update(parsed)
    ctx["cases"] = cases
    res.add(2, "test cases found", bool(cases), f"{len(cases)} cases")

    missing_fields = {c: [CASE_FIELDS[k][0] for k in CASE_FIELDS if not v["fields"].get(k)]
                      for c, v in cases.items()}
    missing_fields = {c: m for c, m in missing_fields.items() if m}
    res.add(2, "every case has all eight fields, non-empty", not missing_fields,
            "; ".join(f"{c}: {', '.join(m)}" for c, m in list(missing_fields.items())[:10]))

    level_mismatch = []
    for c, v in cases.items():
        lvl_text = v["fields"].get("level", "").lower()
        if lvl_text and not any(w in lvl_text.split("—")[0].split(" - ")[0] for w in LEVEL_WORDS[v["level_code"]]):
            level_mismatch.append(c)
    res.add(2, "Level field agrees with the level code in the ID", not level_mismatch, ", ".join(level_mismatch))

    no_just = [c for c, v in cases.items()
               if v["fields"].get("level") and not re.search(r"[—–:-]\s*\S", v["fields"]["level"])]
    res.add(2, "Level field carries a justification", not no_just, ", ".join(no_just))

    bad_traces, unknown = [], []
    traced: set[str] = set()
    for c, v in cases.items():
        t = v["fields"].get("traces", "")
        refs = ids(REQ, t)
        traced |= refs
        if not refs and not (v["level_code"] == "MAN" and ids(QID, t)):
            bad_traces.append(c)
        unknown += [f"{c}→{r}" for r in refs if reqs and r not in reqs]
    res.add(2, "every case traces to at least one REQ", not bad_traces, ", ".join(bad_traces))
    res.add(2, "every traced REQ exists in the inventory", not unknown, ", ".join(unknown[:10]))

    bad_prio = [c for c, v in cases.items() if not re.search(r"\bP[0-3]\b", v["fields"].get("priority", ""))]
    res.add(2, "every case has priority P0-P3", not bad_prio, ", ".join(bad_prio))

    vague = [c for c, v in cases.items() if VAGUE_EXPECTED.search(v["fields"].get("expected", ""))]
    res.add(2, "no vague expected results ('works correctly', 'всё работает', …)", not vague, ", ".join(vague))

    if plan:
        risk_rows = {r[0].strip("* "): r for r in table_rows(find_section(secs, "risk") or "") if r and REQ.fullmatch(r[0].strip("* "))}
        matrix_rows = {r[0].strip("* "): r for r in table_rows(find_section(secs, "matrix") or "") if r and REQ.fullmatch(r[0].strip("* "))}
        if reqs:
            res.add(2, "risk assessment has a row for every REQ", set(reqs) <= set(risk_rows),
                    "missing: " + ", ".join(sorted(set(reqs) - set(risk_rows), key=lambda x: int(x[4:]))))
            res.add(2, "traceability matrix has a row for every REQ", set(reqs) <= set(matrix_rows),
                    "missing: " + ", ".join(sorted(set(reqs) - set(matrix_rows), key=lambda x: int(x[4:]))))
        bad_risk = [k for k, r in risk_rows.items() if not re.search(r"\bP[0-3]\b", " ".join(r))]
        res.add(2, "every risk row assigns a priority P0-P3", not bad_risk, ", ".join(bad_risk))

        silent = []
        for k in reqs:
            if k in traced:
                continue
            row = " ".join(matrix_rows.get(k, [])).lower()
            explained = any(w in row for w in ("out of scope", "blocked", "deferred", "вне", "заблок", "отлож"))
            if not explained:
                silent.append(k)
        res.add(2, "every REQ is covered, or explicitly out of scope / blocked", not silent, ", ".join(silent))

        blocked_refs = ids(QID, find_section(secs, "matrix") or "")
        if ctx.get("qs"):
            res.add(2, "every Q cited as a blocker exists in the gap report", blocked_refs <= ctx["qs"],
                    ", ".join(sorted(blocked_refs - ctx["qs"])))

        matrix_tc = ids(TCID, find_section(secs, "matrix") or "")
        res.add(2, "every TC ID named in the matrix exists in a case file", matrix_tc <= set(cases),
                ", ".join(sorted(matrix_tc - set(cases))))

        prio_of_req = {}
        for k, r in risk_rows.items():
            m = re.search(r"\bP([0-3])\b", " ".join(r))
            if m:
                prio_of_req[k] = int(m.group(1))
        best_case_prio: dict[str, int] = {}
        for v in cases.values():
            m = re.search(r"\bP([0-3])\b", v["fields"].get("priority", ""))
            if not m:
                continue
            for r in ids(REQ, v["fields"].get("traces", "")):
                best_case_prio[r] = min(best_case_prio.get(r, 9), int(m.group(1)))
        under = [f"{r} (P{p} → best case P{best_case_prio[r]})" for r, p in prio_of_req.items()
                 if r in best_case_prio and best_case_prio[r] > p]
        res.add(2, "each REQ's highest-priority case matches the REQ's priority", not under, ", ".join(under))

    automated = [v for v in cases.values() if v["level_code"] != "MAN"]
    if automated:
        e2e_share = sum(v["level_code"] == "E2E" for v in automated) / len(automated)
        res.add(2, "pyramid is not inverted (E2E share of automated cases <= 50%)", e2e_share <= 0.5,
                f"E2E share {e2e_share:.0%}")
    return ctx


def check_stage3(res: Result, d: Path, ctx: dict) -> None:
    path = d / "autotest-summary.md"
    if not res.add(3, "autotest-summary.md exists", path.exists()):
        return
    md = path.read_text()
    secs = check_sections(res, 3, "autotest-summary.md", md)
    rows = [r for r in table_rows(find_section(secs, "mapping") or "") if r and TCID.search(r[0])]
    seen: dict[str, int] = {}
    bad_status = []
    for r in rows:
        tc = TCID.search(r[0]).group(0)
        seen[tc] = seen.get(tc, 0) + 1
        status = next((s for s in STATUSES if s in " ".join(r).lower()), None)
        if status is None:
            bad_status.append(tc)
    cases = ctx.get("cases", {})
    expected = {c for c, v in cases.items() if v["level_code"] != "MAN"}
    if expected:
        res.add(3, "every automatable case appears in the mapping", expected <= set(seen),
                "missing: " + ", ".join(sorted(expected - set(seen))))
    dup = [c for c, n in seen.items() if n > 1]
    res.add(3, "no case appears twice in the mapping", not dup, ", ".join(dup))
    res.add(3, "every mapping row has a valid status (passed / failed / not run / manual)", not bad_status,
            ", ".join(bad_status))
    cmd = find_section(secs, "commands") or ""
    res.add(3, "commands run are recorded", bool(re.search(r"`[^`]+`|```", cmd)))


def check_stage4(res: Result, d: Path, ctx: dict) -> None:
    path = d / "qa-review-report.md"
    if not res.add(4, "qa-review-report.md exists", path.exists()):
        return
    md = path.read_text()
    secs = check_sections(res, 4, "qa-review-report.md", md)
    summary = find_section(secs, "trace_summary") or ""
    reqs = set(ctx.get("reqs", {}))
    if reqs:
        listed = ids(REQ, summary)
        res.add(4, "traceability summary gives a verdict for every REQ", reqs <= listed,
                "missing: " + ", ".join(sorted(reqs - listed)))
    findings = find_section(secs, "findings") or ""
    rids = re.findall(r"\*\*(R-\d+)\*\*", findings)
    res.add(4, "findings are numbered R-<n> and unique", len(rids) == len(set(rids)), f"{len(rids)} findings")
    no_sev = [rid for rid in rids
              if not re.search(re.escape(rid) + r"\*\*\s*\[([^\]]+)\]", findings)
              or re.search(re.escape(rid) + r"\*\*\s*\[([^\]]+)\]", findings).group(1).lower() not in SEVERITIES]
    res.add(4, "every finding carries a severity tag", not no_sev, ", ".join(no_sev))
    disputed = find_section(secs, "disputed") or ""
    res.add(4, "disputed section is filled ('None' or items)", len(disputed.strip()) > 0)


def check_state(res: Result, state_path: Path, d: Path) -> None:
    try:
        st = json.loads(state_path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        res.add(0, "task state is valid JSON", False, str(e))
        return
    res.add(0, "task state is valid JSON", True)
    for key in ("task_id", "status", "output_language", "stages", "history"):
        res.add(0, f"task state has '{key}'", key in st)
    res.add(0, "task status is a known value",
            st.get("status") in {"TODO", "IN_PROGRESS", "BLOCKED", "IN_REVIEW", "DONE", "FAILED"}, str(st.get("status")))
    res.add(0, "output_language is en or ru", st.get("output_language") in {"en", "ru"}, str(st.get("output_language")))
    stages = st.get("stages", [])
    res.add(0, "task state has four stages", len(stages) == 4)
    for s in stages:
        if s.get("status") == "done":
            outs = s.get("output") or []
            outs = [outs] if isinstance(outs, str) else outs
            res.add(0, f"stage {s.get('stage')} done ⇒ has completed_at and outputs",
                    bool(s.get("completed_at")) and bool(outs))
    res.add(0, "history is a non-empty list", isinstance(st.get("history"), list) and len(st["history"]) > 0)
    if st.get("status") == "IN_REVIEW":
        res.add(0, "IN_REVIEW ⇒ all four stages done", all(s.get("status") == "done" for s in stages))


def check_language(res: Result, d: Path, lang: str) -> None:
    for f in ("spec-gap-report.md", "test-plan.md", "qa-review-report.md"):
        p = d / f
        if not p.exists():
            continue
        text = re.sub(r"```.*?```", "", p.read_text(), flags=re.S)
        ratio = len(CYRILLIC.findall(text)) / max(1, len(re.findall(r"[A-Za-zА-Яа-яЁё]", text)))
        ok = ratio > 0.3 if lang == "ru" else ratio < 0.1
        res.add(0, f"{f} is written in the output language ({lang})", ok, f"cyrillic share {ratio:.0%}")


# --- entry point ---------------------------------------------------------------------

def run(task_dir: Path, stages: set[int] | None = None, state: Path | None = None,
        lang: str | None = None) -> Result:
    res = Result(str(task_dir))
    present = {
        1: (task_dir / "spec-gap-report.md").exists(),
        2: (task_dir / "test-plan.md").exists() or any((task_dir / f).exists() for f in LEVEL_FILES.values()),
        3: (task_dir / "autotest-summary.md").exists(),
        4: (task_dir / "qa-review-report.md").exists(),
    }
    wanted = stages or {s for s, ok in present.items() if ok}
    ctx: dict = {}
    if 1 in wanted or 2 in wanted or 4 in wanted:
        sub = Result(str(task_dir))
        ctx = check_stage1(sub if 1 not in wanted else res, task_dir)
    if 2 in wanted or 3 in wanted:
        sub = Result(str(task_dir))
        ctx = check_stage2(sub if 2 not in wanted else res, task_dir, ctx)
    if 3 in wanted:
        check_stage3(res, task_dir, ctx)
    if 4 in wanted:
        check_stage4(res, task_dir, ctx)
    if state:
        check_state(res, state, task_dir)
        if lang is None:
            try:
                lang = json.loads(state.read_text()).get("output_language")
            except (OSError, json.JSONDecodeError):
                pass
    if lang in {"en", "ru"}:
        check_language(res, task_dir, lang)
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("task_dir", type=Path)
    ap.add_argument("--stages", help="comma-separated stages to check, e.g. 1,2 (default: those present)")
    ap.add_argument("--state", type=Path, help="path to the task's pipeline-state JSON")
    ap.add_argument("--lang", choices=["en", "ru"], help="expected output language")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    stages = {int(s) for s in args.stages.split(",")} if args.stages else None
    res = run(args.task_dir, stages, args.state, args.lang)
    if args.json:
        print(json.dumps(res.summary(), ensure_ascii=False, indent=2))
    else:
        for c in res.checks:
            mark = "ok  " if c.passed else "FAIL"
            detail = f"  ({c.detail})" if c.detail and not c.passed else ""
            print(f"{mark} [stage {c.stage}] {c.name}{detail}")
        s = res.summary()
        print(f"\n{'PASS' if res.passed else 'FAIL'}: {s['total'] - s['failed']}/{s['total']} checks passed")
    return 0 if res.passed else 1


if __name__ == "__main__":
    sys.exit(main())
