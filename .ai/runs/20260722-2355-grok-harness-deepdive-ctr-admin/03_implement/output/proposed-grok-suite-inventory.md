# Proposed `runtimes/grok/` inventory (NOT created)

Research blueprint for a future implementation task after decision accept.
Maps operator harness tiers + docs.x.ai surfaces into concrete repo files.

## Layer 0 / org index (once)

| Path | Purpose |
|---|---|
| `GROK.md` | Peer of `CLAUDE.md` / `CODEX.md` — read `.ai/CONTEXT.md`, route to named agent `AGENT.md`, warn Slack bots ≠ registry |
| `.ai/shared/references/agent-runtimes.md` | Add suite row: `runtimes/grok/` ↔ `grok-build-cli` |
| `.ai/CONTEXT.md` runtime table | Add Grok entry |
| `.ai/INITIALIZE.md` Phase 5B/7 | Branch for `grok-build-cli` |
| Decision file | Accepted extension of 0002 (from draft in parent run) |

## Per-agent suite (when primary or surveyed secondary)

```
.ai/agents/<name>/runtimes/grok/
  README.md                 # suite purpose; Tier C non-identity note; never copy caps
  tools.json                # verified capabilities only
  automation/profile.md     # TUI / headless / ACP / /loop — honesty required
  inspect/                  # optional: redacted grok inspect snippets under runs/, not secrets
```

Optional project overlays (security-reviewed before commit):

```
.grok/
  config.toml               # ONLY mcp_servers / plugins / permission per docs
  rules/*.md                # project rules beyond AGENTS.md
  skills/ hooks/ agents/ personas/ plugins/ sandbox.toml
```

Do **not** commit: `~/.grok/auth.json`, session tokens, raw session dumps with
secrets, marketplace credentials.

## Suggested first `tools.json` capability categories

Status must be `verified` only with dated evidence from a machine that has
`grok` installed.

| id (example) | kind | Evidence idea |
|---|---|---|
| `grok-binary` | shell | `grok version` exit 0 |
| `grok-inspect` | shell | `grok inspect --json` (redacted) |
| `grok-auth` | auth | login method in use (OIDC / device / API key env) — no secrets |
| `grok-model-default` | model | default model name from config |
| `grok-builtin-fs` | builtin_tools | Read/Edit/Grep/list (IDs from inspect/docs) |
| `grok-builtin-bash` | builtin_tools | Bash / shell tool |
| `grok-web` | builtin_tools | web_search / web_fetch feature flags as configured |
| `grok-mcp` | mcp | `grok mcp list` / `doctor` |
| `grok-acp` | protocol | `grok agent stdio` handshake smoke (if used) |
| `grok-headless` | automation | `grok -p` sample (read-only) |
| `grok-loop` | automation | `/loop` only if actually configured — else omit |
| `grok-hooks` | hooks | project/user hooks path + trust state |
| `grok-worktree` | worktrees | `grok worktree list` if isolation used |
| `grok-permissions` | policy | record `permission_mode` + sandbox profile |

## Automation profile template (honesty checklist)

Must answer:

1. Which front ends are in use: TUI / headless / ACP?
2. Is `/loop` or any unattended schedule claimed? Evidence?
3. Actual permission mode and sandbox (not aspirational)?
4. MCP servers approved by owner Phase 3?
5. Explicit “none” if only interactive TUI with human approval.

## Scaffold / schema changes (future task, coordinated)

| Component | Change |
|---|---|
| `scripts/agent-scaffold` | `--primary-runtime grok` → `grok-build-cli` + suite skeleton |
| `scripts/agent-contract-scaffold` | `--runtime grok` + templates |
| `scripts/agent-automation-spec` | Grok branch (not Cursor UI) |
| `scripts/agent-verify-caps` | `--environment grok-build-cli` |
| `scripts/verify-semantic-hierarchy` | `VALID_RUNTIMES` += `grok-build-cli` |
| `scripts/verify-agent-setup` | `RUNTIME_SUITE` map |
| `.ai/shared/schemas/contract.schema.json` | enum += `grok-build-cli` |
| `.ai/contracts/_templates/grok-contract-template.{json,md}` | Cora path |

## Contract Administrator gate

Cora must not emit `primary_runtime: grok-build-cli` in `contract.json` until
schema validates and scaffold can create `runtimes/grok/` without hand-hacks.
This research inventory is the pre-contract checklist for that GO.
