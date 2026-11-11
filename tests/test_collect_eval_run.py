"""Collect QA artifacts from both kept-workspace layouts."""

import pytest

from collect_eval_run import collect


@pytest.mark.parametrize("layout", ["home/cwd", "sealed/home/cwd"])
def test_collects_artifacts_from_kept_workspace(tmp_path, layout):
    kept = tmp_path / "claude-eval-test"
    artifact = kept / layout / "tests" / "test_pricing.py"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("def test_pricing():\n    assert True\n", encoding="utf-8")

    dest = tmp_path / "result"
    result = collect(kept, "orchestration-fresh-pricing", dest)

    copied = dest / "artifacts" / "tests" / "test_pricing.py"
    assert copied.read_bytes() == artifact.read_bytes()
    assert result["artifacts"] == [str(artifact.relative_to(kept / layout))]
