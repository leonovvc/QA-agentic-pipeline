# Unit test cases

### TC-UNIT-001: Quantity limits are enforced
- **Traces:** REQ-1
- **Technique:** Boundary value analysis — quantity: 1, 20
- **Level:** Unit — `isValidQuantity` is a pure function
- **Priority:** P2
- **Preconditions:** none
- **Test data:** 1, 20
- **Steps:**
  1. Call `isValidQuantity` for 1 and 20
- **Expected result:** both are valid

### TC-UNIT-002: Subtotal is the sum of price × quantity
- **Traces:** REQ-3
- **Technique:** Equivalence partitioning — valid class "multiple lines"
- **Level:** Unit — arithmetic only
- **Priority:** P1
- **Preconditions:** none
- **Test data:** (100.00 × 2), (49.50 × 3)
- **Steps:**
  1. Call `subtotal`
- **Expected result:** 348.50

### TC-UNIT-003: Member discount decision table
- **Traces:** REQ-5, A1, A2
- **Technique:** Decision table — member × subtotal ≥ 3000 × sale, rules R1–R4
- **Level:** Unit — pure function `memberDiscount`
- **Priority:** P0
- **Preconditions:** none
- **Test data:** R1 member/3000.00/no sale → 150.00; R2 non-member/3000.00/no sale → 0; R3 member/2999.99/no sale → 0; R4 member/3000.00/sale → 0
- **Steps:**
  1. Call `memberDiscount` for R1–R4
- **Expected result:** R1 → 150.00; R2–R4 → 0.00
