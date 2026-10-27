---
type: regex
target: { source: file, path: docs/qa/cart-orders/qa-review-report.md }
pattern: "TC-API-002[^\\n]{0,400}(vague|works correctly|not observable|not specific|ambiguous|message)|works correctly[^\\n]{0,300}TC-API-002"
flags: i
---
