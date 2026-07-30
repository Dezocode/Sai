# Google Drive memory bank — setup guide

**Audience:** dezocode and monaecode (operators)  
**Canonical source:** GitHub `Dezocode/Sai` (`.ai/` tree)  
**Drive role:** Read-only mirror + shared recovery layer — never authoritative

This guide sets up a **hierarchical memory bank on Google Drive** that mirrors
the ICM scaffolding in `.ai/`: shared memory, contracts, projects, and
**one memory folder per registered agent**.

---

## Architecture

```
Git (canonical)                         Google Drive (mirror)
─────────────────                       ───────────────────────
.ai/shared/memory/          ────────►   SAI/repositories/dezocode-sai/memory/
.ai/contracts/              ────────►   SAI/contracts/
.ai/projects/               ────────►   SAI/projects/
.ai/agents/sai/memory/      ────────►   SAI/agents/ceo/memory/
.ai/agents/mimi/memory/     ────────►   SAI/agents/mimi/memory/
.ai/agents/cora/memory/     ────────►   SAI/agents/ctr-admin/memory/
.ai/agents/alfred/memory/   ────────►   SAI/agents/ctr-code-alfred1/memory/
... (every registry agent)  ────────►   SAI/agents/<agent-id>/memory/
```

Per-agent memory layout (Git and Drive):

```
memory/
  manifest.json              # agent_id, drive_mirror_path, contracts[]
  contracts/<contract-id>.json
  audit/index.json
  audit/YYYY/summary.jsonl
  capabilities-history.jsonl
```

**Tooling:** `scripts/agent-sync-drive` uploads after a verified GitHub push.
**Validation:** `scripts/agent-drive-scaffold` confirms every registry agent has
`memory/` before first sync.

Policy: `.ai/_config/sync-policy.md`  
Decision: `.ai/shared/memory/decisions/0003-contractor-charters-and-agent-memory.md`

---

## Two connection paths (use both)

| Path | Best for | Auth device | Batch mirror | Live Drive ops |
|---|---|---|---|---|
| **A — rclone + Google OAuth** | `agent-sync-drive` after every push | Mac (one-time) | ✅ | ❌ |
| **B — Composio Google Drive** | Mimi `#knowledgebase`, Alfred dashboard A2 | **iPhone or Mac** (Connect Link) | ❌ | ✅ |

Git remains canonical. Composio does **not** replace `agent-sync-drive`; it
enables live read/write from agents (Mimi, Alfred) between sync cycles.

---

## Path A — rclone (batch memory mirror)

Use on your **Mac** where you push to `Dezocode/Sai`.

### 1. Install rclone

```bash
brew install rclone
```

### 2. Configure Google Drive remote

```bash
rclone config
# n) New remote
# name: gdrive
# Storage: drive (Google Drive)
# scope: drive (full access) or drive.readonly if you only mirror out
# auto config: y   ← opens browser OAuth on Mac
```

### 3. Set environment variable

Add to your shell profile (`~/.zshrc`):

```bash
export SAI_DRIVE_REMOTE="gdrive:SAI"
```

Create an empty **`SAI`** folder in My Drive if it does not exist (rclone creates subpaths on first sync).

### 4. Validate scaffolds

```bash
cd /path/to/Sai
scripts/agent-drive-scaffold
```

### 5. First sync (after push)

```bash
git push origin main   # HEAD must exist on remote
scripts/agent-sync-drive --repo-key dezocode-sai
```

Expect `[SAI][SYNC]` with status `synced` and a SHA-256 checksum. Without
`SAI_DRIVE_REMOTE`, status is `pending` (Git work is never blocked).

### monaecode fork

```bash
scripts/agent-sync-drive --repo-key monaecode-sai --remote gdrive:SAI
```

---

## Path B — Composio (iPhone-friendly live connection)

Use when you want to **connect Google Drive from your iPhone** or enable Mimi /
Alfred live Drive tooling without rclone.

Composio MCP is **not** available in Cursor Cloud VMs. Complete auth on
**Cursor Desktop** or via the Composio dashboard.

### Option B1 — Cursor Desktop + Composio MCP (recommended)

1. Open **Cursor Desktop** on Mac (same account as this repo).
2. Ensure **Composio** MCP server is enabled (Settings → MCP).
3. In chat, ask: *"Connect Google Drive via Composio"*.
4. Composio returns a **Connect Link** — open it on your **iPhone** Safari if
   you prefer mobile OAuth; Google sign-in works the same.
5. Wait until connection status is **ACTIVE** (Composio polls automatically).

Verified toolkits for Mimi (see `.ai/agents/mimi/runtimes/claude/tools.json`):

- `composio-googledrive-toolkit`
- `COMPOSIO_MANAGE_CONNECTIONS` / `COMPOSIO_WAIT_FOR_CONNECTIONS`

After active: Mimi can maintain `#knowledgebase` index integrity per
`.ai/agents/mimi/skills.md`.

### Option B2 — Composio dashboard

1. Go to [https://platform.composio.dev](https://platform.composio.dev)
2. **Connections → Add connection → Google Drive**
3. Complete OAuth (works on iPhone browser)
4. Copy connection id for VPS / Alfred A2 (`COMPOSIO_API_KEY` on Hostinger)

### Alfred VPS (contract A2 — later)

On Hostinger after `COMPOSIO_API_KEY` is in `/etc/openclaw/sai.env`:

- Dashboard **Settings → Auth → Composio Google Drive** tile
- See `openclaw-dashboard/settings/auth/providers.md`

---

## Recommended operator sequence (dezocode)

1. **Now (iPhone):** Composio Connect Link for Google Drive (Path B1 or B2) —
   unblocks Mimi and Alfred live ops.
2. **Mac session:** rclone + `SAI_DRIVE_REMOTE` (Path A) — enables automatic
   batch mirror of **all agent memory trees** after each push.
3. Run `scripts/agent-drive-scaffold` — confirm every agent shows `[OK]`.
4. Push this repo, then `scripts/agent-sync-drive` — first `synced` SYNC event.

---

## Verification checklist

| Check | Command / evidence |
|---|---|
| All agents have memory/ | `scripts/agent-drive-scaffold` exit 0 |
| rclone remote works | `rclone lsd gdrive:SAI` |
| Sync after push | `scripts/agent-sync-drive` → `synced` + checksum |
| Composio Drive active | Composio dashboard or `COMPOSIO_MANAGE_CONNECTIONS list` |
| Drive layout | `SAI/agents/<agent-id>/memory/manifest.json` exists per agent |
| Slack | `[SAI][SYNC]` posted with drive_status |

---

## Rules (non-negotiable)

1. **Never** edit canonical memory only on Drive — changes must return via Git PR.
2. **Never** store secrets, tokens, or `.git` on Drive.
3. Drive sync runs **only after** GitHub verifies the pushed commit SHA.
4. Reconcile Drive-originated edits through a branch + PR (sync-policy rule 8).

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| SYNC always `pending` | Set `SAI_DRIVE_REMOTE`; install rclone |
| `HEAD not on remote` | Push branch before sync |
| Composio toolkit unverified | Complete Connect Link OAuth; wait ACTIVE |
| Agent missing from Drive | Run `agent-memory-scaffold`; re-run sync |
| Cloud agent cannot auth | Expected — use Mac/iPhone for OAuth steps above |
