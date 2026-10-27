# Third-Party Notices

This plugin adapts ten skills from:

**[petrkindlmann/qa-skills](https://github.com/petrkindlmann/qa-skills)** — QA and
test-automation skills for AI agents, by Petr Kindlmann, MIT License.

The original skills were written as a standalone library. In this plugin each one was
reworked into a procedure of a specific pipeline stage, keeping its methodology (the
checklists, catalogs, tables, worked examples, and reference files) while changing how it
connects to everything else. Common changes to every adapted skill:

- a **Role in the QA pipeline** section: which stage and agent use it, which artifacts it
  reads, which it writes;
- IDs and formats aligned with the pipeline's artifact contract (`REQ-<n>`, `Q<n>`, `A<n>`,
  `TC-<LVL>-<nnn>`, `R-<n>`; documents under `docs/qa/<task-id>/`);
- the output-language and readability rules of `qa-output-standards`;
- references to upstream skills this plugin does not ship were replaced with the
  in-plugin skill that now owns that job, or marked out of scope;
- frontmatter: `metadata.author: qa-agentic-pipeline` plus `metadata.adapted_from`
  naming the upstream skill.

## Adapted skills

| Skill | Pipeline stage | What changed beyond the common changes |
|---|---|---|
| `qa-project-context` | all | New **QA Pipeline** section (output language, docs location, test-case system, Definition of Ready, E2E budget, security lens, spec owners); a blank `references/template.md`; a table of which stage reads which section |
| `risk-based-testing` | 1, 2, 4 | New **Pipeline Mode**: a per-requirement Risk Assessment (impact × probability → zone → P0–P3 → required depth) written into `test-plan.md`; open questions raise probability; the original six-phase workflow kept as Product Mode |
| `test-planning` | 2 | Becomes the generator of `test-plan.md` with fixed sections; REQ → TC traceability matrix; a Feature Test Plan template in `references/plan-documents.md`; sprint/release planning kept |
| `test-case-management` | 2, 4 | Pipeline case format (ID + eight fields: traces, technique, level, priority, preconditions, test data, steps, expected result); per-level case files or filing into an existing TestRail/Xray/Zephyr/Qase hierarchy; lint checklist extended with Russian anti-phrases |
| `ai-test-generation` | 3 | Steps 1–4 of its staged pipeline mapped to Stages 1–2; new **Pipeline Mode** that starts at oracle design for existing cases; Step 7 review assigned to Stage 4 (the generator never reviews itself); model-specific guidance generalized |
| `unit-testing` | 3 | Playbook for unit-level cases: one test or one parametrized row per case with TC IDs in ids; no CI/coverage-gate changes during a pipeline run |
| `api-testing` | 3 | Playbook for API-level cases: client from the stack profile, three oracles per error case (status, error body, unchanged state), home of security-lens cases, honest `not run` reporting |
| `playwright-automation` | 3 | Playbook for E2E cases: one test per case, one `test.step` per case step, seed via API / assert via UI, extend an existing Cypress suite instead of adding Playwright |
| `ai-qa-review` | 4 | Pipeline checks before the smell buckets (TC ID present, oracle matches the case, reported status is true, readability); a severity mapping from smells to Blocking/Major/Minor/Disputed |
| `security-testing` | 1, 2, 4 | New **Lens Mode**: OWASP Top 10 (2025) questions asked of the spec in Stage 1 and security negative cases derived in Stage 2; the original CI scanning content kept as Scan Mode, run only on explicit request |

All other files in this repository (the four agents; the skills `run-qa-pipeline`,
`qa-pipeline-task-state`, `spec-gap-analysis`, `test-design-techniques`,
`test-pyramid-strategy`, `qa-doc-review`, `stack-detection-for-autotests`,
`qa-output-standards`; the artifact contract; `tools/`, `tests/`, `evals/`, `docs/`) are
original to this project.

## License text (MIT)

```
MIT License

Copyright (c) 2026 Petr Kindlmann

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

When pulling a newer upstream version of an adapted skill, merge the upstream changes
into the adapted file rather than overwriting it, and run `python tools/validate_plugin.py`
to catch references to upstream skills this plugin does not ship.
