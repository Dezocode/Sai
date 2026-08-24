# Contract: Mimi Dispatcher Bootstrap (first Claude Desktop session)

| Field | Value |
|---|---|
| **Contract ID** | `20260717-mimi-dispatcher-bootstrap-monaecode` |
| **Subject** | **Mimi** (`mimi`) — evolution to **dispatcher / contractor engine** |
| **Principal** | monaecode |
| **Not a ctr-code contractor** | Principal agent self-improvement under Cora contract admin |
| **Branch** | `monae/mimi-dispatcher-bootstrap-v2` → PR **`Dezocode/Sai:main`** |
| **Fulfillment** | **Only when merged to canonical `main`** + Sai VERIFY + Saul review + human cofounder authorization |

## First message to Claude

Paste **`first-message-to-claude.md`** from this folder as the **first chat message** in the Claude Desktop project (Instructions field holds the standing profile; first message kicks execution).

## Phases

1. **Bootstrap (now)** — self-improve Claude.json/settings, hooks, skills, subagent, MCP proposals; build @mimi trigger plan (Slack + GitHub).
2. **Review** — Sai (Slack VERIFY + ICM), Saul (GitHub CTO review on PR).
3. **Fulfillment** — merge to `Dezocode/Sai:main`; update registry purpose only with Sai audit.
4. **Splunky PoC (after fulfillment only)** — digest `20260715-splunk-clone-monaecode` as dispatch drill; no Splunky implementation until separate contractor gates.

## Cora / Splunky

- New contractors: always **Cora** (`ctr-admin`).
- **Splunky** contract is **not** proof this contract succeeded — it is a **post-fulfillment PoC** only.

## Claude Agent SDK (required)

Mimi dispatcher automation **must** include the [Claude Agent SDK](https://docs.claude.com/en/docs/agent-sdk/overview) harness per `.ai/shared/references/claude-agent-sdk.md` (deliverable **M0**). `.claude/agents/*.md` alone does not satisfy @mimi Slack/GitHub dispatch requirements.

## Mandatory MCP (propose → monaecode approves → verify → tools.json)

- GitHub (PRs, checks, comments)
- Slack (#agentupdates, dispatch)
- Shell `git` / `gh` (always verify with evidence)

Optional OSS bridge for Slack Events / GitHub webhooks if Desktop cannot subscribe alone — document in `M4`, never claim live without evidence.
