---
type: regex
weight: 2
target: { source: file, path: docs/qa/cart-orders/qa-review-report.md }
pattern: "TC-E2E-002[^\\n]{0,500}(unit|lower level|pyramid|push down|misallocat)|(unit|pyramid|misallocat)[^\\n]{0,500}TC-E2E-002"
flags: i
---
