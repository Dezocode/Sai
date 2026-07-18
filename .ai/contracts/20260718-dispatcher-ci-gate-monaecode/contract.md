# Contract: Dispatcher CI merge gate

| Field | Value |
|---|---|
| **Contract ID** | `20260718-dispatcher-ci-gate-monaecode` |
| **Short ref** | `20260718-0155` (Cora Slack tel link) |
| **Subject** | Blocking CI before Mimi dispatcher merge to `Dezocode/Sai:main` |
| **Principal** | monaecode (U0BGNS7F0T1) |
| **Issued by** | Cora (ctr-admin) on Sai CEO directive |
| **Status** | active |

## Purpose

Ensure every registered SAI agent appears in the canonical **dispatch matrix**
(Slack + GitHub routing) and that Mimi dispatcher PRs cannot merge until
Desktop-verified subagent CLI + SDK smoke evidence exists.

## Deliverables (canonical repo)

| ID | Path | Description |
|---|---|---|
| D0 | `.ai/_config/dispatch-matrix.json` | Routing for ceo, mimi, saul, cora, alpha |
| D1 | `scripts/verify-dispatcher-matrix` | Structural + merge-gate verifier |
| D2 | `.ai/shared/references/dispatcher-desktop-evidence.md` | Host-only checklist |
| D3 | `.github/workflows/agent-audit.yml` | `dispatcher-merge-gate` job on dispatcher paths |

## Acceptance

1. `scripts/verify-dispatcher-matrix` OK on every push/PR (structural).
2. PRs touching dispatcher paths trigger merge gate; gate fails until:
   - verified `claude-agent-sdk` in Mimi `tools.json`
   - `dispatcher-desktop-proof.txt` in a run `04_verify/output/`
3. Sai posts `[SAI][VERIFY]` citing this contract after CI wiring lands on canonical.

## Out of scope for cloud agents

Live Claude Desktop sessions, authenticated SDK `--smoke`, and live dispatch of
all five agents must run on co-founder Desktop hosts — documented in D2, not
fabricated in CI.
