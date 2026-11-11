"""tools/measure_run_cost.py attributes every API call to the right stage and prices it."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from measure_run_cost import ORCHESTRATOR, SERVICE, build_ledger, call_cost, summarize  # noqa: E402

MODEL = "claude-sonnet-5-5"
SESSION = "11111111-2222-3333-4444-555555555555"


def usage(inp=0, w1h=0, w5m=0, read=0, out=0):
    return {"input_tokens": inp, "cache_creation_input_tokens": w1h + w5m, "cache_read_input_tokens": read,
            "output_tokens": out, "cache_creation": {"ephemeral_1h_input_tokens": w1h, "ephemeral_5m_input_tokens": w5m}}


def assistant(mid, u, content=None, model=MODEL):
    return {"type": "assistant",
            "message": {"id": mid, "model": model, "usage": u, "content": content or [{"type": "text", "text": "…"}]}}


def spawn(tool_id, agent):
    return {"type": "tool_use", "id": tool_id, "name": "Agent", "input": {"subagent_type": f"qa-agentic-pipeline:{agent}"}}


def write_jsonl(path: Path, rows: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\nnot json\n", encoding="utf-8")


def subagent(session_dir: Path, agent_id: str, agent_type: str, tool_use_id: str, rows: list) -> None:
    base = session_dir / SESSION / "subagents" / f"agent-{agent_id}"
    write_jsonl(base.with_suffix(".jsonl"), rows)
    base.with_suffix(".meta.json").write_text(json.dumps({"agentType": agent_type, "toolUseId": tool_use_id}),
                                              encoding="utf-8")


@pytest.fixture
def run(tmp_path: Path) -> tuple[Path, Path]:
    session = tmp_path / "projects" / "ws-slug"
    write_jsonl(session / f"{SESSION}.jsonl", [
        {"type": "user", "message": {"role": "user", "content": "Прогони QA-пайплайн"}},
        # one response logged once per content block; the last copy has the final output count
        assistant("m1", usage(inp=2, w1h=20_000, out=1), content=[{"type": "text", "text": "start"}]),
        assistant("m1", usage(inp=2, w1h=20_000, out=120), content=[spawn("t1", "spec-analyst")]),
        assistant("m2", usage(inp=1, read=20_000, out=30), content=[spawn("t2", "autotest-builder")]),
        assistant("synthetic", usage(out=5), model="<synthetic>"),
    ])
    subagent(session, "a1", "qa-agentic-pipeline:spec-analyst", "t1", [
        assistant("s1", usage(inp=3, w5m=10_000, out=900)),
        assistant("s2", usage(inp=1, read=10_000, out=400)),
    ])
    # autotest-builder starts its own helper agent: billed to Stage 3, not to "other"
    subagent(session, "a2", "qa-agentic-pipeline:autotest-builder", "t2", [
        assistant("b1", usage(inp=5, w1h=8_000, out=200), content=[spawn("t3", "Explore")]),
    ])
    subagent(session, "a3", "Explore", "t3", [assistant("x1", usage(inp=4, w1h=5_000, out=100))])
    trace = tmp_path / "trace.jsonl"
    write_jsonl(trace, [
        {"type": "result", "total_cost_usd": 0.05, "num_turns": 2},
        {"type": "result", "total_cost_usd": 0.1, "num_turns": 3, "duration_ms": 120_000, "modelUsage": {}},
    ])
    return session, trace


def test_calls_deduplicated_and_attributed(run):
    ledger = build_ledger(*run)
    by_id = {c["id"]: c for c in ledger["calls"]}
    assert sorted(by_id) == ["b1", "m1", "m2", "s1", "s2", "x1"]  # no synthetic, no duplicate m1
    assert by_id["m1"]["output"] == 120
    assert by_id["m1"]["bucket"] == by_id["m2"]["bucket"] == ORCHESTRATOR
    assert by_id["s1"]["bucket"] == by_id["s2"]["bucket"] == "Stage 1 — spec-analyst"
    assert by_id["b1"]["bucket"] == by_id["x1"]["bucket"] == "Stage 3 — autotest-builder"


def test_summary_totals_and_prices(run):
    s = summarize(build_ledger(*run))
    rows = {r["bucket"]: r for r in s["rows"]}
    assert [r["bucket"] for r in s["rows"]] == [ORCHESTRATOR, "Stage 1 — spec-analyst", "Stage 3 — autotest-builder"]
    st1 = rows["Stage 1 — spec-analyst"]
    assert (st1["api_calls"], st1["input"], st1["cache_write_5m"], st1["cache_read"], st1["output"]) == (2, 4, 10_000, 10_000, 1300)
    assert st1["input_total"] == 20_004
    # Sonnet 5.5: $2 in, 1.25x for 5m writes, $0.10 cache read, $10 out
    assert st1["cost_usd"] == pytest.approx((4 * 2 + 10_000 * 2.5 + 10_000 * 0.1 + 1300 * 10) / 1e6, abs=1e-4)
    assert s["total"]["api_calls"] == 6
    assert s["total"]["cost_usd"] == pytest.approx(sum(r["cost_usd"] for r in s["rows"]), abs=1e-4)
    assert (s["harness_total_cost_usd"], s["num_turns"]) == (0.1, 5)  # last (cumulative) cost; turns summed


def test_without_trace_there_is_no_harness_total(run):
    assert summarize(build_ledger(run[0]))["harness_total_cost_usd"] is None


def test_tokens_missing_from_transcripts_become_a_service_row(run):
    session, trace = run
    computed = build_ledger(session)["calls"]
    total = {f: sum(c[f] for c in computed) for f in ("input", "cache_read", "output")}
    writes = sum(c["cache_write_5m"] + c["cache_write_1h"] for c in computed)
    write_jsonl(trace, [{"type": "result", "total_cost_usd": 1.0, "modelUsage": {MODEL: {
        "inputTokens": total["input"] + 10, "cacheReadInputTokens": total["cache_read"] + 45_000,
        "outputTokens": total["output"], "cacheCreationInputTokens": writes}}}])
    s = summarize(build_ledger(session, trace))
    service = s["rows"][-1]
    assert service["bucket"] == SERVICE
    assert (service["input"], service["cache_read"], service["output"], service["cache_write_5m"]) == (10, 45_000, 0, 0)
    assert s["total"]["cache_read"] == total["cache_read"] + 45_000


def test_one_hour_cache_write_is_twice_input():
    c = {"model": MODEL, "input": 0, "cache_write_5m": 0, "cache_write_1h": 1_000_000, "cache_read": 0, "output": 0}
    assert call_cost(c) == pytest.approx(4.0)


def test_unknown_model_is_an_error():
    with pytest.raises(KeyError):
        call_cost({"model": "some-new-model", "input": 1, "cache_write_5m": 0, "cache_write_1h": 0, "cache_read": 0, "output": 0})
