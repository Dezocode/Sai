# Handoff — PR #18 P1 provisional read-only contractor profiles

## Result

Addressed dezocode P1 on PR #18: Splunky provisional Claude bootstrap, project settings, and subagent no longer grant repository-wide `Write`/`Edit` or `permissionMode: acceptEdits`. Documented `file_mutations_after_persona_gate` merge path; added reusable template and CI verifier.

## Verification

- `scripts/verify-provisional-contractor-perms`: OK
- `scripts/verify-semantic-hierarchy`: OK
- `scripts/verify-scaffold-safety`: OK
- `scripts/verify-agent-audit origin/main..HEAD`: OK (after commit)

## Next action

monaecode: after Splunky ONBOARDING Phase 3–6, merge `file_mutations_after_persona_gate` and `shell_allowlist_after_phase_5b` into `splunk-clone/.claude/settings.json` per contract amendments; re-run CTO review on PR #18.
