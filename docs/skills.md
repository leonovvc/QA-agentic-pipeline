# Skills catalogue

18 skills. **Original** skills were written for this plugin. **Adapted** skills come from
[petrkindlmann/qa-skills](https://github.com/petrkindlmann/qa-skills) (MIT) and were
reworked into the procedure of a specific pipeline stage — the methodology is kept, the
wiring is new (see [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) for the per-skill
change list).

Skills are loaded on demand: Claude Code reads a skill's full text only when it is
invoked or preloaded by an agent, so the catalogue's size does not cost context in
sessions that don't use it.

## Orchestration and conventions

| Skill | Origin | Used by | What it does |
|---|---|---|---|
| [`run-qa-pipeline`](../skills/run-qa-pipeline/SKILL.md) | original | entry point | Drives the four stages, resolves language, assembles the Human Checkpoint; owns the [artifact contract](../skills/run-qa-pipeline/references/artifact-contract.md) |
| [`qa-pipeline-task-state`](../skills/qa-pipeline-task-state/SKILL.md) | original | orchestrator | Jira-style task file, status machine, resume rules, `board.md` |
| [`qa-output-standards`](../skills/qa-output-standards/SKILL.md) | original | all agents | Output language (EN/RU), what always stays English, readability bar for cases and test code |
| [`qa-project-context`](../skills/qa-project-context/SKILL.md) | adapted | all stages | `.agents/qa-project-context.md`: stack, risks, conventions, and the **QA Pipeline** settings |

## Stage 1 — spec analysis

| Skill | Origin | What it does |
|---|---|---|
| [`spec-gap-analysis`](../skills/spec-gap-analysis/SKILL.md) | original | Requirements Inventory, gaps, contradictions, Track A/B questions, assumptions, inline-annotated spec |
| [`security-testing`](../skills/security-testing/SKILL.md) — Lens Mode | adapted | OWASP Top 10 (2025) questions asked of the spec |
| [`risk-based-testing`](../skills/risk-based-testing/SKILL.md) | adapted | Orders Track B questions by the risk of what they block |

## Stage 2 — QA documentation

| Skill | Origin | What it does |
|---|---|---|
| [`test-planning`](../skills/test-planning/SKILL.md) | adapted | `test-plan.md`: scope, assumptions, risk table, traceability matrix, pyramid, entry/exit criteria |
| [`risk-based-testing`](../skills/risk-based-testing/SKILL.md) — Pipeline Mode | adapted | Impact × probability per REQ → zone → P0–P3 → required depth |
| [`test-design-techniques`](../skills/test-design-techniques/SKILL.md) | original | EP, BVA, decision tables, pairwise, state transitions, security negative cases, exploratory charters |
| [`test-pyramid-strategy`](../skills/test-pyramid-strategy/SKILL.md) | original | Lowest sufficient level per case, with a reason; E2E budget |
| [`test-case-management`](../skills/test-case-management/SKILL.md) | adapted | Eight-field case format, lint checklist, files per level or TestRail / Xray / Zephyr / Qase payloads |
| [`security-testing`](../skills/security-testing/SKILL.md) — Lens Mode | adapted | Security negative cases tagged with their OWASP category |

## Stage 3 — autotests

| Skill | Origin | What it does |
|---|---|---|
| [`stack-detection-for-autotests`](../skills/stack-detection-for-autotests/SKILL.md) | original | Detects runner, directories, conventions, CI before any test is written |
| [`ai-test-generation`](../skills/ai-test-generation/SKILL.md) — Pipeline Mode | adapted | Case → oracles → code, with a mechanical check against hallucinated APIs |
| [`unit-testing`](../skills/unit-testing/SKILL.md) | adapted | Jest / Vitest / pytest playbook for unit-level cases |
| [`api-testing`](../skills/api-testing/SKILL.md) | adapted | REST / GraphQL playbook for API-level and security-lens cases |
| [`playwright-automation`](../skills/playwright-automation/SKILL.md) | adapted | Playwright playbook for E2E cases: one `test.step` per case step |

## Stage 4 — review

| Skill | Origin | What it does |
|---|---|---|
| [`qa-doc-review`](../skills/qa-doc-review/SKILL.md) | original | Independent re-derivation from the spec, severity scale, Disputed section |
| [`ai-qa-review`](../skills/ai-qa-review/SKILL.md) | adapted | Test-code review: TC IDs, oracle match, honest status, six smell buckets, mutation testing |

## Standalone use

| Skill | Standalone mode |
|---|---|
| `security-testing` — Scan Mode | OWASP ZAP, OSV-Scanner, Semgrep, auth/session tests in CI — only on explicit request |
| `risk-based-testing` — Product Mode | Product-level risk heatmap with failure-mode analysis |
| `test-planning` | Sprint and release test plans with estimation and buffers |
| `ai-test-generation` — Standalone Mode | Full seven-step generation from a PRD, story, diff, bug report or OpenAPI spec |
| `ai-qa-review` | Audit of an existing test suite |
| `test-case-management` | Authoring and linting cases directly in TestRail, Xray, Zephyr Scale, or Qase |
