---
description: Stage 2 alone — from a finished spec analysis, write a risk-based test plan and cases that apply BVA, a decision table, and a state-transition model, keep the pyramid unit-heavy, and trace every case to a REQ.
tags: [stage2]
max_turns: 80
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Agent, TaskCreate, TaskUpdate, TaskList, TaskGet]
expected_outcome: test-plan.md and per-level case files under docs/qa/cart-orders/, all six REQs traced, boundaries 0/1/20/21 and 4999.99/5000, an illegal Shipped→cancel case, a decision table for the member discount, few E2E cases.
---

The spec analysis for the cart/orders feature is done — everything is in docs/qa/cart-orders/ and the task file in docs/qa/pipeline-state/. Now write the test plan and the test cases. Documentation only — no autotests yet. Don't ask me anything; English, please.
