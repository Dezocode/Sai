# Review record — stage 05

Reviews received on this run's PR ([Dezocode/Sai#27](https://github.com/Dezocode/Sai/pull/27)) and their disposition. This stage was
initially skipped — publishing happened straight after 04_verify, which
`verify-semantic-hierarchy` and canonical `icm-enforcement` both correctly
rejected. Recorded lesson: **05_review is mandatory whenever
06_publish_sync/output exists.**

## 1. Cora — CONTRACT_REVIEW `20260717-0323-mimi-contract-review-ctr-admin`
(Slack ts 1784258795, 2026-07-16 22:26 CDT)

| Finding | Disposition |
|---|---|
| P1 plain-text `@sai` tag notified no one | Fixed `45cd98b`: real `<@USER_ID>` routing table in skill + instructions; corrected thread reply posted with working mentions |
| P1 automation profile Cursor-framed | Interim annotation `45cd98b`; full fix this round (see Saul P1 below) |
| P2 skills.md stale | Fixed `45cd98b`: dispatcher skills section |

## 2. Sai — `[SAI][VERIFY]` FAIL `20260717-0330-pr27-icm-registry-caps-ceo`
(Slack ts 1784259055, 2026-07-16 22:30 CDT)

| Finding | Disposition |
|---|---|
| P1 run has 06_publish_sync but no 05_review (CI run 29552518131 FAIL) | Fixed this round: this file; verifier re-run OK (evidence in 04_verify/output/verification.md) |
| Registry unchanged / proposal-only | Confirmed correct — no action |
| Caps survey session-evidence discipline | Confirmed acceptable — no action |

## 3. Saul — REQUEST_CHANGES
([review 4719159552](https://github.com/Dezocode/Sai/pull/27#pullrequestreview-4719159552), head `45cd98b`, 2026-07-16 22:32 CDT)

| Inline P1 | Disposition |
|---|---|
| `mimi-dispatch-stub.yml:38` — workflow_dispatch strings pasted into shell (injection / `../` traversal) | Fixed this round: inputs only via `env:`, strict regex validation before any use, malicious-input regressions recorded in 04_verify/output/workflow-injection-tests.md |
| `runtimes/claude/automation/profile.md:5` — Claude adapter still owns Cursor UI state | Fixed this round: profile rewritten Claude-native (hand-authored, provenance noted, pending `--suite claude` generator from PR #19); Cursor walkthrough moved to `runtimes/cursor/automation/profile.md` |
| `.claude/settings.json:8` — `Bash(git branch:*)` may permit deletion/rename | Fixed this round: wildcard replaced with `--list`/`--show-current` forms; explicit deny entries for `-D/-d/-m/-M` and force-push; matcher evidence in 04_verify |
| (verdict) subagent invocation unproved | Open — environment-blocked this session; fresh-session repro steps committed; fulfillment gate stays open |

## Gate status after this round

Merge remains blocked pending: CI green on new head → Sai re-VERIFY →
Saul re-review of final head → monaecode + dezocode authorization.
