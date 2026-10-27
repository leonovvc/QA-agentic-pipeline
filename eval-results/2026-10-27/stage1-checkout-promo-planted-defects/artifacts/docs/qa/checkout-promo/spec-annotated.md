# Feature spec: Promo codes at checkout — annotated

> Source: `specs/checkout-promo.md` (v1.3). Markers below correspond to findings in
> spec-gap-report.md by ID. `Q` = gap / contradiction / open question, `A` = assumption made.

Version 1.3 · Owner: Checkout team · Status: Ready for development [Q28: TRACK A — status says "ready", but a contradiction (Q4) and two blocking gaps (Q18, Q19) remain; default taken: proceed with blocked items kept visible, see A1]

## 1. Overview
Customers can enter a promo code on the checkout page to get a discount on their order.
Marketing creates promo codes in the admin panel. [Q1: TRACK B — no creation rules: required fields, case-insensitive uniqueness, whether format/percentage list is enforced, editability] [Q26: TRACK A — is the admin panel in test scope? Default: no, see A20]

## 2. Code rules
1. A promo code is 6–12 characters long and contains Latin letters and digits only. [Q2: TRACK B — no stated outcome for malformed input (too short/long, space, symbols, Cyrillic look-alikes, empty, trimming)]
2. Codes are not case-sensitive. [Q3: TRACK B — in which case is the code echoed on the discount line and in the email?]
3. Each code has an expiry date. A code can be used up to and including its expiry date. [Q4: CONTRADICTION, BLOCKING for day-D cases — §5.2 says codes stop working at the START of the expiry date; see A1] [Q5: TRACK B — "date" has no time or timezone; see A2]
4. A code is either percentage-based (5%, 10%, 15% or 20% off the items subtotal) or a fixed amount (500 ₽ off). [Q6: TRACK B — no rounding rule for kopecks; see A3] [Q7: TRACK B — is 500 ₽ the only fixed value; what does "items subtotal" include (sale prices, delivery); see A4] [A18: ASSUMPTION — single currency RUB, 2-decimal precision]
5. Some codes are single-use: once an order with the code is placed, the code cannot be used again by anyone. [Q8: TRACK B — what event is "placed" (created, paid, confirmed); abandoned or failed payment; see A5] [Q9: TRACK B — two simultaneous orders with the same code; see A6] [Q10: TRACK B — limits of non-single-use codes, per-customer limit, guests; see A7]
6. Codes apply only to orders over 3000 ₽. [Q11: TRACK B — which amount is compared (items subtotal, total with delivery, after discount); "over" read as strictly greater; see A8] [Q12: TRACK B — outcome for orders ≤ 3000 ₽ and when the cart drops below after the code is applied; see A9]

## 3. Checkout behaviour
1. The promo field is shown under the order summary, with an "Apply" button. [Q13: TRACK B — remove control, persistence across reload, editability after apply, Enter key; see A10] [Q14: TRACK B, SECURITY — no attempt limit / rate limiting, distinguishable errors allow code enumeration; see A14]
2. When a valid code is applied, the discount line appears in the order summary and the total is updated. [Q15: TRACK B — content and format of the discount line unspecified] [A19: ASSUMPTION — discount is computed server-side, the client cannot supply its own amount]
3. When the code has expired, the message "This promo code has expired" is shown under the field. [Q16: TRACK B — no outcome or message for unknown, malformed, already-used, below-threshold, voucher-conflict, or server-error cases; see A9]
4. Only one promo code can be applied to an order. Applying a second code replaces the first. [Q17: TRACK B — if the second code is invalid, is the first kept? see A11]
5. Coupons cannot be combined with vouchers. [Q18: BLOCKING — "coupon" and "voucher" are undefined; relation to promo codes and to gift cards (§6) unknown; no outcome, no message; see A12]
6. Code validation must be fast. [Q19: BLOCKING — no measurable target; see A13] [Q27: TRACK A — are non-functional checks in scope? Default: no, see A14]
[Q20: TRACK B — silence on accessibility, localization (English-only message in a ₽ store), browser/device support]

## 4. Order placement
1. The discount is recorded on the order and shown in the order confirmation email. [Q21: TRACK B — is eligibility re-checked at placement (expired/deactivated/consumed/threshold in between); what is stored on the order; see A15] [Q22: TRACK B — email content, language, timing, failure handling]
2. If the order is cancelled, a single-use code becomes available again. [Q23: TRACK B — who cancels, which statuses, partial cancel / return / refund, restored after expiry or deactivation, who can reuse; see A16]

## 5. Admin
1. Marketing can deactivate a code at any time; a deactivated code behaves like an expired one. [Q24: TRACK B — effect on carts/checkouts in progress, reactivation, deactivating a used code, message shown; see A17] [Q25: TRACK B, SECURITY — which roles may create/deactivate, audit log, behavior for unauthorized calls]
2. Codes stop working at the start of their expiry date. [Q4: CONTRADICTION with §2.3 — see above]

## 6. Out of scope
Gift cards, loyalty points. [Q18: relevant — if "voucher" means gift card, §3.5 refers to something this section puts out of scope]
