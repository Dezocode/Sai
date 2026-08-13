# OpenClaw TRIAGE consumer (bounded)

OpenClaw on Hostinger must load `TRIAGE.yaml` and `policy.yaml` for any
Runtime Intelligence background action.

## Normalization
1. Dedupe by `event_id`.
2. Resolve repo/PR/head SHA (refuse unintegrated patches).
3. Classify T0–T5.
4. Persist to `/opt/sai/runtime-intelligence/state/runtime-intel.db`.
5. Act only within `allowed` verbs in `policy.yaml`.

## Hard stops
- T5 human-only → notify only, no code mutation.
- T4 without explicit capacity evidence → refuse.
- Merge/force-push/mark-ready → refuse and record finding.
