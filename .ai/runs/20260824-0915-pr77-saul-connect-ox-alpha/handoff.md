# Handoff — 20260824-0915-pr77-saul-connect-ox-alpha

## What changed
- headMismatch(s,prHead) helper: session head prefixes can no longer suppress the mismatch flag; head_full or exact head must equal authoritative HEAD (Saul 97373399655). Four unit locks.
- probeSessions(): periodic GET of SESSIONS_URL on every load cycle even when /prs is preferred — acceptance requires the live read-only sessions GET regardless of preferred plane (Saul 97376638286). Needle-locked.
- cmd/sai-verify/main.go pathRe: .gitignore added as standalone alternative — it was structurally unclaimable, leaving unmapped() dirty and failing TestLinkedWorktreeHook + anti-regression preserve.

## Verification
py_compile OK; --selftest ALL PASS; --check ALL PASS features=11 + prs-probe; go vet + full go test ./cmd/sai-verify ALL PASS locally incl TestLinkedWorktreeHook.
