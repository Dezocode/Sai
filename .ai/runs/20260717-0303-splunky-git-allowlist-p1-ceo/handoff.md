# Handoff — Splunky git Bash least-privilege (P1 CTO review)

## Result

Replaced `Bash(git *)` in `splunk-clone/.claude/settings.json` and
`.ai/contracts/20260715-splunk-clone-monaecode/claude-desktop-bootstrap.json`
with explicit allow patterns for ICM-safe git operations plus a deny list
blocking force-push, remote ref deletion, hard reset, rebase, and related
destructive commands. Canonical copy:
`.ai/shared/references/claude-code-git-bash-allowlist.json`.

## Verification

- `scripts/verify-semantic-hierarchy` — OK
- `scripts/verify-agent-audit origin/main..HEAD` — OK
- `python3 -m json.tool` on edited JSON files — OK
- `rg 'Bash\\(git \\*\\)'` — no matches

## Next safe action

- monaecode: merge synced settings into local Claude Desktop after pull.
- Splunky Phase 5B: expand capabilities only with verified evidence, not broad Bash grants.

## Risks

Deny patterns depend on Claude Code permission matching; destructive
variants not covered by deny should be reported and added to the reference file.
