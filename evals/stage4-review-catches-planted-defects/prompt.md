---
description: Stage 4 alone — the independent reviewer must re-derive coverage from the original spec and catch planted defects in a test plan that looks complete, without rewriting it.
tags: [stage4]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Agent, TaskCreate, TaskUpdate, TaskList, TaskGet]
expected_outcome: qa-review-report.md that flags the illegal-transition gap for REQ-6, the incomplete BVA in TC-UNIT-001, the threshold rule tested only at E2E, and the vague expected result in TC-API-002; plan and cases unchanged.
---

Our QA docs for the cart/orders feature are in docs/qa/cart-orders/ (spec, spec analysis, test plan, test cases; no autotests yet). Please review the test documentation before we start automating. Write the review in English; I won't be around for questions.
