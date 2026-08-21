# Handoff — feature maps GitHub Pages

## Product purpose (held)

Sai is the app for parents to give their children access to the internet and AI tools safely. This PR adds no product features. It publishes the already-canonical verify-sai map as a GitHub Pages site so Dezocode can see live maps, sub-features, and check blockers without treating Drive HTML as a second constitution.

## SHAs

- START_HEAD: `bb39842bf30bdb08ab0cf859bb4f5f39f379f8f9` (GitHub `origin/main`. Equals OBSERVED_START_HEAD. Main did not move.)
- FINAL_HEAD: fill after push (local commit SHA at commit time)
- Branch: `cursor/feature-maps-pages-32aa` (cloud prefix required). Suggested `docs/feature-maps-pages` was not used.
- Agent: cursor-cloud / `bc-e0e95991-dee1-4019-a799-278f28c332aa`. Did not reuse `bc-98be4562-0631-4643-875d-5b8831b8e95f`. Did not update PR 73.

## Files

- `scripts/render-sai-feature-maps` — Python 3 generator from HEAD maps
- `.github/workflows/feature-maps-pages.yml` — workflow name **Feature maps Pages**
- `.cursor/skills/verify-sai/features/protected-ci.md` — additive `ci-feature-maps-pages`
- `.ai/runs/20260821-2034-feature-maps-pages-cursor-cloud/`

## Local generate

```
scripts/render-sai-feature-maps --check
scripts/render-sai-feature-maps --out DIR
```

`--out` writes `feature-maps.html`, `index.html`, empty `.nojekyll`. Do not commit generated HTML.

## Pages

- Workflow name: **Feature maps Pages**
- PR / non-main push: `build` only. No `github-pages` environment.
- `main` push: `deploy` with `pages: write` + `id-token: write`.
- Repo Settings still need Pages source = GitHub Actions and environment `github-pages`. Org Free Pages may need a public repo. Failed deploy must not be a required check.
- Hostinger stays Saul-go.

## CI / blockers

- Local drive 56/0 and renderer `--check` passed.
- Do not claim Saul success. Saul `action_required` on other PRs is out of scope.
- Live Pages URL is pending Settings. Do not merge. Stay draft.
- Next safe action: co-founder reviews draft PR; enable Pages source GitHub Actions if deploy should publish after merge.
