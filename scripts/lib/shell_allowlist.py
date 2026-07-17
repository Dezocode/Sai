#!/usr/bin/env python3
"""Claude Code-style Bash(...) allowlist matching for contract shell grants."""

from __future__ import annotations

import fnmatch
import re
from typing import Iterable

BASH_WRAPPER_RE = re.compile(r"^Bash\((.+)\)$")

# Commands that must never match any contractor shell allow entry (branch mutations).
HARD_GATED_GIT_BRANCH_COMMANDS: tuple[str, ...] = (
    "git branch -d feature/x",
    "git branch --delete feature/x",
    "git branch -D feature/x",
    "git branch -m old new",
    "git branch -M old new",
    "git branch --move old new",
    "git branch -c old new",
    "git branch -C old new",
    "git branch --copy old new",
    "git branch --list -D feature/x",
)

# Inner patterns that are never permitted in documented allowlists (wildcard delete/copy).
FORBIDDEN_INNER_PATTERNS: tuple[str, ...] = (
    "git branch *",
    "git branch-*",
)

SAFE_GIT_BRANCH_COMMANDS: tuple[str, ...] = (
    "git branch",
    "git branch --show-current",
    "git branch -a",
    "git branch -r",
    "git branch -vv",
    "git branch --list",
    "git branch --list proj/splunk-clone/ctr-code-splunky/task-slug",
    "git branch proj/splunk-clone/ctr-code-splunky/task-slug origin/main",
)

# Inner patterns that permit only an exact command string (no trailing args).
EXACT_ONLY_INNER_PATTERNS: frozenset[str] = frozenset(
    {
        "git branch",
        "git branch --show-current",
        "git branch -a",
        "git branch -r",
        "git branch -vv",
        "git branch --list",
    }
)


def parse_bash_entry(entry: str) -> str | None:
    entry = entry.strip()
    m = BASH_WRAPPER_RE.match(entry)
    if not m:
        return None
    return m.group(1).strip()


def inner_pattern_matches_command(command: str, inner: str) -> bool:
    """Return True if a shell command is permitted by one inner pattern."""
    command = " ".join(command.strip().split())
    inner = inner.strip()
    if not inner:
        return False

    if "*" not in inner:
        if inner in EXACT_ONLY_INNER_PATTERNS:
            return command == inner
        return command == inner or command.startswith(inner + " ")

    return fnmatch.fnmatchcase(command, inner)


def command_allowed(command: str, bash_entries: Iterable[str]) -> bool:
    for entry in bash_entries:
        inner = parse_bash_entry(entry)
        if inner is None:
            continue
        if inner_pattern_matches_command(command, inner):
            return True
    return False


def collect_allow_entries_from_bootstrap(data: dict) -> list[str]:
    block = data.get("shell_allowlist_after_phase_5b") or {}
    allow = block.get("allow") or []
    if not isinstance(allow, list):
        return []
    return [str(x) for x in allow]
