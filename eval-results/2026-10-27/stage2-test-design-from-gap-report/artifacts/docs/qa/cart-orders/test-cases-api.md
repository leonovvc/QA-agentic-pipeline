# Test cases — API level (cart-orders)

Conventions: endpoint paths and field names below are **logical placeholders** (A6); `autotest-builder` maps them to the real routes. Users: `U1` (customer, owner of the cart/order), `U2` (another customer, not the owner). "4xx" means any client-error status; the spec does not fix the exact code (A6). Cases marked **[assumption-based]** depend on an assumption listed in `test-plan.md`.

Logical operations:
- `PATCH /carts/{cartId}/lines/{lineId}` with body `{"quantity": <value>}` — set line quantity
- `GET /carts/{cartId}` — returns `lines[].quantity`, `subtotal`, `memberDiscount`, `shippingCost`
- `POST /orders/{orderId}/cancel` — cancel an order as the authenticated user
- `GET /orders/{orderId}` — returns `status`

## REQ-1 / REQ-2 / REQ-3 — Quantity and subtotal

### TC-API-001: Setting a valid quantity updates the line and recalculates the subtotal
- **Traces:** REQ-1, REQ-3
- **Technique:** Equivalence partitioning — valid class "quantity within 1..20"; recalculation after a change
- **Level:** API — proves the stored line and the recalculated subtotal come back through the contract
- **Priority:** P1
- **Preconditions:** Cart `C1` of `U1` has line `L1`, price `1000.00`, quantity `2`; subtotal is `2000.00`
- **Test data:** requested quantity `3`
- **Steps:**
  1. As `U1`, `PATCH /carts/C1/lines/L1` with `{"quantity": 3}` → Expected: status `200`
  2. `GET /carts/C1` → Expected: `lines[L1].quantity = 3`, `subtotal = 3000.00`
- **Expected result:** Line `L1` quantity is `3` and `subtotal` is `3000.00`

### TC-API-002: Quantity 21 is rejected with the spec message and the previous quantity is kept
- **Traces:** REQ-2
- **Technique:** Boundary value analysis — `quantity`, max+1 (21), checking message and unchanged state through the contract
- **Level:** API — the rejection response and the unchanged stored state are the contract the UI relies on
- **Priority:** P2
- **Preconditions:** Cart `C1` of `U1` has line `L1`, price `1000.00`, quantity `2`
- **Test data:** requested quantity `21`
- **Steps:**
  1. As `U1`, `PATCH /carts/C1/lines/L1` with `{"quantity": 21}` → Expected: 4xx status, error message `Quantity must be between 1 and 20`
  2. `GET /carts/C1` → Expected: `lines[L1].quantity = 2`, `subtotal = 2000.00`
- **Expected result:** The request is rejected with a 4xx and the message `Quantity must be between 1 and 20`; quantity stays `2`

### TC-API-003: Negative quantity is rejected and the previous quantity is kept
- **Traces:** REQ-1
- **Technique:** Security negative — OWASP A06 Insecure Design (quantity abuse: negative value); equivalence partitioning — invalid class "negative"
- **Level:** API — server-side validation must hold regardless of what the client sends
- **Priority:** P1
- **Preconditions:** Cart `C1` of `U1` has line `L1`, price `1000.00`, quantity `2`
- **Test data:** requested quantity `-5`
- **Steps:**
  1. As `U1`, `PATCH /carts/C1/lines/L1` with `{"quantity": -5}` → Expected: 4xx status, error message `Quantity must be between 1 and 20`
  2. `GET /carts/C1` → Expected: `lines[L1].quantity = 2`, `subtotal = 2000.00`
- **Expected result:** Rejected with a 4xx; quantity stays `2`; subtotal stays `2000.00` (no negative line total)

### TC-API-004: Quantity 2147483648 (32-bit integer max + 1) is rejected without a server error
- **Traces:** REQ-1
- **Technique:** Security negative — OWASP A06 Insecure Design (quantity abuse: huge value); boundary value analysis — int32 overflow
- **Level:** API — overflow and parsing happen at the request boundary
- **Priority:** P1
- **Preconditions:** Cart `C1` of `U1` has line `L1`, price `1000.00`, quantity `2`
- **Test data:** requested quantity `2147483648`
- **Steps:**
  1. As `U1`, `PATCH /carts/C1/lines/L1` with `{"quantity": 2147483648}` → Expected: 4xx status (not 5xx), error message `Quantity must be between 1 and 20`
  2. `GET /carts/C1` → Expected: `lines[L1].quantity = 2`, `subtotal = 2000.00`
- **Expected result:** Rejected with a 4xx (no 5xx); quantity stays `2`; subtotal stays `2000.00`

### TC-API-005: Quantity 99999999999999999999 (beyond 64-bit) is rejected without a server error
- **Traces:** REQ-1
- **Technique:** Security negative — OWASP A06 Insecure Design (quantity abuse: huge value); boundary value analysis — int64 overflow
- **Level:** API — a different parser failure mode from int32 overflow (TC-API-004); only visible at the request boundary
- **Priority:** P1
- **Preconditions:** Cart `C1` of `U1` has line `L1`, price `1000.00`, quantity `2`
- **Test data:** requested quantity `99999999999999999999` (sent as a JSON number)
- **Steps:**
  1. As `U1`, `PATCH /carts/C1/lines/L1` with `{"quantity": 99999999999999999999}` → Expected: 4xx status (not 5xx)
  2. `GET /carts/C1` → Expected: `lines[L1].quantity = 2`, `subtotal = 2000.00`
- **Expected result:** Rejected with a 4xx (no 5xx); quantity stays `2`; subtotal stays `2000.00`

### TC-API-006: Non-integer quantity 2.5 is rejected and the previous quantity is kept **[assumption-based: A5]**
- **Traces:** REQ-1, A5
- **Technique:** Security negative — OWASP A06 Insecure Design (quantity abuse: non-integer); equivalence partitioning — invalid class "non-integer number"
- **Level:** API — type validation at the request boundary
- **Priority:** P1
- **Preconditions:** Cart `C1` of `U1` has line `L1`, price `1000.00`, quantity `2`
- **Test data:** requested quantity `2.5`
- **Steps:**
  1. As `U1`, `PATCH /carts/C1/lines/L1` with `{"quantity": 2.5}` → Expected: 4xx status (not 5xx); the error message text is NOT asserted (not specified, OP-1)
  2. `GET /carts/C1` → Expected: `lines[L1].quantity = 2`, `subtotal = 2000.00`
- **Expected result:** Rejected with a 4xx; quantity stays `2`; subtotal stays `2000.00`

### TC-API-007: Non-numeric quantity "abc" is rejected and the previous quantity is kept **[assumption-based: A5]**
- **Traces:** REQ-1, A5
- **Technique:** Security negative — OWASP A06 Insecure Design (quantity abuse: wrong type); equivalence partitioning — invalid class "non-numeric string"
- **Level:** API — type validation at the request boundary
- **Priority:** P1
- **Preconditions:** Cart `C1` of `U1` has line `L1`, price `1000.00`, quantity `2`
- **Test data:** requested quantity `"abc"` (JSON string)
- **Steps:**
  1. As `U1`, `PATCH /carts/C1/lines/L1` with `{"quantity": "abc"}` → Expected: 4xx status (not 5xx); the error message text is NOT asserted (OP-1)
  2. `GET /carts/C1` → Expected: `lines[L1].quantity = 2`, `subtotal = 2000.00`
- **Expected result:** Rejected with a 4xx; quantity stays `2`; subtotal stays `2000.00`

## REQ-4 / REQ-5 — Shipping and discount wiring

### TC-API-008: Cart with subtotal 5000.00 returns shipping cost 0.00
- **Traces:** REQ-4
- **Technique:** Boundary value analysis — shipping threshold, exactly 5000.00 (wiring check; the rule itself is covered by TC-UNIT-008/009)
- **Level:** API — proves the cart endpoint exposes the shipping rule; the rule is not re-tested here
- **Priority:** P1
- **Preconditions:** `U1` is not a loyalty member; cart `C2` of `U1` has one line, price `2500.00`, quantity `2`
- **Test data:** subtotal `5000.00`
- **Steps:**
  1. As `U1`, `GET /carts/C2` → Expected: `subtotal = 5000.00`, `shippingCost = 0.00`
- **Expected result:** `shippingCost` is `0.00`

### TC-API-009: Loyalty member cart with subtotal 4000.00 returns memberDiscount 200.00 **[assumption-based: A2]**
- **Traces:** REQ-5, A2
- **Technique:** Decision table — rule R1 (member = Y, subtotal ≥ 3000 = Y, sale = N), wiring check
- **Level:** API — proves the membership and the sale flag from the pricing service reach the discount rule
- **Priority:** P0
- **Preconditions:** `U1` is a loyalty member; the pricing service stub reports sale period = `false`; cart `C3` of `U1` has one line, price `4000.00`, quantity `1`
- **Test data:** subtotal `4000.00`; sale flag `false`
- **Steps:**
  1. As `U1`, `GET /carts/C3` → Expected: `subtotal = 4000.00`, `memberDiscount = 200.00`
- **Expected result:** `memberDiscount` is `200.00`

### TC-API-010: Loyalty member cart during a sale period returns memberDiscount 0.00 **[assumption-based: A2]**
- **Traces:** REQ-5, A2
- **Technique:** Decision table — rule R2 (member = Y, subtotal ≥ 3000 = Y, sale = Y), wiring check
- **Level:** API — the sale flag comes from another service (A2); the integration is only visible here
- **Priority:** P0
- **Preconditions:** `U1` is a loyalty member; the pricing service stub reports sale period = `true`; cart `C3` of `U1` has one line, price `4000.00`, quantity `1`
- **Test data:** subtotal `4000.00`; sale flag `true`
- **Steps:**
  1. As `U1`, `GET /carts/C3` → Expected: `subtotal = 4000.00`, `memberDiscount = 0.00`
- **Expected result:** `memberDiscount` is `0.00`

## REQ-6 — Order cancellation

### TC-API-011: Owner cancels a Paid order **[assumption-based: A3, A7]**
- **Traces:** REQ-6, A3, A7
- **Technique:** State transition — valid: Paid → cancel, as the owner
- **Level:** API — status code and persisted order state are the contract; Paid is the riskier of the two cancellable states (money already taken)
- **Priority:** P1
- **Preconditions:** Order `O1` in status `Paid` belongs to `U1`
- **Test data:** actor `U1`
- **Steps:**
  1. As `U1`, `POST /orders/O1/cancel` → Expected: 2xx status
  2. As `U1`, `GET /orders/O1` → Expected: `status` is not `Paid`
- **Expected result:** Cancel returns 2xx; the stored order status is no longer `Paid` (the resulting state name is not specified, OP-2)

### TC-API-012: Owner cannot cancel a Shipped order
- **Traces:** REQ-6
- **Technique:** State transition — illegal: Shipped → cancel
- **Level:** API — the rejection and the unchanged stored state are the contract
- **Priority:** P1
- **Preconditions:** Order `O2` in status `Shipped` belongs to `U1`
- **Test data:** actor `U1`
- **Steps:**
  1. As `U1`, `POST /orders/O2/cancel` → Expected: 4xx status (exact code not specified, A6)
  2. As `U1`, `GET /orders/O2` → Expected: `status = "Shipped"`
- **Expected result:** Cancel is rejected with a 4xx; the order status is still `Shipped`

### TC-API-013: Another customer cannot cancel the order and gets 403 **[assumption-based: A3]**
- **Traces:** REQ-6, A3
- **Technique:** Security negative — OWASP A01 Broken Access Control (horizontal access: another user's order)
- **Level:** API — the access control is enforced server-side; the UI adds no protection
- **Priority:** P0
- **Preconditions:** Order `O3` in status `Created` belongs to `U1`; `U2` is a different authenticated customer
- **Test data:** actor `U2`; order `O3` (owner `U1`)
- **Steps:**
  1. As `U2`, `POST /orders/O3/cancel` → Expected: status `403`
  2. As `U1`, `GET /orders/O3` → Expected: `status = "Created"`
- **Expected result:** Status `403`; the order status is still `Created`
