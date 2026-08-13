# 0006 — Repo-native agent authorization and independent Codex/Saul review

- Date: 2026-08-13
- Task-ID: 20260813-1517-auth-loop-cursor-cloud
- Status: accepted
- Approver: dezocode (PR #62 issue comment 5282088737 is the controlling
  FINAL ARCHITECTURE DECISION; comment 5281938753 is required groundwork
  unless it conflicts — 5282088737 wins)
- Source: https://github.com/Dezocode/Sai/issues/62#issuecomment-5282088737

## Decision

SAI write authorization is repo-native, fail-closed, and reconstructable
from Git. Runtime roles stay distinct:

- **Cursor Cloud** orchestrates and may implement only after assuming an
  authorized SAI identity. Unbound `cursor-cloud` / `cursoragent` is
  provenance, not authority.
- **Cora (`ctr-admin`)** is the Cursor-native Contract Administrator.
  When no applicable implementation agent exists, the runtime raises
  `CONTRACT_REQUIRED`, assumes Cora through `scripts/sai-assume-agent`,
  and Cora creates an immutable contract revision, provisional contractor
  identity, isolated branch/worktree, path/capability scope, and a
  `PROVISIONAL_EXECUTION` lease. Cora must not implement product or
  control-plane code under that identity.
- **Contractors** implement inside the current revision's lease. A new
  revision stale-s the old lease.
- **Saul (`dezo-sec-codex1`)** remains Codex-native. Do not create or
  assume Saul on Cursor. GitHub is the event bus; GitHub Actions invokes
  Codex via `scripts/invoke-saul-review` using `OPENAI_API_KEY` or
  `CODEX_API_KEY`. Missing credentials emit `disposition: BLOCKED`
  (`CODEX_UNAVAILABLE`), never APPROVE.
- **Sai (`ceo`)** independently records governance verification of the
  same exact contract revision and implementation SHA.
- **Human** is the final merge/authorization authority. Routine
  Cora↔contractor↔Saul loops do not require a human. Authority-expanding
  amendments stop for human approval.

Contracts are versioned and immutable (`revisions/vN.yaml`). Saul
`REQUEST_CHANGES` is machine-readable YAML. Cora maps
`CTO-id → amendment → vN+1` for ordinary technical changes. Dual final
readiness requires Cora admin complete, Saul APPROVE (runtime `codex`,
not synthetic) of the current revision and SHA, Sai APPROVE of the same,
CI green on that SHA, no stale approvals, no unresolved REQUEST_CHANGES,
and no pending expansion gate. A new SHA invalidates implementation
approvals; a new revision invalidates contract approvals.

Local session `.git/sai-session.json` is cache only. pre-commit,
pre-push, and GitHub CI replay tracked leases/revisions/registry.
Bootstrap task `20260813-1517-auth-loop-cursor-cloud` may land this
control plane; it is not a standing implementation identity.

## Context

PR #62 added codebase health gates (decision 0005). Unbound Cursor Cloud
was still making durable commits. Saul's Codex profile had no GitHub
event trigger. The co-founder required a complete event-driven loop, not
a Cursor impersonation of Saul.

## Alternatives considered

- **Wait for Codex Desktop native GitHub scheduling** — rejected; GitHub
  Actions is the durable event bus now.
- **Duplicate Saul as a Cursor agent** — rejected by 5282088737.
- **Trust local hooks / session files** — rejected; CI must replay Git.
- **Fake Saul APPROVE in tests as a stand-in for production** — rejected;
  fixtures are labeled synthetic and cannot satisfy the human gate.

## Rationale

Identity, contract revision, and independent CTO review must be
mechanically true or the commit/push/CI graph fails closed.

## Consequences

- New scripts and `.ai/requests/` + versioned contract revisions.
- Workflow `.github/workflows/saul-review.yml`.
- Codex secrets must be provisioned by a human before the loop is READY.
- Historical commits without `.ai/_config/authorization.yaml` are
  skipped by CI replay (pre-system).
