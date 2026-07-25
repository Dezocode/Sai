# Layered load order — Alfred bootstrap (ICM + product)

**Audience:** Alfred (`ctr-code-alfred1`) on first VPS session  
**Binding:** Same order as `first-message-to-openclaw.md` — this doc adds **why** each layer loads.

---

## Layer 0 — Repo identity (`.ai/` root)

| Order | File | Purpose |
|---|---|---|
| L0.1 | `.ai/CONTEXT.md` | SAI organization rules, governed repos, review gates |
| L0.2 | `.ai/_config/reporting.yaml` | Slack channel IDs, event types |
| L0.3 | `.ai/_config/security-policy.md` | Hard gates (secrets, force-push, production) |
| L0.4 | `.cursor/rules/sai-coordination.mdc` | Cursor-side binding (manual read if in Cursor) |

**Output:** Create `.ai/runs/<task-id>/metadata.json` + post `[SAI][INTAKE]`.

---

## Layer 1 — Contract binding

| Order | File | Purpose |
|---|---|---|
| L1.1 | `.ai/contracts/20260722-openclaw-dashboard-dezocode/contract.json` | Deliverables A0–A12, acceptance criteria |
| L1.2 | `contract.md` | Human-readable scope |
| L1.3 | `amendments/20260722-dezocode-pr45-review.md` | dezocode hard gates |
| L1.4 | `amendments/20260722-saul-cto-review.md` | Gateway bind + fail-closed gates |
| L1.5 | `PR45-REVIEW-TRACKER.md` | What's done vs open from #agentupdates |
| L1.6 | `research-integration-methods.md` | Per-deliverable integration research |
| L1.7 | `first-message-to-openclaw.md` | Executable session script (you are here) |

---

## Layer 2 — Product ICM (`openclaw-dashboard/`)

| Order | File | Purpose |
|---|---|---|
| L2.1 | `openclaw-dashboard/CONTEXT.md` | Product Layer 0 |
| L2.2 | `openclaw-dashboard/ICM-HANDBOOK.md` | Tab/settings scaffold map |
| L2.3 | `openclaw-dashboard/docs/icm-protocol-handbook.md` | Runs, CI, git discipline |
| L2.4 | `openclaw-dashboard/design/DESIGN-LANGUAGE.md` | **Before any UI** — one design system |
| L2.5 | Tab `CONTEXT.md` + `BUILD.md` | Only for surface you are building |

**Rule:** One task-id per BUILD phase; `[SAI][PLAN]` before edits.

---

## Layer 3 — Runtime (OpenClaw-primary)

| Order | File | Purpose |
|---|---|---|
| L3.1 | `OPENCLAW.md` | Repo entry for Gateway sessions |
| L3.2 | `.ai/shared/references/openclaw-runtime.md` | Scaffold paths, Phase 5B survey |
| L3.3 | `.ai/agents/alfred/AGENT.md`, `skills.md`, `hooks.json` | Your profile |
| L3.4 | `.ai/agents/_roles/contractor-coding/CHARTER.md` | Contractor authority |
| L3.5 | `runtimes/openclaw/gateway/config/gateway-exposure-policy.md` | **Loopback default** |
| L3.6 | OpenClaw docs (external) | Gateway, Slack, Telegram channels |

**ONBOARDING:** Execute `.ai/ONBOARDING.md` on VPS (not full INITIALIZE Phases 2–9 until Gateway live).

---

## Layer 4 — Build loop (repeat per deliverable)

```
intake → plan → implement → verify → review → publish_sync
         │              │
         └─ .ai/stages/* CONTEXT.md loads only what each stage needs
```

| Stage | Load | Write |
|---|---|---|
| Plan | Tab CONTEXT + research § | `.ai/runs/<id>/02_plan/` |
| Implement | Tab BUILD phase + design tokens | Product code on bootstrap branch |
| Verify | Smoke scripts + verifiers | `.ai/runs/<id>/04_verify/output/` |
| Publish | handoff.md + Slack VERIFY | PR to bootstrap branch only |

---

## PR #45 scaffold vs fulfillment

| Phase | Can proceed? |
|---|---|
| Merge contract/scaffold PR #45 | Humans + CI green on **docs/scaffold** |
| Paste first-message on VPS | After contract `status: active` |
| Alfred `registry status: active` | After L4 fulfillment (production smoke, p99, persona gate) |
| Merge product to `main` | Sai VERIFY + Saul review + both cofounders |

See [PR45-REVIEW-TRACKER.md](../../.ai/contracts/20260722-openclaw-dashboard-dezocode/PR45-REVIEW-TRACKER.md).
