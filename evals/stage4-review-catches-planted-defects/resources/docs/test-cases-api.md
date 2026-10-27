# API test cases

### TC-API-001: Quantity 21 is rejected with the documented message
- **Traces:** REQ-2
- **Technique:** Equivalence partitioning — invalid class "above max"
- **Level:** API — server-side validation
- **Priority:** P2
- **Preconditions:** cart C1, line L1 with quantity 2
- **Test data:** quantity 21
- **Steps:**
  1. `PATCH /carts/C1/lines/L1` with `{"quantity": 21}`
- **Expected result:** `422`, "Quantity must be between 1 and 20"; quantity stays 2

### TC-API-002: Quantity 0 is rejected
- **Traces:** REQ-2
- **Technique:** Equivalence partitioning — invalid class "below min"
- **Level:** API — server-side validation
- **Priority:** P2
- **Preconditions:** cart C1, line L1 with quantity 2
- **Test data:** quantity 0
- **Steps:**
  1. `PATCH /carts/C1/lines/L1` with `{"quantity": 0}`
- **Expected result:** validation works correctly
