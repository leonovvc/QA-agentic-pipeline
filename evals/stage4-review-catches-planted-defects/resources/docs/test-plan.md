# Test Plan — Cart limits, shipping and order cancellation

> Task: cart-orders

## Scope
- **In scope:** REQ-1 … REQ-6

## Assumptions
- **A1**, **A2**, **A3** (Stage 1) as stated in the gap report.

## Risk Assessment
| REQ | Impact | Probability | Score | Zone | Priority | Depth / rationale |
|---|---|---|---|---|---|---|
| REQ-1 | 3 | 3 | 9 | MEDIUM | P2 | Boundaries of 1..20 |
| REQ-2 | 3 | 3 | 9 | MEDIUM | P2 | Error message |
| REQ-3 | 4 | 3 | 12 | HIGH | P1 | Arithmetic |
| REQ-4 | 5 | 3 | 15 | CRITICAL | P0 | Threshold |
| REQ-5 | 5 | 3 | 15 | CRITICAL | P0 | Three conditions |
| REQ-6 | 4 | 3 | 12 | HIGH | P1 | Lifecycle |

## Traceability Matrix
| REQ | Test cases | Techniques | Status |
|---|---|---|---|
| REQ-1 | TC-UNIT-001 | BVA | covered |
| REQ-2 | TC-API-001, TC-API-002 | EP | covered |
| REQ-3 | TC-UNIT-002 | EP | covered |
| REQ-4 | TC-E2E-002 | BVA | covered |
| REQ-5 | TC-UNIT-003 | Decision table | covered |
| REQ-6 | TC-E2E-001 | State transition | covered |

## Pyramid Allocation
Unit 3, API 2, E2E 2.

## Entry and Exit Criteria
- **Exit:** all P0/P1 cases pass.

## Case Location
test-cases-unit.md, test-cases-api.md, test-cases-e2e.md
