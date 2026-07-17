# Intake — Mimi Dispatcher Bootstrap v2

- **Task**: `20260717-0229-mimi-dispatcher-bootstrap-mimi`
- **Contract**: `.ai/contracts/20260717-mimi-dispatcher-bootstrap-monaecode/` (issuer: Cora `ctr-admin`, active in registry)
- **Requester**: monaecode, in-chat, 2026-07-16 local / 2026-07-17 UTC: "fastforward my fork up to dezocode/sai:main then finish this contract".
- **Prior run**: `20260716-2122-mimi-dispatcher-bootstrap-mimi` — BLOCKED (contract artifacts not on disk). Now superseded: artifacts exist on `upstream/cursor/mimi-dispatcher-bootstrap-f1d6` and were imported to this branch; Cora is registered.

## Pre-work completed (evidence in events queue)

- Fork fast-forward: `origin/main` d091438 → 3c5c799 (= `upstream/main`), pushed with documented `SAI_AUDIT_BYPASS` (FAILs were in upstream-merged history: 29 merge-handoff gaps on 20260715 CEO/Cora commits, not new work).

## Scope

Deliverables M1–M6 per `contract.json`: Claude-native dispatcher profile (subagent, skills, settings), hooks/automation truth table, MCP connector verification, @mimi trigger documentation + stub workflow, charter amendment proposal, review package + PR to `Dezocode/Sai:main`.

## Out of scope (hard gates)

- No Splunky PoC or splunk-clone work before fulfillment gate.
- No registry `status`/power changes — proposal diff only.
- No merge; humans merge. No force-push, no channel creation.
