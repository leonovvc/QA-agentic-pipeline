---
name: qa-project-context
description: >-
  Create and maintain .agents/qa-project-context.md — the one file every stage of the
  QA pipeline reads first: product and key flows, tech and test stack, CI/CD,
  environments, quality goals, risk areas, team, conventions, and the QA Pipeline
  settings (output language EN/RU, docs location, test-case system, Definition of Ready
  for specs, E2E budget, security lens). Use when: "set up QA context," "configure the
  QA pipeline," "set the output language," "initialize QA for this repo," or when
  run-qa-pipeline reports the context file is missing. Not for: analysing a specific
  spec — use spec-gap-analysis; not for running the pipeline — use run-qa-pipeline.
  Related: run-qa-pipeline, qa-output-standards, risk-based-testing,
  stack-detection-for-autotests, spec-gap-analysis.
license: MIT
metadata:
  author: qa-agentic-pipeline
  adapted_from: petrkindlmann/qa-skills@qa-project-context (MIT, Petr Kindlmann)
  version: "3.0"
  category: foundation
---

<objective>
This skill writes the single file every other QA skill reads. Without it, each skill
re-asks "what framework? what CI? where do tests live?" from scratch and gives generic
advice. It produces `.agents/qa-project-context.md` in the project root, capturing product,
tech stack, test stack, CI/CD, environments, quality goals, risk areas, team, and
conventions — with no `[bracketed placeholders]` left behind.
</objective>

## Role in the QA pipeline

This file is optional — `run-qa-pipeline` runs on defaults without it and says so in the
Human Checkpoint — but every stage gets sharper when it exists:

| Section | Read by | Effect |
|---|---|---|
| QA Pipeline | `run-qa-pipeline`, all four agents | Output language, docs location, test-case system, E2E budget, security lens |
| QA Pipeline → Definition of Ready | `spec-analyst` (`spec-gap-analysis`) | The bar a spec is checked against instead of the generic checklist |
| Product → key flows, Risk Areas | `qa-doc-writer` (`risk-based-testing`) | Impact scores in the plan's Risk Assessment start from these, not from guesses |
| Test Stack, Conventions | `autotest-builder` (`stack-detection-for-autotests`) | Confirms detection; selector and naming strategy for generated tests |
| Quality Goals | `qa-doc-writer` (`test-planning`) | Exit criteria in `test-plan.md` |
| CI/CD, Environments | `autotest-builder` | Which tests can actually run locally vs. only in CI |

Fill those sections well and every stage of the pipeline gets sharper for free.

## Discovery Questions

First, check whether `.agents/qa-project-context.md` already exists — if it does, read it and
skip every section already filled (no `[brackets]`). Then scan the repo for config files (see
Codebase Detection) and present detected values for confirmation rather than asking blind.
Walk the remaining questions **section by section**, never all at once.

### Product
- What is the product called, and what does it do in one sentence?
- What type is it? (SaaS, e-commerce, media, mobile app, API service, internal tool) — changes which flows matter.
- What are the production, staging, and development URLs?
- What are the 5–10 most critical user journeys? ("If this breaks, we get paged at 2am.") This list drives every other skill's coverage priorities.

### Tech Stack
- Frontend framework and language? Backend framework, language, and API style (REST, GraphQL, tRPC, gRPC)?
- Database, cache layer, ORM? Hosting, CDN, monitoring?
- Monorepo? If yes, list each app separately (see Monorepo note) — sharding and detection differ.

### Test Stack
- E2E tests today? Framework, config location, test directory. Same for unit, API, visual, performance.
- If a framework is detected from config files, populate Test Stack with its name + version + path — don't re-ask.
- Zero test infrastructure? That's a valid answer; record "None selected yet" and note a default (see Core Principle 3).

### CI/CD
- Platform? When do tests run (every push, PR only, nightly, manual)? Sharding/parallelism?
- What blocks a deploy, and what artifacts are saved (screenshots, reports, coverage)?

### Environments
- How many environments, with URLs? How close is staging to production (infra, data shape, third-party integrations)?
- Mock services or real APIs in development? — environment parity drives test reliability.

### Quality Goals
- Coverage targets today? Flake tolerance? Suite-duration budgets? Metrics tracked or wanted?
- No targets yet? Suggest realistic ones by maturity (see Quality Goals section).

### Risk Areas
- Which parts cause the most production incidents? Which integrations are flakiest (payment, email, third-party APIs)?
- Where is churn high and coverage low? Score everything with Impact × Likelihood (see Risk Areas section).

### Team
- How many QA engineers, and their specializations? Developer-to-QA ratio? Methodology (Scrum, Kanban, Shape Up)?
- When does QA engage (shift-left during spec, or after dev)? — sets the automation ownership model.

### QA Pipeline
- **Output language** for test cases, reports, test titles and code comments: English (`en`)
  or Russian (`ru`)? (See `qa-output-standards` — identifiers stay English either way.)
- Where should pipeline docs live? Default `docs/qa/`.
- Is there a test-case management system (TestRail, Xray, Zephyr Scale, Qase)? Project and
  root section/folder the pipeline should file cases under?
- Does the team have a Definition of Ready / spec template for incoming specs? Paste it or link it.
- E2E budget: the maximum share of automated cases at E2E level (default 20%) and how long
  one E2E test takes in CI here.
- Security lens: `auto` (default — apply the OWASP spec check when the feature touches auth,
  user input, payments, personal data, file upload, or external integrations), `always`, or `off`.
- Who owns specs — who answers Track B questions (analyst, PM, tech lead)?

### Conventions
- Test file naming pattern? Co-located or separate? Branching strategy and PR requirements?
- Selector strategy for E2E? Test-data strategy (factories, fixtures, seeded DB, API-per-test)?

## Core Principles

1. **One file is the source of truth for the whole pipeline.** Every stage reads
   `.agents/qa-project-context.md` first. Duplicating its facts into other docs guarantees
   drift — keep stack, goals, and risks here and let other skills reference them.

2. **Capture the real state, not the aspiration.** If there are no E2E tests, write "None
   selected yet," not a wish. Downstream skills route on what's true: a missing framework
   triggers a setup suggestion; a fake one sends them building on sand.

3. **Detect before you ask; recommend a default only when there's nothing to detect.**
   Read `package.json` and config files first and confirm what you find (the same detection
   table `stack-detection-for-autotests` uses). Tool *recommendations* belong to the
   specialized skills — the one exception is a project with zero test infrastructure, where
   you note **Playwright** (E2E) and **Vitest** (unit) — or **pytest** for a Python project —
   as defaults in the Test Stack and hand off to `playwright-automation` / `unit-testing`. This is the single
   carve-out to the "no recommendations" rule; everywhere else, just record.

4. **Risk Areas is the highest-leverage section — never skip it.** It is the direct input to
   the Risk Assessment that `risk-based-testing` builds in every test plan. Push for at least
   3–4 entries scored by impact and likelihood even when the user says "everything's fine."

## Codebase Detection

Scan for these before asking about the stack. Present detected values for confirmation; when a
test config is found, write the framework name into Test Stack rather than re-asking.

| File | Indicates |
|------|-----------|
| `package.json` | Node.js project — check `dependencies` for the framework |
| `next.config.*` | Next.js |
| `nuxt.config.*` | Nuxt/Vue |
| `angular.json` | Angular |
| `astro.config.*` | Astro |
| `react-router.config.ts` | React Router 7 / Remix |
| `requirements.txt` / `pyproject.toml` | Python project |
| `go.mod` | Go project |
| `playwright.config.*` | Playwright is set up → populate Test Stack E2E |
| `cypress.config.*` | Cypress is set up → populate Test Stack E2E |
| `vitest.config.*` / `jest.config.*` | Unit test framework → populate Test Stack Unit |
| `.github/workflows/` | GitHub Actions CI |
| `.gitlab-ci.yml` | GitLab CI |
| `Jenkinsfile` | Jenkins |
| `docker-compose.*` | Docker-based environments |
| `wrangler.*` | Cloudflare Workers |
| `vercel.json` | Vercel hosting |
| `bun.lock` / `bun.lockb` | Bun runtime |
| `pnpm-workspace.yaml` / `turbo.json` / `nx.json` | Monorepo — handle per the Monorepo note |
| `src-tauri/tauri.conf.json` | Tauri desktop app |
| `.claude/` | Project uses Claude Code skills/agents |
| `.claude-plugin/plugin.json` | Project ships a Claude Code plugin |
| `AGENTS.md` | Codex / multi-agent workflow conventions |

## Workflow: Creating the Context File

1. **Check for existing context.** Look for `.agents/qa-project-context.md` in the project root.
2. **If absent:** create `.agents/` if needed, scaffold the section structure, run the Discovery
   Questions starting with Product, and write the file once filled.
3. **If present with placeholders:** read it, list which sections are complete vs. unfilled, ask
   only about the unfilled sections, then update — preserve completed sections untouched.
4. **If present and complete:** summarize the current context, ask what changed (new tools, team
   changes, shifted goals), and update only the deltas.
5. **After completion:** confirm the file path, run Verification (below), and suggest the next
   step: with a spec in hand → `run-qa-pipeline`; no E2E framework yet → `playwright-automation`;
   no unit tests → `unit-testing`.

For two full filled-in files (SaaS and a multi-site publisher) plus the monorepo layout, see
`references/examples.md`. One short illustrative snippet:

```markdown
## Test Stack
### E2E / Integration
- **Framework:** Playwright 1.60
- **Config Location:** playwright.config.ts
- **Test Directory:** tests/e2e/
### Unit / Component
- **Framework:** None selected yet — Vitest recommended (see unit-testing)
```

## Section Guidance

What makes a good entry in each section. The blank template is
`references/template.md` — copy it to `.agents/qa-project-context.md` and fill it in.

**Product.** Key user flows must be specific and testable: "Buyer searches products, adds to
cart, checks out with Stripe, receives confirmation email" — not "user uses the app." This list
is what every test skill uses to prioritize. Aim for 5–10.

**Tech Stack.** Record frontend, backend, database, hosting separately. Pin versions only when
they change the testing approach (App Router vs. Pages Router differ materially). Don't copy a
version just because an example shows one — read it from `package.json`.

**Test Stack.** For each tool: framework name + version, config location, test directory. No
infrastructure yet is valid — write "None selected yet" and the recommended default (Principle 3).

**Monorepo.** List each frontend app as its own Tech Stack and Test Stack entry; keep the
shared API/backend as one entry. Shard E2E **per app** (a change in `apps/admin` shouldn't run
`apps/storefront` E2E), and note in CI/CD which path filters gate which app's suite. Detection
hint: `turbo.json` / `pnpm-workspace.yaml` / `nx.json`. See `references/examples.md`.

**CI/CD.** Answer what other skills need: what blocks a deploy, how fast feedback is, what
evidence is preserved.

**Environments.** Note how staging diverges from production — a different DB engine in staging
means staging-green tests can still fail in prod.

**Quality Goals.** Concrete and measurable only. Pick starting targets by maturity:

| Maturity | Unit coverage | E2E | Flakiness | Suite duration |
|----------|--------------|-----|-----------|----------------|
| Early-stage startup | 60% on business logic | Top 5 critical flows | <2% | Unit <3 min, E2E <15 min |
| Growth-stage | 80% | All critical paths | <2% | Unit <3 min, E2E <15 min |
| Enterprise | 90%+ | Comprehensive + perf budgets | <1% | Unit <3 min, E2E <15 min |

Write them as numbers: "80% line coverage measured by Istanbul," "flake rate <2% over a rolling
30-day window," "full E2E under 15 min with 4 shards." Never "we want great quality."

**Risk Areas.** Use the table — columns Area, Risk Level, Business Impact, Notes — and score with
**Impact × Likelihood**:

- **Critical (test first):** high impact + high likelihood (payment flow with known edge cases).
- **Important:** high impact + low likelihood (auth — catastrophic if broken, rarely changes).
- **Monitor:** low impact + high likelihood (notification formatting — breaks often, low severity).
- **Backlog:** low impact + low likelihood (admin settings — stable, rarely used).

At least 3 entries, never vague ("everything breaks").

**Team.** Record actual headcount and the dev:QA ratio — it sets the automation ownership model:

| Dev:QA ratio | Ownership model |
|--------------|-----------------|
| Solo / zero QA (effectively infinite) | Devs own all tests. No manual regression suite; lean on low-barrier automation (Playwright + Vitest) and CI gates. QA "role" = strategy + critical-path E2E, done by the dev. |
| High (8:1+) | Developers write tests; QA focuses on strategy, critical-path automation, exploratory testing. |
| Balanced (4:1) | QA owns E2E, devs own unit, integration shared. |
| QA-heavy (<3:1) | Dedicated automation engineers, comprehensive regression suites, scheduled exploratory cadence. |

**QA Pipeline.** Short key-value lines the agents can read without interpretation:

```markdown
## QA Pipeline
- **Output language:** ru
- **Docs location:** docs/qa/
- **Test-case system:** TestRail — project "Shop", root section "Checkout"
- **Definition of Ready:** docs/process/definition-of-ready.md
- **E2E budget:** max 20% of automated cases; ~40 s per E2E test in CI
- **Security lens:** auto
- **Spec owners:** product analyst (Track B questions), backend lead (API contracts)
```

**Conventions.** Selector strategy especially — `playwright-automation` reads it to generate matching selectors. Default to `data-testid` for stability
(`data-testid="invoice-create-button"`, kebab-case). If the team prefers semantic/ARIA selectors
for accessibility-aware testing, record concrete tokens — `role="button"`, `role="heading"`,
`getByRole('link', { name: ... })` — and the tradeoff: ARIA roles double as a11y assertions and
survive markup churn, but are less stable than `data-testid` when copy or roles change, so pin a
`name`/`level` to keep them unambiguous.

## Anti-Patterns

### 1. Asking all questions at once
Dumping 30 questions is overwhelming and gets shallow answers. Walk section by section, Product first.

### 2. Leaving `[brackets]` in the final file
If the user has no answer, record the actual state ("None — no E2E framework selected yet"), not a
placeholder. Placeholders left in the file silently break every downstream skill that parses it.

### 3. Inventing information
Detect the stack from `package.json`, `requirements.txt`, or config files — then confirm with the
user before writing. Don't guess a database or hosting provider.

### 4. Skipping Risk Areas
The single most valuable section for downstream skills. Push for at least 3–4 scored entries even
when the user insists everything is fine.

### 5. Recommending tools beyond the zero-infra default
This skill records current state; tool selection belongs to `playwright-automation`,
`unit-testing`, and the other specialized skills. The *only* recommendation you make here is the
Playwright + Vitest default when there is no test infrastructure at all (Principle 3).

## Verification

Prove the produced file is complete, smallest check first. From the project root:

```bash
test -f .agents/qa-project-context.md \
  && ! grep -q '\[.*\]' .agents/qa-project-context.md \
  && echo "context complete: file exists, no placeholders"
```

Exit 0 with the message means the file exists and every `[bracketed placeholder]` is gone. A
non-zero exit means either the file is missing or placeholders remain — fix those before handing
off to the pipeline. Then eyeball that all ten section headers are present:

```bash
grep -c '^## ' .agents/qa-project-context.md   # expect >= 10
```

## Done When

- `.agents/qa-project-context.md` exists in the project root and `grep -q '\[.*\]'` returns
  non-zero (no bracketed placeholders remain).
- All ten sections are present: Product, Tech Stack, Test Stack, CI/CD, Environments, Quality
  Goals, Risk Areas, Team, Conventions, QA Pipeline.
- QA Pipeline states the Output language (`en` or `ru`) explicitly.
- Product lists at least 5 specific, testable key user flows (no "user uses the app").
- Test Stack names the actual frameworks + versions + paths in use, or states "None selected yet"
  with the recommended default noted.
- Risk Areas table has at least 3 entries scored by impact and business impact.
- Quality Goals are concrete numbers (coverage %, flake %, durations) — not aspirational prose.
- Team section shows actual headcount and the dev:QA ratio (or "solo").

## Related Skills

- **run-qa-pipeline** — reads this file first; runs on defaults when it is missing and
  recommends creating it in the Human Checkpoint.
- **qa-output-standards** — what the Output language setting controls, and what always
  stays English.
- **risk-based-testing** — turns Risk Areas and key flows into the Risk Assessment in each
  test plan.
- **stack-detection-for-autotests** — re-detects the stack per run; this file confirms it.
- **spec-gap-analysis** — checks specs against the Definition of Ready recorded here.
- **playwright-automation** / **unit-testing** — set up E2E / unit frameworks after the Test
  Stack section is filled; they read Conventions for selector and naming strategy.

## Reference Files (in `references/`)

- **template.md** — the blank file with all ten sections, ready to copy.
- **examples.md** — two complete filled-in context files (SaaS and a multi-site publisher) plus
  the monorepo Tech/Test Stack layout.
