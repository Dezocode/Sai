# Handoff — Runtime Intelligence init (PROVISIONAL + CONTRACT_DRAFTED)

## Exact state
- Parent PR: #62 (`cursor/codebase-health-90ba` @ de821c7)
- Stacked sub-PR: #64 `cursor/ri-subprocess-init-20260813` (**draft**)
- Task-ID: `20260813-1945-ri-subprocess-init`
- Contract-ID: `20260813-ri-subprocess-init` revision **v3**
- Contractor: `ctr-code-ri1` (active lease `lease-774a407c44b4`; v2 lease stale)
- Saul last exact-head: run `31745529943` REQUEST_CHANGES on `c32303f` (CTO-004/005/006)
- Organizational status: **PROVISIONAL — NOT INITIALIZED**

## Decision 0006 path (turn 3)
1. authorize-task → CONTRACT_REQUIRED
2. assume Cora (cursor-cloud-vm) → create contract v1 + lease
3. Cora committed contract artifacts
4. assume contractor for provisional implementation
5. Fixed worktree session + `.ai` glob_match lstrip bug in `scripts/lib/sai_auth.py`

## Follow-up 2026-08-13 (ChatGPT/Saul state)
- Converted PR #64 to draft while exact-head gates are unsatisfied
- Stripped `=== path ===` banner from tracked Saul disposition YAML
- SHA-pinned `skip_commits_missing_contract_at_or_before` at `46e73c3` (no force-push)
- Provisional registry binding for `ctr-code-ri1`; Cora admin marked complete on v2
- Merged parent PR #62 `de821c7` (Saul CapDrop sandbox + audit grammar pin)

## Approvals still required
1. Saul technical APPROVE (formal Codex path) on the new exact head
2. Sai governance APPROVE of the same SHA
3. Explicit human admission

## CI honesty
Pre-contract commits lack Contract-ID. No force-push. Replay skip is SHA-pinned
to `46e73c3` only. New commits carry full trailers.

## Never
merge main / force-push / mark-ready / self-declare ACTIVE
