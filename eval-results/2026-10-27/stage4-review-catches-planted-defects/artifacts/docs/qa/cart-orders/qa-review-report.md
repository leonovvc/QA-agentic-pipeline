# QA Review — Cart limits, shipping and order cancellation

Scope: documentation only (test plan + 7 test cases). No autotests exist, so there is no autotest review.
Source of truth: `spec-source.md` (re-read independently), then `spec-gap-report.md` and `spec-annotated.md`.
Note: `.agents/qa-project-context.md` does not exist; output language defaulted to English as requested.

## Verdict
**Not ready for automation.** The plan marks 6 of 6 requirements "covered". Re-derived from the spec, none is fully covered: 5 are partially covered, and REQ-6 has no coverage of its negative paths or of ownership (A3). There are 7 cases for 6 requirements, and 1 of them (TC-API-002) is not executable as written.

## Traceability Summary
Re-derived from the spec: 6 statements, which match REQ-1…REQ-6. I found no whole statement that Stage 1 dropped. Stage 1 did miss two implicit rules, listed under Findings (R-9, R-10).

0 of 6 fully covered, 5 partially covered, 1 effectively not covered. "Covered" in the plan's matrix is overstated for every row.

| REQ | Verdict | Cases | Gap |
|---|---|---|---|
| REQ-1 | partial | TC-UNIT-001 | only valid boundaries 1 and 20; no 0/21 (R-3) |
| REQ-2 | partial | TC-API-001, TC-API-002 | 002 has no checkable oracle; no UI display check (R-2, R-4) |
| REQ-3 | partial | TC-UNIT-002 | one partition; "recalculated after every change" untested (R-6) |
| REQ-4 | partial | TC-E2E-002 | only at E2E; one boundary pair; discount interaction unspecified (R-7, R-9) |
| REQ-5 | partial, depends on Q1 | TC-UNIT-003 | one case for four rules; no rounding case; no cart-level check (R-8) |
| REQ-6 | NOT covered (negative paths) | TC-E2E-001 | only Paid→Cancelled; forbidden cancels and Created→Cancelled missing (R-1) |
| A3 (403 for non-owner) | NOT covered | — | no case traces A3 (R-5) |

## Findings

### Blocking

**R-1** [Blocking] REQ-6, spec §6 — the spec states a failure mode, "a Shipped or Delivered order cannot be cancelled", and no case covers it. The Created → Cancelled path and the forward transitions (Created→Paid→Shipped→Delivered) are also untested. State transition testing is named in the plan, but only 1 valid transition of roughly 6 is exercised, and no invalid transition. → Add a state-transition set at API level (or unit, if there is a state-machine function): cancel from Created and Paid are accepted; cancel from Shipped and Delivered are rejected with the order state unchanged. Keep TC-E2E-001 as the single UI journey.

**R-2** [Blocking] TC-API-002, REQ-2 — expected result is "validation works correctly", which is not observable. A case that cannot fail cannot be automated. → Rewrite to match TC-API-001: status code, the exact message "Quantity must be between 1 and 20", and the quantity staying at 2.

**R-3** [Blocking] TC-UNIT-001, REQ-1 — boundary value analysis is named, but only the valid boundaries (1, 20) are tested. The invalid boundaries 0 and 21 are the ones that catch off-by-one defects (`<` vs `<=`). The plan's matrix credits REQ-1 with BVA while the cases for 0/21 sit under REQ-2 at the API level only, so the validation function itself is never tested at its edges. → Add 0 and 21 (and ideally 2 and 19, one nominal value) to the unit parametrization, each with a distinct expected result. Add TC-UNIT-001 to the REQ-2 trace.

**R-5** [Blocking] A3 / security lens A01, spec §6 — the gap report names broken access control (another user cancelling an order) as the applicable OWASP risk and writes A3 for it. No test case traces A3. The security row produced an assumption but no negative case. → Add an API case: user B cancels user A's Paid order → 403, status unchanged. Also confirm 403 is right (vs 404), because A3 is only an assumption.

### Major

**R-4** [Major] REQ-2, spec §2 — the spec says the message is *shown* to the customer and the previous quantity is kept. Only the API response is tested; nothing checks that the UI displays the message and restores the previous quantity. Also, `422` in TC-API-001 is not in the spec and is not listed as an assumption. → Add `422` as an assumption (A4) or ask the owner; decide on one UI-level check (see Disputed 3).

**R-6** [Major] TC-UNIT-002, REQ-3 (P1) — a single case with a single "multiple lines" partition. Not covered: single line; empty cart (subtotal 0); the "recalculated after every change" behavior (change quantity, remove a line, add a line); amounts with kopecks that expose rounding. → Add partitions, and at least one API case that changes a line and re-reads the subtotal.

**R-7** [Major] TC-E2E-002, REQ-4 (P0) — misallocated and thin. The shipping rule is pure arithmetic on a number and is tested only through the browser, which is the slowest and least diagnostic level. Only one boundary pair is covered. → Move the boundary cases to unit/API: 0 (empty cart), 4999.99, 5000.00, 5000.01, and a clear below-threshold value, e.g. 1000. Keep at most one E2E check that the shipping line appears. Related: R-9. Also split: two behaviors in one case (see R-11).

**R-8** [Major] TC-UNIT-003, REQ-5 (P0) — (a) one case covers four rules, so a failure does not say which rule broke; (b) A1 says rounding is half-up to 0.01 ₽, but no case has an amount that rounds (e.g. 3000.10 × 5% = 150.005 → 150.01), so the main P0 uncertainty (Q1) is untested; (c) there is no cart-level check that the discount appears in the total, and no check of A2 (sale flag from the pricing service) beyond a boolean argument; (d) the plan marks REQ-5 "covered" and does not mention that it depends on open Q1. → Split into one case per rule (or one parametrized case with a row per ID), add a rounding row tagged to A1/Q1, add an API/integration case for the sale flag, and mark the matrix row "covered under A1; Q1 open".

**R-9** [Major, Stage 1 miss] spec §3–§5 — the spec never says whether the 5000 ₽ free-shipping threshold uses the subtotal before or after the member discount. A member with a 5200 ₽ subtotal pays 4940 ₽ after discount, so the answer changes shipping from 0 to 300 ₽. Q1 asks only about the 3000 ₽ threshold. → Raise a new Q for the analyst; do not write expected results for this combination until answered; add one case when A5 is chosen.

**R-10** [Major, Stage 1 miss] spec §6 — the lifecycle lists Created, Paid, Shipped, Delivered, but the plan and TC-E2E-001 assert a "Cancelled" status that the spec never defines. Nothing is said about what happens to a payment on cancelling a Paid order (refund). → Raise a Q: does the Cancelled state exist, and is a refund in scope? The assertion in TC-E2E-001 is based on an unlisted assumption.

**R-12** [Major] test-plan.md — the plan is thin: the Pyramid Allocation section gives counts ("Unit 3, API 2, E2E 2") with no per-case justification; there are no entry criteria; the risk table "Depth / rationale" column is one-liners that do not state how many techniques or levels each zone requires. The two CRITICAL (P0) requirements are covered by one case each at a single level. The distribution is 7 cases with 2 E2E, and both P0/P1 logic requirements REQ-4/REQ-6 are tested at E2E only. → Expand the allocation with a one-line reason per case, add entry criteria, and give P0 requirements cases at at least two levels.

**R-13** [Major] security lens, A06 — the gap report says negative or huge quantities are "covered by REQ-1", but REQ-1 has no negative, non-integer, non-numeric, or very large quantity (e.g. -1, 2.5, "abc", 2147483648) case. → Add API negative cases for these inputs, with the expected rejection.

### Minor

**R-11** [Minor] TC-E2E-002 — one case with two scenarios (4999.99 and 5000.00 carts) and vague preconditions ("carts with subtotals…" — which items and prices produce them?). Failure of one blocks the report on the other. → Make it a parametrized case or two cases, with concrete line items (e.g. 1 × 4999.99).

**R-14** [Minor] TC-UNIT-001 — the title "Quantity limits are enforced" and the expected result "both are valid" do not state the invalid side; after R-3 the title should say what is accepted and rejected. TC-UNIT-002 Test data is written as expressions rather than line items (price, quantity).

**R-15** [Minor] test-plan.md — Scope has no out-of-scope or blocked items, though REQ-5 is blocked in part by Q1. The "Assumptions" section only points to the gap report instead of listing the content of A1–A3.

**R-16** [Minor] TC-E2E-001 — step 2 combines click and confirm, and the confirmation dialog is not mentioned in the spec. Clarify whether a confirmation exists.

## Disputed — Needs Human Decision

1. **Priority of REQ-1 and REQ-2 (P2).** Writer: quantity limits are low-impact input validation (impact 3), so P2 and light depth. Reviewer: A06 in the gap report treats unbounded quantities as a security risk, and the server-side limit is the only protection. That argues for P1 and negative-input cases (R-13). At stake: P2 means a lighter, possibly skipped regression; P1 adds roughly 4–6 cheap API cases.

2. **Write REQ-5 rounding cases now or wait for Q1.** Writer: proceed on assumption A1 (half-up, threshold before discount). Reviewer: proceed with A1 but tag the rounding rows to A1/Q1 so they are easy to find and change; waiting would leave a P0 requirement without automation. At stake: if the owner chooses a different rounding rule, the tagged rows need rewriting; if cases wait, the most expensive money rule stays untested.

3. **Does REQ-2 need an E2E/UI check?** Writer: the API cases cover it (server-side validation), so no E2E. Reviewer: the spec says the message is *shown*, which only a UI-level check proves; one component-level or E2E check is enough. At stake: E2E budget and maintenance cost vs. a possible UI regression that is never caught while the API stays correct.

## Readability
Language is English; IDs and identifiers are untranslated; all eight fields are present in every case. Exceptions: R-2 (non-observable expected result), R-11 and R-14 (vague data and preconditions, two behaviors in one case), R-16.

## Autotest Review
Not applicable — no autotests exist yet. No autotest-summary.md to cross-check.

## Recommended order before automating
1. Fix R-1, R-2, R-3, R-5 (the Blocking items).
2. Send R-9, R-10 (and the `422`/`403` choice) to the spec owner together with Q1.
3. Rework levels for REQ-4/REQ-6 (R-7, R-12), then re-review only the changed items.
