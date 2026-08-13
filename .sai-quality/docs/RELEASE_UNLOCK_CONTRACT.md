# Feature Unlock Contract

`python3 scripts/qualityctl.py unlock` is the only supported Phase-0 unlock path.

The command must verify:

- all `required_for_unlock` gates are PASS;
- feature-lock invariant currently passes;
- architecture registry is valid;
- toolchain lock contains no unresolved enabled tool;
- cumulative DEEP checks pass;
- fault-injection suite proves negative cases are caught;
- no unresolved critical/high security finding exists under the configured policy;
- no baseline was refreshed after the final baseline gate without a policy event;
- evidence exists for the current working-tree/commit state.

If successful, it removes `.sai-quality/FEATURES_LOCKED` and writes `.sai-quality/FEATURES_UNLOCKED.json` with timestamp, git SHA, gate evidence references, and policy digest.

Deleting `FEATURES_LOCKED` manually is a policy violation; CI treats absence of both a valid lock marker and a valid unlock certificate as failure.
