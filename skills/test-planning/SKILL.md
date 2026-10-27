---
name: test-planning
description: >-
  Build the test plan for a feature, sprint, or release. In the QA pipeline this is
  Stage 2's plan document, test-plan.md: scope (in / out / blocked by a spec gap),
  assumptions, the per-requirement Risk Assessment, the REQ → test case traceability
  matrix, pyramid allocation, entry/exit criteria, and where the cases live. Also
  covers feature decomposition into testable scenarios, effort estimation by test type,
  risk × effort prioritization when capacity is short, and sprint scheduling with
  buffers. Use when: "write a test plan," "test plan for this feature/spec," "sprint
  test plan," "release test plan," "coverage mapping," "test estimation." Not for:
  scoring risk itself — use risk-based-testing; not for choosing techniques per
  requirement — use test-design-techniques; not for writing the individual cases — use
  test-case-management.
  Related: risk-based-testing, test-design-techniques, test-pyramid-strategy,
  test-case-management, spec-gap-analysis, qa-doc-review.
license: MIT
metadata:
  author: qa-agentic-pipeline
  adapted_from: petrkindlmann/qa-skills@test-planning (MIT, Petr Kindlmann)
  version: "3.0"
  category: strategy
---

<objective>
A test plan answers four questions: what to test, how deeply, who does it, and when it must be done. In this plugin its first job is traceability — every requirement the spec analysis found either maps to test cases or is explicitly out of scope or blocked, so the reviewer and the human can see coverage at a glance instead of inferring it from a pile of cases. A plan that silently loses a requirement is worse than no plan, because it looks complete.
</objective>

## Role in the QA pipeline

`qa-doc-writer` (Stage 2) writes `docs/qa/<task-id>/test-plan.md` with this skill. Its inputs are the original spec and Stage 1's `spec-gap-report.md` — in particular the **Requirements Inventory** (`REQ-<n>`), the Q items, and the Assumptions. Its sections and their order are fixed by the artifact contract (`${CLAUDE_PLUGIN_ROOT}/skills/run-qa-pipeline/references/artifact-contract.md`); the template is **Feature Test Plan** in `references/plan-documents.md`.

| Plan section | Built with |
|---|---|
| Scope (in / out / blocked) | Step 1 below + Blocking Gaps from Stage 1 |
| Assumptions | Stage 1 assumptions inherited + Stage 2's own (`A<n> (Stage 2)`) |
| Risk Assessment | `risk-based-testing`, Pipeline Mode |
| Traceability Matrix | Step 2 below — `REQ → TC IDs → techniques → status` |
| Pyramid Allocation | `test-pyramid-strategy` |
| Entry and Exit Criteria | Core Principle 6 + Quality Goals from `qa-project-context` |
| Case Location | `test-case-management` (files per level, or the test-case system path) |
| Estimate *(optional)* | Step 3 — include when the user asked for one or a sprint window is known |

Steps 4-6 (prioritization under capacity, allocation, schedule) apply when the plan is for a sprint or release with a real time window; for a single feature run through the pipeline, the Risk Assessment's priority column already decides what is cut first.

## Quick Route

| Situation | Go to |
|-----------|-------|
| Plan a feature from a spec (pipeline Stage 2) | Role in the QA pipeline → Steps 1-2 → Feature Test Plan template |
| Plan a single sprint | Steps 1-6 below, then the 1-page sprint template in `references/plan-documents.md` |
| Plan a release | Release template in `references/plan-documents.md` |
| Track an in-flight plan / feed results back | `references/tracking-formats.md` (daily status + retrospective) |
| Decide what to cut when over capacity | Step 4 prioritization matrix |

---

## Discovery Questions

Before writing a test plan, gather context. Check `.agents/qa-project-context.md` first -- if it exists, use it as the foundation and skip questions already answered there.

### Scope

- What is the scope? (single sprint, release, hotfix, feature)
- Which features are new vs. changed vs. unchanged?
- Which features are being released for the first time?
- Are there infrastructure or dependency changes (database migrations, API version bumps, third-party provider switches)?
- Is there a requirements document, PRD, or set of user stories to map against?

### Time and Resources

- What is the testing window? (days, hours available)
- Who is available for testing? (SDETs, manual testers, developers)
- Are there shared resources that could bottleneck? (staging environments, test accounts, devices)
- Is there a hard deadline that cannot move, or is the release date flexible?

### Risk Context

- Which areas changed the most in this cycle?
- What broke in the last release or sprint?
- Are there known fragile areas or tech debt that increase risk?
- For risk-based prioritization methodology, see `risk-based-testing`.

### Existing Coverage

- What automated tests already exist for the in-scope features?
- What is the current pass rate of the automated suite?
- Are there known gaps in automation that require manual testing?
- When was the last exploratory testing session on these features?

---

## Core Principles

### 1. Coverage-Driven: Map Every Requirement to at Least One Test

A test plan without traceability to requirements is a guess. Every `REQ-<n>` from the spec analysis must map to at least one test case, or be listed as out of scope or blocked by a named `Q<n>`. Gaps in this mapping are untested requirements -- the most dangerous kind of risk.

### 2. Time-Boxed: Plan Fits the Available Window

Testing expands to fill available time if unbounded. Set a time box for each activity and stick to it. When the window is too short, the prioritization matrix determines what gets cut -- not gut feeling.

### 3. Prioritized: Not Everything Gets Equal Depth

A payment flow change and a tooltip fix do not deserve equal effort. Use the risk x effort matrix to allocate depth: some features get full regression, others a smoke test, some nothing if low-risk and unchanged.

### 4. Buffered: Leave Room for the Unexpected

Plans that schedule 100% of available time fail when bugs are found. Allocate only 70-80% of the testing window to planned work and explicitly reserve the remaining 20-30% for bug verification, re-testing, and unplanned investigation. If buffer is not a named line in the plan, you do not have one.

### 5. Visible: The Plan Is a Communication Tool

Developers need to know what gets tested to write testable code. Product managers need coverage visibility to make release decisions. Publish the plan where the team can see it.

### 6. Entry and Exit Criteria Are First-Class

The most-reused part of any plan is its gate. Make it explicit, not buried: **entry** = code-complete on staging + existing suite green + test data seeded; **exit** = every HIGH-risk area covered + no open P0/P1 + zero unexplained GAP rows in the coverage matrix. Everything else is detail around these two checkpoints.

---

## Workflow

The six workflow steps each have a fill-in-the-blank scaffold. The decision prose stays here; the copy-paste templates (decomposition, coverage matrix, estimation worksheet, prioritization matrix, allocation table, schedule) live in `references/workflow-templates.md`.

### Step 1: Feature Analysis and Decomposition

Break each in-scope feature into testable units. In the pipeline, the units are the `REQ-<n>` rows of the Requirements Inventory — do not re-decompose the spec from scratch, or the plan and the gap report will disagree about what the requirements are. A "testable unit" is a specific behavior that can be verified with a clear pass/fail outcome. Walk every feature against these scenario categories so none gets skipped:

- **Happy path** — the primary success flow.
- **Validation** — required fields empty, format violations, boundary values.
- **Error conditions** — server 5xx, network timeout, rejected input.
- **Edge cases** — unicode, oversized payloads, unsupported formats.
- **Concurrency / race conditions** — two users edit the same record simultaneously, double-submit, retry-after-timeout. These hide the worst data-corruption bugs and are the category most often missed.
- **Integration points** — behavior across each boundary the feature crosses.

See `references/workflow-templates.md` for the decomposition template and a worked "User Profile Edit" example that exercises all six categories.

> **AI decomposition cross-check.** When an agent decomposes features, have it immediately map its own scenarios back against the Step 2 coverage matrix. Any requirement with no scenario, or any scenario category above with no entry, is a decomposition gap the agent must surface before estimation — this is how you catch the agent's blind spots, not after CI does.

### Step 2: Requirements-to-Test Coverage Mapping

Create a traceability matrix that maps every requirement to its test cases. In the pipeline this is the plan's `## Traceability Matrix`:

```markdown
| REQ | Test cases | Techniques | Status |
|---|---|---|---|
| REQ-1 | TC-UNIT-001…004, TC-E2E-001 | BVA, decision table | covered |
| REQ-4 | — | — | blocked by Q2 (no valid range stated) |
| REQ-7 | — | — | out of scope (performance, owned by SRE load tests) |
```

For a sprint plan, see `references/workflow-templates.md` for the broader coverage matrix template.

Rules for the coverage matrix:
- Every requirement must appear in the matrix (target: 100% mapping)
- "GAP" status triggers a decision: write a test, accept the risk, or defer
- Test case IDs follow `TC-<LVL>-<nnn>` (artifact contract); after Stage 3, `autotest-summary.md` links each ID to its test file and test name
- Manual tests reference the test case document or charter

### Step 3: Effort Estimation

Estimate effort for each test type using historical data. If no historical data exists, use the reference estimates below and calibrate after the first sprint.

**Estimation reference (per test case):**

| Test Type | Write Time | Execute Time | Maintenance (per quarter) |
|-----------|-----------|-------------|--------------------------|
| Unit test | 0.5 hr | < 1 sec | 5 min |
| Integration test | 1 hr | 5-30 sec | 15 min |
| E2E test (Playwright/Cypress) | 2-3 hours | 30s-2 min | 30 min |
| Manual test case (write) | 0.25 hr | 5-15 min per execution | 10 min |
| Exploratory session (charter) | 15 min | 1.5 hrs per session | N/A |
| Accessibility review (manual) | 0.5-1 hr per area | included in write | 15 min |
| Visual regression test | 30-60 min | 10-30 sec | 20 min (baseline updates) |
| Performance test (k6 script) | 2-4 hours | 5-30 min per run | 30 min |
| Prompt regression / LLM eval | 30-60 min per case | 30 sec - 2 min (with API cost) | 20 min |
| Setup & test data (per feature) | 0.5-2 hrs | one-time | re-seed per env |

Write Time is authoring only. The "Setup & test data" row is the line planners most often omit — environment, fixtures, and mock configuration routinely run 20-40% of total effort, so budget it as a real line rather than discovering it mid-sprint.

> **AI authoring trade-off.** Using an agent to author tests cuts *Write Time* by roughly 40-60%, but add a *Review Time* line of similar size per case — Bolton's "AI productivity paradox" (2026) is that the speed-up evaporates when an agent ships plausible-but-broken tests that pass a casual review and fail in CI. In this pipeline that review is Stage 4 (`qa-doc-reviewer` with `ai-qa-review`) — budget for acting on its findings.

> **Test-smells review.** ISTQB's CTAL-AT v2.0 (May 2026) names test smells as a planning concern. Budget a recurring 30-min "test-smells review" per sprint against the taxonomy in `ai-qa-review` — cheap, and it finds maintenance debt before it compounds.

Use the sprint estimation worksheet in `references/workflow-templates.md` to roll per-case estimates up to a capacity-utilization figure (target: 70-80%, leaving 20-30% buffer).

### Step 4: Prioritization Matrix (Risk x Effort)

When the estimated effort exceeds available capacity (it usually does), use the risk x effort matrix to decide what to cut. See `references/workflow-templates.md` for the full matrix grid.

For each test case, plot it on the matrix using the risk score from `risk-based-testing` and the effort estimate from Step 3, then consume capacity in priority order: **DO FIRST → DO SECOND → DO THIRD → DEFER → SKIP**.

**Tie-break rule:** within HIGH risk, low-effort beats high-effort — a HIGH-risk / low-effort test (DO FIRST) outranks a HIGH-risk / high-effort test (DO THIRD), because it buys the most risk reduction per hour. Medium-risk items defer before you cut any HIGH-risk coverage; low-risk items defer or skip entirely. Never cut buffer to fit more planned work.

### Step 5: Resource Allocation

Assign testing work based on skill match and availability.

**Allocation principles:**
- Automated test writing goes to SDETs or developers with framework experience
- Exploratory testing goes to the person who understands the feature best (often the developer or product manager, not just QA)
- New feature testing benefits from fresh eyes -- assign someone who did not build it
- Critical path testing should not have a single point of failure -- two people should be able to cover it
- Each person's load stays at 70-80% utilization, not 100% — the rest is their buffer
- Buffer is distributed per person, not lumped into one tester's block: every assignee carries their own buffer line so a blocker on one person does not consume everyone's slack

See `references/workflow-templates.md` for the allocation table format.

### Step 6: Schedule with Buffers

Map testing activities to the sprint timeline. Testing should not be back-loaded to the last two days. See `references/workflow-templates.md` for the 2-week sprint schedule template.

**Key scheduling rules:**
- Testing starts as soon as features are code-complete, not at sprint end
- Environment setup and test data preparation happen on Day 1, not Day 3
- Bug verification is continuous, not batched
- The last day is for confirmation, not for starting new testing

---

## Plan Documents

Full copy-paste plan documents live in `references/plan-documents.md`:

- **Sprint Test Plan (1-Page)** — scope, coverage summary, effort budget, entry/exit criteria, plan risks. Keep a sprint plan to one page.
- **Feature Test Plan** — the pipeline's `test-plan.md`, section for section as the artifact contract requires.
- **Release Test Plan** — aggregates sprint plans and adds release-specific concerns (full regression, cross-browser, perf benchmark, security scan, smoke test) plus go/no-go criteria.
- **Feature Coverage Matrix** — per-feature scenario list with priority, test type, location, and status.
- **Test Estimation Worksheet** — new-test development, existing-suite execution, manual testing, and a summary delta vs. available capacity.

---

## Tracking Progress During the Sprint

A test plan is useless if nobody checks it after Day 1. Track progress daily, and feed the results back into future planning at sprint end.

- **Daily test status** — completed, blocked, bugs found, tomorrow's plan, coverage percentage, and buffer consumed. See the format in `references/tracking-formats.md`.
- **Sprint retrospective inputs** — estimation accuracy broken out by test type, coverage delta, bug counts by severity, and lessons. See the format in `references/tracking-formats.md`; feed these data points into the next sprint's estimates.

---

## Anti-Patterns

### Planning Without Risk Assessment

Treating every feature with equal depth wastes effort on low-risk areas and under-tests critical paths. Always run the prioritization matrix (Step 4) before allocating effort. For the full risk methodology, see `risk-based-testing`.

### No Buffer for Bug Discovery

Scheduling 100% of available hours for planned activities leaves no time for verification when bugs are found. Reserve 20-30% as buffer and track consumption daily.

### Back-Loading Testing to Sprint End

Leaving all testing for the last two days rushes coverage and surfaces bugs too late to fix. Start testing as features become available; continuous testing beats batch testing at sprint end.

### Test Plan as Compliance Artifact

A 30-page plan filed and forgotten helps nobody. The plan should be one page for a sprint, actively tracked, and updated daily. If the plan is not changing, nobody is using it.

### Estimating Without Historical Data

Effort estimates pulled from thin air are unreliable. Track actual time spent — broken out by test type — and use that data for future estimates. After 2-3 sprints, estimates become reliable.

### Ignoring Environment and Data Setup

Environment setup, test data creation, and mock configuration can consume 20-40% of testing effort. Include the "Setup & test data" row from Step 3 in the estimate or the plan will always run over.

### Single-Person Coverage on Critical Path

A single tester covering all critical-path work is a failure point. Ensure at least two people can cover critical-path testing.

---

## Verification

**Feature plan (pipeline):** every `REQ-<n>` in `spec-gap-report.md` appears exactly once in both the Risk Assessment and the Traceability Matrix; every TC ID in the matrix exists in a case file; every `blocked` row names an existing `Q<n>`; the section headings match the artifact contract. `tools/check_artifacts.py` in the plugin repository checks all of this mechanically.

**Sprint/release plan:** every in-scope ticket ID from the sprint board appears in the Scope table; the coverage matrix has zero unexplained GAP rows (each GAP carries an accept/defer note); allocated capacity sums to 70-80% with a named buffer line; and the entry/exit criteria checklists are filled, not placeholder.

## Done When

**Feature plan (pipeline)**
- [ ] `test-plan.md` has all sections from the artifact contract, in order, written in the run's output language (`qa-output-standards`)
- [ ] Every REQ is covered, out of scope with a reason, or blocked by a named Q — no silent gaps
- [ ] Inherited and own assumptions are listed separately
- [ ] Entry/exit criteria are concrete (e.g. "all P0/P1 cases pass; no open Blocking review finding")
- [ ] Case Location names the actual files or test-case-system path

**Sprint / release plan**
- [ ] A plan document exists (1-page sprint template or release template) with scope table, coverage summary, effort budget, and entry/exit criteria all filled in — no placeholders
- [ ] Every in-scope feature is decomposed into specific testable scenarios with pass/fail criteria, covering happy path, validation, error, edge, and concurrency categories
- [ ] A requirements-to-test coverage matrix exists with no unexplained GAP entries
- [ ] Each scenario is estimated and plotted on the risk x effort matrix, with deferred items explicitly listed
- [ ] Allocated capacity is 70-80% with 20-30% buffer explicitly reserved as a named line

## Reference Files (in `references/`)

- **workflow-templates.md** — Fill-in scaffolds for the six workflow steps: decomposition template + example, coverage matrix, sprint estimation worksheet, risk×effort matrix grid, allocation table, and 2-week schedule.
- **plan-documents.md** — Full copy-paste documents: Feature Test Plan (the pipeline's `test-plan.md`), 1-page sprint test plan, release test plan, feature coverage matrix, and estimation worksheet.
- **tracking-formats.md** — Daily test status format and sprint retrospective inputs format (with per-test-type variance).

## Related Skills

- **risk-based-testing** -- fills the Risk Assessment section and decides depth and priority per requirement.
- **test-design-techniques** -- chooses the technique per requirement that the Traceability Matrix records.
- **test-pyramid-strategy** -- fills the Pyramid Allocation section.
- **test-case-management** -- writes the cases the matrix points to, and decides where they live.
- **spec-gap-analysis** -- supplies the Requirements Inventory, Q items, and assumptions the plan is built on.
- **qa-doc-review** -- independently checks this plan's traceability against the original spec.
- **qa-project-context** -- Quality Goals feed the exit criteria.
