# .sai structure benchmark

Generated: 2026-08-24T22:07:38.219111+00:00

Baselines: `.cursor` @ origin/main and `~/.agents`. Atomic CLI cloned shallow into ignored `bench/atomic/` (MIT © 2025 Bastani Inc.) — clone stays uncommitted; only this report lands.

| Dimension | .cursor @main | .agents | .sai | verdict |
|---|---|---|---|---|
| manifest | hooks.json (19 hook events) | *.<agent>.md flat files | hooks.json + harness provenance | .sai superset |
| hook implementations dir | hooks/ | — | hooks/ | matches .cursor |
| skills convention | skills/<name>/SKILL.md | skills/<name>/SKILL.md | skills/crosscomm/SKILL.md | matches both |
| rules dir | rules/ | — | (deferred) | add when a rule exists |
| settings | settings.json | — | (deferred) | prototype needs none yet |
| provenance/license block | absent | absent | present (Atomic MIT derivation) | .sai addition — keep |

## Actions adopted
- Single-source implementations under `.sai/hooks/`; `.cursor/hooks.json` delegates.
- Adopt `.agents`-style flat agent doc when a second persona joins the lane.
- Re-run whenever `.cursor` on main changes the hook schema.
