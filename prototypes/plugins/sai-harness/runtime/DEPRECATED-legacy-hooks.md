# Legacy .sai/hooks/ deprecation path

The validated scripts in this canonical tree supersede the per-checkout
`.sai/hooks/` copies (grokbot.sh, sai-channel.sh, audit-gateway.sh,
aspectizer.sh, lane-connector.sh, sai-harness-tui).

## Cutover stages
1. **Now (#148):** canonical tree is source of truth for NEW deployments.
   Legacy locations keep working; each legacy script gains a deprecation
   banner pointing here (added in this commit where a legacy copy is
   deployed on this host).
2. **#149+:** transports consume only canonical paths; legacy scripts are
   shims that exec the canonical file.
3. **Removal:** legacy copies deleted once zero callers remain (verified by
   grep gate in T7 deletion-safety test). Production is never affected:
   production has zero dependency on either location.

## Rule
No behavior changes during migration — canonical files are verbatim moves
plus declared additions (ci-probe.sh, identity/, state/). Any fix lands in
the canonical tree first; legacy shims inherit.
