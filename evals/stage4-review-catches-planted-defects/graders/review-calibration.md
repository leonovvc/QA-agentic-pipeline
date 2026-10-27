---
type: llm
weight: 2
focus: { source: file, path: docs/qa/cart-orders/qa-review-report.md }
---

This is an independent QA review of a test plan. Planted problems: REQ-6 (order state machine) has only one valid-transition case and no illegal-transition case (e.g. cancelling a Shipped order); TC-UNIT-001 claims boundary value analysis for quantity 1..20 but tests only 1 and 20; the free-shipping threshold, a pure calculation, is tested only at E2E (TC-E2E-002); TC-API-002's expected result is "validation works correctly".

PASS if all hold: (a) at least three of the four planted problems are reported as findings with a citation (REQ or TC ID); (b) the missing illegal-transition coverage or the incomplete BVA is rated Blocking or Major, not Minor; (c) the "Disputed" section, if non-empty, contains only genuine judgment calls stated with both positions — objectively missing coverage is not placed there; (d) the review states how many requirements are covered.
FAIL otherwise.
