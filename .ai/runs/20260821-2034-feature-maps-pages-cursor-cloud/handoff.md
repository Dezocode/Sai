# Handoff — feature maps GitHub Pages

## Product purpose (held)

Sai is the app for parents to give their children access to the internet and AI tools safely. This PR adds no product features. It publishes the already-canonical verify-sai map as a GitHub Pages site so Dezocode can see live maps, sub-features, and check blockers without treating Drive HTML as a second constitution.

## SHAs

- START_HEAD: `bb39842bf30bdb08ab0cf859bb4f5f39f379f8f9` (GitHub `origin/main`. Equals OBSERVED_START_HEAD. Main did not move.)
- PRODUCT_HEAD: `4db544e2e9da0097a5e55e45dc13684fb642184f` (generator, workflow, additive map)
- Saul P1 follow-up: token split in `.github/workflows/feature-maps-pages.yml` (this commit)
- Branch: `cursor/feature-maps-pages-32aa`
- PR: https://github.com/Dezocode/Sai/pull/74 (draft). Did not update PR 73.
- Agent: cursor-cloud / `bc-e0e95991-dee1-4019-a799-278f28c332aa`

## Files

- `scripts/render-sai-feature-maps` — Python 3 generator from HEAD maps
- `.github/workflows/feature-maps-pages.yml` — trusted check-run fetch, then unset tokens before renderer
- `.cursor/skills/verify-sai/features/protected-ci.md` — additive `ci-feature-maps-pages` plus token-split how-to/gotcha
- `.ai/runs/20260821-2034-feature-maps-pages-cursor-cloud/`

## Local generate

```
scripts/render-sai-feature-maps --check
scripts/render-sai-feature-maps --out DIR
```

## Pages

- Workflow name: **Feature maps Pages**
- PR / non-main push: `build` only. No `github-pages` environment.
- `main` push: `deploy` with `pages: write` + `id-token: write`.
- Candidate renderer does not receive `GH_TOKEN` or `GITHUB_TOKEN`.
- Repo Settings still need Pages source = GitHub Actions and environment `github-pages`.
- Hostinger stays Saul-go.

## CI / blockers

- Saul / Product Quality P1 on `6a858c8` (UNIT-0017 token in renderer) is the follow-up this commit addresses. Do not claim Saul success until the new head re-runs.
- Live Pages URL is pending Settings. Do not merge. Stay draft.
- Slack `SAI_SLACK_BOT_TOKEN` unset; events queued.
- Next safe action: wait for Saul / Product Quality on this head; co-founder reviews draft PR 74.
