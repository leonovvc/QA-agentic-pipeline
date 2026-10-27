---
name: stack-detection-for-autotests
description: >-
  Detect a target repository's language, existing test frameworks, directory
  conventions, and CI setup before generating a single autotest, so new tests extend
  the existing suite instead of creating a second, incompatible one. Produces a short
  stack profile consumed by playwright-automation, api-testing, and unit-testing. Use
  when: "what test framework does this repo use," "where should new tests go,"
  "detect the test stack," "set up autotests for this project" (as the first step).
  Not for: writing the tests themselves once the stack is known — use
  playwright-automation, api-testing, or unit-testing. Not for: allocating which cases
  go to which level — use test-pyramid-strategy.
  Related: test-pyramid-strategy, playwright-automation, api-testing, unit-testing,
  qa-project-context.
license: MIT
metadata:
  author: qa-agentic-pipeline
  version: "1.1"
  category: automation
---

<objective>
Generating Playwright tests into a repo that already has a mature Cypress suite doesn't add coverage, it adds a second test runner nobody asked for. This skill runs before any autotest is written: it establishes what already exists so new tests are additions to one coherent suite, not a competing one.
</objective>

## Discovery Questions

Check `.agents/qa-project-context.md` first — a filled-in Tech Stack / Test Stack section answers most of this without scanning; skip straight to **Decision Table** if so.

1. **Is there a project root to scan, or is this a greenfield/empty repo?** A truly empty repo skips detection and goes straight to the defaults in the Decision Table.
2. **Is more than one language/framework present (monorepo, separate frontend/backend)?** Produce one stack profile per distinguishable test surface, not one blended guess.

## Detection Procedure

1. **Language & package manifest** — look for `package.json` (Node/JS/TS), `requirements.txt`/`pyproject.toml`/`Pipfile` (Python), `go.mod` (Go), `pom.xml`/`build.gradle` (Java/Kotlin), `Gemfile` (Ruby), `composer.json` (PHP). More than one present confirms a polyglot repo.
2. **Existing test frameworks & config** — search for `playwright.config.*`, `cypress.config.*`, `jest.config.*`/`vitest.config.*`, `pytest.ini`/`setup.cfg`/`pyproject.toml [tool.pytest]`, `phpunit.xml`, and existing test directories (`tests/`, `test/`, `__tests__/`, `spec/`, `e2e/`). Note naming conventions actually used (`*.spec.ts` vs `*.test.ts`, `test_*.py` vs `*_test.py`).
3. **CI configuration** — check `.github/workflows/`, `.gitlab-ci.yml`, or equivalent for what test commands already run in CI; a framework installed but never invoked in CI is a weaker signal than one wired into the pipeline.
4. **Stated conventions** — check `README.md`/`CONTRIBUTING.md` for an explicit "how to run tests" or "how to write tests" section; stated conventions override inference from file scanning when they conflict.
5. **API surface, if relevant** — for API-level tests, identify the API style (REST/GraphQL/gRPC) and whether an OpenAPI/GraphQL schema exists to test against directly.

## Decision Table

| What's found | What to do |
|---|---|
| Existing Playwright/Cypress config + test directory | Extend it: same directory, same naming convention, same page-object/fixture pattern already in use |
| Existing unit framework (Jest/Vitest/pytest/etc.) | Use it for all new unit-level cases; do not introduce a second unit framework |
| Test infra exists but is inconsistent (two different patterns in the same directory) | Follow the more recently modified / more prevalent pattern; note the inconsistency in the stack profile rather than picking arbitrarily |
| No E2E framework, but the project is a web app with user-facing flows | Default to Playwright (current default per `playwright-automation`) |
| No API test setup, but the project exposes REST/GraphQL endpoints | Default per `api-testing` — lightweight framework matching the backend language (e.g., the language's native HTTP test client) rather than introducing an unrelated stack |
| No test infrastructure at all | Propose a minimal scaffold (one framework per level, matching the app's language) rather than a full enterprise setup — one framework per level, smallest config that runs; do not over-engineer for a project with no existing testing culture |
| CI exists but doesn't run the detected framework | Flag this explicitly — new tests that don't run in CI provide false confidence |

## Output Contract

The profile is written as the `## Stack Profile` section of `autotest-summary.md` (artifact contract), one sub-block per test surface:

```markdown
## Stack Profile — <repo/module name>

## Language(s)
...

## Unit Test Framework
<framework, config location, directory, naming convention, or "none detected — see recommendation">

## API Test Approach
<framework/library, or "none detected — see recommendation">

## E2E Framework
<framework, config location, directory, page-object pattern if any, or "none detected — see recommendation">

## How to Run
<the exact commands for each level, as the repo itself runs them (package.json scripts, Makefile, tox/nox, CI job)>

## CI Integration
<what runs today, what's missing>

## Recommendation *(only if gaps found)*
<minimal addition needed, matching existing conventions>
```

This profile heads every `autotest-summary.md` and is what `qa-doc-review` checks new tests against for consistency.

## Anti-Patterns

- **Defaulting to Playwright/Jest without checking.** The stated defaults in this skill are fallbacks for when nothing exists — always check first.
- **Creating a second test directory "to keep the new tests separate."** Fragments the suite and doubles CI configuration for no benefit; extend the existing one.
- **Ignoring CI wiring.** A passing local test that never runs in CI is not coverage the team can rely on.
- **Over-scaffolding a project with no test culture.** Proposing a full contract-testing + visual-regression + mutation-testing setup for a repo with zero existing tests creates a wall nobody climbs — start with the minimal level that matches the feature being tested now.

## Done When

- A stack profile exists for every distinguishable test surface in the repo, including the exact commands to run each level.
- Every "none detected" line has a stated, justified default rather than being left blank.
- Any inconsistency in existing test patterns is noted, not silently picked around.

## Related Skills

- **test-pyramid-strategy** — consumes this profile's current-shape data when sanity-checking a new allocation.
- **playwright-automation**, **api-testing**, **unit-testing** — the authoring playbooks per level once the stack is known.
- **qa-project-context** — the faster path when the profile is already documented there.
