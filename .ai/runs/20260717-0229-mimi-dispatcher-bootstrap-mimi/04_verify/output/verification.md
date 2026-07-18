# Verification — 2026-07-17 (UTC), claude-code-cli session

All command output captured live this session; nothing below is inferred.

| Check | Command | Result |
|---|---|---|
| Mechanical init | `SAI_AGENT_ID=mimi scripts/agent-init` | **AGENT-INIT: PASS** |
| Semantic hierarchy | `scripts/verify-semantic-hierarchy` | **OK** |
| Audit trail | `scripts/verify-agent-audit main..HEAD` | **OK (main..HEAD)** |
| Caps survey | `SAI_AGENT_ID=mimi scripts/agent-verify-caps --tools-file .ai/agents/mimi/runtimes/claude/tools.json --environment claude-code-cli` | Ran; **script emitted Cursor-template MCP entries with unearned evidence** ("Cursor Slack MCP available" in a Claude Code session) — corrected by hand to session-true entries, see `subagent-invocation.md` note and commit "Refresh Claude runtime capability survey". Known script gap for `claude-code-cli`; flagged for follow-up. |
| gh (as monaecode) | `gh auth status`; `gh repo view Dezocode/Sai` | Verified: scopes gist/read:org/repo/workflow; canonical default=main |
| Slack read | `slack_read_channel` C0BH15HDN2Z (live connector) | Verified: retrieved Saul CTO summary of 2026-07-16 20:38 CDT |
| Slack send | — | **Not exercised**; requires monaecode per-action approval; entry stays `unverified` |
| Force-push guard hook | piped sample PreToolUse payloads through `.claude/settings.json` hook command | blocks `--force`/`-f` (exit 2), allows normal push (exit 0) |
| Subagent frontmatter | python parse of `.claude/agents/mimi-dispatcher.md` | OK — name/description/memory/tools valid |
| Stub workflow YAML | ruby YAML.load_file | OK |

## Remediation round (Sai VERIFY FAIL + Saul REQUEST_CHANGES, 2026-07-17)

| Fix | Evidence |
|---|---|
| 05_review stage gap | `05_review/output/review-record.md` added; `verify-semantic-hierarchy` re-run OK (was FAIL: "has 06_publish_sync output but missing 05_review") |
| Workflow shell injection | Inputs via `env:` only; anchored-regex validation; 18-case malicious-input regression ALL PASS → `workflow-injection-tests.md` |
| `Bash(git branch:*)` wildcard | Allow narrowed to `--list` / `--show-current` / `-vv` exact forms; explicit `deny` added for `git branch -D/-d/-m/-M`, `git push --force/-f`, `git reset --hard`, `git clean -f`. Matcher evidence: prefix-matcher cannot reach `git branch -D` from any remaining allow rule (no allow rule prefixes it), deny rules take precedence per Claude Code permission semantics, and the PreToolUse force-push guard (tested live earlier this run) adds a hook-layer backstop. In-runtime deny regression requires a fresh session — listed with subagent repro steps. |
| Cursor-owned state in Claude adapter | `runtimes/claude/automation/profile.md` rewritten Claude-native (hand-authored; regenerate with `--suite claude` post-#19); Cursor walkthrough moved to `runtimes/cursor/automation/profile.md`; legacy `automation/profile.md` reduced to a pointer |

## Fork sync (pre-work)

`origin/main` fast-forwarded d091438 → 3c5c799 = `upstream/main`, pushed
with `SAI_AUDIT_BYPASS` (reason recorded in queued BYPASS event: the 29
merge-handoff FAILs are in upstream-merged 20260715 history, not new work).

## PR overlap survey

- **PR #21** (Dezocode, `cursor/mimi-dispatcher-bootstrap-f1d6`): carries the
  same contract folder — byte-identical to this branch's copy (verified via
  `git diff`, only delta is our added `amendments/` file). Its
  `claude-desktop-project-instructions.md` differs from ours (theirs is a
  short pointer; ours is the full standing profile) — merge-order conflict to
  resolve at review, not unilaterally.
- **PR #19** (Saul's "go first" recommendation, per #agentupdates): overlaps
  on `.ai/agents/mimi/runtimes/claude/automation/profile.md` (we regenerated
  it). If #19 merges first we rebase and regenerate with the fixed script.
