---
name: run-e2e-before-fix
description: Reproduce every bug end to end before changing code.
type: feedback
tags: [demo, testing, bugfix]
update_at: 2026-10-02
---

Reproduce a reported bug the way a user would hit it before writing a fix.

**Why:** Unit-level guesses repeatedly missed the real cause.
**How to apply:** Any bug report; put the repro steps in the PR description.
Related: [[e2e-test-setup]]