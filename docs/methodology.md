# Methodology: P0–P3 risk priorities, boundary values, decision tables, and planted-defect evals

[Русская версия](methodology.ru.md)

This document explains the four ideas the pipeline rests on. Every example comes from the
recorded run in [`eval-results/2026-10-27`](../eval-results/2026-10-27): these are real
artifacts the agents produced, not made-up illustrations.

The running example is the "Cart, shipping and order cancellation" spec from the
`stage2-test-design-from-gap-report` case:

| ID | Requirement |
|---|---|
| REQ-1 | Quantity per cart line is 1 to 20 |
| REQ-2 | An out-of-range quantity shows "Quantity must be between 1 and 20" and keeps the previous value |
| REQ-3 | Subtotal = Σ price × quantity, recalculated after every change |
| REQ-4 | Shipping is 300 ₽, free when the subtotal is 5000 ₽ **or more** |
| REQ-5 | Loyalty members get 5% off when the subtotal is at least 3000 ₽, except during a sale |
| REQ-6 | Order: Created → Paid → Shipped → Delivered; only Created or Paid can be cancelled |

---

## 1. Risk-based priorities P0–P3

### The idea

Testing everything equally deep is neither possible nor useful. A bug in the amount to
pay and a typo in a tooltip cost the business very different amounts. So the depth of
testing for each requirement follows its **risk**, not the length of its description.

### How it is scored (`risk-based-testing`, Pipeline Mode)

```
Risk = Impact (1–5) × Probability (1–5)      → range 1…25
```

**Impact** — what happens if the requirement breaks: 5 — money lost, data leaked, an
irreversible action; 3 — a broken flow with a workaround; 1 — internal, unnoticed by
users. Requirements about money, access, personal data, and irreversible actions start
at Impact ≥ 4.

**Probability** — how likely a defect is: rule complexity (several conditions, rounding,
time zones), new or changed code, external dependencies. One pipeline-specific rule:
**every open question (Q) or assumption (A) about a requirement adds +1** — ambiguity in
the spec is itself a defect source.

| Zone | Risk | Priority | Minimum depth |
|---|---|---|---|
| CRITICAL | 15–25 | **P0** | Every applicable technique: all partitions, all boundaries, full decision table or state model, negative paths; a case at the lowest level that proves the rule + one E2E journey |
| HIGH | 10–14 | **P1** | All partitions and boundaries, top error paths, at the lowest sufficient level |
| MEDIUM | 5–9 | **P2** | One representative per partition + happy path + key error |
| LOW | 1–4 | **P3** | Happy path, or an explicit deferral with the reason stated in Scope |

### Example from the run

| REQ | Impact | Probability | Risk | Priority | Why |
|---|---|---|---|---|---|
| REQ-5 discount | 5 | 5 | 25 | **P0** | Money + three conditions + open Q1, A1, A2 (+1 each) |
| REQ-6 cancellation | 4 | 4 | 16 | **P0** | Irreversible action + access control (OWASP A01) |
| REQ-4 shipping | 5 | 3 | 15 | **P0** | Money, the 5000 boundary |
| REQ-1 quantity | 4 | 3 | 12 | **P1** | Quantity abuse (negative, overflow) |
| REQ-3 subtotal | 5 | 2 | 10 | **P1** | Money, but simple arithmetic |
| REQ-2 message | 3 | 3 | 9 | **P2** | Text and keeping the value |

Result: the agent wrote 9 cases for REQ-5 (full decision table, both sides of the
threshold, rounding) and 3 for REQ-2.

### Rules people ask about

- **A case inherits priority from its requirement:** the most important case of a P0
  requirement is P0 too. Supporting cases (an exploratory charter, a cosmetic check) may be
  lower. `check_artifacts.py` fails a plan where a P0 requirement is covered only by P2 cases.
- **When time runs out**, cut from the bottom of the table and say so in Scope. P0/P1 are
  never dropped silently.
- **Severity ≠ priority.** Severity is how bad a defect is once it exists. Priority is how
  urgently to test or fix. A catastrophic but very unlikely failure can rank below a
  moderate but frequent one, because the product decides, not impact alone.

---

## 2. Boundary value analysis

### The idea

Defects cluster at the edges of ranges: `<` instead of `<=`, off-by-one, overflow, empty
input. The middle of a range almost never breaks. For a range `[min, max]` test:

```
min-1 (invalid)   min (valid)   max (valid)   max+1 (invalid)
```

That is two-point BVA. Three-point BVA adds `min+1` and `max-1`, used for P0 when an error
is especially expensive. For money the step is the smallest unit (0.01), for dates the
second at midnight, for strings the length, not the content.

**Relation to equivalence partitioning.** EP splits inputs into classes the system treats
the same and picks one representative per class. BVA tests the edges of those classes.
They are used together: classes "below 1", "1–20", "above 20" plus boundaries 0, 1, 20, 21.

### Examples from the run

| Requirement | Boundary values | Cases |
|---|---|---|
| REQ-1 quantity 1…20 | 0, 1, 20, 21 | TC-UNIT-001…004 |
| REQ-4 free shipping from 5000 | 4999.99 → 300; 5000.00 → 0 | TC-UNIT-008, TC-UNIT-009 |
| REQ-5 discount from 3000 | 2999.99 → 0; 3000.00 → 150.00 | TC-UNIT-012, TC-UNIT-013 |

### Where BVA caught a bug

The Stage 3 eval repo has a planted defect: `if subtotal > 5000` instead of `>=`. The test
at 4999.99 passes, and a mid-range test would pass too. Only **TC-UNIT-004 at exactly
5000.00** fails — and the agent reported it as a product defect rather than "fixing" the
expectation to match the code.

### Where BVA hits the spec

The promo-code spec says "orders **over** 3000 ₽". Is exactly 3000.00 included? Test design
cannot decide that; it is a spec gap. Stage 1 raises it as a question for the analyst
(Track B) or an explicit assumption, and only then does Stage 2 build boundary cases. This
gap is planted in the eval spec on purpose (defect D2).

### A typical mistake the reviewer catches

The Stage 4 eval plants a plan that says "BVA" but tests only 1 and 20. The reviewer rated
it **Blocking** (R-3): "the invalid boundaries 0 and 21 are the ones that catch `<` vs `<=`".
A technique applied wrong is treated as worse than one skipped: it looks like coverage.

---

## 3. Decision table testing

### The idea

When the outcome depends on a **combination** of conditions, checking each condition
separately misses interaction bugs. A decision table lists condition combinations
(columns, called rules) and the expected action for each. Each rule is one test case.

`n` boolean conditions give `2ⁿ` combinations. Combinations with the same outcome collapse
with a "don't care" (`—`), so the real number of rules is usually smaller.

### Example from the run: REQ-5, member discount

Three conditions → 8 combinations → 4 rules:

| Condition / action | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| Loyalty member? | Y | Y | Y | N |
| Subtotal ≥ 3000? | Y | Y | N | — |
| Sale period? | N | Y | — | — |
| **5% discount** | **Yes** | No | No | No |

R4 replaces 4 combinations (not a member → nothing else matters), R3 replaces 2. Four
cases instead of eight, with no rule left untested.

The table combines with BVA: rule R3 is tested at 2999.99 and R1 at exactly 3000.00
(TC-UNIT-012, TC-UNIT-013). A separate case checks rounding: 3000.10 × 5% = 150.005 →
150.01 (half-up, assumption A1).

### Decision table or pairwise?

- **Decision table** — when the spec has a small set of **named business rules** (who gets
  a discount, what shipping costs).
- **Pairwise** — when there are many independent parameters and the risk is an unexpected
  interaction (browser × OS × role × locale). All pairs of values are covered, not all
  combinations, and that trade-off is stated explicitly.
- If the spec **doesn't say** what should happen for a combination, the table must not
  invent an answer — that is a question for the analyst.

### Related technique: state transitions

REQ-6 (order lifecycle) uses a state model: one case per allowed transition and one per
**forbidden** transition (cancel Shipped, cancel Delivered, Created → Shipped skipping Paid).
Forbidden transitions are the ones teams skip most often; the Stage 4 eval plants exactly
that omission, and the reviewer flagged it as Blocking (R-1).

---

## 4. How the agents are tested: evals on specs with planted defects

### The idea

To check whether an agent finds problems, you need an answer known in advance. It is the
same principle as **fault seeding** in classic QA and mutation testing for test suites:
insert defects known only to the evaluator, then measure the share the evaluated party finds.

### How a case is built

```
evals/stage1-checkout-promo-planted-defects/
├── resources/spec.md      promo-code spec with 8 planted defects
├── ground-truth.yaml      what was planted and how to recognise a finding
├── scaffold.sh            copies the spec into the run's empty workspace
├── prompt.md              a realistic user request + run limits
└── graders/               checks on the result
```

Defects planted in the promo-code spec:

| ID | Type | What was planted |
|---|---|---|
| D1 | Contradiction | §2.3 "valid up to and including the date" vs §5.2 "stops working at the start of the date" |
| D2 | Boundary | "Over 3000" — is exactly 3000 included? Before or after the discount? |
| D3 | Untestable NFR | "Code validation must be fast" — no number |
| D4 | Missing error path | No messages for a non-existent code, wrong format, below minimum |
| D5 | Terminology | "Coupons" and "vouchers" are never defined |
| D6 | Security (A07) | No attempt limit — codes can be brute-forced |
| D7 | Concurrency (A06) | A single-use code applied in two carts at once |
| D8 | Missing rule | Rounding of percentage discounts; a fixed discount larger than the subtotal |

Likewise: a Russian password-reset spec with 6 security gaps, a test plan with 4 defects
for the reviewer, a repo with a `>` instead of `>=` bug for Stage 3, a spec with no
requirements (the pipeline must stop as `BLOCKED`), and an interrupted session (it must
resume at Stage 3).

### How results are scored

1. **`claude plugin eval` graders** — mostly deterministic: a regex over a produced file,
   file existence, whether a tool was called (e.g. the agent did **not** edit
   `src/shop/pricing.py`). An LLM judge only where regex can't express the check, with
   explicit PASS/FAIL conditions and a majority of three votes.
2. **Recall against ground truth** — `tools/score_spec_analysis.py`. A defect counts as
   found only when **one** finding of the report (a table row, a question, an assumption)
   matches all pattern groups. Keywords scattered across unrelated sentences don't count;
   summaries and checklists are excluded — mentioning a topic in passing is not raising it.
3. **Contract check** — `tools/check_artifacts.py`: structural correctness (every
   requirement traced, IDs consistent, all eight case fields present).
4. **Reproducibility** — run artifacts are committed; `verify_recorded_runs.py` in CI
   recomputes the published numbers with the current tools.

Result of the 2026-10-27 run: **8 of 8** defects found in the promo-code spec, **6 of 6** in
the password-reset spec; the reviewer found all 4 planted defects in the test plan.

### Honest limitations

- **Recall is measured, precision is not.** The agent raised 28 questions for 8 planted
  defects. Extra questions are not penalised, so finding volume is published next to recall.
- **One run per case** is a signal, not a statistic: model outputs vary.
- **The specs and the ground truth have the same author.** It measures whether planted
  defects are found, not an independent expert's verdict on the whole report.
- **Graders make mistakes too.** Reading the transcripts revealed two false-negative
  graders (a too-narrow regex; a check that matched file content instead of the path).
  They are fixed in git history; the stored artifacts allow re-grading.

### What the evals found in the plugin itself

Asked "make autotests for these cases", Claude first wrote correct tests itself instead of
dispatching `autotest-builder` — so no `autotest-summary.md` and no task-state update. The
agent and skill trigger descriptions were fixed; the 2026-10-30 re-run dispatched
`autotest-builder` and scored 1.00 instead of 0.50 (details in [evals.md](evals.md)).

---

## FAQ

**How is your P0 different from bug severity?**
P0 here is the testing priority of a requirement before any defect exists, computed from
impact and probability. Severity is a property of a defect that has been found.

**Why does an open question raise probability?**
If a rule in the spec is ambiguous, the developer and the tester are likely to read it
differently. That is a direct defect source, not a formality.

**Why min-1 and max+1 if the valid boundaries are already tested?**
The invalid boundaries are what catch `<` vs `<=`. A test at 1 and 20 passes both for
`0 < q <= 20` and for `0 <= q <= 20` — it cannot tell the correct code from the wrong one.

**Why not test all 8 discount combinations?**
You can, but 4 of them duplicate each other in outcome and code path. A decision table with
"don't care" gives the same rule coverage in half the cases, and each remaining case points
at a specific rule when it fails.

**How do you check the agent doesn't bend a test to fit a bug?**
The Stage 3 eval has a real bug. One grader requires the failure to be reported as a
product defect; another checks the agent never called Write/Edit on the product file. The
Stage 4 reviewer also re-runs a sample of tests reported as passed.
