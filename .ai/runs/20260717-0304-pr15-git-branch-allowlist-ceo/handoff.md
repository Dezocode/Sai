# Handoff — PR #15 git branch allowlist (P1)

## Done

- Replaced `Bash(git branch *)` in `claude-desktop-bootstrap.json` with least-privilege entries (list, show-current, contract-prefix branch create).
- Documented branch deletion in `explicitly_excluded`.
- Added `scripts/lib/verify-claude-shell-allowlist.py` and wired it into `verify-scaffold-safety` (CI).

## Verification

- `python3 scripts/lib/verify-claude-shell-allowlist.py .ai/contracts/.../claude-desktop-bootstrap.json` → PASS
- `scripts/verify-scaffold-safety` → OK

## Next

- monaecode: merge approved allowlist into `splunk-clone/.claude/settings.json` after Splunky Phase 5B.
- dezocode: re-review PR #15 thread on git branch permissions.
