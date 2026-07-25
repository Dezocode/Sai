# Activation & merge checklist — PR #45 / contract `20260722-openclaw-dashboard-dezocode`

**PR:** https://github.com/Dezocode/Sai/pull/45  
**Branch:** `cursor/alfred-openclaw-contract-f1d6`  
**Contract status:** `draft` (as of last scaffold commit)  
**Architecture classification:** `isolated_prototype` — see [DR-20260724-openclaw-dashboard-prototype-boundary.md](../../shared/memory/decisions/DR-20260724-openclaw-dashboard-prototype-boundary.md)  
**CEO gate:** `[SAI][VERIFY][20260724-0311-pr45-architecture-decision-ceo]` — Part A authorized conditional on DR + amendments below

This checklist separates **merging PR #45 into `main`** (scaffold/intake) from
**activating the contract** and **Alfred organization onboarding** (production).

---

## Part A — Merge PR #45 into `Dezocode/Sai:main` (scaffold project intake)

PR #45 adds the OpenClaw dashboard **contract, Alfred profile, product ICM scaffold,
design system, secrets structure, and smoke gates** — not production dashboard code.

**Prototype boundary (Sai CEO 2026-07-24):** agent infrastructure (Alfred, OpenClaw
runtime, contract, ICM/CI extensions) may land on `main`. `openclaw-dashboard/` is
**prototype documentation only** — stack choices are proposed, not accepted core
architecture. See DR-20260724.

### Ready now (evidence)

| Gate | Status |
|---|---|
| GitHub CI `icm-enforcement` | PASS (verify on latest push) |
| `verify-semantic-hierarchy` | PASS |
| `verify-agent-setup` (Alfred OpenClaw scaffold) | PASS |
| `verify-merge-handoff` | PASS (all Task-IDs have handoffs) |
| `verify-scaffold-safety` | PASS |
| Saul P1 gateway loopback + fail-closed subagent gate | Addressed in branch |
| Saul P1 subagent discovery + P2 links | Closed at `904070f` |
| Sai CEO architecture gate | PASS — DR-20260724 + this checklist update |
| Secrets structure (PR #45 controlling) | `secrets-security.md`, `auth-matrix.md`, `settings/secrets/` |
| Design language v2 + Telegram fleet A13 | Documented |

### Required before merge (human)

| # | Action | Owner |
|---|---|---|
| M0 | Confirm DR-20260724 + contract/checklist/banner amendments on PR branch | Cora / ctr-admin |
| M1 | Review PR #45 diff on GitHub | dezocode + monaecode |
| M2 | Saul CTO re-review — confirm architecture gate + P1 fixes acceptable | Saul / dezocode |
| M3 | Explicit **merge authorization** for scaffold PR to `main` | dezocode + monaecode |
| M4 | Click merge on GitHub (or authorize agent merge) | dezocode or monaecode |

### Not required to merge PR #45

- Alfred VPS bootstrap
- Contract `status: active`
- Production smoke PASS (fulfillment stubs may exit **2** — expected pre-activation)
- `tests/smoke/all-gates.sh` exit 0 (orchestrator may exit **1** while contract-scope gates fail-closed on pending registry — expected)
- Real Telegram registry links
- `activity-ingest` p99 ≤ 15ms

**After merge:** `openclaw-dashboard/` and Alfred contract live on `main` as **project scaffold**.
Alfred remains `registry status: provisional`.

---

## Part B — Deploy (merge + paste) and formal activation

**Two-step deploy:** [DEPLOY-MERGE-AND-PASTE.md](./DEPLOY-MERGE-AND-PASTE.md) — merge PR #45, paste `first-prompt-attach-contract.md`. No activation commit required before paste.

Formal `contract.json` → `"status": "active"` after Alfred A0 PASS (recommended, not a paste blocker).

| # | Action | Owner |
|---|---|---|
| A1 | VPS prep: Node 24+, `openclaw onboard`, clone `Dezocode/Sai` @ `main` | dezocode |
| A2 | **Paste** [first-prompt-attach-contract.md](./first-prompt-attach-contract.md) into OpenClaw | dezocode |
| A3 | Alfred runs A0 per [vps-bootstrap.md](../../../openclaw-dashboard/docs/vps-bootstrap.md) | Alfred |
| A4 | Set `contract.json` → `"status": "active"` after A0 evidence | dezocode + monaecode |
| A5 | Provision secrets in `/etc/openclaw/sai.env` (Alfred MCQ if missing) | dezocode + Alfred |

---

## Part C — Alfred organization onboarding (after activation)

Blocks `registry status: active` and product merge from bootstrap → `main`.

| # | Gate | Owner |
|---|---|---|
| O1 | Alfred ONBOARDING persona gate (`.ai/ONBOARDING.md` Phases 1–6 on VPS) | Alfred |
| O2 | Phase 5B `agent-verify-caps` on VPS — populate `tools.json` | Alfred |
| O3 | `/etc/openclaw/sai.env` + loopback Gateway + exposure evidence | Alfred |
| O4 | `activity-ingest` + p99 ≤ 15ms (`verify-ingest-latency.sh` exit 0) | Alfred |
| O5 | Dashboard apps smoke — 100% production flows | Alfred |
| O6 | `verify-agent-telegram.sh` + fleet-coherence + secrets-compliance PASS | Alfred |
| O7 | Telegram proof run — dezocode confirms INTAKE+HANDOFF | dezocode |
| O8 | `[SAI][VERIFY]` PASS from Sai | Sai automation |
| O9 | Saul CTO review — no open P1 | Saul |
| O10 | Merge `proj/openclaw-dashboard/ctr-code-alfred1/bootstrap` → `main` | dezocode + monaecode |

---

## Part D — Optional project infrastructure

| Item | Owner | Notes |
|---|---|---|
| `#proj-openclaw-dashboard` Slack channel | dezocode | Approve + create |
| NotebookLM export → `docs/sources/` | dezocode | A4/A5 ingest |
| GitHub Actions `SAI_SLACK_BOT_TOKEN` secret | dezocode | CI reporting |
| monaecode/Sai fork sync to canonical SHA | monaecode | After main merge |

---

## Quick decision tree

```
Merge PR #45 now?
  → CI green + human review + cofounder merge auth → YES (scaffold only)

Deploy Alfred (2 steps)?
  → Merge → VPS prep (vps-bootstrap § dezocode) → paste first-prompt-attach → YES

Activate contract.json status formally?
  → After Alfred A0 PASS evidence → recommended, not required before paste

Alfred active + product on main?
  → After Part C complete → YES
```

---

## Links

| Doc | Path |
|---|---|
| Contract JSON | [contract.json](./contract.json) |
| Secrets control | [secrets-security.md](../../../openclaw-dashboard/docs/secrets-security.md) |
| Review tracker | [PR45-REVIEW-TRACKER.md](./PR45-REVIEW-TRACKER.md) |
| Prototype boundary DR | [DR-20260724-openclaw-dashboard-prototype-boundary.md](../../shared/memory/decisions/DR-20260724-openclaw-dashboard-prototype-boundary.md) |
| First prompt | [first-prompt-attach-contract.md](./first-prompt-attach-contract.md) |
| Deploy (2 steps) | [DEPLOY-MERGE-AND-PASTE.md](./DEPLOY-MERGE-AND-PASTE.md) |
| VPS bootstrap | [vps-bootstrap.md](../../../openclaw-dashboard/docs/vps-bootstrap.md) |
