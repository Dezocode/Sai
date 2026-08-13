# Saul sandbox fix (turn 5)

## MEASURED FACT
- Saul container CapDrop=ALL + no-new-privileges → `unshare`/`bwrap` fail
- Host `kernel.unprivileged_userns_clone=1` insufficient inside that container
- Formal run 31738840708: disposition BLOCKED FINAL_REVIEW_PACKAGE_UNREADABLE
- Probe inside container: `codex exec -s danger-full-access` succeeds (exit 0)

## FIX
`scripts/lib/sai_auth_review.py` `_codex_cmd()` default sandbox =
`danger-full-access` (Docker-isolated Saul runner is the outer sandbox).
Override with `SAI_CODEX_SANDBOX=read-only|workspace-write|bypass`.

## Contract
v2 amendment A-RI-001 expands paths for this fix + code-health orphan allowlist.

## Status
Still PROVISIONAL. Must re-dispatch formal Saul and obtain APPROVE before ACTIVE.
