# Gateway exposure policy — Alfred VPS (security default)

**Contract:** A0, A11 | **Amendment:** [20260722-saul-cto-review.md](../../../../../../../.ai/contracts/20260722-openclaw-dashboard-dezocode/amendments/20260722-saul-cto-review.md)

## Default (mandatory on bootstrap)

| Setting | Value | Rationale |
|---|---|---|
| `gateway.host` | `127.0.0.1` | Loopback only — no public Gateway listener |
| `gateway.port` | `18789` | Local Control UI + ingest |
| Slack mode | Socket Mode | Outbound to Slack — no inbound public HTTP required for Slack |
| Telegram | Pairing + DM policy | Bot token in VPS env only |

**Never** commit `openclaw.json` with secrets or `0.0.0.0` bind without documented exposure approval.

## Allowed remote access paths (pick one, document in run verify output)

### Option A — Tailscale (preferred)

1. Install Tailscale on VPS; join tailnet
2. Gateway stays on `127.0.0.1:18789`
3. Dashboard Mac/iOS clients reach VPS via Tailscale IP
4. Ingest WebSocket: `ws://100.x.x.x:18789/activity/stream` over tailnet

### Option B — TLS reverse proxy

1. Caddy/nginx on VPS terminates TLS
2. Proxy → `127.0.0.1:18789` with mTLS or OAuth at edge
3. Firewall: deny direct 18789 from public internet
4. Document cert rotation in host-health settings

### Option C — SSH tunnel (dev only)

1. `ssh -L 18789:127.0.0.1:18789 alfred@vps`
2. Not acceptable for production org onboarding alone — pair with A or B

## Enabling channels safely

| Channel | Before enable |
|---|---|
| Slack | Socket Mode app token in env; verify bot scopes minimal |
| Telegram | Pairing list reviewed; one route per agent_id |
| Dashboard auth | OAuth callbacks only on HTTPS proxy hostname |

## Verification

```bash
# Must show 127.0.0.1 (not 0.0.0.0) in effective config
openclaw config get gateway.host
ss -tlnp | grep 18789   # LISTEN 127.0.0.1:18789 only
openclaw-dashboard/scripts/verify-gateway-health.sh
```

Post `[SAI][VERIFY]` evidence path in handoff — no listener IPs in Slack (use "loopback verified").
