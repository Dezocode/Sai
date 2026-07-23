# Plan — Grok Build runtime research (pre-contract)

## Current vs desired

| Current | Desired (this task) |
|---|---|
| SAI runtimes: `cursor`, `claude` (+ Agent SDK), `codex` (decision 0002) | Evidence-based verdict on whether Grok Build requires `runtimes/grok/` |
| Agent primary suites unevenly scaffolded | Written critique vs docs; prioritized gaps — **no live scaffold edits** |
| No Grok enum / Layer 0 entry / contract template | Research recommendations + proposed decision draft only |

## Work to perform

1. **Intake** — repo facts, claims check, task ID, Slack INTAKE.
2. **Plan** — this file; Slack PLAN before research write-up commit.
3. **Research implement (docs only under run dir)**  
   - Map Grok harness tiers (binary/auth/API → config/rules/tools/sessions →
     skills/agents → ops) to SAI Layer 0–4 and runtime-adapter model.  
   - Compare Grok modes (TUI / headless `-p` / ACP `grok agent stdio`) to
     Cursor / Claude Code / Codex automation models.  
   - Audit sai/mimi/saul/cora/alpha runtime folders vs
     `agent-runtimes.md` + `claude-agent-sdk.md`.  
   - Produce `03_implement/output/research-report.md` + proposed decision
     draft (not under `shared/memory/decisions/` yet).
4. **Verify** — JSON lint on run artifacts; `verify-semantic-hierarchy`;
   note what was *not* changed.
5. **Review/handoff** — co-founder gate: accept/reject new-runtime decision
   before any contract or schema change.
6. **Publish** — commit run artifacts only; push branch; open draft PR;
   Slack COMMIT/PUSH/PR/HANDOFF.

## Files claimed

Only:

- `.ai/runs/20260722-2341-grok-build-runtime-research-ctr-admin/`

Explicitly **not** claimed (future contract/decision task):

- `.ai/shared/references/agent-runtimes.md`
- `.ai/shared/memory/decisions/*`
- `.ai/shared/schemas/contract.schema.json`
- `scripts/agent-scaffold`, `scripts/agent-contract-scaffold`
- `.ai/contracts/_templates/*`
- `GROK.md`, `.ai/agents/*/runtimes/grok/`

## Justification

Research-only artifacts keep ICM audit trail without colliding with stale
ctr-admin claims or prematurely expanding the runtime enum. Architectural
change requires a reviewed decision before scaffolding or contracts.

## Verification

- `python3 -m json.tool` on run JSON
- `scripts/verify-semantic-hierarchy`
- `scripts/verify-agent-audit -n 5 HEAD` after commit
- `scripts/verify-merge-handoff origin/main..HEAD` after handoff present

## Risks / rollback

- Risk: treating Claude-compatible rule loading as “no new runtime needed.”
  Mitigation: document independent config, permissions, ACP, hooks trust,
  `/loop` automation.
- Rollback: abandon run dir + branch if co-founders reject research scope.

## Human review gates

- **Required before any future implementation:** new decision record
  (supersedes/extends 0002), schema enum change, scaffold script changes,
  Layer 0 `GROK.md`, first Grok-primary agent registration.
- This research PR is informational; merge optional after co-founder read.

## Provenance

Intake `01_intake/output/intake.md`; decision 0002; `agent-runtimes.md`;
`claude-agent-sdk.md`; xAI Grok Build public docs; requester harness notes.
