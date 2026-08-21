# Handoff — feature maps GitHub Pages

## Product purpose (held)

Sai is the app for parents to give their children access to the internet and AI tools safely. This PR adds no product features. It publishes the already-canonical verify-sai map as a GitHub Pages site so Dezocode can see live maps, sub-features, and check blockers without treating Drive HTML as a second constitution.

## Parser boundary

Interpretation happens in `cmd/sai-verify maps`. The Pages generator consumes that JSON. Python does not parse README index or four-H2 Markdown.

## SHAs

- START_HEAD: `bb39842bf30bdb08ab0cf859bb4f5f39f379f8f9` (GitHub `origin/main`. Equals OBSERVED_START_HEAD. Main did not move.)
- Prior product HEAD: `36e124fa55ccf8dfb6ca2c125f7a1a71289419bf`
- Branch: `cursor/feature-maps-pages-32aa`
- PR: https://github.com/Dezocode/Sai/pull/74 (draft). Did not update PR 73.
- Agent: cursor-cloud / `bc-e0e95991-dee1-4019-a799-278f28c332aa`

## Files

- `cmd/sai-verify/main.go` — `maps` JSON dump of the full feature map
- `cmd/sai-verify/main_test.go` — `TestMapsJSON`
- `scripts/render-sai-feature-maps` — consumes `go run ./cmd/sai-verify maps`; Origin chrome; four H2s; `html.escape`; missing `gh` → unevaluated
- `.github/workflows/feature-maps-pages.yml` — setup-go on build and deploy; `include-hidden-files: true` on the build artifact; trusted check-run fetch, then unset tokens before renderer
- `.cursor/skills/verify-sai/features/protected-ci.md` — additive maps/hidden proofs
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

- Saul check `96920958116` ran on `36e124f` (P1 dual parser, P2 hidden files). That check is stale vs this HEAD. Do not claim Saul success.
- Live Pages URL is pending Settings. Do not merge. Stay draft.
- Slack `SAI_SLACK_BOT_TOKEN` unset; events queued.
- Next safe action after candidate CI is green on this HEAD: wait for a fresh Saul / Product Quality run.
