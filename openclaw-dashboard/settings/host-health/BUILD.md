# BUILD — Host health settings

A0 scaffolds exist in repo — **enhance on VPS**, do not recreate from scratch:

1. `scripts/verify-gateway-health.sh` — exit 0 when Gateway + doctor/HTTP OK
2. `host/systemd/openclaw-gateway.service` — loopback unit template
3. `docs/vps-bootstrap.md` — Alfred A0-1–A0-6 steps

Next (post-A0):

4. VPS agent cron: health checks every 60s → emit to activity-ingest
5. Desktop panel: green/yellow/red tiles + last 24h uptime chart
6. Surface ingest p99 from tracking SLO alongside host metrics
