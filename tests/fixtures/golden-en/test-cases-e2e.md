# E2E test cases — Cart quantity limits

### TC-E2E-001: Changing quantity updates the subtotal shown in the cart
- **Traces:** REQ-3, A1
- **Technique:** Equivalence partitioning — valid class "increase"
- **Level:** E2E — proves the UI shows the server's recalculated subtotal
- **Priority:** P1
- **Preconditions:** cart with one line priced 100.00, quantity 1
- **Test data:** new quantity 3
- **Steps:**
  1. Open /cart → Expected: subtotal 100.00
  2. Set quantity to 3 → Expected: subtotal 300.00
- **Expected result:** subtotal reads 300.00 without reloading the page
