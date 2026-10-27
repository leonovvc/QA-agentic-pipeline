---
name: api-testing
description: >-
  Test REST and GraphQL APIs against a real test environment with Playwright
  APIRequestContext, Supertest, httpx/requests, or the repo's existing HTTP client. In
  the QA pipeline this is Stage 3's playbook for every case allocated to the API level:
  the business rules enforced server-side, status codes, error bodies, auth and
  permission boundaries, and response contracts. Covers schema validation with Zod
  4/AJV, auth flow testing, CRUD lifecycle tests, error and header validation,
  pagination, idempotency, and performance assertions. Use when: "API test," "endpoint
  test," "REST test," "GraphQL test," "schema validation," "automate the API-level
  cases." Not for: browser UI flows — use playwright-automation; pure functions — use
  unit-testing; deciding which cases are API-level — use test-pyramid-strategy.
  Related: test-pyramid-strategy, stack-detection-for-autotests, ai-test-generation,
  playwright-automation, security-testing, qa-output-standards.
license: MIT
metadata:
  author: qa-agentic-pipeline
  adapted_from: petrkindlmann/qa-skills@api-testing (MIT, Petr Kindlmann)
  version: "3.0"
  category: automation
---

<objective>
A response that adds a nullable field or quietly drops one slips past `toHaveProperty` spot-checks and silently breaks the frontend in production. Schema-as-contract tests catch that drift in CI, not prod. This skill produces REST and GraphQL API tests that assert response shape, status codes, headers, auth boundaries, and timing — against a real test environment, not a mocked stand-in.
</objective>

## Role in the QA pipeline

`autotest-builder` uses this skill for every case in `test-cases-api.md`.

- **Client and runner come from the stack profile** (`stack-detection-for-autotests`): an
  existing Playwright project gets `APIRequestContext` tests in its API folder; an
  Express/Nest app with Jest gets Supertest; a Python service gets pytest + httpx. Don't
  introduce a second HTTP test stack.
- **One case → one test**; the title is `TC-API-<nnn>: <case title>` in the output language.
  Error-path cases assert the status code **and** the error body (machine-readable code,
  not just the message text) **and** that state did not change (follow-up GET) — the
  three oracles `ai-test-generation` Step 5 asks for.
- **Security-lens cases** that Stage 2 derived from `security-testing` (auth bypass, IDOR,
  injection payloads, rate limits) are API-level by default; write them with the patterns
  in `references/test-patterns.md` and the security skill's references.
- **Environment:** tests read the base URL and credentials from env/config the repo
  already uses. If the API isn't reachable from this environment, write the tests, mark
  them `not run` in `autotest-summary.md`, and state exactly what is missing (URL,
  token, seed data) — never claim they pass.
- **Clean up** every entity a test creates (anti-pattern 5), so reruns are deterministic.

## Discovery Questions

Check `.agents/qa-project-context.md` first — if it exists, use it and skip anything already answered there. Then:

1. **REST, GraphQL, or both?** REST-only suites use standard HTTP assertions. GraphQL needs query/mutation builders and benefits from an introspection-diff snapshot.
2. **Auth mechanism?** JWT, API key, OAuth 2.0, or session cookies — each needs a different fixture strategy.
3. **OpenAPI/Swagger spec available?** If yes, auto-generate Zod schemas as contracts (`orval`, `openapi-zod-client`) and consider spec-driven fuzzing with Schemathesis.

---

## Core Principles

1. **Test contracts, not implementations.** Assert on response shape, status codes, and headers — not on internal logic or database state.
2. **Schema validation catches drift before it breaks consumers.** A failing schema test means you caught a breaking change before your frontend did.
3. **Auth flows are tests too — don't just hardcode tokens.** Test login, refresh, expiration, and permission boundaries.
4. **Response time is a testable assertion.** Performance regressions caught in CI are cheaper than production incidents.

---

## Exploratory vs Automated: Tooling

API exploration (debugging, manual probing, OpenAPI playground) and automated API testing are different jobs. Use the right tool for each:

| Tool | Best for | Why |
|------|----------|-----|
| **Bruno** (v3.4+) | File-based collections, git-reviewable workflows, FOSS Postman replacement | Filesystem-first, no cloud sync required; gRPC + OAuth + GraphQL query builder |
| **Hurl** (8.x) | Plain-text HTTP testing, CI smoke checks | One file = many requests + assertions; runs anywhere curl runs; certificate + JSONPath (RFC 9535) queries |
| **Hoppscotch** | Web-based Postman-style exploration | Open source, runs in browser, good for quick checks |
| **Playwright `APIRequestContext`** | Automated tests in your test runner | This skill's focus — covered below |
| **Supertest** (Node) / **httpx** (Python) | In-process API tests against your own app | Fastest feedback when you control both sides |

Skip Postman/Insomnia for new projects unless your team already has investment there — file-based tools (Bruno, Hurl) are easier to review in PRs and survive when collections drift.

## Playwright API Testing

`APIRequestContext` supports standalone API tests without launching a browser and shares cookie/storage state with browser contexts. Use it for:

- **Standalone API tests** — `request.get/post/...` with status, header, and body assertions.
- **Combined browser + API tests** — seed data via API, assert it appears in the UI, then clean up via API.
- **Authenticated fixtures** — log in once in a fixture, hand a pre-authenticated `APIRequestContext` to tests, and dispose it on teardown. Never hardcode tokens.

See `references/playwright-setup.md` for the `playwright.config.ts`, standalone tests, combined browser+API test, and the authenticated API fixture.

---

## Schema Validation

Validate response shape against a schema rather than spot-checking individual fields with `toHaveProperty`. Two common approaches:

- **Zod 4** — define a schema, `safeParse` the response, and assert `result.success`. Log `result.error.issues` on failure for a precise diff. Use the Zod 4 native string formats: `z.email()`, `z.uuid()`, `z.iso.datetime()` — the chained `z.string().email()` forms are deprecated and slated for removal.
- **AJV with JSON Schema** — when you already have JSON Schema (e.g. from an OpenAPI spec), compile and validate with `ajv` + `ajv-formats`.

**Schema-as-contract:** have both the API and the tests import the same schema file. If the response shape changes, consumer tests fail immediately. With an OpenAPI spec, auto-generate the schema (`orval` or `openapi-zod-client`). For spec-first teams, add **Schemathesis** as a CI job to fuzz the live API against the spec and catch undocumented shapes and edge-case 500s.

See `references/schema-validation.md` for the Zod 4, AJV, schema-as-contract, and Schemathesis implementations.

---

## Test Patterns

Cover each endpoint with a happy-path test plus at least one error-path test. The common patterns:

- **CRUD lifecycle** — a `describe.serial` block that creates, reads, updates, deletes, then verifies the 404. Carries the resource id across steps.
- **Auth flows** — login success, invalid credentials (401), expired token (401), token refresh, and permission boundary (403). Treat auth as its own describe block.
- **Error responses** — 400 (malformed body), 422 (validation with field details), 429 (rate limit + `retry-after`). Don't ship happy-path-only suites.
- **Response headers** — assert `content-type`, `cache-control`, and rate-limit headers directly (not behind a conditional that may never fire). See the pattern below.
- **Pagination** — first-page metadata, out-of-bounds empty page, and rejection of invalid page size.
- **File upload/download** — multipart upload and `content-disposition` header verification.
- **GraphQL** — a small `gql` helper, then query / mutation / invalid-query (errors array) cases, plus an introspection-diff snapshot to catch silently-removed fields.
- **Webhooks** — spin up a throwaway HTTP server, register a webhook, trigger the event, and assert delivery.

See `references/test-patterns.md` for the full runnable implementations of every pattern above plus performance assertions.

### Response Headers

Headers carry the contract: cache directives, rate-limit info, content type, CORS policy. Assert them with `response.headers()` and index by lowercase name; don't gate the assertion behind an `if (rateLimited)` that may not fire.

```typescript
test('GET /api/users sets expected response headers', async ({ request }) => {
  const response = await request.get('/api/users');
  const headers = response.headers();

  expect(headers).toBeDefined();
  expect(headers['content-type']).toContain('application/json');
  expect(headers['cache-control']).toBeDefined();   // "no-store" | "max-age=60" | ...
});
```

For the rate-limit and `retry-after` variants, see `references/test-patterns.md` (Response Header Validation).

---

## Performance Assertions

Response time and payload size are testable assertions — assert that a hot endpoint responds within a budget (e.g. 500ms), that payloads stay under a size ceiling, and that the API survives a burst of concurrent requests without 5xx. See `references/test-patterns.md` (Performance Assertions section) for the code.

---

## Anti-Patterns

### 1. Hardcoded auth tokens
Tokens expire, rotate, and differ across environments. Use a login fixture that acquires tokens dynamically.

### 2. Testing against production
API tests create, modify, and delete data. Run against a dedicated test environment or local instance.

### 3. Not validating error responses
Happy-path-only suites miss the most common production issues. Test 400, 401, 403, 404, and 500 responses for every endpoint.

### 4. Asserting headers only conditionally
Headers carry cache directives, rate limit info, content type, and CORS policy. Assert them directly on every relevant response — a check buried inside `if (rateLimited)` may never run and proves nothing.

### 5. No cleanup after test data creation
Tests that create resources without deleting them pollute the database. Use `afterEach`/`afterAll` hooks or fixture teardown.

### 6. Treating API tests as unit tests
Don't mock the database — API tests verify the contract from the consumer's perspective. Mock only genuine third parties you don't own (payment gateways, external SaaS).

### 7. Ignoring idempotency
PUT and DELETE should be idempotent. Test that calling them twice produces the same result.

---

## Done When

- Every target endpoint has at least a happy-path test and at least one error-path test (4xx or 5xx response validated).
- Auth flow tested as its own describe block: successful login, invalid credentials, expired token, and permission boundary (403).
- Schema validation assertions on response shape using Zod 4 or AJV — not just `toHaveProperty` spot-checks.
- Header assertions exist for at least `content-type` and any cache/rate-limit headers the API sets, asserted unconditionally.
- Contract tests in place for any endpoint consumed by a different team or service (a shared schema file; consumer-driven contract testing with Pact is out of this plugin's scope).
- Genuine third-party calls (payment gateways, external SaaS) are mocked or virtualized; the API and its database run for real.
- The suite was run against the test environment and every API case has a real status in `autotest-summary.md` (`passed` / `failed` with a defect classification / `not run` with the missing prerequisite).

## Reference Files (in `references/`)

- **playwright-setup.md** — `playwright.config.ts`, standalone API tests, combined browser+API tests, and the authenticated `APIRequestContext` fixture.
- **schema-validation.md** — Zod 4 and AJV/JSON-Schema response validation, the schema-as-contract pattern, and Schemathesis spec-driven fuzzing.
- **test-patterns.md** — Runnable CRUD lifecycle, auth flows, error responses, response headers, pagination, file upload/download, GraphQL (+ introspection diff), webhook, and performance tests.

## Related Skills

- **test-pyramid-strategy** — decides which cases are API-level.
- **stack-detection-for-autotests** — picks the client, runner, and folder.
- **ai-test-generation** — the case → oracle → code method Stage 3 applies.
- **playwright-automation** — browser E2E and combined browser + API patterns.
- **security-testing** — auth, access-control, and injection test patterns for security-lens cases.
- **unit-testing** — when a rule can be proven without HTTP at all.
- **qa-output-standards** — language and readability rules for test titles and comments.
