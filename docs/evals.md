# Evals — how the plugin is tested

An agentic pipeline can look impressive in a demo and still lose requirements, invent
rules, or report tests as passing that never ran. The evals here are built to catch
exactly that, in three layers that trade cost for realism.

| Layer | Tool | Model calls | Runs in |
|---|---|---|---|
| 1. Static validation | `tools/validate_plugin.py`, `claude plugin validate` | none | CI, every push |
| 2. Contract checks | `tools/check_artifacts.py` + pytest | none | CI, every push |
| 3. Behavioral evals | `claude plugin eval` suite in `evals/` + `tools/score_spec_analysis.py` | yes | manual workflow; results recorded in `eval-results/` |

## Layer 1 — static validation

`tools/validate_plugin.py` walks every skill and agent and fails on:

- malformed YAML frontmatter, a skill whose `name` differs from its directory, a
  description over 1024 characters or without a "Use when" trigger;
- a `Related` link or an inline reference to a skill this plugin does not ship — in
  particular any of the ~20 skills of the upstream library that were not vendored;
- a `references/*.md` or `${CLAUDE_PLUGIN_ROOT}/…` path that does not exist;
- an agent that preloads a non-existent skill, uses an unknown tool, or does not point
  at the artifact contract and the output standards;
- drift between the artifact contract's case-field labels and `test-case-management`;
- a stage table in `run-qa-pipeline` naming an unknown agent or skill;
- `THIRD_PARTY_NOTICES.md` out of sync with the skills that declare `adapted_from`;
- unbalanced code fences in any skill or reference file.

`tests/test_validate_plugin.py` breaks a copy of the plugin in each of these ways and
asserts the validator reports it. CI also runs Claude Code's own `claude plugin validate`.

## Layer 2 — the artifact contract, checked by a program

Every stage writes markdown with a fixed skeleton
([artifact contract](../skills/run-qa-pipeline/references/artifact-contract.md)), so
`tools/check_artifacts.py` can verify a run's output without a model:

| Stage | Examples of what is checked |
|---|---|
| 1 | Required sections; testability score 1–5; `REQ` IDs sequential; every non-testable REQ points at an existing `Q`; one global `Q` sequence; every `Q`/`A` in the report has an inline marker in the annotated spec and vice versa; security lens filled |
| 2 | Every case has all eight fields; ID level = file = Level field; Level has a justification; every case traces to an existing REQ; every REQ is covered, out of scope, or blocked by a real Q; risk row and matrix row for every REQ; each REQ's highest-priority case matches its priority; no vague expected results (EN/RU list); E2E share ≤ 50% |
| 3 | Every automatable case mapped exactly once; statuses from the allowed set; commands recorded |
| 4 | A traceability verdict for every REQ; findings numbered `R-n` with a severity |
| state | Valid JSON; known status; `output_language`; done stages have outputs; `IN_REVIEW` ⇒ all stages done |
| language | Reports are actually written in the run's language |

Two golden runs (English, Russian) in `tests/fixtures/` pass all checks;
`tests/test_check_artifacts.py` mutates them into 25 realistic defects — a requirement
silently dropped, a renumbered marker, a case in the wrong level file, a P0 requirement
covered only by P3 cases, an inverted pyramid, an unmapped case, an unrated finding — and
asserts each is reported by name.

The checker is deliberately *structural*. It can tell that a REQ has no case; it cannot
tell that a boundary-value case forgot `max+1`. That semantic layer is what the reviewer
agent and the behavioral evals are for.

## Layer 3 — behavioral evals

The suite in [`evals/`](../evals) uses Claude Code's
[plugin eval](https://code.claude.com/docs/en/plugin-evals) format: each case is a
realistic request (`prompt.md`), an optional workspace fixture (`scaffold.sh`), and
graders. Most graders are deterministic — `regex` over a produced file, `file_exists`,
`tool_used` — with an `llm` judge only for judgment that regex can't express, written as
explicit PASS/FAIL conditions.

| Case | Stage | What is planted / asked | What must happen |
|---|---|---|---|
| `stage1-checkout-promo-planted-defects` | 1 | EN promo-code spec with **8 planted defects**: an expiry-date contradiction, a `> vs ≥` threshold, an unmeasurable "fast", missing error paths, undefined "coupons/vouchers", no brute-force limit, a single-use race, no rounding rule | Requirements inventory; the contradiction under *Contradictions*; the security lens raises brute force; inline markers; no test plan yet |
| `stage1-password-reset-security-lens-ru` | 1 | RU password-reset spec with **6 planted gaps**: account enumeration via different messages, no token lifetime, token reuse, no rate limit, undefined "strong password", sessions after reset | Report in Russian; Security Lens section citing A07; enumeration, token lifetime, rate limiting raised as questions |
| `orchestration-blocks-on-empty-spec` | orchestration | A marketing text with no requirement | Task ends `BLOCKED`; no test plan or cases; the reply explains what the spec owner must provide |
| `stage2-test-design-from-gap-report` | 2 | A finished gap report (6 REQs: limits, money, a 3-condition discount, an order state machine) | Risk table and matrix for every REQ; boundaries `0/1/20/21` and `4999.99/5000`; a decision table; an **illegal** state transition; ≤ 4 E2E cases; no code |
| `stage3-autotests-python-ru` | 3 | A pytest repo with an existing suite and a **planted product bug** (`>` instead of `>=` for free shipping); RU cases | Tests extend `tests/`, carry `TC-UNIT-…` IDs and Russian titles, are run with pytest; the boundary failure is reported as a suspected product defect; `src/` untouched; the API case `not run` with the reason |
| `stage4-review-catches-planted-defects` | 4 | A complete-looking plan with **4 planted defects**: REQ-6 has no illegal-transition case, BVA without `min-1/max+1`, a pure calculation tested only at E2E, a vague expected result | Each defect reported with a citation and a severity; nothing rewritten; Disputed used only for real judgment calls |
| `orchestration-resume-interrupted-stage3` | 3–4 | Task file with stages 1–2 done and stage 3 interrupted, plus a half-written test file | Stages 1–2 never rewritten; stage 3 redone whole; stage 4 run; `IN_REVIEW`; checkpoint written |
| `routing-concept-question-no-pipeline` | routing | "What's the difference between EP and BVA?" | A short correct answer; no agents, no pipeline, no files |

### Recall against ground truth

For the two Stage 1 cases, `ground-truth.yaml` lists every planted defect with regex
groups that must all match **inside one finding** (a Q/A entry, an inventory row, a
security-lens line). `tools/score_spec_analysis.py` reports recall and the volume of
findings, so "found 8 of 8 with 22 questions" can be read honestly next to each other.
Summary paragraphs and checklists are excluded, so naming a topic in passing doesn't
count as raising it.

### Recorded results

`tools/collect_eval_run.py` turns a run into a committed record under
`eval-results/<run-id>/`: the harness's `aggregate-result.json` and `report.html`, and per
case the artifacts the agents actually produced, the transcript, and `scores.json` with
contract conformance and recall computed independently of the graders.
`tools/verify_recorded_runs.py` re-derives every recorded number in CI.

<!-- EVAL-DETAILS:START -->
#### Run 2026-10-27

See the results table in the [README](../README.md#evidence-that-it-works). Per-case
`scores.json` under [`eval-results/2026-10-27/`](../eval-results/2026-10-27) list the
artifacts produced, tools and agents used, contract checks that failed, and recall.
Transcripts were not committed (≈1.5 MB each); the HTML report keeps every grader's
verdict and the judge's reasoning.

What the run changed in the plugin: Stage 3 trigger descriptions (`autotest-builder`,
`ai-test-generation`, `run-qa-pipeline`) — see footnote ³ in the README. What it changed
in the suite: two grader fixes (footnote ¹). Notable expected failures in the contract
column: the Stage 4 fixture keeps its planted vague expected result, and a `BLOCKED` spec
has, by definition, an empty requirements inventory.

#### Re-run 2026-10-30 — Stage 3 after the trigger fix

[`eval-results/2026-10-30-stage3-rerun`](../eval-results/2026-10-30-stage3-rerun):
score **1.00** (was 0.50), $0.36. The request "сделай автотесты по этим кейсам" now
dispatches `qa-agentic-pipeline:autotest-builder`, which extended `tests/` with
`test_pricing_rules.py` and `test_cart_api.py`, ran pytest, reported TC-UNIT-004 as a
suspected product defect (expected 0.00 at exactly 5000.00, got 300.00 — the planted
`>` instead of `>=`), marked TC-API-001 `not run` (no `CART_API_URL`), left TC-MAN-001
manual, set Stage 3 to `done` in the task file, and did not touch `src/`. Contract
conformance of the produced docs: 60/60.
<!-- EVAL-DETAILS:END -->

### Running the suite

```bash
# Linux: the shell sandbox needs bubblewrap and socat
sudo apt-get install -y bubblewrap socat

claude plugin eval . \
  --scaffold --trust-plugin \
  --allow-tools Write Edit Bash \
  --ablation none --runs 1 -j 3 \
  --keep-temp --output-dir /tmp/qa-evals

python tools/collect_eval_run.py --results /tmp/qa-evals --kept /tmp/claude-eval-* --run-id $(date +%F)
```

`--scaffold` runs the cases' `scaffold.sh` (they only copy fixtures into the empty run
workspace). `Bash` is needed by Stage 3 to run pytest and by the orchestrator to take
timestamps; every command runs inside Claude Code's OS-level sandbox, confined to the run
workspace. `--ablation none` skips the no-plugin baseline: without the plugin there is no
pipeline, artifact contract, or task file to grade, so the baseline would mostly measure
the graders. The GitHub Actions workflow `Behavioral evals` runs the same command on
demand with an `ANTHROPIC_API_KEY` secret.

### Limitations

- One run per case is a smoke signal, not a statistic; LLM runs vary. Use `--runs 3` (the
  harness default) before drawing conclusions from a score change.
- Ground truth was written by the same author as the specs. It measures whether planted
  defects are found, not how a real spec owner would rate the whole report.
- Regex graders can produce false negatives when the agent phrases a finding in a way
  the pattern didn't anticipate. When that happened during calibration the grader was
  widened and the change is visible in git history; the recorded artifacts let anyone
  re-grade.
- Stage 3 is evaluated on a small Python repo; the Playwright and API playbooks are
  exercised through the pipeline's documents but not against a live web app here.
