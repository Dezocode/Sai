# Verification — portable scaffold path guards

## Commands

```text
bash -n scripts/lib/agent-path-guards.sh: OK
bash -n scripts/agent-{scaffold,memory-scaffold,contract-scaffold,contract-pr-review}: OK
verify-scaffold-safety: OK (Linux)
verify-scaffold-safety: OK (simulated macOS — realpath -m unavailable, python3 fallback)
verify-agent-audit origin/main..HEAD: OK
verify-semantic-hierarchy: OK
```

## Portability fixes

1. `guard_normalize_path` — uses GNU `realpath -m` when available; falls back to `python3` `os.path.normpath(os.path.abspath(...))` on macOS.
2. `guard_json_safe_string` — replaced BSD-incompatible `grep` character class with portable `case` pattern matching.

## macOS simulation

PATH wrapper rejected `realpath -m`; python3 fallback resolved paths and all scaffold-safety regression checks passed.
