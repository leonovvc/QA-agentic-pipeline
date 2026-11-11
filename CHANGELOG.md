# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/).

## [1.1.0] — 2026-11-11

### Added
- **Token cost per stage** — `tools/measure_run_cost.py` attributes every API call of a
  run to the orchestrator or the stage agent that made it (from the session transcripts;
  nested agents billed to their stage), prices it, and checks the total against Claude
  Code's own. `collect_eval_run.py` records a small `usage-ledger.json` and a `cost`
  section in `scores.json`; `verify_recorded_runs.py` re-derives recorded costs in CI.
- Eval case `pipeline-e2e-cart-pricing-ru` — the whole pipeline from one request on a RU
  spec and a pytest repo with a planted bug; the run the cost is measured on.
- Eval case `stage3-greenfield-no-tests-ru` — Stage 3 on a repo with no tests at all:
  stack detection must say so, pick one framework, scaffold minimally.
- Recorded local runs `eval-results/2026-11-11-local`, `…-local-rerun`, `…-local-rerun2`:
  one full pass costs ≈1.8–3M tokens, **$1.64–2.13 (median $1.73)** on Claude Sonnet 5.5,
  9–13 min (run 1: orchestrator $0.50, stages $0.19 / $0.63 / $0.26 / $0.54); details in
  `docs/evals.md#cost-of-one-run`.
- Three graders in every case that reaches Stage 3 (`main-thread-does-not-*`): a
  main-thread trace line must never write `autotest-summary.md` or a test file, or run the
  suite.
- `docs/faq.ru.md` — answers to common questions about how the agents decide (existing
  autotests, pyramid level, lost requirements, resume, review independence, cost).
- `collect_eval_run.py --case/--workspace/--trace/--session` records a headless run made
  outside the harness (needed on Windows, where the harness can't sandbox Bash).
- The `Behavioral evals` workflow records each case with `collect_eval_run.py` and uploads
  artifacts, scores and cost.

### Fixed
- **The main thread took over a blocked Stage 3** (found by the greenfield eval): after
  `autotest-builder`'s pytest command was denied, the routing conversation ran the tests
  and rewrote `autotest-summary.md` without Stack Profile or Mapping (contract 57/60).
  `run-qa-pipeline` Core Principle 8: the orchestrator writes only the task file,
  `board.md` and `checkpoint.md`, never a stage's artifacts or tests, and doesn't run the
  suite; an agent's "could not run" is the stage's result. `autotest-builder`: retry a
  denied command once as a plain single command, else write the full summary with `not
  run`, the exact command and "denied"; its description tells the main conversation to
  relay that result as-is. Re-run: 60/60, main thread wrote nothing; the e2e re-run 69/69.
- `measure_run_cost.py`: wall time from transcript timestamps (a session resumed by
  background agents has one `result` per turn, each with only that turn's duration).
- `check_artifacts.py`: a section is read from the non-empty one of two matching headings
  (a report with both `## Соответствие кейсов и тестов` and `## Mapping`).
- `collect_eval_run.py` no longer crashes on system events whose `message` is a string.
- All tools and tests read and write files as UTF-8 explicitly, so they run on Windows
  (cp1251 default) without `-X utf8`.

- **A defect-finding test silenced with `xfail`** (found by the e2e re-run):
  `autotest-builder` marked the 5000 ₽ boundary test `xfail(strict=True)` to keep the
  suite green. The rule "a test that found a suspected product defect stays red — no
  `xfail` / `test.fail` / `test.fixme` / `it.failing`; quarantine is the human's call" is
  now in `autotest-builder`, the artifact contract, `unit-testing`, `ai-test-generation`
  and a note in `playwright-automation`; `qa-doc-review` reports such a marker as Major,
  not Disputed. New grader `defect-test-not-silenced` in every Stage 3 case (a plain
  `skip` for a missing prerequisite stays allowed). The next e2e run and a Stage 3 run
  both left the test red.

### Known gap
- Stage 1 often logs assumptions without an inline marker in `spec-annotated.md` (3 of
  the last 4 runs that include Stage 1); the contract checker reports it, no grader yet.

## [1.0.1] — 2026-10-30

### Added
- `docs/methodology.md` / `docs/methodology.ru.md`: risk-based P0–P3 priorities, boundary
  value analysis, decision tables, state transitions, and how the planted-defect evals
  work — illustrated with artifacts from the recorded run.
- Recorded Stage 3 re-run (`eval-results/2026-10-30-stage3-rerun`): 1.00, up from 0.50.

### Fixed
- README eval table: the recorded Stage 1 promo run had 23 requirements and 28 questions
  (25 and 22 were from an earlier trial run).

## [1.0.0] — 2026-10-27

First public release.

### Added
- **Artifact contract** (`skills/run-qa-pipeline/references/artifact-contract.md`): one
  definition of every stage's files, IDs (`REQ`, `Q`, `A`, `TC-<LVL>-<nnn>`, `R`), required
  sections, and case fields; every skill and agent links to it.
- **Requirements Inventory** in Stage 1 — numbered `REQ-<n>` rows that every later stage
  traces to, so coverage is a number, not an impression.
- **`qa-output-standards`** skill — output language chosen once per run (English or
  Russian), identifiers always in English, and a readability bar for test cases and test
  code.
- **Security lens** (`security-testing` Lens Mode) — OWASP Top 10 (2025) questions asked
  of the spec in Stage 1, security negative cases in Stage 2, checked in Stage 4.
- **Risk Assessment** in every test plan (`risk-based-testing` Pipeline Mode) driving
  P0–P3 priorities and required depth.
- Per-task docs directory `docs/qa/<task-id>/` (previously all tasks shared `docs/qa/`),
  `spec-source.md` snapshot, and `checkpoint.md`.
- Agents preload their core skills (`skills:` frontmatter) and read the contract via
  `${CLAUDE_PLUGIN_ROOT}`; the reviewer can re-run a sample of reported-passing tests.
- `tools/validate_plugin.py` — static validation (frontmatter, cross-references, dangling
  links to skills not shipped, reference files, contract drift, attribution).
- `tools/check_artifacts.py` — validates a pipeline run's output against the contract
  (English and Russian).
- `tools/score_spec_analysis.py` — recall of planted spec defects against ground truth.
- Behavioral eval suite for `claude plugin eval` (8 cases across all stages,
  orchestration, and routing) with recorded results.
- CI: static validation, pytest, golden fixtures, `claude plugin validate`; a manual
  workflow for the behavioral evals.
- Marketplace manifest, icon, documentation (`docs/`), Russian README.

### Changed
- The ten skills adapted from petrkindlmann/qa-skills were reworked into stage
  procedures (see `THIRD_PARTY_NOTICES.md`); ~20 references to upstream skills that this
  plugin does not ship were removed or replaced.
- `Q<n>` numbering is one global sequence across blocking gaps, contradictions, and open
  questions.
- Track B questions are ordered by the risk of the requirement they block.

## [0.3.0] — 2026-10

Internal version: four agents, the orchestrator with Jira-style task state, original
Stage 1/2/4 skills, and ten skills vendored verbatim from petrkindlmann/qa-skills.
