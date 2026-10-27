#!/usr/bin/env python3
"""Turn a `claude plugin eval --keep-temp` run into a committed, re-checkable record.

For every kept run directory it finds the case it belongs to (by matching the prompt in
the run's transcript), copies what the agents produced (docs/qa/** and new test files)
into eval-results/<run-id>/<case>/artifacts/, and computes independent scores on those
artifacts:

  * contract conformance — tools/check_artifacts.py on each task directory produced;
  * spec-defect recall    — tools/score_spec_analysis.py for cases with ground-truth.yaml.

It also copies the harness's aggregate-result.json and report.html. The resulting
scores.json files are what tools/verify_recorded_runs.py re-derives in CI.

    python tools/collect_eval_run.py --results /path/to/output-dir \\
        --kept /tmp/claude-eval-* --run-id 2026-10-27
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_artifacts import run as check_run  # noqa: E402
from score_spec_analysis import score as recall_score  # noqa: E402

SKIP_PARTS = {".claude", "node_modules", ".pytest_cache", "__pycache__", ".git"}


def case_prompts() -> dict[str, str]:
    prompts = {}
    for p in sorted((ROOT / "evals").glob("*/prompt.md")):
        body = p.read_text().split("---", 2)[-1].strip()
        prompts[p.parent.name] = body
    return prompts


def first_user_text(trace: Path) -> str:
    for line in trace.read_text(errors="replace").splitlines():
        try:
            m = json.loads(line)
        except json.JSONDecodeError:
            continue
        if m.get("type") != "user":
            continue
        content = m.get("message", {}).get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return " ".join(b.get("text", "") for b in content if isinstance(b, dict))
    return ""


def identify(kept: Path, prompts: dict[str, str]) -> str | None:
    """The prompt is not echoed in out/trace.jsonl; the session log under config/ has it."""
    texts = [first_user_text(p) for p in sorted((kept / "config" / "projects").glob("*/*.jsonl"))]
    trace = kept / "out" / "trace.jsonl"
    if trace.exists():
        texts.append(first_user_text(trace))
    for text in texts:
        for name, body in prompts.items():
            if body[:120] in text:
                return name
    return None


def tool_calls(trace: Path) -> list[dict]:
    calls = []
    for line in trace.read_text(errors="replace").splitlines():
        try:
            m = json.loads(line)
        except json.JSONDecodeError:
            continue
        for b in (m.get("message", {}) or {}).get("content", []) or []:
            if isinstance(b, dict) and b.get("type") == "tool_use":
                calls.append({"name": b.get("name"), "input": b.get("input", {})})
    return calls


def collect(kept: Path, case: str, dest: Path) -> dict:
    cwd = kept / "home" / "cwd"
    art = dest / "artifacts"
    if art.exists():
        shutil.rmtree(art)
    art.mkdir(parents=True)
    scaffold_files = set()
    scaffold_res = ROOT / "evals" / case / "resources"
    if scaffold_res.exists():
        scaffold_files = {p.name for p in scaffold_res.rglob("*") if p.is_file()}

    copied = []
    for p in sorted(cwd.rglob("*")):
        if not p.is_file() or SKIP_PARTS & set(p.relative_to(cwd).parts):
            continue
        rel = p.relative_to(cwd)
        is_doc = rel.parts[:2] == ("docs", "qa")
        is_test = rel.parts and rel.parts[0] in {"tests", "test", "e2e", "__tests__"} and p.suffix in {".py", ".ts", ".js"}
        if is_doc or is_test:
            target = art / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, target)
            copied.append(str(rel))

    trace = kept / "out" / "trace.jsonl"
    calls = tool_calls(trace) if trace.exists() else []
    shutil.copy2(trace, dest / "trace.jsonl") if trace.exists() else None

    scores: dict = {"case": case, "artifacts": copied, "tool_calls": {}, "task_dirs": {}}
    for c in calls:
        scores["tool_calls"][c["name"]] = scores["tool_calls"].get(c["name"], 0) + 1
    agents = sorted({str(c["input"].get("subagent_type", "")) for c in calls if c["name"] in {"Agent", "Task"}} - {""})
    skills = sorted({str(c["input"].get("skill", "")) for c in calls if c["name"] == "Skill"} - {""})
    scores["agents_dispatched"], scores["skills_invoked"] = agents, skills

    state_dir = art / "docs" / "qa" / "pipeline-state"
    for task_dir in sorted((art / "docs" / "qa").glob("*")) if (art / "docs" / "qa").exists() else []:
        if not task_dir.is_dir() or task_dir.name == "pipeline-state":
            continue
        state = state_dir / f"{task_dir.name}.json"
        res = check_run(task_dir, state=state if state.exists() else None)
        s = res.summary()
        scores["task_dirs"][task_dir.name] = {
            "contract_checks_total": s["total"],
            "contract_checks_failed": s["failed"],
            "failed_checks": [f"[stage {c['stage']}] {c['name']}" + (f" ({c['detail']})" if c["detail"] else "")
                              for c in s["checks"] if not c["passed"]],
        }
        truth_path = ROOT / "evals" / case / "ground-truth.yaml"
        report = task_dir / "spec-gap-report.md"
        if truth_path.exists() and report.exists():
            r = recall_score(report.read_text(), yaml.safe_load(truth_path.read_text()))
            scores["task_dirs"][task_dir.name]["spec_defect_recall"] = {
                "planted": r["planted"], "found": r["found"], "recall": r["recall"],
                "missed": [d["id"] for d in r["defects"] if not d["found"]],
                "requirements_inventoried": r["requirements_inventoried"],
                "questions_raised": r["questions_raised"],
            }
    (dest / "scores.json").write_text(json.dumps(scores, ensure_ascii=False, indent=2) + "\n")
    return scores


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--results", type=Path, required=True, help="the --output-dir of the eval run")
    ap.add_argument("--kept", type=Path, nargs="+", required=True, help="kept temp dirs (--keep-temp)")
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args()

    out = ROOT / "eval-results" / args.run_id
    out.mkdir(parents=True, exist_ok=True)
    for name in ("aggregate-result.json", "report.html"):
        if (args.results / name).exists():
            shutil.copy2(args.results / name, out / name)

    prompts = case_prompts()
    seen: dict[str, int] = {}
    for kept in args.kept:
        case = identify(kept, prompts)
        if not case:
            print(f"skip {kept}: no matching case")
            continue
        seen[case] = seen.get(case, 0) + 1
        dest = out / case if seen[case] == 1 else out / f"{case}--run{seen[case]}"
        s = collect(kept, case, dest)
        dirs = ", ".join(f"{k}: {v['contract_checks_total'] - v['contract_checks_failed']}/{v['contract_checks_total']}"
                         for k, v in s["task_dirs"].items())
        print(f"{case}: {len(s['artifacts'])} artifacts · contract {dirs or '—'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
