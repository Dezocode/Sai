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
  Second production review run **31730478466** on `1552da5` is still
  **REQUEST_CHANGES** (CTO-004 P0 officer-trailer trust, CTO-005 P0
  persistent-runner executes PR checkout, CTO-006 bootstrap expiration,
  CTO-007 null contract_id on detached PR checkout).
- Sai independent APPROVE of the same (do not impersonate ceo).
- Human gate READY, stale-after-new-commit, restored READY.
- `pull_request_target` / trusted-scripts-from-main isolation.

## Next safe action

Do not merge. Have a follow-on implement CTO-004/005/006 with co-founder
review. Detect-contract now also matches `GITHUB_HEAD_REF` so PR jobs bind
`20260813-pr62-saul-smoke`. Registered **Sai (ceo)** must record
verification; this unbound runtime will not assume `ceo`.
