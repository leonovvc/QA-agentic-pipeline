---
name: spec-gap-analysis
description: >-
  Parse an incoming technical specification (ТЗ) — URL, pasted text, or PDF — and
  produce two artifacts: a structured findings report (a numbered Requirements Inventory
  REQ-1…n, gaps, contradictions, untestable requirements, missing acceptance criteria and
  edge cases, a security lens, open questions sorted into "ask the operator now" vs
  "route to the analyst/business owner") plus a copy of the spec with each finding marked
  inline at its exact location. Produces reports ABOUT the spec, never a rewritten spec.
  Use when: "check this ТЗ," "analyze this spec for gaps," "is this spec ready for test
  design," "find contradictions in these requirements," "testability review of the
  spec." Not for: writing the test plan or cases — use test-planning and
  test-design-techniques; not for reviewing QA documentation — use qa-doc-review.
  Related: qa-project-context, security-testing, risk-based-testing,
  test-design-techniques, qa-doc-review, qa-output-standards.
license: MIT
metadata:
  author: qa-agentic-pipeline
  version: "2.0"
  category: foundation
---

<objective>
A test plan built on an unread gap in the spec inherits that gap silently — every downstream test case looks complete while testing the wrong thing, or nothing, at the ambiguous point. This skill is the first gate of the pipeline: it reads the spec adversarially, for what it does NOT say as much as for what it does, and hands downstream stages a report they can build on instead of the raw spec itself.
</objective>

## Discovery Questions

Check `.agents/qa-project-context.md` first — its QA Pipeline section may state the org's Definition of Ready for a spec (the bar this analysis checks against), the Security lens setting, and who owns specs (the addressee for Track B). Write the report in the run's output language (`qa-output-standards`); IDs and section headings follow the artifact contract (`${CLAUDE_PLUGIN_ROOT}/skills/run-qa-pipeline/references/artifact-contract.md`).

1. **What form is the input in?** URL, pasted text, or PDF — see **Input Handling** below; each has a different failure mode to watch for.
2. **Is there a Definition of Ready / spec template the org uses?** If yes, check against it explicitly instead of a generic checklist.
3. **Who can actually answer open questions?** This skill cannot ask the business anything — it can only surface the question. Note in the report who the likely owner is (PM, backend lead, design) where inferable. Every question also gets sorted into one of two tracks — see **Two Question Tracks** below.
4. **Is a partial/draft spec acceptable to proceed on, or must gaps block the pipeline?** Default: proceed and mark clearly which downstream test design is built on a stated assumption rather than a confirmed requirement — a full stop is reserved for a spec too incomplete to derive any acceptance criteria from at all.

## Two Question Tracks

A question that comes out of this analysis needs a different next step depending on who can actually answer it — conflating the two makes both worse (the person running the pipeline gets stuck waiting on the business for something they could decide themselves, or the business gets flooded with operational questions that were never theirs to answer). Sort every open question into exactly one track:

- **Track A — ask the operator now.** Anything the pipeline needs decided to keep moving, and that the person running the pipeline can plausibly answer themselves (scope for this pass, which of two reasonable assumptions to build on, whether a partial spec is acceptable to proceed). Ask these directly in the conversation as they come up, don't just bury them in the report.
- **Track B — route to the analyst/business owner.** Product-intent questions only the spec's author or business owner can resolve (what should happen in an unspecified case, which of two conflicting stated rules is correct, a missing business rule). These cannot be answered by guessing harder — write them as a ready-to-forward list the operator can paste to whoever owns the spec, one question per line, self-contained (no "see above" — each question makes sense read in isolation).

Order Track B by the risk of the requirement each question blocks (`risk-based-testing`: money, access, personal data first) — the spec owner may answer only the top few.

Both tracks still appear in the **Open Questions** section of the report (that section is the durable record); Track A questions are *additionally* asked in-conversation as soon as they're identified rather than only surfacing at the end.

## Core Principles

1. **Read for what's not said.** A spec that describes the happy path in detail and says nothing about errors has an implicit gap at every error path, even though nothing is technically "wrong" in the text.
2. **Every finding cites its exact location.** "Section 3.2, second bullet: ambiguous" is checkable; "the auth section is unclear" is not. Quote or paraphrase the specific line.
3. **Distinguish a blocking gap from a note.** A blocking gap means no reasonable test case can be written until it's resolved (e.g., no stated valid range for a required numeric field). A note means the pipeline can proceed on a stated, reasonable assumption. Never let the two blur together in the output.
4. **Don't invent requirements — assume explicitly, out loud.** When proceeding past a gap, the report states the exact assumption made, so a human reviewing the final checkpoint sees it was a decision, not a fact.
5. **Testability is itself a check, not an afterthought.** A requirement like "the system should be fast" or "the UI should be intuitive" is a gap even if grammatically complete — flag anything without a measurable or objectively checkable acceptance criterion.

## Input Handling

- **URL:** fetch the page content. If it's a live app/prototype rather than a document, note that the "spec" is the live behavior itself, which changes the gap analysis (behavior can be observed, but *intent* still needs to be inferred — flag intent gaps distinctly from behavior gaps).
- **Pasted text:** use directly; if it's clearly a fragment (mid-sentence start/end, missing referenced sections like "see diagram above" with no diagram), flag the fragment itself as a completeness gap before analyzing content.
- **PDF:** extract text (and tables, if present) before analysis. If extraction quality is low (scanned/image-based PDF, garbled text), say so explicitly and give a confidence level for the whole analysis rather than silently analyzing corrupted text as if it were reliable.

## Requirements Inventory

Before hunting for gaps, list what the spec **does** require. Walk the spec in order and give every distinct, checkable obligation an ID `REQ-<n>`: one behavior per REQ (split "the code is applied and a confirmation is shown" into two), with its spec location, the requirement in the spec's own words, the acceptance criterion if one is stated ("none stated" otherwise), and whether it is testable as written (`yes`, `partly → Q<n>`, `no → Q<n>`).

This table is the backbone of the whole pipeline: Stage 2 traces every test case to a REQ, Stage 4 measures coverage against it, and the human sees "N of M requirements covered" instead of a guess. Two rules keep it honest:

- **Only what the spec says.** An implied requirement you would like the spec to have is a gap (a Q), not a REQ.
- **Never renumber.** Once Stage 2 has started, REQ IDs are frozen; a requirement discovered later gets the next free number.

## Analysis Checklist

Work through each dimension; not every spec will have findings in every category, but check all of them.

| Dimension | What to look for |
|---|---|
| Functional completeness | Every user-facing action mentioned has a stated outcome for both success and failure |
| Acceptance criteria | Each requirement has a criterion that is objectively checkable (a number, a state, a specific message) — not "should work correctly" |
| Edge cases | Empty/zero/null inputs, maximum values, concurrent actions, partial failures, network/timeout behavior — stated or silently assumed? |
| Non-functional requirements | Performance, security, accessibility, i18n/l10n, browser/device support — explicitly scoped in or silently absent (absence is a gap, not an exclusion, unless the spec explicitly excludes it) |
| Data & state model | Are entities, their required fields, and valid states/transitions clear enough to design state-transition or boundary cases against? |
| Integration & dependency points | Third-party services, other internal systems, feature flags — are their failure modes in scope? |
| Terminology | A glossary check: does the same term mean the same thing everywhere in the doc? Conflicting definitions are contradictions, not style issues |
| Internal consistency | Do two sections of the same spec state different rules for the same scenario? |
| Security (lens) | When the feature has a security trigger, run the OWASP spec questions from `security-testing` → Lens Mode; every unstated security behavior becomes a Q or an explicit A |

## Output Contract

This stage produces **two** artifacts, not one — the structured report (consumed by `qa-doc-writer` and `qa-doc-reviewer`) and an annotated copy of the spec text itself (for the human, and for whoever fields Track B questions) — plus `spec-source.md`, a verbatim snapshot of the spec as received (fetched/extracted text), so later stages and later sessions review against exactly what Stage 1 saw. All three go to `docs/qa/<task-id>/`.

**Numbering:** `Q<n>` is one sequence across Blocking Gaps, Contradictions, and Open Questions (Q1, Q2, … never restarting per section); `A<n>` is its own sequence. Each entry begins with its bold ID (`**Q3** — …`).

### 1. `spec-gap-report.md` — the structured report

```markdown
# Spec Gap Analysis — <feature/spec name>

## Source
<URL / "pasted text" / PDF filename, plus extraction confidence if PDF>

## Testability Score: <1-5>
<one line: what drives the score>

## Requirements Inventory
| ID | Spec location | Requirement | Acceptance criterion | Testable |
|---|---|---|---|---|
| REQ-1 | §2, bullet 1 | <in the spec's words> | <as stated, or "none stated"> | yes / partly → Q<n> / no → Q<n> |

## Blocking Gaps
<numbered list; each: spec location, what's missing, why it blocks test design,
marker ID (e.g. [Q3]) linking to spec-annotated.md>
(none, if none)

## Contradictions
<numbered list; each: the two conflicting statements with their locations,
marker ID linking to spec-annotated.md>
(none, if none)

## Open Questions
### Track A — for you, now
<numbered list; each: the question — ask these in-conversation as soon as they're
found, don't hold them for the end of the report>
(none, if none)

### Track B — for the analyst / spec owner
<numbered list; each: a self-contained, ready-to-forward question plus the likely
owner if inferable — written so the operator can paste this list to them as-is>
(none, if none)

## Assumptions Made to Proceed
<numbered list; each: the gap, the assumption chosen, and why it's the reasonable
default — this list is what qa-doc-reviewer re-checks against the original spec, and
what surfaces in the final human checkpoint if genuinely contestable>

## Security Lens
<applicable OWASP rows → the Q/A each produced; not-applicable rows with the reason;
or "Not applicable — no security triggers in this spec">

## Ready-for-Test-Design Checklist
- [ ] Every in-scope user action has a success and failure outcome
- [ ] Every acceptance criterion is objectively checkable
- [ ] Edge cases are addressed or explicitly out of scope
- [ ] No unresolved contradictions remain
```

### 2. `spec-annotated.md` — the spec, with every finding marked where it happens

A copy of the original spec text (or, for a URL/live app, the extracted/observed text) with an inline marker dropped at the exact point each Blocking Gap, Contradiction, or Open Question was found — reading the annotated copy top to bottom should surface every finding in the order it occurs in the spec, without needing to cross-reference the report:

```markdown
# <feature/spec name> — annotated

> Source: <URL / "pasted text" / PDF filename>. Markers below correspond to
> findings in spec-gap-report.md by ID.

<spec text, reproduced or closely paraphrased, with markers inserted inline:>

...the discount code field accepts up to 20 characters. [Q1: BLOCKING — no stated
valid character set; is unicode/emoji allowed?]

...on checkout, the order total is recalculated. [A2: ASSUMPTION — recalculation
is assumed synchronous; spec doesn't say, see Assumptions §2]

...refunds are processed within 3-5 business days. [Q3: TRACK B — Section 4.1 says
"3-5 business days," Section 6 says "up to 7 days" for the same flow — which is
correct?]
```

Marker prefixes: `Q<n>` for a Blocking Gap, Contradiction, or Open Question, `A<n>` for an Assumption Made, each matching its entry in `spec-gap-report.md`. Don't renumber between the two files — `[Q3]` in the annotated copy and `**Q3**` in the report must be the same item. A finding that concerns a spec's silence (nothing to anchor to) is marked at the end of the section where the missing behavior belongs.

## Anti-Patterns

- **Silently "fixing" the spec while summarizing it.** If the analysis quietly resolves an ambiguity in its own summary without flagging it, downstream agents build on a spec that never existed.
- **Flagging everything as blocking.** A report where 40 items are all "blocking" is as useless as one with none — calibrate against "can a reasonable test case be written without guessing."
- **Treating the report as the new source of truth.** The report is an analysis layer on top of the spec, not a replacement for it — `qa-doc-writer` and `qa-doc-reviewer` both still need the original spec.
- **Skipping non-functional requirements because the spec doesn't mention them.** Silence on performance/security/accessibility is a gap to flag, not evidence they're out of scope.

## Done When

- Every finding cites a specific spec location.
- The Requirements Inventory lists every checkable obligation in the spec as a `REQ-<n>` with its location; every `partly`/`no` row points at an existing Q.
- Q numbering is one global sequence, and every Q/A appears both in the report and as an inline marker.
- The Security Lens section exists — with findings, or with the explicit "not applicable" reason.
- Blocking Gaps and Assumptions Made are in separate sections and never mixed.
- The Testability Score has a one-line justification.
- Every open question is sorted into Track A or Track B — never left in one undifferentiated list.
- Track A questions were asked in-conversation as they were found, not only left in the report.
- `spec-annotated.md` exists, every marker in it has a matching numbered entry in `spec-gap-report.md`, and no finding in the report is missing its inline marker.
- `spec-source.md`, `spec-gap-report.md`, and `spec-annotated.md` are saved in `docs/qa/<task-id>/` (or the configured docs location), in the run's output language.

## Related Skills

- **qa-project-context** — universal dependency; check first for org-specific Definition of Ready.
- **test-design-techniques** — the next stage; cannot start meaningfully until blocking gaps here are resolved or explicitly assumed.
- **risk-based-testing** — orders Track B questions by the risk of the requirement they block.
- **security-testing** — Lens Mode supplies the OWASP spec questions for the Security dimension.
- **qa-doc-review** — re-derives coverage from the original spec and cross-checks it against this report's Assumptions Made.
