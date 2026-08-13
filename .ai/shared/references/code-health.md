# Codebase health policy (Layer 3)

> Decision: `0005-codebase-health-registry`. Registry:
> `.ai/_config/code-health.yaml`. Runner: `scripts/verify-code-health`.

## Commands

```bash
scripts/verify-code-health --self-test   # runtime evaluation (fixtures)
scripts/verify-code-health               # live: ci-coverage, bloat, duplicates, orphans
scripts/verify-code-health list          # registry dump
scripts/verify-code-health bloat         # one detector
```

CI (`.github/workflows/agent-audit.yml`) runs self-test, then the live scan,
on every push and every PR to `main`.

## Adding a check

1. Implement a deterministic command (prefer `scripts/verify-<name>`).
2. Add a row to `checks:` in `.ai/_config/code-health.yaml` with `status`,
   `command`, `ci_marker`, and `self_test`.
3. If `active`: put `ci_marker` verbatim in `agent-audit.yml` and give the
   check a self-test (`synthetic` for dispatcher detectors, `live-pass` for
   existing verifiers that already run on this repo).
4. If the stack does not exist yet, add `status: deferred` and
   `activate_when` instead of a silent skip.
5. Run `scripts/verify-code-health --self-test` and `scripts/verify-code-health`.

The meta-check **fails CI** when step 3 is skipped.

## What each live detector means

| Detector | Fail when | Not a fail |
|---|---|---|
| **Bloat** | Tracked file exceeds line/byte limit for its extension | Paths in `bloat.allowlist` (must include a reason in the commit) |
| **Duplicates** | Unexpected identical content, or Jaccard ≥ threshold on line shingles | Empty files; ICM families (runtime README stubs; mirrored `automation/profile.md`); excluded basenames (`CONTEXT.md`, `tools.json`, …) |
| **Orphans** | A file under `orphans.roots` is never mentioned by another tracked file | Mentions in docs, CI, hooks, or other scripts; `.ai/runs/` is not a scan corpus |
| **CI coverage** | Active `ci_marker` missing from the workflow, or a root `scripts/verify-*` is unregistered | `deferred` checks with a written `activate_when` |

## When the app stack is chosen

Promote the deferred rows (`app-unit-tests`, `app-import-orphans`,
`app-semantic-clones`) in the same commit that adds the stack decision
record and the real commands. Do not invent npm/pip tools before that
commit.

## Runtime evaluation

See `tests/code-health/README.md`. Fixture trees are built in `/tmp` so
known-bad oversized files are never committed.
