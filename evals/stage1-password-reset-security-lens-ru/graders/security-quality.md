---
type: llm
weight: 2
focus: { source: file, path: docs/qa/password-reset/spec-gap-report.md }
---

This is a Russian-language QA spec-gap report for a password-reset spec. The spec shows a different message when the email is not registered, never says how long the reset link is valid, never says whether the link can be reused, and never limits how often a reset can be requested.

PASS if the report (in Russian) raises at least three of those four issues as open questions or gaps (not as facts it decided on its own), and routes product-rule questions to the analyst/spec owner (Track B).
FAIL if fewer than three are raised, if the report is mostly in English, or if it silently decides the security rules itself without flagging them.
