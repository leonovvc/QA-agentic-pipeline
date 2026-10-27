---
name: test-case-management
description: >-
  Write test cases to a deterministic standard and file them where the team keeps them:
  per-pyramid-level markdown files in the QA pipeline, or TestRail, Xray (Jira), Zephyr
  Scale, and Qase via their real APIs/CSV import. Covers case anatomy (ID, traces,
  technique, level, priority, preconditions, test data, steps, expected result), one case
  per rule, ambiguous-step linting, extending an existing suite hierarchy instead of a
  parallel one, requirement traceability, and which manual cases should graduate to
  automation. Use when: "write test cases," "manual test case," "TestRail/Xray/Zephyr/Qase
  case," "import CSV into TestRail," "lint these steps," "traceability report," "should
  this be automated." Not for: deciding which techniques produce which cases — use
  test-design-techniques; not for test code — use unit-testing, api-testing, or
  playwright-automation.
  Related: test-design-techniques, test-pyramid-strategy, test-planning,
  qa-output-standards, qa-doc-review, qa-project-context.
license: MIT
metadata:
  author: qa-agentic-pipeline
  adapted_from: petrkindlmann/qa-skills@test-case-management (MIT, Petr Kindlmann)
  version: "2.0"
  category: process
---

<objective>
A test case that says "test the login" with expected result "verify it works" passes
every review and catches nothing — two testers run it differently and neither can say whether
it failed. This skill produces deterministic cases (discrete steps, one observable expected
result each, concrete test data) that also carry their traceability (which requirement,
which technique, which pyramid level), files them where the team actually keeps cases, and
emits tool-correct API/CSV payloads for TestRail, Xray Cloud, Zephyr Scale, and Qase —
whose look-alike APIs use different auth schemes, endpoints, and step-field names that
agents routinely cross-wire.
</objective>

## Role in the QA pipeline

| Stage | Who | Uses this skill for |
|---|---|---|
| 2 | `qa-doc-writer` | Writing every case in the pipeline format below, filing it (local files or test-case system), self-linting before handoff |
| 3 | `autotest-builder` | Reading cases: the TC ID becomes part of each autotest's title; `Level` decides the framework |
| 4 | `qa-doc-reviewer` | The lint checklist is part of the Case quality dimension of `qa-doc-review` |

The case text follows the run's output language and the readability bar in
`qa-output-standards`; IDs and field labels follow the artifact contract
(`${CLAUDE_PLUGIN_ROOT}/skills/run-qa-pipeline/references/artifact-contract.md`).

### Where the cases live

- **No test-case system, or no access given** → one markdown file per pyramid level in
  `docs/qa/<task-id>/`: `test-cases-unit.md`, `test-cases-api.md`, `test-cases-e2e.md`,
  `test-cases-manual.md` — only for levels that have cases. Never create an empty file.
- **A test-case system with access** → first list the existing hierarchy (TestRail
  sections, Xray/Zephyr folders, Qase suites) in the project named in
  `qa-project-context`, and **extend it** — add the feature's section under the right
  parent; never stand up a parallel tree. Tag each case with its pyramid level and TC ID,
  link it to the requirement issue at creation, and record the project + section path in
  `test-plan.md` → Case Location.

## Quick Route

| Request | Go to |
|---------|-------|
| Write one well-formed case from an AC | [Test-Case Anatomy](#test-case-anatomy) |
| Bulk-generate cases from a story | [Bulk Authoring](#bulk-authoring-from-stories) + tool section |
| "Lint these steps / are these verifiable?" | [Ambiguous-Step Linting](#ambiguous-step-linting) + `references/linting.md` |
| TestRail / Xray / Zephyr / Qase API payload | [Tool Payloads](#tool-payloads) + `references/tool-apis.md` |
| CSV to import into TestRail | `references/import-and-traceability.md` (CSV section) |
| Organize suites/sections | `references/import-and-traceability.md` (organization) |
| Requirements ↔ tests, coverage gaps | [Traceability](#traceability) + `references/import-and-traceability.md` |
| Manual → automation decision | [Automation Graduation](#automation-graduation) |

## Discovery Questions

First, check `.agents/qa-project-context.md` in the project root for the tool, project keys,
and conventions; skip anything answered there. If it's missing, suggest creating one with the
`qa-project-context` skill. Then clarify:

- **Which tool — TestRail, Xray, Zephyr Scale, or Qase?** Each has a different API auth scheme,
  endpoint shape, and step-field name. Getting this wrong produces payloads that 401 or 400.
- **TestRail only: single-repository mode or multiple suites?** Changes whether cases live under
  sections in one suite or in separate suites — affects every `section_id` and the org plan.
- **Xray/Zephyr only: Jira Cloud or Server/DC?** Cloud and Server use different base paths and
  auth. This skill targets Cloud; Server uses different endpoints.
- **Source of the cases — acceptance criteria, a user story, a free-form feature?** Drives how
  many cases to generate and how to split rules.
- **Do you need requirement traceability?** If yes, capture the Jira/requirement issue keys now
  so cases link on creation rather than being back-filled.

---

## Core Principles

1. **An expected result must be deterministically checkable.** A second human (or a machine)
   must be able to agree on pass/fail without guessing. "Works", "looks right", "is fine",
   "wait a bit" fail this test. Name an exact value, a named element and its state, a specific
   message, a status code, a count, or a time-bounded condition.

2. **One assertion per step.** Each step has a single expected result. Cramming three checks
   into one step makes a failure ambiguous about which check broke and which to re-run.

3. **One case per business rule, not one giant case.** "Valid code reduces total / expired code
   errors / used code rejected" is three cases with three independent pass/fail verdicts — not
   one case with a paragraph of expecteds.

4. **The tool's API is the spec — don't cross-wire the four tools.** TestRail's
   `custom_steps_separated`, Qase's `Token` header, Xray's two-step GraphQL auth, and Zephyr's
   separate `teststeps` call are NOT interchangeable. Copy from the right tool's section.

5. **Traceability exists to surface what is NOT covered.** The deliverable is the list of
   requirements with zero linked tests, from a native coverage report — not a spreadsheet that
   rots and not "every test links to something."

6. **Automate by ROI, not by volume.** Limited capacity means stable, high-frequency,
   regression/smoke cases graduate first; exploratory, one-off, and high-churn/flaky cases stay
   manual. "Automate everything" wastes capacity on the worst candidates.

---

## Test-Case Anatomy

### Pipeline format (eight fields + ID)

Every case in the pipeline is a level-3 heading `TC-<LVL>-<nnn>: <title>` followed by
eight mandatory fields: **Traces**, **Technique**, **Level**, **Priority**,
**Preconditions**, **Test data**, **Steps**, **Expected result** (exact format in the
artifact contract). The first four are what make a case reviewable and automatable:

| Field | Holds | Why it is mandatory |
|---|---|---|
| ID `TC-<LVL>-<nnn>` | Level code + sequence | Autotests, the summary, and review findings cite it |
| **Traces** | `REQ-<n>` (and any `A<n>` the case depends on) | Without it coverage can only be guessed |
| **Technique** | Named technique + the class/boundary/rule/transition this case represents | Makes a missing boundary visible to the reviewer |
| **Level** | `Unit` / `API` / `E2E` / `Manual` + one-clause justification | `test-pyramid-strategy` requires the reason, not just the label |
| **Priority** | `P0`–`P3` from the plan's Risk Assessment | Decides run order and what is cut first |

For a multi-step case, put the expected result of each step inline
(`1. … → Expected: …`) and keep **Expected result** for the final observable outcome.
Single-action API and unit cases have one step and one expected result.

### The five readability parts (any tool, any format)

A well-formed case has these five parts. Every part is mandatory; a case missing
preconditions or test data is not reproducible.

| Part | What it holds | Failure if omitted |
|------|---------------|--------------------|
| **Title** | Feature — scenario — expected outcome, one line | Unsearchable, duplicated |
| **Preconditions** | State the test assumes (account exists, on page X, flag on) | Tester guesses setup; flaky |
| **Steps** | Discrete actions, one action per step | Non-reproducible |
| **Expected Results** | One observable post-condition per step | Not verifiable |
| **Test Data** | Concrete values used (codes, emails, counts, timings) | Not repeatable |

**BAD** (single vague step, non-verifiable expected, no preconditions, no data):

```
Title: Login test
Steps: Test the login.
Expected: Verify it works.
```

**GOOD** — from the AC "after 5 wrong-password attempts, the account locks for 15 minutes":

```
Title: Login — account locks for 15 minutes after 5 failed attempts
Preconditions: A registered account exists for user@example.com. The user is logged out
               on the /login page. Lockout policy: 5 attempts, 15-minute lockout.
Test Data: email user@example.com, wrong password "WrongPass!", correct password "Passw0rd!"
Steps (one assertion per step / single expected result each):
  1. Action:   Submit the login form with user@example.com and "WrongPass!".
     Expected: Error "Invalid email or password." shows; the failed-attempt count is now 1.
  2. Action:   Repeat the wrong-password submit until 5 failed attempts total.
     Expected: On the 5th failure the account is locked; message reads
               "Account locked. Try again in 15 minutes."
  3. Action:   Immediately submit with the CORRECT password "Passw0rd!".
     Expected: Login is still blocked; the same lockout message is shown (lockout overrides
               valid credentials).
  4. Action:   Wait 15 minutes, then submit with the correct password.
     Expected: Login succeeds and the dashboard loads.
```

Note: explicit preconditions, concrete test data (5 attempts, 15-minute lockout), discrete
steps, and a single deterministic expected result per step.

---

## Bulk Authoring from Stories

Given a story or set of acceptance criteria, split into cases by rule, then generate the
tool-specific payload. In the pipeline, the "rules" are the partitions, boundaries, table
rules, or transitions `test-design-techniques` derived for each REQ — one case per
derived item, never one case per REQ. Worked example for the discount-code story (valid reduces total / expired
errors / already-used rejected) → **three** cases:

1. Apply a valid code → total reduces (happy path).
2. Apply an expired (invalid) code → inline error, total unchanged.
3. Apply an already-used / already-redeemed code → rejected, total unchanged.

Add the obvious negatives the story implies but doesn't state (empty code, malformed code) when
the team wants edge coverage. Each case gets discrete steps and one expected per step — never one
giant case covering all three rules. Scope — which requirements get cases at all — is decided in `test-plan.md`
(`test-planning` + `risk-based-testing`), not here.

---

## Ambiguous-Step Linting

When asked to "lint" a suite, your job is to FLAG non-deterministic steps and rewrite them — NOT
to agree that they "look fine." The agreeable failure mode (rubber-stamping "everything works")
is the exact thing this section prevents.

A step is bad when its expected result is not deterministically verifiable. Flag any of:

- **Vague action** — "click around", "test the X", "play with it" → name the exact element + action.
- **Vague data** — "some data", "a value", "stuff" → give concrete test data.
- **Non-observable expected** — "everything works", "it looks right", "is fine", "no problems"
  → name the exact observable result.
- **Unbounded wait** — "wait a bit", "after a while" → bound it ("within 10 s" / "until the
  spinner disappears and a row appears").
- **Multiple assertions in one step** → split to one assertion per step.

For the classic four-step bad suite ("app opens / everything works / it looks right / the report
is ready"), all four are ambiguous and must be flagged and rewritten with explicit selectors,
exact values, and bounded conditions — never returned as "no issues found". The full lint
checklist, the worked rewrite of those four steps, and the lint-output table format are in
`references/linting.md`.

---

## Tool Payloads

The four tools are easy to cross-wire. Summary — full curl/GraphQL bodies in
`references/tool-apis.md`:

| Tool | Auth | Create endpoint | Steps field |
|------|------|-----------------|-------------|
| **TestRail** | Basic `email:api_key` | `POST add_case/{section_id}` | `custom_steps_separated` array of `{content, expected}` |
| **Xray Cloud** | `POST /api/v2/authenticate` → Bearer token | GraphQL `createTest` at `/api/v2/graphql` | `steps[] {action, result}`; Gherkin → `testType: Cucumber` + `gherkin` |
| **Zephyr Scale Cloud** | `Authorization: Bearer <JWT>` | `POST /v2/testcases` then `POST /v2/testcases/{key}/teststeps` | separate `teststeps` call, `inline {description, expectedResult, testData}` |
| **Qase** | header `Token: <key>` | `POST /v1/case/{CODE}/bulk` | `steps[] {action, expected_result, data}` |

Tool-specific traps that the reference spells out and you must respect:

- **TestRail** — separated steps need `custom_steps_separated` (NOT the plain `custom_steps` text
  blob); the endpoint is `add_case/{section_id}` (NOT `add_test`, which is a run instance). Base
  is `{instance}/index.php?/api/v2`. Don't use a Qase-style `POST /case`.
- **Xray Cloud** — authenticate first (`/api/v2/authenticate` with client_id/client_secret →
  bearer, 24h), then prefer **GraphQL** `createTest`. Import Gherkin as a **Cucumber** test, not
  a Generic one. Avoid the deprecated Cloud path `/rest/raven/1.0/...` and Server-style REST and
  Jira username/password basic auth.
- **Zephyr Scale Cloud** — base is `api.zephyrscale.smartbear.com/v2` with JWT Bearer. Steps are a
  SEPARATE `/testcases/{key}/teststeps` call, not a text blob in the create body. Don't emit `/v1/`,
  the wrong host, or Qase's `Token` header.
- **Qase** — auth is `Token: <key>`, NOT `Authorization: Bearer`. Use `POST /case/{CODE}/bulk`
  with a `cases` array instead of N single POSTs. Don't use TestRail's `add_case` /
  `custom_steps_separated`.

CSV import for TestRail (header row mapped to importer fields: `Title`, `Section Hierarchy`,
`Steps (Separated)`, `Expected Result`, `Priority`, `Type`, `Preconditions`) is in
`references/import-and-traceability.md` — use a real CSV with a header row, never free-form prose
or a single Description column, and never JSON when CSV was requested.

---

## Organization

Use **sections and subsections** for hierarchy, kept **shallow** (3–4 levels). For a web + mobile
product the default is **single-repository mode** with top-level sections per platform
(`Web`, `Mobile (iOS)`, `Mobile (Android)`, `Shared / API`), feature sections beneath. Split into
**multiple suites** only when platforms are owned by separate teams with separate cadences.

Avoid: one folder per test case, deep nesting 7+ levels deep, dumping every case in the root
section, and duplicating the same case across suites (keep one source of truth). The
single-repository vs multiple-suites trade-off and the full org rules are in
`references/import-and-traceability.md`.

---

## Traceability

Goal: a coverage report that shows which **stories have no tests** — the uncovered requirements.

For **Xray on Jira**: from each Test, add the native **"tests" issue link** to the requirement's
Jira issue key (NOT to a Test Execution — that records runs, not coverage). Read per-story
coverage from the Story's Test Coverage panel, and project-wide from the **Traceability Report /
Requirement Coverage report**. Then filter for requirements with **0 linked tests** — those are
the gaps to close. Do not propose a manual spreadsheet as the only traceability mechanism, and do
not ignore uncovered requirements. Zephyr Scale, Qase, and TestRail equivalents (issue links +
their coverage/traceability views) are in `references/import-and-traceability.md`.

---

## Automation Graduation

Score each manual case by ROI: `value ≈ run_frequency × regression_importance ÷ (automation_cost
× expected_maintenance)`. With limited capacity (e.g. a 400-case Zephyr Scale backlog):

- **Automate first:** high-frequency cases (run every release / regression / smoke), on stable /
  low-churn / deterministic features, that guard critical regression or smoke paths.
- **Stay manual:** exploratory or one-off cases, rarely-run cases, high-churn UI still in flux,
  flaky / non-deterministic behavior, and cases needing human judgment.

Reject "automate everything" and "automate the flaky, frequently changing UI first" — both spend
scarce capacity on the worst-ROI candidates. Full decision rule in
`references/import-and-traceability.md`. In the pipeline the graduation decision is made at
planning time: a case whose Level is `Unit`/`API`/`E2E` is automated by Stage 3; `Manual`
cases stay manual and Stage 3 lists them as such. The test code itself is written with
`unit-testing`, `api-testing`, or `playwright-automation` — not here.

---

## Review Hygiene

- Every case is reviewable in one screen: title states the outcome, preconditions present, steps
  discrete, each expected observable, test data concrete.
- Run the lint checklist on a new case before it merges; reject non-deterministic expecteds.
- Link to the requirement at creation time, not as a back-fill.
- Tag the suite (smoke / regression / platform) so runs can filter; an untagged 400-case repo is
  unusable for release selection.

---

## Anti-Patterns

### 1. One vague step with a "verify it works" expected
"Test the login → verify it works" is unrunnable. Write discrete steps, one observable expected
each, explicit preconditions, concrete test data.

### 2. Rubber-stamping a suite when asked to lint it
Saying steps "look fine" or lightly rewording while leaving "everything works" and "wait a bit"
in place is the failure linting exists to catch. Flag every non-verifiable expected and rewrite it.

### 3. Cross-wiring the four tools' APIs
Bearer on Qase (it uses `Token`), `add_case`/`custom_steps_separated` on Qase or Zephyr,
`/rest/raven/1.0/` on Xray Cloud, `/v1/` on Zephyr Scale Cloud, steps as a text blob in Zephyr's
create body. Each is a 4xx or a silent wrong-field. Copy from the correct tool section.

### 4. One giant case for a multi-rule story
Folding "valid / expired / already-used" into one case yields a single pass/fail that hides which
rule broke. One case per rule.

### 5. CSV as free-form prose or a single Description column
A TestRail import without a header row mapped to importer fields needs manual remapping. Provide
`Title`, `Section Hierarchy`, `Steps (Separated)`, `Expected Result`, etc.

### 6. Deep nesting and per-case folders
7+ level trees and one-folder-per-case make the repository unnavigable. Keep 3–4 shallow levels of
sections; platform at the top for web+mobile.

### 7. Traceability as a manual spreadsheet
A hand-kept sheet can't reliably answer "which stories have no tests." Use the tool's native
requirement→test link and coverage/Traceability report, and surface the uncovered requirements.

### 8. Automate-everything / automate-the-flaky-first
Automating one-off exploratory cases or high-churn/flaky UI first burns capacity for negative ROI.
Sequence stable high-frequency regression/smoke first.

---

## Verification

Prove the produced artifact actually works before handing it off, smallest check first:

- **Pipeline format:** every `### TC-` heading is followed by all eight fields; the level
  code in the ID matches the Level field and the file; every Traces entry names a REQ that
  exists in `spec-gap-report.md`. `tools/check_artifacts.py` in the plugin repository runs
  exactly these checks.

- **Lint your own output:** grep the generated cases for the banned expecteds —
  `grep -niE "verify it works|looks right|is fine|wait a bit|no problems|everything works|работает корректно|отображается правильно|всё работает|подождать немного" docs/qa/*/test-cases-*.md`
  must return nothing. Any hit is a non-deterministic expected to rewrite.
- **TestRail CSV:** open it and confirm a header row exists with `Title`, `Section Hierarchy`,
  `Steps (Separated)`, `Expected Result` — `head -1 cases.csv` should show those columns, not a
  single `Description`. Dry-run the import wizard; the wizard auto-matches columns with no manual
  remapping when the headers are right.
- **API payload, before the real POST:** validate the JSON (`jq . payload.json` exits 0) and
  confirm the auth header and endpoint match the target tool's row in
  [Tool Payloads](#tool-payloads) — Qase `Token:` not `Authorization: Bearer`, TestRail
  `add_case/{section_id}` not `add_test`. A `201`/test-id in the response (or a `200` with the new
  case `key` for Zephyr) confirms the create; a `401` means the auth scheme is cross-wired, a
  `400` means the step field is.
- **Traceability:** run the tool's coverage/Traceability report and confirm it lists requirements
  with 0 linked tests — an empty "uncovered" column means the links landed; a populated one is the
  gap list to close.

---

## Done When

- In the pipeline: every case has its ID and all eight fields, sits in the file for its level,
  traces to at least one existing REQ, and is written in the run's output language.
- Each generated case has a title, preconditions, discrete steps, one observable expected result
  per step, and concrete test data — no "verify it works" / "looks right" / "wait a bit" expecteds.
- A multi-rule story produced one case per rule, not one combined case.
- Any emitted API payload uses the correct tool's auth scheme, endpoint, and step-field name
  (TestRail `custom_steps_separated`+`add_case/{section_id}`; Xray two-step auth + GraphQL
  `createTest`, Cucumber for Gherkin; Zephyr `/v2` Bearer + separate `/teststeps`; Qase `Token`
  header + `/case/{CODE}/bulk`).
- Any TestRail CSV has a header row mapping columns to importer fields (`Title`,
  `Section Hierarchy`, `Steps (Separated)`, `Expected Result`).
- A linted suite returns every ambiguous step flagged and rewritten — never "no issues found"
  when smells are present.
- Traceability uses the tool's native requirement→test link and a coverage report that lists the
  uncovered requirements.
- Automation graduation produces an ROI-ordered list (stable + high-frequency + regression/smoke
  first) and names what stays manual.

---

## Related Skills

- **test-design-techniques** — produces the partitions/boundaries/rules each case represents;
  the Technique field names them.
- **test-pyramid-strategy** — fills the Level field with its justification.
- **test-planning** — the plan's Traceability Matrix and Case Location point at these cases.
- **qa-output-standards** — output language and the readability bar for titles, steps, and
  expected results.
- **qa-doc-review** — re-runs the lint checklist and the traceability checks independently.
- **qa-project-context** — the test-case system, project keys, and conventions this skill reads
  before generating any payload.

---

## Reference Files (in `references/`)

- **tool-apis.md** — full TestRail / Xray Cloud / Zephyr Scale / Qase create-case payloads
  (curl + GraphQL), auth flows, and the per-tool cross-wiring traps.
- **linting.md** — the ambiguous-step lint checklist, the worked rewrite of the four classic bad
  steps, and the lint-output table format.
- **import-and-traceability.md** — TestRail CSV column→field mapping with a 3-case example,
  suite/section organization rules, requirement traceability + coverage-gap reports, and the
  automation-graduation decision rule.
