# Spec Gap Analysis — Cart quantity limits

## Source
Pasted text (spec-source.md), 4 numbered statements.

## Testability Score: 4
Ranges and messages are explicit; currency and rounding of the shipping threshold are not.

## Requirements Inventory
| ID | Spec location | Requirement | Acceptance criterion | Testable |
|---|---|---|---|---|
| REQ-1 | §1 | Quantity per cart line is 1 to 20 | Values 1..20 accepted | yes |
| REQ-2 | §2 | Out-of-range quantity shows an error and keeps the previous value | Exact message; quantity unchanged | yes |
| REQ-3 | §3 | Subtotal is recalculated after every quantity change | Subtotal = Σ price × quantity | yes |
| REQ-4 | §4 | Subtotal ≥ 5000 gives free shipping | Shipping = 0 when subtotal ≥ 5000 | partly → Q1 |

## Blocking Gaps
(none)

## Contradictions
(none)

## Open Questions
### Track A — for you, now
(none)

### Track B — for the analyst / spec owner
1. **Q1** — §4: is the 5000 threshold in RUB, and is it compared before or after discounts? Owner: product analyst.

## Assumptions Made to Proceed
1. **A1** — §3: recalculation is synchronous; the new subtotal is visible immediately after the change.

## Security Lens
Applicable: A06 Insecure Design (negative quantities) — covered by REQ-1 boundaries; no other triggers (no auth, no personal data).

## Ready-for-Test-Design Checklist
- [x] Every in-scope user action has a success and failure outcome
- [x] Every acceptance criterion is objectively checkable
- [x] Edge cases are addressed or explicitly out of scope
- [x] No unresolved contradictions remain
