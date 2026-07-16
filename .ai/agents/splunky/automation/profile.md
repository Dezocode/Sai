# Claude Code operating profile — Splunky (ctr-code-splunky)

Legacy alias path for verifiers. Canonical copy:
`.ai/agents/splunky/runtimes/claude/automation/profile.md`.

## Runtime truth

**Claude Code CLI / Claude Desktop** is Splunky's primary runtime (`claude-code-cli`).
This profile documents **session-driven** operation only. It is **not** a Cursor
Automations UI spec — do not create Cursor automation from this file.

As of 2026-07-16, Phase 5B capability survey for this runtime has **not** completed:
`runtimes/claude/tools.json` lists zero verified capabilities. No Claude scheduled
task, Slack wake trigger, or GitHub event trigger has been verified live, so none
is claimed in `.ai/agents/registry.json` (entry remains `delegated:`).

## Invocation

1. Open **`monaecode/Sai`** in Claude Code (repo root).
2. `cd splunk-clone` (recommended product working directory).
3. Read `splunk-clone/CLAUDE.md`, then `.ai/agents/splunky/AGENT.md`, contract
   `../.ai/contracts/20260715-splunk-clone-monaecode/onboarding-prompt.md`.
4. Subagent definition: `splunk-clone/.claude/agents/splunky.md`.
5. Use `SAI_AGENT_ID=ctr-code-splunky` for SAI scripts and run artifacts.

Slack: `#splunk-clone-project` (contract PLAN/VERIFY) and `#agentupdates`
(`C0BH15HDN2Z`) for ICM events per `.ai/_config/reporting.yaml`.

## Session startup contract

1. Verify repository (`monaecode/Sai`), branch pattern
   `proj/splunk-clone/ctr-code-splunky/<task-slug>`, remote, worktree isolation,
   and active file claims in other runs' `metadata.json`.
2. Read `.ai/CONTEXT.md`, Splunky's charter, applicable stage under `.ai/stages/`,
   and contract `20260715-splunk-clone-monaecode`.
3. For contractor work, execute `.ai/ONBOARDING.md` gates before material edits.
4. Post INTAKE and PLAN (Slack + `.ai/runs/<task-id>/`) before edits; preserve
   human review gates in `.ai/_config/security-policy.md`.
5. Run `scripts/verify-agent-audit`, `scripts/verify-semantic-hierarchy`, and
   contract-specific checks before push; include Task-ID / Agent trailers on
   every agent commit.
6. Post VERIFY/HANDOFF with exact command output; run
   `scripts/agent-contract-pr-review` on every PR.

## Future automation (Claude-native only)

After Phase 5B completes in Claude Code:

```bash
SAI_AGENT_ID=ctr-code-splunky scripts/agent-verify-caps \
  --tools-file .ai/agents/splunky/runtimes/claude/tools.json \
  --environment claude-code-cli
```

If Claude Code exposes a **verified** recurring mechanism (e.g.
`create_scheduled_task` with evidence, as documented for Mimi in
`.ai/agents/mimi/runtimes/claude/tools.json`), record the exact task name,
schedule, caveat, and first successful `[SAI][VERIFY]` run here and in
`hooks.json` **before** changing the registry from `delegated:` to a live claim.

Do **not** point Splunky principals at Cursor → Automations for this runtime.

## Verified capabilities

Authoritative evidence: `.ai/agents/splunky/runtimes/claude/tools.json`.
Only entries with `"status": "verified"` may appear in automation claims.
