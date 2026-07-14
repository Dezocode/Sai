# Plan — 20260714-0501-initialize-protocol-cursor-cloud-30d8

## Current behavior

Agents joining the SAI system have charters and rules to read, but no single
executable entry point: orientation to Slack/GitHub, hook installation,
role binding, naming, registration, and Cursor automation setup are spread
across documents and depend on agent diligence. The semantic hierarchy of
`.ai/` (ICM structure) is documented but not machine-enforced, so a
non-conforming run directory or missing stage artifact would merge silently.

## Desired behavior

- `.ai/INITIALIZE.md`: a read-and-execute protocol (Phases 0–7) that any
  agent can follow to full initialization, including asking its principal
  for a name and role title, registering in `.ai/agents/registry.json`, and
  creating its own Cursor automation for protocol upkeep.
- `scripts/agent-init`: automated Phase 2 — governed-repo check, hook
  install/verify, queue setup, honest environment report, CI-presence
  check, semantic + audit verification, and a live hook self-test.
- `scripts/verify-semantic-hierarchy`: machine enforcement of the ICM
  structure (required layer files, exact six stages, run/task-id grammar,
  metadata consistency, stage-order provenance, events.jsonl validity,
  registry validity, no secrets in `.ai/`), wired into **pre-push**
  (protected refs) and **CI** (every push and PR).

## Proposed file changes

New: `.ai/INITIALIZE.md`, `.ai/agents/registry.json`, `scripts/agent-init`,
`scripts/verify-semantic-hierarchy`, this run record.
Modified: `.github/workflows/agent-audit.yml` (semantic step),
`.githooks/pre-push` (semantic gate), `.ai/CONTEXT.md`,
`.cursor/rules/sai-coordination.mdc`, all three charters (initialization
sections), `.ai/shared/memory/repository-map.md`,
`.ai/shared/references/testing.md`, `scripts/install-agent-hooks` (chmod
list).

## Verification planned

bash -n on changed shell files; JSON/YAML parse; `verify-semantic-hierarchy`
against the live tree; negative tests (bad run name, missing metadata,
implement-without-plan, unknown stage, secret in `.ai/`); `agent-init`
failure and success paths plus live hook self-test in a scratch clone;
pre-push semantic gate blocking a violation on a protected ref while
allowing unprotected refs; CI green after push.

## Risks and rollback

The semantic gate could block future legitimate structures; the documented
`SAI_AUDIT_BYPASS` and a rule change via PR are the escape hatches. Rollback:
revert the commit; hooks remain opt-in.

## Review gates

PR #3 remains the human gate. No hard security gates triggered.
