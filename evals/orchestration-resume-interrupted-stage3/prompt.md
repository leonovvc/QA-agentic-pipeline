---
description: Resume after a dropped session — the orchestrator must read the task file, keep Stages 1-2 untouched, restart the interrupted Stage 3 whole, run Stage 4, and finish at IN_REVIEW with a checkpoint.
tags: [orchestration, ru]
max_turns: 150
timeout_seconds: 3000
allowed_tools: [Read, Glob, Grep, Skill, Agent, TaskCreate, TaskUpdate, TaskList, TaskGet]
expected_outcome: Stage 3 redone (autotest-summary.md), Stage 4 done (qa-review-report.md), checkpoint.md written, task status IN_REVIEW; spec-gap-report.md, test-plan.md and test-cases files never rewritten.
---

Вчера сессия оборвалась посреди QA-пайплайна по задаче pricing. Продолжи пайплайн. Меня не будет до вечера — вопросы не задавай.
