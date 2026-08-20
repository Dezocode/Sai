# AGENTS.md

Repo-wide agent guidance. For the full coordination protocol read
`.ai/CONTEXT.md` first, then `.cursor/rules/sai-coordination.mdc` (Cursor) or
`CLAUDE.md` / `CODEX.md` (other runtimes). This file only adds the
environment/runtime notes that are not obvious from those documents.

## Cursor Cloud specific instructions

### What this repo is
There is **no application/product code yet**. Today the repo is the SAI agent
coordination framework (the ICM methodology): Markdown contracts + JSON/YAML
config, enforced by Bash scripts (`scripts/*`), git hooks (`.githooks/*`), and
the `.github/workflows/agent-audit.yml` CI. The "product" you run is that
enforcement/coordination tooling — there is no web server, database, or build.

### Toolchain (already present on the base image; no install step)
`bash`, `git`, `python3` (stdlib only for the checks), `PyYAML` (for YAML
validation), `jq`, and `gh` are all preinstalled. `rclone` is **not** installed
and is optional — `scripts/agent-sync-drive` records Drive sync as "pending"
and exits 0 when it or `SAI_DRIVE_REMOTE` is missing. There are no package
manifests/lockfiles, so the startup update script is effectively a no-op (it
just re-asserts executable bits on `scripts/*` and `.githooks/*`).

### Running the checks (this is the "test/lint/build" for this repo)
Run the same suite CI runs — sources: `.github/workflows/agent-audit.yml` and
`.ai/shared/references/testing.md`. Key commands:
- `scripts/verify-semantic-hierarchy` — validate `.ai/` structure + registry.
- `scripts/verify-agent-audit <range>` — commit-trailer audit (e.g. `-n 20 HEAD`).
- `scripts/verify-merge-handoff origin/main..HEAD` — HANDOFF documentation gate.
- `python3 -m json.tool <file>` / `python3 -c 'import yaml,...'` — JSON/YAML lint.

### Cursor plugins and Custom Modes

This repo enables the **pstack** marketplace plugin at project scope in
`.cursor/settings.json`. After a **new** Cloud Agent or a local window
reload on a commit that includes that file, type `/` and use `/poteto-mode`
or `/setup-pstack`. ICM index: `.ai/plugins/pstack/`. Cursor does not load
plugins from `.ai/`.

The project Custom Mode for Cloud Agents is `/lauren-mode`
(`.cursor/skills/lauren-mode/`). Pin it with Option+Enter (Mac) or
Alt+Enter (Windows), or choose Use as Mode, so the skill stays on for the
session. It wraps pstack and adds the 2026-08-19 harness (`/goal`,
subscriptions, VM-isolated subagents, steering), Browser pane notes, and
`@cursor/sdk` cloud launch notes. Do not copy the pstack tree into
`.cursor/skills/`.

Shared pstack role models live in `.cursor/rules/pstack-models.mdc` so Cloud
Agents get them. `~/.cursor/rules/pstack-models.mdc` from `/setup-pstack`
does not apply here.

### 2026-08-19 Cloud Agent harness

- **Custom Mode.** `/lauren-mode` pinned as above.
- **`/goal`.** Use `CreateGoal` / `UpdateGoal` for an objective that must
  hold until complete. Pair with the mode. Use `/loop` only for recurring
  check-ins.
- **Subagents on their own VMs.** `Task` with `environment: "cloud"` (or
  Desktop `/in-cloud`). One agent per working tree still holds.
- **Subscriptions.** Describe the wait, or `/subscribe`. Cloud agents
  auto-subscribe to PRs they create (GitHub Actions CI follow-ups).
- **Steering.** Follow-ups wait for the next tool call. They do not interrupt
  the current tool.
- **Browser pane.** `@Browser` attaches the IDE Browser. GUI proof on this
  VM uses `computerUse`. Chrome is `/usr/bin/google-chrome`.
- **Environment.** Personal dashboard env
  [6f2ece39-800a-11f1-ba66-0e7d0216e441](https://cursor.com/dashboard/cloud-agents/environments/e/6f2ece39-800a-11f1-ba66-0e7d0216e441).
  Do not commit `.cursor/environment.json` unless a co-founder wants to
  replace that personal config.

Details: `.cursor/skills/lauren-mode/references/`.

### Non-obvious gotchas
- **Commit trailers are enforced.** The cloud git identity
  (`cursoragent@cursor.com`) matches the "agent commit" detector, so **every**
  commit you make MUST include `Task-ID: YYYYMMDD-HHMM-<purpose>-<agent-id>`
  and `Agent: <name>` trailers, or `verify-agent-audit` fails in CI.
- **Merge-handoff gate.** Each agent commit's `Task-ID` must have a matching
  `.ai/runs/<task-id>/` containing `handoff.md` (>20 bytes) **or** a `HANDOFF`
  event in `events.jsonl`, or `verify-merge-handoff` fails. Create the run
  directory (with `metadata.json`) alongside the change it documents.
- **Do not casually run `scripts/agent-init` or `scripts/install-agent-hooks`.**
  They set `core.hooksPath=.githooks`, which makes commit/push auto-invoke
  `scripts/agent-report` (event queuing). The scripts themselves warn against
  this in a managed VM; leave hooks uninstalled unless intentionally testing them.
- **Slack reporting degrades gracefully.** Without `SAI_SLACK_BOT_TOKEN`,
  `scripts/agent-report` queues schema-valid events under
  `.git/agent-events/queue/` and still exits 0 — nothing is sent.
