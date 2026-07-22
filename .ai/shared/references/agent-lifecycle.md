# Agent and contractor lifecycle (Layer 3)

Authoritative status enums for routing and audit. Narrative terms such as
"superseded" describe **why** an agent left active duty; they are not
substitutes for the `status` field.

## Registry (`registry.json`)

| `status` | Meaning |
|---|---|
| `provisional` | Scaffolded; ONBOARDING / persona gate incomplete |
| `active` | Principal + Sai audit complete; may receive work |
| `retired` | No new work; profile and `memory/` preserved for audit |

Valid values are enforced by `scripts/verify-semantic-hierarchy`.

## Contract (`assigned_contractors[]` in `contract.json`)

Uses the **same three values** as the registry (`provisional`, `active`,
`retired`). Schema: `.ai/shared/schemas/contract.schema.json`.

When a contractor slot is replaced by another agent on the same contract,
set `status` to `retired` and record the replacement in `note` (e.g.
"superseded by Splunky"). Do not invent alternate status strings such as
`superseded`.

## Reconciliation rule

For every assigned contractor, `assigned_contractors[].status` must match
`registry.json` `status` for the same `agent_id`. Mismatch blocks merge
until contract or registry is corrected.

## Related terms (not status enums)

| Term | Use |
|---|---|
| **superseded** | Audit narrative: agent replaced by a successor on the same project |
| **closed** | Whole contract `status` in `contract.json`, not per-agent |
| **deprecated** | Documents/automation specs replaced by a newer path |

## References

- Decision 0003 — contractor charters and per-agent memory
- `.ai/agents/README.md` — registry fields
- `.ai/shared/schemas/contract.schema.json`
