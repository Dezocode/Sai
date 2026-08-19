# Intake — Lauren mode cloud skills + 08-19-26 harness

- Task-ID: `20260819-2341-lauren-mode-cloud-cursor-cloud`
- Requester: dezocode (U0BHYH0NMCY)
- Source: mobile Cloud Agent run `bc-01a01c62-2904-7567-b237-4ba571eafd30` named "Lauren mode cloud setup"
- Quote: `/cursor-sdk get Lauren mode set up in my cloud skills get all these updates live internal browser pane my cloud agent config https://cursor.com/changelog/08-19-26`

## Requested outcome

1. A project Custom Mode in Cloud Agent skills named for Lauren Tan's pstack (`/lauren-mode`), pin-able via Option+Enter / Use as Mode.
2. The 2026-08-19 Cursor changelog features usable from that mode: subscriptions, Custom Modes, subagents on their own VMs, `/goal`, steering that waits for the next tool call.
3. Internal Browser pane guidance (`@Browser`, built-in Browser subagent, `computerUse` on this VM).
4. Record the live Cloud Agent environment (personal DB-managed) without replacing it with a repo `environment.json`.
5. Cursor SDK cloud launch notes so `@cursor/sdk` agents pick up the same project skills.

## Repository facts (command-backed)

```
git rev-parse --show-toplevel → /workspace
git remote -v → origin https://github.com/dezocode/sai (fetch/push)
git status → on main, clean, up to date with origin/main
git fetch origin main → dda0e97 Merge pull request #67
branch created → cursor/lauren-mode-cloud-fd30 from origin/main
```

`gh` is authenticated. Canonical repo is `Dezocode/Sai`. This VM is a Cloud Agent clone, not a Google Drive worktree.

## Current state

- pstack is project-enabled in `.cursor/settings.json` (decision 0004). `/poteto-mode` already has `mode: true` in the marketplace skill.
- `.cursor/skills/` does not exist. Decision 0004 forbids copying the pstack tree there (duplicate `/` names).
- `.cursor/rules/pstack-models.mdc` was deferred. `/setup-pstack` writes `~/.cursor/rules/`, which Cloud Agents do not apply.
- Cloud environment is personal/DB-managed: `environmentJsonPath` is null; `environment.json` is owner-restricted. Environment dashboard: `6f2ece39-800a-11f1-ba66-0e7d0216e441`. This pod booted from build `bld-20260819-500928d1-8214-4bc0-9bb9-e36884ef51f0`. Chrome is present at `/usr/bin/google-chrome`.
- No application product to serve. Checks are ICM scripts.

## Constraints

- Do not copy pstack skills into `.cursor/skills/`.
- Do not commit `.cursor/environment.json`. A repo file would override the personal dashboard environment.
- Do not run `scripts/agent-init` / `install-agent-hooks` on this managed VM.
- Do not force-push, merge, or mark the PR ready.
- Commit trailers and merge-handoff required.
- Detected Task model slugs only in `pstack-models.mdc` (no unverified default slugs such as `grok-4.6-fast-xhigh`).

## Acceptance

- `/lauren-mode` exists as a project skill with Custom Mode frontmatter (`mode: true`, icon, color).
- Cloud agents on this commit can pin it and get 08-19-26 harness instructions plus Browser pane + SDK launch notes.
- Shared pstack role models are committed for Cloud + local.
- ICM memory/docs name the new skill without claiming marketplace pstack was vendored.
- Verification commands recorded. This session cannot prove the Desktop `/` picker; disclose that.

## Security / compatibility

No hard gates from `.ai/_config/security-policy.md`. No secrets. Environment IDs are public dashboard IDs.
