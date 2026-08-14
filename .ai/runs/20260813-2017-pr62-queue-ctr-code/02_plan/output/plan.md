# Plan — SAUL-BOOTSTRAP P0 (v12 reuse)

Parent pr62-primary. Lease lease-c3a003pr62q1. HEAD confirmed
`d4e86cbcd9f342a0bae9836483461ec2134b4c17` (Cora reused v12).
Do not PASS, push, merge, impersonate Saul, restore saul-review.yml,
write production keys, create `/opt/sai/trusted-reviewer`, or SSH Hostinger.
P1-D runner label is DEFERRED_NONBLOCKING — no new blocker/allowlist.

## Current vs desired

Operator `scripts/saul-hostinger-bootstrap-review` defaults
`SAI_CANDIDATE_TREE` to repo root and, if trusted invoke/attest are
missing, falls back to `root/scripts/...` (candidate if cwd is
candidate). No check that candidate HEAD equals `--head`. Forbidden.

Desired: hermetic `sai_auth_bootstrap.py` fail-closed on mutable refs,
HEAD mismatch, non-git candidate, unresolved SHA, and missing trusted
executables. Never substitute candidate copies. Re-check HEAD before
invoke (TOCTOU). Record external Hostinger Codex as BLOCKED evidence
(not a qualifying Saul review). Manifest is INFORMATION only.

## File changes

- NEW `scripts/lib/sai_auth_bootstrap.py` — helpers (not identity module)
- EDIT `scripts/saul-hostinger-bootstrap-review` — require env + --head;
  delete fallback; trusted executables only
- NEW `scripts/lib/sai_auth_bootstrap_test.py` — hermetic git fixtures
- EDIT `.github/workflows/agent-audit.yml` — run bootstrap tests
- EDIT `scripts/lib/sai_auth_blockers.py` — cheap self-test import
- EDIT `scripts/lib/sai_auth_blockers_test.py` — LIVE_REQUIRED + no PASS
- NEW blockers HEAD/FALLBACK/TREE; evidence yaml+manifest+handoff;
  merge-readiness logical WAITING_EXTERNAL_REAL_SAUL
- Denied: `.ai/agents/saul/**`, decisions, authorizations

## Verification

`python3 scripts/lib/sai_auth_bootstrap_test.py`;
`saul-attest` / `sai-blockers` / `invoke-saul-review` /
`verify-saul-workflow-trust` / `verify-agent-authorization` self-tests;
bootstrap `--self-test` exit 2; line limits; no fallback assignment;
`saul-review.yml` absent.

# Plan — contractor remediation CTO-009/010/011

Implement tracked officer grants in replay, close bootstrap at d113fa0,
run Saul reviewer code from SAI_TRUSTED_TREE, and make duplicate dispatch
evals NOOP. Do not become Sai or Cora. Do not merge.

## Wave SAUL-IDENTITY-001 (v12 reuse, no A-013)

See `identity-plan.md`. Bind Saul identity to Hostinger Ed25519 attestation.
Cursor named subagent is not Saul. Do not PASS. Do not merge/push.
