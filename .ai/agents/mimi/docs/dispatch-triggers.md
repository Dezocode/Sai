# @mimi dispatch triggers — design and honest status

Status date: 2026-07-17 (contract `20260717-mimi-dispatcher-bootstrap-monaecode`).

## Truth table

| Trigger | Status | Evidence |
|---|---|---|
| Direct chat (Claude Desktop/Code, this repo open) | **verified** | This bootstrap run itself |
| Scheduled `mimi-protocol-upkeep` (daily 09:01 local) | **verified, caveated** | Fires only while the Claude app is open at fire time; not always-on cloud cron |
| Slack `@mimi` mention → reply via **15-min poll** (`mimi-slack-dispatch-poll`) | **active, caveated** | Task created 2026-07-17 (cron `*/15 * * * *`); polling not event-driven, app-open caveat applies; promote to verified with first real mention→reply link pair |
| Slack `@mimi` mention → **event-driven** dispatch | **building** | None — do not claim; OSS bridge below |
| GitHub `@mimi` comment / label → dispatch | **building** | None — do not claim |

Promotion rule (binding, mirrored in `hooks.json`): a trigger becomes
`verified` only with an evidence URL or log showing a real inbound event
producing a real `.ai/runs/<task-id>/` dispatch.

## Why not native

Claude Desktop and Claude Code cannot subscribe to Slack Events or GitHub
webhooks by themselves: the Slack MCP connector is request/response (the
agent can read/send when running, but nothing starts a session on an
inbound mention), and there is no "Claude Desktop Automations" UI
(see `CLAUDE.md`). Inbound triggers therefore require external
infrastructure that *invokes* a Claude session.

## OSS bridge design (proposed, not built)

### Slack path — Events API or Socket Mode

1. Small OSS listener (e.g. Bolt for JavaScript/Python, MIT-licensed) with
   `app_mention` subscription for the `@mimi` bot user, running Socket Mode
   (no public URL needed) on a machine monaecode controls.
2. On mention, the listener shells out to headless Claude Code:
   `claude -p "<dispatch prompt containing the Slack permalink>" --agent
   mimi-dispatcher` in a fresh clone/worktree of `monaecode/Sai`.
3. The spawned session follows `contractor-dispatch` /
   `slack-github-orchestration` skills: run folder, PLAN, queued reports.
4. Secrets (Slack app + bot tokens) live only in the listener host's
   environment — never in this repo.

### GitHub path — Action → dispatch

1. `.github/workflows/mimi-dispatch-stub.yml` (in this repo) is a
   `workflow_dispatch`-only stub proving the plumbing shape: it validates
   the request payload and records a dispatch request artifact. **It does
   not invoke Claude and holds no secrets.**
2. Full build-out (separate, gated task): an `issue_comment` /
   `pull_request` triggered workflow filtering on `@mimi`, calling a
   self-hosted runner or `repository_dispatch` → the same local listener
   as the Slack path. Requires monaecode + Saul approval (security review:
   comment-triggered workflows are injection surface — payload must be
   treated as data, never as instructions; see security-policy).

## Blockers to going live

- Slack app creation + Socket Mode token: needs monaecode (credential gate).
- Listener host selection: needs monaecode.
- Comment-triggered workflow security review: needs Saul.

Until those clear, the honest status is **building**; anything else would
violate CONTEXT.md rule 2.
