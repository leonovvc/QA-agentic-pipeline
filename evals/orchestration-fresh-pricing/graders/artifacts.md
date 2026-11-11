---
type: regex
target: files
pattern: '^(?=[\s\S]*^docs/qa/([^/\r\n]+)/spec-gap-report\.md\r?$)(?=[\s\S]*^docs/qa/\1/spec-source\.md\r?$)(?=[\s\S]*^docs/qa/\1/spec-annotated\.md\r?$)(?=[\s\S]*^docs/qa/\1/test-plan\.md\r?$)(?=[\s\S]*^docs/qa/\1/test-cases-unit\.md\r?$)(?=[\s\S]*^docs/qa/\1/autotest-summary\.md\r?$)(?=[\s\S]*^docs/qa/\1/qa-review-report\.md\r?$)(?=[\s\S]*^docs/qa/\1/checkpoint\.md\r?$)(?=[\s\S]*^docs/qa/pipeline-state/\1\.json\r?$)'
flags: m
weight: 2
---
