# Cursor runtime — optional Saul adapter

Cursor is not Saul's primary runtime. `@saul` may attach the runtime-neutral
profile, but Cursor capability surveys must write only to a future
`runtimes/cursor/tools.json` and must never overwrite the canonical Codex
inventory at `runtimes/codex/tools.json`.
