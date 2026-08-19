# Live Cloud Agent environment

Recorded 2026-08-19 from `environment-info` on run `bc-01a01c62-2904-7567-b237-4ba571eafd30`. Re-read the Cursor Cloud `environment-info` tool before treating these IDs as current.

| Field | Value |
|---|---|
| Name | dezocode/sai |
| Source | Personal (dashboard-managed, not a repo file) |
| Environment ID | [6f2ece39-800a-11f1-ba66-0e7d0216e441](https://cursor.com/dashboard/cloud-agents/environments/e/6f2ece39-800a-11f1-ba66-0e7d0216e441) |
| `environmentJsonPath` | null (DB-managed) |
| Repo | `github.com/dezocode/sai` |
| Egress | unrestricted |
| Chrome | `/usr/bin/google-chrome` on this image |

`environment.json` is owner-restricted for personal environments. This agent cannot dump the saved install/start scripts. Precedence is still: committed `.cursor/environment.json` wins over personal and team dashboard configs.

## Do not commit `.cursor/environment.json`

A repo file would replace the personal environment for every Cloud Agent on that revision. Decision 0004 already rejected stuffing plugins into `environment.json` (the schema has no `plugins` key). Skills and plugins load from git. They do not need an install script.

To change install/start, use the dashboard Save flow after `propose-environment-json`. Do not snapshot or trigger a draft build from a skills-only change.

## What "live" means for this task

- Skills and rules become live on the next Cloud Agent whose checkout includes this commit.
- This session cannot hot-load `/lauren-mode` into its own `/` picker.
- Recurring system builds on the personal environment may show `SKIPPED`. That is the dashboard scheduler, not a skills failure.
