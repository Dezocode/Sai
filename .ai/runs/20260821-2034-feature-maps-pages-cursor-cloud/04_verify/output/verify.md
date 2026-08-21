# Verify — feature maps Pages

Local (this VM, exact HEAD maps):

- `scripts/render-sai-feature-maps --check` → `OK render-sai-feature-maps --check features=10`
- Token split: two fetch steps with `GH_TOKEN`; two render steps with `unset GITHUB_TOKEN GH_TOKEN` and no `gh api`
- `go run ./cmd/sai-verify drive` rebound after workflow + map edits: pass=56 fail=0, completeness=proven
- `scripts/verify-semantic-hierarchy` → OK
- Insertions vs origin/main: 793 (budget 1200)

Skipped: live GitHub Pages deploy (needs Settings Pages=GitHub Actions). Hostinger not touched. Saul re-run pending on the token-split head.
