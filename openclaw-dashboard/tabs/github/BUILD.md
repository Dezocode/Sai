# BUILD — GitHub tab

## Phase 1: GitHub App

1. Register GitHub App (manifest in `integrations/github/` — no secrets in repo).
2. Install on Dezocode/Sai and monaecode/Sai.
3. Store creds on VPS.

## Phase 2: github-watch service

1. Webhooks: push, check_run, workflow_run.
2. Aggregate failure rate by project slug (parse branch prefix `proj/<slug>/`).
3. Emit events to activity-ingest.

## Phase 3: Desktop UI

1. Repo switcher: canonical vs fork.
2. Branch table: name, ahead/behind, CI badge, last actor.
3. Failure rate sparkline per project.

## Phase 4: Permissions

1. Respect user OAuth token for private fork visibility.
2. Service account for org-wide monitoring tiles.
