---
name: no-mocks-in-integration
description: Integration tests hit a real Postgres container, never mocks.
type: feedback
tags: [demo, testing, db]
update_at: 2026-10-02
---

Integration tests run against the Postgres container from docker compose.

**Why:** A mocked test passed while a broken migration shipped on 2026-08-12.
**How to apply:** New or changed tests under tests/integration.
Related: [[e2e-test-setup]] [[postgres-version-pin]]