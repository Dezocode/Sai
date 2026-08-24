# Tab: Research — sessions + MCP gateway

| Field | Value |
|---|---|
| **Deliverable** | A5 |
| **Research** | [§6](../../../.ai/contracts/20260722-openclaw-dashboard-dezocode/research-integration-methods.md#6-research-tab-and-mcp-server) |
| **Services** | `services/research-mcp/` |
| **Subagent** | `.openclaw/agents/research-coordinator.md` |
| **Desktop route** | `/research` |

## Owner requirement

Archive and run **research agent sessions** (new + contracted) to:

- Compile sources and reasoning
- Propose verifiable improvements to foundation code / tech stack
- Benchmark CPU/GPU reductions
- Push **approved** findings into second brain as backlinkable notes
- Expose flexible context gateway as **MCP server** for all SAI agents

## Tech stack

| Layer | Choice |
|---|---|
| Session UI | React wizard + session list per `contract_id` |
| Runtime | OpenClaw subagent `research-coordinator` |
| Output | JSON → human review gate → vault markdown |
| MCP | `research-mcp`: archive_source, propose_improvement, link_to_vault |

## Dependencies

- A4 second brain (vault-mcp)
- A0 Gateway healthy
- Registry + `.ai/contracts/*` for contracted agents

## Verification

- [ ] End-to-end: source → session → vault note → MCP query
- [ ] Decision record draft path documented for `.ai/shared/memory/decisions/`

Build: [BUILD.md](./BUILD.md)
