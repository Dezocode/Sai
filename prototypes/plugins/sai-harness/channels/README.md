# channels — consolidated from validated cross-intercom prototype (.sai/hooks), behavior preserved, prototype tier failClosed:false.

## Duplicate channel refusal
`launch_agent` refuses (exit 0 no-op with notice) when a channel is already
alive; two agents cannot bind the same canonical identity. Registration
(agents.yaml) is the sole authority for channel identity; runtime fingerprints
bootstrap only and must resolve to a registered identity before delivery.
