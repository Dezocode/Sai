# Grok Runtime Intelligence container

Decision 0007 Phase C: substantive RI findings run in a dedicated container with
a verified reasoning model and `reasoning_effort=high`.

- Image does **not** embed API keys; host `/root/.grok` is mounted read-only.
- Does **not** replace `grok-telegram-worker.service` (Telegram bridge stays host systemd).
- Organizational status remains **PROVISIONAL** until Saul + Sai + human approve
  the exact init SHA on the stacked sub-PR.

```bash
cd runtime-intelligence/docker
docker compose build
docker compose run --rm grok-ri status
docker compose run --rm -e RI_GROK_EFFORT=low grok-ri deep-findings "x"  # must refuse
```
