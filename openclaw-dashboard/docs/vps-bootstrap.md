# VPS bootstrap — Alfred A0 (merge + paste)

**Audience:** dezocode (one-time VPS prep) + Alfred (executable A0 on paste).  
**Contract:** `20260722-openclaw-dashboard-dezocode`  
**Two-step deploy:** merge PR #45 → paste `first-prompt-attach-contract.md` into OpenClaw.

---

## dezocode — before paste (≈10 minutes, one time)

On Hostinger VPS (Ubuntu 22.04+):

```bash
# 1. Node 24.15+ (see https://docs.openclaw.ai/)
node -v   # must be v20+ ; v24.15+ recommended

# 2. OpenClaw CLI
npm install -g openclaw@latest
openclaw onboard --install-daemon

# 3. Clone canonical repo at post-merge main
git clone https://github.com/Dezocode/Sai.git
cd Sai
git checkout main && git pull origin main

# 4. Optional: create sai.env skeleton (values filled during A0/A2 — not in Git)
sudo mkdir -p /etc/openclaw
sudo touch /etc/openclaw/sai.env
sudo chmod 600 /etc/openclaw/sai.env
# Alfred will request MCQ for TELEGRAM_BOT_TOKEN, SLACK_*, etc. when needed
```

Then open a **fresh OpenClaw Gateway session** and paste the entire contents of:

`.ai/contracts/20260722-openclaw-dashboard-dezocode/first-prompt-attach-contract.md`

---

## Alfred — A0 execution order (on paste)

Execute in order. Post `[SAI][PLAN]` before repo edits. Telegram INTAKE to dezocode first.

### Step A0-1 — Bind + worktree

```bash
cd /path/to/Sai
git fetch origin main
git worktree add ../sai-alfred-bootstrap proj/openclaw-dashboard/ctr-code-alfred1/bootstrap 2>/dev/null \
  || git checkout -b proj/openclaw-dashboard/ctr-code-alfred1/bootstrap
cd ../sai-alfred-bootstrap || true
```

Create `.ai/runs/<task-id>/` per first-message §0.

### Step A0-2 — Dependency gate

```bash
openclaw-dashboard/scripts/verify-all-dependencies.sh
```

If FAIL: install missing packages, re-run until PASS. Do not proceed.

### Step A0-3 — Gateway loopback

```bash
openclaw gateway --host 127.0.0.1 --port 18789 &
sleep 3
openclaw dashboard   # confirm Control UI
openclaw doctor      # save output to run artifacts
openclaw-dashboard/scripts/verify-gateway-health.sh
openclaw-dashboard/scripts/verify-gateway-bind.sh
```

If health FAIL: fix Gateway config, re-run. Loopback **127.0.0.1 only** (Saul P1).

### Step A0-4 — Systemd (production path)

Enhance template if needed (never embed secrets):

- `openclaw-dashboard/host/systemd/openclaw-gateway.service`

```bash
sudo cp openclaw-dashboard/host/systemd/openclaw-gateway.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable openclaw-gateway
sudo systemctl start openclaw-gateway
openclaw-dashboard/scripts/verify-gateway-health.sh
```

### Step A0-5 — Secrets (BLOCKED → MCQ, not dead stop)

Read `secrets-security.md` and `auth-matrix.md`.

- If `/etc/openclaw/sai.env` missing required values:
  1. Write `continuation_checkpoint` (see BLOCKED-MCQ-CONTINUATION.md)
  2. Telegram MCQ to dezocode with **2–4 complete plans** (e.g. provide tokens now / doc-only continue / defer with HANDOFF)
  3. Mirror `[SAI][BLOCKED]` to Slack (plan titles only)
  4. **Wait** for plan selection → resume from checkpoint
- Do not guess secrets; do not proceed on blocked path without selected plan

### Step A0-6 — Verify + commit A0 evidence

```bash
openclaw-dashboard/scripts/verify-all-dependencies.sh
openclaw-dashboard/scripts/verify-gateway-health.sh
openclaw-dashboard/scripts/verify-gateway-bind.sh
openclaw-dashboard/scripts/verify-secrets-compliance.sh
```

Record in `.ai/runs/<task-id>/04_verify/output/verification.md`.

Commit A0 enhancements on bootstrap branch with Task-ID trailers. Post `[SAI][VERIFY]`.

---

## Scaffold scripts (in repo — enhance, do not delete)

| Script | Purpose |
|---|---|
| `scripts/verify-all-dependencies.sh` | Node, npm, git, gh, python3, jq, openclaw CLI |
| `scripts/verify-gateway-health.sh` | Gateway doctor or loopback HTTP probe |
| `scripts/verify-gateway-bind.sh` | Fail if bind policy allows 0.0.0.0 |
| `scripts/verify-ingest-latency.sh` | **Stub until activity-ingest** — exit 2 expected pre-A3 |

---

## What A0 does NOT require

- Contract `status: active` commit (paste after merge = bootstrap authorized)
- Real Telegram registry links (fulfillment — fail-closed gate expected)
- Production smoke PASS (stubs exit 2 until later deliverables)
- Dashboard application code (prototype spec only)

---

## Hostinger notes (from Alfred A0 bootstrap run)

### Container environment
- Hostinger VPS uses **containerd**, not Docker CE directly
- Docker socket is NOT available inside the container
- Containers run under the `node` user (UID 1000)
- `sudo` is available for container-level privileged operations
- `/data` is mounted from the host (`/dev/sda1`) — persisted across restarts

### OpenClaw specifics
- Gateway config: `~/.openclaw/openclaw.json`
- Plugin install is persistent: `openclaw plugins install @openclaw/<name>` writes to `/data/.openclaw/npm/`
- Config changes via `openclaw config patch` hot-reload; some changes require SIGUSR1
- Log output: `/tmp/openclaw-<uid>/openclaw-<date>.log`
- Gateway bind is loopback-only at `127.0.0.1:18789` — verify with `verify-gateway-bind.sh`
- Slack Socket Mode plugin: `@openclaw/slack`

### Secrets
- `/etc/openclaw/sai.env` must be created with `sudo mkdir -p`; does not exist by default
- Mode `0600`, owner `root:root` per security doctrine
- `OPENCLAW_GATEWAY_TOKEN` is auto-generated in the Gateway config — extract with `jq '.gateway.auth.token'`
- `SLACK_BOT_TOKEN` may be provided via Telegram; `SLACK_APP_TOKEN`, `TELEGRAM_BOT_TOKEN`, `COMPOSIO_API_KEY` are deferred

### Tailscale
- Inside container: install via Homebrew (`brew install tailscale`)
- No `/dev/net/tun` device — must use `--tun=userspace-networking` mode
- Socket must be in a writable path: `--socket=/tmp/tailscaled.sock`
- SSH key generation: `ssh-keygen -t ed25519` for container-to-host access
- `sudo env "PATH=$PATH"` needed when running system-wide commands

### Git & GitHub
- Remote uses HTTPS — push via `gh auth token` when interactive auth unavailable:
  ```bash
  git remote set-url origin https://x-access-token:$(gh auth token)@github.com/Dezocode/Sai.git
  git push ...
  git remote set-url origin https://github.com/Dezocode/Sai.git
  ```
- `gh` CLI is authenticated as `Dezocode` with `repo` scope

## Links

- Binding paste prompt: `.ai/contracts/20260722-openclaw-dashboard-dezocode/first-prompt-attach-contract.md`
- Full first message: `.ai/contracts/20260722-openclaw-dashboard-dezocode/first-message-to-openclaw.md`
- Gateway policy: `.ai/agents/alfred/runtimes/openclaw/gateway/config/gateway-exposure-policy.md`
