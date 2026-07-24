# Contract: OpenClaw SAI Dashboard (Alfred)

**Binding document for Alfred on OpenClaw Gateway.** This file, `contract.json`, and
`first-message-to-openclaw.md` are the authoritative contract set. Human-readable
summary — machine gates live in JSON and smoke scripts.

| Field | Value |
|---|---|
| **Contract ID** | `20260722-openclaw-dashboard-dezocode` |
| **Status** | `draft` — activate only per Part B below |
| **Project** | OpenClaw SAI Dashboard (`openclaw-dashboard/`) |
| **Contractor** | Alfred — The OpenClaw Administrator (`ctr-code-alfred1`) |
| **Principals** | dezocode (U0BHYH0NMCY) and monaecode (U0BGNS7F0T1) |
| **Contract sender** | dezocode — mandatory Telegram session reporting recipient |
| **Contractor type** | coding |
| **Isolation mode** | `prototype` — product work on `proj/openclaw-dashboard/*` until fulfillment gate |
| **Architecture classification** | `isolated_prototype` — see DR below |
| **Stack criteria** | `proposed-not-canonical` — Tauri/React/SwiftUI/Phaser are experiment inputs, not accepted SAI core |
| **Runtime** | `openclaw-gateway-vps` (Hostinger VPS OpenClaw Gateway — **not Cursor**) |
| **Repository** | `Dezocode/Sai` (canonical); sync `monaecode/Sai` by SHA |
| **Branch prefix** | `proj/openclaw-dashboard/` |
| **Bootstrap branch** | `proj/openclaw-dashboard/ctr-code-alfred1/bootstrap` |
| **Product root** | `openclaw-dashboard/` (**prototype scaffold** — Markdown/JSON spec until promotion) |
| **Slack** | `#agentupdates` (primary); `#proj-openclaw-dashboard` (project — owner approval) |
| **Registry** | Alfred `provisional` until Part C organization onboarding completes |

## Architecture decision (binding — read before building)

→ **[DR-20260724-openclaw-dashboard-prototype-boundary.md](../../shared/memory/decisions/DR-20260724-openclaw-dashboard-prototype-boundary.md)**

Sai CEO classification `[SAI][VERIFY][20260724-0311-pr45-architecture-decision-ceo]`:

| Layer | What it is | Canonical `main` after Part A scaffold merge |
|---|---|---|
| Alfred profile, OpenClaw runtime adapter, this contract, ICM/CI extensions | Agent infrastructure (L0–L3) | May land on `main` as coordination scaffold |
| `openclaw-dashboard/` product tree | **Isolated prototype** — spec, tokens, smoke gates | Documentation only — **not** accepted parent-app architecture |

**You must not treat tech-stack docs as committed product decisions.** Promotion to core
requires a superseding decision record + stack-specific CI + green full smoke (no ignored
stubs) + cofounder review.

Also read: [ACTIVATION-AND-MERGE-CHECKLIST.md](./ACTIVATION-AND-MERGE-CHECKLIST.md) (Parts A–D).

## Binding first message (OpenClaw session entry)

Paste into a **fresh OpenClaw session** on the Hostinger VPS:

→ **[first-message-to-openclaw.md](./first-message-to-openclaw.md)**

Short attach prompt (same contract):

→ **[first-prompt-attach-contract.md](./first-prompt-attach-contract.md)**

## Contract JSON (machine-readable gates)

→ **[contract.json](./contract.json)** — deliverables A0–A13, fulfillment gate,
`architecture_classification`, `stack_criteria_status`, reviewers, Telegram session.

## Research and PR context

Each deliverable links to integration research in:

→ **[research-integration-methods.md](./research-integration-methods.md)**

NotebookLM owner source:

→ **[notebooklm-context.md](./notebooklm-context.md)**

## Mission summary

Alfred integrates a fresh **OpenClaw** install as the SAI workspace's top automation
and coordination platform:

1. **Gateway ops** — Hostinger VPS, loopback default (`127.0.0.1`), health monitoring, config mirror
2. **Both GitHub repos** — `Dezocode/Sai` and `monaecode/Sai` branch/CI tracking
3. **Slack workspace** — agent reporting SOP, public channel discipline, activity ingest
4. **Composio** — Telegram, Google Drive, Gemini Notebook / NotebookLM exports
5. **Dashboard tabs (prototype spec)** — Tracking, Second brain, Research, Habbo chat, Config, GitHub
6. **Clients (proposed stack)** — Mac desktop + iPhone Whisper — versions experimental per DR
7. **Agent team** — config-expert, research-coordinator; three-connection gate for all subagents
8. **Telegram session bot** — message contract sender (dezocode) every ICM stage; fleet coherence

## Dashboard ICM scaffold (product filesystem — prototype)

Each tab and settings page has **`CONTEXT.md` + `BUILD.md`** under `openclaw-dashboard/`.
Read the **prototype banner** in [openclaw-dashboard/CONTEXT.md](../../../openclaw-dashboard/CONTEXT.md) first.

| Path | Surface |
|---|---|
| `openclaw-dashboard/ICM-HANDBOOK.md` | Master handbook |
| `openclaw-dashboard/tabs/*/` | Dashboard tabs |
| `openclaw-dashboard/settings/*/` | Auth, secrets, host-health, reporting, models |

Linked in `contract.json` → `dashboard_icm`.

## Lifecycle gates (Parts A–C)

### Part A — Scaffold intake (repo PR #45 → `main`)

Merges **agent infrastructure + prototype product spec** to canonical `main`.
Does **not** activate you or accept the product stack. Stub smoke (exit **2**) and
fail-closed contract gates (exit **1** on pending registry) are **expected** pre-fulfillment.

→ [ACTIVATION-AND-MERGE-CHECKLIST.md](./ACTIVATION-AND-MERGE-CHECKLIST.md) Part A

### Part B — Contract activation (`draft` → `active`)

Authorizes VPS bootstrap and first-message execution. Requires merged scaffold +
confirmed terms + secrets plan. Sets `contract.json` → `"status": "active"`.

### Part C — Organization onboarding (your `registry status: active`)

Production fulfillment on bootstrap branch → merge to `main`. Blocks until all
organization_onboarding_gate + fulfillment_gate conditions evidenced.

## Organization onboarding gate (dezocode hard requirements)

Alfred joins the SAI organization only when Part C completes:

1. **OpenClaw-primary** — `openclaw-gateway-vps`; not a Cursor runtime agent
2. **100% production** — dashboard, host CLI, dependencies, auth regulation complete on VPS
3. **Live feed** — host admin CLI streams activity into all monitoring tabs
4. **Latency SLO** — p99 **≤ 15ms** from CLI event to dashboard tab render
5. **ICM + Sai + Saul** — verifiers PASS; Sai VERIFY; Saul review; cofounder merge auth
6. **Stack promotion** — if implementing Tauri/React/SwiftUI/Phaser, treat as prototype until superseding DR

See [amendments/20260722-dezocode-pr45-review.md](./amendments/20260722-dezocode-pr45-review.md),
[amendments/20260722-saul-cto-review.md](./amendments/20260722-saul-cto-review.md),
[amendments/20260722-saul-review-4751481118.md](./amendments/20260722-saul-review-4751481118.md).

## Secrets security (PR #45 controlling)

PR #45 governs credential **structure** for OpenClaw + dashboard — values on VPS only:

→ [secrets-security.md](../../../openclaw-dashboard/docs/secrets-security.md)  
→ [auth-matrix.md](../../../openclaw-dashboard/docs/auth-matrix.md)  
→ [settings/secrets/](../../../openclaw-dashboard/settings/secrets/CONTEXT.md)

## Review status

→ [PR45-REVIEW-TRACKER.md](./PR45-REVIEW-TRACKER.md)  
→ [ACTIVATION-AND-MERGE-CHECKLIST.md](./ACTIVATION-AND-MERGE-CHECKLIST.md)

## Fulfillment gate (Part C — binding)

Alfred receives **final organization approval** only when all conditions in
`contract.json` → `fulfillment_gate` are true, including:

- Sai `[SAI][VERIFY] PASS` referencing this `contract_id`
- Saul acceptable CTO review (no blocking P1)
- Both co-founders explicitly authorize merge of **bootstrap product work** to `Dezocode/Sai:main`
- Fleet coherence, secrets compliance, three-connection gates, Telegram session proof

Until Part C: work **only** on isolated `proj/openclaw-dashboard/*` branches.
Do **not** self-promote to `registry status: active`.

## Contract sender — Telegram session reporting

**dezocode** (`U0BHYH0NMCY`) originated this contract and receives **every Alfred session
run update on Telegram** (INTAKE through HANDOFF), with Slack mirror to `#agentupdates`.

→ [telegram-session-protocol.md](../../../openclaw-dashboard/docs/telegram-session-protocol.md)  
→ [BEHAVIORS.md](../../agents/alfred/runtimes/openclaw/telegram/BEHAVIORS.md)  
→ [session-memory.md](../../agents/alfred/runtimes/openclaw/telegram/session-memory.md)

## Fleet coherence

Alfred + all subagents and dashboard-created agents follow identical ICM + Telegram + Slack
protocols. Proof gate: [fleet-coherence-gate.md](../../../openclaw-dashboard/docs/fleet-coherence-gate.md)

Subagent onboarding: [subagent-onboarding-protocol.md](../../../openclaw-dashboard/docs/subagent-onboarding-protocol.md)

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
| A9 | Mac desktop + iPhone Whisper (**proposed stack**) | [§10](./research-integration-methods.md#10-mac-desktop-and-iphone-whisper) |
| A10 | Agent Telegram inbox verification | [§11](./research-integration-methods.md#11-agent-telegram-inbox-verification) |
| A11 | Dashboard auth hub | [§12](./research-integration-methods.md#12-dashboard-auth-hub) |
| A12 | Review package + merge gate | [§13](./research-integration-methods.md#13-fulfillment-and-merge-gate) |
| A13 | Telegram session bot + fleet coherence | [§14](./research-integration-methods.md#14-telegram-session-fleet-coherence) |

## Acceptance criteria

See `contract.json` → `acceptance_criteria` and `acceptance_criteria_note`.

Stack-related criteria (native apps, Phaser, cross-platform UI) are **proposed-not-canonical**
per DR-20260724 until promotion decision. ICM, security, Telegram, fleet, and secrets
criteria are binding regardless of stack promotion state.

Summary:

1. All A0–A13 deliverables evidenced on bootstrap branch with ICM run artifacts
2. `first-message-to-openclaw.md` executed as opening session (after Part B activation)
3. Contract sender receives Telegram updates for every session run stage
4. Fleet coherence proof gate PASS (Alfred + fleet agents)
5. Production smoke on approved flows — zero blocking errors (Part C)
6. Composio auth flows reachable from dashboard when Gateway healthy
7. Every registry/subagent: verified Telegram + Slack + Habbo (or documented BLOCKED row)
8. `scripts/agent-contract-pr-review` PASS on every PR
9. No secrets in Git; Sai VERIFY + Saul CTO review + human merge authorization

## Approved capabilities

_(Recorded during ONBOARDING Phase 3 owner approval loops.)_

See `contract.json` → `proposed_capabilities` for mandatory candidates (status: proposed).

## Reviewers

| Role | Agent | Gate |
|---|---|---|
| CEO | Sai (`ceo`) | `[SAI][VERIFY]` on ICM + architecture classification |
| CTO | Saul (`dezo-sec-codex1`) | Security, VPS, fail-closed smoke, promotion boundary |
| Humans | dezocode, monaecode | Contract terms, activation, merge authorization |

---

*Last upgraded: 2026-07-24 — DR-20260724 + Sai CEO architecture gate (dezocode: binding doc must be complete before merge).*
