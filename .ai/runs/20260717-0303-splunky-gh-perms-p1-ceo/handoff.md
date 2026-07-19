# Handoff — 20260717-0303-splunky-gh-perms-p1-ceo

## Result

Addressed dezocode P1 CTO review on PR #16: provisional contractor Splunky no
longer grants blanket `Bash(gh *)` in Claude Code settings or contract bootstrap.
Replaced with explicit read/PR-open `gh` subcommand allowlist documented in
`.ai/shared/references/contractor-claude-gh-permissions.md`. ONBOARDING Phase 3
now references the rule. CI gate added in `scripts/verify-scaffold-safety`.

## Verification

- `scripts/verify-scaffold-safety` — OK (includes new provisional-gh-wildcard checks)
- `scripts/verify-agent-audit origin/main..HEAD` — OK after commit
- `scripts/verify-semantic-hierarchy` — OK

## Next safe action

Co-founder review PR #16; after merge, Splunky ONBOARDING on monaecode/Sai should
merge updated bootstrap into local `splunk-clone/.claude/settings.json`.
