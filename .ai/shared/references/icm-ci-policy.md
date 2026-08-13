# ICM CI policy — canonical repo and forks

> Verified 2026-08-13 (code health registry, decision 0005). Implements [arXiv:2603.16021](https://arxiv.org/abs/2603.16021)
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
2. **`scripts/verify-scaffold-safety`** — scaffold path guards and contract-review regressions.
3. **`scripts/verify-agent-setup`** — agent profiles (verified caps, Claude Agent SDK
   scaffold, contract deliverables, hooks reporting/CI bindings).
4. **`scripts/verify-semantic-hierarchy`** — ICM layer structure of `.ai/`:
   stage contracts, run grammar, registry, agent folders, no secrets in `.ai/`.
5. **`scripts/verify-merge-handoff`** — every agent commit in the push
   range maps to a task-id with `handoff.md` or a HANDOFF event; pushes to
   `main` additionally require the tip commit's task-id to have handoff.
6. **`scripts/verify-code-health`** — registry-driven bloat, duplicate, and
   orphan scans, plus a meta-check that every **active** health check's
   `command` is an **unconditional** `run:` step in `icm-enforcement` (not a
   `grep`/comment mention, and not a `run:` under job/step `if:` such as
   `merge-handoff-slack`). CI runs `--self-test` first (runtime evaluation
   of dispatcher detectors). `live-pass` is not a negative evaluation.
   Policy: `.ai/shared/references/code-health.md`.
7. **Merge HANDOFF to #agentupdates** — on every push to `main`, CI job
   `merge-handoff-slack` runs `scripts/ci-merge-handoff-slack` (requires
   `SAI_SLACK_BOT_TOKEN` GitHub secret; when absent, agents must post via
   Cursor Slack MCP or `scripts/agent-report flush`).

8. **`scripts/verify-agent-authorization`** — synthetic identity/lease/path
   fixtures, then CI replay of the commit range from tracked Git (session
   files are not trusted).
9. **`scripts/verify-contract-authorization --self-test`** plus Saul
   invoke/consume self-tests. Human-gate is recorded fail-closed.
10. **`.github/workflows/saul-review.yml`** — GitHub event invokes Codex as
    Saul. Missing `OPENAI_API_KEY`/`CODEX_API_KEY` is BLOCKED, not APPROVE.

## Fork parity

Fork owners must:

1. Keep `.github/workflows/agent-audit.yml` identical to canonical (sync by SHA
   when mirroring, never recreate as unrelated commits).
2. Not disable or bypass the semantic hierarchy or audit verifiers.
3. Report CI failures to #agentupdates with `[SAI][BLOCKED]` or `[SAI][VERIFY]`.

The CEO agent (Sai) monitors fork CI status via `gh` and flags drift in
reports.

## Local enforcement (complements CI)

- **`pre-push`** hook blocks protected-ref pushes without valid audit trailers,
  semantic violations, missing merge HANDOFF documentation, or codebase
  health failures (`scripts/verify-code-health`).
- **`scripts/agent-init`** verifies hooks, semantic hierarchy, and live hook
  self-test before an agent is considered initialized.

## Adding CI to a new fork

1. Ensure the fork has fetched latest `main` from `Dezocode/Sai`.
2. Confirm `.github/workflows/agent-audit.yml` exists and matches canonical.
3. Push a branch; confirm the Actions tab shows green `agent-audit` runs.
4. Record verification in a run under `.ai/runs/<task-id>/04_verify/`.
