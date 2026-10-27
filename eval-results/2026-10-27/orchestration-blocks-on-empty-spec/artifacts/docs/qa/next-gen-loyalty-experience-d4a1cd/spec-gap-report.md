# Spec Gap Analysis — Next-gen loyalty experience

> WHOLE-SPEC BLOCKER: the spec contains no testable requirement and no acceptance criterion. Zero REQ items could be derived. Test design cannot start until the Blocking Gaps (Q1-Q5) are resolved, most likely by obtaining a real functional spec (Q15).

## Source
specs/loyalty.md (plain text file, 483 bytes, 3 short paragraphs), snapshot in `spec-source.md`. The snapshot was missing at the start of the run and was recreated verbatim from the original file. Extraction confidence: n/a (plain text, complete, not a fragment). Output language: English (given by the operator).

## Testability Score: 1
The text is a vision statement: it names no user action, rule, entity, value, state, channel, or measurable outcome, so nothing can be objectively checked.

## Requirements Inventory
| ID | Spec location | Requirement | Acceptance criterion | Testable |
|---|---|---|---|---|
| (none) | — | No checkable obligation exists in the spec. Candidate phrases ("modern, intuitive and fun", "best-in-class", "drives engagement and retention", "stronger KPIs") are wishes, not obligations, and are logged as gaps (Q1-Q5) rather than as REQs. | none stated | no → Q1 |

Total REQs: 0. Stage 2 has nothing to trace to; coverage would be 0 of 0 and meaningless.

## Blocking Gaps
1. **Q1** — Whole spec (paras 1-3): no functional requirement at all. No stated behavior of the loyalty program (earning, redeeming, tiers, balances, expiry, notifications). "Reimagine how shoppers feel rewarded" names no mechanism. Blocks everything. [Q1]
2. **Q2** — Para 1, "across all channels": channels are not listed (web, mobile app, in-store/POS, email?). Scope and test levels cannot be set. [Q2]
3. **Q3** — Para 1, "In Q1 we will reimagine": no statement of what is new vs. current loyalty behavior, and no baseline. Unknown whether this is a UI redesign, a rule change, or both, so there is no reference behavior to test or regression-test against. [Q3]
4. **Q4** — Para 2, "modern, intuitive and fun": subjective, with no measurable or checkable criterion. [Q4]
5. **Q5** — Para 3, "happier customers and stronger KPIs": success measures are unnamed, with no metric, target, or measurement method. Not verifiable by QA and not tied to any feature. [Q5]

## Contradictions
(none — the text is too thin to contradict itself)

## Open Questions
### Track A — for you, now
The operator is away, so this was not asked live; it is logged with the assumption taken (see A1).
1. **Q6** — Is it acceptable to stop the pipeline after Stage 1 and wait for a real spec, rather than proceed to test design on invented requirements? (Assumed: yes, stop; see A1.) [Q6]

### Track B — for the analyst / spec owner
Ordered by the risk of the requirement blocked (money and access first). Each question is self-contained and can be forwarded as-is.
1. **Q7** — What are the loyalty program rules? How are points or rewards earned (per currency unit, per action), how are they redeemed (what for, minimum and maximum amounts), do they expire, can a balance go negative, and what happens to earned points when an order is refunded or returned? Please give exact values and rounding rules. Likely owner: Product Manager. [Q7]
2. **Q8** — Who may view and change a customer's loyalty balance and tier (customer, support agent, admin, marketing)? How is a customer identified across channels (account login, phone number, card barcode), and how are guests and duplicate or merged accounts handled? Which customer data is collected and what consent is required? Likely owner: Product Manager with Backend lead and Security/Legal. [Q8]
3. **Q9** — Which channels are in scope for the Q1 release (web, iOS, Android, in-store POS, email, other), and must behavior be identical in each? Which browsers, devices, and locales or languages must be supported? Likely owner: Product Manager. [Q9]
4. **Q10** — Which user-visible features make up the "new experience" (for example dashboard, tier progress, rewards catalog, notifications, gamification), and for each one what is the expected behavior on success and on failure (insufficient points, service unavailable)? Likely owner: Product Manager and Design. [Q10]
5. **Q11** — What is the current loyalty behavior being replaced, and which parts must stay unchanged? Is there a migration of existing balances and tiers, and what is the cutover and rollback plan? Likely owner: Product Manager and Backend lead. [Q11]
6. **Q12** — What measurable acceptance criteria define "modern, intuitive and fun" (for example a design-system reference, an accessibility standard such as WCAG 2.1 AA, a usability benchmark)? Likely owner: Design. [Q12]
7. **Q13** — Which KPIs define "stronger KPIs" and "drives engagement and retention", with baseline, target, and measurement window? Are these in QA scope or only for analytics event validation? Likely owner: Product Manager and Marketing. [Q13]
8. **Q14** — What are the non-functional requirements: response-time targets, expected load (for example during promotions), availability, and behavior when dependent systems (marketing tools, POS, order system) are down? Which marketing initiatives does this integrate with? Likely owner: Backend lead and Marketing. [Q14]
9. **Q15** — Is there a fuller specification, design file, or ticket set behind this one-page vision (the "Q1" plan)? If yes, please send it, since this document alone cannot be tested. Likely owner: Product Manager. [Q15]

## Assumptions Made to Proceed
1. **A1** — Gap: no testable content at all (Q1, Q6). Assumption: the pipeline stops after Stage 1 and no test plan or test cases are written, because any would be invented. Reason: building on invented requirements would give false coverage. [A1]
2. **A2** — Gap: output language. Assumption: English, as the operator instructed. [A2]
3. **A3** — Gap: no Definition of Ready available (no `.agents/qa-project-context.md` was found in the working tree). Assumption: the generic Analysis Checklist applies. [A3]

No requirement-level assumptions are made, deliberately: with no stated behavior, an assumption would amount to inventing the spec.

## Security Lens
The text states no behavior, but a loyalty program implies triggers: money-like value (point balances and redemption), personal data (customer profile and purchase history), accounts and permissions, and multi-channel identity. These are inferred from the domain, not from the spec. Rows with a finding:
- Authentication / access control (who can view or modify balances): Q8.
- Business logic abuse (earning and redemption limits, double redemption races, refund clawback): Q7.
- Personal data and consent: Q8.
- Rate limiting, input validation, admin actions, uploads, URLs/webhooks: cannot be assessed; no mechanism is described (see Q10, Q14).

## Ready-for-Test-Design Checklist
- [ ] Every in-scope user action has a success and failure outcome (no user action is stated: Q1, Q10)
- [ ] Every acceptance criterion is objectively checkable (none stated: Q4, Q5, Q12, Q13)
- [ ] Edge cases are addressed or explicitly out of scope (Q7, Q14)
- [x] No unresolved contradictions remain (none found)

Verdict: NOT READY. Whole-spec blocker; the pipeline should not proceed to Stage 2.
