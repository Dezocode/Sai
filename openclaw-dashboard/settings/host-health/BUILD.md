# BUILD — Host health settings

1. Implement `verify-gateway-health.sh` (exit 0 when Gateway + Control UI OK).
2. VPS agent cron: run health checks every 60s → emit to activity-ingest.
3. Desktop panel: green/yellow/red tiles + last 24h uptime chart.
4. Link to `docs/vps-bootstrap.md` for Alfred bootstrap checklist.
5. Surface ingest p99 from tracking SLO alongside host metrics.
