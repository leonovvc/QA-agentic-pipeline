---
type: llm
weight: 2
focus: { source: file, path: docs/qa/cart-orders/test-plan.md }
---

This is a test plan for: quantity limits 1–20 (REQ-1/2), subtotal arithmetic (REQ-3), free shipping at ≥ 5000 (REQ-4), a member discount with three conditions (REQ-5), and an order state machine with cancellation (REQ-6).

PASS if all hold: (a) every REQ-1…REQ-6 appears in a risk table with a priority and in a traceability matrix; (b) the money rules (REQ-3, REQ-4, REQ-5) are not given a lower priority than the error message rule (REQ-2); (c) the pyramid rationale puts pure calculations at unit level rather than E2E; (d) the plan records which assumptions (A1–A3) it builds on.
FAIL if any of (a)–(d) is missing.
