# Plan — 20260714-0418-sai-agent-framework-cursor-cloud-30d8

## Current behavior

The repository has no agent infrastructure: no shared instructions, no stage
contracts, no memory, no reporting tooling, no hooks, no CI verification.

## Desired behavior

A version-controlled ICM workspace (arXiv:2603.16021) that lets the CEO
agent and both secretary agents work from the same instructions with
auditable, reviewable, stage-gated workflows and honest Slack/Drive
reporting.

## Proposed file changes (all new files)

| Path | Purpose |
|---|---|
| `.ai/CONTEXT.md` | Layer 0 workspace identity and map |
| `.ai/_config/{repositories.yaml,reporting.yaml,sync-policy.md,security-policy.md}` | Layer 3 policy |
| `.ai/agents/{ceo,secretary-dezocode,secretary-monaecode}/CHARTER.md` | Layer 1 agent charters (CEO + two secretaries) |
| `.ai/shared/memory/*` + `decisions/0001-*` | Durable memory seeded with verified facts |
| `.ai/shared/schemas/*.schema.json` | Event and stage-output JSON Schemas |
| `.ai/shared/references/{git-workflow,testing,release-policy}.md` | Stable references |
| `.ai/stages/<NN_stage>/CONTEXT.md` | Six stage contracts with inputs/process/outputs/verification/gates/rollback/provenance |
| `.ai/runs/README.md` + this run | Layer 4 conventions and first audit record |
| `.ai/audit/README.md` | Audit trail documentation |
| `.cursor/rules/sai-coordination.mdc` | Shared Cursor operating rules for both users' agents |
| `.githooks/*` | post-checkout/commit/merge/rewrite, pre-push, push wrapper |
| `scripts/{agent-report,agent-sync-drive,install-agent-hooks,verify-agent-audit}` | Reporting, Drive sync, bootstrap, CI audit |
| `.github/workflows/agent-audit.yml` | Server-side audit verification and push confirmation |

## Justification

Required by the shared operating prompt before coordinated multi-agent work
can begin; recorded as decision 0001.

## Verification planned

`bash -n` on every script/hook; JSON parse of schemas and metadata; YAML
parse of config; dry-run of `agent-report emit` (offline queue) and
`verify-agent-audit`; executable bits set.

## Risks and rollback

Low risk: new files only, no behavior change to existing content. Rollback:
delete the branch before merge (the pushed branch is inert until PR merge).

## Files claimed

See `metadata.json` `claimed_files`.

## Human review gates

The draft PR to `Dezocode/Sai:main` is the review gate; no hard security
gates are triggered (no deletions, force-pushes, releases, or credential
changes).
