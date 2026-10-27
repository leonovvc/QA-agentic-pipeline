---
name: qa-doc-review
description: >-
  Independently review a test plan and test case set for spec traceability, correct
  application of test design techniques, correct pyramid allocation, duplication, and
  case quality — then produce a severity-ranked findings report that explicitly
  separates ordinary defects from genuinely disputed/ambiguous calls that need a human
  decision. Use when: "review this test plan," "review these test cases," "QA
  documentation review," "is this test coverage complete," "audit the test plan before
  automation." Not for: reviewing already-written automated test CODE for smells — use
  ai-qa-review (this skill covers that too when autotests exist, by invoking it as a
  sub-check). Not for: writing the test plan itself — use test-planning.
  Related: spec-gap-analysis, test-design-techniques, test-pyramid-strategy,
  risk-based-testing, test-case-management, qa-output-standards, ai-qa-review,
  run-qa-pipeline.
license: MIT
metadata:
  author: qa-agentic-pipeline
  version: "2.0"
  category: ai-qa
---

<objective>
A review that re-reads the test-plan author's own summary of the spec will always agree with itself. This skill re-derives expected coverage from the *original* spec and the `spec-gap-analysis` report independently, then diffs it against what was actually produced — the only way a review catches "the writer missed a whole acceptance criterion," not just "the writer's cases look internally consistent."
</objective>

## Discovery Questions

Check `.agents/qa-project-context.md` first. Read the artifacts from `docs/qa/<task-id>/`; write the report in the run's output language with the IDs and headings from the artifact contract (`${CLAUDE_PLUGIN_ROOT}/skills/run-qa-pipeline/references/artifact-contract.md`).

1. **What's in scope for this review?** Documentation only (test plan + test cases), or also the resulting autotests? If autotests exist, this skill's code-quality dimension delegates to `ai-qa-review` rather than duplicating its smell taxonomy.
2. **What's the source of truth?** Always the original spec plus `spec-gap-analysis`'s two artifacts (`spec-gap-report.md` and `spec-annotated.md`) — never the test plan's own restated summary of requirements. The annotated copy is the fast way to walk findings in spec order; the report is the structured record.
3. **Is this a full audit or a targeted re-review after fixes?** A targeted re-review only re-checks previously flagged items plus anything touched since, not the whole document again.

## Core Principles

1. **Review against the spec, not against the writer's account of the spec.** Re-derive the list of acceptance criteria from `spec-source.md` independently before opening the test plan, then compare it with Stage 1's Requirements Inventory too — a requirement the spec states but the inventory missed is a finding against Stage 1 (cite the spec location), and it is still uncovered.
2. **Traceability, not case count, measures coverage.** 80 test cases covering 4 of 6 acceptance criteria is worse than 20 cases covering 6 of 6 — count requirements-to-test links, not lines.
3. **A technique applied wrong is worse than a technique skipped.** A boundary-value section that tests `min` and `max` but not `min-1`/`max+1` looks like coverage while providing almost none of it — call these out by name, don't just note "coverage looks reasonable."
4. **Surface disagreement, don't silently resolve it.** When the reviewer's own judgment differs from the writer's on a genuinely close call (e.g., "is this edge case in scope," "should this be E2E or integration"), that is a **Disputed** item for the human checkpoint — this skill does not have the authority to overrule Agent-2 or Agent-3 on a judgment call, only to flag defects and disagreements clearly.
5. **Every finding needs a citation.** A spec location, a test-case ID, or an autotest file path — never a finding stated only as a general impression.

## Review Checklist

| Dimension | Check |
|---|---|
| Traceability | Every `REQ-<n>` (and every requirement you re-derived that the inventory missed) maps to at least one test case or is explicitly out of scope / blocked by a named Q; every `A<n>` a case depends on is listed in its Traces |
| Risk depth | P0/P1 requirements received the depth `risk-based-testing` prescribes for their zone (all partitions and boundaries, error paths, the required levels) |
| Security lens | If the spec has a security trigger, `## Security Lens` exists in the gap report and every applicable OWASP row produced a Q, an A, or a security negative case — and those cases are not all E2E |
| Technique correctness | For each technique named in the plan (`test-design-techniques`), verify it was applied correctly — right classes, boundaries actually at the boundary, pairwise combinations actually covering pairs |
| Pyramid allocation | Cross-check each case's assigned level (`test-pyramid-strategy`) against its actual purpose; flag misallocated cases (logic tested only at E2E, or a contract check missing entirely) |
| Duplication / overlap | Cases asserting the same thing at the same level with no added value |
| Negative/error-path coverage | Every documented failure mode from the spec has a corresponding negative case |
| Case quality | Each case has all eight fields of the pipeline format; the `test-case-management` lint checklist finds no ambiguous step or non-observable expected result |
| Readability & language | Cases and autotests meet `qa-output-standards` §2–3 and are written in the run's output language; identifiers and IDs are untranslated |
| Case location | Cases are where `test-plan.md` says they are — split into the right per-pyramid-level file, or filed under the correct existing section/suite in the test-case system — not scattered or duplicated across both |
| Autotest alignment *(conditional — only if autotests exist)* | Every non-`MAN` case appears once in `autotest-summary.md`; delegate code-level checks (TC ID, oracle match, honest status, smells) to `ai-qa-review` and use its severity mapping |

## Severity Scale

- **Blocking** — a required acceptance criterion has no corresponding test case, or a stated technique was applied incorrectly enough to miss real defects.
- **Major** — meaningful gap or misallocation that should be fixed before this plan is considered final, but doesn't block starting automation.
- **Minor** — quality/clarity issue (weak case description, minor duplication) worth fixing but not blocking.
- **Disputed — needs human decision** — a genuine judgment call where the reviewer's own view differs from the writer's and reasonable QA engineers could land either way (scope boundaries, risk-acceptance trade-offs, priority calls). Never downgrade a Disputed item to a severity level to force a resolution — pass it through as-is.

## Output Contract

`docs/qa/<task-id>/qa-review-report.md`:

```markdown
# QA Review — <feature/spec name>

## Traceability Summary
<N of M requirements covered>
| REQ | Verdict | Cases |
|---|---|---|
| REQ-1 | covered | TC-UNIT-001…004, TC-E2E-001 |
| REQ-5 | NOT covered | — (see R-1) |
| REQ-7 | blocked by Q2 | — |

## Findings
### Blocking
**R-1** [Blocking] REQ-5, spec §3.2 — no case covers the "code already used" rule → add an API case for the used-code partition.
### Major
...
### Minor
...

## Disputed — Needs Human Decision
1. **<topic>** — Writer: <position and reasoning>. Reviewer: <position and reasoning>. At stake: <what each choice risks>.
(or "None")

## Readability
<meets qa-output-standards / list of R-n findings>

## Autotest Review
<ai-qa-review result: per-file smell table, sample re-run results, mutation score if available>
```

Every finding has exactly one severity, an `R-<n>` ID, at least one citation (REQ, Q/A, TC ID, or file:line), and a fix direction.

## Anti-Patterns

- **Grading the plan against its own table of contents.** Confirms internal consistency, misses whole missing sections.
- **Rubber-stamping because the plan "looks thorough."** Length and formatting quality are not proxies for traceability — always do the independent re-derivation.
- **Resolving a Disputed item unilaterally to keep the pipeline moving.** Defeats the purpose of the human checkpoint; if it's genuinely close, it goes to the human, full stop.
- **Re-litigating settled, non-ambiguous items as Disputed.** Reserve Disputed for real judgment calls — an objectively missing acceptance criterion is a Blocking finding, not a dispute.

## Done When

- Every REQ — plus any requirement the reviewer re-derived that Stage 1 missed — has a traceability verdict (covered / not covered / blocked by Q<n>).
- Every finding has a severity and a citation.
- The Disputed section, if non-empty, states both positions neutrally.
- Risk depth, security lens, readability, and (when autotests exist) autotest alignment each have a verdict.
- The report is saved as `docs/qa/<task-id>/qa-review-report.md` and is what `run-qa-pipeline` assembles into the final human checkpoint.

## Related Skills

- **spec-gap-analysis** — re-read as the independent source of truth, not the test plan's summary of it.
- **test-design-techniques** / **test-pyramid-strategy** — the standards this review checks technique and allocation against.
- **ai-qa-review** — delegate to this for autotest code-level checks (traceability, oracle match, smells) and use its severity mapping.
- **risk-based-testing** — the depth each priority zone requires.
- **test-case-management** — the lint checklist for case quality.
- **qa-output-standards** — the readability and language bar.
- **run-qa-pipeline** — consumes this report as the final stage before the human checkpoint.
