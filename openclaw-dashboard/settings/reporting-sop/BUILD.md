# BUILD — Reporting SOP settings

1. UI table: agent_id, last `[SAI][EVENT]`, channel, compliant Y/N.
2. Parser for #agentupdates → activity-ingest (coordinate tracking tab).
3. Violation banner when active agent silent > configurable threshold.
4. Link to `.ai/_config/reporting.yaml` (read-only mirror in dashboard).
5. Alfred automation: on registry add, append SOP row + Telegram verification task.

Public channels only — never display secrets or private channel content.
