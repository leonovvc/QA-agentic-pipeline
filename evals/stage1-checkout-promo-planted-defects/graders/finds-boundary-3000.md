---
type: regex
target: { source: file, path: docs/qa/checkout-promo/spec-gap-report.md }
pattern: "(exactly|equal to|>=|≥|inclusive|at least|strict|or (below|less|more)|qualif)[^\\n]{0,160}3[ ,]?000|3[ ,]?000(\\.00|,00)?[^\\n]{0,160}(exactly|equal|>=|≥|inclusive|at least|strict|or (below|less|more)|qualif|eligible)"
flags: i
---
