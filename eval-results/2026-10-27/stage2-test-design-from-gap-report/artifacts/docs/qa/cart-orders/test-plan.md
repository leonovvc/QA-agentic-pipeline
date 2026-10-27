# Test plan — Cart limits, shipping and order cancellation (cart-orders)

Output language: English. Inputs: `spec-source.md`, `spec-gap-report.md`, `spec-annotated.md`.

## Scope

**In scope (all six requirements):**
- REQ-1 Quantity per line 1..20, including quantity abuse (negative, huge, non-integer, non-numeric)
- REQ-2 Out-of-range error message and kept previous quantity
- REQ-3 Subtotal calculation and recalculation after every change
- REQ-4 Shipping 300 ₽, free from 5000 ₽
- REQ-5 Loyalty member 5% discount (threshold 3000 ₽, not in a sale period)
- REQ-6 Order lifecycle and cancellation rules, including the owner-only cancel check (security lens A01)

**Out of scope (with reason):**
- Authentication flows (OWASP A07) and sensitive-data handling (A04): not applicable per the gap report's Security Lens.
- Refund or payment reversal when a Paid order is cancelled: the spec says nothing about it (OP-4).
- Non-functional checks (performance, accessibility, visual): no requirement states them.

**Blocked:** none. The gap report has no Blocking Gaps. REQ-5 is "partly testable" because of Q1; it is tested on A1/A2, and the cases that depend on them are marked **[assumption-based]**.

**Deliberate omissions (stated, not silent):**
- Quantity 2 and 19 (min+1, max-1) and a mid-range value are not written as separate cases: they are in the same valid partition as 1 and 20 and would add no coverage.
- Non-owner cancel of a Paid order is not a second case: it is the same attacker partition as TC-API-013 (another user's order). If a defect shows ownership is checked only in some states, add it.
- Backward state moves (for example Shipped → Paid) are not tested: the spec does not forbid or allow them explicitly (OP-7).

## Assumptions

### Inherited from Stage 1 (the test design is built on these)
| ID | Assumption | Cases that depend on it |
|---|---|---|
| A1 | Member discount is rounded half-up to 0.01 ₽; the 3000 ₽ threshold is checked on the subtotal before any discount (related to Q1) | TC-UNIT-012, 013, 015, 016 |
| A2 | "Sale period" is a boolean flag provided by the pricing service | TC-UNIT-010 to 016, TC-API-009, TC-API-010 |
| A3 | Only the order's owner can cancel it; any other user gets 403 | TC-API-011, TC-API-013 |

**Q1** (Track B, unresolved): how the member discount is rounded and whether the 3000 ₽ threshold is checked before or after the discount. Not a Blocking Gap. The REQ-5 cases that depend on it will need re-checking when the product analyst answers.

### Stage 2's own assumptions
| ID | Assumption | Cases that depend on it |
|---|---|---|
| A4 (Stage 2) | The free-shipping threshold (5000 ₽) is evaluated on the subtotal before the member discount, consistent with A1. The spec says "subtotal" in both rules | TC-UNIT-016 |
| A5 (Stage 2) | A non-integer or non-numeric quantity (2.5, "abc") is treated like an out-of-range one: it is rejected and the previous quantity is kept. The error message for it is not asserted | TC-API-006, TC-API-007, TC-MAN-001 |
| A6 (Stage 2) | The spec defines no API. Endpoint paths and field names in the API cases are logical placeholders, and a rejection is asserted as "any 4xx, never 5xx", not a specific code. Only 403 (from A3) is asserted exactly | all TC-API |
| A7 (Stage 2) | A successful cancel is asserted only as "request succeeds and the status is no longer the previous one". The name of the state after cancellation is not in the spec's lifecycle | TC-UNIT-017, 018, TC-API-011, TC-E2E-003 |
| A8 (Stage 2) | Skipping a state (Created → Shipped) is not allowed; this is read from the spec's ordered lifecycle "Created → Paid → Shipped → Delivered" | TC-UNIT-024 |

### Open points for the spec owner (proposed for Track B; not decided here)
| ID | Open point | Handling in this plan |
|---|---|---|
| OP-1 | Error message for a non-integer or non-numeric quantity | Message not asserted; invariant only (rejected, quantity kept) |
| OP-2 | State after cancellation (is there a "Cancelled" state?) | Asserted only as "status changed" (A7) |
| OP-3 | Cancelling an already-cancelled order; whether a cancel control remains | Not asserted; explored in TC-MAN-001 |
| OP-4 | Refund behavior when a Paid order is cancelled | Out of scope; explored in TC-MAN-001 |
| OP-5 | How free shipping is displayed ("0 ₽" or "Free") | E2E asserts the numeric amount only |
| OP-6 | Subtotal and shipping for an empty cart | Not asserted; explored in TC-MAN-001 |
| OP-7 | Whether backward or repeated state moves are allowed; precedence of 403 versus "state not cancellable" when a non-owner cancels a Shipped order | Not tested |
| OP-8 | Rounding of a subtotal when a price has more than two decimals | Not tested; prices in test data have at most two decimals |

## Risk Assessment

Impact and Probability follow `risk-based-testing` (Pipeline Mode). Every open Q or A touching a requirement adds 1 to Probability.

| REQ | Impact (1-5) | Probability (1-5) | Score | Zone | Priority | Depth / rationale |
|---|---|---|---|---|---|---|
| REQ-1 | 4 | 3 | 12 | HIGH | P1 | Quantity abuse (A06) can corrupt totals; off-by-one at 1 and 20. All four boundaries plus every abuse partition (negative, int32, int64, non-integer, non-numeric); A5 adds 1 to Probability |
| REQ-2 | 3 | 3 | 9 | MEDIUM | P2 | Exact message and kept value; one unit case, one API case, one E2E case for the display. A5/OP-1 adds 1 to Probability |
| REQ-3 | 5 | 2 | 10 | HIGH | P1 | Money. Multi-line sum, fractional-price precision, recalculation after change |
| REQ-4 | 5 | 3 | 15 | CRITICAL | P0 | Money. Both sides of the 5000 threshold; interaction with the discount rests on A4 (adds 1 to Probability) |
| REQ-5 | 5 | 5 | 25 | CRITICAL | P0 | Money plus three conditions plus open Q1, A1 and A2. Full decision table, both threshold boundaries, half-up rounding, wiring of the sale flag |
| REQ-6 | 4 | 4 | 16 | CRITICAL | P0 | Irreversible action plus access control (A01) plus A3. Every valid and illegal cancel transition, the owner/non-owner split, one E2E journey |

## Traceability Matrix

| REQ | Test cases | Techniques | Status |
|---|---|---|---|
| REQ-1 | TC-UNIT-001, 002, 003, 004; TC-API-001, 003, 004, 005, 006, 007; TC-E2E-002; TC-MAN-001 | BVA, EP, security negative (A06), exploratory charter | covered (TC-API-006/007 assumption-based on A5) |
| REQ-2 | TC-UNIT-005; TC-API-002; TC-E2E-001 | EP, BVA | covered |
| REQ-3 | TC-UNIT-006, 007; TC-API-001; TC-E2E-002 | EP | covered |
| REQ-4 | TC-UNIT-008, 009, 016; TC-API-008; TC-E2E-002 | BVA, decision table | covered (TC-UNIT-016 assumption-based on A4) |
| REQ-5 | TC-UNIT-010 to 016; TC-API-009, 010 | decision table, BVA, EP | covered, partly assumption-based on A1/A2; open Q1 |
| REQ-6 | TC-UNIT-017 to 024; TC-API-011, 012, 013; TC-E2E-003; TC-MAN-001 | state transition, security negative (A01), exploratory charter | covered (cancel cases assumption-based on A3/A7/A8) |

All six REQs are covered; none is blocked or out of scope.

## Pyramid Allocation

| Level | Cases | Share of automated cases |
|---|---|---|
| Unit | 24 | 60% (24 of 40) |
| API | 13 | 33% (13 of 40) |
| E2E | 3 | 8% (3 of 40) |
| Manual (not automated) | 1 | n/a |
| **Total** | **41** (40 automated + 1 manual) | |

Rationale: the feature is mostly business rules (ranges, thresholds, a discount decision table, a state machine), so they are proven at unit level, one case per partition, boundary, rule or transition. API holds only what the contract must prove: the abuse inputs and the unchanged state after rejection (A06), the owner-only 403 (A01), the cancel status codes, and one wiring check each for shipping and discount (including the sale flag from another service, A2). E2E is kept to three journeys the browser alone can prove: the error message display, the quantity-to-shipping golden path, and the cancel control. The E2E share (8%) is under the default 20% budget. The API-heavy abuse cases are not duplicated at unit level because the failure mode (parsing and overflow at the request boundary) lives at the API.

Technique detail: BVA on quantity (0, 1, 20, 21) and on both thresholds (2999.99/3000.00; 4999.99/5000.00); decision table for REQ-5 with four collapsed rules R1-R4; state transition for REQ-6 (3 valid moves, 2 valid cancels, 2 illegal cancels, 1 illegal skip).

## Entry and Exit Criteria

**Entry:**
- Code for the cart, shipping, discount and order-cancellation features is available on a test environment.
- The existing suite is green.
- Test data is available: customers `U1` (loyalty member and non-member variants) and `U2`; orders in each status; a pricing-service stub that can return sale period `true` and `false`.
- The real API routes are known so that A6 placeholders can be mapped.

**Exit:**
- All P0 and P1 cases pass (every TC-UNIT, TC-API and TC-E2E case with priority P0 or P1).
- All P2 cases pass or have a logged defect with a decision.
- No open P0 or P1 defect.
- Every REQ-1..REQ-6 row in the Traceability Matrix is covered, with zero unexplained gaps.
- Every assumption-based case is either confirmed by the spec owner's answer (Q1, OP-list) or reported as relying on an unconfirmed assumption in the Human Checkpoint Report.
- TC-MAN-001 is executed and its session note delivered to the spec owner.

## Case Location

No test-case system is in use. The cases are local files in `docs/qa/cart-orders/`:
- `/tmp/claude-eval-fePbxG/home/cwd/docs/qa/cart-orders/test-cases-unit.md` — TC-UNIT-001 to 024
- `/tmp/claude-eval-fePbxG/home/cwd/docs/qa/cart-orders/test-cases-api.md` — TC-API-001 to 013
- `/tmp/claude-eval-fePbxG/home/cwd/docs/qa/cart-orders/test-cases-e2e.md` — TC-E2E-001 to 003
- `/tmp/claude-eval-fePbxG/home/cwd/docs/qa/cart-orders/test-cases-manual.md` — TC-MAN-001
