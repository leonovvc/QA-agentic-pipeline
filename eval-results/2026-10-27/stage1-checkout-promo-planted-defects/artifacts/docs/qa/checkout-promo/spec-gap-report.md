# Spec Gap Analysis — Promo codes at checkout (specs/checkout-promo.md, v1.3)

## Source
`specs/checkout-promo.md` (local Markdown file, v1.3, owner: Checkout team). Verbatim snapshot in `spec-source.md`. Text source, no extraction loss; confidence in the reading: high.
No `.agents/qa-project-context.md` exists in this repository, so no org Definition of Ready was available; the generic checklist below was used. Output language: English (default).

Note: the spec header says "Status: Ready for development". Against the checklist at the bottom it is not ready for test design — one contradiction, two blocking gaps and many unspecified negative paths remain.

## Testability Score: 2
The happy path and the code format are checkable. The score is held down by one internal contradiction (expiry boundary), two requirements that cannot be tested as written (vouchers, "fast"), and the near-total absence of failure outcomes, money-rounding rules and cancellation/concurrency semantics.

## Requirements Inventory
| ID | Spec location | Requirement | Acceptance criterion | Testable |
|---|---|---|---|---|
| REQ-1 | §1 | "Marketing creates promo codes in the admin panel." | none stated | partly → Q1, Q26 |
| REQ-2 | §2, item 1 | "A promo code is 6–12 characters long" | length 6–12 | partly → Q2 |
| REQ-3 | §2, item 1 | Code "contains Latin letters and digits only" | charset stated; outcome for violations none | partly → Q2 |
| REQ-4 | §2, item 2 | "Codes are not case-sensitive." | none stated beyond the sentence | yes |
| REQ-5 | §2, item 3 | "A code can be used up to and including its expiry date." | none stated for time of day / timezone | partly → Q4, Q5 |
| REQ-6 | §2, item 4 | Percentage codes give 5%, 10%, 15% or 20% off the items subtotal | percentages stated; rounding none | partly → Q6, Q7 |
| REQ-7 | §2, item 4 | Fixed-amount code gives "500 ₽ off" | 500 ₽ | partly → Q7 |
| REQ-8 | §2, item 5 | Single-use code "cannot be used again by anyone" once an order with it is placed | none stated for "placed" / concurrency | partly → Q8, Q9 |
| REQ-9 | §2, item 6 | "Codes apply only to orders over 3000 ₽." | strict "over" 3000 ₽; basis of the amount none | partly → Q11, Q12 |
| REQ-10 | §3, item 1 | Promo field shown under the order summary with an "Apply" button | position and button label stated | yes |
| REQ-11 | §3, item 2 | Valid code applied → "the discount line appears in the order summary" | none stated for line content | partly → Q15 |
| REQ-12 | §3, item 2 | Valid code applied → "the total is updated" | none stated for rounding | partly → Q6 |
| REQ-13 | §3, item 3 | Expired code → message "This promo code has expired" shown under the field | exact message text and position | yes |
| REQ-14 | §3, item 4 | "Only one promo code can be applied to an order." | none stated | yes |
| REQ-15 | §3, item 4 | "Applying a second code replaces the first." | none stated for an invalid second code | partly → Q17 |
| REQ-16 | §3, item 5 | "Coupons cannot be combined with vouchers." | none stated | no → Q18 |
| REQ-17 | §3, item 6 | "Code validation must be fast." | none stated | no → Q19 |
| REQ-18 | §4, item 1 | "The discount is recorded on the order" | none stated for what is recorded | partly → Q21 |
| REQ-19 | §4, item 1 | Discount is "shown in the order confirmation email" | none stated for content | partly → Q22 |
| REQ-20 | §4, item 2 | Order cancelled → "a single-use code becomes available again" | none stated for cancellation scope | partly → Q23 |
| REQ-21 | §5, item 1 | "Marketing can deactivate a code at any time" | none stated | partly → Q24, Q25 |
| REQ-22 | §5, item 1 | "a deactivated code behaves like an expired one" | behavior = REQ-13 by reference | partly → Q24 |
| REQ-23 | §5, item 2 | "Codes stop working at the start of their expiry date." | none stated | partly → Q4 |

§6 (gift cards, loyalty points out of scope) is a scope statement, not a testable obligation, so it has no REQ. 23 REQs in total: 4 `yes` (REQ-4, 10, 13, 14), 2 `no` (REQ-16, 17), 17 `partly`.

## Blocking Gaps
**Q18** — §3, item 5 ("Coupons cannot be combined with vouchers"). "Coupon" and "voucher" are never defined anywhere in the spec; the rest of the document says "promo code". It is unclear whether "coupon" = promo code, what a "voucher" is, whether a voucher is a gift card (§6 puts gift cards out of scope), how a customer would hold both, which one is rejected or removed, and what message is shown. No test with a concrete input and expected result can be written. Blocks REQ-16. Marker `[Q18]`.

**Q19** — §3, item 6 ("Code validation must be fast"). No measurable target (latency percentile, load, environment). Cannot be verified or failed objectively. Blocks REQ-17 only; all functional requirements are unaffected. Marker `[Q19]`.

(The expiry contradiction **Q4** below is also blocking for the "on the expiry date itself" boundary cases of REQ-5 and REQ-23.)

## Contradictions
**Q4** — §2, item 3 vs §5, item 2. §2.3: "A code can be used up to and including its expiry date." §5.2: "Codes stop working at the start of their expiry date." On the expiry date itself, the first says the code works, the second says it does not. The two rules produce opposite results for the single most important boundary of REQ-5/REQ-23 (day D). Blocking for boundary cases on day D; cases for D-1 and D+1 are unaffected. Marker `[Q4]`.

## Open Questions
### Track A — for you, now
Per the run instruction (unattended, no questions to the operator), these were not asked in the conversation; each carries the default taken. Change them if the default is wrong.

**Q26** — Is the admin panel (code creation / deactivation UI) in the test scope of this pass, or only the customer-facing checkout behavior? Default taken: A20 — admin is exercised only as a means to set up and deactivate codes (via UI, API or data seeding, whichever the later stages find available); the admin UI itself is not designed against. Marker `[Q26]`.

**Q27** — Are non-functional checks (performance, rate limiting / enumeration, accessibility) in scope of this pass? Default taken: A14 — out of scope for the functional test design; they are recorded as spec gaps (Q14, Q19, Q20) and left to a separate decision. Marker `[Q27]`.

**Q28** — May the pipeline proceed on a spec that has one contradiction and two blocking gaps? Default taken: A1 — yes, with blocked items kept visible: REQ-16, REQ-17 and the expiry-day boundary are marked blocked in Stage 2, not guessed. Marker `[Q28]`.

### Track B — for the analyst / spec owner
Ordered by the risk of the requirement each question blocks (money and access first). Each question stands alone; the likely owner is given in brackets. Entries without a bold ID are the Blocking Gap / Contradiction items already described above, repeated here in forwardable form.

- (Q4) [PM / Checkout team] Section 2.3 says a promo code works "up to and including its expiry date", but section 5.2 says codes "stop working at the start of their expiry date". On the expiry date itself, does the code work or not?

**Q8** — §2, item 5. [PM / backend lead] A single-use code "cannot be used again" once an order with it is "placed". What event counts as "placed": the order being created at checkout submit, successful payment, or order confirmation? If payment fails or the customer abandons the payment page, is the code consumed, reserved for some time, or still free?

**Q9** — §2, item 5. [backend lead] If two customers apply the same single-use code and submit orders at the same moment, which order gets the discount and what does the other customer see (error, order without discount, order blocked)?

**Q21** — §4, item 1 and §3, item 2. [backend lead] Between applying a code and placing the order the code may expire, be deactivated, be consumed by someone else, or the cart may fall to 3000 ₽ or below. Is eligibility re-checked when the order is placed? If the code is no longer valid at that moment, is the order rejected, placed without the discount, or placed with the discount anyway? And what exactly is stored on the order (code, type, percentage, discount amount in ₽, subtotal)?

**Q23** — §4, item 2. [PM / backend lead] "If the order is cancelled, a single-use code becomes available again." Who can cancel (customer, support, system on payment timeout), in which order statuses, and does this also apply to partial cancellation, returns and refunds? If the code has expired or been deactivated by the time of the cancellation, is it still restored (and thus still unusable)? Can anyone use the restored code, or only the original customer?

- (Q18) [PM / Checkout team] Section 3.5 says "Coupons cannot be combined with vouchers". What are "coupons" and "vouchers" as distinct from promo codes — is a voucher the same as a gift card? When a customer has both, which one is kept, which one is rejected, in what order, and what message is shown?

**Q11** — §2, item 6. [PM] "Codes apply only to orders over 3000 ₽." Which amount is compared with 3000 ₽: the items subtotal (as §2.4 uses), the subtotal after discounted/sale prices, the total including delivery, or the total after the promo discount? "Over" is read as strictly greater than 3000.00 ₽ — confirm.

**Q12** — §2, item 6. [PM / UX] What does the customer see when a valid code is entered for an order of 3000 ₽ or less (message text, code kept or dropped)? And if a code is already applied and the customer then removes items or changes quantities so the order falls to 3000 ₽ or below — is the code removed, is the discount kept, or is checkout blocked? Likewise, when quantities change with a percentage code applied, is the discount recalculated?

**Q6** — §2, item 4 and §3, item 2. [PM / backend lead] How is a percentage discount rounded to kopecks (half-up, half-even, down, up), and is it rounded per item or on the whole subtotal? Which value is rounded — the discount or the new total?

**Q7** — §2, item 4. [PM] (a) Is 500 ₽ the only fixed amount, or an example (can marketing create 300 ₽ or 1000 ₽ codes)? Likewise, are 5/10/15/20% the only allowed percentages, and does the admin panel enforce that list? (b) What is included in "items subtotal": are items already on sale included at their sale price, and are delivery and taxes excluded?

**Q10** — §2, item 5. [PM] "Some codes are single-use." How is the flag set (admin field at creation?), and what are the limits for all other codes — unlimited uses by anyone, a per-customer limit, a total limit? Can a guest (not logged in) use a code, and can the same customer use the same multi-use code on several orders?

**Q25** — §5, item 1. [backend lead / security] Which admin roles may create and deactivate codes, and are these actions written to an audit log (who, when, which code)? What happens when a user without the role calls the same action?

**Q14** — §3, item 1. [security / backend lead] Codes are 6–12 characters of letters and digits and the spec sets no limit on attempts. Is there rate limiting or temporary blocking after repeated invalid codes (per session, IP, account)? Should the error responses for "does not exist", "expired" and "already used" be distinguishable (the "expired" message confirms the code exists)?

**Q24** — §5, item 1. [PM / backend lead] When marketing deactivates a code, what happens to a cart that already has it applied and to a checkout in progress? Can a deactivated code be reactivated? Can a code that has already been used be deactivated? Does the deactivated code show exactly "This promo code has expired" (as "behaves like an expired one" implies), or a different message? Does deactivation touch orders already placed (it should not — confirm)?

**Q17** — §3, item 4. [PM / UX] A promo code is already applied and the customer enters a second code. If the second code is invalid (expired, unknown, below threshold), does the first code stay applied or is it removed? What if the customer enters the same code again?

**Q5** — §2, item 3. [PM / backend lead] An expiry is a date with no time or timezone. In which timezone does the expiry day begin and end (store timezone, server UTC, customer's timezone)? Which timezone is shown to marketing in the admin panel?

**Q2** — §2, item 1. [PM / UX] What happens when the customer enters something that is not a valid code format: fewer than 6 or more than 12 characters, a space, hyphen or other symbol, Cyrillic characters that look like Latin ones, or an empty field? Is the Apply button disabled, is an inline error shown, or is the lookup simply "not found"? Are leading/trailing spaces trimmed? Is pasted text with a trailing space accepted?

**Q16** — §3, item 3. [PM / UX] Only one error message is defined ("This promo code has expired"). What are the outcomes and exact messages for: unknown code, malformed code, single-use code already used, order of 3000 ₽ or less, voucher conflict, and a server error or timeout during validation? Is the total in all of these cases unchanged?

**Q1** — §1. [PM / Marketing] What are the rules for creating a code in the admin panel: required fields, whether code uniqueness is checked case-insensitively (§2.2 means `SPRING10` and `spring10` would clash), whether the format of §2.1 and the percentage list of §2.4 is enforced at creation, and whether an existing code's expiry, type or value can be edited?

- (Q19) [tech lead / PM] Section 3.6 says "Code validation must be fast". What is the target: response time at which percentile, under what load, in which environment?

**Q22** — §4, item 1. [PM] What does the confirmation email show about the discount: the code, the discount line with an amount, the new total? In which language and at what point is it sent, and does a failure to send the email affect the order?

**Q15** — §3, item 2. [UX] What does the "discount line" look like: label text (does it show the code?), sign and format of the amount (e.g. "−500 ₽"), position relative to the subtotal and total? What is the exact result for a percentage code — is the percentage shown?

**Q13** — §3, item 1. [UX] Can the customer remove an applied code (and how)? Does the applied code survive a page reload or leaving and returning to checkout within the same cart? Is the field editable after a code is applied? Does pressing Enter in the field act as "Apply"?

**Q20** — §3 (silence). [PM / UX] The spec says nothing about accessibility (error message announced to screen readers, keyboard use), localization (the only message is in English, while the prices are in ₽ — is the English text final or is there a translated message?), or supported browsers/devices and mobile layout. Are any of these in scope?

**Q3** — §2, item 2. [UX] Codes are not case-sensitive. In what case is the code shown back to the customer (as typed, as stored, uppercase) on the discount line and in the email?

## Assumptions Made to Proceed
**A1** — (Q4, Q28) The contradiction is not resolved by choosing a side. Boundary cases for the expiry day itself are marked blocked in Stage 2; cases for the day before expiry (code works) and the day after (code does not work) are valid under both readings and proceed. Why: both readings are plausible and either would silently invent a requirement.

**A2** — (Q5) A single business timezone is used and tests avoid sub-day precision: expiry cases use dates at least one full day away from "today". Why: it keeps cases valid regardless of the timezone chosen.

**A3** — (Q6) Percentage discount is computed on the items subtotal and rounded half-up to 0.01 ₽; the total is subtotal − discount. Contestable — rounding is a money rule the owner should confirm.

**A4** — (Q7) 500 ₽ and 5/10/15/20% are the only values; "items subtotal" = sum of line price × quantity of the cart items at their displayed price, excluding delivery and taxes. Why: the spec lists exactly these values and names "items subtotal".

**A5** — (Q8) "Placed" = the order was successfully created at checkout submission. Failed or abandoned payment behavior is not tested until Q8 is answered. Contestable.

**A6** — (Q9) Single-use invariant: of two simultaneous submissions with the same single-use code, at most one order gets the discount. Which response the loser sees is not asserted. Why: "cannot be used again by anyone" implies it.

**A7** — (Q10) Codes that are not single-use have no usage limit (any number of uses by anyone, guests included). Why: nothing in the spec limits them.

**A8** — (Q11) The 3000 ₽ threshold is compared with the items subtotal before the promo discount, strictly greater: 3000.00 is not eligible, 3000.01 is eligible. Why: "over" is strict, and §2.4 names the items subtotal as the base. Contestable (basis).

**A9** — (Q12, Q16) For every failure other than expiry (unknown, malformed, already used, below threshold): the code is not applied, the total is unchanged, and some visible error is shown; only the expired message text is asserted. Eligibility is re-evaluated when the cart changes. Contestable.

**A10** — (Q13) Removal of an applied code and persistence across reload are not tested.

**A11** — (Q17) If a second code is invalid, the first code stays applied. Contestable — the opposite reading (first code is dropped) is also reasonable.

**A12** — (Q18) No assumption: REQ-16 is blocked, no cases are written for it.

**A13** — (Q19, Q27) REQ-17 is excluded from functional test design; if a performance check is wanted, it needs a numeric target first.

**A14** — (Q14, Q20, Q27) Rate limiting, enumeration resistance, accessibility, localization and browser/device matrix are out of this pass's functional design and stay recorded as gaps.

**A15** — (Q21) Eligibility is re-validated server-side when the order is placed: an order cannot receive a discount from a code that is expired, deactivated or already consumed at that moment. Contestable.

**A16** — (Q23) Cancelling an order restores a single-use code to "unused" regardless of who cancels it; if it has expired or been deactivated in the meantime it is restored but remains unusable.

**A17** — (Q24) A deactivated code shows the same message as an expired code ("This promo code has expired"), reading §5.1 literally. Contestable — the message is misleading for the customer.

**A18** — (general) One currency (RUB, ₽); amounts have kopeck precision (2 decimals).

**A19** — (security, Q21) Discount amounts are calculated server-side from the code and the cart; the client cannot send its own discount value. Why: baseline for any pricing feature; tests will try to tamper with it as a negative case.

**A20** — (Q26) The admin panel is not tested as a UI; codes are created and deactivated through whichever mechanism the later stages find available (admin UI, API or seed data).

## Security Lens
Triggers present: user input (code field), pricing/payment amount, admin actions, personal data (confirmation email).

| OWASP 2025 area | Applies? | Result |
|---|---|---|
| A01 Broken Access Control | Yes — deactivation/creation of codes in the admin panel; single-use "by anyone" | Q25 (roles, unauthorized calls); Q10 (who may use a code) |
| A05 Injection | Yes — free-text code field | Q2 (what the field accepts); format is restricted to letters/digits by §2.1, so injection strings should be rejected as malformed — covered under Q2 |
| A06 Insecure Design | Yes — no attempt limit, distinguishable errors, race on single-use, replay after cancel | Q14 (enumeration / brute force), Q9 (race), Q23 (restore after cancel), A19 (server-side pricing) |
| A09 Security Logging & Alerting Failures | Yes — admin deactivation and repeated failed attempts | Q25 (audit log), Q14 |
| A10 Mishandling of Exceptional Conditions | Yes — validation timeout or backend error during Apply | Q16 (outcome when validation fails) |
| A07 Authentication Failures | Not applicable beyond Q10 — no login or session behavior is specified by this feature | — |
| A04 Cryptographic Failures, A02 Security Misconfiguration, A03 Supply Chain, A08 Integrity Failures | Not applicable — no secrets, configuration, dependencies or signed artifacts in this spec | — |
| Personal data | The confirmation email carries order data only; no new personal data introduced by the feature | Q22 (email content) |

## Ready-for-Test-Design Checklist
- [ ] Every in-scope user action has a success and failure outcome — only the success path and the "expired" failure are defined (Q16, Q2, Q12)
- [ ] Every acceptance criterion is objectively checkable — REQ-16 and REQ-17 are not (Q18, Q19)
- [ ] Edge cases are addressed or explicitly out of scope — rounding, threshold basis, concurrency, timezone and cancellation are not (Q6, Q11, Q9, Q5, Q23)
- [ ] No unresolved contradictions remain — Q4 is open
