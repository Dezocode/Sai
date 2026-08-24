# OpenClaw surfaces
The OpenClaw SAI Dashboard prototype exposes documented tabs, settings, desktop/iOS shells, and one design language. It is not accepted core architecture (DR-20260724).
## Sub-features
- `oc-root` `openclaw-dashboard/{README,CONTEXT,ICM-HANDBOOK}.md` prototype boundary + load order.
- `oc-tab-tracking` `openclaw-dashboard/tabs/tracking/{CONTEXT,BUILD}.md` live activity meter / 15ms SLO.
- `oc-tab-second-brain` `openclaw-dashboard/tabs/second-brain/{CONTEXT,BUILD}.md` vault + graph.
- `oc-tab-research` `openclaw-dashboard/tabs/research/{CONTEXT,BUILD}.md` + `shared-workspaces.md`.
- `oc-tab-chat` `openclaw-dashboard/tabs/chat-room/{CONTEXT,BUILD,game-engine,agent-rolodex}.md` Habbo + Telegram PM.
- `oc-tab-github` `openclaw-dashboard/tabs/github/{CONTEXT,BUILD}.md` branch/CI dashboard.
- `oc-tab-config` `openclaw-dashboard/tabs/config/{CONTEXT,BUILD}.md` OpenClaw config mirror.
- `oc-set-auth` `openclaw-dashboard/settings/auth/{CONTEXT,BUILD,providers}.md`
- `oc-set-host` `openclaw-dashboard/settings/host-health/{CONTEXT,BUILD}.md`
- `oc-set-reporting` `openclaw-dashboard/settings/reporting-sop/{CONTEXT,BUILD}.md`
- `oc-set-models` `openclaw-dashboard/settings/models/{CONTEXT,BUILD}.md`
- `oc-set-secrets` `openclaw-dashboard/settings/secrets/{CONTEXT,BUILD}.md` masked status, no secret values.
- `oc-app-desktop` `openclaw-dashboard/apps/desktop/{CONTEXT,BUILD,tech-stack}.md`
- `oc-app-ios` `openclaw-dashboard/apps/ios-whisper/{CONTEXT,BUILD,tech-stack}.md`
- `oc-design` `openclaw-dashboard/design/{DESIGN-LANGUAGE.md,components.md,tokens.json}` + smoke `tests/smoke/design-tokens.sh` `design-compliance.sh` + `design-compliance.md`
- `oc-layered-load` `openclaw-dashboard/docs/LAYERED-LOAD-ORDER.md`
## How to get to it (user POV)
- Read `openclaw-dashboard/CONTEXT.md` then the tab/settings folder `CONTEXT.md`. Design: `openclaw-dashboard/design/DESIGN-LANGUAGE.md`; smoke `openclaw-dashboard/tests/smoke/design-tokens.sh` and `design-compliance.sh`. Desktop/iOS shells via `apps/desktop` and `apps/ios-whisper` (spec until src exists).
## Driving it with verify-sai
- **Tokens.** ::exec openclaw-dashboard/tests/smoke/design-tokens.sh
- **Design.** ::exec openclaw-dashboard/tests/smoke/design-compliance.sh
- **Tab files.** ::exists openclaw-dashboard/tabs/chat-room/CONTEXT.md openclaw-dashboard/apps/desktop/CONTEXT.md
## Gotchas
- Stack names in BUILD.md are experiment inputs, not parent-app decisions. Chat tab is immersive-game mode; other tabs share the shell aesthetic. Missing `apps/desktop/src` is expected; design smoke is schema-level until src exists.
