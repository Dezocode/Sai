#!/usr/bin/env python3
"""Verify Claude Code Bash allowlist entries do not permit destructive git branch ops.

Used by scripts/verify-scaffold-safety (PR #15 P1). Pattern matching mirrors
Claude Code permissions: Bash(exact) or Bash(prefix *) wildcard suffix.
"""
from __future__ import annotations

import fnmatch
import json
import sys
from pathlib import Path


def bash_pattern_to_fnmatch(entry: str) -> str | None:
    if not entry.startswith("Bash(") or not entry.endswith(")"):
        raise ValueError(f"not a Bash permission: {entry!r}")
    inner = entry[5:-1]
    if inner.endswith(" *"):
        return inner[:-2] + "*"
    return inner


def command_permitted(command: str, allow: list[str]) -> bool:
    cmd = command.strip()
    for entry in allow:
        pat = bash_pattern_to_fnmatch(entry)
        if fnmatch.fnmatchcase(cmd, pat):
            return True
    return False


DESTRUCTIVE_BRANCH_COMMANDS = [
    "git branch -D feature",
    "git branch -d feature",
    "git branch --delete feature",
    "git branch --force-delete feature",
    "git branch -D proj/splunk-clone/ctr-code-splunky/old",
]

SAFE_BRANCH_COMMANDS = [
    "git branch",
    "git branch --list",
    "git branch --list 'proj/*'",
    "git branch --show-current",
    "git branch proj/splunk-clone/ctr-code-splunky/new-task",
]


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "usage: verify-claude-shell-allowlist.py PATH/to/claude-desktop-bootstrap.json",
            file=sys.stderr,
        )
        return 2
    path = Path(sys.argv[1])
    doc = json.loads(path.read_text())
    block = doc.get("shell_allowlist_after_phase_5b") or {}
    allow = block.get("allow") or []

    forbidden_literals = ["Bash(git branch *)", "Bash(git *)", "Bash(gh *)"]
    for bad in forbidden_literals:
        if bad in allow:
            print(f"FAIL  bootstrap allow contains forbidden broad pattern: {bad}", file=sys.stderr)
            return 1

    for cmd in DESTRUCTIVE_BRANCH_COMMANDS:
        if command_permitted(cmd, allow):
            print(f"FAIL  destructive command permitted by allowlist: {cmd}", file=sys.stderr)
            return 1

    for cmd in SAFE_BRANCH_COMMANDS:
        if not command_permitted(cmd, allow):
            print(f"FAIL  safe command not permitted (regression): {cmd}", file=sys.stderr)
            return 1

    print("PASS  claude shell allowlist — git branch least-privilege")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
