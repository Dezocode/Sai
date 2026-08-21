# Plan — Origin-light feature maps Pages

## Current

HEAD maps are 10 feature files + README. Pages generator existed as a second Markdown parser. Saul P1 UNIT-0018 on `36e124f` requires interpretation in `cmd/sai-verify` only.

## Desired

Exact-HEAD generator that consumes `go run ./cmd/sai-verify maps` JSON. One Origin-light `feature-maps.html` / `index.html`. GitHub Pages via Actions. PR build-only. Main deploy non-required. Hidden files included on the verified build artifact.

## File changes

1. `cmd/sai-verify/main.go` — `maps` command dumps full features (id, file, title, desc, subfeatures, entry_points, proofs, gotchas).
2. `cmd/sai-verify/main_test.go` — `TestMapsJSON` requires `protected-ci` with subfeatures.
3. `scripts/render-sai-feature-maps` — Python consumes kernel JSON. No README/four-H2 grammar. Origin chrome. `--check` writes a temp dir.
4. `.github/workflows/feature-maps-pages.yml` — setup-go for `go run`; `include-hidden-files: true` on upload-artifact; `build` on PR/push; `deploy` only on `main`.
5. `.cursor/skills/verify-sai/features/protected-ci.md` — additive maps/hidden proof bullets (do not rewrite existing `::exists` workflow line).
6. Run artifacts under this task ID.

## Out of scope

PR 73, Hostinger, Apple/Go/SDL product, merging, ready-for-review, required-check promotion of Pages.

## Verification

- `scripts/render-sai-feature-maps --check`
- renderer source contains `go run ./cmd/sai-verify maps` and does not contain `load_index` / `parse_feat` / `LINK_RE`
- `go test` / `go vet` / `go run ./cmd/sai-verify doctor` / `preserve` / `drive`
- `scripts/verify-semantic-hierarchy`
- insertion count vs origin/main ≤ 1200
- generated HTML contains indexed titles + sub-ids; body canvas stays `#f8f8f8` not `#0F1115`

## Risks / rollback

- Pages Settings or public-repo requirement may block live deploy. Workflow stays non-required.
- Checks panel is best-effort (`gh` / GITHUB_TOKEN). Missing checks render as unevaluated, never as success.
- Rollback: close draft PR. No main rewrite.
