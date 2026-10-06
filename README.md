# Agent workspace template

A repository template that gives Claude Code and Codex one set of instructions, a shared file-based project memory, shared skills and hooks, and a home for reports.
Agent rules live in [AGENTS.md](AGENTS.md) and memory rules in [.agents/MEMORY.md](.agents/MEMORY.md); this README covers how to use the template.

## What you get

| Path | Purpose |
|---|---|
| `AGENTS.md` | Agent instructions, read by Codex directly and by Claude Code through `CLAUDE.md` |
| `.agents/MEMORY.md` | Memory rules plus a generated index of shared memories, read at session start |
| `.agents/memories/<type>/` | Project memory, one fact per file (`user` is local; `feedback`, `project`, `reference` are shared) |
| `.agents/skills/` | Shared skills: `memory-manage`, and `how` (adapted from [poteto/how](https://github.com/poteto/how), MIT) |
| `.agents/hooks/` | `redact-secrets.py` masks secrets; `memory-guard.py` lints memories and reports as they are written |
| `.agents/tools/` | `memory-lint`, `memory-index` and `memory-map` |
| `docs/` | Committed team documentation |
| `reports/<category>/` | Local, gitignored reports |
| `.claude/`, `.codex/` | Per-agent settings and hook registration |
| `.claude/agents/`, `.codex/agents/` | Subagents: `code-reviewer`, `security-auditor`, `test-engineer` and `web-performance-auditor` for both (from [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills), MIT), and the Claude-only `builder` |

CI runs `memory-lint` on every push and PR.
Example memories live on the `demo` branch.
Requires Git and Python 3.10+ (standard library only).

## Start a new project

1. Clone the template and keep it as `upstream`:

   ```sh
   git clone https://github.com/hoannc0506/agent-workspace.git my-project
   cd my-project
   git remote rename origin upstream
   ```

2. Push to your own empty repository:

   ```sh
   git remote add origin <your-project-repo-url>
   git push -u origin main
   ```

3. Add project instructions to `AGENTS.md` in a new section.
4. Open the project in Claude Code (`claude`, then approve the project hooks) or Codex (trust the project, then review hooks with `/hooks`).

Personal settings go in `.claude/settings.local.json` (gitignored) or `~/.codex/config.toml`.

## Daily use

- Ask an agent to "remember" something; it saves a memory with the `memory-manage` skill.
- Ask for plans, research or reviews; agents write them to `reports/<category>/`, and anything worth keeping moves to `docs/`.
- Run parallel work in worktrees under `.worktrees/<type>/<slug>`.
- Before pushing, run `.agents/tools/memory-lint`; view memories as a mind map with `.agents/tools/memory-map --open`.

## Related: agent-skills

[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) is a set of engineering skills, slash commands and subagents for coding agents, from spec and plan to build, review and ship.
This template does not need it: its subagents are copied into `.claude/agents/` and `.codex/agents/`, and the Claude-only `builder` subagent is a self-contained adaptation of its `/build` workflow.
Install it for the full skill set:

```sh
# Claude Code
/plugin marketplace add addyosmani/agent-skills
/plugin install agent-skills@addy-agent-skills

# Codex and other agents, through the skills CLI
npx skills add addyosmani/agent-skills
```

## Update from the template

```sh
git fetch upstream && git merge upstream/main
```

On conflicts, keep your project content and take the template version of template-owned files (listed in `AGENTS.md`).
