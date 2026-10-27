"""The plugin passes its own static validation, and the validator catches real breakage.

Each mutation test copies the plugin to a temp dir, breaks one thing the way it breaks
in practice, and asserts the validator reports exactly that problem.
"""
import shutil
from pathlib import Path

import pytest

from validate_plugin import validate

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture()
def plugin_copy(tmp_path: Path) -> Path:
    dst = tmp_path / "plugin"
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns(".git", "evals", "tests", "__pycache__"))
    return dst


def errors_for(root: Path) -> list[str]:
    return validate(root).errors


def test_repository_plugin_is_valid():
    report = validate(ROOT)
    assert report.errors == [], "\n".join(report.errors)
    assert report.checks > 500  # the validator actually walked every skill and agent


def test_detects_skill_name_not_matching_directory(plugin_copy: Path):
    md = plugin_copy / "skills" / "unit-testing" / "SKILL.md"
    md.write_text(md.read_text().replace("name: unit-testing", "name: unit-tests", 1))
    assert any("frontmatter name 'unit-tests' != directory name" in e for e in errors_for(plugin_copy))


def test_detects_dangling_reference_to_upstream_skill(plugin_copy: Path):
    md = plugin_copy / "skills" / "api-testing" / "SKILL.md"
    md.write_text(md.read_text() + "\nFor CI wiring see `ci-cd-integration`.\n")
    assert any("'ci-cd-integration', which this plugin does not ship" in e for e in errors_for(plugin_copy))


def test_detects_related_skill_that_does_not_exist(plugin_copy: Path):
    md = plugin_copy / "skills" / "test-planning" / "SKILL.md"
    md.write_text(md.read_text().replace("## Related Skills\n", "## Related Skills\n\n- **release-gate** -- decides go/no-go.\n", 1))
    assert any("related skill 'release-gate' does not exist" in e for e in errors_for(plugin_copy))


def test_detects_missing_reference_file(plugin_copy: Path):
    (plugin_copy / "skills" / "ai-qa-review" / "references" / "mutation-testing.md").unlink()
    assert any("references/mutation-testing.md, which does not exist" in e for e in errors_for(plugin_copy))


def test_detects_agent_preloading_unknown_skill(plugin_copy: Path):
    md = plugin_copy / "agents" / "qa-doc-writer.md"
    md.write_text(md.read_text().replace("  - test-planning\n", "  - test-plannning\n", 1))
    assert any("preloads skill 'test-plannning'" in e for e in errors_for(plugin_copy))


def test_detects_broken_contract_path(plugin_copy: Path):
    (plugin_copy / "skills" / "run-qa-pipeline" / "references" / "artifact-contract.md").rename(
        plugin_copy / "skills" / "run-qa-pipeline" / "references" / "contract.md")
    errs = errors_for(plugin_copy)
    assert any("artifact-contract.md, which does not exist" in e for e in errs)


def test_detects_description_over_limit(plugin_copy: Path):
    md = plugin_copy / "skills" / "test-pyramid-strategy" / "SKILL.md"
    text = md.read_text()
    md.write_text(text.replace("Use when:", "Use when: " + "very " * 250, 1))
    assert any("test-pyramid-strategy: description is" in e for e in errors_for(plugin_copy))


def test_detects_attribution_drift(plugin_copy: Path):
    notices = plugin_copy / "THIRD_PARTY_NOTICES.md"
    notices.write_text("\n".join(l for l in notices.read_text().splitlines() if not l.startswith("| `api-testing`")))
    assert any("does not list adapted skill 'api-testing'" in e for e in errors_for(plugin_copy))


def test_detects_unbalanced_code_fence(plugin_copy: Path):
    md = plugin_copy / "skills" / "qa-doc-review" / "SKILL.md"
    md.write_text(md.read_text() + "\n```markdown\nunterminated\n")
    assert any("qa-doc-review/SKILL.md: unbalanced" in e for e in errors_for(plugin_copy))
