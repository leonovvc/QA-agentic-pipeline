---
name: test-design-techniques
description: >-
  Formal test design techniques for turning a requirement into a minimal, high-coverage
  set of test cases: equivalence partitioning, boundary value analysis, decision table
  testing, pairwise/combinatorial testing, state transition testing, and exploratory
  charters — plus selection criteria for which technique fits which kind of requirement.
  Use when: "which test design technique," "equivalence classes," "boundary values,"
  "pairwise testing," "decision table," "state transition testing," "how many test
  cases do I actually need," "reduce test case count without losing coverage." Not for:
  ranking areas by business risk — use risk-based-testing. Not for: allocating tests
  across unit/API/E2E — use test-pyramid-strategy.
  Related: spec-gap-analysis, test-pyramid-strategy, test-planning, risk-based-testing,
  test-case-management, security-testing, qa-doc-review.
license: MIT
metadata:
  author: qa-agentic-pipeline
  version: "1.1"
  category: strategy
---

<objective>
A requirement with 4 independent boolean flags has 16 possible combinations; a naive tester writes all 16, a competent one writes 4 (equivalence classes) or 8 (pairwise) and catches the same defects. This skill is the decision procedure for picking the right formal technique per requirement, so test-case count stays proportional to actual risk of a missed defect, not to how exhaustively someone could enumerate inputs.

**Before starting:** check `.agents/qa-project-context.md` in the project root — it may already state which techniques the team standardizes on and skip that decision here.
</objective>

## Discovery Questions

1. **What shape is the requirement?** A single input field with a valid range → boundary value analysis. Several independent input fields → equivalence partitioning. Several fields that *interact* → pairwise/decision table. A workflow with statuses → state transition. A vague or exploratory area with no clear input/output → exploratory charter, not a formal technique.
2. **How many parameters interact, and do all combinations matter?** Below ~3 parameters with independent effects, test them individually. At 3+ interacting parameters, full combinatorial coverage explodes — decide between decision table (when there is a small number of *named business rules*) and pairwise (when the concern is unexpected interactions, not enumerated rules).
3. **Is the spec's acceptance criterion itself testable?** If you cannot state the expected output for a chosen input without guessing, this is a `spec-gap-analysis` finding, not a test-design problem — flag it upstream before designing cases against it.
4. **What did `spec-gap-analysis` already flag?** Blocking gaps and stated assumptions change which inputs are even valid to test — read that report before starting.

## Core Principles

1. **Every class needs exactly one representative, not more.** Once partitioning is correct, adding a second case from the same equivalence class finds nothing a mutation test wouldn't already catch elsewhere — it only adds maintenance cost.
2. **Boundaries hide more defects than midpoints.** Off-by-one errors, `<` vs `<=`, integer overflow, and empty/null handling cluster at boundaries. A technique choice that skips boundaries is a coverage gap even if class coverage looks complete.
3. **Combinatorial explosion is a design smell, not a testing problem.** If pairwise reduction still leaves an unmanageable case count, the underlying feature likely has too many independent toggles — say so in the test plan, don't just grind through the matrix.
4. **State-based features need state-based tests.** Enumerating "valid input → valid output" for a stateful workflow (order status, approval flow, session lifecycle) misses illegal-transition defects that only a state transition model surfaces.
5. **Name the technique in the test case metadata.** A test plan that says "boundary value analysis, `quantity` field, classes: 0, 1, max, max+1" is auditable; a plan that just lists inputs is not — `qa-doc-review` checks for this explicitly.

## Technique Catalog

| Technique | Use for | Typical case-count effect | Section |
|---|---|---|---|
| Equivalence Partitioning | Independent input fields with distinct valid/invalid ranges or categories | One test per class instead of one per possible value | Below |
| Boundary Value Analysis | Any bounded numeric/length/date input | Adds the 4-6 cases that actually catch off-by-one bugs | Below |
| Decision Table Testing | A handful of *named business rules* driven by combinations of conditions | Collapses a rules document into N table columns, one case each | Below |
| Pairwise / Combinatorial | 3+ independent parameters, no named rules, concern is unexpected interaction | Cuts full combinatorial count (often 100s) to ~10-20 pairs-covering cases | Below |
| State Transition Testing | Workflows/entities with defined statuses and allowed transitions | One case per valid transition + one per each illegal transition attempted | Below |
| Security negative cases | Requirements touched by the security lens (access control, auth, input handling, abuse) | One case per attacker-controlled partition (another user's ID, injection payload, N+1-th attempt) | Below |
| Exploratory Charters | Vague requirements, new/unfamiliar features, UX quality | Not a case-count technique — a time-boxed session with a mission | Below |

### Equivalence Partitioning

Split each input into partitions where every value in a partition should behave identically. Test one representative per partition (valid partitions get positive assertions, invalid partitions get error assertions).

*Worked example* — `discount_code` field, spec says "5-10 alphanumeric characters, case-insensitive, must exist in the promotions table":
- Classes: valid existing code; well-formed but non-existent code; too-short string; too-long string; contains non-alphanumeric characters; empty string; lowercase variant of a valid code (tests the case-insensitivity rule explicitly, since it's a distinct rule, not just a formatting variant).
- BAD: testing `SAVE10`, `SAVE20`, `SAVE30` — three values in the same "valid existing code" class, same code path, zero incremental coverage.

### Boundary Value Analysis

For a bounded range `[min, max]`, test: `min-1` (invalid), `min` (valid), `min+1` (valid), `max-1` (valid), `max` (valid), `max+1` (invalid). For string/collection length, boundaries are length values, not content. For dates, boundaries include the instant of a cutoff (23:59:59 vs 00:00:00 on the cutoff day).

*Worked example* — "cart allows 1 to 20 items": test 0 items (invalid, and check the specific empty-cart error, not just "rejected"), 1 item, 2 items, 19 items, 20 items, 21 items.

### Decision Table Testing

Use when the spec (or `spec-gap-analysis`'s clarified assumptions) names a small set of business conditions and outcomes — e.g., "shipping cost depends on: is the user a member (Y/N), is the cart over $50 (Y/N), is it a holiday promo period (Y/N)." Build one column per unique condition combination that has a distinct, spec-defined outcome; collapse combinations that share an outcome into one column with a "don't care" mark. Each column is one test case.

### Pairwise / Combinatorial Testing

Use when there is no small set of named rules — just several independent-seeming parameters (browser × OS × user role × locale) where the actual risk is an unanticipated interaction, not a documented rule. Generate an all-pairs covering array (by hand for ≤4 parameters with ≤3 values each; with a pairwise tool — e.g., PICT — beyond that) instead of the full cross product. State in the test plan which specific combinations were deliberately *not* covered, since pairwise is a coverage trade-off, not full coverage.

### State Transition Testing

Model the entity as states and allowed transitions (draw or list them). Write one case per valid transition (precondition state → action → expected new state) and one case per plausible *illegal* transition attempt (e.g., "cancel" on an already-`shipped` order), asserting it is rejected and the state is unchanged. Illegal-transition cases are the ones teams skip and where the real defects live.

### Security Negative Cases

When `security-testing`'s lens applies, treat the attacker as one more input dimension and partition it like any other: **horizontal access** (another user's resource ID), **vertical access** (a lower role calling an admin action), **malicious input** (one injection payload per interpreter the input reaches — SQL, HTML, shell, URL), **volume/abuse** (the first request over the stated rate limit), **session state** (expired token, token after logout). One case per partition, named `Security negative — OWASP A0x (<partition>)` in the Technique field. If the spec doesn't state the expected secure behavior, that is a Stage 1 gap, not something to invent here.

### Exploratory Charters

For an area too vague or novel for a formal technique, write a charter instead of scripted steps — it still goes in the plan as a `TC-MAN-<nnn>` case so coverage stays visible: **Mission** ("Explore promo-code entry with unusual input to discover validation and messaging gaps"), **Areas/variations** to try, **Time box** (30–90 min), and **What to record** (bugs, questions, new cases to formalize). Technique: `Exploratory charter`; Level: `Manual — no stable oracle yet`. Charters are run by people, never automated by Stage 3.

## Writing It Down — the Technique Field

Every case's Technique field (format in the artifact contract (`${CLAUDE_PLUGIN_ROOT}/skills/run-qa-pipeline/references/artifact-contract.md`)) names the technique **and** the item it represents, so the reviewer can reconstruct the partition/boundary set from the cases alone:

```markdown
- **Technique:** Boundary value analysis — `items`, max+1 (21)
- **Technique:** Equivalence partitioning — invalid class "non-existent code"
- **Technique:** Decision table — rule R3 (member = N, subtotal ≥ 50, promo period = Y)
- **Technique:** State transition — illegal: `shipped` → cancel
```

A case that represents several boundaries at once (parametrized) lists each one.

## Anti-Patterns

- **Testing every value "to be thorough."** Inflates case count without inflating defect-detection — a padded suite that takes longer to run and maintain while catching the same bugs as a well-partitioned one.
- **Skipping boundaries because "the middle case passed."** The middle of a valid range is the least likely place for an off-by-one defect to hide.
- **Full combinatorial matrix when pairwise would do.** 5 parameters with 4 values each is 1024 full combinations vs. ~20 pairwise cases; running the full matrix is not more rigorous, it's slower feedback for the same bug-catching power at that level of confidence.
- **Applying decision tables to interactions with no named business rule.** If the spec doesn't define what should happen for a combination, a decision table forces an invented outcome — that's a `spec-gap-analysis` finding, not something to paper over with a table.

## Done When

- Every test case in the plan states which technique produced it and, for partitioning/boundary cases, which class or boundary it represents.
- No two cases in the same equivalence class exist without a stated reason (e.g., "also verifies case-insensitivity").
- Every bounded input has explicit boundary cases (`min-1`, `min`, `max`, `max+1` or the length/date equivalent).
- Every stateful entity in scope has at least one illegal-transition case.
- Combinations left uncovered by a pairwise reduction are listed explicitly, not silently dropped.
- When the security lens applies, every applicable OWASP row has at least one security negative case (or a Stage 1 Q explaining why it can't be designed yet).
- Exploratory charters exist only for areas no formal technique fits, each with a mission and a time box.

## Related Skills

- **spec-gap-analysis** — run first; an untestable or ambiguous acceptance criterion is a spec problem, not a technique-selection problem.
- **test-pyramid-strategy** — once cases exist, decide which pyramid level executes each one.
- **risk-based-testing** — when case count still exceeds available time even after reduction, this is what decides which classes to cut first.
- **test-case-management** — writes each derived item as a case in the pipeline format.
- **security-testing** — the lens that decides when security negative cases are required, and their payloads.
