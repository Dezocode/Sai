# Plan — Origin-light feature maps Pages

## Current

HEAD maps are 10 feature files + README. No repo script emits HTML. Origin renders a private Drive copy. Live required checks on main: `icm-enforcement`, Anti-regression, PR line budget, Saul / Product Quality.

## Desired

Exact-HEAD generator using the kernel's four-H2 contract (Sub-features, How to get to it, Driving it, Gotchas) plus README `## Features` index. One Origin-light `feature-maps.html` / `index.html`. GitHub Pages via Actions. PR build-only. Main deploy non-required.

## File changes

1. `scripts/render-sai-feature-maps` — Python 3. Reads README index then sibling `*.md`. Renders Origin chrome, feature cards, optional checks JSON, SDL constitution chip. `--check` writes a temp dir (no worktree residue).
2. `.github/workflows/feature-maps-pages.yml` — `build` on PR/push (contents read, regular artifact). `deploy` only on `main` push (`pages: write`, `id-token: write`, `github-pages` env). Pin action SHAs. Include `.nojekyll` in the site dir.
3. `.cursor/skills/verify-sai/features/protected-ci.md` — add sub-feature `ci-feature-maps-pages` plus new proof bullets (do not rewrite existing `::exists` workflow line; that would weaken preserve).
4. Run artifacts under this task ID.

## Out of scope

PR 73, Hostinger, Apple/Go/SDL product, merging, ready-for-review, required-check promotion of Pages.

## Verification

- `scripts/render-sai-feature-maps --check`
- `go run ./cmd/sai-verify doctor` / `preserve` / `drive`
- `scripts/verify-semantic-hierarchy`
- `python3 -m json.tool` on new JSON
- insertion count vs origin/main ≤ 1200
- generated HTML contains indexed titles + sub-ids; body canvas stays `#f8f8f8` not `#0F1115`

## Risks / rollback

- Pages Settings or public-repo requirement may block live deploy. Workflow stays non-required.
- Checks panel is best-effort (`gh` / GITHUB_TOKEN). Missing checks render as unevaluated, never as success.
- Rollback: close draft PR. No main rewrite.
