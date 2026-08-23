# Verification — 20260823-0215-pr-sessions-dashboard-hermes

Exact-head evidence for this run. Convention (established by
`20260822-1930-saul-findings-remediation-hermes` and accepted by Saul):
in-tree statements describe **ancestor commits only**; the reviewed head is
bound to check outcomes by GitHub branch CI and the Saul check-binding after
each push. No statement here claims results for its own commit's SHA.

## Provenance chain

- `b3b9ed4` — scaffold (docs).
- `1ef26ca` — first implementation push; Saul round 1 @ `9ca6221` returned
  two P1 findings about stale provenance in these files. Both are addressed
  by this rewrite.
- `9ca6221` — docs commit; all four target CI checks green at that SHA
  (agent-audit, Anti-regression, PR line budget, Feature maps Pages);
  Saul check `97131784569` bound to it with P0=0 P1=2 P2=0 (both P1s were
  the stale-provenance findings above; regression guards all PASS there).
- `055796c` — product commit: PR graph/summary row above the wheel,
  stale-heartbeat styling (30m threshold), 60s client refresh; `--check`
  extended; protected-ci.md rows updated. Pushed and remote-verified.
- The commit carrying this file is a direct child of `055796c` and changes
  only `.ai/runs/` artifacts. Every capture below was executed on
  `055796c` before staging evidence files.

## Capture A — renderer + live API @ `055796c`

```
$ git rev-parse HEAD
055796cbb0b363606b8390e0f117049ba7f08c83

$ python3 -m py_compile scripts/render-sai-feature-maps && echo COMPILE-OK
COMPILE-OK
[exit=0]

$ scripts/render-sai-feature-maps --check
OK render-sai-feature-maps --check features=11
[exit=0]

$ rm -rf /tmp/sess-site && scripts/render-sai-feature-maps --out /tmp/sess-site
wrote /tmp/sess-site/feature-maps.html
wrote /tmp/sess-site/pr-sessions.html
[exit=0]

$ curl -sS https://srv1840454.hstgr.cloud/api/hermes-sessions/sessions
API rows: 1   (live GET, exit=0)
```

## Capture B — DOM smoke vs live API response @ `055796c`

Node harness executes the inline page script against the real API body.

```
WHEEL len 758 | SUMMARY: PR GRAPH  prs: 1  sessions: 1  active: 1   heartbeats fresh(<30m): 1  stale: 0
wheel_has_card       = true
card_id              = true
card_head            = true
card_profile_field   = true
card_status_field    = true
card_phase_field     = true
card_steer_field     = true
card_monitors_field  = true
heartbeat_age        = true
grouped_by_pr        = true
no_script_injection  = true
summary_graph_label  = true
summary_counts       = true
note_refresh         = true
SMOKE-OK
[exit=0]
```

## Capture C — synthetic variants (stale / failed / done / error / empty)

Fixtures only; no fabricated production data.

```
A stale_row           = true      # heartbeat >30m -> red hb-stale marker row
A stale_card_outline  = true      # whole PR card outlined red when any session stale
A failed_bad_cls      = true      # failed status pill .st.bad
A done_mute_cls       = true      # done status pill .st.mute
A grouped_77_two      = true      # two sessions grouped under one PR #77 card
A summary             = PR GRAPH prs: 2  sessions: 3  active: 1  done: 1  failed: 1  heartbeats fresh(<30m): 2  stale: 1
B unavailable_msg     = true      # fetch failure -> "Sessions unavailable (...)"
B summary_empty       = true      # no invented counts on error
B note                = "unavailable"
C empty_msg           = true      # empty sessions -> "No sessions reported right now."
C summary_empty       = true
[exit=0]
```

## Capture D — repo verifiers + go suite @ `055796c`

```
$ scripts/verify-semantic-hierarchy
verify-semantic-hierarchy: OK
$ scripts/verify-agent-audit -n 20 HEAD
verify-agent-audit: OK (-n 20 HEAD)
$ scripts/verify-merge-handoff origin/main..HEAD
verify-merge-handoff: OK (1 task-id(s) checked)
$ go test ./...
ok github.com/Dezocode/Sai/cmd/sai-design-check 0.088s
ok github.com/Dezocode/Sai/cmd/sai-verify       7.077s
ok github.com/Dezocode/Sai/internal/app
$ go vet ./... && echo GO-VET-OK
GO-VET-OK
```
All exits 0.

## Capture E — sai-verify drive @ `055796c`

`go run ./cmd/sai-verify drive` → JSON payload: head `055796c…`,
base `759d017…`, **pass 62 / fail 1 / skip 0**. The single FAIL row is the
known pre-existing environmental failure: `coordination-reporting` Emit
fixture uses worktree-relative `read=.git/agent-events/queue`, which cannot
resolve under this linked worktree (`gitdir` lives in `/root/Sai/.git/
worktrees/sai-pr77`). Reproduced identically on BASE earlier in this run;
CI runs on a normal clone where the row passes. Fixture queue file removed
after the run (queue verified empty).

## Capture F — push verification

```
$ git push origin hermes/pr-sessions-dashboard
To https://github.com/Dezocode/Sai.git
   9ca6221..055796c  hermes/pr-sessions-dashboard -> hermes/pr-sessions-dashboard
$ git ls-remote origin hermes/pr-sessions-dashboard
055796cbb0b363606b8390e0f117049ba7f08c83 refs/heads/hermes/pr-sessions-dashboard
```
Remote SHA == local HEAD at push time.

## Skipped / environment notes

- `bash -n scripts/render-sai-feature-maps` not applicable (Python script);
  `python3 -m py_compile` used instead.
- Drive sync not attempted (rclone absent); recorded as pending per repo
  convention.
