# Unit test cases — Cart quantity limits

### TC-UNIT-001: Quantity 0 and 21 are rejected, 1 and 20 are accepted
- **Traces:** REQ-1
- **Technique:** Boundary value analysis — quantity: 0, 1, 20, 21
- **Level:** Unit — `validateQuantity(q)` is a pure function
- **Priority:** P2
- **Preconditions:** none
- **Test data:** q ∈ {0, 1, 20, 21}
- **Steps:**
  1. Call `validateQuantity(q)` for each value
- **Expected result:** 1 and 20 → valid; 0 and 21 → `QUANTITY_OUT_OF_RANGE`

### TC-UNIT-002: Subtotal equals the sum of price × quantity
- **Traces:** REQ-3, A1
- **Technique:** Equivalence partitioning — valid class "multiple lines"
- **Level:** Unit — arithmetic only
- **Priority:** P1
- **Preconditions:** none
- **Test data:** lines (100.00 × 2), (49.50 × 3)
- **Steps:**
  1. Call `subtotal(lines)`
- **Expected result:** 348.50

### TC-UNIT-003: Free shipping starts exactly at 5000
- **Traces:** REQ-4, A2
- **Technique:** Boundary value analysis — subtotal: 4999.99, 5000.00
- **Level:** Unit — `shippingCost(subtotal)` is a pure function
- **Priority:** P0
- **Preconditions:** standard shipping rate is 300.00
- **Test data:** 4999.99, 5000.00
- **Steps:**
  1. Call `shippingCost(subtotal)` for each value
- **Expected result:** 4999.99 → 300.00; 5000.00 → 0.00
