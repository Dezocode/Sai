# Handoff — codebase health registry (0005)

- Task-ID: `20260813-1315-codebase-health-cursor-cloud`
- Agent: `cursor-cloud`
- Branch: `cursor/codebase-health-90ba`
- Status: implemented on a draft PR; not merged

## State

dezocode asked how to keep the tree healthy as the parent app starts to
land. This task installed a registry-driven gate so health checks cannot
exist only as docs:

- Registry: `.ai/_config/code-health.yaml`
- Runner: `scripts/verify-code-health` (`--self-test` then live)
- Policy: `.ai/shared/references/code-health.md` and decision 0005
- CI: `.github/workflows/agent-audit.yml` runs both invocations
- Local: `.githooks/pre-push` runs the live scan on `main`

Active detectors: CI coverage (every active `ci_marker` plus every root
`scripts/verify-*`), file bloat, exact/near duplicates, unreferenced
scripts. Deferred: app unit tests, import-graph orphans, AST clones,
OpenClaw ingest-latency stub, secrets-compliance until explicitly activated.

## Evidence

Local (this session):

- `scripts/verify-code-health --self-test` PASS (8 fixture evaluations)
- `scripts/verify-code-health` PASS (30)
- `scripts/verify-semantic-hierarchy` OK
- `scripts/verify-agent-audit origin/main..HEAD` OK
- `scripts/verify-merge-handoff origin/main..HEAD` OK

Draft PR: https://github.com/Dezocode/Sai/pull/62
Remote SHA at first push: `716c5aba8fe89d897942f957ed02cd65f7a8c17c`

GitHub Actions on the PR was not observed green in this session.

## Risks

- Near-duplicate Jaccard can false-positive on generated files; current
  excludes cover ICM templates. Tune thresholds in the YAML if CI flags a
  legitimate pair.
- Orphan detection is string mention, not a call graph.
- Decision 0005 and the Saul roadmap lane change wait on co-founder review
  of the draft PR.

## Next safe action

1. Co-founders review the draft PR (do not merge until ready).
2. When a product stack is chosen, promote deferred rows in the same commit
   as the stack decision record.
3. Optional follow-up: add negative fixture tests for pre-existing verifiers
   (`verify-semantic-hierarchy`, etc.) beyond live-pass.
