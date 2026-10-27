# Test Plan — Cart quantity limits

> Task: cart-quantity-limits-1a2b3c

## Scope
- **In scope:** REQ-1 … REQ-4 (REQ-4 built on the default reading until Q1 is answered)
- **Out of scope:** none
- **Blocked:** none

## Assumptions
- **A1** (Stage 1) — synchronous recalculation; TC-E2E-001 asserts without polling.
- **A2 (Stage 2)** — threshold compared to the subtotal before discounts, in RUB.

## Risk Assessment
| REQ | Impact | Probability | Score | Zone | Priority | Depth / rationale |
|---|---|---|---|---|---|---|
| REQ-1 | 3 | 3 | 9 | MEDIUM | P2 | BVA on 1..20 |
| REQ-2 | 3 | 3 | 9 | MEDIUM | P2 | Error message + unchanged state |
| REQ-3 | 4 | 3 | 12 | HIGH | P1 | Money: unit math + one journey |
| REQ-4 | 4 | 4 | 16 | CRITICAL | P0 | Money + open Q1: boundary 4999.99/5000 |

## Traceability Matrix
| REQ | Test cases | Techniques | Status |
|---|---|---|---|
| REQ-1 | TC-UNIT-001 | BVA | covered |
| REQ-2 | TC-API-001 | EP | covered |
| REQ-3 | TC-UNIT-002, TC-E2E-001 | EP | covered |
| REQ-4 | TC-UNIT-003 | BVA | covered |

## Pyramid Allocation
| Level | Cases | Share of automated |
|---|---|---|
| Unit | 3 | 60% |
| API | 1 | 20% |
| E2E | 1 | 20% |

Rationale: limits and money math are pure functions; the error contract is API; one journey proves the UI shows the server's subtotal.

## Entry and Exit Criteria
- **Entry:** cart service on staging
- **Exit:** all P0/P1 cases pass; no open Blocking review finding

## Case Location
- test-cases-unit.md, test-cases-api.md, test-cases-e2e.md
