# Protected CI
GitHub Actions enforce ICM audit, trusted-base behavioral anti-regression, and a 1,200 added-line PR budget without trusting candidate credentials.
## Sub-features
- `ci-agent-audit` `.github/workflows/agent-audit.yml` on push/** and PR to `main`: scaffold safety, shell allowlist, agent-setup, audit, hierarchy, handoff, OpenClaw bind/deps/health/telegram self-tests, JSON schemas, ICM file presence.
- `ci-merge-handoff-job` `merge-handoff-slack` job only on `main` push.
- `ci-anti-regression` `.github/workflows/anti-regression.yml` `pull_request_target` checks out exact base + head; runs `trusted/.github/policy/anti-regression.py`.
- `ci-anti-policy` `.github/policy/anti-regression.py` JSON parse, no new secrets, gateway loopback, connection fail-closed, constitution (budget 1200 + trusted anti-regression shape), scaffold/shell/setup, mutation self-test.
- `ci-line-budget` `.github/workflows/pr-line-budget.yml` `pull_request_target`; fail if GitHub `additions` > 1200; deletions free.
- `ci-verify-sai` agent-audit runs `go test -race` / `go vet` and `go run ./cmd/sai-verify doctor|preserve|proof` on exact HEAD once the kernel exists.
- `ci-preserve-trusted` after this kernel is on base, trusted anti-regression builds BASE `sai-verify` and preserves BASE feature IDs against candidate (candidate cannot self-authorize deletions).
## How to get to it (user POV)
- Open a PR targeting `main` — Actions: agent-audit, Anti-regression, PR line budget.
- Push any branch — agent-audit `icm-enforcement`.
- Inspect policy: `.github/policy/anti-regression.py --trusted <dir> --candidate <dir> --self-test`
## Driving it with verify-sai
Preconditions: files present; network not required for local policy.
- **Workflows present.** `test -f .github/workflows/agent-audit.yml -a -f .github/workflows/anti-regression.yml -a -f .github/workflows/pr-line-budget.yml`
- **Policy self-test.** `python3 .github/policy/anti-regression.py --trusted . --candidate . --self-test`; exit 0 (slow copy). Prefer CI for full mutation suite.
- **Budget constant.** `grep -q 'MAX_ADDITIONS: "1200"' .github/workflows/pr-line-budget.yml`
- **Trusted path.** `grep -q 'trusted/.github/policy/anti-regression.py' .github/workflows/anti-regression.yml`
- **Proof.** `go run ./cmd/sai-verify relevant --path .github/workflows/agent-audit.yml --tool Read` lists `protected-ci`.
## Gotchas
- `pull_request_target` must not persist credentials or pass secrets to candidate.
- Raising 1200 or dropping trusted-base execution is a constitution failure.
- Candidate-modified verifier is never the sole authority after BASE has `sai-verify`.
