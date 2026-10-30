# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/).

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
