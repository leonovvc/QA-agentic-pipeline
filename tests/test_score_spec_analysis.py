"""The recall scorer counts a planted defect only when one finding raises it."""
from pathlib import Path

import yaml

from score_spec_analysis import finding_units, score

TRUTH = {
    "defects": [
        {"id": "D1", "kind": "contradiction", "all_of": ["expir", "5\\.2", "2\\.3|conflict"]},
        {"id": "D2", "kind": "security", "all_of": ["brute|rate.?limit"]},
    ]
}


def test_counts_a_defect_raised_in_one_finding():
    report = """## Contradictions
1. **Q1** — §2.3 vs §5.2: the expiry rules conflict.

## Open Questions
2. **Q2** — Is there a rate limit on code attempts?
"""
    result = score(report, TRUTH)
    assert result["found"] == 2 and result["recall"] == 1.0
    assert result["questions_raised"] == 2


def test_keywords_scattered_across_findings_do_not_count():
    report = """## Open Questions
1. **Q1** — When does a code expire?
2. **Q2** — §5.2 needs a time zone.
3. **Q3** — Do §2.3 and the admin panel conflict?
"""
    assert score(report, TRUTH)["defects"][0]["found"] is False


def test_summary_sections_are_not_findings():
    report = """## Testability Score: 2
Expiry rules in §2.3 and §5.2 conflict; no rate limit.

## Open Questions
(none)
"""
    assert score(report, TRUTH)["found"] == 0


def test_table_rows_are_units():
    units = finding_units("## Requirements Inventory\n| REQ-1 | §1 | a | b | yes |\n| REQ-2 | §2 | c | d | no → Q1 |\n")
    assert units == ["| REQ-1 | §1 | a | b | yes |", "| REQ-2 | §2 | c | d | no → Q1 |"]


def test_every_stage1_ground_truth_file_is_well_formed():
    root = Path(__file__).resolve().parent.parent / "evals"
    files = sorted(root.glob("*/ground-truth.yaml"))
    assert files, "no ground-truth files found"
    for f in files:
        truth = yaml.safe_load(f.read_text())
        assert truth["language"] in {"en", "ru"}, f
        ids = [d["id"] for d in truth["defects"]]
        assert len(ids) == len(set(ids)) >= 5, f
        for d in truth["defects"]:
            assert d["all_of"] and all(isinstance(g, str) and g for g in d["all_of"]), (f, d["id"])
