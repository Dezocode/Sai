# Plan — CTO P1 provisional shell allowlist

## Problem

Splunky bootstrap and `splunk-clone/.claude/settings.json` granted `Bash(git *)` and
`Bash(gh *)` while registry status is `provisional` and `approved_capabilities[]` is empty.

## Approach

1. Add Layer 3 reference `contractor-provisional-shell-allowlist.json` with explicit patterns and documented exclusions aligned with `security-policy.md`.
2. Apply the allowlist to contract bootstrap and live Splunky settings; document reference path in `$comment`.
3. ONBOARDING Phase 4: require owner-approved git/gh before expanding beyond provisional list.
4. Verify JSON parse + semantic hierarchy + agent audit on branch.

## Out of scope

Broadening MCP grants, merging PR #16, or marking Splunky `active`.
