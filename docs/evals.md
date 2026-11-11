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

Every case that reaches Stage 3 also carries three `match: not_contains` regexes over the
trace that check **who** did the work, not only that it got done: a line from the main
thread (`"parent_tool_use_id":null`) must never Write/Edit `autotest-summary.md` or a test
file, nor run the suite (`pytest`, `vitest`, `jest`, `playwright test`; `--version` checks
are allowed). `tool_used` can't tell the main thread from a sub-agent, so these are regexes.
A fourth, `defect-test-not-silenced`, fails if any test file written in the run carries an
expected-failure marker (`pytest.mark.xfail`, `test.fail`, `test.fixme`, `it.failing`):
the planted bug must leave a red test. A plain `skip` for a missing prerequisite is allowed.

| Case | Stage | What is planted / asked | What must happen |
|---|---|---|---|
| `stage1-checkout-promo-planted-defects` | 1 | EN promo-code spec with **8 planted defects**: an expiry-date contradiction, a `> vs ≥` threshold, an unmeasurable "fast", missing error paths, undefined "coupons/vouchers", no brute-force limit, a single-use race, no rounding rule | Requirements inventory; the contradiction under *Contradictions*; the security lens raises brute force; inline markers; no test plan yet |
| `stage1-password-reset-security-lens-ru` | 1 | RU password-reset spec with **6 planted gaps**: account enumeration via different messages, no token lifetime, token reuse, no rate limit, undefined "strong password", sessions after reset | Report in Russian; Security Lens section citing A07; enumeration, token lifetime, rate limiting raised as questions |
| `orchestration-blocks-on-empty-spec` | orchestration | A marketing text with no requirement | Task ends `BLOCKED`; no test plan or cases; the reply explains what the spec owner must provide |
| `stage2-test-design-from-gap-report` | 2 | A finished gap report (6 REQs: limits, money, a 3-condition discount, an order state machine) | Risk table and matrix for every REQ; boundaries `0/1/20/21` and `4999.99/5000`; a decision table; an **illegal** state transition; ≤ 4 E2E cases; no code |
| `stage3-autotests-python-ru` | 3 | A pytest repo with an existing suite and a **planted product bug** (`>` instead of `>=` for free shipping); RU cases | Tests extend `tests/`, carry `TC-UNIT-…` IDs and Russian titles, are run with pytest; the boundary failure is reported as a suspected product defect; `src/` untouched; the API case `not run` with the reason |
| `stage4-review-catches-planted-defects` | 4 | A complete-looking plan with **4 planted defects**: REQ-6 has no illegal-transition case, BVA without `min-1/max+1`, a pure calculation tested only at E2E, a vague expected result | Each defect reported with a citation and a severity; nothing rewritten; Disputed used only for real judgment calls |
| `stage3-greenfield-no-tests-ru` | 3 | The same cases on a Python repo with **no tests at all** (no `tests/`, no pytest config, no CI) and the same planted bug | Stack Profile says nothing was found and justifies pytest; one framework, minimal scaffold; no JS test stack created; test files open with a header naming the task; pytest run; the boundary failure still reported as a product defect |
| `pipeline-e2e-cart-pricing-ru` | 1–4 | One request — "прогони QA-пайплайн по ТЗ" — on a 7-requirement RU spec and the pytest repo with the planted bug; the user is away | All four agents dispatched; gap report, plan, autotest summary, review and checkpoint written; task `IN_REVIEW`; new tests extend `tests/` and are run; the 5000 ₽ boundary reported as a defect; `src/` untouched. **This is the run the per-stage token cost is measured on** |
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

#### Local run 2026-11-11 — the whole pipeline end to end, and a repo with no tests

[`eval-results/2026-11-11-local`](../eval-results/2026-11-11-local), Claude Sonnet 5.5,
one run per case. Run on Windows, where `claude plugin eval` refuses to grant Bash (no
sandbox backend), so each case's prompt was run headlessly in a workspace prepared by its
`scaffold.sh` (`claude -p … --plugin-dir . --tools <the case's tools> --output-format
stream-json`), recorded with `collect_eval_run.py --case … --workspace … --trace …
--session …`, and graded by applying the same graders by hand. Bash was limited to an
allowlist (`pytest`, `python`, `cd`, `ls`, `cat`, …); background agents cannot ask for
permission, so commands Claude Code's shell checks hold for approval (`$(…)`, variables,
heredocs) were denied — 12 times in the e2e run, 3 in the greenfield run. Under the
harness on Linux those run in the sandbox instead.

- **`pipeline-e2e-cart-pricing-ru`** — all deterministic graders pass (14/14), the
  checkpoint reply meets the judge criteria. All four agents ran in order (Stage 1
  1.5 min, 2 — 5.5, 3 — 1.4, 4 — 4.0); 19 REQs and 11 questions from a 7-point spec, the
  three planted ambiguities raised (unmeasurable "быстро" → Q5, rounding mode → Q6,
  free-shipping threshold before/after the discount → a Disputed item); 41 cases
  (18 unit / 16 API / 5 E2E / 2 manual); `tests/test_pricing_rules.py` with 18 tests next
  to the existing suite; the 5000 ₽ boundary left failing and reported as a product
  defect; API/E2E cases `not run` because the repo has no endpoint or UI. Contract 70/71:
  three assumptions (A1, A2, A7) have no inline marker in the annotated spec — the same
  minor deviation as in the 2026-10-27 Stage 1 run. **$2.13**, token breakdown in
  [Cost of one run](#cost-of-one-run).
- **`stage3-greenfield-no-tests-ru`** — deterministic graders 10/10: the stack was
  detected as "no test infrastructure", pytest chosen, `[tool.pytest.ini_options]` added
  to `pyproject.toml`, `tests/unit/` and `tests/api/` created with a header naming the
  task, no JS tooling. The LLM criterion fails on (d): the summary does not mention CI,
  and contract checks fail 3/60 — the final `autotest-summary.md` has no Stack Profile /
  Mapping / Commands sections. Cause: `autotest-builder` was denied `python -m pytest`
  (see above), so the main thread ran the tests itself and **rewrote the summary in its
  own format**. Environment-induced, but a real gap: nothing stops the orchestrator from
  doing Stage 3's job when the agent is blocked. $0.30.

**Re-run after the fix** — [`eval-results/2026-11-11-local-rerun`](../eval-results/2026-11-11-local-rerun),
same environment and the same kind of permission denials, after `run-qa-pipeline` got
Core Principle 8 ("the orchestrator never does a stage's work") and `autotest-builder`
got "retry a denied command as a plain single command; if still denied, write the full
summary with `not run` + the exact command" — plus three new graders on who did the work
(see above):

- **`stage3-greenfield-no-tests-ru`** — deterministic graders 13/13 (incl. the three new
  ones), LLM criteria met, contract **60/60** (was 57/60). `autotest-builder` retried the
  denied command, ran pytest itself, and wrote a full summary with Stack Profile
  ("не обнаружен" for all three levels, pytest chosen and why, "CI-конфигурации нет"),
  Mapping and the command with its exit code; the main thread wrote nothing. $0.31.
- **`pipeline-e2e-cart-pricing-ru`** — deterministic graders 17/17, contract **69/69**;
  the orchestrator no longer re-ran the suite (the reviewer's re-run sample did). A second
  cost sample: **$1.64**, 10.3 min — with 21 cases instead of 41, the clearest illustration
  that one run is one sample. New observation: `autotest-builder` marked the defect-finding
  test `xfail(strict=True)` to keep the suite green; the reviewer reported it as Major R-1
  and put "xfail or red" to the human as a Disputed item — the Stage 4 safety net working,
  but against the agent's own "a failing test that found a bug stays failing".

**Re-run after the xfail rule** — [`eval-results/2026-11-11-local-rerun2`](../eval-results/2026-11-11-local-rerun2).
`autotest-builder`, `unit-testing`, `ai-test-generation` and the artifact contract now say
a test that found a suspected product defect stays red — no `xfail` / `test.fail` /
`test.fixme` / `it.failing` — and `qa-doc-review` treats such a marker as a Major finding,
not a Disputed item; the new `defect-test-not-silenced` grader checks it:

- **`pipeline-e2e-cart-pricing-ru`** — deterministic graders 18/18; the boundary test left
  red ("остаётся красным, без `xfail`"), and the reviewer framed the human's choice as
  "fix the code / change the spec / quarantine" in the defect entry, quoting the contract.
  Contract 70/71 — the recurring Stage 1 gap again (A1, A2, A8, A9 without inline markers).
  Third cost sample: **$1.73**, 9.4 min, 20 REQs, 20 cases.
- **`stage3-autotests-python-ru`** (the existing-suite case, as an extra sample) — all
  graders pass, contract 60/60; the Mapping row says "тест оставлен красным, без
  xfail/skip", and the API case is skipped with `skipif` for the missing `CART_API_URL`,
  i.e. `not run`. $0.29.

The checker change in this release (`find_section` reads the non-empty one of two
matching headings — the e2e summary had an empty `## Соответствие кейсов и тестов` right
above `## Mapping`) moved that run from 69/71 to 70/71 and no earlier recorded number.
<!-- EVAL-DETAILS:END -->

### Cost of one run

`tools/measure_run_cost.py` attributes every API call of a run to the agent that made
it, from the session transcripts Claude Code writes (`<session>.jsonl` for the main
thread, `<session>/subagents/agent-*.jsonl` + `.meta.json` for each agent; a nested agent
is billed to the stage that started it). The stream-json trace alone is not enough: its
per-message `output_tokens` are the values at the start of streaming. Prices are list
prices; the harness's own total is printed next to the computed one, and tokens Claude
Code reports for the session that no transcript holds (status summaries) are shown as a
separate row so the two totals match exactly. `collect_eval_run.py` stores the per-call
counts (no prompt text, ~16 KB) as `usage-ledger.json`, and CI re-derives every recorded
cost from it.

```bash
python tools/measure_run_cost.py --session <kept-dir>/config/projects/<slug> --trace <kept-dir>/out/trace.jsonl
python tools/measure_run_cost.py --ledger eval-results/2026-11-11-local/pipeline-e2e-cart-pricing-ru/usage-ledger.json
```

**One full pass over a spec** — `pipeline-e2e-cart-pricing-ru`, Claude Sonnet 5.5,
three runs on 2026-11-11 (before and after the fixes above). Run 1 in full:

| Who | API calls | Cache write | Cache read | Output | All input | Cost |
|---|---:|---:|---:|---:|---:|---:|
| Orchestrator (main thread) | 26 | 55.3k | 1,303.0k | 15.3k | 1,358.3k | $0.50 |
| Stage 1 — spec-analyst | 3 | 32.1k | 39.9k | 10.4k | 71.9k | $0.19 |
| Stage 2 — qa-doc-writer | 6 | 82.6k | 245.7k | 39.5k | 328.3k | $0.63 |
| Stage 3 — autotest-builder | 8 | 54.5k | 272.1k | 10.1k | 326.7k | $0.26 |
| Stage 4 — qa-doc-reviewer | 13 | 90.9k | 636.6k | 25.2k | 727.5k | $0.54 |
| Claude Code service calls | 1 | 0.4k | 45.0k | 0.0k | 45.3k | $0.01 |
| **Total** | **57** | **315.7k** | **2,542.3k** | **100.5k** | **2,858.1k** | **$2.13** |

All three runs:

| | Run 1 | Run 2 | Run 3 |
|---|---:|---:|---:|
| What it produced | 19 REQs, 41 cases | 19 REQs, 21 cases | 20 REQs, 20 cases |
| Tokens (input + output) | 2.96M (2.86M + 100k) | 1.96M (1.89M + 75k) | 1.76M (1.68M + 82k) |
| Orchestrator / Stage 1 / 2 / 3 / 4 | $0.50 / 0.19 / 0.63 / 0.26 / 0.54 | $0.44 / 0.22 / 0.43 / 0.20 / 0.35 | $0.47 / 0.20 / 0.45 / 0.19 / 0.41 |
| **Total** | **$2.13** | **$1.64** | **$1.73** |
| Wall time | 13.1 min | 10.3 min | 9.4 min |
| Input read from cache | 89% | 86% | 84% |

How to read it:

- **≈1.8–3M tokens, $1.64–2.13 (median $1.73) and 9–13 minutes per pass** for a
  one-page spec that becomes 19–20 requirements — about $0.09–0.11 per requirement. The
  spread comes mostly from how many cases Stage 2 wrote (41 vs 20–21): cost grows with
  requirements and cases, not with the length of the spec text.
- **The bill is output and cache writes, not context.** Output (the documents and code the
  agents write, thinking included) is 46–47% of the cost, cache writes (each file entering
  an agent's context for the first time) 41–45%, cache reads 8–12%. The 1.4–2.5M cached
  tokens — every call resending the system prompt, skills and history — cost $0.14–0.25.
- **The most expensive stages are writing and reviewing**: Stage 2 (writes all cases) and
  Stage 4 (re-reads the spec, the plan, every case file and the tests, re-runs a sample)
  — 48–55% together. The orchestrator's ~25% is mostly cache reads: it carries the whole
  run in one context.
- **On Claude Opus 5.5** the same tokens would cost exactly 2× ($3.3–4.3, median $3.5): its prices are
  double Sonnet 5.5's. A different model also writes a different number of tokens, so
  measure before relying on that.
- **Caveats.** Three runs, and the plugin changed between them (the fixes above), so read
  the range, not a trend; use `--runs 3` or more on one version before comparing versions.
  All runs were local (base context ~25.6k tokens vs ~19.5k under the harness, because
  of Claude Code's built-in skills) and had Bash denials; in run 1 they also made the
  orchestrator re-run pytest itself.

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
demand with an `ANTHROPIC_API_KEY` secret, then records every case with
`collect_eval_run.py` (artifacts, contract scores, per-stage token cost) and uploads it.

**On Windows** the harness refuses cases that need Bash: it cannot confine shell tools
there. Run such a case headlessly instead — scaffold a workspace, run the prompt with the
plugin, record it — as described in the 2026-11-11 run above:

```bash
mkdir ws && (cd ws && bash ../evals/pipeline-e2e-cart-pricing-ru/scaffold.sh)
cd ws && claude -p "$(python -c "import sys;print(open(sys.argv[1],encoding='utf-8').read().split('---',2)[2].strip())" ../evals/pipeline-e2e-cart-pricing-ru/prompt.md)" \
  --plugin-dir .. --add-dir .. --setting-sources project --strict-mcp-config \
  --tools Read Glob Grep Skill Agent Write Edit Bash TaskCreate TaskUpdate TaskList TaskGet \
  --permission-mode acceptEdits --allowedTools "Bash(pytest *)" "Bash(python *)" "Bash(cd *)" "Bash(ls *)" \
  --model claude-sonnet-5-5 --output-format stream-json --verbose > ../trace.jsonl
cd .. && python tools/collect_eval_run.py --run-id $(date +%F)-local --case pipeline-e2e-cart-pricing-ru \
  --workspace ws --trace trace.jsonl --session ~/.claude/projects/<ws-slug>
```

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
