# Runtime Intelligence Memory Architecture

## Tier 0 — ephemeral
Process/container memory and temporary experiment files. Never authoritative.

## Tier 1 — Hostinger operational memory
Suggested root:

```text
/opt/sai/runtime-intelligence/
  state/runtime-intel.db
  telemetry/
  experiments/
  cache/
  queue/
  exports/
  dashboard/
  openclaw/
  grok/
```

Start with SQLite; move high-volume metrics to a Prometheus-compatible TSDB/VictoriaMetrics only when needed.

Suggested domains: events, experiments, samples, runtime_health, workflow_runs, findings, issue_links, pr_links, stub_observations, memory_sync, dashboard_snapshots, capacity_events, subprocess_runs.

Raw/high-frequency telemetry stays local. Do not store credentials, OAuth state, cookies, API keys, or raw secrets.

## Tier 2 — Git-backed organizational semantic memory
Git is durable organizational truth for promoted knowledge. Recommended skeleton:

```text
memory/
  manifests/INDEX.yaml
  agents/
  architecture/
  decisions/
  incidents/open/
  incidents/resolved/
  experiments/YYYY/EXP-*/
  findings/open/
  findings/resolved/
  stubs/INDEX.yaml
  stubs/unresolved/
  stubs/resolved/
  runtimes/cursor/
  runtimes/codex-saul/
  runtimes/hermes/
  runtimes/grok/
  runtimes/openclaw/
  benchmarks/
  patterns/
  dashboard/latest-summary.json
```

Promote local memory when a result is a confirmed defect, incident, architectural lesson, repeated anomaly, benchmark used for a decision, reusable test pattern, support sub-PR, new stub, or changed runtime/governance assumption.

Every durable object records provenance, task/experiment, repo/PR, exact SHA(s), contract revision when applicable, source evidence, timestamps, issue/PR links, and uncertainty.

## Tier 3 — Sai Wiki projection
Human-readable projection regenerated from structured memory. Suggested pages: Runtime Control Tower, Runtime Health, Experiments, Incidents, Open Findings, Stub Index, Benchmark History, Agent Runtimes, Operating Manual, Architecture Decisions.

Wiki prose is never the sole machine source of truth.

## Projection of Decision 0008 (repo is canonical)

Persistent logical primary, `/resume-sai`, named Cora/contractor tree,
read-only 1500s watchdog, and the two-primary cap are defined in
`.ai/shared/memory/decisions/0008-persistent-primary-cursor-orchestrator.md`.

Runtime Intelligence (Hermes/Grok/OpenClaw) may **project** that record
into Hostinger memory and the Sai Wiki (suggested page: Operating Manual /
Architecture Decisions). They must not rewrite it. They may run
`scripts/sai-watchdog` as a no-model heartbeat. They do not consume a
primary-implementation slot (kind `runtime_intelligence` / `stacked`).

Physical Cloud `bcId` resume requires an official follow-up prompt; silent
GitHub wake is unsupported. Logical pickup is `/resume-sai`.

Blocker authority (Decision 0008 amendment): any authorized agent may
append evidence-backed blockers. Only Saul technically PASSes via a
qualifying full CTO review. Sai PASSes governance blockers only. Project
the open-blocker set onto the Control Tower; do not delete history.

## Live dashboard
Host on Hostinger. Hermes/OpenClaw may continuously refresh it from local telemetry. Grok may contribute adversarial/comparative interpretation but must not overwrite measured telemetry.

Minimum panels: runtime/agent status, current repo/PR/head, state-machine phase, CI, Saul runner, experiment progression, latency, retry counts, CPU/memory, token/cost where observable, stale approval/lease events, authorization blocks, event backlog, confirmed findings, runtime comparison on common workloads, incident timeline.

## Conflict rule
If local Hostinger state conflicts with tracked Git organizational state, Git wins for organizational authority. Local telemetry remains evidence and the discrepancy may itself become a Runtime Intelligence issue.