# E2E test cases

### TC-E2E-001: Customer cancels a paid order
- **Traces:** REQ-6
- **Technique:** State transition — valid: Paid → Cancelled
- **Level:** E2E — the customer-facing cancel button
- **Priority:** P1
- **Preconditions:** order O1 in status Paid
- **Test data:** order O1
- **Steps:**
  1. Open the order page → Expected: "Cancel order" button visible
  2. Click "Cancel order" and confirm → Expected: status shows "Cancelled"
- **Expected result:** order O1 status is Cancelled

### TC-E2E-002: Free shipping applies from 5000
- **Traces:** REQ-4
- **Technique:** Boundary value analysis — subtotal 4999.99 and 5000.00
- **Level:** E2E — the customer sees the shipping line in the cart
- **Priority:** P0
- **Preconditions:** carts with subtotals 4999.99 and 5000.00
- **Test data:** two carts
- **Steps:**
  1. Open each cart → Expected: shipping 300.00 and 0.00 respectively
- **Expected result:** shipping 300.00 for 4999.99; 0.00 for 5000.00
