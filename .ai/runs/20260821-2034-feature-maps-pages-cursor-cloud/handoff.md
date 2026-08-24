# Handoff — feature maps GitHub Pages

## Product purpose (held)

Sai is the app for parents to give their children access to the internet and AI tools safely. This PR adds no product features. It publishes the already-canonical verify-sai map as a GitHub Pages site so Dezocode can see live maps, sub-features, and check blockers without treating Drive HTML as a second constitution.

## Parser boundary

Interpretation happens in `cmd/sai-verify maps`. That command is the only machine parser. It reuses `fillMap` and fail-closes when the map is invalid: empty stdout, stderr `invalid map`, exit 1. Success JSON encodes `Problems: s.Problems` (empty). The Pages generator consumes that JSON. Python does not parse README index or four-H2 Markdown.

## SHAs

- START_HEAD: `bb39842bf30bdb08ab0cf859bb4f5f39f379f8f9` (GitHub `origin/main`)
- Independently confirmed GitHub branch HEAD before this worker: `aeb1dfe1bcae573bb0dcf150b5c563fb317d1d06` (equals `origin/cursor/feature-maps-pages-32aa` and local HEAD; did not reset)
- NEW HEAD: `50d45edd345047bc4a49388a59f0010abbdc6bd2` (fail-closed `mapsCmd` on `cursor/feature-maps-pages-32aa`)
- Branch: `cursor/feature-maps-pages-32aa`
- PR: https://github.com/Dezocode/Sai/pull/74 (draft). Did not update PR 73.
- Pages parent: `bc-e0e95991-dee1-4019-a799-278f28c332aa`
- This worker: `bc-5becca1d-506c-5f8a-8ea4-dca3a37e8053`
- Agent: cursor-cloud / `cursoragent@cursor.com`

## Units closed on this commit

- UNIT-0018 / UNIT-0020: `mapsCmd` calls `fillMap` after `loadFeats` and the empty-feats error. Invalid map returns before `Encode`.
- UNIT-0019: `TestMapsJSON` keeps the protected-ci happy path and adds a dead-index case (`invalid map`, empty stdout, `dead index` on stderr).

## Files

- `cmd/sai-verify/main.go` — fail-closed `maps` JSON dump via `fillMap`
- `cmd/sai-verify/main_test.go` — `TestMapsJSON` happy path plus invalid-map
- `scripts/render-sai-feature-maps` — consumes `go run ./cmd/sai-verify maps`; SystemExit on kernel `problems`
- `.github/workflows/feature-maps-pages.yml` — token-free PR/non-main build; deploy fetches on main
- `.cursor/skills/verify-sai/features/protected-ci.md` — okTok-safe Pages PR checks needle
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

## Verification (this worker)

- First `go run ./cmd/sai-verify drive` on this dirty tree failed only `::gotest -race ./...` via `TestFuturePRAndHooks` dishonest proof (`PASS evidence-bound` from the prior fail=0 receipt). Expected locally. Did not change the test.
- Recovery drive fail=0 pass=59 sweep=clean. `::gotest -race ./...` PASS including `TestMapsJSON`.
- `python3 scripts/render-sai-feature-maps --check` → `OK render-sai-feature-maps --check features=10`
- `go test ./cmd/sai-verify -run TestMapsJSON -count=1` PASS (0.008s)
- `go vet ./cmd/sai-verify` PASS
- `scripts/verify-semantic-hierarchy` OK
- `scripts/verify-agent-audit -n 20 HEAD` OK
- `scripts/verify-merge-handoff origin/main..HEAD` OK
- Post-commit drive on `50d45ed` fail=0 pass=59 sweep=clean completeness=proven.
- Insertions vs `origin/main` 884 on `50d45ed` (under 1200).

## Remaining action

Wait for candidate CI green on the NEW HEAD, then a fresh Codex Saul (`codex_invoked=true`, `synthetic=false`). Do not claim Saul SUCCESS. Stay draft. Do not merge. Do not mark ready. Do not update PR 73. Do not edit Hostinger. Slack `SAI_SLACK_BOT_TOKEN` unset; events queued when reported.
