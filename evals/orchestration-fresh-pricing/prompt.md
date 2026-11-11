---
description: Run all four QA stages from a fresh cart-pricing spec and an existing pytest repository, then present the human checkpoint.
tags: [orchestration, ru]
max_turns: 180
timeout_seconds: 3600
allowed_tools: [Read, Glob, Grep, Skill, Agent, TaskCreate, TaskUpdate, TaskList, TaskGet]
expected_outcome: New Stage 1–4 artifacts, pytest run with the free-shipping boundary failure reported, product code untouched, and a task in IN_REVIEW with a human checkpoint.
---

Прогони полный QA-пайплайн по ТЗ `specs/cart-pricing.md` для текущего репозитория. Тесты уже запускаются через pytest. Ветка подготовлена. Пройди все этапы до итогового отчёта на русском, вопросы по ходу зафиксируй для итогового обсуждения. Ничего не коммить.
