# Contract: OpenClaw SAI Dashboard (Alfred)

| Field | Value |
|---|---|
| **Contract ID** | `20260722-openclaw-dashboard-dezocode` |
| **Project** | OpenClaw SAI Dashboard (`openclaw-dashboard`) |
| **Contractor** | Alfred — The OpenClaw Administrator (`ctr-code-alfred1`) |
| **Principals** | dezocode (U0BHYH0NMCY) and monaecode (U0BGNS7F0T1) |
| **Contractor type** | coding |
| **Isolation** | prototype (merge to main only after fulfillment gate) |
| **Runtime** | `openclaw-gateway-vps` (Hostinger VPS OpenClaw Gateway — **not Cursor**) |
| **Repository** | `Dezocode/Sai` (canonical); sync `monaecode/Sai` by SHA |
| **Branch prefix** | `proj/openclaw-dashboard/` |
| **Bootstrap branch** | `proj/openclaw-dashboard/ctr-code-alfred1/bootstrap` |
| **Product root** | `openclaw-dashboard/` |
| **Slack** | `#agentupdates` (primary); `#proj-openclaw-dashboard` (project — owner approval) |

## Binding first message

Paste into a **fresh OpenClaw session** on the Hostinger VPS:

→ **[first-message-to-openclaw.md](./first-message-to-openclaw.md)**

## Research and PR context

Each deliverable links to integration research in:

→ **[research-integration-methods.md](./research-integration-methods.md)**

NotebookLM owner source:

→ **[notebooklm-context.md](./notebooklm-context.md)**

## Mission summary

Alfred integrates a fresh **OpenClaw** install as the SAI workspace's top automation
and coordination platform:

1. **Gateway ops** — Hostinger VPS, health monitoring, config mirror
2. **Both GitHub repos** — `Dezocode/Sai` and `monaecode/Sai` branch/CI tracking
3. **Slack workspace** — agent reporting SOP, public channel discipline, activity ingest
4. **Composio** — Telegram, Google Drive, Gemini Notebook / NotebookLM exports
5. **Dashboard tabs** — Tracking (live meter graph), Second brain (Obsidian clone),
   Research (+ MCP), Habbo-style chat room, Config, GitHub
6. **Clients** — Mac desktop app + iPhone Whisper companion
7. **Agent team** — config-expert subagent; Telegram inbox verification for all registry agents

## Dashboard ICM scaffold (product filesystem)

Each tab and settings page has **`CONTEXT.md` + `BUILD.md`** under `openclaw-dashboard/`:

| Path | Surface |
|---|---|
| `openclaw-dashboard/ICM-HANDBOOK.md` | Master handbook |
| `openclaw-dashboard/tabs/*/` | Dashboard tabs (tracking, second-brain, research, chat-room, github, config) |
| `openclaw-dashboard/settings/*/` | Auth, host-health, reporting-sop, models |

Linked in `contract.json` → `dashboard_icm`.

## Organization onboarding gate (dezocode hard requirements)

Alfred joins the SAI organization only when:

1. **OpenClaw-primary** — `openclaw-gateway-vps`; not a Cursor runtime agent
2. **100% production** — dashboard, host CLI, dependencies, auth regulation complete on VPS
3. **Live feed** — host admin CLI streams activity into all monitoring tabs
4. **Latency SLO** — p99 **≤ 15ms** from CLI event to dashboard tab render
5. **ICM + Sai** — all `.ai` verifiers PASS; Sai VERIFY; Saul review; cofounder merge auth

See [amendments/20260722-dezocode-pr45-review.md](./amendments/20260722-dezocode-pr45-review.md) and [amendments/20260722-saul-cto-review.md](./amendments/20260722-saul-cto-review.md).

## Secrets security (PR #45 controlling)

PR #45 governs credential **structure** for OpenClaw + dashboard — values on VPS only:

→ [secrets-security.md](../../openclaw-dashboard/docs/secrets-security.md)  
→ [auth-matrix.md](../../openclaw-dashboard/docs/auth-matrix.md)  
→ [settings/secrets/](../../openclaw-dashboard/settings/secrets/CONTEXT.md)

## Activation & merge checklist

→ [ACTIVATION-AND-MERGE-CHECKLIST.md](./ACTIVATION-AND-MERGE-CHECKLIST.md)

**Review status:** [PR45-REVIEW-TRACKER.md](./PR45-REVIEW-TRACKER.md)

## Fulfillment gate

Alfred receives **final organization approval** only when Sai, Saul, both co-founders,
and merge to `Dezocode/Sai:main` complete per `contract.json` → `fulfillment_gate`.

Until then: work **only** on isolated `proj/openclaw-dashboard/*` branches.

## Contract sender — Telegram session reporting

**dezocode** (`U0BHYH0NMCY`) originated this contract and receives **every Alfred session
run update on Telegram** (INTAKE through HANDOFF), with Slack mirror to `#agentupdates`.

→ [telegram-session-protocol.md](../../openclaw-dashboard/docs/telegram-session-protocol.md)  
→ [BEHAVIORS.md](../../.ai/agents/alfred/runtimes/openclaw/telegram/BEHAVIORS.md)  
→ **First prompt to attach:** [first-prompt-attach-contract.md](./first-prompt-attach-contract.md)

## Fleet coherence

Alfred + all subagents and dashboard-created agents follow identical ICM + Telegram + Slack
protocols. Proof gate: [fleet-coherence-gate.md](../../openclaw-dashboard/docs/fleet-coherence-gate.md)

## Deliverables (A0–A13)

| ID | Title | Research |
|---|---|---|
| A0 | OpenClaw Gateway bootstrap (VPS) | [§1](./research-integration-methods.md#1-openclaw-gateway-hostinger-vps) |
| A1 | SAI ICM integration + reporting SOP | [§2](./research-integration-methods.md#2-sai-icm-integration) |
| A2 | Composio (Telegram, Drive, Notebook) | [§3](./research-integration-methods.md#3-composio-integrations) |
| A3 | Tracking tab — live activity meter | [§4](./research-integration-methods.md#4-tracking-tab-live-activity-meter) |
| A4 | Second brain — Obsidian clone | [§5](./research-integration-methods.md#5-second-brain-obsidian-clone) |
| A5 | Research tab + MCP gateway | [§6](./research-integration-methods.md#6-research-tab-and-mcp-server) |
| A6 | Habbo clone chat + Telegram PM | [§7](./research-integration-methods.md#7-habbo-clone-chat-room) |
| A7 | OpenClaw config mirror + config-expert | [§8](./research-integration-methods.md#8-openclaw-config-mirror) |
| A8 | GitHub branch + CI dashboard | [§9](./research-integration-methods.md#9-github-branch-and-ci-tracking) |
| A9 | Mac desktop + iPhone Whisper | [§10](./research-integration-methods.md#10-mac-desktop-and-iphone-whisper) |
| A10 | Agent Telegram inbox verification | [§11](./research-integration-methods.md#11-agent-telegram-inbox-verification) |
| A11 | Dashboard auth hub | [§12](./research-integration-methods.md#12-dashboard-auth-hub) |
| A12 | Review package + merge gate | [§13](./research-integration-methods.md#13-fulfillment-and-merge-gate) |
| A13 | Telegram session bot + fleet coherence | [§14](./research-integration-methods.md#14-telegram-session-fleet-coherence) |

## Acceptance criteria

1. All A0–A13 deliverables evidenced on bootstrap branch with ICM run artifacts
2. `first-message-to-openclaw.md` executed as opening session
3. Contract sender receives Telegram updates for every session run stage
4. Fleet coherence proof gate PASS (Alfred + config-expert + research-coordinator)
5. Mac desktop + iPhone companion pass smoke suite (no blocking errors on approved flows)
6. Composio auth flows reachable from dashboard when Gateway healthy
7. Every registry agent: verified Telegram inbox or documented BLOCKED
8. `scripts/agent-contract-pr-review` PASS on every PR
9. No secrets in Git; Sai VERIFY + Saul CTO review + human merge authorization

## Approved capabilities

_(Recorded during ONBOARDING Phase 3 owner approval loops.)_

See `contract.json` → `proposed_capabilities` for mandatory candidates.
