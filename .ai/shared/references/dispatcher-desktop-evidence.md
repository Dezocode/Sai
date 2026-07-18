# Dispatcher desktop evidence — host-only verification

> Contract `20260718-dispatcher-ci-gate-monaecode` · Cora directive
> `20260718-0155` · Blocking merge gate: `SAI_CI_DISPATCH_MERGE_GATE=1`

Cloud CI **cannot** produce authenticated Claude Desktop evidence. The
`dispatcher-merge-gate` job in `.github/workflows/agent-audit.yml` activates
only when a PR touches Mimi dispatcher paths; it requires the artifacts below
recorded on a **Desktop host** (Claude Code CLI, Claude Desktop, Codex Desktop,
or Cursor Desktop as appropriate).

## Required proof package (one run folder)

Create `.ai/runs/<task-id>/04_verify/output/` with:

| File | Agent / runtime | What to capture |
|---|---|---|
| `dispatcher-desktop-proof.txt` | **Mimi** (required for merge gate) | Summary: agent-init exit 0, SDK `--smoke` exit 0, subagent invoke transcript refs |
| `agent-sdk-smoke.txt` | Mimi | Read-only SDK `query()` smoke log |
| `subagent-mimi-dispatcher.txt` | Mimi | CLI invoke of `mimi-dispatcher` subagent (command + exit code + summary) |
| `agent-init-<agent-id>.txt` | Each agent tested | `SAI_AGENT_ID=<id> scripts/agent-init` on Desktop |
| `dispatch-drill-<agent-id>.txt` | ceo, mimi, saul, cora, alpha | One Slack post + one GitHub action per agent (or honest BLOCKED) |

Minimum merge gate today: **`dispatcher-desktop-proof.txt` > 20 bytes** in any
run under `.ai/runs/*/04_verify/output/`.

## Dispatch matrix (CI-verifiable)

Structural routing for all registered agents lives in
`.ai/_config/dispatch-matrix.json`. CI always runs
`scripts/verify-dispatcher-matrix` (structural mode).

## Desktop checklist by agent

| agent_id | Host | Subagent / entry | Slack | GitHub |
|---|---|---|---|---|
| `ceo` | Cursor Desktop / Cloud automation | `@sai` | #agentupdates `@sai:` | PR trigger on Dezocode/Sai |
| `mimi` | Claude Desktop + SDK | `mimi-dispatcher` / SDK `query()` | `@mimi` dispatch | labeled issue or PR comment |
| `dezo-sec-codex1` | Codex Desktop | CODEX.md → saul | #dev / #agentupdates | PR review on canonical |
| `ctr-admin` | Cursor Desktop | `@cora` | #agentupdates contract posts | contract PR review |
| `ctr-code-splunk1` | Claude Code | ONBOARDING + contract | dispatched by Mimi | `proj/splunk-clone/...` branch |

## When CI blocks

PR touches:

- `.ai/agents/mimi/**`
- `.claude/**`
- `.ai/contracts/*dispatcher*/**`
- `.ai/_config/dispatch-matrix.json`

→ job `dispatcher-merge-gate` runs with `SAI_CI_DISPATCH_MERGE_GATE=1`.

Fix by completing Desktop evidence and adding verified `claude-agent-sdk` to
`.ai/agents/mimi/runtimes/claude/tools.json` per
`.ai/shared/references/claude-agent-sdk.md`.
