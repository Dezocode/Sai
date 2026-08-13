# Handoff — 20260813-1752-saul-runner-cursor-cloud

## Disposition

**BLOCKED / REQUEST_CHANGES** — not READY FOR HUMAN REVIEW.

## Proven

- Self-hosted runner **hostinger-saul-codex** (`[self-hosted]`, Linux/X64, containerized, Codex 0.147.0).
- Real GitHub event → that runner → local `codex exec` with `codex_invoked: true`.
- Real Saul **REQUEST_CHANGES** (run **31729666256**, SHA `34b26f5`, comment 5284640842).
- Cora consume → contract `20260813-pr62-saul-smoke` **v1→v2** A-002 TRACE CTO-001/002/003.
- Stale v1 lease; contractor reload on v2 lease-5d635bef02b9.
- CTO-001/002/003 remediations implemented locally (human_gate, bootstrap.standing, job-level fork skip).

## Not proven

- Saul **APPROVE** of the exact current contract revision + exact HEAD.
- Sai independent APPROVE of the same (do not impersonate ceo).
- Human gate READY, stale-after-new-commit, restored READY.
- `pull_request_target` trusted-script isolation (CTO-1 P0 from run 31729323810).

## Next safe action

Push remediations; wait for a second `saul-cto-review` on hostinger-saul-codex. If Saul APPROVE, have registered **Sai (ceo)** record verification of the same SHA/revision. Do not merge. Do not mark ready.
