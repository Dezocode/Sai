# Protected CI
GitHub Actions enforce ICM audit, trusted-base behavioral anti-regression, and a 1,200 added-line PR budget without trusting candidate credentials.
## Sub-features
- `ci-agent-audit` `.github/workflows/agent-audit.yml` on push/** and PR to `main`: scaffold safety, shell allowlist, agent-setup, audit, hierarchy, handoff, OpenClaw bind/deps/health/telegram self-tests, JSON schemas, ICM file presence.
- `ci-merge-handoff-job` `merge-handoff-slack` job only on `main` push.
- `ci-anti-regression` `.github/workflows/anti-regression.yml` `pull_request_target` checks out exact base + head; runs `trusted/.github/policy/anti-regression.py`.
- `ci-anti-policy` `.github/policy/anti-regression.py` JSON parse, no new secrets, gateway loopback, connection fail-closed, constitution (budget 1200 + trusted anti-regression shape), scaffold/shell/setup, mutation self-test.
- `ci-line-budget` `.github/workflows/pr-line-budget.yml` `pull_request_target`; fail if GitHub `additions` > 1200; deletions free.
- `ci-verify-sai` agent-audit runs `go test -race` / `go vet` / `sai-verify drive|doctor|preserve|proof` on `pull_request.head.sha` (not the merge ref) and uploads `sai-verify-proof.txt` plus `sai-verify-proof.json`.
- `ci-preserve-trusted` after this kernel is on base, trusted anti-regression builds BASE `sai-verify` and preserves BASE feature IDs against candidate (candidate cannot self-authorize deletions).
- `ci-feature-maps-pages` `.github/workflows/feature-maps-pages.yml` builds Origin-light HTML from HEAD `.cursor/skills/verify-sai/features/` via `scripts/render-sai-feature-maps`; `main` deploy is non-required GitHub Pages. Also emits `pr-sessions.html`: scrollable PR wheel joining two live data planes by PR number - authoritative GitHub PR state for Dezocode/Sai via unauthenticated public REST (`api.github.com`, CORS-enabled, ETag conditional GETs, never any token) and the public sessions API. Cards are the union of GitHub PRs and session `pr` keys; open PRs with no session render an Agent NONE warning while a sessions outage renders Agent UNKNOWN (attachment unknown, never claimed absent); session HEAD is compared against authoritative PR HEAD; summary/graph row covers PR states and agent/heartbeat freshness with fresh/stale/missing as distinct buckets (30m threshold; missing never counted as stale); Saul state comes from the check-run's own published counts when present (latest run wins) or its conclusion, never invented totals; malformed payloads on either plane (sessions API or GitHub pull list) degrade as unavailable instead of silent empty; session-linked PRs outside the first GitHub listing page are still enriched via their per-PR endpoint; renderer `--check` asserts both plane URLs, tab link, wheel, summary mount, NONE/UNKNOWN/mismatch/bucket markers, 60s client refresh, and banned-token absence; renderer stays token-free.
## How to get to it (user POV)
- Open a PR targeting `main` — Actions: agent-audit, Anti-regression, PR line budget. Push any branch — agent-audit `icm-enforcement`. Inspect policy: `.github/policy/anti-regression.py --trusted <dir> --candidate <dir> --self-test`
- Pages: local `scripts/render-sai-feature-maps --check`; renderer consumes `go run ./cmd/sai-verify maps`; PR job `build` without `github-pages` env; PR/non-main build writes empty checks JSON and does not receive github.token; live conclusions are fetched only on main deploy; renderer never gets `GH_TOKEN`; `main` push deploys if Pages source is GitHub Actions.
## Driving it with verify-sai
- **Workflows.** ::exists .github/workflows/agent-audit.yml .github/workflows/anti-regression.yml .github/workflows/pr-line-budget.yml
- **Policy.** ::py .github/policy/anti-regression.py --trusted . --candidate . --self-test timeout=180
- **Budget.** ::contains .github/workflows/pr-line-budget.yml MAX_ADDITIONS
- **Trusted path.** ::contains .github/workflows/anti-regression.yml trusted/.github/policy/anti-regression.py
- **Pages render.** ::exists scripts/render-sai-feature-maps
- **Pages workflow.** ::exists .github/workflows/feature-maps-pages.yml
- **Pages sessions.** ::contains scripts/render-sai-feature-maps pr-sessions.html
- **Pages maps.** ::contains scripts/render-sai-feature-maps go run ./cmd/sai-verify maps
- **Pages hidden.** ::contains .github/workflows/feature-maps-pages.yml include-hidden-files
- **Pages PR checks.** ::contains .github/workflows/feature-maps-pages.yml feature-maps-checks.json
## Gotchas
- `pull_request_target` must not persist credentials or pass secrets to candidate. agent-audit checks out with `persist-credentials: false` and unsets `GITHUB_TOKEN` before candidate `go test`. Policy rejects package-level `= func(` initializers. Raising 1200 or dropping trusted-base execution is a constitution failure. Candidate-modified verifier is never the sole authority after BASE has `sai-verify`. After BASE has the kernel, `runRecipe`/`allowBin`/`parseRecipe`/recipe.err/`git`/`recipeEnv` text must match trusted so argv cannot become `bash -lc` while leaving the exec call sites unchanged.
- Pages HTML is public; no secrets. Org Free Pages may need a public repo. Failed deploy must not be a required check. Hostinger stays Saul-go.
- PR and non-main Pages build must not receive github.token. Those jobs write empty checks JSON. Live check-run fetch stays on main deploy only. Unset `GITHUB_TOKEN` `GH_TOKEN` before the renderer. Do not export GH_TOKEN into the candidate renderer step.
- Feature-map interpretation stays in `cmd/sai-verify maps`. The Pages generator consumes that JSON. Do not add a second README or four-H2 parser.
- `pr-sessions.html` is a client-side consumer of two public read APIs: the sessions API and GitHub's unauthenticated REST (public repo fields only). The renderer never holds a sessions write token or any GitHub credential; missing data must render as unavailable, never fabricated. Heartbeat styling distinguishes fresh/stale/missing (30m threshold) - missing heartbeats are labeled missing without asserting elapsed time, and sessions-plane outages must not be read as 'no worker attached'. Rate limits are handled by ETag conditional requests, not by embedding tokens.
