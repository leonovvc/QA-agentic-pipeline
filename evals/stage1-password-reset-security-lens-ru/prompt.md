---
description: Stage 1 on a Russian spec with security triggers — the security lens must surface account enumeration, token lifetime/reuse, and rate limiting; the report must be in Russian.
tags: [stage1, security, ru]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Agent, TaskCreate, TaskUpdate, TaskList, TaskGet]
expected_outcome: spec-gap-report.md in Russian under docs/qa/password-reset/, with a filled Security Lens section and most planted security gaps raised as questions.
---

Проанализируй ТЗ на восстановление пароля: specs/password-reset.md. Нужен только анализ ТЗ (пробелы, противоречия, вопросы аналитику), тест-план пока не пиши.

Работай без вопросов ко мне, все допущения фиксируй в отчёте. Документы — на русском, в папку docs/qa/password-reset/.
