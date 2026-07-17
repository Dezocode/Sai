# Plan — PR #18 P1 git branch shell allowlist

1. Replace `Bash(git branch *)` with enumerated inspection/creation patterns scoped to `proj/splunk-clone/ctr-code-splunky/*`.
2. Add `scripts/lib/shell_allowlist.py` matcher plus `scripts/verify-contract-shell-allowlist` with negative tests for every hard-gated branch mutation.
3. Wire verifier into `.github/workflows/agent-audit.yml`.
