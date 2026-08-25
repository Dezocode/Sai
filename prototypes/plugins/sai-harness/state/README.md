# state
Canonical per-host state dir outside any checkout. `migrate.sh` moves legacy
per-checkout .sai/state here: dry-run default, journaled commit, rollback.
Fresh clones can no longer wipe live state (G2 root cause closed).
