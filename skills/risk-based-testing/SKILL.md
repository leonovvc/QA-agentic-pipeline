---
name: risk-based-testing
description: >-
  Score every requirement of a feature by business impact × probability (1-5 × 1-5),
  place it in a risk zone, and turn the zone into concrete test depth: priority P0-P3,
  how many techniques/cases it deserves, and which pyramid levels must cover it. In the
  QA pipeline it produces the Risk Assessment table of test-plan.md (Stage 2) and ranks
  which spec gaps to raise with the business first (Stage 1); standalone it builds a
  product-level risk heatmap with failure-mode analysis. Use when: "risk assessment,"
  "risk matrix," "what could break," "prioritize test cases," "where to focus
  testing," "we can't test everything — what do we cut." Not for: writing the test
  plan document itself — use test-planning; not for allocating cases to unit/API/E2E —
  use test-pyramid-strategy.
  Related: test-planning, test-pyramid-strategy, spec-gap-analysis, security-testing,
  qa-project-context.
license: MIT
metadata:
  author: qa-agentic-pipeline
  adapted_from: petrkindlmann/qa-skills@risk-based-testing (MIT, Petr Kindlmann)
  version: "3.0"
  category: strategy
---

<objective>
Equal coverage across all requirements wastes effort on low-risk behavior while leaving critical paths under-tested — five boundary cases for a tooltip's length limit is effort stolen from the payment rule next to it. This skill quantifies risk as impact × probability and converts it into test depth, so the size of a test plan follows the business consequences of failure rather than the length of the spec's prose.
</objective>

## Role in the QA pipeline

| Stage | Who uses it | Input | Output |
|---|---|---|---|
| 1 — spec analysis | `spec-analyst` | Requirements Inventory, Q items | Track B questions ordered by the risk of the requirement they block (highest first) |
| 2 — QA documentation | `qa-doc-writer` | `spec-gap-report.md`, Risk Areas and key flows from `qa-project-context` | The `## Risk Assessment` table in `test-plan.md` — one row per `REQ-<n>` |
| 4 — review | `qa-doc-reviewer` | the Risk Assessment | Checks that P0/P1 requirements actually got the depth this skill prescribes |

In the pipeline you run **Pipeline Mode** (below) — a per-feature assessment that fits in one table. The full six-phase workflow after it is **Product Mode**: use it standalone, or when Pipeline Mode finds a requirement in the CRITICAL zone that deserves a failure-mode analysis.

## Pipeline Mode — per-feature Risk Assessment

1. **List the units of risk.** One row per `REQ-<n>` from the Requirements Inventory. Requirements blocked by a Q still get a row — their risk decides how loudly the Q should be raised.
2. **Score Impact (1-5)** with the Phase 2 impact table. Start from `qa-project-context` → Risk Areas and key user flows: a requirement on a listed key flow starts at Impact ≥ 4. Money, auth, personal data, and irreversible actions start at Impact ≥ 4 regardless.
3. **Score Probability (1-5)** with the Phase 2 probability table. Signals available at spec time: complexity of the rule (conditions, states, rounding, time zones), new vs. changed code (ask, or check git churn on the module if the repo is at hand), external dependencies, and **every open Q or A touching the requirement raises Probability by 1** — ambiguity is a defect source.
4. **Score = Impact × Probability → zone → priority → depth:**

   | Zone | Score | Priority | Minimum depth for this REQ |
   |---|---|---|---|
   | CRITICAL | 15-25 | P0 | Every applicable formal technique (all partitions, all boundaries, full decision table / state model); negative and error paths; at least one case at the lowest level that can prove the rule plus one E2E journey through it; failure-mode analysis (Phase 3) |
   | HIGH | 10-14 | P1 | All partitions and boundaries; top error paths; covered at the lowest sufficient level, E2E only if the risk lives in integration |
   | MEDIUM | 5-9 | P2 | One representative per partition + happy path; key error case |
   | LOW | 1-4 | P3 | Happy path, or explicitly deferred with the reason stated in Scope |

5. **Write the table** into `test-plan.md` (format in the artifact contract (`${CLAUDE_PLUGIN_ROOT}/skills/run-qa-pipeline/references/artifact-contract.md`)):

   ```markdown
   ## Risk Assessment
   | REQ | Impact | Probability | Score | Zone | Priority | Depth / rationale |
   |---|---|---|---|---|---|---|
   | REQ-1 | 5 | 3 | 15 | CRITICAL | P0 | Money: discount math + rounding; full BVA + decision table |
   | REQ-6 | 2 | 2 | 4 | LOW | P3 | Copy of the success toast; one E2E assertion inside REQ-1's journey |
   ```

6. **When scope must be cut**, cut from the bottom of the table up and say so in Scope — never silently drop a P0/P1 requirement.

The core cases of a requirement carry its priority; supporting cases (an exploratory charter, a cosmetic check) may be lower — but every REQ's highest-priority case matches the REQ's priority, so a P0 requirement is never covered only by P2 cases.


## Discovery Questions (Product Mode)

In Pipeline Mode most of these are answered by the spec and `qa-project-context`; ask only what changes an Impact or Probability score. Check `.agents/qa-project-context.md` first — if it exists, use it as the foundation and skip questions already answered there. Gather the rest from stakeholders across engineering, product, and operations.

### Revenue-Critical Flows
- Which user flows directly generate revenue? (checkout, subscription, billing, upgrades)
- What is the revenue impact per hour of downtime for each flow?
- Are there time-sensitive flows? (flash sales, market-hours trading, payroll deadlines)
- Which flows have contractual SLAs with financial penalties?

### Recent Failures
- What broke in the last 3 releases? What escaped to production?
- What were the root causes? (code defect, config error, third-party failure, data migration)
- What was the blast radius of each incident? (users affected, revenue lost, reputation impact)
- Were there near-misses caught late in testing that could have escaped?

### Fragile Areas
- Which parts of the codebase change most frequently? (high churn = high risk)
- Which modules have the lowest test coverage today?
- Which areas have the most complex business logic or the most conditional branches?
- Which code was written by engineers who have since left the team?

### Third-Party Dependencies
- Which external services does the product depend on? (payment processors, auth providers, CDNs, APIs)
- What is the historical reliability of each dependency?
- What happens when each dependency goes down? (graceful degradation or hard failure?)
- Are there single points of failure with no fallback?

### Compliance and Data
- What regulatory requirements apply? (GDPR, PCI-DSS, HIPAA, SOC2, SOX, EU AI Act)
- What data is most sensitive? (PII, financial, health, credentials)
- What are the legal consequences of a data breach or compliance violation?
- Are there audit requirements that mandate specific testing evidence?

---

## Core Principles

1. **Not all features are equal.** A bug in checkout that blocks purchases is categorically different from a misaligned icon on a settings page. Equal coverage everywhere wastes resources on low-risk areas while leaving critical paths under-tested.
2. **Risk = Impact × Probability.** Risk is not a gut feeling. It is a product of two dimensions scored independently: how bad if this fails (impact), and how likely to fail (probability). Score both consistently across the product, then multiply.
3. **Risk assessment is continuous.** A risk model created once and never updated creates false confidence. Risk changes when the product changes, when dependencies change, when the team changes, and after every production incident. Build reassessment into the rhythm.
4. **Near-misses are data.** A catastrophic bug caught in staging is not a success story — it is a signal that the model underestimated that area. Track near-misses with the same rigor as production incidents.
5. **Risk informs coverage, not the other way around.** Do not start with "we need 80% coverage everywhere." Start with "where would a failure hurt most?" and let the model drive coverage targets per module.

---

## Workflow

```
1. Identify → 2. Classify → 3. Analyze → 4. Heatmap → 5. Coverage → 6. Reassess → (repeat)
                                 ↑
                       score ≥ 10 only; skip to 4 if no items reach threshold
```

### Phase 1: Risk Identification (Product Mode)

Enumerate everything that could go wrong. Cast a wide net. Sources include:

- **Stakeholder interviews:** Product managers know business-critical flows. Engineers know fragile code. Support knows recurring user complaints.
- **Incident history:** Past failures predict future failures. Review post-mortems from the last 6–12 months.
- **Dependency mapping:** List every external service, database, message queue, and third-party API. Each is a risk vector.
- **Change analysis:** Areas with frequent code changes have higher defect probability. Use the ranked churn command in Phase 6 to find them; `git log --stat <file>` is for per-commit inspection of a specific suspect, not for ranking.
- **Architecture review:** Shared databases, single points of failure, synchronous chains, and tightly coupled modules amplify blast radius.

Use **HTSM v6.3** (Heuristic Test Strategy Model, Bach) as a Phase-1 lens — its state-based and boundary heuristics surface risks a pure feature-list misses. Download: https://www.satisfice.com/download/heuristic-test-strategy-model

Output: a raw list of risk items, each describing what could fail and what the consequence would be.

### Phase 2: Risk Classification

Categorize each risk item along two axes.

**Impact categories (how bad is it):**

| Score | Level | Definition | Examples |
|-------|-------|-----------|----------|
| 5 | Catastrophic | Revenue loss, data breach, legal action, user safety | Payment processing fails, PII exposed |
| 4 | Major | Significant user impact, SLA violation, major feature broken | Login broken for segment, data corruption |
| 3 | Moderate | Workflow disrupted, workaround exists | Search returns wrong results, export fails |
| 2 | Minor | Cosmetic or minor UX issue | Alignment bug, slow non-critical page |
| 1 | Negligible | No user impact, internal only | Admin tooltip wrong, log format issue |

**Probability categories (how likely is it):**

| Score | Level | Definition | Indicators |
|-------|-------|-----------|-----------|
| 5 | Frequent | Expected in most releases | High code churn, no tests, complex logic |
| 4 | Likely | Will probably happen within a quarter | Recent changes, partial coverage, known tech debt |
| 3 | Possible | Could happen, has happened before | Moderate complexity, some coverage |
| 2 | Unlikely | Improbable but not impossible | Stable code, good coverage, simple logic |
| 1 | Rare | Requires exceptional circumstances | Well-tested, rarely changed, simple |

Composite score = Impact × Probability. Frequent changes indicate defect probability, so a Moderate-impact (3) feature under heavy churn scores Probability 5 → **Risk score: 15 → CRITICAL zone**, despite "only" moderate impact. The composite score drives priority, not impact alone.

### Phase 3: Failure Mode Analysis

For each high-risk item (score ≥ 10), perform a detailed failure mode analysis.

```
Feature/Component: [name]
Risk Score: [impact × probability]

Failure Mode 1: [what specifically can fail]
  Trigger:            [what causes this failure]
  Blast Radius:       [users affected, systems affected, data affected]
  Detection Method:   [how would we know -- monitoring, user report, test]
  Current Mitigation: [existing tests, monitoring, feature flags, fallbacks]
  Gap:                [what is missing from current mitigation]

Failure Mode 2: ...
```

**Example — E-commerce Checkout (Risk Score 20, Impact 5 × Probability 4):**

```
Failure Mode 1: Payment charge succeeds but order not recorded
  Trigger:            Race condition between payment API callback and order write
  Blast Radius:       Individual users; money charged but no order confirmation
  Detection Method:   Payment reconciliation job (runs hourly), user complaint
  Current Mitigation: Idempotency key on payment, retry on order write
  Gap:                No automated test for the race condition; reconciliation delay is 1 hour

Failure Mode 2: Discount code applies incorrect amount
  Trigger:            Percentage discount on already-discounted item
  Blast Radius:       All users with stacked discounts; revenue leakage
  Detection Method:   Margin monitoring alert (>5% deviation)
  Current Mitigation: Unit tests for single discounts
  Gap:                No tests for discount stacking; no tests for rounding edge cases

Failure Mode 3: Inventory not reserved during checkout
  Trigger:            Concurrent purchases of last-stock item
  Blast Radius:       Oversold items, fulfillment failure, customer trust
  Detection Method:   Fulfillment team discovers during packing
  Current Mitigation: Database-level stock check on order creation
  Gap:                No load test simulating concurrent last-item purchases
```

#### AI/LLM failure classes

For AI/LLM features, classify against these CT-GenAI classes and score Impact and Probability independently like any other risk. The mitigation is the existence of an automated **eval suite**, not a single manual test.

> **AI/LLM-specific failure classes** (from ISTQB CT-GenAI v1.1, effective 27 April 2026):
> - **Hallucination / reasoning error** — Impact: moderate to major; Probability: high without explicit prompt-eval coverage. Detection: golden-dataset evals, fact-check assertions.
> - **Bias** — Impact: catastrophic in regulated industries (finance, healthcare, hiring). Probability: dataset-dependent. Detection: counterfactual evals, demographic-parity checks.
> - **Prompt injection / jailbreak** — Impact: major (data exfiltration, prompt extraction). Probability: high for any externally-facing LLM feature. Detection: Garak, PyRIT, Promptfoo redteam.
> - **Privacy leak** — Impact: catastrophic under GDPR/CCPA/EU AI Act. Probability: dataset-dependent. Detection: PII scanning of training data and prompts.
> - **AI Act / regulatory non-compliance** — Impact: catastrophic (fines, ban). Probability: high for EU-facing AI features. Detection: a compliance review against the applicable regulation.
>
> Tool freshness (mid-2026): PyRIT now lives at **microsoft/PyRIT** — the old Azure-hosted repo was archived March 2026, so do not point new redteam work at the legacy Azure path. Promptfoo was acquired by OpenAI (March 2026) but remains MIT-licensed. Garak is current and unchanged.

**Reference frameworks:** **CT-GenAI v1.1** (ISTQB, effective 27 April 2026) codifies the AI/LLM classes above. **WQR 2025-26** (Capgemini, 17th edition, Nov 2025) gives the adoption-stage framing for AI risk planning.

### Phase 4: Risk Heatmap

Plot all risk items on a 5×5 matrix to communicate priorities and drive coverage decisions.

```
                    PROBABILITY
                    Rare(1)   Unlikely(2)  Possible(3)  Likely(4)   Frequent(5)
                   +----------+-----------+-----------+----------+-----------+
  Catastrophic(5)  |  5  MED  | 10  HIGH  | 15  CRIT  | 20 CRIT  | 25  CRIT  |
                   +----------+-----------+-----------+----------+-----------+
  Major(4)         |  4  LOW  |  8  MED   | 12  HIGH  | 16 CRIT  | 20  CRIT  |
I                  +----------+-----------+-----------+----------+-----------+
M  Moderate(3)     |  3  LOW  |  6  MED   |  9  MED   | 12 HIGH  | 15  CRIT  |
P                  +----------+-----------+-----------+----------+-----------+
A  Minor(2)        |  2  LOW  |  4  LOW   |  6  MED   |  8 MED   | 10  HIGH  |
C                  +----------+-----------+-----------+----------+-----------+
T  Negligible(1)   |  1  LOW  |  2  LOW   |  3  LOW   |  4 LOW   |  5  MED   |
                   +----------+-----------+-----------+----------+-----------+
```

**Zone boundaries and action mapping:**

| Zone | Score Range | Color | Testing Action |
|------|------------|-------|---------------|
| CRITICAL | 15-25 | Red | Automate fully + monitor in production + load test + manual exploratory |
| HIGH | 10-14 | Orange | Automate fully + periodic manual review |
| MEDIUM | 5-9 | Yellow | Automate happy path + key error cases |
| LOW | 1-4 | Green | Manual testing on release or skip entirely |

Populated example (where each named risk lands):

```
                    Rare(1)   Unlikely(2)  Possible(3)  Likely(4)   Frequent(5)
  Catastrophic(5)             Auth bypass   Payments fail  Checkout crash
  Major(4)                                  Data export    Search broken  User upload
  Moderate(3)                  Report fmt    Email deliver  Profile edit
  Minor(2)         Footer link Tooltip text  Theme switch
  Negligible(1)    Admin label
```

### Phase 5: Test Coverage Alignment

Map test density to risk level. Every zone gets a prescribed approach.

| Risk Zone | Unit Tests | Integration Tests | E2E Tests | Manual Testing | Monitoring |
|-----------|-----------|------------------|-----------|---------------|-----------|
| CRITICAL (15-25) | 90%+ branch coverage | All service boundaries | Full user journey + error paths | Exploratory each release | Real-time alerts, synthetic checks |
| HIGH (10-14) | 80%+ branch coverage | Key interactions | Happy path + top 3 error paths | Spot checks | Dashboard + daily review |
| MEDIUM (5-9) | 70%+ branch coverage | Happy path only | Happy path only | On major changes | Weekly review |
| LOW (1-4) | Basic happy path | None required | None required | On initial build | None required |

#### Gap Analysis Worksheet

Compare current coverage against required coverage per risk zone:

```
Feature: [name]
Risk Zone: [CRITICAL / HIGH / MEDIUM / LOW]      Risk Score: [number]

Required Coverage:
  Unit:        [target %]     Current: [actual %]     Gap: [delta]
  Integration: [required?]    Current: [exists? y/n]  Gap: [missing scenarios]
  E2E:         [required?]    Current: [exists? y/n]  Gap: [missing flows]
  Monitoring:  [required?]    Current: [exists? y/n]  Gap: [missing alerts]

Priority: [P0 / P1 / P2 / P3]
Estimated Effort: [hours / story points]
Owner: [name]                Target Sprint: [sprint number]
```

A churn signal forces this worksheet open: a module that changed 47 times in 3 months (Probability → 5) with only 40% branch coverage and no integration tests jumps zones (e.g. MEDIUM → HIGH), and the new coverage target is justified by the churn, not picked arbitrarily.

See `references/examples.md` for four fully-scored examples (checkout, media platform, third-party API, auth) showing the path from risk score to prescribed coverage.

### Phase 6: Monitoring and Reassessment

Risk assessment is not a one-time activity. Build reassessment into the team's rhythm.

**Reassessment triggers:**
- After every production incident (within 48 hours): re-score the affected items, check dependency health, and re-run the Phase-5 gap analysis to expose any coverage gap the incident revealed
- When a new feature area is introduced
- When a critical dependency changes (API version, provider switch)
- When team composition changes significantly
- Quarterly at minimum, even without triggers

**Continuous risk signals to monitor:**
- **Code churn by module** (ranked frequency table):
  ```bash
  git log --since="3 months ago" --name-only --format= | grep -v '^$' | sort | uniq -c | sort -rn | head -20
  ```
- **Defect clustering:** Which modules produce the most bugs? Track with issue labels.
- **Near-miss frequency:** How often do staging/QA catches prevent production incidents?
- **Dependency health:** Monitor status pages and uptime of critical third-party services.
- **Coverage trends:** Is coverage increasing or decreasing in high-risk areas?

---

## Anti-Patterns

### Testing everything equally
Applying the same coverage target to every feature regardless of risk. A 90% target on a settings page wastes effort that should go to payments or auth. Let the risk model drive allocation.

### One-time risk assessment
Creating a matrix during planning and never updating it. The product, team, and dependencies all change. A model from 6 months ago is outdated and out of date the moment a dependency, feature, or incident shifts the picture — it does not reflect today. Schedule reassessment and enforce it.

### Ignoring near-misses
Treating bugs caught in staging as pure successes. If a critical bug was caught only by manual testing, the automated safety net has a gap. Document near-misses and adjust the model.

### Risk theater
Going through the motions (filling matrices, drawing heatmaps) without changing test allocation. If the heatmap exists but coverage does not align to it, the exercise was wasted. Verify alignment quarterly. Bolton's "Quality Engineering Is Not Testing" (2026-04-20) warns of exactly this — building a heatmap and calling it "QE done." Reference: https://developsense.com/blog/2026/04/quality-engineering-is-not-testing

### Anchoring on historical risk
Over-weighting past incidents and under-weighting new vectors. A module that failed 2 years ago and was since rewritten may no longer be high risk; a brand-new third-party integration has unknown risk that deserves attention.

### Confusing severity with priority
Severity is how bad a failure is; priority is how urgently to test it. A catastrophic-but-rare failure (earthquake destroys data center) can be lower priority than a moderate-but-frequent one (search occasionally wrong). Use the composite score, not impact alone.

---

## Verification

Prove the matrix is real and aligned before calling it done — smallest check first:

- **Artifact exists and is tracked:** `git ls-files | grep -E 'risk-matrix|qa-project-context'` returns the file. An untracked draft on someone's laptop is not a risk model.
- **Every in-scope feature is scored:** grep the artifact for rows missing an impact or probability number. A feature with a name but no score is a gap, not a low risk.
- **Top items have failure mode analysis:** every item scoring ≥ 10 has a block with all five fields (Trigger, Blast Radius, Detection Method, Current Mitigation, Gap). A failure mode with an empty Gap line was not actually analyzed.
- **Coverage aligns to the heatmap:** for each CRITICAL/HIGH feature, confirm the prescribed coverage from the Phase-5 table actually exists (run the suite, check the coverage report's per-module numbers against the target). If the heatmap says CRITICAL but the module has 40% branch coverage and no E2E, the exercise was Risk Theater.
- **Churn signal is current:** re-run the Phase-6 churn command; any module in the top 10 that is not scored ≥ Probability 4 is a model that has drifted from reality.

## Done When

**Pipeline Mode**
- `test-plan.md` has a `## Risk Assessment` row for every `REQ-<n>` in the Requirements Inventory, each with Impact, Probability, Score, Zone, Priority, and a one-line rationale.
- Every REQ's highest-priority case carries the REQ's priority (a P0 requirement has at least one P0 case).
- Every CRITICAL requirement either has a Phase 3 failure-mode block in the plan or a stated reason why none applies.
- Any requirement deferred for lack of time is listed in Scope with its zone — nothing P0/P1 is dropped silently.

**Product Mode**
- A scored risk matrix exists as a tracked artifact (`.agents/qa-project-context.md` Risk Areas or a committed `risk-matrix.md`), every in-scope feature scored on impact (1-5) and probability (1-5) and placed in a named zone.
- Every feature scoring ≥ 10 has a completed failure mode analysis (trigger, blast radius, detection method, current mitigation, gap).
- Coverage requirements per zone are mapped against current coverage, with each gap assigned a Priority (P0-P3) and an owner.
- Reassessment triggers and cadence are recorded in the same artifact.

## Reference Files (in `references/`)

- **examples.md** — Four fully-scored worked examples (checkout, media platform, third-party API, auth): risk profile → failure modes → prescribed coverage.

## Related Skills

- **test-planning** — the plan document whose Risk Assessment section this skill fills.
- **test-pyramid-strategy** — decides the level for each case; the depth column here says which levels must be represented for a P0/P1 requirement.
- **spec-gap-analysis** — supplies the REQ inventory and the Q/A items that raise Probability.
- **security-testing** — the security lens; auth, input handling, payments and personal data start at Impact ≥ 4.
- **qa-project-context** — key flows and Risk Areas that seed Impact scores; Product Mode writes the matrix back there.
- **qa-doc-review** — verifies P0/P1 requirements received the prescribed depth.
