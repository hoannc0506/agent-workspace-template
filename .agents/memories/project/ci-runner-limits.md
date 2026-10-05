---
name: ci-runner-limits
description: CI runners have 4 GB RAM; parallel test workers capped at 2.
type: project
tags: [demo, ci, testing]
update_at: 2026-10-02
---

CI runners have 4 GB RAM, so test workers are capped at 2.

**Why:** More workers caused OOM-killed jobs.
**How to apply:** When changing test parallelism.
