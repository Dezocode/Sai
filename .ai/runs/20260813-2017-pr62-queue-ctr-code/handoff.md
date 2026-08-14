# Handoff — contractor (blocker ledger + trust pin + resume stale-Saul fix)

Contract v3, lease `lease-c3a003pr62q1`.

- Durable blockers ledger; Cursor/contractor self-PASS mechanically rejected.
- `sai-resume` no longer returns a Saul snapshot for the wrong HEAD.
- Empty-dest first-writer freeze in `saul-review.yml` (workflow_dispatch of
  the provisioner 404s until that workflow exists on `main`). Existing
  MANIFEST is never overwritten. HOME fallback for trust dest.
- `sai-wait` 900s non-model wait with early wake.

Do not merge. Technical PASS awaits qualifying Saul.
