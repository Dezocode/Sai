# Verify — feature maps Pages

Local (this VM, exact HEAD maps):

- `scripts/render-sai-feature-maps --check` → `OK render-sai-feature-maps --check features=10`
- Isolated PATH without `gh` (only `git` + `python3`) → same `--check` OK (P2 missing-gh)
- Generated HTML has `<h2>Sub-features</h2>`, `<h2>How to get to it</h2>`, `<h2>Driving it</h2>`, `<h2>Gotchas</h2>` ten times each
- Protected CI card includes `ci-feature-maps-pages` rest text, ents, `::exists` proofs, Hostinger gotcha
- Token split still in workflow (UNIT-0017): trusted fetch then `unset GITHUB_TOKEN GH_TOKEN`
- `go run ./cmd/sai-verify drive` pass=56 fail=0, completeness=proven (bound to dirty renderer, then commit)
- Insertions vs origin/main: 834 (budget 1200)

Skipped: live GitHub Pages deploy (needs Settings Pages=GitHub Actions). Hostinger not touched. Do not claim Saul success until the four-H2 head re-runs.
