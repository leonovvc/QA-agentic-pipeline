# Cart quantity limits — annotated

> Source: pasted text. Markers correspond to findings in spec-gap-report.md.

1. A customer can set the quantity of each cart line from 1 to 20.
2. Entering a quantity outside that range shows the error "Quantity must be between 1 and 20" and keeps the previous quantity.
3. The cart subtotal is recalculated after every quantity change. [A1: ASSUMPTION — synchronous recalculation]
4. Orders with a subtotal of 5000 or more get free shipping. [Q1: TRACK B — currency and before/after discounts?]
