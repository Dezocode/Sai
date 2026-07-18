# Testing and verification reference (Layer 3)

## Current state

The repository has no application code and therefore no test suite yet
(verified 2026-07-14). Until a stack is chosen, "relevant verification" for
a change means the checks below that apply to the files touched.

## Infrastructure checks (apply now)

| Files touched | Required check |
|---|---|
| `scripts/*`, `.githooks/*` | `bash -n <file>` syntax check; executable bit set |
| `*.json` | parse with `python3 -m json.tool` or `jq .` |
| `*.yaml`, `*.yml` | parse with `python3 -c 'import yaml,sys;yaml.safe_load(open(sys.argv[1]))'` (or equivalent) |
| Event/manifest payloads | validate against `.ai/shared/schemas/*.schema.json` |
| Audit metadata | `scripts/verify-agent-audit <range>` |
| `.ai/**` structure | `scripts/verify-semantic-hierarchy` |
| Agent profiles, Claude SDK scaffold, contracts | `scripts/verify-agent-setup` |
| Scaffold / contract-review regressions | `scripts/verify-scaffold-safety` |

## Rules

1. Record exact commands and results in
   `.ai/runs/<task-id>/04_verify/output/verification.md`.
2. Record relevant failures verbatim, plus skipped checks and environment
   limitations.
3. Never describe a check as passing if it was skipped, unavailable, or only
   partially run. Write `skipped: <reason>` instead.
4. When application code exists, extend this file with the stack's test,
   lint, type-check, build, migration, and security commands via a reviewed
   commit.
