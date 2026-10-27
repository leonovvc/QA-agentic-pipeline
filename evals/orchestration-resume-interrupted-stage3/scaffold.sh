#!/usr/bin/env bash
# Same repo and docs as stage3-autotests-python-ru, but the task file says the previous
# session died in the middle of Stage 3 and left a half-written test file behind.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
src="$here/../stage3-autotests-python-ru/resources"
cp -r "$src/project/." .
mkdir -p docs/qa/pricing docs/qa/pipeline-state
cp "$src"/docs/*.md docs/qa/pricing/
cat > tests/test_pricing_partial.py <<'PY'
# left behind by an interrupted session
from decimal import Decimal

from shop.pricing import is_valid_quantity


def test_tc_unit_001_
PY
t0="2026-10-26T18:00:00Z"
cat > docs/qa/pipeline-state/pricing.json <<JSON
{
  "task_id": "pricing",
  "title": "Ценообразование корзины",
  "source": {"type": "text", "value": "docs/qa/pricing/spec-source.md"},
  "target_repo": ".",
  "output_language": "ru",
  "docs_dir": "docs/qa/pricing",
  "status": "IN_PROGRESS",
  "created_at": "$t0",
  "updated_at": "2026-10-26T18:40:00Z",
  "stages": [
    {"stage": 1, "agent": "spec-analyst", "status": "done", "started_at": "$t0", "completed_at": "2026-10-26T18:10:00Z",
     "output": ["docs/qa/pricing/spec-source.md", "docs/qa/pricing/spec-gap-report.md", "docs/qa/pricing/spec-annotated.md"]},
    {"stage": 2, "agent": "qa-doc-writer", "status": "done", "started_at": "2026-10-26T18:10:00Z", "completed_at": "2026-10-26T18:30:00Z",
     "output": ["docs/qa/pricing/test-plan.md", "docs/qa/pricing/test-cases-unit.md", "docs/qa/pricing/test-cases-api.md", "docs/qa/pricing/test-cases-manual.md"]},
    {"stage": 3, "agent": "autotest-builder", "status": "in_progress", "started_at": "2026-10-26T18:30:00Z", "completed_at": null, "output": null},
    {"stage": 4, "agent": "qa-doc-reviewer", "status": "pending", "started_at": null, "completed_at": null, "output": null}
  ],
  "assumptions_log": ["A1 — округление half-up, порог до скидки"],
  "disputed_items": [],
  "history": [
    {"at": "$t0", "event": "task_created"},
    {"at": "2026-10-26T18:10:00Z", "event": "stage_completed", "stage": 1},
    {"at": "2026-10-26T18:30:00Z", "event": "stage_completed", "stage": 2},
    {"at": "2026-10-26T18:30:00Z", "event": "stage_started", "stage": 3}
  ]
}
JSON
