---
type: regex
weight: 2
target: trace
match: not_contains
pattern: '"name":"(Write|Edit)","input":\{"file_path":"[^"]*autotest-summary\.md"[^\n]*"parent_tool_use_id":null'
---
Only `autotest-builder` writes `autotest-summary.md`. A Write/Edit of it on a main-thread
line (`parent_tool_use_id: null`) means the orchestrator or the routing conversation did
Stage 3's job itself — seen once when the agent's pytest command was denied.
