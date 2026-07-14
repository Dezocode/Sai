# Stage 06 — Publish and synchronize

## Purpose

Publish the reviewed change to GitHub, verify remote state, replicate to
Drive, and hand off.

## Inputs

| Layer | Path | What to load |
|---|---|---|
| 4 | `.ai/runs/<task-id>/05_review/output/review.md` | Review disposition |
| 3 | `.ai/shared/references/git-workflow.md` | Push/PR rules |
| 3 | `.ai/_config/sync-policy.md` | Drive replication rules |
| 3 | `.ai/_config/reporting.yaml` | Report format |

## Process

1. Commit atomically with descriptive messages and the `Task-ID`, `Agent`,
   `Plan`, `Report-Event` trailers.
2. Push the task branch to the intended remote
   (`git push -u <remote> <branch>`), retrying transient failures with
   backoff.
3. Open or update the appropriate PR (target per
   `.ai/_config/repositories.yaml`, default `Dezocode/Sai:main`).
4. **Do not** force-push, merge, close, or mark ready for review without
   explicit authorization.
5. Verify the remote commit SHA
   (`git ls-remote <remote> refs/heads/<branch>` equals local HEAD).
6. Publish the audit events (COMMIT, PUSH, PR) via `scripts/agent-report`;
   flush any queued events in order.
7. Update the Drive mirror via `scripts/agent-sync-drive` **only after** the
   GitHub verification in step 5; record the resulting status honestly.
8. Write `handoff.md` and post the final HANDOFF report.

## Outputs

- Pushed branch and PR.
- `.ai/runs/<task-id>/06_publish_sync/output/publish.md` — remote SHA
  verification evidence, PR link, Drive sync record.
- `.ai/runs/<task-id>/handoff.md` — final state, evidence for every claim,
  risks and skipped checks, next safe action.
- HANDOFF report to #agentupdates.

## Verification

The remote SHA check in step 5 is mandatory. A task is complete only when:
requested behavior is implemented or conclusively investigated; relevant
verification has run; authorized changes are committed and pushed; the PR is
updated; the remote SHA is verified; Slack reports are delivered or queued;
Drive sync is verified or explicitly pending/failed; memory and docs are
accurate; risks and skipped checks are disclosed. Never say "fully
synchronized", "all tests pass", or "complete" without evidence for each
claim.

## Human review gate

The PR itself. Merging is always a human (or human-authorized) action.

## Rollback

A pushed but unmerged branch is inert: post BLOCKED/HANDOFF describing the
state. Deleting a pushed branch is a destructive action requiring approval.

## Provenance

`publish.md` links commit SHAs, push output, PR URL, event IDs, and Drive
checksums.
