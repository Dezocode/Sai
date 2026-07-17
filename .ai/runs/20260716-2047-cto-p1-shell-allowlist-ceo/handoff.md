# Handoff — 20260716-2047-cto-p1-shell-allowlist-ceo

## Result

Addressed PR #16 CTO P1: removed `Bash(git *)` and `Bash(gh *)` from Splunky
Claude bootstrap and `splunk-clone/.claude/settings.json`. Added
`.ai/shared/references/contractor-provisional-shell-allowlist.json` and wired
ONBOARDING Phase 4 + contract.md to require owner-approved git/gh before
expansion.

## Verification

`verify-semantic-hierarchy` OK; `verify-agent-audit origin/main..HEAD` OK after commit.

## Risks

Branch-scoped push patterns assume work stays on `proj/splunk-clone/ctr-code-splunky/*`.
Owner must still approve git/gh in Phase 3 before treating shell access as fully authorized.

## Next safe action

Co-founder: cherry-pick or merge this commit onto PR #16 branch
(`cursor/agent-initialization-compliance-e6d3`) or retarget PR; Splunky remains
implementation `no_go` until ONBOARDING persona gate PASS.
