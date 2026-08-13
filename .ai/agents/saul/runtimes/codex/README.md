# Codex Desktop runtime — Saul

This is Saul's primary runtime suite. Load `CODEX.md`, then
`.ai/agents/saul/AGENT.md`. The authoritative capability inventory is
`tools.json`; it may be refreshed only from Saul's own live Codex Desktop
session with `--environment codex-desktop`.

Automation is session-driven on Codex Desktop. Unattended CTO review is
invoked by **GitHub Actions** (`.github/workflows/saul-review.yml` on
`[self-hosted]`) → dedicated Dockerized Saul runner → local authenticated
Codex CLI → `scripts/invoke-saul-review`, which loads this Codex profile.
Repository `OPENAI_API_KEY` / `CODEX_API_KEY` secrets are optional
fallback only, not the production prerequisite. Missing or failed local
`codex exec` fails closed (`BLOCKED` / truthful reason, with
`codex_invoked` reflecting whether execution was attempted). Do not
impersonate Saul on Cursor. Do not copy or commit Codex auth files.
