# Verification — agent initialization compliance

## Commands

```bash
SAI_AGENT_ID=ceo-automation scripts/verify-scaffold-safety
SAI_AGENT_ID=ceo-automation scripts/verify-semantic-hierarchy
SAI_AGENT_ID=ceo-automation scripts/verify-agent-audit origin/main..HEAD
bash -n scripts/agent-scaffold scripts/agent-memory-scaffold scripts/agent-contract-scaffold scripts/agent-contract-pr-review scripts/lib/agent-path-guards.sh
```

## P1 fixes (CTO PR #9 review)

1. **Path validation** — `scripts/lib/agent-path-guards.sh` shared by all scaffold scripts; rejects traversal and out-of-subtree writes.
2. **Contract review semantics** — `agent-contract-pr-review` returns `pending_manual` (non-zero exit) when acceptance criteria are manual; `pass` only when all automated checks pass and no manual criteria remain.

## Roadmap impact

Contractor/prototype lane (PR #9) remains blocked until it rebases onto these fixes and Saul re-authenticates GitHub for CTO review submission.
