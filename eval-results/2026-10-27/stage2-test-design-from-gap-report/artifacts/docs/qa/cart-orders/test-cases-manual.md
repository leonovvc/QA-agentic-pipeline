# Test cases — Manual (cart-orders)

### TC-MAN-001: Exploratory charter — behavior the spec leaves open around quantity input and order cancellation
- **Traces:** REQ-1, REQ-6, A5, A7
- **Technique:** Exploratory charter — no stable oracle exists for the open points OP-1, OP-2, OP-3, OP-4
- **Level:** Manual — the expected behavior is not specified, so there is nothing to automate yet
- **Priority:** P2
- **Preconditions:** A test environment with a customer account, a loyalty-member account, one cart, and orders in each of the statuses Created, Paid, Shipped, Delivered
- **Test data:** quantity inputs `""` (empty), `" 5 "` (spaces), `5.0`, `1e1`, `０５` (full-width digits), `0x10`; orders in each status; two browser sessions of the same customer
- **Steps:**
  1. Mission: explore quantity-field input and order cancellation with unusual values and timing to discover validation, messaging and state gaps. Time box: 60 minutes.
  2. Areas: (a) the quantity inputs listed in Test data; (b) cancelling an already-cancelled order; (c) double-click or two sessions cancelling the same order at once; (d) cancelling a Paid order and what the customer is shown about money and the resulting state; (e) an empty cart: subtotal and shipping shown.
  3. Record: every observed message and status, any server error, any state inconsistent between cart/order pages, and a proposed expected result for each open point.
- **Expected result:** A written session note exists listing, for each of OP-1..OP-4 and the empty-cart case, the observed behavior and a proposed expected result for the spec owner; any 5xx, incorrect charge, or inconsistent state is raised as a defect
