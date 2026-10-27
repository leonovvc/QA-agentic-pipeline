---
type: regex
target: { source: file, path: docs/qa/password-reset/spec-gap-report.md }
pattern: "(токен|ссылк)[^\\n]{0,160}(срок|время жизни|истека|TTL|действител)|(срок|время жизни|TTL)[^\\n]{0,160}(токен|ссылк)"
flags: i
---
