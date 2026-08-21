# Implement — feature maps Pages

Generator `scripts/render-sai-feature-maps` reads `features/README.md` then sibling `*.md` using the kernel four-H2 contract. HTML is generated output. Maps stay canonical.

Workflow `Feature maps Pages` (`.github/workflows/feature-maps-pages.yml`):
- `build` on PR and any push. No `github-pages` environment. `--check` then `--out` under `$RUNNER_TEMP`. Regular artifact.
- `deploy` only on push to `main`. `pages: write` + `id-token: write`. Environment `github-pages`. Non-required.

Map: additive `ci-feature-maps-pages` on `protected-ci.md`. Existing Workflows `::exists` line unchanged. Proofs are `::exists` (renderer is not in `allowBin`; CI and `--check` remain the behavioral proof).

No Apple, Go kernel, or SDL product edits. Hostinger untouched. PR 73 untouched.
