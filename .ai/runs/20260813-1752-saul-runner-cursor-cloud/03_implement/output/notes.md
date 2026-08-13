# Implement notes — self-hosted Saul runner retarget

Changed the obsolete GitHub-hosted + mandatory API-key path without
redesigning Decision 0006.

- `.github/workflows/saul-review.yml` now `runs-on: [self-hosted]` (GitHub
  built-in label; custom labels will be pinned after Jobs API evidence).
  Empty `OPENAI_API_KEY`/`CODEX_API_KEY` are unset so they cannot override
  local Codex OAuth. Runner identity and `codex --version` are logged;
  auth files are not.
- `scripts/lib/sai_auth_review.py` invokes an installed local `codex`
  without requiring API keys. Keys remain npx fallback only. Failed exec
  is BLOCKED with truthful reason and accurate `codex_invoked`.
- `scripts/lib/sai_auth_package.py` builds a retrievable FINAL package:
  metadata, complete changed-file set, complete diff, contract, prior
  findings, CI status, schema/docs.
- Lazy first-write: `ensure_primary_runtime` runs only when pre-commit
  sees staged paths. No session-start init.
- Policy/docs updated (authorization.yaml, Decision 0006 amendment, Saul
  Codex README/profile/prompt, ICM CI policy).

Local self-tests and e2e A–F/K–N/S/V–Y still pass. Production H–J/P–U
await the first self-hosted job assignment.
