# Settings: Host health

| Field | Value |
|---|---|
| **Deliverable** | A0 |
| **Desktop route** | `/settings/host-health` |

## Owner requirement

OpenClaw **Hostinger VPS** connection health in dashboard:

- Gateway process / systemd status
- Control UI HTTP probe
- Latency to ingest WebSocket
- Disk, memory, Node version
- `openclaw doctor` last run summary

## Paths

- `host/systemd/openclaw-gateway.service`
- `scripts/verify-gateway-health.sh`
- `docs/vps-bootstrap.md`

Build: [BUILD.md](./BUILD.md)
