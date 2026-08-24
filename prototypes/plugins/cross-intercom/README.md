# Sai Harness — cross-intercom prototype plugin

Status: **prototype tier** (`prototypes/plugins/cross-intercom/`, PR-76 lane). Nothing here ships to main production code; graduation requires an explicit production-authority PR.

Author/agent: **her** · Harness name: **Sai Harness**

## Purpose

A local-side, gh-authenticated bridge that hooks agents into Sai cross-communication lanes while working on the repo:

1. **Aspectizer hook** — on every incoming user request (`beforeSubmitPrompt`), decompose the request into named aspects and inject them as structured context so downstream agents see the request's parts, not just its prose.
2. **Lane connector** — use the local `gh` credential (never an embedded secret) to authenticate this agent to the sessions API being hardened in the hermes-sessions-api work: read the public planes, upsert a `sai-sessions-v2` session row tagged with its **side** (`local` vs `repo`) and `monitors:["crosscom"]`.

Local side = agent running in a local checkout. Repo side = state published by/for the GitHub PR plane. Crosscomming = both sides converge on one session identity per Task-ID.

## Provenance & licensing

Sai Harness's hook model derives from **Atomic CLI** ([bastani-inc/atomic](https://github.com/bastani-inc/atomic)) — **MIT © 2025 Bastani, Inc.** Free to use, modify, and redistribute. Sole attribution clause: products exceeding 100M MAU or $20M monthly revenue must display "Atomic" in their UI. A future goal integrates the Atomic CLI itself into this plugin (see GOALS.md).

## Layout

```
.sai/hooks.json                 Sai Harness manifest (provenance, MIT, hook wiring)
.sai/hooks/aspectizer.sh        aspect decomposition hook (implementation lives HERE)
.sai/hooks/lane-connector.sh    gh-auth bridge to sessions API (implementation lives HERE)
.cursor/hooks.json              Cursor-plane wiring delegating to .sai/hooks/*
docs/GOALS.md                   /goals for this PR
```

Single source of truth: implementations live under `.sai/hooks/`; `.cursor/` wiring delegates.

## Non-goals

- No production `.cursor/` edits; no verifier changes; no server-side auth changes here (that contract is defined in GOALS.md for the API lane).
