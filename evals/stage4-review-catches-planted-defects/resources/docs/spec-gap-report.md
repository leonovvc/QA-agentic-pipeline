# Spec Gap Analysis — Cart limits, shipping and order cancellation

## Source
Pasted text (spec-source.md), 6 numbered statements.

## Testability Score: 4
Ranges, amounts and states are explicit; rounding and the sale-period source are not.

## Requirements Inventory
| ID | Spec location | Requirement | Acceptance criterion | Testable |
|---|---|---|---|---|
| REQ-1 | §1 | Quantity per line is 1 to 20 | 1..20 accepted | yes |
| REQ-2 | §2 | Out-of-range quantity shows an error and keeps the previous value | Exact message; quantity unchanged | yes |
| REQ-3 | §3 | Subtotal = Σ price × quantity, recalculated after every change | Arithmetic | yes |
| REQ-4 | §4 | Shipping is 300 ₽, free when subtotal ≥ 5000 ₽ | 4999.99 → 300; 5000 → 0 | yes |
| REQ-5 | §5 | Members get 5% off when subtotal ≥ 3000 ₽, not during a sale | Discount amount by membership × threshold × sale | partly → Q1 |
| REQ-6 | §6 | Order lifecycle and cancellation rules | Allowed/forbidden transitions | yes |

## Blocking Gaps
(none)

## Contradictions
(none)

## Open Questions
### Track A — for you, now
(none)

### Track B — for the analyst / spec owner
1. **Q1** — §5: how is the member discount rounded, and is the 3000 ₽ threshold checked before or after it? Owner: product analyst.

## Assumptions Made to Proceed
1. **A1** — §5: the discount is rounded half-up to 0.01 ₽ and the threshold is checked on the subtotal before any discount.
2. **A2** — §5: "sale period" is a boolean flag provided by the pricing service.
3. **A3** — §6 (security lens, A01): only the order's owner can cancel it; any other user gets 403.

## Security Lens
Applicable: A01 Broken Access Control (cancelling another customer's order) → A3; A06 Insecure Design (negative or huge quantities) → covered by REQ-1. Not applicable: A07 (no authentication flow in scope), A04 (no sensitive data).

## Ready-for-Test-Design Checklist
- [x] Every in-scope user action has a success and failure outcome
- [x] Every acceptance criterion is objectively checkable
- [x] Edge cases are addressed or explicitly out of scope
- [x] No unresolved contradictions remain
