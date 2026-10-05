# Agent instructions

## General guidelines

- Never use the em dash "-". Use plain dash "-" instead.
- When writing commit messages, NEVER auto-add your agent name as co-author.
- Never manually modify CHANGELOG.md files or any files that are marked as auto-generated.
- When writing or substantially editing long Markdown files, put each full sentence on its own line.
- When making technical decisions, prefer quality, simplicity, robustness, scalability and long term maintainability over development cost.
- For bug fixes, first reproduce the bug end to end, as close as possible to how a user would hit it.
- When testing a product end to end, be picky about the UI and fix anything that clearly looks off, even if unrelated.
- Hold the same bar for lint errors, test failures and flaky tests: fix them even when you did not cause them.

## Workspace layout

```
AGENTS.md                 instructions for all agents (this file)
CLAUDE.md                 imports AGENTS.md for Claude Code
.agents/                  shared by every agent
  MEMORY.md               memory rules and index; read at session start
  memories/<type>/        project memory, one fact per .md file
  skills/<skill>/SKILL.md shared skills (.claude/skills links here)
  hooks/                  hook scripts used by both agents
  tools/                  CLI tools (memory-lint, memory-index, memory-map)
docs/                     committed documentation shared with the team
reports/<category>/       local reports, gitignored
.claude/  .codex/         settings for one agent only
.worktrees/<type>/<slug>/ local git worktrees, gitignored
```

- Put anything both agents use in `.agents/`; add skills only in `.agents/skills/`.
- Register every hook in both `.claude/settings.json` and `.codex/config.toml`.
Hooks are standard-library Python and fail open (exit 0 on internal errors).

## Memory

- At the start of every session, read `.agents/MEMORY.md`: the memory rules and an index of shared memories.
Also read every file in `.agents/memories/user/` (local, not indexed).
- Use the `memory-manage` skill for every memory change, then run `.agents/tools/memory-index`.
- Keep project memory only in `.agents/memories`; never write to `~/.claude/projects/*/memory`, Codex memories or any other user-scope memory.

## Reports and docs

- Write reports to `reports/<category>/YYYY-MM-DD-<slug>.<ext>` (`plans`, `research`, `reviews`, `incidents`, `architecture`); they are gitignored.
- Prefer one self-contained `.html` file: plain light theme, system fonts, minimal CSS, no dark mode or heavy effects.
- Add simple diagrams where they help: inline SVG or HTML boxes, thin lines, no gradients or shadows; C4 model, one level per diagram, for architecture.
- Move anything the team or future sessions need into `docs/` (committed, `.md` by default) and never reference a report from a shared memory.

## Git

- Follow Conventional Commits: `<type>(<scope>): <short imperative summary>`, with type `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`, `build`, `ci` or `revert`.
- Verify Git's author identity before committing.
- Commit memory changes separately with a `memory:` prefix, including the regenerated `.agents/MEMORY.md`; never commit `.agents/memories/user/`.
- Do not commit or push unless the user asks.

## Worktrees

- Create worktrees only as `.worktrees/<type>/<slug>` on a branch of the same name: `git worktree add .worktrees/<type>/<slug> -b <type>/<slug>`.
- `<type>` is the Conventional Commits type; `<slug>` is 1 to 3 kebab-case words, with no dates, tickets, agent names or random suffixes.
- Remove the worktree and branch once it is merged or abandoned.

## Template sync

- The template is the `upstream` remote; update with `git fetch upstream && git merge upstream/main`.
- The template owns `AGENTS.md`, `.agents/skills`, `.agents/hooks`, `.agents/tools`, the base `.claude/` and `.codex/` settings, CI and the rules part of `.agents/MEMORY.md`.
- The project owns its memories, the memory index, docs, reports and local settings; on conflicts keep project content and take template versions of template-owned files.
