---
name: sai-icm-contract
description: SAI ICM protocol and contract 20260715-splunk-clone-monaecode — use for task IDs, runs, Slack reporting, PR reviews, and ONBOARDING gates.
---

# SAI ICM + Splunk contract

## Load

- `.ai/ONBOARDING.md`
- `.ai/contracts/20260715-splunk-clone-monaecode/contract.json`
- `.ai/agents/splunky/hooks.json`

## Every task

1. Create `.ai/runs/<task-id>/metadata.json` with contract fields.
2. Post PLAN before edits (Slack + run artifacts).
3. Commit trailers: `Task-ID`, `Agent: Splunky`, `Report-Event`.
4. Run `scripts/agent-contract-pr-review` before requesting human merge.

## Channels

- `#splunk-clone-project` — PR bookends
- `#agentupdates` — CONTRACT, PERSONA_GATE, HANDOFF
