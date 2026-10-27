---
type: llm
weight: 2
focus: { source: file, path: docs/qa/checkout-promo/spec-gap-report.md }
---

This is a QA spec-gap report for a promo-code spec. In the spec, §2.3 says a code is usable up to and including its expiry date, while §5.2 says codes stop working at the start of their expiry date.

PASS if all of the following hold:
- That §2.3/§5.2 conflict is reported as a contradiction (not merely as an assumption).
- Blocking gaps and assumptions are listed in separate sections.
- Open questions are split into a Track A list and a Track B list.
- The report does not present invented requirements as facts (anything not in the spec is framed as a question or an explicit assumption).

FAIL if any of these is missing, or if every single finding is labelled blocking.
