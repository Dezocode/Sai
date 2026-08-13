# 0005 — Quality OS as additive control plane; executable slice G00–G03

- Date: 2026-08-13
- Task-ID: 20260813-0307-quality-os-improve-cursor-cloud
- Status: proposed
- Approver: pending dezocode / monaecode (review of PR stacked on #59)

## Decision

Adopt `.sai-quality/` as an **additive** quality control plane beside ICM (`.ai/`). It does not replace agent coordination, charters, or `agent-audit.yml`.

Until co-founders explicitly approve G04+ supply-chain pinning:

- The executable slice is G00–G03 (`qualityctl build --through G03`).
- G04–G15 remain catalogued and `required_for_unlock`, but are `deferred`.
- Product feature lock stays active. `qualityctl unlock` must not succeed.
- Do not install or stand up SonarQube, Dependency-Track, or Renovate on Cursor Cloud or GitHub Actions as part of Phase 0 bootstrap.

ICM remains the agent-governance system. `openclaw-dashboard/` remains an isolated prototype (DR-20260724), not a Quality OS product root.

## Context

PR #59 added a pstack-informed G00–G15 Quality OS overlay. Review found the narrative plan sound and the machine loop not executable: later gates checked lockfile pins or always-printed PASS; G14 contradicted unpinned `checkout@v4`; root zip docs fought ICM; an alwaysApply Cursor rule would bind every agent.

## Alternatives considered

- **Execute `build --through G15` as written** — rejected. It stalls at unresolved tools or rubber-stamps scanners.
- **Merge the bootstrap and treat green CI as unlock** — rejected. CI only proved G00–G02.
- **Delete the overlay** — rejected. Registry/adapters/evidence and the feature-lock *intent* are worth keeping after honesty fixes.

## Rationale

A quality factory is useful before parent/child product UI. It is only useful if gates mean what they say. G00–G03 can run on this repo now (Python stdlib, no product stack). G04+ is a supply-chain and infra decision (binaries, Docker services, Renovate PRs) and needs a separate approval.

## Consequences

- Docs live under `.sai-quality/docs/`, not the repository root.
- `.cursor/rules/95-sai-quality-os.mdc` is glob-scoped, not alwaysApply.
- Quality workflows pin `actions/checkout` by SHA and verify `--through G03`.
- Unlock stays blocked until G04+ is approved and actually runs the named tools.
