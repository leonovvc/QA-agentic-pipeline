# API test cases — Cart quantity limits

### TC-API-001: Out-of-range quantity returns 422 and keeps the previous quantity
- **Traces:** REQ-2
- **Technique:** Equivalence partitioning — invalid class "above max"
- **Level:** API — the error contract and unchanged state are server-side
- **Priority:** P2
- **Preconditions:** cart C1 has line L1 with quantity 2
- **Test data:** quantity 21
- **Steps:**
  1. `PATCH /carts/C1/lines/L1` with `{"quantity": 21}`
- **Expected result:** `422`, message "Quantity must be between 1 and 20"; `GET /carts/C1` shows quantity 2
