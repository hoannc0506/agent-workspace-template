# Agent workspace template

A repository template that gives Claude Code and Codex a shared, file-based project memory, shared skills and hooks, and a home for reports.
All agent rules live in [AGENTS.md](AGENTS.md).

## Start a project

1. Fork this repository on GitHub (into an org or another account, since GitHub does not allow forking into the owner's own account), then clone the fork.
2. Track the template for updates:

   ```sh
   git remote add upstream <template-repo-url>
   ```

3. Open the project in Codex and trust it, then review and trust the project hooks with `/hooks`.

## Update from the template

```sh
git fetch upstream && git merge upstream/main
```

## Check memories and reports

```sh
.agents/tools/memory-lint
```
