# Plan — mimi-dispatcher-bootstrap-v2

Branch `monae/mimi-dispatcher-bootstrap-v2` off `main` @ 3c5c799 (post fast-forward).

## Commits (each with Task-ID / Agent / Report-Event trailers)

1. **Contract of record + run scaffold** — import `.ai/contracts/20260717-mimi-dispatcher-bootstrap-monaecode/` from `upstream/cursor/mimi-dispatcher-bootstrap-f1d6`; run folder; close prior blocked run as superseded.
2. **M1 Claude-native identity** — `.claude/agents/mimi-dispatcher.md`, `.claude/skills/mimi-dispatcher/{icm-portfolio-audit,contractor-dispatch,slack-github-orchestration}/SKILL.md`, `.claude/settings.json` (permissions + hooks), `.ai/agents/mimi/runtimes/claude/claude-desktop-bootstrap.json`, `.ai/agents/mimi/claude-desktop-project-instructions.md`.
3. **M2 hooks/automation truth table** — `.ai/agents/mimi/hooks.json` slack/github triggers `status: building` with evidence rule; regenerate `runtimes/claude/automation/profile.md` via `scripts/agent-automation-spec`.
4. **M3/M4 connectors + triggers** — capability survey via `scripts/agent-verify-caps` (verified-only in `runtimes/claude/tools.json`); `.ai/agents/mimi/docs/dispatch-triggers.md` OSS path; `.github/workflows/mimi-dispatch-stub.yml` (workflow_dispatch stub, no secrets).
5. **M5 charter amendment proposal** — `amendments/charter-dispatcher-proposal.md` + registry diff proposal (no live registry change); AGENT.md purpose update marked as proposal-backed.
6. **M6 proof package** — run verifiers, subagent invocation transcript in `04_verify/output/`, `handoff.md`, PR to `Dezocode/Sai:main`.

## Gates honored

- Ask monaecode before recording GitHub/Slack/git-gh in approved capabilities (contract 1C) and before opening the PR.
- Slack posts queue via `scripts/agent-report` (token unset); never claim delivery.
- No Splunky PoC, registry activation, force-push, or channel creation before fulfillment.
