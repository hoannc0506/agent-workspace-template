---
name: memory-manage
description: Save, update, delete or review project memories in .agents/memories. Use when the user says "remember this", "forget that" or corrects how you work, when you learn a durable fact worth keeping for future sessions (a decision, constraint, preference or external pointer), or when asked to review or clean up memories.
---

# memory-manage

Project memory is a folder of Markdown files, one fact per file, in `.agents/memories/<type>/<name>.md`.
`.agents/MEMORY.md` holds the rules (types, file format, what to save) and, below a marker line, the index of shared memories that `.agents/tools/memory-index.py` generates.
Follow those rules; this skill is the procedure.
Regenerate the index after every change; `memory-lint` fails while it is out of date.

## Save

1. Check it is worth saving: not already in the code, git history, `AGENTS.md` or another memory, and useful beyond the current task.
2. Pick the type, which picks the folder.
3. Search for an existing memory on the same fact: scan `.agents/MEMORY.md`, then `grep -ril <keyword> .agents/memories`.
   If one exists, update it instead of creating a new file.
4. Write the file with `update_at` set to today.
5. Run `.agents/tools/memory-index.py` to add it to `.agents/MEMORY.md`.
6. Run `.agents/tools/memory-lint.py <file>` and fix every error.
7. Tell the user in one line what you saved and where.

## Update

1. Edit the file in place; keep it one fact; set `update_at` to today.
2. If the name changes, rename the file to match and update every `[[old-name]]` link (`grep -rl "\[\[old-name\]\]" .agents/memories`), bumping `update_at` on each file you touch.
3. Run `.agents/tools/memory-index.py` so the index matches the new name, description or tags.
4. Run `memory-lint` on the changed files.

## Delete

Delete when the user asks to forget something or a memory turns out to be wrong.

1. Remove the file.
2. Remove or repoint every `[[name]]` link to it, bumping `update_at` on each file you touch.
3. Run `.agents/tools/memory-index.py` to drop it from the index.
4. Run `.agents/tools/memory-lint.py` (no arguments) and fix any new warnings.
5. Tell the user what was deleted.

## Review

Run when asked to review, consolidate or clean up memories.

1. Merge memories that state the same fact; keep the clearer name and fix links.
2. Verify facts against the repo: files, functions, flags and commands a memory names must still exist.
   Fix or delete stale ones.
3. Convert relative dates to absolute ones and split memories that hold more than one fact.
4. Normalize tags so the same concept uses the same tag.
5. Run `.agents/tools/memory-index.py`, then `.agents/tools/memory-lint.py` with no arguments until it reports 0 errors.
6. Summarize the changes (merged, updated, deleted) so the user can review them in a PR.

## Git

- Never commit anything in `.agents/memories/user/`.
- Commit memory changes separately from code changes, with a `memory:` prefix, e.g. `memory: add run-e2e-before-fix`.
Include the regenerated `.agents/MEMORY.md` in the same commit.
- Do not commit unless the user asks; shared memories reach the team through a reviewed PR.
