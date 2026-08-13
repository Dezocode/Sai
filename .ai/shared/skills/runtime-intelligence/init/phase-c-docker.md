# Phase C — Dockerized Grok (PROVISIONAL)

## Paths
- `runtime-intelligence/docker/Dockerfile.grok-ri`
- `runtime-intelligence/docker/docker-compose.yml`
- `runtime-intelligence/docker/entrypoint.sh`

## Model policy
- Default model env: `RI_GROK_MODEL=grok-4.5` (verify at runtime against `grok models`)
- Default effort: `RI_GROK_EFFORT=high`
- `deep-findings` command **refuses** non-high effort

## Separation
Telegram bridge remains host systemd (`grok-telegram-worker.service`).
This container is for Runtime Intelligence experiment/findings isolation.

## Status
Built/run evidence recorded by `run-phase-i-matrix` item 14. Org ACTIVE not claimed.
