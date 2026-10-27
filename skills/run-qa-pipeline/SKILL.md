---
name: run-qa-pipeline
description: >-
  Run the full 4-stage agentic QA cycle end-to-end from a single spec input (URL,
  pasted text, or PDF) to a consolidated human decision package: spec analysis → QA
  documentation (test plan + test cases) → autotests → independent review, with one
  final human checkpoint for anything disputed. Orchestrates spec-analyst,
  qa-doc-writer, autotest-builder, and qa-doc-reviewer in sequence, persisting
  progress to a Jira-style task file after every stage so a dropped connection, an
  exhausted daily limit, or a closed session resumes from the first unfinished stage
  instead of restarting. Use when: "run the QA pipeline," "process this spec through
  QA," "resume the QA pipeline," "продолжи пайплайн," "прогони QA-пайплайн," or any
  request that continues work on a task in docs/qa/pipeline-state/. Not for: running a
  single stage in isolation — invoke that stage's agent directly.
  Related: qa-pipeline-task-state, qa-output-standards, spec-gap-analysis,
  qa-doc-review, qa-project-context.
license: MIT
metadata:
  author: qa-agentic-pipeline
  version: "2.0"
  category: foundation
---

<objective>
Running four QA agents manually, one at a time, with the person re-pasting outputs between them, is exactly the coordination tax this plugin exists to remove. This skill is the entry point: give it a spec in whatever form it exists, and it drives all four stages autonomously, logging every assumption along the way, and stops for a human exactly once — at the end, with everything genuinely disputed collected in one place.
</objective>

## Discovery Questions

Ask only what's missing; don't block on defaults that are safe to assume.

1. **Does a task already exist for this input?** Compute the task ID (per `qa-pipeline-task-state`) and check `docs/qa/pipeline-state/<task-id>.json` *before* asking anything else. If a non-`DONE` task exists, this is a resume, not a fresh start — skip straight to **Resume Procedure** below and only ask what that procedure needs.
2. **What is the input, and in what form?** A URL, pasted spec text, or a PDF file/attachment. If none is provided, ask for it — this is the one input the pipeline cannot proceed without on a fresh start.
3. **Which repository are the autotests targeting, and which branch?** If this session's working directory already looks like the target repo (per `stack-detection-for-autotests`), confirm rather than ask. If genuinely ambiguous, ask once at the start rather than partway through Stage 3. The pipeline writes to whatever branch is already checked out there — it never creates or switches branches, and Stage 3 never commits, pushes, or opens a PR on its own (see `autotest-builder`); that stays the human's call.
4. **Does `.agents/qa-project-context.md` already exist in the target repo?** If not, proceed with the pipeline's own defaults (docs in `docs/qa/`, no test-case system, E2E budget 20%, security lens `auto`) and note in the final report that a `qa-project-context` setup would sharpen future runs — do not block the pipeline on creating it first.
5. **Output language — English or Russian?** Resolve it per `qa-output-standards` §1 (explicit request → project context → existing task → ask once now → language of the spec). It is recorded in the task file and passed to every stage; it never changes mid-run.

## Core Principles

1. **The chain runs autonomously end to end.** Once the input is in hand, Stages 1-4 proceed without stopping for approval between them — that division of labor is what the four agents are for.
2. **Every assumption made to keep moving is logged, not silently absorbed.** `spec-gap-analysis`'s Assumptions Made section, any scope call `qa-doc-writer` makes, any stack default `autotest-builder` falls back to — all of it surfaces in the final report, even when no agent flagged it as disputed.
3. **The orchestrator never resolves a Disputed item itself.** `qa-doc-reviewer`'s Disputed section is passed through to the human checkpoint verbatim — this skill has no authority to pick a side.
4. **One genuine exception to "no mid-chain stop": a spec too broken to proceed at all.** If `spec-analyst` cannot derive any acceptance criteria from the input (empty, unreadable, or entirely off-topic), stop immediately and say so — this is not a judgment call to defer, there is nothing for Stage 2 to build on. Record this as `BLOCKED` in the task file (per `qa-pipeline-task-state`), not `FAILED` — it's a content question, not a technical error.
5. **The pipeline is not "done" until a human has seen the consolidated checkpoint.** Even a fully clean run (no Blocking findings, no Disputed items) still produces and presents the checkpoint report — silence from the reviewer is not the same as skipping the human step.
6. **Progress lives on disk, not in this session's memory.** Every stage transition is written to the task file (`qa-pipeline-task-state`) before and after that stage runs — if this session ends mid-stage for any reason (dropped connection, exhausted daily limit, closed window), the next session resumes from the task file, not from what this conversation remembers.
7. **A resumed stage restarts whole; a completed stage never reruns.** If the task file shows a stage `in_progress` with no `completed_at`, that stage is redone from scratch on resume — its partial work, if any, is not trusted. Stages already `done` are never rerun; their output files are read directly as input to the next stage.

## Pipeline Stages

What each stage writes, the ID scheme (`REQ-<n>`, `Q<n>`, `A<n>`, `TC-<LVL>-<nnn>`, `R-<n>`), and the file layout under `docs/qa/<task-id>/` are defined once in `references/artifact-contract.md` — read it before the first stage, and hand each agent the paths, not paraphrases.

| Stage | Agent | Skill(s) used | Produces |
|---|---|---|---|
| 1 | `spec-analyst` | `spec-gap-analysis`, `security-testing` (Lens Mode), `risk-based-testing` (Track B order) | `spec-source.md` + `spec-gap-report.md` (with Requirements Inventory and Security Lens) + `spec-annotated.md` |
| 2 | `qa-doc-writer` | `test-planning`, `risk-based-testing`, `test-design-techniques`, `test-pyramid-strategy`, `test-case-management`, `security-testing` (Lens Mode), `qa-output-standards` | `test-plan.md` plus cases split by pyramid level — local files (`test-cases-unit.md` / `test-cases-api.md` / `test-cases-e2e.md` / `test-cases-manual.md`) or, when a test-case system with access is given, entries filed into its existing suite/section hierarchy |
| 3 | `autotest-builder` | `stack-detection-for-autotests`, `ai-test-generation`, `unit-testing`, `api-testing`, `playwright-automation`, `qa-output-standards` | autotest files in the target repo (on whatever branch is already checked out — no commit/push/PR), `autotest-summary.md` |
| 4 | `qa-doc-reviewer` | `qa-doc-review`, `ai-qa-review`, `qa-output-standards` | `qa-review-report.md` |

Invoke each stage's agent with the prior stage's full output as input, not a paraphrase of it — `qa-doc-writer` needs the actual `spec-gap-report.md`, not a summary of its summary.

## Task State & Resume

Every run of this pipeline is backed by a task file — see `qa-pipeline-task-state` for the full schema, status set, and transition rules. This skill only covers how the orchestration loop uses it; read that skill before implementing either procedure below.

### Fresh-Start Procedure

1. Compute the task ID from the input and confirm no existing task file matches (if one does, switch to **Resume Procedure** instead).
2. Resolve the output language (Discovery Question 5) and create the task file (`TODO`, all stages `pending`, `output_language`, `docs_dir`).
3. Proceed to **Orchestration Procedure** at Stage 1.

### Resume Procedure

1. Load the existing task file. Report its status and which stage is next in one line before doing anything else (e.g., "Задача checkout-discount-code-a1b2c3: этапы 1-2 завершены, этап 3 был прерван — перезапускаю его.").
2. If task `status` is `BLOCKED`: this is a content question, not a technical retry — surface the stored blocker and wait for the human's answer before touching any stage.
3. If task `status` is `IN_REVIEW`: the pipeline already finished; re-present the stored Human Checkpoint Report rather than rerunning anything.
4. Otherwise, find the first stage that is not `done`. If that stage is `in_progress` (was interrupted) or `failed`, restart it whole. If it's `pending`, start it normally. Stages already `done` are not rerun — read their `output` files directly as input to the next stage.
5. Continue at that stage in **Orchestration Procedure**.

## Orchestration Procedure

Before each stage: write that stage's status to `in_progress` in the task file (`qa-pipeline-task-state`). After each stage: write `done` + the output path, or `failed` + the reason, before moving on. This bracketing is what makes the pipeline resumable — do it around every stage, not just at the end.

1. **Resolve the input.** URL → fetch. PDF → extract. Pasted text → use directly. Hand off to `spec-analyst` together with the task ID, `docs_dir`, and output language.
2. **Stage 1.** Run `spec-analyst`. If Blocking Gaps make test design impossible for the *entire* spec (not just one section), set the task to `BLOCKED` and stop — this is the sole mid-chain exception (Core Principle 4). Otherwise continue with whatever is testable, carrying forward the Assumptions Made list into the task file's `assumptions_log`.
3. **Stage 2.** Run `qa-doc-writer` with the spec + Stage 1's report as input.
4. **Stage 3.** Run `autotest-builder` with Stage 2's test plan/cases as input, targeting the confirmed repository.
5. **Stage 4.** Run `qa-doc-reviewer` with the original spec, Stage 1's report, Stage 2's output, and Stage 3's output. On completion, set task `status` to `IN_REVIEW` and populate `disputed_items` from its report.
6. **Assemble the Human Checkpoint Report** (below) from all four stages' outputs, save it as `docs/qa/<task-id>/checkpoint.md`, and present it. The pipeline's work is complete at this point; downstream actions (committing, opening a PR, resolving Disputed items) wait for the human's response. When the human resolves everything, set task `status` to `DONE`; if they ask for one stage to be redone, set only that stage back to `pending` and the task to `IN_PROGRESS`.

## Human Checkpoint Report

```markdown
# QA Pipeline — Human Checkpoint

## Task
<task_id> · status: IN_REVIEW · board: docs/qa/pipeline-state/board.md

## Input
<spec source, one line>

## Stage 1 — Spec Analysis
Testability score: <N/5>. Requirements: <M> (REQ-1…REQ-M). Blocking gaps: <count>.
Track B questions for the spec owner: <count> (docs/qa/<task-id>/spec-gap-report.md).
Security lens: <applied — N findings | not applicable>.

## Stage 2 — QA Documentation
Test plan: <N test cases covering K of M requirements>; blocked: <REQ IDs + Q>.
Pyramid split: <unit / API / E2E / manual counts>. Priorities: <P0 n · P1 n · P2 n · P3 n>.

## Stage 3 — Autotests
<N files created/extended, mapped to which pyramid levels>. Anything not automated
and why (manual/exploratory cases stay manual — that's expected, not a gap).

## Stage 4 — Review Summary
Traceability: <K of M requirements covered>. Blocking: <n> · Major: <n> · Minor: <n>

## Everything Assumed Along the Way
<consolidated list from Stage 1's Assumptions Made plus any scope calls Stages 2-3
made — even if none were flagged as Disputed>

## Disputed — Needs Your Decision
<Stage 4's Disputed section, verbatim; "None" if genuinely none>

## Next Step
Awaiting your review of the Disputed items above (if any) before this cycle is
considered final.
```

## Anti-Patterns

- **Skipping straight to Stage 3 on a spec Stage 1 marked not-testable.** Autotests built on unclarified requirements automate the wrong thing convincingly.
- **Letting Stage 4's Disputed items get absorbed into "Minor" to shrink the report.** Defeats the one human checkpoint this pipeline has.
- **Presenting the checkpoint as a summary of what was DONE rather than what needs a DECISION.** The report's job is to make the Disputed section impossible to miss, not to bury it under a wall of "everything looks great."
- **Treating the checkpoint as optional when the run was clean.** A clean run still gets presented — "no disputes" is information the human should see stated, not inferred from silence.
- **Starting a fresh task without checking for an existing one first.** Produces a duplicate task file for the same spec and throws away the resumability this pipeline exists to provide.
- **Resuming a stage mid-way instead of restarting it whole.** There's no reliable way to know how much of an interrupted stage actually finished — per `qa-pipeline-task-state`, always redo it from the start.

## Verification

Confirm all four stages' artifacts exist in `docs/qa/<task-id>/` before assembling the checkpoint: `spec-source.md` + `spec-gap-report.md` + `spec-annotated.md`, `test-plan.md` + the per-level case files (or the noted test-case-system location), the autotest files listed in `autotest-summary.md`, and `qa-review-report.md`. A missing artifact means a stage was skipped, not that it produced nothing. Cross-check each artifact's path against the task file's `stages[].output` (a stage with more than one artifact stores an array of paths, not a single string) — they must match.

## Done When

- All four stage artifacts exist and were produced from the actual prior-stage output, not a paraphrase.
- The task file reflects the true state of every stage (`done` stages have `completed_at` and an `output` path; nothing is silently ahead of or behind what actually ran).
- The Human Checkpoint Report is assembled and presented, with Disputed items (if any) unmistakable.
- Every assumption made anywhere in the chain appears somewhere in the checkpoint report.
- Every artifact is in the task's output language and follows `references/artifact-contract.md` (the plugin repository's `tools/check_artifacts.py` validates this mechanically).

## Related Skills

- **qa-pipeline-task-state** — the persistence layer this orchestrator reads and writes around every stage; read it first when implementing either the Fresh-Start or Resume procedure.
- **spec-gap-analysis**, **test-planning** + **test-design-techniques** + **test-pyramid-strategy**, **stack-detection-for-autotests**, **qa-doc-review** — the four stages this orchestrates.
- **qa-output-standards** — the output-language rule and the readability bar every stage applies.
- **qa-project-context** — sharpens every stage when filled in; not required to run the pipeline.

## Reference Files (in `references/`)

- **artifact-contract.md** — file layout, ID scheme, required sections and fields of every artifact, and the invariants the tooling checks.
