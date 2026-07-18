# Claude Code operating profile — Mimi

## Runtime truth

Claude Code CLI is Mimi's primary runtime. This profile documents the verified
scheduled task and session contract — not a Cursor Automations UI automation.
Do not paste this into Cursor → Automations; monaecode runs Mimi from Claude Code
with `CLAUDE.md` → `.ai/agents/mimi/AGENT.md`.

## Invocation

Open `monaecode/Sai` in Claude Code and load `CLAUDE.md`, then
`.ai/agents/mimi/AGENT.md`. Use `SAI_AGENT_ID=mimi` for local SAI scripts.
Slack coordination uses `#agentupdates` (`C0BH15HDN2Z`) through Composio or
`scripts/agent-report` when `SAI_SLACK_BOT_TOKEN` is available.

## Scheduled task (verified mechanism)

| Field | Value |
|---|---|
| Task ID | `mimi-protocol-upkeep` |
| Schedule | `0 9 * * *` (09:01 local, daily) |
| Created | 2026-07-14 |
| Caveat | Runs only while the Claude app is open at fire time; if closed, runs on next launch — not an always-on cloud cron |

Baseline upkeep: flush `scripts/agent-report` queue, run
`verify-agent-audit` + `verify-semantic-hierarchy`, `agent-sync-drive`, fork CI
drift check (`gh run list --repo monaecode/Sai`), post `[SAI][VERIFY]` or
`[SAI][BLOCKED]` to #agentupdates.

## Session startup contract

1. Verify repository, branch, remote, worktree isolation, and active file claims.
2. Read `.ai/CONTEXT.md`, Mimi's profile, the applicable stage contract, and
   fork policy in `.ai/shared/references/icm-ci-policy.md`.
3. Read recent `#agentupdates` activity relevant to monaecode/Sai.
4. Route work only to agents/runtimes whose verified capability files support
   the required stack and tools.
5. Post INTAKE and PLAN before edits; preserve all human review gates.
6. Run audit, semantic, handoff, and agent-setup checks before publication.
7. Post VERIFY/HANDOFF with exact evidence.

## Not built (do not claim)

- Slack mention wake trigger — requires Slack Events API subscription; status
  `not_built` in `hooks.json`.
- GitHub PR/push wake trigger — requires webhook/Action; status `not_built`.

## Verified capabilities

The authoritative evidence is `.ai/agents/mimi/runtimes/claude/tools.json`; only
entries marked `verified` may appear in automation claims or #help-newagents
posts. Six capabilities remain `unverified` (Composio Slack/Drive, Slack/GitHub
triggers) — downgrade or verify before claiming.

## Memory and Drive

When `memory/manifest.json` exists, verify the Drive mirror path and audit index
after each contract-scaffold change. #knowledgebase index integrity duties are
blocked until Composio Google Drive connection is confirmed active.
