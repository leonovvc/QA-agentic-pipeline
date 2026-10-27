# Feature spec: Promo codes at checkout

Version 1.3 · Owner: Checkout team · Status: Ready for development

## 1. Overview
Customers can enter a promo code on the checkout page to get a discount on their order.
Marketing creates promo codes in the admin panel.

## 2. Code rules
1. A promo code is 6–12 characters long and contains Latin letters and digits only.
2. Codes are not case-sensitive.
3. Each code has an expiry date. A code can be used up to and including its expiry date.
4. A code is either percentage-based (5%, 10%, 15% or 20% off the items subtotal) or a fixed amount (500 ₽ off).
5. Some codes are single-use: once an order with the code is placed, the code cannot be used again by anyone.
6. Codes apply only to orders over 3000 ₽.

## 3. Checkout behaviour
1. The promo field is shown under the order summary, with an "Apply" button.
2. When a valid code is applied, the discount line appears in the order summary and the total is updated.
3. When the code has expired, the message "This promo code has expired" is shown under the field.
4. Only one promo code can be applied to an order. Applying a second code replaces the first.
5. Coupons cannot be combined with vouchers.
6. Code validation must be fast.

## 4. Order placement
1. The discount is recorded on the order and shown in the order confirmation email.
2. If the order is cancelled, a single-use code becomes available again.

## 5. Admin
1. Marketing can deactivate a code at any time; a deactivated code behaves like an expired one.
2. Codes stop working at the start of their expiry date.

## 6. Out of scope
Gift cards, loyalty points.
