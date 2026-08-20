# Coordination reporting
Agents emit schema-valid SAI events, queue when Slack is down, install git hooks that report worktree/commit/push, and record Drive sync without blocking Git.
## Sub-features
- `report-emit` `scripts/agent-report emit <TYPE> [--task-id …]` writes schema-valid JSON to `.git/agent-events/queue/` and mirrors `events.jsonl`.
- `report-flush` `scripts/agent-report flush` FIFO; missing `SAI_SLACK_BOT_TOKEN` keeps queue and flush exits 1; `emit … --no-deliver` exits 0.
- `report-push-confirm` `scripts/agent-report push-confirm [remote]` requires `git ls-remote` SHA == HEAD.
- `report-redact` `agent-report` strips tokens/keys before queue or Slack.
- `hook-install` `scripts/install-agent-hooks` sets `core.hooksPath=.githooks` and chmod.
- `hook-pre-push` `.githooks/pre-push` blocks `main` without audit/hierarchy/handoff unless `SAI_AUDIT_BYPASS`.
- `hook-post-commit` `.githooks/post-commit` emits COMMIT (never blocks git).
- `hook-post-checkout` `.githooks/post-checkout` emits WORKTREE on branch change.
- `hook-post-merge` `.githooks/post-merge` emits COMMIT.
- `hook-post-rewrite` `.githooks/post-rewrite` emits WORKTREE for rebase/amend.
- `hook-post-push-eq` `.githooks/post-push-equivalent.sh` push then `push-confirm`.
- `drive-sync` `scripts/agent-sync-drive [--remote] [--repo-key]` pending+exit 0 without rclone/remote.
- `ci-handoff-slack` `scripts/ci-merge-handoff-slack` posts merge HANDOFF when token set.
## How to get to it (user POV)
- `scripts/agent-report emit INTAKE --task-id <id> --purpose … --result …` `scripts/install-agent-hooks` then ordinary `git commit` / `git push` `.githooks/post-push-equivalent.sh -u origin <branch>` when a post-push confirm is required `scripts/agent-sync-drive` after a verified remote SHA
## Driving it with verify-sai
- **Emit.** ::exec scripts/agent-report emit INTAKE --task-id 20990101-0000-verify-sai-fixture --purpose t --result t --no-deliver
- **Drive pending.** ::exec scripts/agent-sync-drive
## Gotchas
- `SAI_AGENT_REPORT_ACTIVE=1` prevents hook recursion. Slack MCP posts are not `agent-report` events unless also emitted. Never commit queue files under `.git/`.
