---
name: e2e-test-setup
description: E2E suite runs against the docker compose stack in tests/e2e.
type: project
tags: [demo, testing, ci]
---

Run make e2e; it starts the compose stack and seeds fixtures.

**Why:** Local and CI runs must match.
**How to apply:** Before claiming a fix works.
Related: [[ci-runner-limits]]