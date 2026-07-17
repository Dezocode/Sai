# Claude Code operating profile — Splunky (ctr-code-splunky)

## Runtime truth

Splunky's **primary runtime is Claude Code** (`claude-code-cli`). Work happens in
session-driven Claude Desktop / Claude Code sessions rooted at
`splunk-clone/` (`CLAUDE.md`) with the ICM mirror at
`.ai/agents/splunky/`.

No Cursor Automations profile, unattended cloud cron, Slack wake trigger, or
GitHub event trigger has been verified for Splunky. Do **not** prescribe or
claim live Cursor UI automation for this agent.

## Invocation

1. Open **monaecode/Sai** in Claude Code or Claude Desktop.
2. `cd splunk-clone` (recommended product cwd).
3. Read `CLAUDE.md`, then `.ai/agents/splunky/AGENT.md`, contract
   `20260715-splunk-clone-monaecode`, and the active stage under `.ai/stages/`.
4. Use `SAI_AGENT_ID=ctr-code-splunky` for SAI scripts in the repo root.
5. Optional subagent: `splunk-clone/.claude/agents/splunky.md`.

## Session startup contract

1. Verify repository, branch (`proj/splunk-clone/ctr-code-splunky/*` on
   monaecode/Sai), remote, worktree isolation, and active file claims in
   other runs' `metadata.json`.
2. Read `.ai/CONTEXT.md`, Splunky's profile, applicable stage contract, and
   contract `20260715-splunk-clone-monaecode`.
3. Read recent `#splunk-clone-project` and `#agentupdates` activity relevant
   to the task.
4. Post INTAKE and PLAN before edits; preserve all human review gates in
   `.ai/_config/security-policy.md`.
5. Run `scripts/verify-agent-audit`, `scripts/verify-semantic-hierarchy`,
   and contract-specific checks before publication.
6. Post VERIFY/HANDOFF (or BLOCKED) with exact evidence; use
   `#splunk-clone-project` for contract PLAN/VERIFY and `#agentupdates`
   for cross-agent coordination.

## Protocol upkeep (session-driven)

When monaecode opens a upkeep session (manual or future Claude scheduled
task), run the SAI protocol block from `.ai/_config/reporting.yaml`:

1. `git fetch origin main` — confirm clean checkout of monaecode/Sai.
2. `scripts/agent-report flush` — report delivered vs queued events.
3. `scripts/verify-agent-audit origin/main..HEAD` and
   `scripts/verify-semantic-hierarchy`.
4. `scripts/agent-sync-drive` — report pending/synced/failed honestly.
5. Role work only within Splunk clone prototype scope; otherwise stop and
   report scope refusal.
6. Post `[SAI][VERIFY]` or `[SAI][BLOCKED]` to `#agentupdates`
   (`C0BH15HDN2Z`), tagging monaecode (`U0BGNS7F0T1`).

## Future automation offer

When Claude Code exposes a verified recurring mechanism for this principal,
record the exact task id, schedule, first successful run, and caveats in
`hooks.json` and here before changing the registry from `delegated:` to a
live automation claim. Until then, registry stays delegated to this file.

## Verified capabilities

Authoritative evidence: `.ai/agents/splunky/runtimes/claude/tools.json`.
Phase 5B (`scripts/agent-verify-caps --environment claude-code-cli`) is
**pending** — no capabilities are marked `verified` yet; do not list tools
in automation claims until surveyed.

## Optional Cursor runtime

If monaecode later runs Splunky in Cursor Desktop (`@splunky`), use a
**separate** optional suite under `runtimes/cursor/` and generate a Cursor
Automations spec only after a Cursor-specific capability survey. That spec
must not replace this Claude-primary profile.
