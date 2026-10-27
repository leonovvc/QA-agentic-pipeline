# Test cases — Unit level (cart-orders)

Conventions: the unit cases describe pure business rules in logical terms (quantity-update rule, subtotal calculation, shipping rule, member-discount rule, order state machine). `autotest-builder` maps them to the real functions or classes. Amounts are in ₽. Cases marked **[assumption-based]** depend on an assumption listed in `test-plan.md`; if the assumption changes, only those cases change.

## REQ-1 / REQ-2 — Quantity per line

### TC-UNIT-001: Quantity 0 is rejected as below the minimum
- **Traces:** REQ-1
- **Technique:** Boundary value analysis — `quantity`, min-1 (0)
- **Level:** Unit — pure range rule, no I/O
- **Priority:** P1
- **Preconditions:** A cart line exists with current quantity 3
- **Test data:** requested quantity `0`; current quantity `3`
- **Steps:**
  1. Apply the quantity-update rule to the line with requested quantity `0`
- **Expected result:** The result is "rejected"; the line quantity is still `3`

### TC-UNIT-002: Quantity 1 is accepted (lower boundary)
- **Traces:** REQ-1
- **Technique:** Boundary value analysis — `quantity`, min (1)
- **Level:** Unit — pure range rule, no I/O
- **Priority:** P1
- **Preconditions:** A cart line exists with current quantity 3
- **Test data:** requested quantity `1`; current quantity `3`
- **Steps:**
  1. Apply the quantity-update rule to the line with requested quantity `1`
- **Expected result:** The result is "accepted"; the line quantity is `1`

### TC-UNIT-003: Quantity 20 is accepted (upper boundary)
- **Traces:** REQ-1
- **Technique:** Boundary value analysis — `quantity`, max (20)
- **Level:** Unit — pure range rule, no I/O
- **Priority:** P1
- **Preconditions:** A cart line exists with current quantity 3
- **Test data:** requested quantity `20`; current quantity `3`
- **Steps:**
  1. Apply the quantity-update rule to the line with requested quantity `20`
- **Expected result:** The result is "accepted"; the line quantity is `20`

### TC-UNIT-004: Quantity 21 is rejected as above the maximum
- **Traces:** REQ-1
- **Technique:** Boundary value analysis — `quantity`, max+1 (21)
- **Level:** Unit — pure range rule, no I/O
- **Priority:** P1
- **Preconditions:** A cart line exists with current quantity 3
- **Test data:** requested quantity `21`; current quantity `3`
- **Steps:**
  1. Apply the quantity-update rule to the line with requested quantity `21`
- **Expected result:** The result is "rejected"; the line quantity is still `3`

### TC-UNIT-005: Rejected quantity returns the exact error message and keeps the previous quantity
- **Traces:** REQ-2
- **Technique:** Equivalence partitioning — invalid class "above range", checking the message and state-preservation oracle
- **Level:** Unit — the message text and the "keep previous value" rule are pure logic
- **Priority:** P2
- **Preconditions:** A cart line exists with current quantity 7
- **Test data:** requested quantity `21`; current quantity `7`
- **Steps:**
  1. Apply the quantity-update rule to the line with requested quantity `21`
- **Expected result:** The error message is exactly `Quantity must be between 1 and 20`; the line quantity is still `7`

## REQ-3 — Subtotal

### TC-UNIT-006: Subtotal of several lines is the sum of price × quantity
- **Traces:** REQ-3
- **Technique:** Equivalence partitioning — valid class "multi-line cart"
- **Level:** Unit — pure arithmetic
- **Priority:** P1
- **Preconditions:** None (pure calculation)
- **Test data:** line A price `199.90` × quantity `3`; line B price `50.00` × quantity `2`
- **Steps:**
  1. Calculate the subtotal for lines A and B
- **Expected result:** Subtotal is exactly `699.70`

### TC-UNIT-007: Subtotal keeps exact cents for a fractional price
- **Traces:** REQ-3
- **Technique:** Equivalence partitioning — valid class "fractional price" (guards against binary floating-point error)
- **Level:** Unit — pure arithmetic
- **Priority:** P1
- **Preconditions:** None (pure calculation)
- **Test data:** one line, price `0.10` × quantity `3`
- **Steps:**
  1. Calculate the subtotal for the line
- **Expected result:** Subtotal is exactly `0.30` (not `0.30000000000000004` and not `0.3` rounded to another value)

## REQ-4 — Shipping

### TC-UNIT-008: Subtotal 4999.99 pays 300 ₽ shipping
- **Traces:** REQ-4
- **Technique:** Boundary value analysis — shipping threshold, max-1 below 5000.00 (4999.99)
- **Level:** Unit — pure threshold rule
- **Priority:** P0
- **Preconditions:** None (pure calculation)
- **Test data:** subtotal `4999.99`
- **Steps:**
  1. Calculate the shipping cost for subtotal `4999.99`
- **Expected result:** Shipping cost is `300.00`

### TC-UNIT-009: Subtotal 5000.00 ships free
- **Traces:** REQ-4
- **Technique:** Boundary value analysis — shipping threshold, exactly 5000.00
- **Level:** Unit — pure threshold rule
- **Priority:** P0
- **Preconditions:** None (pure calculation)
- **Test data:** subtotal `5000.00`
- **Steps:**
  1. Calculate the shipping cost for subtotal `5000.00`
- **Expected result:** Shipping cost is `0.00`

## REQ-5 — Loyalty member discount (decision table: member / subtotal ≥ 3000 / sale period)

Decision table (all columns A2-dependent; the outcome in columns R1 and the boundary cases also depends on A1):

| Rule | Member | Subtotal ≥ 3000 | Sale period | Outcome |
|---|---|---|---|---|
| R1 | Y | Y | N | 5% discount |
| R2 | Y | Y | Y | no discount |
| R3 | Y | N | – | no discount |
| R4 | N | – | – | no discount |

### TC-UNIT-010: Member, subtotal 4000.00, no sale gets a 200.00 discount
- **Traces:** REQ-5, A2
- **Technique:** Decision table — rule R1 (member = Y, subtotal ≥ 3000 = Y, sale = N)
- **Level:** Unit — pure discount rule; the sale flag is an input (A2)
- **Priority:** P0
- **Preconditions:** None (pure calculation)
- **Test data:** isMember `true`; subtotal `4000.00`; isSalePeriod `false`
- **Steps:**
  1. Calculate the member discount
- **Expected result:** Discount is `200.00` (5% of 4000.00)

### TC-UNIT-011: Member during a sale period gets no discount
- **Traces:** REQ-5, A2
- **Technique:** Decision table — rule R2 (member = Y, subtotal ≥ 3000 = Y, sale = Y)
- **Level:** Unit — pure discount rule; the sale flag is an input (A2)
- **Priority:** P0
- **Preconditions:** None (pure calculation)
- **Test data:** isMember `true`; subtotal `4000.00`; isSalePeriod `true`
- **Steps:**
  1. Calculate the member discount
- **Expected result:** Discount is `0.00`

### TC-UNIT-012: Member with subtotal 2999.99 gets no discount **[assumption-based: A1, A2]**
- **Traces:** REQ-5, A1, A2
- **Technique:** Boundary value analysis — discount threshold, min-1 (2999.99); decision table rule R3
- **Level:** Unit — pure threshold rule
- **Priority:** P0
- **Preconditions:** None (pure calculation)
- **Test data:** isMember `true`; subtotal `2999.99`; isSalePeriod `false`
- **Steps:**
  1. Calculate the member discount
- **Expected result:** Discount is `0.00`

### TC-UNIT-013: Member with subtotal exactly 3000.00 gets 150.00 discount **[assumption-based: A1, A2; Q1]**
- **Traces:** REQ-5, A1, A2
- **Technique:** Boundary value analysis — discount threshold, exactly 3000.00; decision table rule R1. Confirms the threshold is checked on the subtotal before the discount (A1): the discounted 2850.00 would be below 3000.
- **Level:** Unit — pure threshold rule
- **Priority:** P0
- **Preconditions:** None (pure calculation)
- **Test data:** isMember `true`; subtotal `3000.00`; isSalePeriod `false`
- **Steps:**
  1. Calculate the member discount
- **Expected result:** Discount is `150.00`

### TC-UNIT-014: Non-member with subtotal 4000.00 gets no discount
- **Traces:** REQ-5, A2
- **Technique:** Decision table — rule R4 (member = N)
- **Level:** Unit — pure discount rule
- **Priority:** P0
- **Preconditions:** None (pure calculation)
- **Test data:** isMember `false`; subtotal `4000.00`; isSalePeriod `false`
- **Steps:**
  1. Calculate the member discount
- **Expected result:** Discount is `0.00`

### TC-UNIT-015: Discount of 150.005 is rounded half-up to 150.01 **[assumption-based: A1; Q1]**
- **Traces:** REQ-5, A1, A2
- **Technique:** Equivalence partitioning — class "discount with a half-cent remainder"; rounding rule from A1
- **Level:** Unit — pure rounding rule
- **Priority:** P0
- **Preconditions:** None (pure calculation)
- **Test data:** isMember `true`; subtotal `3000.10` (5% = 150.005); isSalePeriod `false`
- **Steps:**
  1. Calculate the member discount
- **Expected result:** Discount is `150.01`

## REQ-4 × REQ-5 — Shipping threshold with discount

### TC-UNIT-016: Member with subtotal 5000.00 gets 250.00 discount and still ships free **[assumption-based: A1, A2, A4]**
- **Traces:** REQ-4, REQ-5, A1, A2, A4
- **Technique:** Decision table — interaction of rule R1 with the shipping threshold (shipping is evaluated on the subtotal before the discount, A4)
- **Level:** Unit — pure rule interaction
- **Priority:** P0
- **Preconditions:** None (pure calculation)
- **Test data:** isMember `true`; subtotal `5000.00` (after discount it would be 4750.00); isSalePeriod `false`
- **Steps:**
  1. Calculate the member discount and the shipping cost for the order
- **Expected result:** Discount is `250.00`; shipping cost is `0.00`

## REQ-6 — Order lifecycle and cancellation

State model: Created → Paid → Shipped → Delivered. Cancellation allowed from Created and Paid; forbidden from Shipped and Delivered.

### TC-UNIT-017: A Created order can be cancelled **[assumption-based: A7]**
- **Traces:** REQ-6, A7
- **Technique:** State transition — valid: Created → cancel
- **Level:** Unit — state-machine rule, no I/O
- **Priority:** P1
- **Preconditions:** An order exists in status `Created`
- **Test data:** order status `Created`; actor = the order's owner
- **Steps:**
  1. Request cancellation of the order
- **Expected result:** The request succeeds; the order status is no longer `Created` (the name of the resulting state is not specified, see OP-2)

### TC-UNIT-018: A Paid order can be cancelled **[assumption-based: A7]**
- **Traces:** REQ-6, A7
- **Technique:** State transition — valid: Paid → cancel
- **Level:** Unit — state-machine rule, no I/O
- **Priority:** P1
- **Preconditions:** An order exists in status `Paid`
- **Test data:** order status `Paid`; actor = the order's owner
- **Steps:**
  1. Request cancellation of the order
- **Expected result:** The request succeeds; the order status is no longer `Paid`

### TC-UNIT-019: A Shipped order cannot be cancelled
- **Traces:** REQ-6
- **Technique:** State transition — illegal: Shipped → cancel
- **Level:** Unit — state-machine rule, no I/O
- **Priority:** P1
- **Preconditions:** An order exists in status `Shipped`
- **Test data:** order status `Shipped`; actor = the order's owner
- **Steps:**
  1. Request cancellation of the order
- **Expected result:** The request is rejected; the order status is still `Shipped`

### TC-UNIT-020: A Delivered order cannot be cancelled
- **Traces:** REQ-6
- **Technique:** State transition — illegal: Delivered → cancel
- **Level:** Unit — state-machine rule, no I/O
- **Priority:** P1
- **Preconditions:** An order exists in status `Delivered`
- **Test data:** order status `Delivered`; actor = the order's owner
- **Steps:**
  1. Request cancellation of the order
- **Expected result:** The request is rejected; the order status is still `Delivered`

### TC-UNIT-021: Created order moves to Paid
- **Traces:** REQ-6
- **Technique:** State transition — valid: Created → Paid
- **Level:** Unit — state-machine rule, no I/O
- **Priority:** P1
- **Preconditions:** An order exists in status `Created`
- **Test data:** order status `Created`
- **Steps:**
  1. Advance the order to its next state
- **Expected result:** The order status is `Paid`

### TC-UNIT-022: Paid order moves to Shipped
- **Traces:** REQ-6
- **Technique:** State transition — valid: Paid → Shipped
- **Level:** Unit — state-machine rule, no I/O
- **Priority:** P1
- **Preconditions:** An order exists in status `Paid`
- **Test data:** order status `Paid`
- **Steps:**
  1. Advance the order to its next state
- **Expected result:** The order status is `Shipped`

### TC-UNIT-023: Shipped order moves to Delivered
- **Traces:** REQ-6
- **Technique:** State transition — valid: Shipped → Delivered
- **Level:** Unit — state-machine rule, no I/O
- **Priority:** P1
- **Preconditions:** An order exists in status `Shipped`
- **Test data:** order status `Shipped`
- **Steps:**
  1. Advance the order to its next state
- **Expected result:** The order status is `Delivered`

### TC-UNIT-024: A Created order cannot skip directly to Shipped **[assumption-based: A8]**
- **Traces:** REQ-6, A8
- **Technique:** State transition — illegal: Created → Shipped (skipping Paid)
- **Level:** Unit — state-machine rule, no I/O
- **Priority:** P2
- **Preconditions:** An order exists in status `Created`
- **Test data:** order status `Created`; target status `Shipped`
- **Steps:**
  1. Request a transition of the order directly to `Shipped`
- **Expected result:** The transition is rejected; the order status is still `Created`
