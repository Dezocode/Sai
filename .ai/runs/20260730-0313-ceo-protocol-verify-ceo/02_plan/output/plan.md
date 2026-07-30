# Plan — 20260730-0313-ceo-protocol-verify-ceo

## Trigger

Saul CTO review (`20260730-0312-cto-verified-pr-governance-dezo-sec-codex1`) tagged
`@sai` with PR #51 REQUEST_CHANGES: INITIALIZE.md claims full
`agent-event.schema.json` enforcement but verifiers only checked a subset.

## Scope (CEO purpose only)

1. Add stdlib `scripts/lib/validate-agent-event.py` with negative self-test.
2. Wire full schema validation into `verify-semantic-hierarchy` and
   `verify-agent-audit`; add CI self-test step.
3. Remediate tracked historical `events.jsonl` rows that fail the schema.
4. Merge prior INITIALIZE hardening from PR #51 branch (`9be2`) — claim is
   now true after verifier work.
5. Post VERIFY to #agentupdates; push branch for human review (no merge).

## Out of scope

- PR merge/close, Alfred activation, contractor remediation on their branches.
- Drive credential provisioning.
