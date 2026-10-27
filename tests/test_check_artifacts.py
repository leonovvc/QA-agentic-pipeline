"""check_artifacts accepts contract-conforming output and rejects each kind of violation.

The golden fixtures are complete, hand-checked pipeline outputs (one English, one
Russian). Each mutation reproduces a defect seen in real LLM output — a lost
requirement, a renumbered marker, a case without a level, an inverted pyramid — and
asserts the checker reports it by name.
"""
import json
import re
import shutil
from pathlib import Path

import pytest

from check_artifacts import run

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture()
def en(tmp_path: Path) -> Path:
    d = tmp_path / "golden-en"
    shutil.copytree(FIXTURES / "golden-en", d)
    return d


@pytest.fixture()
def ru(tmp_path: Path) -> Path:
    d = tmp_path / "golden-ru"
    shutil.copytree(FIXTURES / "golden-ru", d)
    return d


def failed(result) -> list[str]:
    return [c.name for c in result.checks if not c.passed]


def edit(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    assert old in text, f"fixture no longer contains {old!r}"
    path.write_text(text.replace(old, new, 1))


# --- golden runs pass ----------------------------------------------------------------

def test_golden_english_run_passes_all_stages(en: Path):
    res = run(en, state=en / "state.json")
    assert res.passed, failed(res)
    assert {c.stage for c in res.checks} == {0, 1, 2, 3, 4}


def test_golden_russian_run_passes_with_russian_headings_and_labels(ru: Path):
    res = run(ru, lang="ru")
    assert res.passed, failed(res)


# --- stage 1 -------------------------------------------------------------------------

def test_missing_requirements_inventory(en: Path):
    edit(en / "spec-gap-report.md", "## Requirements Inventory", "## Requirements")
    assert "spec-gap-report.md: required sections present" in failed(run(en, {1}))


def test_non_sequential_req_ids(en: Path):
    edit(en / "spec-gap-report.md", "| REQ-3 | §3", "| REQ-5 | §3")
    assert "REQ IDs are unique and sequential from 1" in failed(run(en, {1}))


def test_untestable_req_without_question(en: Path):
    edit(en / "spec-gap-report.md", "partly → Q1", "partly")
    assert "every non-testable REQ points at an existing Q" in failed(run(en, {1}))


def test_finding_without_inline_marker(en: Path):
    edit(en / "spec-annotated.md", "[Q1: TRACK B — currency and before/after discounts?]", "")
    assert "every Q in the report has an inline marker" in failed(run(en, {1}))


def test_renumbered_inline_marker(en: Path):
    edit(en / "spec-annotated.md", "[Q1:", "[Q2:")
    names = failed(run(en, {1}))
    assert "every inline Q marker exists in the report" in names


def test_empty_security_lens(en: Path):
    text = (en / "spec-gap-report.md").read_text()
    text = re.sub(r"## Security Lens\n.*?\n\n", "## Security Lens\n\n", text, flags=re.S)
    (en / "spec-gap-report.md").write_text(text)
    assert "security lens section is filled (findings or 'not applicable')" in failed(run(en, {1}))


# --- stage 2 -------------------------------------------------------------------------

def test_case_missing_a_field(en: Path):
    edit(en / "test-cases-unit.md", "- **Technique:** Boundary value analysis — quantity: 0, 1, 20, 21\n", "")
    assert "every case has all eight fields, non-empty" in failed(run(en, {1, 2}))


def test_case_in_the_wrong_level_file(en: Path):
    edit(en / "test-cases-unit.md", "### TC-UNIT-002:", "### TC-API-002:")
    assert "test-cases-unit.md: every case ID matches the file's level" in failed(run(en, {1, 2}))


def test_level_field_contradicts_id(en: Path):
    edit(en / "test-cases-api.md", "- **Level:** API —", "- **Level:** E2E —")
    assert "Level field agrees with the level code in the ID" in failed(run(en, {1, 2}))


def test_level_without_justification(en: Path):
    edit(en / "test-cases-unit.md", "- **Level:** Unit — arithmetic only", "- **Level:** Unit")
    assert "Level field carries a justification" in failed(run(en, {1, 2}))


def test_case_traces_to_unknown_requirement(en: Path):
    edit(en / "test-cases-api.md", "- **Traces:** REQ-2", "- **Traces:** REQ-9")
    names = failed(run(en, {1, 2}))
    assert "every traced REQ exists in the inventory" in names


def test_requirement_silently_dropped(en: Path):
    # REQ-4's only case disappears and the matrix still claims coverage-less "covered"
    text = (en / "test-cases-unit.md").read_text()
    (en / "test-cases-unit.md").write_text(text.split("### TC-UNIT-003")[0])
    edit(en / "test-plan.md", "| REQ-4 | TC-UNIT-003 | BVA | covered |", "| REQ-4 | — | — | covered |")
    assert "every REQ is covered, or explicitly out of scope / blocked" in failed(run(en, {1, 2}))


def test_requirement_explicitly_blocked_is_accepted(en: Path):
    text = (en / "test-cases-unit.md").read_text()
    (en / "test-cases-unit.md").write_text(text.split("### TC-UNIT-003")[0])
    edit(en / "test-plan.md", "| REQ-4 | TC-UNIT-003 | BVA | covered |", "| REQ-4 | — | — | blocked by Q1 |")
    assert "every REQ is covered, or explicitly out of scope / blocked" not in failed(run(en, {1, 2}))


def test_blocker_cites_unknown_question(en: Path):
    edit(en / "test-plan.md", "| REQ-4 | TC-UNIT-003 | BVA | covered |", "| REQ-4 | TC-UNIT-003 | BVA | blocked by Q7 |")
    assert "every Q cited as a blocker exists in the gap report" in failed(run(en, {1, 2}))


def test_vague_expected_result_english_and_russian(en: Path, ru: Path):
    edit(en / "test-cases-unit.md", "- **Expected result:** 348.50", "- **Expected result:** works correctly")
    assert "no vague expected results ('works correctly', 'всё работает', …)" in failed(run(en, {1, 2}))
    edit(ru / "test-cases-unit.md", "- **Ожидаемый результат:** 900,00", "- **Ожидаемый результат:** всё работает")
    assert "no vague expected results ('works correctly', 'всё работает', …)" in failed(run(ru, {1, 2}))


def test_p0_requirement_covered_only_by_lower_priority_cases(en: Path):
    edit(en / "test-cases-unit.md", "- **Priority:** P0", "- **Priority:** P3")
    assert "each REQ's highest-priority case matches the REQ's priority" in failed(run(en, {1, 2}))


def test_supporting_case_may_have_lower_priority(en: Path):
    # REQ-3 is P1 and keeps its P1 unit case; its E2E journey dropping to P2 is fine
    edit(en / "test-cases-e2e.md", "- **Priority:** P1", "- **Priority:** P2")
    assert "each REQ's highest-priority case matches the REQ's priority" not in failed(run(en, {1, 2}))


def test_inverted_pyramid(en: Path):
    for lvl_file, code in (("test-cases-unit.md", "UNIT"), ("test-cases-api.md", "API")):
        p = en / lvl_file
        p.unlink()
    (en / "test-cases-e2e.md").write_text((FIXTURES / "golden-en" / "test-cases-e2e.md").read_text())
    res = run(en, {1, 2})
    assert "pyramid is not inverted (E2E share of automated cases <= 50%)" in failed(res)


# --- stage 3 -------------------------------------------------------------------------

def test_case_missing_from_autotest_mapping(en: Path):
    edit(en / "autotest-summary.md", "| TC-UNIT-002 | src/cart/subtotal.test.ts | TC-UNIT-002: subtotal | passed | |\n", "")
    assert "every automatable case appears in the mapping" in failed(run(en, {3}))


def test_invalid_autotest_status(en: Path):
    edit(en / "autotest-summary.md", "| TC-UNIT-001: quantity boundaries | passed |", "| TC-UNIT-001: quantity boundaries | green |")
    assert "every mapping row has a valid status (passed / failed / not run / manual)" in failed(run(en, {3}))


def test_commands_not_recorded(en: Path):
    edit(en / "autotest-summary.md", "- `npx vitest run src/cart` — exit 0", "- ran the unit tests")
    assert "commands run are recorded" in failed(run(en, {3}))


# --- stage 4 -------------------------------------------------------------------------

def test_review_skips_a_requirement(en: Path):
    edit(en / "qa-review-report.md", "| REQ-3 | covered | TC-UNIT-002, TC-E2E-001 |\n", "")
    assert "traceability summary gives a verdict for every REQ" in failed(run(en, {4}))


def test_finding_without_severity(en: Path):
    edit(en / "qa-review-report.md", "**R-2** [Minor]", "**R-2**")
    assert "every finding carries a severity tag" in failed(run(en, {4}))


# --- task state & language -----------------------------------------------------------

def test_state_in_review_with_unfinished_stage(en: Path):
    st = json.loads((en / "state.json").read_text())
    st["stages"][2]["status"] = "in_progress"
    (en / "state.json").write_text(json.dumps(st))
    assert "IN_REVIEW ⇒ all four stages done" in failed(run(en, state=en / "state.json"))


def test_wrong_output_language(en: Path):
    res = run(en, lang="ru")
    assert any(n.endswith("is written in the output language (ru)") for n in failed(res))
