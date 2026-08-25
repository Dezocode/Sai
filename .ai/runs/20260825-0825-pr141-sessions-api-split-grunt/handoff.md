# Handoff — PR #141 line-budget split: sessions-api lane + registry RFC move out
Task-ID: 20260825-0825-pr141-sessions-api-split-grunt
PR: Dezocode/Sai#141
Author: grunt (ox-alpha)

## What
Removes from #141 per the owner-approved fleet split plan:
1. services/sessions-api/ (app.py, test_app.py, AGENTS.md, Dockerfile, ~1925 lines)
2. specs/2026-08-24-agent-runtime-registry.md (393 lines — the registry RFC belongs with the sessions-api lane it specs)

#141 retains: sai-cli-layer spec + prototype plugin + bookkeeping (~1130 additions, under 1200).
The removed material re-lands via follow-up branch specs/sessions-api (stacked from pre-split head b9c53c2) as a DRAFT lane.

## Why
PR line budget CI failed at 2624 vs 1200 (base = main). Owner ruled "approve all" ~07:20Z. First split attempt (4dabc12) removed services only → 1523, still over, and lacked the required Agent trailer. This amended commit fixes both. Force-with-lease push: own commit, pushed minutes prior, no downstream consumers (notified peer per crosscomm etiquette).

## Verify
- Diff vs main: only deletions for moved paths (deletions budget-free)
- Additions ≈ 1130 < 1200 — PR line budget passes
- Agent + Task-ID trailers present (agent-audit check)
- icm: claims for moved paths are harmless; completeness sweep flags only existing unmapped files
- Follow-up budget flag: specs/sessions-api carries ~2318 additions vs main — owner decision needed on sub-split vs exception before it opens beyond DRAFT
