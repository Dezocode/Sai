# VPS bootstrap — Alfred A0

1. Provision Hostinger VPS (Ubuntu 22.04+).
2. Install Node 24.15+ per https://docs.openclaw.ai/
3. `npm install -g openclaw@latest && openclaw onboard --install-daemon`
4. Install systemd unit from `host/systemd/` (add template in BUILD).
5. Configure reverse proxy / Tailscale per `settings/host-health/`.
6. Run `scripts/verify-gateway-health.sh` and `scripts/verify-all-dependencies.sh`.

ICM run required with `handoff.md` evidence.
