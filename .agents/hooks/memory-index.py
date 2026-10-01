#!/usr/bin/env python3
"""SessionStart hook (Claude Code and Codex): print the memory index.

Builds one line per memory from its header, so no index file is committed and
teammates never conflict on one. Plain stdout becomes model context on both
agents. Fail-open: any error prints nothing and exits 0.
"""
import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_lint():
    loader = SourceFileLoader("memory_lint", str(ROOT / ".agents" / "tools" / "memory-lint"))
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader(loader.name, loader))
    loader.exec_module(module)
    return module


def build_index(lint):
    memories = lint.load_memories()
    lines = [
        "# Project memory index",
        "Memories live in .agents/memories/<type>/<name>.md. Read a file only when its description is relevant to the task.",
        "Create, update or delete memories only with the memory-manage skill. Rules are in AGENTS.md.",
    ]
    if not memories:
        lines.append("(no memories yet)")
    for typ in lint.TYPES:
        group = [m for m in memories if m.folder == typ]
        if not group:
            continue
        suffix = " (local, not committed)" if typ in lint.LOCAL_TYPES else ""
        lines.append(f"\n## {typ}{suffix}")
        for m in sorted(group, key=lambda m: m.path.name):
            if m.parse_error or not m.name:
                lines.append(f"- {m.path.stem}: (invalid header, run .agents/tools/memory-lint)")
                continue
            tags = m.fields.get("tags")
            tag_text = f" [{', '.join(tags)}]" if isinstance(tags, list) and tags else ""
            lines.append(f"- {m.name}: {m.fields.get('description', '')}{tag_text}")
    stray = [m for m in memories if m.folder not in lint.TYPES]
    if stray:
        lines.append("\n## misplaced (run .agents/tools/memory-lint)")
        lines.extend(f"- {m.rel}" for m in stray)
    return "\n".join(lines)


def main():
    try:
        sys.stdin.read()
        print(build_index(load_lint()))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
