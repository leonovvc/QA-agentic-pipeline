---
description: Stage 3 on a Python repo with no tests at all — stack detection must report that nothing exists, pick one framework matching the language, scaffold minimally, write the verbose greenfield style (a header naming the task), run the tests and still report the planted bug. The counterpart of stage3-autotests-python-ru, where a suite exists and must be extended.
tags: [stage3, ru]
max_turns: 80
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Agent, TaskCreate, TaskUpdate, TaskList, TaskGet]
expected_outcome: autotest-builder dispatched; Stack Profile says no test framework/directory was found and justifies pytest; a new tests/ directory with test files that open with a header naming the task; pytest run; no package.json or JS test config created; TC-UNIT-004 reported as a suspected product defect.
---

Кейсы по ценообразованию лежат в docs/qa/pricing/, файл задачи в docs/qa/pipeline-state/pricing.json. Сделай автотесты по этим кейсам в этом репозитории и прогони их. Ветку я уже создал, коммитить ничего не надо. Меня не будет — вопросы не задавай.
