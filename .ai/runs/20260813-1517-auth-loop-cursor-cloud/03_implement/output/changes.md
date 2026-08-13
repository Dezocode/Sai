# Implementation — authorization control plane

Landed decision 0006 and the tracked surface required by PR #62 comment
5282088737:

- Policy `.ai/_config/authorization.yaml`
- Schemas for request, lease, revision, review, amendment
- `.ai/requests/` plus versioned `.ai/contracts/<id>/revisions/`
- Scripts: sai-authorize-task, sai-assume-agent, sai-release-agent,
  verify-agent-authorization, verify-contract-authorization,
  invoke-saul-review, consume-saul-contract-review, record-sai-verification
- pre-commit, commit-msg, prepare-commit-msg, pre-push replay
- `agent-audit.yml` CI replay + synthetic fixtures
- `saul-review.yml` GitHub → Codex/Saul (fail-closed without secrets)
- Docs: INITIALIZE, ONBOARDING, Cora/Saul/Sai, security, CI, testing,
  architecture, repository map

Bootstrap: this introducing commit uses Task-ID
`20260813-1517-auth-loop-cursor-cloud` (unbound Cursor Cloud landing the
control plane). Cora/contractor identity transitions are proven in
`tests/authorization/e2e.py`.
