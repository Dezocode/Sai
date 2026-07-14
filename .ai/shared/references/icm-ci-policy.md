# ICM CI policy — canonical repo and forks

> Verified 2026-07-14. Implements [arXiv:2603.16021](https://arxiv.org/abs/2603.16021)
> enforcement on GitHub Actions for all governed Sai repositories.

## Governed repositories

| Repository | Role | Must run `agent-audit.yml` |
|---|---|---|
| `Dezocode/Sai` | Canonical upstream | Yes — required |
| `monaecode/Sai` | Co-founder fork | Yes — required |

Any new fork listed in `.ai/_config/repositories.yaml` inherits the same
requirement.

## What CI verifies

The `.github/workflows/agent-audit.yml` workflow runs on every push and on
PRs targeting `main`:

1. **`scripts/verify-agent-audit`** — commit trailers and audit metadata.
2. **`scripts/verify-semantic-hierarchy`** — ICM layer structure of `.ai/`:
   stage contracts, run grammar, registry, agent folders, no secrets in `.ai/`.
3. **JSON schema validation** — event and stage-output schemas; run metadata.

## Fork parity

Fork owners must:

1. Keep `.github/workflows/agent-audit.yml` identical to canonical (sync by SHA
   when mirroring, never recreate as unrelated commits).
2. Not disable or bypass the semantic hierarchy or audit verifiers.
3. Report CI failures to #agentupdates with `[SAI][BLOCKED]` or `[SAI][VERIFY]`.

The CEO agent (Sai) monitors fork CI status via `gh` and flags drift in
reports.

## Local enforcement (complements CI)

- **`pre-push`** hook blocks protected-ref pushes without valid audit trailers
  or semantic violations.
- **`scripts/agent-init`** verifies hooks, semantic hierarchy, and live hook
  self-test before an agent is considered initialized.

## Adding CI to a new fork

1. Ensure the fork has fetched latest `main` from `Dezocode/Sai`.
2. Confirm `.github/workflows/agent-audit.yml` exists and matches canonical.
3. Push a branch; confirm the Actions tab shows green `agent-audit` runs.
4. Record verification in a run under `.ai/runs/<task-id>/04_verify/`.
