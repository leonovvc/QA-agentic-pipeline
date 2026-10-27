---
name: qa-output-standards
description: >-
  The language and readability contract for everything the QA pipeline writes that a
  human reads: test cases, plans, reports, and autotest code. Fixes the output language
  (English or Russian, chosen once per project or run), what always stays English
  (identifiers, IDs, framework keywords), and the readability bar for cases and test
  code — one behavior per case/test, concrete data, Arrange-Act-Assert, names that
  state the expected behavior, comments that explain why. Use when: "which language
  should the test cases be in," "write the cases in Russian/English," "make the
  autotests readable," "test naming convention," "review readability of test cases or
  test code." Not for: choosing which tests to write — use test-design-techniques; not
  for test-smell detection beyond readability — use ai-qa-review.
  Related: qa-project-context, test-case-management, unit-testing, api-testing,
  playwright-automation, ai-qa-review, run-qa-pipeline.
license: MIT
metadata:
  author: qa-agentic-pipeline
  version: "1.0"
  category: foundation
---

<objective>
A test case that two testers read differently, or an autotest whose failure message
doesn't tell you what broke, is a defect in the QA work itself — no matter how good the
coverage behind it. This skill sets one bar for every human-facing artifact the pipeline
produces: written in the language the team chose, and readable to the standard of the
best public test suites. It is deliberately short and prescriptive so every stage
applies it the same way and the reviewer can check it mechanically.
</objective>

## 1. Output language

### How the language is chosen

The pipeline writes in exactly one **output language** per run: `en` (English) or `ru`
(Russian). Resolve it in this order and stop at the first hit:

1. The user's explicit instruction in the current request ("write the cases in English").
2. `Output language` in the **QA Pipeline** section of `.agents/qa-project-context.md`.
3. The task file's `output_language` field (`qa-pipeline-task-state`) — a resumed task
   keeps the language it started with.
4. Ask once, at the very start of the run, as a Track A question ("English or Russian
   for test cases and test code?"). If nobody can answer (unattended run), use the
   language the spec itself is written in, and log that as an assumption.

Record the resolved value in the task file (`output_language`) so every stage, and every
later session, uses the same one. Never switch language mid-run.

### What follows the output language

- All prose in `spec-gap-report.md`, `spec-annotated.md` markers, `test-plan.md`,
  `test-cases-*.md`, `autotest-summary.md`, `qa-review-report.md`.
- Test case titles, preconditions, steps, test data descriptions, expected results.
- Autotest **titles / display names** (`test('…')`, `it('…')`, `@DisplayName`,
  pytest docstrings or `ids=`), `test.step()` labels, assertion messages, and code
  comments.

### What is always English, whatever the output language

| Always English | Why |
|---|---|
| Identifiers: function, method, variable, class, file and directory names | Global convention; tooling, grep, and code review across teams assume ASCII English identifiers |
| Artifact IDs: `REQ-3`, `Q2`, `A1`, `TC-API-004`, `R-7` | IDs are the traceability keys tools parse — see the artifact contract (`${CLAUDE_PLUGIN_ROOT}/skills/run-qa-pipeline/references/artifact-contract.md`) |
| Artifact file names and the section headings/field labels of the templates | Machine-checkable contract (the checker also accepts the Russian labels listed in the artifact contract) |
| Framework keywords, CLI commands, config keys, HTTP methods, status codes | They are code, not prose |
| Tags/markers: `@smoke`, `@p0`, `pytest.mark.api` | Used for filtering in CI |

A pytest function is therefore `def test_rejects_expired_code_with_422():` even in a
Russian run, with the Russian sentence in its docstring; a Playwright test is
`test('TC-E2E-002: истёкший промокод показывает ошибку и не меняет сумму', …)`.

## 2. Readability standard — test cases

Grounded in ISO/IEC/IEEE 29119-3 test-case documentation and ISTQB practice. A case
passes this bar when a mid-level tester who has never seen the feature can execute it
and two such testers would always agree on pass/fail.

1. **One behavior per case.** The title names that behavior and its expected outcome:
   "Expired code is rejected and the total is unchanged" — not "Promo code check".
2. **Title pattern:** `<condition / input> → <expected result>` or a plain sentence
   stating the rule. No "Verify that…", "Check…", "Test of…" prefixes — they carry no
   information.
3. **Concrete test data.** `code = "SPRING10", cart total = 1000.00 ₽` — never "a valid
   code", "some amount". Boundary cases name the exact boundary value.
4. **Steps are imperative, atomic, numbered**, one user or system action each, written
   from the actor's point of view ("Enter `SPRING10` in the promo field").
5. **Every expected result is observable and specific**: a number, a state, an exact
   message, a status code. "Works correctly", "displayed properly", "no errors" are
   rejected by the linter in `test-case-management`.
6. **Preconditions state system state, not actions** ("User is logged in; cart contains
   1 item priced 1000.00"). Setup actions belong in steps or in test data.
7. **No hidden dependencies between cases.** Each case sets up what it needs.
8. **Consistent vocabulary.** Use the spec's own terms (see the spec-gap-analysis
   terminology check); never introduce a synonym for an existing domain term.

## 3. Readability standard — autotest code

Grounded in widely adopted public guidance: the Google style guides, PEP 8 and the
pytest docs, the Playwright "Best Practices" page, Testing Library's guiding principles,
and xUnit Test Patterns (Meszaros). Where the target repository has its own established
style, **its linter/formatter config wins** — match it; this list is the floor, not a
competing style.

1. **The test name states the behavior and the expected result.** Pattern:
   `<unit/feature> <does what> when <condition>` or the case title prefixed with the TC
   ID. `test_apply_discount_returns_original_total_when_code_expired`, not
   `test_discount_2`.
2. **Arrange – Act – Assert (Given – When – Then)**, visually separated by a blank line
   (or `test.step()` blocks in Playwright). One Act per test.
3. **One behavior per test.** Several `expect`s are fine when they describe one outcome;
   two unrelated outcomes are two tests.
4. **No logic in tests** — no `if`, loops computing expected values, or try/except that
   swallow failures. Parametrize instead (`pytest.mark.parametrize`, `test.each`,
   Playwright loops over a data table with the case ID in each title).
5. **No magic values.** Test data comes from named constants, builders, or fixtures whose
   names explain intent (`EXPIRED_CODE`, `cartWithSingleItem(1000)`).
6. **Assertions say what failed.** Prefer framework matchers that print expected vs.
   actual; add a message when the matcher can't (`assert total == 900, "10% discount
   must apply to 1000"`).
7. **Locators and helpers are user-facing and named.** Prefer role/label locators;
   any reusable locator or helper gets a name that says what it targets.
8. **Comments explain *why*, not *what*.** The code shows what; a comment justifies a
   non-obvious wait, a workaround, or the business rule behind an expected value.
   Every test carries its TC ID (in the title or a tag) so a failure traces back to the
   case and requirement without opening the plan.
9. **Deterministic.** No sleeps, no dependence on test order, current date, or shared
   mutable state; freeze time and seed randomness.
10. **File header (new suites only):** one comment block naming the task ID / spec the
    cases came from and where the cases live (`docs/qa/<task-id>/test-cases-api.md`).

### Example — the same test in both output languages

```ts
// en
test('TC-API-004: expired code is rejected with 422 and total is unchanged', async ({ request }) => {
  // Arrange
  const cart = await createCart(request, { items: [{ sku: 'MUG-01', price: 1000 }] });

  // Act
  const response = await applyPromo(request, cart.id, EXPIRED_CODE);

  // Assert
  expect(response.status()).toBe(422);
  expect((await getCart(request, cart.id)).total).toBe(1000);
});

// ru — identifiers stay English, the title and comments follow the output language
test('TC-API-004: истёкший промокод отклоняется с 422, сумма не меняется', async ({ request }) => {
  // Подготовка: корзина с одним товаром за 1000
  const cart = await createCart(request, { items: [{ sku: 'MUG-01', price: 1000 }] });

  // Действие
  const response = await applyPromo(request, cart.id, EXPIRED_CODE);

  // Проверка: код отклонён, сумма корзины не изменилась
  expect(response.status()).toBe(422);
  expect((await getCart(request, cart.id)).total).toBe(1000);
});
```

## Anti-Patterns

- **Mixed-language artifacts** — half the cases in English, half in Russian, or Russian
  identifiers in code. Pick once, record it, apply everywhere.
- **Transliterated identifiers** (`proverka_promokoda`) — use English identifiers and put
  the Russian in the title/docstring.
- **"Readable" as an excuse for verbosity** — readable means the next reader understands
  the intent in seconds, not that every line has a comment.
- **Overriding the repo's linter** because this list says otherwise. The repo's
  enforced style wins; this skill fills gaps where there is none.

## Done When

- The output language is recorded in the task file and every artifact of the run uses it.
- No identifier, ID, file name, or framework keyword is translated.
- Every test case meets section 2; every autotest meets section 3 or the repo's own
  enforced style where that is stricter.
- `qa-doc-reviewer` has a Readability line in its report (findings or "meets standard").

## Related Skills

- **qa-project-context** — stores the project-level `Output language`.
- **test-case-management** — case anatomy and the ambiguous-step linter that enforces
  section 2 mechanically.
- **unit-testing**, **api-testing**, **playwright-automation** — apply section 3 per
  pyramid level.
- **ai-qa-review** — the deeper test-smell review; readability smells overlap section 3.
- **run-qa-pipeline** — resolves the language at run start and passes it to every stage.
