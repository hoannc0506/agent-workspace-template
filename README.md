# Agent workspace template

A repository template that gives coding agents a shared, file-based project memory, shared skills and hooks, and a home for reports.
It ships ready-made settings for Claude Code and Codex, so both agents follow the same instructions in one repository.
All agent rules live in [AGENTS.md](AGENTS.md); this README covers how to use the template.

## What you get

| Path | Purpose |
|---|---|
| `AGENTS.md` | Single source of agent instructions, read by Codex directly and by Claude Code through `CLAUDE.md` |
| `.agents/MEMORY.md` | Memory index, one line per shared memory, read by agents at session start |
| `.agents/memories/<type>/` | Project memory, one fact per Markdown file (`user`, `feedback`, `project`, `reference`) |
| `docs/` | Committed documentation shared with the team |
| `reports/<category>/` | Local, gitignored reports (`plans`, `research`, `reviews`, `incidents`, `architecture`) |
| `.agents/skills/` | Shared skills; `.claude/skills` is a symlink here |
| `.agents/hooks/` | Standard-library Python hooks registered for both agents |
| `.agents/tools/` | `memory-lint`, `memory-index` and `memory-map` CLIs |
| `.claude/settings.json` | Claude Code project settings and hook registration |
| `.codex/config.toml` | Codex project settings and hook registration |
| `.github/workflows/agents-lint.yml` | CI that runs `memory-lint` on every push and PR |

Hooks, wired up for both agents:

- `redact-secrets.py` (prompt submit and tool output) masks secrets in tool output and blocks prompts that contain a known token.
- `memory-guard.py` (after file edits) lints memories, the memory index and reports as soon as an agent writes them.

The memory index is a committed file, not a hook: `AGENTS.md` tells agents to read `.agents/MEMORY.md` at session start, and `.agents/tools/memory-index` regenerates it after every memory change.
`memory-lint` (and CI) fails when the index is out of date.

Skills, shared by both agents:

- `memory-manage` saves, updates, deletes and reviews project memories.
- `how` explains how part of the codebase works, and can optionally critique its architecture.
Adapted from [poteto/how](https://github.com/poteto/how) (MIT, see `.agents/skills/how/LICENSE`) at commit `b1ef429`, with subagent settings made agent-neutral for Claude Code and Codex.

Codex built-in memory is enabled; Claude Code built-in memory is disabled.
Shared project memory lives in `.agents/memories` for both agents.

## Requirements

- Git and Python 3.10 or newer (hooks and tools use only the standard library).
- Claude Code, Codex, or both.

## Start a new project

1. Create your project from the template, keeping its history so template updates merge cleanly:

   ```sh
   git clone https://github.com/hoannc0506/agent-workspace.git my-project
   cd my-project
   git remote rename origin upstream
   ```

2. Create an empty repository for the project on GitHub and push to it:

   ```sh
   git remote add origin <your-project-repo-url>
   git push -u origin main
   ```

   With the GitHub CLI, `gh repo create <name> --private --source . --push` does the same in one step.
   A GitHub fork also works, but GitHub does not allow forking into the account that owns the template.

3. Remove the demo memories (all tagged `demo`) and anything else you do not need:

   ```sh
   grep -rl '^tags:.*\bdemo\b' .agents/memories | xargs -r rm
   .agents/tools/memory-index
   ```

4. Add your project's own instructions to `AGENTS.md` under a new section, keeping the template sections intact so template updates merge cleanly.
5. Open the project in your agents:
   - Claude Code: run `claude` in the repository and approve the project hooks when asked.
   - Codex: open the project, trust it so `.codex/config.toml` loads, then review and trust the hooks with `/hooks`.
6. Ask the agent what is in the memory index; it should answer from `.agents/MEMORY.md`.

Personal Claude Code settings go in `.claude/settings.local.json` (gitignored).
Personal Codex settings go in `~/.codex/config.toml`.
The shared `.codex/config.toml` contains only hook registration and the repository memory policy, leaving model, reasoning effort, personality, approval policy, sandbox mode and UI preferences to each user.
Codex project configuration overrides user configuration; see [configuration precedence](https://learn.chatgpt.com/docs/config-file/config-basic).
The `.codex/*.local.*` ignore rule keeps local files out of Git but does not make Codex load them automatically.

## Daily use

- Ask an agent to "remember" a decision, correction or pointer; it saves a memory with the `memory-manage` skill.
- `user` memories (who you are, how you like to work) stay local and are never committed.
`feedback`, `project` and `reference` memories are shared with the team through git.
- Ask for plans, research or reviews as reports; agents write them to `reports/<category>/YYYY-MM-DD-<slug>.html`, which is gitignored.
Move anything the team should keep into `docs/`.
- Run parallel work in worktrees under `.worktrees/<type>/<slug>` (see `AGENTS.md`).

Lint memories and reports before pushing (CI runs the same check):

```sh
.agents/tools/memory-lint
```

View all memories as a mind map:

```sh
.agents/tools/memory-map --open
```

## Update from the template

```sh
git fetch upstream && git merge upstream/main
```

The template owns `AGENTS.md`, `.agents/skills`, `.agents/hooks`, `.agents/tools`, the base `.claude/` and `.codex/` settings and CI.
Your project owns its memories, memory index, docs, reports and local settings.
On conflicts, keep your project content and take the template version of template-owned files.

## Change the template itself

Work in this repository and follow the conventions in `AGENTS.md`:

- Add a skill as `.agents/skills/<name>/SKILL.md`.
- Add a hook to `.agents/hooks/` and register it in both `.claude/settings.json` and `.codex/config.toml`.
Hooks must be standard-library Python and exit 0 on internal errors.
- Run `.agents/tools/memory-lint` before pushing.
