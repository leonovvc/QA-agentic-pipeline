---
type: regex
weight: 2
target: { source: file, path: docs/qa/cart-orders/qa-review-report.md }
pattern: "TC-UNIT-001[^\\n]{0,500}(\\b0\\b|\\b21\\b|min-1|max\\+1|min ?- ?1|max ?\\+ ?1|outside|invalid boundar|off-by-one)|(\\b0\\b|\\b21\\b|min-1|max\\+1)[^\\n]{0,500}TC-UNIT-001"
flags: i
---
