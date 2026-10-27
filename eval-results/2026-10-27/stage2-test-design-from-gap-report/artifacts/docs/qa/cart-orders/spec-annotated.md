# Cart limits, shipping and order cancellation — annotated

1. A customer can set the quantity of each cart line from 1 to 20.
2. Entering a quantity outside that range shows "Quantity must be between 1 and 20" and keeps the previous quantity.
3. The cart subtotal is the sum of price × quantity over all lines, recalculated after every change.
4. Shipping costs 300 ₽; orders with a subtotal of 5000 ₽ or more ship for free.
5. Loyalty members get an extra 5% off the subtotal when the subtotal is at least 3000 ₽, except during a sale period. [Q1: TRACK B — rounding; threshold before/after discount?] [A1: ASSUMPTION — half-up, before discount] [A2: ASSUMPTION — sale flag from pricing service]
6. An order moves Created → Paid → Shipped → Delivered. A Created or Paid order can be cancelled by the customer; a Shipped or Delivered order cannot. [A3: ASSUMPTION — only the owner can cancel; others get 403]
