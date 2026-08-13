# Codex Desktop runtime — Saul

This is Saul's primary runtime suite. Load `CODEX.md`, then
`.ai/agents/saul/AGENT.md`. The authoritative capability inventory is
`tools.json`; it may be refreshed only from Saul's own live Codex Desktop
session with `--environment codex-desktop`.

Automation is session-driven on Codex Desktop. Unattended CTO review is
invoked by **GitHub Actions** (`.github/workflows/saul-review.yml` →
`scripts/invoke-saul-review`), which loads this Codex profile. That path
is **not operational** until a human provisions `OPENAI_API_KEY` or
`CODEX_API_KEY` on the GitHub repository and a real run records a Codex
invocation. Missing credentials fail closed (`BLOCKED` /
`CODEX_UNAVAILABLE`). Do not impersonate Saul on Cursor.
