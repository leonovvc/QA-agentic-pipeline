---
type: regex
target: { source: file, path: docs/qa/checkout-promo/spec-gap-report.md }
pattern: "fast[^\\n]{0,200}(measur|threshold|ms\\b|millisecond|second|latency|response time|untestable|not testable)|(measur|untestable|not testable)[^\\n]{0,200}fast"
flags: i
---
