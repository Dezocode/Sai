# Duplication: runtime→suite mapping in four places

Issue: https://github.com/Dezocode/Sai/issues/180

## Problem

The runtime→suite mapping (cursor/claude/codex/openclaw — which test
suite runs for which agent runtime) is defined in **four** places, and the
copies have already diverged:

1. **Embedded-Python agent-verification helpers (NEAR).**
   `scripts/verify-agent-setup:23-45` vs
   `scripts/verify-semantic-hierarchy:33-58`: identical `fail()`,
   identical `RUNTIME_SUITE` dict, near-identical capability loaders
   (one has an extra existence check + fallback).
2. **Runtime→suite case block in scaffold scripts (NEAR, diverged).**
   `scripts/agent-scaffold:33-36` vs
   `scripts/agent-contract-scaffold:56-59`: same four mappings, but
   `agent-scaffold` writes `RUNTIME_ENV=` while
   `agent-contract-scaffold` writes `PRIMARY_RUNTIME=` for the env value
   — a variable-naming fork.

## Impact

- Adding a runtime (e.g. a new provider env) needs four synchronized
  edits; a missed one silently narrows or widens what CI verifies.
- CI gates (`.github/workflows/agent-audit.yml` runs both verify
  scripts) can disagree about what's valid.
- Downstream consumers expecting one variable name break on the other
  (`RUNTIME_ENV` vs `PRIMARY_RUNTIME`).

## Recommended consolidation

- Extract the embedded Python into `scripts/lib/sai_verify_lib.py`,
  imported by both verify scripts (thin bash wrappers remain).
- Add `guard_runtime_env <runtime>` to
  `scripts/lib/agent-path-guards.sh` (already sourced by both
  scaffolds) emitting both values — or pick one name and migrate.

## Steering prompt (agent-executable)

> In Dezocode/Sai, consolidate the runtime→suite mapping per
> https://github.com/Dezocode/Sai/issues/180. (1) Move the embedded
> Python shared by `scripts/verify-agent-setup` (lines 23-45) and
> `scripts/verify-semantic-hierarchy` (lines 33-58) — the identical
> `fail()`, `RUNTIME_SUITE` dict, and capability loaders — into a new
> `scripts/lib/sai_verify_lib.py`; both scripts become thin bash
> wrappers importing it. Preserve the extra existence check + fallback
> found in the `verify-semantic-hierarchy` copy. (2) Unify the
> runtime→suite case blocks in `scripts/agent-scaffold` (lines 33-36)
> and `scripts/agent-contract-scaffold` (lines 56-59) by adding a
> `guard_runtime_env <runtime>` helper to
> `scripts/lib/agent-path-guards.sh` (already sourced by both
> scaffolds); resolve the `RUNTIME_ENV=` vs `PRIMARY_RUNTIME=` fork by
> picking ONE name (grep consumers first, migrate the minority). (3)
> Run both verify scripts and the `agent-audit` workflow checks after
> the change. Do not change what the mapping maps — only where it
> lives. Open a PR; do not merge it yourself.
