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
## How to get to it (user POV)
- Open a PR targeting `main` — Actions: agent-audit, Anti-regression, PR line budget. Push any branch — agent-audit `icm-enforcement`. Inspect policy: `.github/policy/anti-regression.py --trusted <dir> --candidate <dir> --self-test`
## Driving it with verify-sai
- **Workflows.** ::exists .github/workflows/agent-audit.yml .github/workflows/anti-regression.yml .github/workflows/pr-line-budget.yml
- **Policy.** ::py .github/policy/anti-regression.py --trusted . --candidate . --self-test timeout=180
- **Budget.** ::contains .github/workflows/pr-line-budget.yml MAX_ADDITIONS
- **Trusted path.** ::contains .github/workflows/anti-regression.yml trusted/.github/policy/anti-regression.py
## Gotchas
- `pull_request_target` must not persist credentials or pass secrets to candidate. agent-audit checks out with `persist-credentials: false` and unsets `GITHUB_TOKEN` before candidate `go test`. Policy rejects package-level `= func(` initializers. Raising 1200 or dropping trusted-base execution is a constitution failure. Candidate-modified verifier is never the sole authority after BASE has `sai-verify`. After BASE has the kernel, `runRecipe`/`allowBin`/`parseRecipe`/recipe.err/`git`/`recipeEnv` text must match trusted so argv cannot become `bash -lc` while leaving the exec call sites unchanged.
