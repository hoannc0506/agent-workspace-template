# Agent instructions

These instructions apply to every agent working in this repository (Claude Code reads them through `CLAUDE.md`).

## General guidelines

- Never use the em dash "-". Use plain dash "-" instead.
- When writing commit messages, NEVER auto-add your agent name as co-author.
- Never manually modify CHANGELOG.md files or any files that are marked as auto-generated.
- When writing or substantially editing long Markdown files, put each full sentence on its own line.
Preserve normal Markdown structure, but avoid wrapping multiple sentences onto one physical line.
- When making technical decisions, do not give much weight to development cost.
Instead, prefer quality, simplicity, robustness, scalability, and long term maintainability.
- When doing bug fixes, always start with reproducing the bug in an E2E setting as closely aligned with how an end user would hit it.
This makes sure you find the real problem so your fix will actually solve it.
- When end-to-end testing a product, be picky about the UI you see and be obsessed with pixel perfection.
If something clearly looks off, even if it is not directly related to what you are doing, try to get it fixed along the way.
- Apply that same high standard to engineering excellence: lint, test failures, and test flakiness.
If you see one, even if it is not caused by what you are working on right now, still get it fixed.

## Workspace layout

```
AGENTS.md                 instructions for all agents (this file)
CLAUDE.md                 imports AGENTS.md for Claude Code
.agents/                  shared by every agent
  memories/<type>/        project memory, one fact per .md file
  reports/<category>/     reports (.html, .md, .svg, .png)
  skills/<skill>/SKILL.md shared skills (Codex reads them here; .claude/skills links here)
  hooks/                  hook scripts used by both agents
  tools/                  CLI tools (memory-lint)
.claude/                  Claude Code only settings
.codex/                   Codex only settings
```

- Put anything both agents use in `.agents/`.
Put settings that only one agent understands in `.claude/` or `.codex/`.
- Add a skill as `.agents/skills/<name>/SKILL.md`; `.claude/skills` is a symlink to that folder, so never add skills there separately.
- Add a hook script to `.agents/hooks/` and register it in both `.claude/settings.json` and `.codex/config.toml`.
Hooks must be standard-library Python and fail open (exit 0 on internal errors).
- Built-in agent memory is turned off in both configs.
Never write to `~/.claude/projects/*/memory`, Codex memories or any other user-scope memory.

## Memory

### Reading

- At session start a hook prints the memory index: one line per memory with its type, name, description and tags.
- Open a memory's file (`.agents/memories/<type>/<name>.md`) only when its description is relevant to the current task.
- Memories record what was true when they were written.
Before acting on a memory that names a file, function, flag or command, check that it still exists.
- If a memory conflicts with the code or with what the user says now, trust the present and fix or delete the memory.

### Types

Each type is a category with its own folder.

| Type | Holds | Git |
|---|---|---|
| `user` | Who the user is: role, expertise, personal preferences | local only, gitignored |
| `feedback` | How agents should work: corrections and approaches the user confirmed | shared |
| `project` | Goals, constraints, decisions, deadlines and context not visible in the code | shared |
| `reference` | Pointers to external resources: dashboards, tickets, docs, runbooks | shared |

`user` memories stay on the local machine but inside the project tree, so all memory lives in one place.
Anything the whole team should follow belongs in `feedback` or `project`, never in `user`.

### Format

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

- The header has exactly four fields: `name`, `description`, `type`, `tags`.
- `name` is kebab-case, equals the filename without `.md` and is unique across all types.
- `description` is one line under 200 characters, specific enough to judge relevance from the index alone.
- `type` equals the folder the file is in.
- `tags` is a list of 1 to 5 lowercase tags.
References are tags too, for example `jira:proj-12`, `svc:billing` or `report:plans/2026-10-01-memory-design.html`.
- The body holds one fact.
`feedback` and `project` memories add `**Why:**` and `**How to apply:**` lines.
- Use absolute dates (2026-10-01), never relative ones.
- Link related memories with `[[name]]`.

### When to write

Save:
- a correction or preference the user states about how to work,
- an approach the user confirmed worked, especially a non-obvious one,
- a decision, constraint or deadline that the code does not show,
- a pointer to an external resource the team relies on,
- who the user is and how they like to work (`user`, local).

Do not save:
- anything derivable from the code, git history, `AGENTS.md` or an existing memory,
- details that only matter to the current task,
- secrets, tokens, credentials or personal data about third parties.

### How to write

- Always use the `memory-manage` skill to create, update, delete or review memories.
- Update an existing memory instead of creating a near-duplicate.
- Delete memories that turn out to be wrong.
- A hook lints memory and report files after every write; fix any error it reports immediately.
- Run `.agents/tools/memory-lint` before pushing; CI runs it on every push and PR.

## Reports

- Write reports to `.agents/reports/<category>/YYYY-MM-DD-<slug>.<ext>`, never to the repo root or a temp folder.
- Categories: `plans`, `research`, `reviews`, `incidents`, `architecture`.
To add a category, create its folder with a `.gitkeep` file.
- Prefer one self-contained `.html` file; use `.md` for short text-only reports and `.svg` or `.png` for standalone diagrams.
- HTML style: plain light theme, light background, dark text, minimal CSS, system fonts, no dark mode, no heavy visual effects.
- Add simple diagrams where they aid explanation (flows, sequences, state machines, data models), as inline SVG or HTML/CSS boxes with few boxes, clear labels, thin lines, and no gradients or shadows.
- For architecture use the C4 model: one level per diagram, each labeled with its C4 level.
- Reports are committed and shared.
When a report holds a conclusion future sessions need, save a memory that points to it with a `report:<category>/<file>` tag.

## Git

- Never commit `.agents/memories/user/` contents (only its `.gitkeep` is tracked).
- Commit memory changes separately from code changes, with a `memory:` prefix.
- Do not commit or push unless the user asks.

## Template sync

Projects start as a GitHub fork of the agent-workspace template.
Pull template updates with:

```sh
git fetch upstream && git merge upstream/main
```

The template owns `AGENTS.md`, `.agents/skills`, `.agents/hooks`, `.agents/tools`, the base `.claude/` and `.codex/` settings and CI.
The project owns its memories, reports and local settings.
When resolving merge conflicts, keep project content and take template versions of template-owned files.
