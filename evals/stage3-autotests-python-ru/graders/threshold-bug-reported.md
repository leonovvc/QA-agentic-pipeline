---
type: regex
weight: 3
target: { source: file, path: docs/qa/pricing/autotest-summary.md }
pattern: "TC-UNIT-004[^\\n]*(failed|упал|не прош)[\\s\\S]*(дефект|defect)|(дефект|defect)[\\s\\S]*TC-UNIT-004"
flags: i
---
