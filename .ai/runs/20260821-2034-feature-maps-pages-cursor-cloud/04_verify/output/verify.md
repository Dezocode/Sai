# Verify — feature maps Pages

Local (this VM, exact HEAD maps):

- `scripts/render-sai-feature-maps --check` → `OK render-sai-feature-maps --check features=10`
- `scripts/render-sai-feature-maps --out /tmp/feature-maps-site` → Origin tokens `#f8f8f8` `#f3f3f3` `#141414` `#34785c`; SDL chip `#0F1115` `#5B8CFF`; empty `.nojekyll`; `ci-feature-maps-pages` present; Hostinger sentence present
- `go run ./cmd/sai-verify drive` → pass=56 fail=0, `ci-feature-maps-pages` in doctor ids, Pages proofs PASS
- `scripts/verify-semantic-hierarchy` → OK
- Generator + workflow + map line count ~491 before run artifacts. Under 1200.

Skipped: live GitHub Pages deploy (needs Settings Pages=GitHub Actions and `github-pages` env). Saul / Product Quality is not this PR's job. Hostinger not touched.
