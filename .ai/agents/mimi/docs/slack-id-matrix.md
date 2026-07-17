# Slack ID matrix — SAI workspace (Mimi's canonical copy)

Standing rule (monaecode, 2026-07-17): **every Mimi post ends with a tag
line** using `@agentname` from this matrix paired with the real
`<@USER_ID>` mention — plain `@name` alone notifies no one (Cora P1,
review `20260717-0323`).

| Identity | @agentname | Real mention | Notes (honest routing) |
|---|---|---|---|
| monaecode (principal, co-founder) | `@monaecode` | `<@U0BGNS7F0T1>` | Human; always tagged on Mimi reports |
| dezocode (co-founder) | `@dezocode` | `<@U0BHYH0NMCY>` | Human; CTO-gate + merge routing |
| Sai (CEO agent, `ceo`) | `@sai` | `<@U0BH7V4145S>` | Posts via the Cursor automation bot; no dedicated Sai Slack user registered |
| Cora (Contract Admin, `ctr-admin`) | `@cora` | `<@U0BH7V4145S>` | Same Cursor bot as Sai — name Cora explicitly in text so the automation routes it |
| Saul (CTO agent, `dezo-sec-codex1`) | `@saul` | `<@U0BH6EGUEQ3>` | Posts via the Codex bot; escalation human is `@dezocode` |
| Mimi (`mimi`) | `@mimi` | `<@U0BH5QE5B8B>` | Posts via the Claude bot |

## Post-ending tag line format

```
Tags: @monaecode <@U0BGNS7F0T1> · @sai <@U0BH7V4145S> · @saul <@U0BH6EGUEQ3>
```

Include exactly the identities the post concerns (principal always).
Update this matrix only with evidence (a message actually posted by that
bot/user); registry (`.ai/agents/registry.json`) remains the identity
authority.
