---
name: test-pyramid-strategy
description: >-
  Assign each test case in a test plan to a pyramid level (unit / API-integration / E2E)
  with a one-line justification, and check the resulting shape against the target
  repo's actual test-execution cost. Tactical, per-feature allocation — not a
  quarterly QA strategy document. Use when: "which level should this test run at,"
  "pyramid allocation," "too many E2E tests," "unit vs integration vs E2E," "test
  distribution for this feature." Not for: org-wide, multi-quarter pyramid strategy.
  Not for: picking the automation tool itself — use stack-detection-for-autotests,
  playwright-automation, api-testing, unit-testing.
  Related: test-design-techniques, test-planning, stack-detection-for-autotests,
  risk-based-testing, qa-doc-review.
license: MIT
metadata:
  author: qa-agentic-pipeline
  version: "1.1"
  category: strategy
---

<objective>
A test plan that assigns every case to E2E "because that's what the user sees" produces a suite that is slow, flaky, and expensive to diagnose when it fails — and it is the single most common defect `qa-doc-review` finds in AI-generated test plans. This skill is the per-feature allocation pass: for a given set of test cases, decide the cheapest level that can still prove the thing, and state why.
</objective>

## Discovery Questions

Check `.agents/qa-project-context.md` first: the **E2E budget** in its QA Pipeline section (default: at most 20% of automated cases at E2E) is the hard ceiling for this allocation unless the plan states why it must be exceeded.

1. **What does this test case actually need to prove?** A business rule, calculation, or validation → provable at unit level. A contract between two services (request/response shape, status codes, auth) → API/integration level. A real user journey spanning UI + backend + third-party integration, or something only observable end-to-end (multi-step checkout, cross-page state) → E2E.
2. **What is the current pyramid shape of the target repo?** Run `stack-detection-for-autotests` first — if the repo is already E2E-heavy, adding more E2E cases for logic that could be unit-tested compounds an existing problem rather than being a neutral default.
3. **What is the CI time/flakiness budget?** A repo with a 3-minute CI gate cannot absorb 40 new E2E cases; push more of the case set down a level or trim scope.
4. **Is this genuinely new functionality, or a variant of something already covered at a lower level?** Testing the same business rule at unit level AND re-asserting it inside an E2E flow is redundant unless the E2E case is specifically verifying the wiring, not the rule.

## Core Principles

1. **Push each assertion to the lowest level that can prove it.** If a unit test can prove the discount calculation is correct, an E2E test asserting the same number only proves the wiring is intact — write it as a smoke assertion, not a rerun of the business logic.
2. **E2E tests are for things only E2E can prove.** Real navigation, real third-party integration behavior, cross-system state that no single service owns, and the handful of business-critical golden-path journeys. Everything else is a candidate to push down.
3. **The shape is diagnostic, not decorative.** A rough 70/20/10 (unit/integration/E2E) split is a useful sanity check, not a quota to hit — deviate when the feature genuinely warrants it (a pure-UI feature has little to unit-test; a calculation-heavy backend feature has little to E2E), but state the deviation and why.
4. **Redundant coverage across levels is waste unless it proves a different failure mode.** Re-testing the same rule at two levels only earns its cost if each level catches a distinct class of defect (unit: logic error; E2E: the two services disagreeing about the contract).
5. **A skipped level is a decision, not an oversight.** If a feature plan has zero unit tests, that must be because the feature has no meaningful logic to isolate (e.g., pure UI/CSS) — state that; `qa-doc-review` treats an unexplained missing level as a finding.

## Allocation Heuristic

| Test case characteristic | Default level | Why |
|---|---|---|
| Pure business logic / calculation / validation rule, no I/O | Unit | Fastest feedback, no flakiness surface, isolates the exact failing rule |
| Data transformation, parsing, mapping between formats | Unit | Same as above; mock the I/O boundary |
| Single-service request/response contract (status codes, payload shape, auth, error codes) | API/Integration | Proves the contract without the cost of rendering UI |
| Interaction between two owned services (no UI) | API/Integration | Catches integration defects unit tests can't see, cheaper than E2E |
| Multi-step user journey through the UI (signup, checkout, core workflow) | E2E | Only level that proves the whole path actually works for a user |
| Third-party integration behavior (payment gateway, SSO) observable only via the full flow | E2E | Contract mocks can't catch a real third-party regression |
| Illegal state-transition / error-path case from `test-design-techniques` | Same level as the entity's other transition tests | Consistency; usually unit or API, rarely needs full E2E |
| Security negative case (access control, injection, rate limit, session) | API | The control is enforced server-side; E2E only when the behaviour is client-visible (rendered payload, masked field) |
| Exploratory charter, or a check needing human judgment (UX, copy tone) | Manual | No stable oracle to automate yet |
| Cross-cutting non-functional check (a11y, visual) | E2E only when a REQ states it (e.g. a WCAG level); otherwise out of the functional pyramid | Track separately; don't let it inflate the E2E share |

## Worked Example

Feature: "apply a discount code at checkout." Test cases from `test-design-techniques` (equivalence classes: valid code, expired code, non-existent code, malformed code, code below minimum cart value; boundary: cart value at exactly the minimum):

- All 6 partition/boundary cases for the discount *calculation rule itself* → **unit** (pure function: code + cart state → discount amount or rejection reason).
- "Applying a valid code returns a 200 with the updated cart total; applying an invalid code returns a 422 with the correct error code" → **API/integration** (one case each for valid and one representative invalid class — not all 6, that duplicates the unit coverage).
- "User enters a valid code at checkout and sees the updated total before paying" → **E2E** (one golden-path case; this is the only thing that proves the UI actually wires up to the rule).

Result for this feature: 6 unit, 2 integration, 1 E2E — not because of a quota, but because the calculation is where the complexity lives and the UI path is thin.

## Anti-Patterns

- **"Test it at E2E because that's realistic."** Realism is not free — it's the most expensive, slowest-feedback, most flake-prone level. Reserve it for what only it can prove.
- **Inverted pyramid from AI-generated plans.** Left to a default, an LLM asked to "write tests for this feature" tends to over-produce E2E scripts because they read as most literally descriptive of the spec. This skill exists specifically to correct that bias — check the actual output distribution, not just the intent.
- **Zero unit tests on a logic-heavy backend feature.** If the feature has calculations, validation, or branching business rules and the plan has no unit level, that's a gap, not a stylistic choice.
- **Duplicating the same assertion at every level "for safety."** Costs CI time and maintenance without adding defect-detection power; document why a case appears at more than one level if it genuinely does.

## Writing It Down — the Level Field

Each case's Level field holds the level and a one-clause reason (format in the artifact contract); the level code in the case ID must match:

```markdown
- **Level:** Unit — pure function `applyDiscount(subtotal, code)`; no I/O involved
- **Level:** API — the 422 and error code are the contract the frontend relies on
- **Level:** E2E — the only proof the total shown before payment reflects the server's calculation
- **Level:** Manual — exploratory charter; no stable oracle yet
```

`test-plan.md` → Pyramid Allocation states the counts, the share of automated cases per level, and the rationale for the shape.

## Verification

Count existing test files by directory/naming convention in the target repo (from `stack-detection-for-autotests`'s stack profile) and compare the ratio to what this plan is about to add. A plan that pushes an already 80%-E2E repo further in that direction should say so explicitly and flag it as a pre-existing debt the plan is not trying to fix.

## Done When

- Every test case in the plan has a pyramid level and a one-clause justification.
- The feature's overall level distribution is stated as a ratio (e.g., "6 unit / 2 integration / 1 E2E") with a one-line rationale for the shape.
- Any deliberate deviation from a roughly unit-heavy default is explained.
- No case duplicates another case's assertion at a different level without a stated distinct reason.
- The E2E share of automated cases is within the budget from `qa-project-context` (default 20%), or the excess is justified in the plan.

## Related Skills

- **test-design-techniques** — produces the case set this skill allocates.
- **stack-detection-for-autotests** — supplies the current repo pyramid shape and available frameworks per level.
- **unit-testing**, **api-testing**, **playwright-automation** — the per-level playbooks Stage 3 uses once a case has its level.
- **risk-based-testing** — when CI budget forces cuts, risk ranking decides which allocated cases survive.
