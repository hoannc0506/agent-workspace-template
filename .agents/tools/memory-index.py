#!/usr/bin/env python3
"""Regenerate the memory index in .agents/MEMORY.md from the memory headers.
Only the part below the marker line is rewritten; the rules above it are kept.

Usage:
  memory-index           rewrite .agents/MEMORY.md
  memory-index --check   exit 1 if .agents/MEMORY.md is out of date

Run it after every memory you create, update, rename or delete.
Local user memories are left out because the index is committed.
"""
import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_lint():
    loader = SourceFileLoader("memory_lint", str(ROOT / ".agents" / "tools" / "memory-lint.py"))
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader(loader.name, loader))
    loader.exec_module(module)
    return module


def main(argv):
    if any(a in ("-h", "--help") for a in argv):
        print(__doc__.strip())
        return 0
    lint = load_lint()
    rel = lint.INDEX.relative_to(ROOT).as_posix()
    if not lint.INDEX.is_file():
        print(f"memory-index: {rel} is missing")
        return 1
    current = lint.INDEX.read_text(encoding="utf-8")
    expected = lint.build_index(lint.load_memories(), current)
    if expected is None:
        print(f"memory-index: {rel} has no marker line: {lint.INDEX_MARKER}")
        return 1
    if "--check" in argv:
        if current != expected:
            print(f"memory-index: {rel} is out of date; run .agents/tools/memory-index.py")
            return 1
        print(f"memory-index: {rel} is up to date")
        return 0
    if current == expected:
        print(f"memory-index: {rel} is up to date")
        return 0
    lint.INDEX.write_text(expected, encoding="utf-8")
    print(f"memory-index: wrote {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
