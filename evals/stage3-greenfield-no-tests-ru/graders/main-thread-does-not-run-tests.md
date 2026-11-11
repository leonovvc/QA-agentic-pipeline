---
type: regex
weight: 1
target: trace
match: not_contains
pattern: '"name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*?\b(pytest|vitest|jest|playwright test)\b(?! --version)(?:[^"\\]|\\.)*"[^\n]*"parent_tool_use_id":null'
---
Running the suite belongs to Stage 3 (and the Stage 4 re-run sample). The main thread
running it duplicates that work and is how a blocked Stage 3 gets taken over.
