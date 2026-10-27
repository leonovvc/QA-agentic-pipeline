# Artifact Contract

The single definition of what each pipeline stage writes, where, and with which IDs.
Every skill and agent in this plugin refers here instead of restating it, and
`tools/check_artifacts.py` in the plugin repository validates real pipeline output
against exactly this document. If a skill and this file disagree, this file wins and
the skill is the bug.

## File layout

All paths are relative to the target repository root. `<task-id>` comes from
`qa-pipeline-task-state` (`<slug>-<6 hex>`). The docs root defaults to `docs/qa/` and
can be changed with `Docs location` in `.agents/qa-project-context.md`.

```
docs/qa/
├── pipeline-state/
│   ├── <task-id>.json          task record (source of truth for progress)
│   └── board.md                generated view of all tasks
└── <task-id>/
    ├── spec-source.md          Stage 1 — the spec text as received/extracted (input snapshot)
    ├── spec-gap-report.md      Stage 1 — structured findings + Requirements Inventory
    ├── spec-annotated.md       Stage 1 — spec text with inline markers
    ├── test-plan.md            Stage 2 — scope, risk table, traceability matrix
    ├── test-cases-unit.md      Stage 2 — only levels that have cases
    ├── test-cases-api.md
    ├── test-cases-e2e.md
    ├── test-cases-manual.md
    ├── autotest-summary.md     Stage 3 — TC → test mapping and real run results
    ├── qa-review-report.md     Stage 4 — independent review
    └── checkpoint.md           Human Checkpoint Report (assembled by run-qa-pipeline)
```

Autotest code never goes under `docs/` — it lands in the repository's own test
directories as detected by `stack-detection-for-autotests`.

## IDs

| ID | Assigned by | Meaning | Rules |
|---|---|---|---|
| `REQ-<n>` | Stage 1 | One testable requirement from the spec, in spec order | Numbered from 1, never renumbered in later stages; every REQ cites a spec location |
| `Q<n>` | Stage 1 | A Blocking Gap, Contradiction, or Open Question | One global sequence across those three sections — `Q3` exists once in the report and once as an inline marker |
| `A<n>` | Stage 1 (Stage 2 continues the sequence) | An assumption made to proceed | Stage 2's own assumptions continue the numbering (`A5`, `A6`, …) and are marked "(Stage 2)" |
| `TC-<LVL>-<nnn>` | Stage 2 | A test case. `LVL` ∈ `UNIT`, `API`, `E2E`, `MAN` | Zero-padded to 3 digits; the level in the ID matches the case's Level field and the file it lives in |
| `R-<n>` | Stage 4 | A review finding | Every finding has exactly one severity and at least one citation (REQ, Q/A, TC ID, or file path) |

## Stage 1 — `spec-gap-report.md`

Required sections (English heading, or the Russian equivalent in brackets):

1. `## Source` [`## Источник`]
2. `## Testability Score: <1-5>` [`## Оценка тестируемости: <1-5>`]
3. `## Requirements Inventory` [`## Перечень требований`] — a table:

   | ID | Spec location | Requirement | Acceptance criterion | Testable |
   |---|---|---|---|---|
   | REQ-1 | §2, bullet 1 | Code applies 10% to the cart subtotal | Total = subtotal × 0.9, rounded half-up to 0.01 | yes |
   | REQ-2 | §3 | Code is validated "quickly" | none stated | no → Q4 |

   `Testable` is `yes`, `partly → Q<n>`, or `no → Q<n>`. Every `no`/`partly` row points
   at a Q.
4. `## Blocking Gaps` [`## Блокирующие пробелы`]
5. `## Contradictions` [`## Противоречия`]
6. `## Open Questions` [`## Открытые вопросы`] with `### Track A` and `### Track B`
7. `## Assumptions Made to Proceed` [`## Допущения`]
8. `## Security Lens` [`## Безопасность`] — results of the OWASP-based spec check from
   `security-testing` (findings are Q items like any other; this section lists which
   checklist rows applied and which were not applicable)
9. `## Ready-for-Test-Design Checklist` [`## Готовность к тест-дизайну`]

Each Q and A entry starts with its ID in bold: `**Q3** — §4.1 vs §6: refund window…`.

## Stage 1 — `spec-annotated.md`

The spec text in original order with inline markers `[Q<n>: …]` and `[A<n>: …]`.
Invariant: the set of Q/A IDs in the annotated spec equals the set in the report.

## Stage 2 — `test-plan.md`

Required sections:

1. `## Scope` [`## Объём`] — in scope, out of scope, blocked (with the Q that blocks it)
2. `## Assumptions` [`## Допущения`] — which Stage 1 assumptions the plan builds on,
   plus Stage 2's own (`A<n> (Stage 2)`)
3. `## Risk Assessment` [`## Оценка рисков`] — one row per REQ (method: `risk-based-testing`, Pipeline Mode):
   `REQ | Impact (1-5) | Probability (1-5) | Score | Zone | Priority (P0-P3) | Depth / rationale`
4. `## Traceability Matrix` [`## Матрица трассировки`] — one row per REQ:
   `REQ | Test cases | Techniques | Status (covered / blocked by Q<n> / out of scope)`
5. `## Pyramid Allocation` [`## Распределение по пирамиде`] — counts per level and a
   one-paragraph rationale
6. `## Entry and Exit Criteria` [`## Критерии входа и выхода`]
7. `## Case Location` [`## Где лежат кейсы`] — the case files, or the test-case system
   project/section path

## Stage 2 — `test-cases-<level>.md`

Each case is a level-3 heading followed by a fixed field list:

```markdown
### TC-API-004: Expired code is rejected with 422 and the total is unchanged
- **Traces:** REQ-3, A2
- **Technique:** Equivalence partitioning — invalid class "expired"
- **Level:** API — the rule is enforced server-side; the UI adds no logic here
- **Priority:** P1
- **Preconditions:** Cart `C1` exists with one item priced 1000.00
- **Test data:** code `SPRING10`, `expires_at` = yesterday 23:59:59 UTC
- **Steps:**
  1. `POST /carts/C1/promo` with body `{"code": "SPRING10"}`
- **Expected result:** `422`, body `error.code = "PROMO_EXPIRED"`; `GET /carts/C1` total is `1000.00`
```

Field labels and their accepted Russian equivalents:

| English | Русский |
|---|---|
| Traces | Трассировка |
| Technique | Техника |
| Level | Уровень |
| Priority | Приоритет |
| Preconditions | Предусловия |
| Test data | Тестовые данные |
| Steps | Шаги |
| Expected result | Ожидаемый результат |

Multi-step cases put each step's expected outcome inline
(`1. Submit the form → Expected: error "…" is shown`) and keep **Expected result** for the
final observable outcome.

Invariants checked by the tooling:

- Every TC has all eight fields, non-empty.
- `Traces` lists at least one existing `REQ-<n>` (or, for `MAN` exploratory charters,
  at least one REQ or Q).
- The `LVL` in the ID matches the `Level` field and the file name.
- Every REQ with `Testable = yes` appears in at least one TC's `Traces`, or is listed
  as out of scope / blocked in the Traceability Matrix.
- `Priority` is `P0`–`P3`, and each REQ's highest-priority case carries the REQ's own
  priority from the Risk Assessment. Supporting cases of the same REQ (an exploratory
  charter, a cosmetic check) may be lower.

## Stage 3 — `autotest-summary.md`

Required sections:

1. `## Stack Profile` [`## Профиль стека`] — output of `stack-detection-for-autotests`
2. `## Mapping` [`## Соответствие кейсов и тестов`] — table:
   `TC | File | Test | Status | Notes` where Status ∈ `passed`, `failed`,
   `not run`, `manual`. `failed` rows say whether it is a suspected product defect or a
   test defect; `not run` rows say exactly what was missing.
3. `## Commands Run` [`## Выполненные команды`] — the exact commands and their exit codes
4. `## Suspected Product Defects` [`## Предполагаемые дефекты продукта`]
5. `## Allocation Disagreements` [`## Несогласие с распределением`] — cases whose level
   Stage 3 disagrees with, without having changed it

Every automated test's title (or tag) contains its TC ID, and every non-`MAN` TC
appears in the Mapping table exactly once.

## Stage 4 — `qa-review-report.md`

Required sections:

1. `## Traceability Summary` [`## Сводка трассировки`] — `N of M` REQs covered, with
   every REQ listed as covered / not covered / blocked
2. `## Findings` [`## Замечания`] with `### Blocking`, `### Major`, `### Minor`
   (or `### Блокирующие`, `### Существенные`, `### Незначительные`)
3. `## Disputed — Needs Human Decision` [`## Спорное — нужно решение человека`] —
   "None" / "Нет" when empty
4. `## Readability` [`## Читаемость`] — result of the `qa-output-standards` check
5. `## Autotest Review` [`## Ревью автотестов`] — the `ai-qa-review` result, when
   autotests exist

Each finding: `**R-<n>** [<severity>] <citation> — <what is wrong> → <what would fix it>`.

## Task record — `pipeline-state/<task-id>.json`

See `qa-pipeline-task-state` for the full schema. Fields the contract relies on:
`task_id`, `status`, `output_language` (`en`|`ru`), `docs_dir`, `stages[].status`,
`stages[].output` (string or array of paths), `assumptions_log`, `disputed_items`,
`history` (append-only).
