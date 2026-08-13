# Handoff — 20260813-1517-auth-loop-cursor-cloud

## Outcome

Authorization/contract/Saul-Codex control plane is implemented on
`cursor/codebase-health-90ba` (PR #62). Local fixtures and e2e A–F, K–N,
S, V–Y pass. The system is **BLOCKED**, not READY FOR HUMAN REVIEW,
until GitHub Actions actually invokes Codex as Saul.

## Decision

`.ai/shared/memory/decisions/0006-agent-authorization-loop.md`

## Next safe action

1. Co-founder provisions GitHub Actions secret `OPENAI_API_KEY` (or
   `CODEX_API_KEY`) on Dezocode/Sai. Do not commit the value.
2. Re-run `saul-review.yml` on this PR (`workflow_dispatch` or push).
3. Cora consumes any REQUEST_CHANGES; contractor reloads the new revision.
4. Sai records `scripts/record-sai-verification` as identity `ceo` on the
   exact revision and SHA.
5. Human gate becomes READY only after Saul+Sai exact-head APPROVE, CI
   green, no stale approvals, no expansion gate.

## Do not

Merge, mark ready, close, force-push, or impersonate Saul on Cursor.
