# Handoff — 20260824-1010-pr77-cred-patterns-ox-alpha

## What changed
- --check banned-token gate upgraded: credential-SHAPED patterns (gh[pousr]_*, github_pat_* with length floors) are rejected on BOTH feature-maps.html and pr-sessions.html with redacted reporting; X-Sessions-Token stays banned everywhere; GH_TOKEN/GITHUB_TOKEN name-bans stay scoped to pr-sessions.html because protected-ci legitimately documents policy by name.

## Verification
Injected ghp_ABCDEFGHIJKLMNOPQRSTUVWX into BASE_CSS of a temp copy: --check fails citing 'contains a credential-shaped token' on BOTH pages. Clean tree: --selftest ALL PASS, --check ALL PASS features=11.
