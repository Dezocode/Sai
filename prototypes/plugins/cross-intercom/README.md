# cross-intercom prototype plugin

Status: **prototype tier** (`prototypes/plugins/cross-intercom/`, PR-76 lane). Nothing here ships to main production code; graduation requires an explicit production-authority PR.

Author/agent: **her**

## Purpose

A local-side, gh-authenticated bridge that hooks agents into Sai cross-communication lanes while working on the repo:

1. **Aspectizer hook** — on every incoming user request (`beforeSubmitPrompt`), decompose the request into named aspects and inject them as structured context so downstream agents see the request's parts, not just its prose.
2. **Lane connector** — use the local `gh` credential (never an embedded secret) to authenticate this agent to the sessions API being hardened in the hermes-sessions-api work: read the public planes, upsert a `sai-sessions-v2` session row tagged with its **side** (`local` vs `repo`) and `monitors:["crosscom"]`.

Local side = agent running in a local checkout (this repo, Atomic/Hermes sessions). Repo side = state published by/for the GitHub PR plane. Crosscomming = both sides converge on one session identity per Task-ID.

## Layout

```
.cursor/hooks.json        prototype hook wiring (beforeSubmitPrompt -> aspectizer)
.cursor/hooks/aspectizer.sh     aspect decomposition hook
.cursor/hooks/lane-connector.sh gh-auth bridge to sessions API
docs/GOALS.md             /goals for the successor PR
```

## Non-goals

- No production `.cursor/` edits; no verifier changes; no server-side auth changes here (that contract is defined in GOALS.md for the API lane).
