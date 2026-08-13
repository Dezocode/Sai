# Intake — agent authorization loop

- Task-ID: `20260813-1517-auth-loop-cursor-cloud`
- Requester: dezocode (`U0BHYH0NMCY`) via Cursor Cloud
- Run URL: https://cursor.com/agents/bc-019ffb40-0226-731b-9d22-f5f991d490ba
- Repository: `Dezocode/Sai` (canonical, not a fork)
- Branch: `cursor/codebase-health-90ba` (draft PR #62)
- Base SHA at intake: `5c8f889e45c85dfbc687b0269a28a5aa7bab2918`

## Requested outcome

Fully implement the mandatory end-state in PR #62 issue comment `5282088737`.
Implement comment `5281938753` groundwork unless it conflicts; `5282088737`
controls. Do not merge, mark ready, close, or rewrite history.

## Verified facts

- Working tree was clean at intake SHA.
- No authorization scripts, `.ai/requests/`, pre-commit hook, or Saul
  GitHub workflow existed.
- Saul Codex README stated no GitHub event trigger is configured.
- `gh secret list` returned no OpenAI/Codex secret. Real Codex invocation
  is an external credential boundary.
- This runtime is unbound `cursor-cloud` / `cursoragent@cursor.com`, not a
  registered SAI identity.

## Non-negotiable roles (from 5282088737)

Cursor Cloud = orchestration/implementation runtime. Cora = Cursor-native
contract administrator (not product coder). Contractors = implementation
identities. Saul = Codex-native CTO (do not impersonate as Cursor). GitHub
= event trigger. GitHub Actions invokes Codex/Saul. Sai = independent
governance. Human = final authority.
