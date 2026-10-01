#!/usr/bin/env python3
"""PostToolUse hook (Claude Code and Codex): lint memories and reports right after
an agent writes them, and feed any errors back so the agent fixes them in the
same turn.

Edited files come from:
  Claude  Write/Edit/MultiEdit -> tool_input.file_path
  Codex   apply_patch          -> "*** Add/Update File:" and "*** Move to:" lines
                                  in tool_input.command (relative to cwd)

Fail-open: any error exits 0 with no output.
"""
import importlib.util
import json
import re
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WATCHED = (ROOT / ".agents" / "memories", ROOT / ".agents" / "reports")
PATCH_PATH = re.compile(r"^\*\*\* (?:Add File|Update File|Move to): (.+)$", re.MULTILINE)


def load_lint():
    loader = SourceFileLoader("memory_lint", str(ROOT / ".agents" / "tools" / "memory-lint"))
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader(loader.name, loader))
    loader.exec_module(module)
    return module


def edited_paths(data):
    tool_input = data.get("tool_input") or {}
    cwd = Path(data.get("cwd") or ".")
    raw = []
    if isinstance(tool_input, dict):
        if isinstance(tool_input.get("file_path"), str):
            raw.append(tool_input["file_path"])
        if data.get("tool_name") == "apply_patch" and isinstance(tool_input.get("command"), str):
            raw.extend(m.strip() for m in PATCH_PATH.findall(tool_input["command"]))
    paths = []
    for r in raw:
        p = Path(r)
        p = (p if p.is_absolute() else cwd / p).resolve()
        if p.is_file() and any(w in p.parents for w in WATCHED):
            paths.append(str(p))
    return paths


def main():
    try:
        data = json.loads(sys.stdin.read() or "{}")
        paths = edited_paths(data)
        if not paths:
            return 0
        out = load_lint().lint(paths)
        if not out.errors and not out.warnings:
            return 0
        verdict = "FAILED" if out.errors else "passed with warnings"
        text = "\n".join(
            [f"memory-lint {verdict} for the file(s) you just wrote. Fix the errors now (rules: AGENTS.md, memory-manage skill):"]
            + out.errors + out.warnings
        )
        print(json.dumps({
            "hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": text}
        }))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
