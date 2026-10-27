#!/usr/bin/env python3
"""Re-derive the published eval numbers from the recorded artifacts (runs in CI).

eval-results/<run-id>/<case>/scores.json holds the contract-conformance and recall
numbers quoted in the README. This script recomputes both from the artifacts committed
next to them, with the current tools, and fails if any number differs — so a published
figure can't silently drift from the evidence, and a change to the checker that would
re-grade old runs is noticed.

    python tools/verify_recorded_runs.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_artifacts import run as check_run  # noqa: E402
from score_spec_analysis import score as recall_score  # noqa: E402


def main() -> int:
    results = ROOT / "eval-results"
    score_files = sorted(results.glob("*/*/scores.json")) if results.exists() else []
    if not score_files:
        print("no recorded runs found")
        return 0
    mismatches = []
    for sf in score_files:
        stored = json.loads(sf.read_text())
        case_dir = sf.parent
        art = case_dir / "artifacts" / "docs" / "qa"
        case = stored["case"]
        for task, rec in stored.get("task_dirs", {}).items():
            task_dir = art / task
            state = art / "pipeline-state" / f"{task}.json"
            s = check_run(task_dir, state=state if state.exists() else None).summary()
            if (s["total"], s["failed"]) != (rec["contract_checks_total"], rec["contract_checks_failed"]):
                mismatches.append(f"{case_dir.relative_to(ROOT)} {task}: contract {s['total'] - s['failed']}/{s['total']} "
                                  f"!= recorded {rec['contract_checks_total'] - rec['contract_checks_failed']}/{rec['contract_checks_total']}")
            if "spec_defect_recall" in rec:
                truth = yaml.safe_load((ROOT / "evals" / case / "ground-truth.yaml").read_text())
                r = recall_score((task_dir / "spec-gap-report.md").read_text(), truth)
                if r["found"] != rec["spec_defect_recall"]["found"]:
                    mismatches.append(f"{case_dir.relative_to(ROOT)} {task}: recall {r['found']} != recorded "
                                      f"{rec['spec_defect_recall']['found']}")
        print(f"checked {sf.relative_to(ROOT)}")
    for m in mismatches:
        print(f"MISMATCH {m}")
    print(f"{'PASS' if not mismatches else 'FAIL'}: {len(score_files)} recorded case runs re-derived")
    return 0 if not mismatches else 1


if __name__ == "__main__":
    sys.exit(main())
