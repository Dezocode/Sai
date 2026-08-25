# Handoff — stale-channel cleanup + owner door docs
Task-ID: 20260825-0945-pr148-stale-cleanup-grunt
PR: Dezocode/Sai#148
Author: grunt (ox-alpha)
## What
channels/stale-cleanup.sh: marks channels dead beyond STALE_AFTER (default 3600s) as stale in channels.json; dry-run default, --commit journaled via stale_cleanup_at; never deletes ledgers (state survives, G2). tui/README: owner attach (read-only default) and steer/prompt doors documented, dead-session delivery parks for replay.
## Why
#148 acceptance: stale channel cleanup + owner attach read-only by default + explicit steer door. Bounded: single pass per invocation, no polling.
## Verify
Fixture test: 2 of 3 channels marked stale (dead-old + never-active), live channel untouched. bash -n clean.
