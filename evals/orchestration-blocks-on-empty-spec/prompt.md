---
description: The orchestrator's one allowed mid-chain stop — a "spec" with no checkable requirement must end as BLOCKED after Stage 1, with no test plan or cases written.
tags: [orchestration]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Agent, TaskCreate, TaskUpdate, TaskList, TaskGet]
expected_outcome: Stage 1 artifacts plus a task file with status BLOCKED; no test-plan.md or test-cases files.
---

Run the QA pipeline on specs/loyalty.md. I'm stepping away — don't wait for me; write everything in English.
