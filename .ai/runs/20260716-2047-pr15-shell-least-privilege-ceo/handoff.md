# Handoff — PR #15 P1 shell least-privilege

## Result

Removed `Bash(git *)` and `Bash(gh *)` from Splunky provisional Claude bootstrap and project settings. Added documented `shell_allowlist_after_phase_5b` in bootstrap JSON and contract amendment `20260716-ceo-p1-shell-least-privilege.json`. Updated onboarding-prompt step 2.

## Verification

- `scripts/verify-semantic-hierarchy`
- `scripts/verify-agent-audit origin/main..HEAD`
- JSON parse on edited bootstrap/settings/amendment

## Next safe action

monaecode: after Splunky completes ONBOARDING Phase 5B, review `shell_allowlist_after_phase_5b.allow` and merge approved entries into `splunk-clone/.claude/settings.json`. Re-run CTO review on PR #15.
