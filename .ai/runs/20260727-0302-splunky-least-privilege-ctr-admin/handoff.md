# Handoff — Splunky least-privilege + repo BLOCKED

## What changed

- `splunk-clone/.claude/agents/splunky.md`: removed `Write`, `Edit`, `Bash`, `acceptEdits`; read-only until Phase 3
- `splunk-clone/.claude/settings.json`: removed `Write`/`Edit` from permissions.allow
- `reviews/20260727-repo-target-blocked.md`: documents merge BLOCKED on wrong repository

## Not done (requires cofounder/Mimi)

- Move scaffold to `monaecode/Sai` (contract.repository)
- Mimi `fulfillment_gate` before `splunky_poc_gate` dispatch
- `#splunk-clone-project` channel approval

## Next safe action

Do **not** merge PR #15 on Dezocode/Sai. Retarget to monaecode fork or amend contract with explicit canonical-repo authorization.
