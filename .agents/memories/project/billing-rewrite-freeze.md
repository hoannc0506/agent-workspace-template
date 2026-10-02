---
name: billing-rewrite-freeze
description: No schema changes to billing tables until the rewrite lands on 2026-12-01.
type: project
tags: [demo, svc:billing, db]
---

Billing table schemas are frozen until 2026-12-01.

**Why:** The rewrite team migrates the same tables.
**How to apply:** Any migration touching billing_*.
Related: [[grafana-billing]] [[postgres-version-pin]]