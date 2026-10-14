# Memory

Shared project memory: one fact per Markdown file in `.agents/memories/<type>/<name>.md`.
This file holds the memory rules and, below them, the generated index of shared memories.

## Reading

- Read this file at the start of every session, and every file in `.agents/memories/user/` (local `user` memories are not indexed).
- Open a memory's file only when its description is relevant to the current task.
- Memories record what was true when they were written.
Before acting on one that names a file, function, flag or command, check that it still exists.
- If a memory conflicts with the code or with what the user says now, trust the present and fix or delete the memory.

## Types

Each type is a folder.

| Type | Holds | Git |
|---|---|---|
| `user` | Who the user is: role, expertise, personal preferences | local only, gitignored |
| `feedback` | How agents should work: corrections and approaches the user confirmed | shared |
| `project` | Goals, constraints, decisions, deadlines and context not visible in the code | shared |
| `reference` | Pointers to external resources: dashboards, tickets, docs, runbooks | shared |

Anything the whole team should follow belongs in `feedback` or `project`, never in `user`.

## Format

```markdown
---
name: run-e2e-before-fix
description: Reproduce every bug end to end before changing code.
type: feedback
tags: [testing, bugfix]
update_at: 2026-10-01
---

Reproduce a reported bug the way a user would hit it before writing a fix.

**Why:** Fixes made from unit-level guesses repeatedly missed the real cause.
**How to apply:** Any bug report; record the repro steps in the PR description.
Related: [[e2e-test-setup]]
```

- The header has exactly five fields: `name`, `description`, `type`, `tags`, `update_at`.
- `name` is kebab-case, equals the filename without `.md` and is unique across all types.
- `description` is one line under 200 characters, specific enough to judge relevance from the index alone.
- `type` equals the folder the file is in.
- `tags` is a list of 1 to 5 lowercase tags.
References are tags too, for example `jira:proj-12`, `svc:billing` or `doc:architecture/billing.md` (a file under `docs/`, never `reports/`).
- `update_at` is the day the memory was last modified, as `YYYY-MM-DD`.
- The body holds one fact; `feedback` and `project` memories add `**Why:**` and `**How to apply:**` lines.
- Use absolute dates (2026-10-01), never relative ones, and link related memories with `[[name]]`.

## When to write

Save a correction or preference about how to work, an approach the user confirmed, a decision, constraint or deadline the code does not show, a pointer to an external resource, or who the user is (`user`, local).

Do not save anything derivable from the code, git history, `AGENTS.md` or an existing memory, details that only matter to the current task, or secrets, credentials and personal data about third parties.

## How to write

- Always use the `memory-manage` skill to create, update, delete or review memories.
- Update an existing memory instead of creating a near-duplicate, and delete memories that turn out to be wrong.
- After every change, run `.agents/tools/memory-index.py` to regenerate the index below, and commit it with the memory change.
- A hook lints memory, index and report files after every write; fix any error it reports immediately.
- Run `.agents/tools/memory-lint.py` before pushing; CI runs it only if `.github/workflows/agents-lint.yml` is turned on.
- `.agents/tools/memory-map.py --open` renders all memories as a mind map in `reports/local/memory-map.html`.

## Index

One line per shared memory: name, description, tags.

<!-- Generated below by .agents/tools/memory-index.py; do not edit by hand. -->

### feedback

(none)

### project

(none)

### reference

(none)
