# Officer grants and human authority records

Tracked write authority for officers lives here. Git is durable truth.
`.git/sai-session.json` and an `Agent:` trailer are not sufficient after
`officer_grants.required_after_sha` (CTO-009).

```
.ai/authorizations/
  grants/     <- principal + task_id + paths (+ runtime)
  human/      <- co-founder grants that Cora must not auto-issue
```

A forged `Agent: ceo` commit without a matching grant in this tree fails
authorization replay.
