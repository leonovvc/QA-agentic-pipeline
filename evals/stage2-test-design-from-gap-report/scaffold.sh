#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p docs/qa/cart-orders docs/qa/pipeline-state
cp "$here"/resources/cart-orders/*.md docs/qa/cart-orders/
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat > docs/qa/pipeline-state/cart-orders.json <<JSON
{
  "task_id": "cart-orders",
  "title": "Cart limits, shipping and order cancellation",
  "source": {"type": "text", "value": "docs/qa/cart-orders/spec-source.md"},
  "target_repo": ".",
  "output_language": "en",
  "docs_dir": "docs/qa/cart-orders",
  "status": "IN_PROGRESS",
  "created_at": "$now",
  "updated_at": "$now",
  "stages": [
    {"stage": 1, "agent": "spec-analyst", "status": "done", "started_at": "$now", "completed_at": "$now",
     "output": ["docs/qa/cart-orders/spec-source.md", "docs/qa/cart-orders/spec-gap-report.md", "docs/qa/cart-orders/spec-annotated.md"]},
    {"stage": 2, "agent": "qa-doc-writer", "status": "pending", "started_at": null, "completed_at": null, "output": null},
    {"stage": 3, "agent": "autotest-builder", "status": "pending", "started_at": null, "completed_at": null, "output": null},
    {"stage": 4, "agent": "qa-doc-reviewer", "status": "pending", "started_at": null, "completed_at": null, "output": null}
  ],
  "assumptions_log": ["A1", "A2", "A3"],
  "disputed_items": [],
  "history": [{"at": "$now", "event": "task_created"}, {"at": "$now", "event": "stage_completed", "stage": 1}]
}
JSON
