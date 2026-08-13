# Intake — Runtime Intelligence subprocess initialization

## Source prompt (immutable)
Initialize Runtime Intelligence subprocess system per Decision 0006, Decision 0007, and
`.ai/shared/skills/runtime-intelligence/TELEGRAM_BOOTSTRAP_PROMPT.md` on parent PR #62
branch `cursor/codebase-health-90ba`. Do not self-declare initialized. Use stacked sub-PR.
Obtain Saul exact-state technical approval, Sai exact-state governance approval, and human
approval. Never merge to main.

## Parent state (exact)
| Field | Value |
|-------|-------|
| Parent PR | https://github.com/Dezocode/Sai/pull/62 |
| Parent branch | `cursor/codebase-health-90ba` |
| Parent head (init base) | `d113fa0bf75b43491c25723f57cf9dec1e6196de` |
| Base for sub-PR | parent branch (NOT main) |
| Parent CI (as of 2026-08-13T19:33Z) | icm-enforcement FAILURE; invoke-saul FAILURE |

## Authority constraints (0006 + 0007)
- Hermes/Grok/OpenClaw are **subprocess runners**, not officers.
- No merge to `main`, no force-push, no mark-ready on protected PRs.
- No top-level PR to main unless co-founder explicitly requests.
- Code changes: stacked/sub-PR against active parent implementation branch.
- Status remains **PROVISIONAL** until Saul + Sai + human approve the exact SHA.
- Do not invent Cora/Saul authority; use Decision 0006 machinery.

## Phase A inventory (Hostinger `srv1840454`, 2026-08-13)

### Host
- OS: Ubuntu 24.04.4 LTS, kernel 6.8.0-137-generic, x86_64
- Disk: ~96G root, ~32G free (68% used)
- User: root

### Container runtime
- Docker 29.6.1
- Containers observed:
  - `hostinger-saul-codex` (Saul Codex runner) — Up
  - `openclaw-fqy8-openclaw-1` (ghcr.io/hostinger/hvps-openclaw:latest) — Up, port 40667
  - `claude-cli` — Up
  - `atomic-harness-wiki` nginx — 127.0.0.1:18080
  - `traefik-traefik-1` — Up
  - **No dedicated Grok Docker container** (Phase C gap)

### Hermes
- `hermes-gateway.service` active (running) since 2026-08-10
- Binary: `/usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main gateway run`
- State: `/root/.hermes/`
- Journal: Telegram `TimedOut` reconnect warnings (degraded connectivity episodes)

### Grok Telegram bridge
- Root: `/root/grok-telegram-bridge/`
- Services active: `grok-telegram-poll`, `grok-telegram-worker`, `grok-telegram-control-relay`
- CLI: `grok 1.0.3` at `/root/.grok/bin/grok`, logged in
- Models discovered: `grok-4.6` (default), `grok-4.5` available
- Bridge defaults in code: `GROK_DEFAULT_MODEL` fallback `grok-4.5`, `GROK_DEFAULT_EFFORT` fallback `high`
- `/deep` path exists in architecture as high-reasoning deep fulfillment (min turns often 12)
- Execution: **host systemd + host grok CLI**, not yet Dockerized per Decision 0007 Phase C

### OpenClaw
- Container `openclaw-fqy8-openclaw-1` running
- Data: `/docker/openclaw-fqy8/data`
- Watchdog: `openclaw-watchdog.service` active
- Role target: bounded background assistant (Decision 0007) — **policy wiring still PROVISIONAL**

### Auth / tools (no secret values)
- `gh` authenticated as **Dezocode**, scopes include repo + workflow
- `codex-cli 0.147.0` at `/root/.local/bin/codex`
- Python 3.12.3, Node v22.23.2
- `jq` **not** installed on PATH (minor tooling gap)

### Governed repo worktrees
| Path | Branch / HEAD |
|------|----------------|
| `/root/Sai` | `main` @ d079351 |
| `/root/sai-ri-subprocess-init` | `cursor/ri-subprocess-init-20260813` @ parent head d113fa0 |
| `/root/sai-alfred-bootstrap` | alfred bootstrap (other agent — do not edit) |
| `/root/sai-grok-research-digest` | research digest worktree |
| `/tmp/sai-pr62` | detached older PR62 SHA |

### Local RI memory
- Created: `/opt/sai/runtime-intelligence/` per MEMORY_ARCHITECTURE.md
- SQLite: `/opt/sai/runtime-intelligence/state/runtime-intel.db`
- `init_gate.status = PROVISIONAL`; Saul/Sai/human = PENDING

### Skill materials on parent head
Present under `.ai/shared/skills/runtime-intelligence/`:
SKILL.md, TRIAGE.yaml, MEMORY_ARCHITECTURE.md, OPERATING_MANUAL.md, TELEGRAM_BOOTSTRAP_PROMPT.md
Decisions: `0006-agent-authorization-loop.md`, `0007-parallel-runtime-intelligence-plane.md`

## Gaps recorded at intake (not resolved by declaration)
1. Grok not Dockerized (Phase C).
2. Model decision text says grok-4.5; CLI default is grok-4.6 — must verify production target for RI findings.
3. OpenClaw not yet bound to TRIAGE.yaml automation.
4. Control Tower dashboard for RI not yet built (skill-lab-dash on :8765 is separate).
5. Subprocess identities not in `.ai/agents/registry.json` (must not self-register ACTIVE).
6. Decision 0006 write-authorization: bootstrap task_ids are Cursor-only; RI needs Cora contract or governance path for durable commits.
7. Parent PR #62 CI currently failing — stacked work must not claim parent ready.
8. Saul/Sai/human approvals of **this** init SHA: none yet.

## Organizational status
**PROVISIONAL / NOT INITIALIZED.** No self-declaration of ACTIVE.
