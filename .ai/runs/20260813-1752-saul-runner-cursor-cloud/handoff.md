# Handoff — 20260813-1752-saul-runner-cursor-cloud

Continuing PR #62 from head `0676b13`. Retargeted Saul to `[self-hosted]`
and stopped requiring GitHub API keys for local Codex. Production smoke
is not complete until a GitHub Actions job is assigned to the dedicated
runner and records `codex_invoked: true`.

Do not merge. Do not mark ready. Next: push, observe `saul-cto-review`
runner_name/labels, then execute remaining smoke phases.
