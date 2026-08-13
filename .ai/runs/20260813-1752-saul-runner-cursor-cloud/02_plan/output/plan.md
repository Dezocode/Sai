# Plan — retarget Saul to the self-hosted runner and finish the production loop

## Intent (before edits)

Keep Decision 0006 / comment 5282088737 architecture. Change only the
obsolete GitHub-hosted + mandatory API-key execution path, the incomplete
Saul review package, and the still-unproven production smoke rows.

## Steps

1. **Runner targeting.** Set `.github/workflows/saul-review.yml` to
   `runs-on: [self-hosted]`. Do not guess a custom label. Record
   `runner.name`, OS/arch, hostname, `codex` presence/version (not auth
   files) in job logs. After the first assigned job, pin any additional
   labels returned by the Jobs API.
2. **Codex invoke.** If `codex` is on PATH, invoke it using the runner's
   persistent authenticated CLI. API keys remain an optional npx fallback
   only. Failed exec → `BLOCKED` with a truthful reason and accurate
   `codex_invoked`. Never synthesize APPROVE.
3. **Review package.** FINAL CTO review gets retrievable exact-head
   context: repo/PR/SHAs, contract revision + scope, prior findings,
   complete changed-file set, complete diff (file + prompt), CI status,
   architecture/security docs, schema. Intermediate deltas may highlight
   a bounded set but FINAL must cover the complete changed-file set.
4. **Policy/docs.** Update `authorization.yaml`, Decision 0006 amendment,
   Saul Codex README/profile, ICM CI policy. Production path is GitHub
   event → Actions → dedicated self-hosted Saul runner → local Codex CLI.
5. **Lazy first-write.** Register compact primary-runtime identity only
   when the pre-commit write gate first fires. No session-start init.
6. **Tests.** Keep local CODEX_UNAVAILABLE when no `codex` binary and no
   API-key fallback. Copy the new package module into e2e fixtures.
7. **Production smoke.** Push, observe assignment, then execute phases
   1–9 against a controlled contract flow. Update the existing A–Y
   matrix with run IDs. Do not impersonate Sai.

## Non-goals

Merge, ready-for-review, history rewrite, Cursor-as-Saul, secret files
in Git, session-start control-plane initialization.

## Risk

GitHub App token cannot list runners (403). If `[self-hosted]` never
picks up a job, stop and report that external blocker. If Codex exec
fails authentication on the runner, fail closed.
