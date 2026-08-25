# Handoff — canonical identity registry + state migration tooling
Task-ID: 20260825-0730-canonical-identity-state-grunt
PR: Dezocode/Sai#148 (assist branch, primary integrates)
Author: grunt (ox-alpha)

## What
- identity/: aliases.json (canonical registry, one identity per channel) + resolve.sh (fail-closed handle resolution, no jq)
- state/: migrate.sh (dry-run default, journaled commit, rollback; canonical state outside checkouts)
- tests/smoke-migrate.sh: 3-pass smoke (dry-run no-op, commit copies, rollback restores)

## Why
Closes #148 prep gaps G1 (identity) + G2 (state survival). Fresh clones can no longer
wipe live fleet state; unregistered handles get zero authority. Owner-approved via
"approve all" ruling ~07:20Z on #147 audit thread; design in grunt-148-architecture-draft.md.

## Verify
bash tests/smoke-migrate.sh <path>/state/migrate.sh  # 3x PASS
bash -n identity/resolve.sh state/migrate.sh          # syntax clean
