#!/usr/bin/env python3
"""Score a Stage 1 spec-gap report against the defects planted in an eval spec.

Each eval spec under evals/stage1-*/ ships a ground-truth.yaml listing the defects that
were deliberately planted in it. A defect counts as *found* when a single finding unit
of the report — one table row, one list item, or one paragraph — matches every regex
group in its `all_of` list (case-insensitive). Requiring all groups inside ONE unit keeps
a report from scoring by scattering keywords across unrelated sentences.

    python tools/score_spec_analysis.py <spec-gap-report.md> <ground-truth.yaml> [--json]

Prints recall (found / planted), the list of misses, and the number of findings the
report raised overall (Q and A entries), so recall can be read next to volume.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml


SKIP_SECTIONS = re.compile(
    r"^##\s+(Source|Источник|Testability Score|Оценка тестируемости|Ready-for-Test-Design|Готовность)", re.I)


def finding_units(md: str) -> list[str]:
    """Split a markdown report into finding units, skipping non-finding sections.

    The score/summary paragraph and the readiness checklist mention many problems in
    passing; counting them would reward a report for naming a topic without raising it.
    """
    md = re.sub(r"```.*?```", "", md, flags=re.S)
    kept, skipping = [], False
    for line in md.splitlines():
        if line.startswith("## "):
            skipping = bool(SKIP_SECTIONS.match(line))
        if not skipping:
            kept.append(line)
    md = "\n".join(kept)
    units: list[str] = []
    current: list[str] = []

    def flush() -> None:
        if current:
            units.append(" ".join(s.strip() for s in current).strip())
            current.clear()

    for line in md.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            flush()
            continue
        if stripped.startswith("|"):
            flush()
            units.append(stripped)
            continue
        if re.match(r"^(\d+\.|[-*])\s+", stripped):
            flush()
        current.append(stripped)
    flush()
    return [u for u in units if u]


def score(report_md: str, truth: dict) -> dict:
    units = finding_units(report_md)
    results = []
    for d in truth["defects"]:
        groups = [re.compile(g, re.I) for g in d["all_of"]]
        hit = next((u for u in units if all(g.search(u) for g in groups)), None)
        results.append({"id": d["id"], "kind": d["kind"], "found": hit is not None,
                        "evidence": (hit[:220] + "…") if hit and len(hit) > 220 else hit})
    found = sum(r["found"] for r in results)
    q_ids = set(re.findall(r"\*\*Q(\d+)\*\*", report_md))
    a_ids = set(re.findall(r"\*\*A(\d+)\*\*", report_md))
    req_ids = set(re.findall(r"\|\s*\**REQ-(\d+)\**\s*\|", report_md))
    return {
        "planted": len(results),
        "found": found,
        "recall": round(found / len(results), 3) if results else None,
        "questions_raised": len(q_ids),
        "assumptions_logged": len(a_ids),
        "requirements_inventoried": len(req_ids),
        "defects": results,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("report", type=Path)
    ap.add_argument("ground_truth", type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    truth = yaml.safe_load(args.ground_truth.read_text())
    result = score(args.report.read_text(), truth)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for r in result["defects"]:
            print(f"{'found ' if r['found'] else 'MISSED'} {r['id']:<4} {r['kind']}")
        print(f"\nrecall {result['found']}/{result['planted']} = {result['recall']:.0%}  ·  "
              f"{result['requirements_inventoried']} REQs, {result['questions_raised']} Qs, "
              f"{result['assumptions_logged']} As")
    return 0


if __name__ == "__main__":
    sys.exit(main())
