---
name: production-deploy-schedule
description: Production deploys only Tue and Thu after QA sign-off, from 2026-10-01.
type: project
tags: [demo, deploy, release, qa]
---

Production deploys happen only on Tuesdays and Thursdays after QA sign-off.

**Why:** Friday deploys caused weekend incidents.
**How to apply:** Check the day and QA status before any production release.
Related: [[grafana-billing]] [[oncall-runbook]]