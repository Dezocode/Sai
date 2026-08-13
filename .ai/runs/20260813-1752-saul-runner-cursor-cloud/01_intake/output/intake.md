# Intake — continue PR #62 from the Saul runner boundary

- Task-ID: `20260813-1752-saul-runner-cursor-cloud`
- Continues: `20260813-1517-auth-loop-cursor-cloud`
- Requester: dezocode (`U0BHYH0NMCY`)
- Repository: `Dezocode/Sai` (canonical)
- Branch: `cursor/codebase-health-90ba` (draft PR #62)
- Exact prior head: `0676b13316994e049c8bacf16f2d8bd57c547c6c`
- Working tree at intake: clean, matching origin

## Requested outcome

Finish the existing authorization/Codex/Saul loop on PR #62. Do not restart
or redesign. The previously missing Saul execution host may now exist as a
Dockerized self-hosted GitHub Actions runner with an already-authenticated
Codex CLI. Verify that through GitHub, retarget the workflow to the real
runner labels, stop treating repository API keys as the required production
path, strengthen the Saul review package, keep lazy first-write + compact
primary-runtime signaling, and prove the real production smoke sequence.

## Constraints (settled)

- Comment 5282088737 is the controlling FINAL architecture.
- Comment 5281938753 is required groundwork unless it conflicts.
- Comment 5283061641 (Saul REQUEST_CHANGES) still applies: real production
  loop proof, lazy first-write, token-optimized compact orchestrator.
- Do not merge, mark ready, close, force-push, rewrite history, expose
  OAuth files, move Codex credentials into Git, or convert Saul to Cursor.
- Unbound `cursor-cloud` must not impersonate Sai (`ceo`) or Saul.

## External discovery at intake

`gh api repos/Dezocode/Sai/actions/runners` returned HTTP 403
("Resource not accessible by integration"). Org runner list returned 404.
The current GitHub App token cannot list runner configuration. Latest
`saul-cto-review` job (run `31717977028`) used GitHub-hosted
`ubuntu-latest` / runner name `GitHub Actions 1000001258` with empty API
keys and `codex_invoked: false`. No later Saul runs exist yet.

Runner name/labels will be proven by assigning a real job to
`runs-on: [self-hosted]` (GitHub's built-in self-hosted label; not a guessed
custom label such as `saul-codex`) and reading `runner_name` / `labels`
from the Jobs API after assignment. If the job never leaves the queue, that
is the remaining external blocker.

## Acceptance (READY FOR HUMAN REVIEW)

All 21 items in the continuation request must be evidenced. Otherwise
report `BLOCKED / REQUEST_CHANGES` with the exact remaining item.
