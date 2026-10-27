---
description: Stage 1 alone — spec-analyst must find the defects planted in a realistic promo-code spec, build the requirements inventory, mark findings inline, and apply the security lens.
tags: [stage1]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Agent, TaskCreate, TaskUpdate, TaskList, TaskGet]
expected_outcome: spec-gap-report.md + spec-annotated.md + spec-source.md under docs/qa/checkout-promo/, in English, with REQ inventory and most of the 8 planted defects found.
---

Here's the spec for our new promo-code feature: specs/checkout-promo.md. Before anyone writes test cases, I need the spec analysis only — gaps, contradictions, open questions, what's testable. Don't write a test plan yet.

Work unattended, don't ask me anything — log any assumption you have to make. Write the documents in English and save them under docs/qa/checkout-promo/.
