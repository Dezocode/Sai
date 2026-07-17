# Contract: Cybersecurity Splunk Clone

| Field | Value |
|---|---|
| **Contract ID** | `20260715-splunk-clone-monaecode` |
| **Amendment** | `20260716-splunky-intake-monaecode` |
| **Project** | Cybersecurity Splunk Clone (`splunk-clone`) |
| **Principal** | monaecode (U0BGNS7F0T1) |
| **Contractor** | **Splunky** (`ctr-code-splunky`) |
| **Contractor type** | coding (PM + lead design + senior engineering) |
| **Isolation** | **prototype** — all product code under `splunk-clone/` on `monaecode/Sai` |
| **Integration (later)** | SAI umbrella **plugin** for cybersecurity & network monitoring (no core coupling until gate) |
| **Runtime** | Claude Code / Claude Desktop (`claude-code-cli`) |
| **Repository** | `monaecode/Sai` (fork) |
| **Product root** | `splunk-clone/` |
| **Branch pattern** | `proj/splunk-clone/ctr-code-splunky/<task-slug>` |
| **Slack channel** | `#splunk-clone-project` (**owner must approve** channel creation) |
| **ICM agent folder** | `.ai/agents/splunky/` |

## Splunk domain mandate

Splunky acts as a **Splunk and SIEM domain expert**: Splunk Enterprise/Cloud capabilities (forwarders, indexing, SPL/search, CIM, apps, dashboards, alerts, RBAC, data models, ITSI/ES patterns) and **competitor best practices** (Elastic Security, Wazuh, Graylog, Microsoft Sentinel, QRadar-class patterns). Deliverables must document tradeoffs and the **MVP subset** appropriate for a future SAI parental cybersecurity plugin.

## Slack PR protocol (mandatory)

Before **every** PR (open, update, ready-for-review):

1. Post `[SAI][PLAN][<task-id>]` to `#splunk-clone-project` with scope, branch, and acceptance criteria touched.

After **every** push that updates a PR:

2. Post `[SAI][VERIFY][<task-id>]` with PR URL, short SHA, and `agent-contract-pr-review` outcome.

If the channel does not exist yet, queue equivalent events via `scripts/agent-report` and note `channel pending_owner_approval` in the PR description.

## Acceptance criteria

See `contract.json` → `acceptance_criteria[]` (testable gates including competitive matrix, pipeline demo, integration manifest, ICM runs, contract PR review pass, Claude agent invocable by name).

## Deliverables

| ID | Deliverable | Path |
|---|---|---|
| D1 | Competitive landscape & Splunk parity map | `splunk-clone/docs/competitive-landscape.md` |
| D2 | Architecture & data model | `splunk-clone/docs/architecture.md` |
| D3 | Ingestion layer | `splunk-clone/src/ingest/` |
| D4 | Search & query layer | `splunk-clone/src/search/` |
| D5 | Dashboards (security + network status) | `splunk-clone/src/ui/` |
| D6 | Alerting & correlation | `splunk-clone/src/alerts/` |
| D7 | Future SAI plugin integration manifest | `splunk-clone/docs/integration-manifest.md` |
| D8 | Claude-native Splunky agent (skills/hooks/MCP) | `splunk-clone/.claude/` + `.ai/agents/splunky/` |
| D9 | Tests & CI scoped to project | `splunk-clone/` |

## Approved capabilities

Empty until **ONBOARDING Phase 3** owner approval loops. Candidates listed in `contract.json` → `proposed_capabilities[]`.

## Claude Desktop / Code setup

- Project subagent: `splunk-clone/.claude/agents/splunky.md` (check into fork)
- Bootstrap reference: `claude-desktop-bootstrap.json` in this contract folder
- Invoke: `"agent": "splunky"` in `splunk-clone/.claude/settings.json` or `@splunky` / explicit subagent delegation per [Claude Code subagents](https://docs.anthropic.com/en/docs/claude-code/sub-agents)

## Superseded

- **Alpha** (`ctr-code-splunk1`) — pilot only; no new work after this amendment.
