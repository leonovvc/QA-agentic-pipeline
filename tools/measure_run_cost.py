#!/usr/bin/env python3
"""Token and cost breakdown of one recorded agent run, per pipeline stage.

Reads the run's Claude Code session transcripts (in a `claude plugin eval --keep-temp`
dir: `config/projects/<slug>/`) and attributes every model call to the agent that made it:

  * the main thread is the orchestrator (`run-qa-pipeline` and the routing around it);
  * a call whose `parent_tool_use_id` points at an `Agent`/`Task` tool call belongs to
    that sub-agent (`spec-analyst` = Stage 1, `qa-doc-writer` = 2, `autotest-builder` = 3,
    `qa-doc-reviewer` = 4).

Tokens are reported the way the API bills them — uncached input, cache writes, cache
reads, output — and priced with the list prices below. The harness's own total
(`result.total_cost_usd` in the stream-json trace, `out/trace.jsonl`) is printed next to
the computed one, so a stale price table or a missed transcript shows up as a mismatch
instead of a silently wrong number. (The trace alone is not enough: its per-message
`output_tokens` are the values at the start of streaming, not the final counts.)

    python tools/measure_run_cost.py --session <kept>/config/projects/<slug> --trace <kept>/out/trace.jsonl
    python tools/measure_run_cost.py --session ... --json     # machine-readable
    python tools/measure_run_cost.py --ledger eval-results/<run>/<case>/usage-ledger.json

`--write-ledger` saves a small per-call ledger (no prompt text) that is committed with a
recorded run, so `tools/verify_recorded_runs.py` can re-derive the published numbers
without the multi-megabyte trace.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
import sys
from pathlib import Path

# USD per million tokens, Anthropic first-party list prices (checked 2026-11-11).
# Cache writes: 5-minute TTL = 1.25 x input, 1-hour TTL = 2 x input. Cache reads as listed.
PRICES = {
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00, "cache_read": 0.10},
    "claude-opus-5-5": {"input": 4.00, "output": 20.00, "cache_read": 0.20},
    "claude-haiku-5-5": {"input": 0.10, "output": 0.50, "cache_read": 0.01},
}

STAGE_OF_AGENT = {
    "spec-analyst": "Stage 1 — spec-analyst",
    "qa-doc-writer": "Stage 2 — qa-doc-writer",
    "autotest-builder": "Stage 3 — autotest-builder",
    "qa-doc-reviewer": "Stage 4 — qa-doc-reviewer",
}
ORCHESTRATOR = "Orchestrator (main thread)"
SERVICE = "Claude Code service calls (not in transcripts)"
TOKEN_FIELDS = ("input", "cache_write_5m", "cache_write_1h", "cache_read", "output")


def _bucket_name(subagent_type: str) -> str:
    short = subagent_type.split(":")[-1]
    return STAGE_OF_AGENT.get(short, f"Other agent — {short}")


def _read_jsonl(path: Path):
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            m = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(m, dict):
            yield m


def _transcript_calls(path: Path) -> tuple[dict[str, dict], list[tuple[str, str]]]:
    """API responses (by message id) and Agent/Task spawns (tool_use id, subagent_type) in one transcript."""
    calls: dict[str, dict] = {}
    spawns: list[tuple[str, str]] = []
    for m in _read_jsonl(path):
        msg = m.get("message")
        if m.get("type") != "assistant" or not isinstance(msg, dict):
            continue
        for b in msg.get("content") or []:
            if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") in {"Agent", "Task"}:
                spawns.append((b.get("id"), str((b.get("input") or {}).get("subagent_type", "?"))))
        usage, mid = msg.get("usage"), msg.get("id")
        if not usage or not mid or msg.get("model") == "<synthetic>":
            continue
        # one response is logged once per content block; the last copy carries the final output count
        cw = usage.get("cache_creation") or {}
        cw_1h = int(cw.get("ephemeral_1h_input_tokens") or 0)
        cw_5m = int(cw.get("ephemeral_5m_input_tokens") or 0) if cw else int(usage.get("cache_creation_input_tokens") or 0)
        calls[mid] = {"id": mid, "model": msg.get("model", "?"), "input": int(usage.get("input_tokens") or 0),
                      "cache_write_5m": cw_5m, "cache_write_1h": cw_1h,
                      "cache_read": int(usage.get("cache_read_input_tokens") or 0),
                      "output": int(usage.get("output_tokens") or 0)}
    return calls, spawns


def _harness_totals(trace: Path | None) -> dict:
    results: list[dict] = []
    if trace and trace.exists():
        results = [m for m in _read_jsonl(trace) if m.get("type") == "result"]
    # a session resumed by background-agent notifications emits one result per resumed turn;
    # cost and model usage are cumulative (take the last), turns are per result (sum them)
    result = results[-1] if results else {}
    return {
        "total_cost_usd": result.get("total_cost_usd"),
        "num_turns": sum(r.get("num_turns") or 0 for r in results) or None,
        "model_usage": {k: {f: v.get(f) for f in ("inputTokens", "outputTokens", "cacheReadInputTokens",
                                                   "cacheCreationInputTokens", "costUSD")}
                        for k, v in (result.get("modelUsage") or {}).items()},
    }


def build_ledger(session_dir: Path, trace: Path | None = None) -> dict:
    """One entry per distinct API response in a session's transcripts, attributed to its agent.

    `session_dir` is the Claude Code project directory of the run (`config/projects/<slug>/`
    in a harness kept dir, `~/.claude/projects/<slug>/` for a local run): `<session>.jsonl`
    is the main thread, `<session>/subagents/agent-<id>.jsonl` (+ `.meta.json`) the agents.
    Transcripts, unlike the stream-json trace, record each response's final output count.
    """
    ledger_calls: list[dict] = []
    for main in sorted(session_dir.glob("*.jsonl")):
        calls, spawns = _transcript_calls(main)
        bucket_of_spawn = {tid: _bucket_name(agent) for tid, agent in spawns}
        ledger_calls += [{**c, "bucket": ORCHESTRATOR} for c in calls.values()]
        agents = []
        for sub in sorted((main.parent / main.stem / "subagents").glob("agent-*.jsonl")):
            meta_path = sub.with_suffix(".meta.json")
            meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
            sub_calls, sub_spawns = _transcript_calls(sub)
            agents.append((meta, sub_calls, sub_spawns))
        # a sub-agent started by a sub-agent is billed to the stage that started it
        for _ in range(len(agents)):
            for meta, _calls, sub_spawns in agents:
                owner = bucket_of_spawn.get(meta.get("toolUseId"))
                if owner:
                    for tid, _agent in sub_spawns:
                        bucket_of_spawn.setdefault(tid, owner)
        for meta, sub_calls, _spawns in agents:
            bucket = bucket_of_spawn.get(meta.get("toolUseId")) or _bucket_name(str(meta.get("agentType", "?")))
            ledger_calls += [{**c, "bucket": bucket} for c in sub_calls.values()]
    harness = _harness_totals(trace)
    ledger_calls += _service_calls(ledger_calls, harness)
    stamps = sorted(str(m["timestamp"]) for f in session_dir.rglob("*.jsonl") for m in _read_jsonl(f) if m.get("timestamp"))
    wall = (datetime.fromisoformat(stamps[-1].replace("Z", "+00:00"))
            - datetime.fromisoformat(stamps[0].replace("Z", "+00:00"))).total_seconds() if stamps else None
    return {"calls": ledger_calls, "harness": harness, "wall_seconds": wall}


def _service_calls(calls: list[dict], harness: dict) -> list[dict]:
    """Tokens Claude Code reports for the session that no transcript holds (status summaries
    and similar service calls), as one entry per model, so the total matches the harness."""
    extra = []
    for model, u in harness.get("model_usage", {}).items():
        mine = [c for c in calls if c["model"] == model]
        diff = {
            "input": (u.get("inputTokens") or 0) - sum(c["input"] for c in mine),
            "cache_read": (u.get("cacheReadInputTokens") or 0) - sum(c["cache_read"] for c in mine),
            "output": (u.get("outputTokens") or 0) - sum(c["output"] for c in mine),
            # the split between 5-minute and 1-hour writes isn't reported in the total; 5m is the cheaper bound
            "cache_write_5m": (u.get("cacheCreationInputTokens") or 0)
            - sum(c["cache_write_5m"] + c["cache_write_1h"] for c in mine),
        }
        diff = {k: max(v, 0) for k, v in diff.items()}
        if any(diff.values()):
            extra.append({"id": f"service-{model}", "model": model, "cache_write_1h": 0, **diff, "bucket": SERVICE})
    return extra


def call_cost(c: dict) -> float:
    p = PRICES.get(c["model"])
    if p is None:
        raise KeyError(f"no price for model {c['model']!r}; add it to PRICES")
    return (c["input"] * p["input"] + c["cache_write_5m"] * p["input"] * 1.25
            + c["cache_write_1h"] * p["input"] * 2 + c["cache_read"] * p["cache_read"]
            + c["output"] * p["output"]) / 1_000_000


def summarize(ledger: dict) -> dict:
    order = [ORCHESTRATOR, *STAGE_OF_AGENT.values(), SERVICE]
    buckets: dict[str, dict] = {}
    for c in ledger["calls"]:
        b = buckets.setdefault(c["bucket"], {**{f: 0 for f in TOKEN_FIELDS}, "api_calls": 0, "cost_usd": 0.0,
                                             "models": set()})
        for f in TOKEN_FIELDS:
            b[f] += c[f]
        b["api_calls"] += 1
        b["cost_usd"] += call_cost(c)
        b["models"].add(c["model"])
    rows = []
    for name in sorted(buckets, key=lambda n: (order.index(n) if n in order else len(order) - 1.5, n)):
        b = buckets[name]
        rows.append({"bucket": name, **{f: b[f] for f in TOKEN_FIELDS}, "api_calls": b["api_calls"],
                     "input_total": b["input"] + b["cache_write_5m"] + b["cache_write_1h"] + b["cache_read"],
                     "cost_usd": round(b["cost_usd"], 4), "models": sorted(b["models"])})
    total = {f: sum(r[f] for r in rows) for f in (*TOKEN_FIELDS, "api_calls", "input_total")}
    total["cost_usd"] = round(sum(r["cost_usd"] for r in rows), 4)
    harness = ledger.get("harness", {}).get("total_cost_usd")
    return {"rows": rows, "total": total, "harness_total_cost_usd": harness,
            "num_turns": ledger.get("harness", {}).get("num_turns"),
            "wall_seconds": ledger.get("wall_seconds")}


def render(s: dict) -> str:
    def k(n: int) -> str:
        return f"{n / 1000:,.1f}k"
    head = "| Who | API calls | Input, uncached | Cache write | Cache read | Output | All input | Cost, $ |"
    lines = [head, "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in [*s["rows"], {"bucket": "**Total**", **s["total"]}]:
        lines.append(f"| {r['bucket']} | {r['api_calls']} | {k(r['input'])} | {k(r['cache_write_5m'] + r['cache_write_1h'])} "
                     f"| {k(r['cache_read'])} | {k(r['output'])} | {k(r['input_total'])} | {r['cost_usd']:.2f} |")
    h = s["harness_total_cost_usd"]
    if h is not None:
        lines.append(f"\nHarness total: ${h:.4f} · computed: ${s['total']['cost_usd']:.4f} "
                     f"({'match' if abs(h - s['total']['cost_usd']) < 0.01 else 'MISMATCH — check PRICES'})")
    if s.get("wall_seconds"):
        lines.append(f"Wall time (first to last transcript entry): {s['wall_seconds'] / 60:.1f} min"
                     + (f" · main-thread turns: {s['num_turns']}" if s.get("num_turns") else ""))
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--session", type=Path, help="the run's Claude Code project dir (holds <session>.jsonl)")
    src.add_argument("--ledger", type=Path, help="a usage-ledger.json written by --write-ledger")
    ap.add_argument("--trace", type=Path, help="stream-json trace, for the harness's own total to compare against")
    ap.add_argument("--json", action="store_true", help="print the summary as JSON")
    ap.add_argument("--write-ledger", type=Path, help="save the per-call ledger to this path")
    args = ap.parse_args()

    ledger = json.loads(args.ledger.read_text(encoding="utf-8")) if args.ledger else build_ledger(args.session, args.trace)
    if args.write_ledger:
        args.write_ledger.write_text(json.dumps(ledger, indent=1) + "\n", encoding="utf-8")
    s = summarize(ledger)
    print(json.dumps(s, ensure_ascii=False, indent=2) if args.json else render(s))
    return 0


if __name__ == "__main__":
    sys.exit(main())
