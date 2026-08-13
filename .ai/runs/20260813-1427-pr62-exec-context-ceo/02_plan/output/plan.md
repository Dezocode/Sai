# Plan — bind CI coverage to icm-enforcement execution context

- Task-ID: `20260813-1427-pr62-exec-context-ceo`
- Intake: `.ai/runs/20260813-1427-pr62-exec-context-ceo/01_intake/output/intake.md`
- Decision: 0005 (amend; do not silently rewrite)
- Relies on: `.ai/shared/memory/architecture.md`, `code-health.md`,
  `icm-ci-policy.md`

## Current vs desired

`workflow_invocations()` YAML-walks every `run:` in `agent-audit.yml` and
ignores job id, job `if:`, and step `if:`. An active verifier moved into
`merge-handoff-slack` (`if: github.ref == 'refs/heads/main' && github.event_name == 'push'`)
still counts as covered, which violates “active checks run on every
push/PR”.

Desired: a `run:` counts only when it is in `ci.coverage_jobs` (default
`icm-enforcement`), the job has no `if:`, and the step has no `if:`.

## File changes

| Path | Change |
|---|---|
| `scripts/lib/code-health-ci.py` | Walk `jobs`/`steps`; filter by allowed jobs and absence of `if:`; stop recursive uncontextual `run:` collection |
| `scripts/lib/code-health.py` | Positive fixture job named `icm-enforcement`; add `ci-coverage-conditional-job` and `ci-coverage-step-if` negatives |
| `.ai/_config/code-health.yaml` | `ci.coverage_jobs: [icm-enforcement]`; list new fixtures |
| `.ai/shared/references/code-health.md` | Document execution-context rule |
| `.ai/shared/references/icm-ci-policy.md` | Same |
| `tests/code-health/README.md` | Document new fixtures |
| `.ai/shared/memory/decisions/0005-*.md` | Amendment: execution context + Sai provenance re-affirmation |
| `.ai/shared/memory/architecture.md` | One-sentence coverage context |
| `.ai/agents/saul/roadmap.json` / `roadmap.md` | Re-affirm lanes as Sai; statuses unchanged (code-health `active`, semantic tracking `proposed`) |
| This run directory | intake/plan/implement/verify/review/publish/handoff |

No workflow job moves. Live `agent-audit.yml` already places active
verifiers in unconditional `icm-enforcement` steps.

## Justification

Saul P1 is a policy hole, not a live mis-wiring. The meta-check must make
the policy claim true. Durable Decision 0005 and roadmap edits on this PR
were committed as `Agent: cursor-cloud`; registry has no such identity.
Re-commit those records as `Agent: ceo` (Sai) without changing lane
statuses.

## Verification

- `scripts/verify-code-health --self-test` (must execute new fixtures)
- `scripts/verify-code-health`
- `scripts/verify-semantic-hierarchy`
- `scripts/verify-agent-audit origin/main..HEAD`
- `scripts/verify-merge-handoff origin/main..HEAD`
- YAML/JSON parse of touched configs
- GitHub Actions `agent-audit` on the new head

## Risks / rollback

- Strict `if:` rejection may later need an allowlist for `always()`;
  out of scope. Rollback: revert this run's commit on the PR branch.

## Review gates

- PLAN posted before edits.
- Remain draft. Fresh Saul exact-head review. Do not merge.
- Decision 0005 amendment is documentation of existing CI policy, not a
  new architecture fork.

## Human review

dezocode already instructed this remediation. No security-policy hard gate.
Proceed after PLAN.
