# Test cases — E2E level (cart-orders)

Conventions: only journeys that cannot be proven below the UI. Business rules are proven at unit and API level; these cases check the wiring once. Control names are described by role because the spec does not name UI labels.

### TC-E2E-001: Entering quantity 21 shows the error message and restores the previous quantity
- **Traces:** REQ-2
- **Technique:** Boundary value analysis — `quantity`, max+1 (21), checking the message display and the kept value
- **Level:** E2E — only the browser proves the message is shown to the customer and the field reverts
- **Priority:** P2
- **Preconditions:** The customer is logged in; the cart has one line, price `1000.00`, quantity `2`; the cart page is open
- **Test data:** entered quantity `21`
- **Steps:**
  1. Enter `21` in the quantity field of the line and confirm the change → Expected: the message `Quantity must be between 1 and 20` is shown
  2. Read the quantity field of the line → Expected: it shows `2`
- **Expected result:** The message `Quantity must be between 1 and 20` is visible, the line quantity is `2` and the subtotal is `2000.00 ₽`

### TC-E2E-002: Quantity 20 on a 250.00 line gives subtotal 5000.00 and free shipping
- **Traces:** REQ-1, REQ-3, REQ-4
- **Technique:** Boundary value analysis — `quantity` max (20) combined with shipping threshold 5000.00 in one golden-path journey
- **Level:** E2E — golden path: the only proof that the quantity change, recalculation and shipping display work together for a customer
- **Priority:** P1
- **Preconditions:** The customer is logged in and is not a loyalty member; the cart has one line, price `250.00`, quantity `1`; the cart page is open
- **Test data:** entered quantity `20`
- **Steps:**
  1. Enter `20` in the quantity field of the line and confirm the change → Expected: the quantity field shows `20`
  2. Read the subtotal → Expected: `5000.00 ₽`
  3. Read the shipping charge → Expected: `0 ₽`
- **Expected result:** Quantity `20`, subtotal `5000.00 ₽`, shipping charge `0 ₽` (the display format for free shipping is not specified, OP-5; assert the numeric amount)

### TC-E2E-003: Customer cancels their own Created order from the UI **[assumption-based: A7]**
- **Traces:** REQ-6, A7
- **Technique:** State transition — valid: Created → cancel, as the owner (UI journey)
- **Level:** E2E — golden path: the only proof the cancel control is wired to the cancellation rule
- **Priority:** P1
- **Preconditions:** Customer `U1` is logged in; order `O4` in status `Created` belongs to `U1`; the order page is open
- **Test data:** order `O4`
- **Steps:**
  1. Activate the cancel-order control on order `O4` → Expected: the action completes and no error message is shown
  2. Reload the order page → Expected: the order status shown is not `Created`
- **Expected result:** After reload, order `O4` is not displayed with status `Created` (the name of the resulting state is not specified, OP-2)
