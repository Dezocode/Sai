# Testing and verification reference (Layer 3)

## Current state

The repository has no accepted application stack and therefore no product
test suite yet (verified 2026-08-13). Until a stack is chosen, "relevant
verification" means the infrastructure checks below **plus**
`scripts/verify-code-health` whenever size, duplication, unreferenced
scripts, or CI wiring might change. See
`.ai/shared/references/code-health.md` and decision 0005.

## Infrastructure checks (apply now)

| Files touched | Required check |
|---|---|
| `scripts/*`, `.githooks/*` | `bash -n <file>` syntax check; executable bit set |
| `*.json` | parse with `python3 -m json.tool` or `jq .` |
| `*.yaml`, `*.yml` | parse with `python3 -c 'import yaml,sys;yaml.safe_load(open(sys.argv[1]))'` (or equivalent) |
| Event/manifest payloads | validate against `.ai/shared/schemas/*.schema.json` |
| Audit metadata | `scripts/verify-agent-audit <range>` |
| `.ai/**` structure | `scripts/verify-semantic-hierarchy` |
| Code health (bloat, duplicates, orphans, CI coverage) | `scripts/verify-code-health --self-test` then `scripts/verify-code-health` |
| Agent profiles, Claude SDK scaffold, contracts | `scripts/verify-agent-setup` |
| Scaffold / contract-review regressions | `scripts/verify-scaffold-safety` |

## Rules

1. Record exact commands and results in
   `.ai/runs/<task-id>/04_verify/output/verification.md`.
2. Record relevant failures verbatim, plus skipped checks and environment
   limitations.
3. Never describe a check as passing if it was skipped, unavailable, or only
   partially run. Write `skipped: <reason>` instead.
4. When application code exists, promote the deferred rows in
   `.ai/_config/code-health.yaml` (`app-unit-tests`, `app-import-orphans`,
   `app-semantic-clones`) in the same reviewed commit that records the stack
   decision. Do not leave stack test commands as comments in CI.
