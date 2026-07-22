# Activation & merge checklist — PR #45 / contract `20260722-openclaw-dashboard-dezocode`

**PR:** https://github.com/Dezocode/Sai/pull/45  
**Branch:** `cursor/alfred-openclaw-contract-f1d6`  
**Contract status:** `draft` (as of last scaffold commit)

This checklist separates **merging PR #45 into `main`** (scaffold/intake) from
**activating the contract** and **Alfred organization onboarding** (production).

---

## Part A — Merge PR #45 into `Dezocode/Sai:main` (scaffold project intake)

PR #45 adds the OpenClaw dashboard **contract, Alfred profile, product ICM scaffold,
design system, secrets structure, and smoke gates** — not production dashboard code.

### Ready now (evidence)

| Gate | Status |
|---|---|
| GitHub CI `icm-enforcement` | PASS (verify on latest push) |
| `verify-semantic-hierarchy` | PASS |
| `verify-agent-setup` (Alfred OpenClaw scaffold) | PASS |
| `verify-merge-handoff` | PASS (all Task-IDs have handoffs) |
| `verify-scaffold-safety` | PASS |
| Saul P1 gateway loopback + fail-closed subagent gate | Addressed in branch |
| Secrets structure (PR #45 controlling) | `secrets-security.md`, `auth-matrix.md`, `settings/secrets/` |
| Design language v2 + Telegram fleet A13 | Documented |

### Required before merge (human)

| # | Action | Owner |
|---|---|---|
| M1 | Review PR #45 diff on GitHub | dezocode + monaecode |
| M2 | Saul CTO re-review — confirm P1 fixes acceptable | Saul / dezocode |
| M3 | Explicit **merge authorization** for scaffold PR to `main` | dezocode + monaecode |
| M4 | Click merge on GitHub (or authorize agent merge) | dezocode or monaecode |

### Not required to merge PR #45

- Alfred VPS bootstrap
- Contract `status: active`
- Production smoke PASS
- Real Telegram registry links
- `activity-ingest` p99 ≤ 15ms

**After merge:** `openclaw-dashboard/` and Alfred contract live on `main` as **project scaffold**.
Alfred remains `registry status: provisional`.

---

## Part B — Activate contract (`draft` → `active`)

Activation authorizes Alfred to execute `first-message-to-openclaw.md` on Hostinger VPS.

| # | Action | Owner |
|---|---|---|
| A1 | Review final [contract.json](./contract.json) + [contract.md](./contract.md) | dezocode + monaecode |
| A2 | Confirm secrets doctrine: [secrets-security.md](../../../openclaw-dashboard/docs/secrets-security.md) | dezocode + Saul |
| A3 | Set `contract.json` → `"status": "active"` (commit on `main` or activation PR) | dezocode + monaecode |
| A4 | Post `[SAI][CONTRACT][task-id]` to #agentupdates announcing activation | Cora or dezocode |
| A5 | Provision VPS secrets per [auth-matrix.md](../../../openclaw-dashboard/docs/auth-matrix.md) — **values on VPS only** | dezocode + Alfred |
| A6 | Paste [first-prompt-attach-contract.md](./first-prompt-attach-contract.md) into OpenClaw Gateway | dezocode triggers Alfred |

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

Activate contract now?
  → After PR #45 merged + terms confirmed + VPS secrets planned → YES

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
| First prompt | [first-prompt-attach-contract.md](./first-prompt-attach-contract.md) |
