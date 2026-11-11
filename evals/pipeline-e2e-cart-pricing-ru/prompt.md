---
description: The whole pipeline in one request — a Russian spec plus a small pytest repo with a planted product bug, run end to end (Stage 1 → 4) without the user. Checks that every stage's agent runs and hands off through the task file, and is the run used to measure what one pipeline pass costs in tokens.
tags: [e2e, orchestration, ru]
max_turns: 200
timeout_seconds: 3600
allowed_tools: [Read, Glob, Grep, Skill, Agent, TaskCreate, TaskUpdate, TaskList, TaskGet]
expected_outcome: all four agents dispatched in order; docs/qa/<task-id>/ has the gap report, test plan and cases, autotest summary, review report and checkpoint; the task ends IN_REVIEW; new pytest files extend tests/ and were run; the 5000 ₽ free-shipping boundary is reported as a suspected product defect; src/ untouched.
---

Прогони QA-пайплайн по ТЗ specs/cart-pricing.md — автотесты для этого репозитория. Ветку я уже создал, коммитить ничего не надо. Меня не будет — вопросы не задавай, всё на русском.
