---
description: Stage 3 alone on a small Python repo with an existing pytest suite and a planted product bug — tests must extend the suite, carry TC IDs and Russian titles, actually run, and report the bug as a suspected product defect without touching product code.
tags: [stage3, ru]
max_turns: 80
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Agent, TaskCreate, TaskUpdate, TaskList, TaskGet]
expected_outcome: new pytest file(s) under tests/ with TC-UNIT-001…005, run with pytest; TC-UNIT-004 fails and is reported as a suspected product defect; TC-API-001 not run with the missing prerequisite; TC-MAN-001 manual; src/shop/pricing.py untouched.
---

Тест-план и кейсы для ценообразования готовы — docs/qa/pricing/, файл задачи в docs/qa/pipeline-state/pricing.json. Сделай автотесты по этим кейсам в этом репозитории и прогони их. Ветку я уже создал, коммитить ничего не надо. Меня не будет — вопросы не задавай.
