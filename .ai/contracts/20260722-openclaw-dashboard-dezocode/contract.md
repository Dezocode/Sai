# Contract: OpenClaw SAI Dashboard (Alfred)

| Field | Value |
|---|---|
| **Contract ID** | `20260722-openclaw-dashboard-dezocode` |
| **Project** | OpenClaw SAI Dashboard (`openclaw-dashboard`) |
| **Contractor** | Alfred — The OpenClaw Administrator (`ctr-code-alfred1`) |
| **Principals** | dezocode (U0BHYH0NMCY) and monaecode (U0BGNS7F0T1) |
| **Contractor type** | coding |
| **Isolation** | prototype (merge to main only after fulfillment gate) |
| **Runtime** | OpenClaw Gateway on Hostinger VPS + Cursor for repo artifacts (`cursor-cloud-vm`) |
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

## Fulfillment gate

Alfred receives **final organization approval** only when Sai, Saul, both co-founders,
and merge to `Dezocode/Sai:main` complete per `contract.json` → `fulfillment_gate`.

Until then: work **only** on isolated `proj/openclaw-dashboard/*` branches.

## Deliverables (A0–A12)

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

## Acceptance criteria

1. All A0–A12 deliverables evidenced on bootstrap branch with ICM run artifacts
2. `first-message-to-openclaw.md` executed as opening session
3. Mac desktop + iPhone companion pass smoke suite (no blocking errors on approved flows)
4. Composio auth flows reachable from dashboard when Gateway healthy
5. Every registry agent: verified Telegram inbox or documented BLOCKED
6. `scripts/agent-contract-pr-review` PASS on every PR
7. No secrets in Git; Sai VERIFY + Saul CTO review + human merge authorization

## Approved capabilities

_(Recorded during ONBOARDING Phase 3 owner approval loops.)_

See `contract.json` → `proposed_capabilities` for mandatory candidates.
