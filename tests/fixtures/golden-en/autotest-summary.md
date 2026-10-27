# Autotest Summary — Cart quantity limits

## Stack Profile
- Language: TypeScript; unit: Vitest (`src/**/*.test.ts`); API + E2E: Playwright (`e2e/`)

## Mapping
| TC | File | Test | Status | Notes |
|---|---|---|---|---|
| TC-UNIT-001 | src/cart/quantity.test.ts | TC-UNIT-001: quantity boundaries | passed | |
| TC-UNIT-002 | src/cart/subtotal.test.ts | TC-UNIT-002: subtotal | passed | |
| TC-UNIT-003 | src/cart/shipping.test.ts | TC-UNIT-003: free shipping threshold | passed | |
| TC-API-001 | e2e/api/cart.spec.ts | TC-API-001: 422 on quantity 21 | not run | staging URL not available here |
| TC-E2E-001 | e2e/cart.spec.ts | TC-E2E-001: subtotal updates | not run | staging URL not available here |

## Commands Run
- `npx vitest run src/cart` — exit 0

## Suspected Product Defects
(none)

## Allocation Disagreements
(none)
