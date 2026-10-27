# Getting started

## Requirements

- [Claude Code](https://code.claude.com) (CLI, desktop, or IDE extension).
- A target repository to run the pipeline in — the place where `docs/qa/` and the
  autotests will be written. For Stage 3 to actually run tests, the repo's own test
  tooling must work in your environment (e.g. `npm test`, `pytest`).

## Install

From inside Claude Code:

```text
/plugin marketplace add leonovvc/qa-agentic-pipeline
/plugin install qa-agentic-pipeline@leonovvc-qa
```

Or try it for one session without installing, from a local clone:

```bash
git clone https://github.com/leonovvc/qa-agentic-pipeline.git
cd /path/to/your/project
claude --plugin-dir /path/to/qa-agentic-pipeline
```

Check that it loaded: `/agents` lists `spec-analyst`, `qa-doc-writer`,
`autotest-builder`, `qa-doc-reviewer`; skills appear as `qa-agentic-pipeline:<name>`.

## Optional: describe your project once

Ask Claude:

```text
Set up the QA project context for this repo.
```

`qa-project-context` detects the stack from config files, asks only what it can't detect,
and writes `.agents/qa-project-context.md`. The section the pipeline reads most is:

```markdown
## QA Pipeline
- **Output language:** ru
- **Docs location:** docs/qa/
- **Test-case system:** none
- **Definition of Ready:** docs/process/definition-of-ready.md
- **E2E budget:** max 20% of automated cases; ~40 s per E2E test in CI
- **Security lens:** auto
- **Spec owners:** product analyst (Track B questions)
```

Without this file the pipeline still runs on defaults and says so in the final report.

## Run the pipeline

Create and check out a branch first — the pipeline writes to whatever branch is checked
out and never commits. Then give it the spec in any form:

```text
Run the QA pipeline on this spec: https://wiki.example.com/checkout/promo-codes
```

```text
Прогони QA-пайплайн по ТЗ из файла specs/password-reset.pdf. Документацию — на русском.
```

```text
Run the QA pipeline on the text below. I'll be away — don't wait for me.
<paste the spec>
```

What happens next:

1. Stage 1 may ask you one or two **Track A** questions right away — things you can
   decide (scope of this pass, which of two readings to build on). If you're away, it
   logs an assumption and continues.
2. Stages 2–4 run without stopping.
3. You get the **Human Checkpoint**: what was assumed, what the reviewer disputes, the
   Track B questions for the spec owner, and where every file is.

## Resume after an interruption

If the session ends mid-run (connection lost, usage limit reached, window closed), start a
new session in the same repository and say:

```text
Resume the QA pipeline.
```
or
```text
Продолжи QA-пайплайн.
```

The orchestrator reads `docs/qa/pipeline-state/`, reports which stages are done, restarts
the interrupted stage from scratch, and continues. `docs/qa/pipeline-state/board.md`
shows all tasks at a glance.

## Use one stage on its own

```text
Analyse specs/promo.md for gaps and contradictions — no test plan yet.
Write test cases from docs/qa/promo/spec-gap-report.md.
Automate the cases in docs/qa/promo/test-cases-api.md.
Review the test plan in docs/qa/promo/.
Check this spec for security gaps.
```

## Where the output goes

```text
docs/qa/
├── pipeline-state/
│   ├── checkout-promo-codes-3f9a1c.json   task record
│   └── board.md                           all tasks
└── checkout-promo-codes-3f9a1c/
    ├── spec-source.md         the spec as received
    ├── spec-gap-report.md     requirements, gaps, questions, assumptions, security lens
    ├── spec-annotated.md      the spec with findings marked inline
    ├── test-plan.md           risk table, traceability matrix, pyramid, criteria
    ├── test-cases-unit.md     ┐
    ├── test-cases-api.md      │ only the levels that have cases
    ├── test-cases-e2e.md      │
    ├── test-cases-manual.md   ┘
    ├── autotest-summary.md    case → test mapping, commands, real results
    ├── qa-review-report.md    independent review
    └── checkpoint.md          what needs your decision
```

Autotests go into the repository's existing test directories.

## Check the output mechanically

From a clone of this repository:

```bash
pip install pyyaml
python tools/check_artifacts.py /path/to/project/docs/qa/<task-id> \
  --state /path/to/project/docs/qa/pipeline-state/<task-id>.json
```

It verifies the artifact contract: every requirement traced, IDs consistent between the
report and the annotated spec, all eight case fields present, levels consistent, the
pyramid not inverted, every automatable case mapped to a test with a real status, every
review finding rated.
