# QA Project Context

<!-- Copy to .agents/qa-project-context.md in the target repository and replace every
     [bracketed] value. Write "None" / "Not yet" where something does not exist —
     never leave a bracket behind. -->

## Product
- **Name:** [product name]
- **What it does:** [one sentence]
- **Type:** [SaaS / e-commerce / mobile app / API service / internal tool]
- **URLs:** production [url], staging [url], development [url]
- **Key user flows (5–10, specific and testable):**
  1. [Buyer searches, adds to cart, pays by card, receives confirmation email]

## Tech Stack
- **Frontend:** [framework + language]
- **Backend:** [framework + language + API style]
- **Database / cache:** [engine]
- **Hosting / CDN / monitoring:** [providers]

## Test Stack
### E2E / Integration
- **Framework:** [name + version, or "None selected yet"]
- **Config location:** [path]
- **Test directory:** [path]
### Unit / Component
- **Framework:** [name + version, or "None selected yet"]
- **Test directory:** [path]
### API
- **Framework:** [name, or "None selected yet"]

## CI/CD
- **Platform:** [GitHub Actions / GitLab CI / Jenkins / …]
- **When tests run:** [every push / PR / nightly]
- **What blocks a deploy:** [suites, thresholds]
- **Artifacts kept:** [reports, traces, coverage]

## Environments
- [name] — [url] — [how it differs from production]

## Quality Goals
- **Unit coverage:** [N% on business logic, measured by …]
- **Flake rate:** [<2% over 30 days]
- **Suite duration:** [unit < N min, E2E < N min]

## Risk Areas
| Area | Risk Level | Business Impact | Notes |
|---|---|---|---|
| [Payments] | [Critical] | [Lost revenue] | [Known edge cases with partial refunds] |

## Team
- **QA engineers:** [N, specializations]
- **Dev:QA ratio:** [N:1 or "solo"]
- **Methodology:** [Scrum / Kanban / …]

## Conventions
- **Test file naming:** [*.spec.ts / test_*.py]
- **Selectors:** [getByRole first, data-testid fallback]
- **Test data:** [factories / fixtures / API seeding]
- **Branching / PR rules:** [trunk-based, PR review required]

## QA Pipeline
- **Output language:** [en | ru]
- **Docs location:** [docs/qa/]
- **Test-case system:** [none | TestRail / Xray / Zephyr Scale / Qase — project, root section]
- **Definition of Ready:** [link or list, or "none"]
- **E2E budget:** [max N% of automated cases; ~N s per E2E test in CI]
- **Security lens:** [auto | always | off]
- **Spec owners:** [who answers Track B questions]
