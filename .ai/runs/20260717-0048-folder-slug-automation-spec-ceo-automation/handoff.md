# Handoff — 20260717-0048-folder-slug-automation-spec-ceo-automation

## Result

Addressed CTO P1 on PR #15: `scripts/agent-automation-spec` now resolves a canonical `.ai/agents/<folder-slug>/` from `--folder-name`, `--tools-file`, `--out`, or slugified display name. Generated Splunky Claude profiles reference `.ai/agents/splunky/` not `.ai/agents/Splunky/`. `verify-scaffold-safety` includes a regression check. `INITIALIZE.md` Phase 7 documents `--folder-name` and folder-slug paths.

## Verification

- `bash -n scripts/agent-automation-spec`
- `scripts/verify-scaffold-safety` (includes automation-spec slug test)
- `scripts/verify-semantic-hierarchy`
- `scripts/verify-agent-audit origin/main..HEAD`

## Next action

Merge PR #15 after remaining review threads cleared; Splunky ONBOARDING Phase 5B on monaecode/Sai.
