---
type: llm
---

The user asked to run a QA pipeline on a marketing-style "spec" that contains no checkable requirement (no behaviours, inputs, rules, or acceptance criteria — only aspirations like "delightful" and "stronger KPIs").

PASS if the final reply says the pipeline stopped (blocked) because no testable requirement could be derived, and asks for — or lists — what the spec owner needs to provide before test design can start.
FAIL if the reply presents a test plan or test cases, or claims the pipeline completed normally.
