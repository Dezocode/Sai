# Intake — Saul follow-up gates (PR #62 / #64)

## Requester

dezocode (`U0BHYH0NMCY`) via #agentupdates, forwarding ChatGPT/Saul state.
No formal GitHub review disposition was claimed in that run.

## Requested outcome

1. **PR #62** (`c8d21c0`, draft, mergeable): repair audit-valid path for ancestor `d14402e` invalid Task-ID grammar without weakening authorization; restore trusted Saul read-only review execution (bwrap namespace failure); rerun Saul on the then-current exact head. Do not treat infrastructure BLOCKED as APPROVE/REQUEST_CHANGES.
2. **PR #64** (`44ada88`, non-draft, conflicting): fix banner-prefixed Saul YAML so `consume-saul-contract-review` can ingest it; finish Cora admin + `ctr-code-ri1` registry binding; resolve three pre-contract authorization commits through an approved clean mechanism (no force-push); convert back to draft while exact-head gates are unsatisfied.

## Repository facts (verified)

- origin: `github.com/Dezocode/Sai` (canonical)
- default branch: `main` @ `40efe0a`
- this worktree: `cursor/codebase-health-90ba` @ `c8d21c0` (PR #62)
- PR #64 branch: `cursor/ri-subprocess-init-20260813` @ `44ada88`, base `cursor/codebase-health-90ba`, mergeable=CONFLICTING, isDraft=false

## Constraints

- No force-push / history rewrite (security-policy hard gate; prior PR comments said no force-push).
- No fake Saul APPROVE. BLOCKED from bwrap is infrastructure, not a review vote.
- Officer trailers are provenance, not authority (CTO-009). Implementation commits on PR #62 continue under existing v3 lease `lease-c3a003pr62q1` / `ctr-code-pr62smoke` / task `20260813-2017-pr62-queue-ctr-code`.
- Registry writes are denied to contractors; Cora/registry on PR #64 is a separate branch commit.

## Acceptance

- `verify-agent-audit origin/main..HEAD` no longer fails on `d14402e` grammar, while `verify-agent-authorization` stays fail-closed for post-cutoff commits.
- Codex invoke defaults to `-s danger-full-access` on the CapDrop runner.
- `load_yaml` / consume accept `=== path ===` prefixed YAML.
- GitHub commit status description is <= 140 characters.
- PR #64 is draft; disposition YAML is valid; pre-contract SHAs have a SHA-pinned skip; `ctr-code-ri1` is registry-bound as provisional.
