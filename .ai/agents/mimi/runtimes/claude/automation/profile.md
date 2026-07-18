# Claude automation profile — Mimi (mimi)

> Hand-authored 2026-07-17 (task
> `20260717-0229-mimi-dispatcher-bootstrap-mimi`) because
> `scripts/agent-automation-spec` has no `--suite claude` yet; regenerate
> with the generator once the accepted change (PR #19 lineage) merges and
> this branch is rebased. Contains **only** Claude-runtime state — the
> Cursor Automations walkthrough lives in
> `../../cursor/automation/profile.md` (secondary runtime).

## Identity

| | |
|---|---|
| Agent name | Mimi |
| Role title | Portfolio Project Agent Manager (dispatcher mandate proposed, contract `20260717-mimi-dispatcher-bootstrap-monaecode`) |
| Agent ID | `mimi` (automation runs as `mimi-automation`) |
| Principal | monaecode (U0BGNS7F0T1) |
| Primary runtime | `claude-code-cli` |

## Live automation (evidence-backed)

| Mechanism | Status | Detail |
|---|---|---|
| Claude Code scheduled task `mimi-protocol-upkeep` | **active, caveated** | cron `0 9 * * *` (09:01 America/Chicago); created 2026-07-14 via `create_scheduled_task` (response confirmed next run). **Caveat:** fires only while the Claude app is open at fire time; runs on next launch otherwise. Not an always-on cloud cron. |
| Slack `@mimi` trigger | **building** | No inbound-event path exists in Claude Desktop/Code; OSS bridge design in `../../../docs/dispatch-triggers.md`; promotion to `verified` requires evidence URL per `hooks.json` |
| GitHub `@mimi` trigger | **building** | Inert stub `.github/workflows/mimi-dispatch-stub.yml` (workflow_dispatch, validated inputs, no secrets, no Claude invocation); end-to-end not built |

## Scheduled-task instructions (source of truth for `mimi-protocol-upkeep`)

On each run, as `SAI_AGENT_ID=mimi-automation`, in a clean
`monaecode/Sai` checkout:

1. `git fetch origin main`; unreachable → post `[SAI][BLOCKED]`, stop.
2. `scripts/agent-report flush` — report delivered vs queued; never
   fabricate delivery.
3. `scripts/verify-agent-audit origin/main..HEAD` +
   `scripts/verify-semantic-hierarchy` — capture exact output.
4. `scripts/agent-sync-drive` — report honest status.
5. Fork CI drift check (`agent-audit.yml` parity vs canonical).
6. Post one `[SAI][VERIFY]` (or `[SAI][BLOCKED]`) to #agentupdates
   (C0BH15HDN2Z) per `.ai/_config/reporting.yaml`, with real `<@USER_ID>`
   mentions (routing table:
   `.claude/skills/mimi-dispatcher/slack-github-orchestration/SKILL.md`)
   and the full report md linked from GitHub (monaecode standing
   directive).
7. Hard limits: no force-push, merge, history rewrite, credential access,
   or `SAI_AUDIT_BYPASS`; security-policy gates absolute.

## Claude-runtime surfaces

- Subagent: `.claude/agents/mimi-dispatcher.md` (dispatch persona,
  tools allowlist, `memory: project`).
- Skills: `.claude/skills/mimi-dispatcher/{icm-portfolio-audit,contractor-dispatch,slack-github-orchestration}/SKILL.md`.
- Settings: `.claude/settings.json` (least-privilege git/gh/scripts
  allowlist, explicit destructive-git denies, force-push PreToolUse guard,
  SessionStart discipline banner).
- Verified capabilities: `../tools.json` (session-evidence discipline;
  only `verified` entries count).
