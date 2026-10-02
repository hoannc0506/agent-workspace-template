---
name: postgres-version-pin
description: Postgres pinned to 16.4 until the 2026-11-15 migration window.
type: project
tags: [demo, db, infra]
---

Do not bump Postgres past 16.4 before 2026-11-15.

**Why:** Extensions are not yet verified on 17.
**How to apply:** Dependency updates and Dockerfiles.
