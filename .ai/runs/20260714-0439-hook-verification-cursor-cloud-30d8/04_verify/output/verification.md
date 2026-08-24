# Verification — 20260714-0439-hook-verification-cursor-cloud-30d8

Requested by dezocode: "ensure all hooks and rules in .ai actually achieve
their intended goal."

Method: fresh clone of the framework branch in a scratch directory
(`--no-hardlinks`), a local bare repository as a stand-in remote
(`testremote`), hooks installed via `scripts/install-agent-hooks`, and a
local mock Slack API server (returns `{"ok": true}` or a simulated failure)
reached through the `SAI_SLACK_API_URL` override added for testability.
`SAI_AGENT_ID=hook-lab`; no real tokens used.

## Test matrix and results

| # | Intended goal under test | Method | Result |
|---|---|---|---|
| T1 | post-checkout reports `git checkout -b` (same SHA) | new branch at same commit | PASS after fix (see below) |
| T1b | post-checkout reports plain branch switches | switch between branches | PASS after fix |
| T1c | post-checkout ignores file checkouts | `git checkout -- <file>` | PASS (no event) |
| T1d | post-checkout ignores true no-ops | `git checkout <current-branch>` | PASS (no event) |
| T2 | post-commit captures SHA, parent, author, paths, Task-ID, Plan ref | commit with trailers | PASS (event fields verified) |
| T3 | post-merge reports merge result | `git merge --no-ff` | PASS (event queued) |
| T4 | post-rewrite reports amends with rewrite-count and risk flag | `git commit --amend` | PASS |
| T5 | pre-push allows compliant push to unprotected ref and announces it | push feature branch | PASS |
| T6 | pre-push blocks protected push lacking audit trailers | push trailer-less agent commit to `main` | PASS (blocked; only the offending commit flagged, compliant commit not flagged) |
| T7 | documented emergency bypass works and is recorded | `SAI_AUDIT_BYPASS=... git push` to `main` | PASS (push allowed, BYPASS event queued) |
| T8 | remote ref deletion flagged as destructive | `git push testremote :ref` | PASS (event carries approval-required risk) |
| T9 | flush delivers queued events, moves to `sent/`, formats per contract | mock Slack, one queued event | PASS (channel, template fields correct) |
| T10 | API-level failure preserves queue, honest exit code | mock returns `ok:false` | PASS (exit 1, event retained) |
| T11 | FIFO ordering across events after recovery | 2 queued events, then flush | PASS (VERIFY delivered before CHANGE) |
| T12 | push wrapper verifies remote SHA after push | `post-push-equivalent.sh` | PASS (`remote SHA verified` with ls-remote evidence) |
| T13 | push-confirm detects local/remote mismatch | reset local HEAD, confirm | PASS (exit 1, BLOCKED event with both SHAs) |
| T14 | recursion guard prevents nested reporting | `SAI_AGENT_REPORT_ACTIVE=1` | PASS (no event, exit 0) |
| T15 | Drive sync refuses unpushed commits (GitHub-first rule) | sync with unpushed HEAD | PASS (exit 1, `failed` recorded) |
| T16 | Drive sync degrades to `pending` without credentials | sync with pushed HEAD, no remote | PASS (exit 0, `pending` recorded) |
| T17 | Rules reference only real paths | scan all backticked repo paths in `.ai/**` and the Cursor rule | PASS after fixing one stale shorthand in a plan table |
| T18 | Secret redaction before delivery | `xoxb-`/`ghp_`/`api_key=` samples | PASS (all `[REDACTED]`) — carried over from bootstrap verification |

## Defects found and fixed

1. **post-checkout missed real transitions** (`.githooks/post-checkout`):
   `git checkout -b` and worktree creation reuse the same SHA, so the old
   `prev == new` guard suppressed the report. Now compares previous branch
   (`@{-1}`) as well, so same-SHA branch switches report while true no-ops
   and file checkouts stay silent.
2. **`agent-report` Slack endpoint was untestable** and the `Git:` line
   rendered empty when no refs existed. Added `SAI_SLACK_API_URL` override
   (defaults to the real API) and fixed the formatting to `Git: n/a`.

## Skipped checks (with reasons)

- Live Slack delivery from `agent-report` (no `SAI_SLACK_BOT_TOKEN` in this
  VM) — the full delivery path was exercised against the mock API instead.
- Live Drive upload (no rclone/`SAI_DRIVE_REMOTE`) — only the refusal and
  pending paths were exercised; the upload/checksum path remains untested
  until credentials exist.
- `.cursor/rules/sai-coordination.mdc` behavioral effect on Cursor Desktop
  agents cannot be tested from this environment; its content was verified
  for accuracy and resolvable references only.
