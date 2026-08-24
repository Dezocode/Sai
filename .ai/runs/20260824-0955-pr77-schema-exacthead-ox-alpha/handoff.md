# Handoff — 20260824-0955-pr77-schema-exacthead-ox-alpha

## What changed
- loadSessions()/loadPrs() require top-level schema==='sai-sessions-v2'; structurally-valid payloads without the schema marker fall back / render unavailable (Saul acceptance FAIL).
- reviewView(): Saul card displays EXACT review HEAD (full sha), never truncated (Saul acceptance FAIL).
- All selftest + probe fixtures carry the schema marker; probe asserts full HEAD string.

## Verification
py_compile OK; --selftest ALL PASS; --check ALL PASS features=11 + prs-probe.
