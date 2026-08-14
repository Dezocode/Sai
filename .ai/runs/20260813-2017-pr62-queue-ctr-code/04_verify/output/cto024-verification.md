# Verify — CTO-024 SHA-bound (not HEAD-union)

See commands in the VERIFY event. Range replay of `origin/main..HEAD` is
valid only after the pin YAML is committed (loader uses `git show HEAD`).

- CTO-024: SHA-bound pins, HEAD-union removed. Awaiting Saul.
- CTO-025: BLOCKED_EXTERNAL; `cto025_activation_on_main: false`.
- CTO-026: TRIAGED meta; not self-passed.
- CTO-027: assigned ctr-admin; not self-passed.
- `sai-blockers --clear CTO-024 --actor cursor` must REJECT.
- `self_pass: false`. `do_not_merge: true`.
