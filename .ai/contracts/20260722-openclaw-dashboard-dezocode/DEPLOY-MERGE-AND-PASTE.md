# Deploy — merge + paste (two steps)

**For dezocode:** this is the only deployment procedure after PR #45 review.

| Step | Action | Who |
|---|---|---|
| **1** | Merge [PR #45](https://github.com/Dezocode/Sai/pull/45) to `Dezocode/Sai:main` | dezocode + monaecode |
| **2** | Paste [first-prompt-attach-contract.md](./first-prompt-attach-contract.md) into fresh OpenClaw on VPS | dezocode |

**One-time VPS prep (~10 min, before step 2):** [vps-bootstrap.md](../../../openclaw-dashboard/docs/vps-bootstrap.md) § dezocode

- Ubuntu 22.04+ Hostinger VPS
- Node 24.15+ · `npm install -g openclaw@latest` · `openclaw onboard`
- `git clone https://github.com/Dezocode/Sai.git && cd Sai && git pull origin main`

No separate contract activation commit is required before paste. Alfred records bootstrap
in `.ai/runs/` and requests formal `contract.json` → `"status": "active"` after A0 PASS.

## What Alfred does on paste (A0)

Follow [vps-bootstrap.md](../../../openclaw-dashboard/docs/vps-bootstrap.md) Alfred steps:

1. Worktree `proj/openclaw-dashboard/ctr-code-alfred1/bootstrap`
2. `verify-all-dependencies.sh` PASS
3. Gateway on `127.0.0.1:18789` · `verify-gateway-health.sh` PASS
4. systemd unit from `host/systemd/openclaw-gateway.service`
5. Secrets MCQ if `/etc/openclaw/sai.env` empty — BLOCKED OK, continue A1 scaffolding
6. Telegram INTAKE to dezocode · Slack mirror · run artifacts

## Not required before paste

- Contract `status: active` (formalized after A0 evidence)
- Telegram registry links · production smoke · ingest p99
- Alfred `registry status: active` (Part C)

## Binding documents

Listed in `contract.json` → `binding_documents[]` and [contract.md](./contract.md).

## After A0

Alfred continues first-message sections A1–A13 on bootstrap branch. Organization onboarding
(Part C) blocks product merge to `main` — not your paste step.

---

*Authority: dezocode — merge + paste deploy model. DR-20260724 applies.*
