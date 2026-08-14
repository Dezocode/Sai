# Intake — Cora Hostinger bootstrap reuse of v12

Requester: parent pr62-primary / physical runtime
`bc-c7ecf2eb-bb68-557e-a2bf-fe78b61046cc`. Named child Cora
(`ctr-admin`), physical runtime
`bc-3386447c-2638-5def-a61d-8d4a3312b14e`. Grant
`grant-pr62-queue-cora`. Standing commit Task-ID
`20260813-2016-pr62-queue-cora`.

Exact requested outcome: confirm contract
`20260813-pr62-saul-smoke` **v12** already covers
Hostinger bootstrap P0-B and P0-C. Reuse
`ctr-code-pr62smoke` and `lease-c3a003pr62q1`. Do not
issue A-013/v13. Append REQ-SAUL-BOOTSTRAP-HEAD-001 and
REQ-SAUL-BOOTSTRAP-FALLBACK-001 (plus optional external
BLOCKED record) to `requirements/ledger.yaml` (YAML
≤300). Do not write blocker items, scripts, workflows,
decisions, or authorizations. Do not PASS, merge, push,
or mark ready.

## Repository facts (command-backed)

- HEAD `0df9a515f409b998822276d73de1ba7173fec1a5` matches
  `origin/cursor/codebase-health-90ba`. Draft PR #62.
- origin/main `40efe0a0724764fc1cf3c45ed8498b5606a0f453`
  (agent-audit.yml only).
- origin `github.com/Dezocode/Sai` canonical, not a fork.
- Working tree clean at intake.
- v12 `current_revision`. allowed_paths already include
  `.ai/runs/**`, `.ai/contracts/20260813-pr62-saul-smoke/**`,
  `tests/**`, `scripts/**`, `.github/workflows/**`,
  `.ai/_config/**`, `.ai/shared/schemas/**`.
- denied_paths: `.ai/agents/saul/**`,
  `.ai/shared/memory/decisions/**`, `.ai/authorizations/**`.
- Lease `lease-c3a003pr62q1` active, revision v12, agent
  `ctr-code-pr62smoke`, Task-ID
  `20260813-2017-pr62-queue-ctr-code`.
- No A-013.yaml / v13.yaml.

## Findings (not PASS)

- Real external Hostinger Codex review (not Cursor):
  SIGNED_ARTIFACT none, disposition BLOCKED, reason
  TRUSTED_BOOTSTRAP_NOT_ESTABLISHED.
- P0-A `/opt/sai/trusted-reviewer` absent: EXTERNAL
  operator. Cursor must not provision Hostinger. State
  WAITING_EXTERNAL_OPERATOR. Cora does not write a
  blocker item.
- P0-B bootstrap does not prove `SAI_CANDIDATE_TREE`
  HEAD == `--head`. Code under `scripts/**` (v12 covers).
- P0-C bootstrap falls back to
  `root/scripts/invoke-saul-review` and `saul-attest`.
  Confirmed `scripts/saul-hostinger-bootstrap-review`
  lines 66-69. Code under `scripts/**` (v12 covers).
- P1-D generic `[self-hosted]`: principal
  DEFERRED_NONBLOCKING. Do not create a blocker.
