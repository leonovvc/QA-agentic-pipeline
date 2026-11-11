---
type: regex
weight: 2
target: trace
match: not_contains
pattern: '"name":"(Write|Edit)","input":\{"file_path":"[^"]*[\\/]tests?[\\/][^"]*\.(py|ts|js)"[^\n]*"parent_tool_use_id":null'
---
Test files are written by `autotest-builder`, never by the main thread.
