# QA Review — Cart quantity limits

## Traceability Summary
4 of 4 requirements covered.
| REQ | Verdict | Cases |
|---|---|---|
| REQ-1 | covered | TC-UNIT-001 |
| REQ-2 | covered | TC-API-001 |
| REQ-3 | covered | TC-UNIT-002, TC-E2E-001 |
| REQ-4 | covered | TC-UNIT-003 |

## Findings
### Blocking
(none)
### Major
**R-1** [Major] REQ-2, TC-API-001 — only the "above max" class is tested; the below-min class (0) has no API case → add TC-API-002 for quantity 0.
### Minor
**R-2** [Minor] TC-UNIT-002 — test data uses only two-decimal prices; add a rounding case.

## Disputed — Needs Human Decision
None.

## Readability
Meets qa-output-standards.

## Autotest Review
3 unit tests re-run: pass. API/E2E not runnable here.
