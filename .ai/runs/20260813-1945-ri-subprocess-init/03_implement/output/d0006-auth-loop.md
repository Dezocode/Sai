# Decision 0006 authorization loop (turn 3)

## Measured sequence
1. `scripts/sai-authorize-task --task-id 20260813-1945-ri-subprocess-init` → **CONTRACT_REQUIRED**
2. Worktree session bug: `.git` is a file → `save_session` failed (fixed in working tree; committed by contractor after Cora).
3. `scripts/sai-assume-agent ctr-admin --task-id … --runtime cursor-cloud-vm` → **ASSUMED Cora**
4. `scripts/sai-authorize-task … --create-contract` → **CONTRACT_DRAFTED**
   - contract_id: `20260813-ri-subprocess-init`
   - revision: v1
   - contractor: `ctr-code-ri1`
   - lease: provisional
5. Cora commits contract artifacts only (no product/control-plane scripts).
6. Release Cora → assume `ctr-code-ri1` for provisional implementation commits.
7. Org status remains **PROVISIONAL**. Saul/Sai/human still PENDING.
8. Pre-contract commits on this branch lack Contract-ID trailers (CI red until rewritten or waived; **no force-push**).

## Evidence paths
- `/root/skill-lab/evidence/deep-fulfillment-job-20260813T194159-edd0a4f4/d0006-authorize-task.txt`
- `…/d0006-assume-cora.txt`
- `…/d0006-create-contract.txt`
- `.ai/contracts/20260813-ri-subprocess-init/`
