# Plan — symlink-aware scaffold path guards

## Problem

PR #10 `guard_normalize_path` used `realpath -m` on Linux (lexical only) and
`os.path.abspath` on macOS. Existing symlinks under `.ai/agents/<slug>` passed
containment checks while `agent-memory-scaffold` wrote outside the repository.

## Approach

1. Unify `guard_normalize_path` on python3 `normpath` (realpath-m semantics, no symlink follow).
2. Add `guard_reject_symlink_components` — reject any existing symlink component.
3. Add `guard_realpath_under_base` — physical resolution must stay under base.
4. Wire into `guard_agent_folder_rel` and `guard_under_ai_subtree`.
5. Add regression test in `verify-scaffold-safety` (isolated repo + symlink).

## Scope

- `scripts/lib/agent-path-guards.sh`
- `scripts/verify-scaffold-safety`
- Run artifacts only

## Out of scope

- Formal GitHub CTO review (blocked on invalid `gh` credential — human action).
- Drive sync (SAI_DRIVE_REMOTE unset).
