# QA Pipeline — Human Checkpoint

## Task
next-gen-loyalty-experience-d4a1cd · status: BLOCKED · board: docs/qa/pipeline-state/board.md

## Input
specs/loyalty.md (pasted/local text, 3 paragraphs)

## Stage 1 — Spec Analysis
Testability score: 1/5. Requirements: 0. Blocking gaps: 5 (Q1–Q5).
Track B questions for the spec owner: 9 (Q7–Q15), see docs/qa/next-gen-loyalty-experience-d4a1cd/spec-gap-report.md.
Security lens: domain-level findings only (Q7 balances/redemption, Q8 access and personal data); the rest cannot be assessed.

## Stage 2 — QA Documentation
Not run. The spec has no requirement to derive test cases from; any case would be invented.

## Stage 3 — Autotests
Not run (depends on Stage 2).

## Stage 4 — Review Summary
Not run (depends on Stages 2–3).

## Everything Assumed Along the Way
- A1 (procedural): stopping after Stage 1 is acceptable because you were away.
- A2: output language is English (your request).
- A3: generic security checklist used because the spec states nothing.
No requirement-level assumptions were made.

## Disputed — Needs Your Decision
None from Stage 4 (not reached). One decision for you: the pipeline stopped at Stage 1 as a whole-spec blocker (Core Principle 4). Say so if you would rather have it continue on invented assumptions, but that is not recommended.

## Next Step
Send the Track B questions (Q7–Q15) to the spec owner. Q15 (is there a fuller spec?) is the fastest unblock. When a testable spec exists, re-run the pipeline: the task is BLOCKED, so Stage 1 restarts.
