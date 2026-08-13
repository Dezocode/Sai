# Plan — authorization, contract evolution, Codex/Saul loop

Decision record: `.ai/shared/memory/decisions/0006-agent-authorization-loop.md`
(accepted architecture, consistent with comment 5282088737).

## What will be built

1. Tracked policy `.ai/_config/authorization.yaml` plus schemas under
   `.ai/shared/schemas/` for task requests, leases, versioned contract
   revisions, Saul/Sai reviews, and amendments.
2. `.ai/requests/<task-id>/request.yaml` and versioned
   `.ai/contracts/<id>/revisions/vN.yaml` (immutable). `contract.json`
   remains the pointer for existing tools.
3. Scripts: `sai-authorize-task`, `sai-assume-agent`, `sai-release-agent`,
   `verify-agent-authorization`, `verify-contract-authorization`,
   `invoke-saul-review`, `consume-saul-contract-review`, plus
   `record-sai-verification` (Sai-identity gated).
4. Ephemeral `.git/sai-session.json` (untrusted). CI/hooks recompute from
   Git + tracked files. Commits whose trees lack the policy file are
   grandfathered. The introducing commit uses a documented bootstrap
   task-id and path allowlist (control-plane landing only).
5. Cora fallback: no applicable implementation agent → `CONTRACT_REQUIRED`
   → assume `ctr-admin` on cursor-cloud-vm → contract v1 + provisional
   contractor + branch/path scope + `PROVISIONAL_EXECUTION` lease →
   release Cora → assume contractor. Cora path class is contract-admin
   only (no product/implementation scripts).
6. Saul loop: GitHub event → `saul-review.yml` → `invoke-saul-review`
   loads Saul Codex profile → Codex CLI if `OPENAI_API_KEY` or
   `CODEX_API_KEY` is present → machine-readable YAML. Missing credentials
   write `disposition: BLOCKED` (`CODEX_UNAVAILABLE`), never APPROVE.
   Idempotency key `(contract, revision, sha, reviewer, review_type)`.
   Workflow never amends contracts (loop prevention).
7. Cora consume: ordinary findings → amendment + immutable vN+1 + stale
   leases. Authority-expanding findings → human-approval-required, no
   auto-grant. Contractor must re-assume against vN+1.
8. Dual exact-head gate: Saul APPROVE + Sai APPROVE/VERIFY of the same
   current revision and implementation SHA, Cora admin complete, CI green
   on that SHA, no stale approvals, no expansion gate. New SHA stale-s
   implementation approvals; new revision stale-s contract approvals.
9. pre-commit / commit-msg / pre-push / agent-audit.yml replay. Code-health
   registers `verify-agent-authorization --self-test` with synthetic
   fixtures actually executed.
10. Docs: INITIALIZE, ONBOARDING, Cora/Saul/Sai, security, reporting, CI
    policy, testing, architecture, repository map.

## Bootstrap (honest)

This Cloud Agent is unbound. Landing the control plane itself is a
one-time bootstrap (`Task-ID: 20260813-1517-auth-loop-cursor-cloud`)
allowed only for listed prefixes. After the policy file exists, later
implementation commits need a lease. E2E tests run in a temp clone and
exercise Cora/contractor identity transitions for real.

## Codex boundary

If GitHub has no OpenAI/Codex secret, items H/I/J/O/P (real Saul via
Actions) cannot pass. Item Y (unavailable → BLOCKED) can. The system will
be reported **BLOCKED**, not READY FOR HUMAN REVIEW, until a real GitHub
event invokes Codex as Saul.

## Verification

- `scripts/verify-agent-authorization --self-test`
- `scripts/verify-contract-authorization --self-test`
- `scripts/invoke-saul-review --self-test`
- `tests/authorization/run-e2e` (matrix A–Y)
- existing ICM suite (`verify-code-health --self-test` then live, audit,
  semantic, handoff)
- GitHub Actions run IDs recorded after push
