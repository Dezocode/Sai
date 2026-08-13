# Handoff — Runtime Intelligence init (PROVISIONAL + CONTRACT_DRAFTED)

## Exact state
- Parent PR: #62 (`cursor/codebase-health-90ba` @ d113fa0)
- Stacked sub-PR: #64 `cursor/ri-subprocess-init-20260813`
- Task-ID: `20260813-1945-ri-subprocess-init`
- Contract-ID: `20260813-ri-subprocess-init` revision **v1**
- Contractor: `ctr-code-ri1` (provisional lease `lease-b78e136152e2`)
- Organizational status: **PROVISIONAL — NOT INITIALIZED**

## Decision 0006 path (turn 3)
1. authorize-task → CONTRACT_REQUIRED
2. assume Cora (cursor-cloud-vm) → create contract v1 + lease
3. Cora committed contract artifacts
4. assume contractor for provisional implementation
5. Fixed worktree session + `.ai` glob_match lstrip bug in `scripts/lib/sai_auth.py`

## Approvals still required
1. Saul technical APPROVE (formal Codex path)
2. Sai governance APPROVE
3. Explicit human admission

## CI honesty
Pre-contract commits lack Contract-ID. No force-push. New commits carry full trailers.

## Never
merge main / force-push / mark-ready / self-declare ACTIVE
