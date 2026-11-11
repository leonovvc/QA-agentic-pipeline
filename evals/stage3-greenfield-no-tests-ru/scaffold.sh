#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp -r "$here/resources/project/." .
mkdir -p docs/qa/pricing docs/qa/pipeline-state
cp "$here"/resources/docs/*.md docs/qa/pricing/
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat > docs/qa/pipeline-state/pricing.json <<JSON
{
  "task_id": "pricing",
  "title": "Ценообразование корзины",
  "source": {"type": "text", "value": "docs/qa/pricing/spec-source.md"},
  "target_repo": ".",
  "output_language": "ru",
  "docs_dir": "docs/qa/pricing",
  "status": "IN_PROGRESS",
  "created_at": "$now",
  "updated_at": "$now",
  "stages": [
    {"stage": 1, "agent": "spec-analyst", "status": "done", "started_at": "$now", "completed_at": "$now", "output": ["docs/qa/pricing/spec-source.md", "docs/qa/pricing/spec-gap-report.md", "docs/qa/pricing/spec-annotated.md"]},
    {"stage": 2, "agent": "qa-doc-writer", "status": "done", "started_at": "$now", "completed_at": "$now",
     "output": ["docs/qa/pricing/test-plan.md", "docs/qa/pricing/test-cases-unit.md", "docs/qa/pricing/test-cases-api.md", "docs/qa/pricing/test-cases-manual.md"]},
    {"stage": 3, "agent": "autotest-builder", "status": "pending", "started_at": null, "completed_at": null, "output": null},
    {"stage": 4, "agent": "qa-doc-reviewer", "status": "pending", "started_at": null, "completed_at": null, "output": null}
  ],
  "assumptions_log": ["A1"],
  "disputed_items": [],
  "history": [{"at": "$now", "event": "task_created"}]
}
JSON
