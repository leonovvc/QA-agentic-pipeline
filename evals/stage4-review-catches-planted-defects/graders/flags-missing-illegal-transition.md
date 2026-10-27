---
type: regex
weight: 2
target: { source: file, path: docs/qa/cart-orders/qa-review-report.md }
pattern: "(REQ-6|TC-E2E-001|state transition)[^\\n]{0,400}(Shipped|Delivered|illegal|invalid|forbidden|cannot be cancel)|(Shipped|Delivered|illegal|invalid|forbidden)[^\\n]{0,400}(REQ-6|TC-E2E-001)"
flags: i
---
