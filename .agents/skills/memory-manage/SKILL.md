---
name: memory-manage
description: Save, update, delete or review project memories in .agents/memories. Use when the user says "remember this", "forget that" or corrects how you work, when you learn a durable fact worth keeping for future sessions (a decision, constraint, preference or external pointer), or when asked to review or clean up memories.
---

# memory-manage

Project memory is a folder of Markdown files, one fact per file, in `.agents/memories/<type>/<name>.md`.
The session-start hook prints an index of every memory (name, description, tags).
`AGENTS.md` holds the full rules; this skill is the procedure.

## Types (= folder)

| Type | Holds | Git |
|---|---|---|
| `user` | Who the user is: role, expertise, personal preferences | local only, never committed |
| `feedback` | How agents should work: corrections and confirmed approaches | shared |
| `project` | Goals, constraints, decisions, deadlines not visible in the code | shared |
| `reference` | Pointers to external resources: dashboards, tickets, docs, runbooks | shared |

If a fact applies to the whole team, it is `feedback` or `project`, never `user`.

## File format

```markdown
---
name: run-e2e-before-fix
description: Reproduce every bug end to end before changing code.
type: feedback
tags: [testing, bugfix]
---

Reproduce a reported bug the way a user would hit it before writing a fix.

**Why:** Fixes made from unit-level guesses repeatedly missed the real cause.
**How to apply:** Any bug report; record the repro steps in the PR description.
Related: [[e2e-test-setup]]
```

- Header has exactly `name`, `description`, `type`, `tags`.
- `name`: kebab-case, equal to the filename without `.md`, unique across all types.
- `description`: one line, under 200 characters, specific enough to judge relevance from the index alone.
- `type`: equal to the folder name.
- `tags`: 1 to 5 lowercase tags; references are tags too, e.g. `jira:proj-12`, `svc:billing`, `report:plans/2026-10-01-memory-design.html`.
- Body: one fact; `feedback` and `project` need `**Why:**` and `**How to apply:**` lines; absolute dates only (2026-10-01, never "next week"); link related memories with `[[name]]`.
- Never store secrets, tokens or credentials.

## Save

1. Check it is worth saving: not already in the code, git history, `AGENTS.md` or another memory, and useful beyond the current task.
2. Pick the type, which picks the folder.
3. Search for an existing memory on the same fact: scan the index, then `grep -ril <keyword> .agents/memories`.
   If one exists, update it instead of creating a new file.
4. Write the file.
5. Run `.agents/tools/memory-lint <file>` and fix every error.
6. Tell the user in one line what you saved and where.

## Update

1. Edit the file in place; keep it one fact.
2. If the name changes, rename the file to match and update every `[[old-name]]` link (`grep -rl "\[\[old-name\]\]" .agents/memories`).
3. Run `memory-lint` on the changed files.

## Delete

Delete when the user asks to forget something or a memory turns out to be wrong.

1. Remove the file.
2. Remove or repoint every `[[name]]` link to it.
3. Run `.agents/tools/memory-lint` (no arguments) and fix any new warnings.
4. Tell the user what was deleted.

## Review

Run when asked to review, consolidate or clean up memories.

1. Merge memories that state the same fact; keep the clearer name and fix links.
2. Verify facts against the repo: files, functions, flags and commands a memory names must still exist.
   Fix or delete stale ones.
3. Convert relative dates to absolute ones and split memories that hold more than one fact.
4. Normalize tags so the same concept uses the same tag.
5. Run `.agents/tools/memory-lint` with no arguments until it reports 0 errors.
6. Summarize the changes (merged, updated, deleted) so the user can review them in a PR.

## Git

- Never commit anything in `.agents/memories/user/`.
- Commit memory changes separately from code changes, with a `memory:` prefix, e.g. `memory: add run-e2e-before-fix`.
- Do not commit unless the user asks; shared memories reach the team through a reviewed PR.
