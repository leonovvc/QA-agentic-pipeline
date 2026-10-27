---
name: qa-pipeline-task-state
description: >-
  Persist the QA pipeline's progress to disk as a Jira-style task record — task ID,
  overall status, per-stage status, timestamps, and history — so a lost connection,
  an exhausted daily limit, or a closed session never forces the 4-stage pipeline to
  restart from scratch. A new session resumes from the first unfinished stage by
  reading this file, not from conversation memory. Use when: "save pipeline
  progress," "resume the QA pipeline," "продолжи пайплайн," "show the pipeline
  board," "what's the status of this QA task," or automatically, as the bookkeeping
  layer run-qa-pipeline calls around every stage. Not for: deciding WHAT each stage
  does — use spec-gap-analysis, test-planning, etc. Not for: syncing with an actual
  Jira/Linear instance — this is a local file-based imitation of that workflow, not
  an integration.
  Related: run-qa-pipeline, spec-gap-analysis, qa-doc-review.
license: MIT
metadata:
  author: qa-agentic-pipeline
  version: "2.0"
  category: foundation
---

<objective>
A pipeline that lives only in a session's conversation memory loses everything the moment that session ends — a dropped connection, an exhausted daily limit, or someone closing the tab mid-run. This skill moves the pipeline's progress to a file in the target repository, structured like a Jira ticket (status, sub-task status per stage, timestamps, history), so the next session — in five minutes or next week — resumes exactly where the last one stopped instead of redoing finished, expensive work.
</objective>

## Discovery Questions

1. **Does a task already exist for this input?** Derive the task ID from the spec (see **Task ID**) and check `docs/qa/pipeline-state/<task-id>.json` before creating a new one — a second run against the same spec must resume, not duplicate.
2. **Is the caller creating a task, updating one, or just reading the board?** Each is a distinct, small operation — don't reread or rewrite more of the file than the operation needs.

## Core Principles

1. **The file on disk is the source of truth, not the conversation.** Any agent or orchestrator step that needs to know "what's done" reads the task file — it never infers progress from what it remembers saying earlier in the session.
2. **A stage interrupted mid-run is restarted whole, not resumed mid-stage.** There is no reliable way to know how much of an in-progress stage actually completed before an interruption, so on detection it is simply re-run from its own start. Stages already marked `done` are never rerun — their output files are read as-is.
3. **Every status change is also a history entry.** The `history` array is append-only and is what makes the task file behave like a Jira activity feed, not just a snapshot — never overwrite it, only append.
4. **`BLOCKED` and `FAILED` are different problems with different fixes.** `BLOCKED` means a human needs to answer something about the spec's content (spec-analyst found a whole-spec blocker). `FAILED` means a stage errored out technically (tool/environment failure) and needs a retry, not a content decision. Never conflate the two — the next action for each is different.
5. **The board is a view, not a second source of truth.** `board.md` is regenerated from the task JSON files every time any of them changes; it is never hand-edited or updated independently of them.

## Task ID

Slugify the spec's title or feature name, append a short hash (first 6 hex chars of the SHA-256 of the source URL, the pasted text, or the file bytes — e.g. `printf %s "$URL" | sha256sum | cut -c1-6`) to keep re-runs against the same spec resolving to the same ID: `<slug>-<hash>`, e.g. `checkout-discount-code-a1b2c3`. If no title is inferable yet (very first pass, before spec-analyst has run), derive a provisional slug from the input source itself (URL path, filename, or first few words of pasted text) and keep it stable for the life of the task.

## File Locations

```
docs/qa/pipeline-state/
├── <task-id>.json     — one file per task, the source of truth
└── board.md           — regenerated summary table across all task files
```

## Task Record Schema

```json
{
  "task_id": "string",
  "title": "string",
  "source": { "type": "url|text|pdf", "value": "string" },
  "target_repo": "string",
  "output_language": "en|ru",
  "docs_dir": "docs/qa/<task-id>",
  "status": "TODO|IN_PROGRESS|BLOCKED|IN_REVIEW|DONE|FAILED",
  "created_at": "ISO 8601",
  "updated_at": "ISO 8601",
  "stages": [
    { "stage": 1, "agent": "spec-analyst",    "status": "pending|in_progress|done|failed|blocked", "started_at": null, "completed_at": null, "output": null },
    { "stage": 2, "agent": "qa-doc-writer",    "status": "pending", "started_at": null, "completed_at": null, "output": null },
    { "stage": 3, "agent": "autotest-builder", "status": "pending", "started_at": null, "completed_at": null, "output": null },
    { "stage": 4, "agent": "qa-doc-reviewer",  "status": "pending", "started_at": null, "completed_at": null, "output": null }
  ],
  "assumptions_log": ["string, ..."],
  "disputed_items": ["string, ..."],
  "history": [
    { "at": "ISO 8601", "event": "task_created" }
  ]
}
```

`output_language` is resolved once at task creation (`qa-output-standards` §1) and never changed for the life of the task, so a resumed run writes in the same language. `docs_dir` is where every stage of this task writes its documents (the artifact contract (`${CLAUDE_PLUGIN_ROOT}/skills/run-qa-pipeline/references/artifact-contract.md`)); one directory per task keeps two features from overwriting each other's reports.

`output` on a stage is the path to that stage's artifact once `status` is `done` (e.g., `docs/qa/checkout-discount-code-a1b2c3/spec-gap-report.md`) — the next stage reads this path directly rather than being handed a paraphrase. A stage that produces more than one artifact (Stage 1's report + annotated spec; Stage 2's plan + per-pyramid-level case files, or a test-case-system location) stores `output` as an array of paths/locations instead of a single string — never collapse multiple artifacts into one path or silently keep only the first.

## Status Reference

**Task-level** (`status`):

| Status | Meaning |
|---|---|
| `TODO` | created, no stage has started |
| `IN_PROGRESS` | a stage is running or ready for its next auto-start |
| `BLOCKED` | a stage found a whole-spec content blocker — needs a human answer about the spec itself |
| `IN_REVIEW` | all 4 stages done, Human Checkpoint assembled, awaiting the human's decision on disputed items |
| `DONE` | human approved / closed the checkpoint |
| `FAILED` | a stage errored out technically — needs a retry, not a content decision |

**Per-stage** (`stages[i].status`): `pending | in_progress | done | failed | blocked`.

## State Transitions

| From | Event | To |
|---|---|---|
| *(none)* | new input received, no existing task ID matches | create `TODO`, stage 1 = `pending` |
| `TODO` | stage 1 starts | `IN_PROGRESS`, stage 1 = `in_progress` |
| `IN_PROGRESS` | stage 1 completes, no whole-spec blocker | stage 1 = `done`, stage 2 = `pending` |
| `IN_PROGRESS` | stage 1 finds a whole-spec blocker | → `BLOCKED`, stage 1 = `blocked` |
| `BLOCKED` | human clarifies the spec | → `IN_PROGRESS`, stage 1 restarts |
| `IN_PROGRESS` (stage N `in_progress`) | session ends without marking stage N `done` | next run detects stage N still `in_progress` → restarts stage N whole; stages 1..N-1 untouched, their outputs reused |
| `IN_PROGRESS` (stage N `done`, N<4) | stage N+1 starts | stage N+1 = `in_progress` |
| `IN_PROGRESS` (stage 4 `done`) | — | → `IN_REVIEW`, Human Checkpoint assembled |
| `IN_REVIEW` | human resolves all disputed items | → `DONE` |
| `IN_REVIEW` | human asks to redo one specific stage | that stage → `pending` (others' `done` untouched) → `IN_PROGRESS` |
| *(any)* | a stage errors out technically | that stage → `failed`, task → `FAILED`; next run retries that stage |

## Procedures

**Create or resume:** compute the task ID from the input; if `docs/qa/pipeline-state/<task-id>.json` exists, load it and report which stage is next (the first stage not `done`) rather than starting over. If it doesn't exist, create it with all stages `pending` and status `TODO`, and append a `task_created` history entry.

**Before starting a stage:** set that stage's `status` to `in_progress` and `started_at` to now; append a `stage_started` history entry; write the file.

**After a stage succeeds:** set `status` to `done`, `completed_at` to now, `output` to the artifact path; append a `stage_completed` history entry; advance the next stage to `pending` if it was still unset; write the file; regenerate `board.md`.

**After a stage fails technically:** set that stage's `status` to `failed`, task `status` to `FAILED`; append a `stage_failed` history entry with the error reason; write the file; regenerate `board.md`.

**On a whole-spec blocker from stage 1:** set stage 1 `status` to `blocked`, task `status` to `BLOCKED`; append a `blocked` history entry; stop the pipeline here and surface it — do not proceed to stage 2.

**On stage 4 completion:** set task `status` to `IN_REVIEW`; assemble the Human Checkpoint (per `run-qa-pipeline`) from the four stage outputs plus `assumptions_log` and `disputed_items`.

**On human resolution:** if everything is resolved, set task `status` to `DONE`. If the human wants a specific stage redone, set that stage back to `pending`, leave earlier `done` stages untouched, and set task `status` to `IN_PROGRESS`.

**board.md regeneration:** on every write to any task file, rebuild `board.md` as a single markdown table across all task files in the directory: `Task ID | Title | Status | Current Stage | Language | Updated`. Never hand-edit this file.

**Timestamps:** take them from the system clock (`date -u +%Y-%m-%dT%H:%M:%SZ`), never estimate them — the history is an audit trail.

## Anti-Patterns

- **Rebuilding pipeline progress from what the assistant remembers saying.** Conversation memory is not the source of truth; always read the task file.
- **Re-running a stage already marked `done` "just to be safe."** Wastes the exact cost this skill exists to avoid; trust the file.
- **Trying to resume an interrupted stage mid-way.** There's no reliable signal for how far it got — restart it whole.
- **Treating `BLOCKED` as a technical failure to retry, or `FAILED` as a content question for the human.** They need different responses; check which one it is before acting.
- **Hand-editing `board.md`.** It's a generated view; edits are lost on the next regeneration and the file falls out of sync with the real task records.
- **Overwriting `history` instead of appending.** Destroys the audit trail that makes this behave like a Jira activity feed rather than a mutable status flag.

## Done When

- A task file exists at `docs/qa/pipeline-state/<task-id>.json` for every spec that has entered the pipeline.
- Every status change has a matching `history` entry and an updated `updated_at`.
- `board.md` reflects the current state of every task file after any change.
- A stage marked `done` is never re-run by a later session; a stage left `in_progress` by an interrupted session is always re-run before the pipeline proceeds.

## Related Skills

- **run-qa-pipeline** — the orchestrator that calls this skill around every stage invocation and reads it first to decide whether to start fresh or resume.
- **spec-gap-analysis** — its whole-spec `BLOCKED` verdict is what this skill's `BLOCKED` status is driven by.
- **qa-doc-review** — its `Disputed` output populates `disputed_items` at the `IN_REVIEW` transition.
