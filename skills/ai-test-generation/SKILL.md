---
name: ai-test-generation
description: >-
  Turn test cases into test code with an LLM without the usual failure modes —
  hallucinated APIs and selectors, assertions that check nothing, duplicated
  scenarios. In the QA pipeline it is Stage 3's method: each pyramid-allocated case
  from Stage 2 becomes a test whose oracles are designed before the code, whose title
  carries the TC ID, and which is mechanically checked against the real codebase
  before anyone reviews it. Standalone, it runs its full seven-step staged pipeline
  (extract → risks → coverage matrix → scenarios → oracles → code → review) from a
  PRD, user story, diff, bug report, or OpenAPI spec. Use when: "automate these test
  cases," "сделай автотесты по кейсам," "tests from spec/user story/OpenAPI." For cases
  in docs/qa/<task-id>/, dispatch the autotest-builder agent, which applies this skill
  and records results. Not for: auditing an existing suite — use ai-qa-review.
  Related: unit-testing, api-testing, playwright-automation,
  stack-detection-for-autotests, ai-qa-review, qa-output-standards.
license: MIT
metadata:
  author: qa-agentic-pipeline
  adapted_from: petrkindlmann/qa-skills@ai-test-generation (MIT, Petr Kindlmann)
  version: "3.0"
  category: ai-qa
---

<objective>
LLMs will happily emit fifty plausible-looking tests that assert nothing, target endpoints that do not exist, and duplicate each other. This skill forces structured intermediates — requirements, coverage matrix, oracle definitions — to exist BEFORE any test code, so what you get is traceable, reviewable, and grounded in the real codebase instead of ad-hoc generated noise.

**Before starting:** check `.agents/qa-project-context.md` in the project root. It carries tech stack, test frameworks, naming conventions, selector strategy, and known risk areas that dramatically improve generated test quality.
</objective>

## Role in the QA pipeline

Inside `run-qa-pipeline` the first five steps of the staged pipeline below already exist as reviewed artifacts — `autotest-builder` must reuse them, not regenerate them:

| Step | Produced by | Artifact Stage 3 reads |
|---|---|---|
| 1 Extract requirements | Stage 1 `spec-analyst` | Requirements Inventory `REQ-<n>` in `spec-gap-report.md` |
| 2 Risks, invariants, ambiguities | Stage 1 + Stage 2 | Q/A items; Risk Assessment in `test-plan.md` |
| 3 Coverage matrix | Stage 2 `qa-doc-writer` | Traceability Matrix in `test-plan.md` |
| 4 Scenarios | Stage 2 | `test-cases-<level>.md` — one case per scenario |
| 5 Oracles | **Stage 3** (starts here) | The case's Expected result is the primary oracle; add the data / negative / side-effect oracles from Step 5 |
| 6 Code | **Stage 3** | Test files in the repo + `autotest-summary.md` |
| 7 Review | Stage 4 `qa-doc-reviewer` + `ai-qa-review` | `qa-review-report.md` |

So in the pipeline, `autotest-builder` runs **Pipeline Mode**:

1. Read the stack profile from `stack-detection-for-autotests` and the cases for the levels it automates.
2. For each non-`MAN` case: design oracles (Step 5) — at minimum the case's expected result, one negative oracle ("what must not happen"), and a data oracle when the outcome is persisted.
3. Generate the code (Step 6) with the framework skill for the case's level, applying `qa-output-standards` §3: the test title is `TC-<LVL>-<nnn>: <case title>` in the output language; identifiers in English.
4. Run the Verification gate below, then actually run the tests and record real results in `autotest-summary.md`.
5. Do **not** self-review as a substitute for Step 7 — hand off to Stage 4.

If a case is too ambiguous to derive an oracle from (its expected result is not observable), do not invent one: mark it `not run` with the reason and raise it in `autotest-summary.md` — that is a Stage 2 defect for the reviewer to see.

**Standalone Mode** (no pipeline artifacts): run all seven steps below in order.

## Quick Route

The pipeline is the same for every input; only the Step 1 extraction emphasis changes. Jump to the matching row, then run Steps 2-7 unchanged.

| Input type | Step 1 extracts | Watch for |
|------------|-----------------|-----------|
| PRD / feature spec | Entities, business rules, acceptance criteria, NFRs, stated assumptions | Implicit requirements inferred from "seamless"/"fast" language |
| User story + AC | Each AC → ≥1 happy + ≥1 negative scenario | ACs that hide multiple behaviors in one line |
| Code diff (`git diff main...HEAD`) | New/changed code paths, modified conditionals, removed behavior | Regression scope: test the changed paths, not the whole module |
| Bug report | Repro steps, expected vs actual, environment | Write a test asserting *expected* — fails now, passes after fix |
| OpenAPI / GraphQL SDL | Endpoints, schemas, required fields, enums, auth | Validation, auth-failure, and edge cases per endpoint, not just 200s |

Playwright projects also pick an agent integration mode — see Discovery Q2.

## Discovery Questions

Check `.agents/qa-project-context.md` first — if it exists, use it and skip anything already answered there. Then clarify:

1. **What is the input source?** Pipeline test cases (→ Pipeline Mode), or a PRD / spec, user story + AC, code diff, bug report, or API schema (→ Standalone Mode; determines Step 1 extraction emphasis, see Quick Route). For an LLM/AI feature spec, stop — what it needs is an eval dataset and graders, not UI tests.

2. **What is the target test framework, and (for Playwright) which agent integration mode?**
   - **E2E:** Playwright (preferred), Cypress. **Unit:** Jest, Vitest, pytest. **API:** Playwright `APIRequestContext`, Supertest, requests.
   - **Playwright CLI + agents** (recommended for Claude Code / Codex / Cursor): `npx playwright init-agents --loop=claude` scaffolds planner/generator/healer agents into `.claude/agents/` as markdown. They are interactive dev tools that produce standard Playwright tests which run unchanged in CI. Token-efficient; runs inside the agent's loop.
   - **Playwright MCP** (`npx @playwright/mcp@latest`): higher overhead, right when the agent must *drive* a live browser interactively over a long session.
   - **Neither** — hand-write tests using AI as a scratch-pad helper.

3. **What project context is available?** Existing test patterns, Page Objects / helpers, data factories / fixtures, CI constraints (timeout, parallelism). More context = less cleanup.

4. **What is the review workflow?** Full pipeline → human review → merge (default); scenarios only → human writes code; or code → human refines iteratively.

5. **What domain knowledge is needed?** Regulated industry (healthcare, finance) compliance, domain invariants (money never negative, appointments cannot overlap), known risk areas from past incidents.

## Core Principles

1. **Pipeline before code.** Never generate test code before establishing what to test, why, and how to verify it. The seven-step pipeline exists to prevent premature code generation that targets the wrong things.

2. **Structured intermediates are the product.** The assumptions document, coverage matrix, and oracle definitions are more valuable than the test code itself. They are reviewable, traceable, and reusable.

3. **Separate what from how.** Scenario generation (what to test) and oracle design (how to verify) are distinct cognitive tasks. Mixing them produces scenarios biased toward what is easy to assert, with assertions tacked on as afterthoughts.

4. **AI generates the first draft; a human reviews and refines.** Never ship AI-generated tests without human review. The AI accelerates — it does not replace judgment.

5. **Context is everything.** Feed the LLM your conventions, existing patterns, selector strategy, and data setup. The more context, the less cleanup.

6. **Quality over quantity.** Each test has a maintenance cost. Focus on critical paths, complex logic, and known risk areas — not test count.

## The Pipeline

**Mandatory workflow — agents MUST follow this order:**

```
Step 1: Extract   → Requirements, entities, business rules from input
Step 2: Analyze   → Risks, invariants, edge cases, ambiguities
Step 3: Map       → Coverage matrix (requirement → scenario → priority)
Step 4: Generate  → Candidate scenarios (happy + boundary + negative + security + a11y)
Step 5: Design    → Assertions and oracles SEPARATELY from scenarios
Step 6: Code      → Test code (only after all above exist)
Step 7: Review    → Human review with traceability back to source
```

Full prompt templates for every step (extraction, risk analysis, scenario, oracle, code) live in `references/prompt-patterns.md`. Below is the shape of each step's output.

### Step 1: Extract Requirements and Entities

Parse the input into structured elements: **Entities** (with roles/states/attributes), **Business Rules** (numbered), **Explicit Requirements** (`[REQ-N]`, stated in source), and **Implicit Requirements** (`[IMP-N]`, inferred — flag every one for human confirmation). Separating explicit from inferred is the rule that prevents testing assumptions as if they were specifications.

### Step 2: Risk Analysis and Invariants

Derive what can go wrong, what must always be true, and where the source is silent.

- **Risks** — table of `Risk | Likelihood | Impact | Source Requirement` (e.g. race condition on stock decrement, email delay > 30s).
- **Invariants** (must ALWAYS hold) — `stock >= 0`, `order total = sum(items) + tax + shipping`, `user sees only their own orders`.
- **Ambiguities** (need human answers) — "Does free shipping apply before or after discount codes?" Capture these explicitly; do not silently pick one.
- **Edge cases derived from risks** — two users buy the last item, payment succeeds but email service is down.

### Step 3: Coverage Matrix

The single most important artifact — it prevents both gaps and duplicates. Map every requirement to scenarios with category, priority, and oracle type:

| Requirement | Scenario | Category | Priority | Oracle Type |
|-------------|----------|----------|----------|-------------|
| REQ-1 | Add single item to empty cart | Happy path | P0 | State: cart count = 1 |
| REQ-1 | Add out-of-stock item | Negative | P0 | UI: error message, cart unchanged |
| REQ-2 | Complete checkout with valid card | Happy path | P0 | State: order created, stock decremented |
| REQ-2 | Two users checkout last item | Race condition | P1 | One succeeds, one gets stock error |
| INV-1 | Stock never goes negative | Invariant | P0 | Data: stock >= 0 after any operation |

After building it, verify: every requirement has ≥1 happy and ≥1 negative scenario; every invariant has a direct test; every Step-2 risk has a scenario; no two rows test the same thing.

### Step 4: Generate Candidate Scenarios

For each matrix row, write the full scenario in Given/When/Then with explicit test-data requirements (`Given: user with 99 items in cart (max 100); When: adds one more; Then: count = 100`). Cover these categories systematically:

| Category | Description |
|----------|-------------|
| Happy path | The user does exactly what the feature is designed for |
| Boundary | Edge of valid input ranges — use the BOUNDARIES framework (`references/prompt-patterns.md`) |
| Negative | Invalid inputs, unauthorized actions |
| Security | Auth bypass, injection, privilege escalation |
| Accessibility | Screen reader, keyboard-only, contrast |
| State transition | Valid and invalid moves between states |
| Concurrency | Two users acting simultaneously |

### Step 5: Design Assertions and Oracles

**Deliberately separate from Step 4.** Scenarios describe behavior; oracles describe how to verify it. For each scenario, define oracles across categories — a single assertion is rarely enough to prove a behavior:

| Oracle category | Asserts | Example |
|-----------------|---------|---------|
| UI state | Visible text / element state | `cart badge toHaveText('1')` |
| Data | Persisted state via API/DB | `GET /api/cart` returns 1 item, correct total |
| Negative | What should NOT happen | no error toast; no navigation away |
| Side effect | Async/external outcomes | analytics `add_to_cart` fired; email in inbox < 30s |

**Oracle quality rules:** assert business outcomes not implementation details; use the most specific assertion available (`toHaveText('$29.99')`, not `toBeTruthy()`); include negative assertions; verify data integrity, not just UI; assert accessibility (focus management, live-region announcements).

### Step 6: Generate Test Code

**Only after Steps 1-5 produce reviewed artifacts.** Code is a mechanical translation of scenarios + oracles into framework syntax, with traceability comments linking back to the requirement and scenario:

```typescript
/**
 * Scenario: SC-001 — Add single item to empty cart
 * Requirement: REQ-1 (User can add items to cart)
 * Priority: P0
 */
test('add single item to empty cart', async ({ page, testProduct }) => {
  await page.goto(`/products/${testProduct.id}`);                       // Given
  await page.getByRole('button', { name: 'Add to cart' }).click();      // When
  await expect(page.getByTestId('cart-badge')).toHaveText('1');         // Then
  await expect(page.getByTestId('error-toast')).not.toBeVisible();      // Negative oracle
});
```

**Code generation rules:** match project conventions (from `qa-project-context.md` and the stack profile); reuse existing Page Objects, fixtures, and data factories; carry traceability in the title (`TC-E2E-001: …` in Pipeline Mode) or a comment (`Scenario: SC-XXX`, `Requirement: REQ-XX` standalone); follow the project's selector strategy; put setup/teardown in fixtures, not inline; meet the readability bar in `qa-output-standards`.

### Step 7: Human Review

Not optional — a mandatory step. In the QA pipeline this is Stage 4: `qa-doc-reviewer` runs it, delegating smell detection to `ai-qa-review`, and **the generator never reviews its own tests**. Standalone, a human runs it before merge. Checklist for every generated test:

- [ ] **Traces to requirement:** test → scenario → coverage row → requirement is followable.
- [ ] **Tests behavior, not implementation:** survives a harmless refactor.
- [ ] **Correct abstraction level:** right test type (unit vs integration vs E2E).
- [ ] **Test naming and readability:** the test name states the behavior; a reader sees intent without decoding the body.
- [ ] **Test isolation / no shared state:** the test creates and cleans up its own data, holds no order dependency on sibling tests, and passes when run alone or in any order.
- [ ] **Realistic test data:** plausible, diverse, using `example.com`.
- [ ] **Meaningful assertions:** matches the oracle definition; specific, not `toBeTruthy()`.
- [ ] **Matches project conventions:** naming, structure, selector strategy.
- [ ] **No flakiness risks:** no hardcoded timeouts, race conditions, or order dependence.
- [ ] **Edge cases included:** goes beyond the happy path.
- [ ] **Assumptions validated:** Step-2 ambiguities were resolved before coding.

**Review outcome per test:** **KEEP** (merge as-is) · **MODIFY** (fix listed issues, then merge) · **REJECT** (wrong requirement, wrong abstraction, hallucinated API) · **DEFER** (blocked on ambiguity).

## Guardrails

Hard rules. Agents MUST follow them.

- **Code before coverage is forbidden.** Never emit test code before Steps 1-3 (requirements, risk analysis with documented assumptions, coverage matrix) exist. If an agent skips to code: STOP, go back.
- **Assert outcomes, not implementation.** `expect(screen.getByRole('progressbar')).toBeVisible()`, not `expect(component.state.isLoading).toBe(true)`. `expect(page.getByTestId('cart-badge')).toHaveText('1')`, not `expect(store.dispatch).toHaveBeenCalledWith(...)`.
- **Scenarios (Step 4) before oracles (Step 5), always.** Scenario = WHAT happens; oracle = HOW to verify. Mixing them biases scenarios toward easy assertions.
- **Always produce the intermediates** — assumptions document, uncovered ambiguities, oracle candidates, and the traceability chain — even in abbreviated form.

**Flag these when detected:**
- **Hallucinated APIs** — endpoints, selectors, methods, or imports that do not exist in the codebase. Verify mechanically (see Verification) before human review.
- **Duplicate scenarios** — same behavior, trivially different data. Consolidate or parametrize.
- **Low-value assertions** — `expect(response).toBeTruthy()`, `expect(page).toHaveURL(/.*/)`.
- **Missing negative cases** — if every scenario is a happy path, the coverage matrix is incomplete.
- **Unrealistic test data** — `test@test.com`, `John Doe`, `password123`. Use diverse, plausible data on `example.com`.

## Model selection per step

Route by difficulty, not habit. Mechanical extraction (Step 1) and coverage-matrix bookkeeping (Step 3) run fine on a small fast model. Oracle design (Step 5) and code generation (Step 6) are where a wrong inference is expensive — fabricated APIs, wrong business arithmetic — so use the strongest model available there. Running the strongest model on every step is wasteful; running the cheapest on Step 6 produces fabricated APIs.

## Verification

Convert the "hallucinated APIs" warning into a mechanical gate. After Step 6, before human review:

1. **Resolve imports / types.** TypeScript: `npx tsc --noEmit` — fabricated imports and wrong signatures fail here. Python: `python -m pyflakes <files>` or `ruff check`.
2. **Grep generated selectors/endpoints against the codebase.** Confirm every `getByTestId('...')` id and every API path the test calls actually exists in source:
   ```bash
   grep -roE "getByTestId\('([^']+)'\)" generated/ | sed -E "s/.*'([^']+)'.*/\1/" | sort -u \
     | while read id; do grep -rq "$id" src/ || echo "MISSING testid: $id"; done
   ```
3. **Run the suite once.** Tests that reference nonexistent routes/selectors fail fast; quarantine those before review rather than reviewing dead code.

Any `MISSING` line or `tsc` error is a hallucination to fix before a human spends review time.

## Anti-Patterns

1. **Skipping to code.** The most common failure: an agent gets a PRD and immediately writes tests. Without the coverage matrix it misses scenarios and duplicates others. The pipeline exists to prevent this.
2. **Asserting implementation instead of behavior.** `expect(component.state.isLoading).toBe(true)` breaks on any refactor. Assert `expect(screen.getByRole('progressbar')).toBeVisible()` — what the user observes.
3. **Mixing scenarios and assertions.** Writing "test this thing and check this value" as one step. Separate *what to test* from *how to verify it*.
4. **No project context in the prompt.** Without conventions and existing patterns, you get generic tests. `qa-project-context.md` exists for exactly this.
5. **Over-generating.** AI will write 50 tests for a simple function. Each carries maintenance cost. Use the coverage matrix to bound generation to meaningful scenarios.
6. **Copy-paste without understanding.** If you cannot explain what a generated test does and why, do not merge it. Tests you do not understand become tests you cannot debug.
7. **Shipping without review.** Step 7 is not optional. AI tests routinely contain hallucinated APIs, wrong selectors, incorrect business logic, and flakiness only human review catches.
8. **Ignoring the feedback loop.** When AI tests catch real bugs, note the prompt patterns that worked; when they false-positive, note what went wrong. Build a project-specific library of what works.

## Done When

- Standalone Mode: all seven artifacts exist: requirements document, risk & invariants, coverage matrix, scenario set, oracle definitions, test code, and review notes with a KEEP/MODIFY/REJECT/DEFER decision per test.
- The coverage matrix was produced and reviewed before any test code file was written.
- Verification passed: `tsc --noEmit` (or language equivalent) exits 0 and the selector/endpoint grep reports zero `MISSING` lines.
- Each generated test has a recorded review decision (Stage 4 in the pipeline); no test is marked KEEP without one.
- The tests were run; failures are reported as test defects or suspected product defects, never "fixed" by weakening the assertion.
- Reproducibility metadata recorded: the model used, the input source (task ID / spec hash), and the version of any skill / CLI / MCP server invoked.
- In Pipeline Mode: every non-`MAN` case appears exactly once in `autotest-summary.md` with a real status, and every test title carries its TC ID.

## Related Skills

- **stack-detection-for-autotests** — always first in Pipeline Mode; decides framework, directory, and conventions.
- **unit-testing**, **api-testing**, **playwright-automation** — framework patterns per pyramid level; generated tests live inside these frameworks.
- **qa-output-standards** — language of titles/comments and the readability bar for test code.
- **test-case-management** — the case format this skill reads in Pipeline Mode.
- **ai-qa-review** — Step 7's smell taxonomy, run by Stage 4 on what this skill generated.
- **qa-project-context** — conventions and risk areas that make generation dramatically better.

## Reference Files (in `references/`)

- **prompt-patterns.md** — Full prompt library aligned to the seven steps: extraction, risk analysis, scenario generation, oracle design, and code generation prompts, plus the BOUNDARIES edge-case framework used in Step 4.
