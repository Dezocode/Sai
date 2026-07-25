# Amendment: merge + paste deploy model (dezocode)

| Field | Value |
|---|---|
| **Date** | 2026-07-24 |
| **Authority** | dezocode — only two steps: merge and paste |
| **Applied by** | Cora (ctr-admin) |

## Requirement

Contract and prompts must be paste-ready. Alfred must know how to run/fill A0 from
repo scaffolds — no separate activation step, no missing script references.

## Changes

| Artifact | Change |
|---|---|
| `DEPLOY-MERGE-AND-PASTE.md` | Two-step procedure for dezocode |
| `first-prompt-attach-contract.md` | Single paste artifact; points to vps-bootstrap A0-1–A0-6 |
| `first-message-to-openclaw.md` | A0 uses existing scaffolds; merge+paste authorized |
| `vps-bootstrap.md` | Full dezocode prep + Alfred A0 executable steps |
| `verify-all-dependencies.sh` | A0 scaffold (new) |
| `verify-gateway-health.sh` | A0 scaffold (new) |
| `host/systemd/openclaw-gateway.service` | A0 template (new) |
| `contract.json` | `deployment.model: merge_and_paste` |
| `ACTIVATION-AND-MERGE-CHECKLIST.md` | Part B = deploy + paste; formal active after A0 |

## Paste blockers removed

- No `status: active` commit required before paste
- Missing A0 scripts no longer referenced without repo files
- Secrets: BLOCKED + MCQ path documented; not a pre-paste hard gate
