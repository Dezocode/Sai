# Launch SAI Cloud Agents with `@cursor/sdk`

Canonical SDK skill: Cursor's `/sdk` plus [cursor.com/docs/api/sdk/typescript](https://cursor.com/docs/api/sdk/typescript). This note is only the SAI cloud launch shape so the agent inherits project skills and plugins.

## Cloud, not local

Always pass `cloud: { repos }`. Omitting both `local` and `cloud` silently selects local. Local will not open a PR and will not boot the Cloud Agent environment.

```typescript
import { Agent } from "@cursor/sdk";

const agent = Agent.create({
  apiKey: process.env.CURSOR_API_KEY!,
  model: { id: "composer-2.5" },
  cloud: {
    repos: [
      {
        url: "https://github.com/Dezocode/Sai",
        startingRef: "main",
      },
    ],
    autoCreatePR: true,
    skipReviewerRequest: true,
  },
});

try {
  const run = await agent.send(
    "Use /lauren-mode as a Custom Mode. Follow SAI ICM. Do not commit environment.json.",
  );
  if (run.supports("stream")) {
    for await (const event of run.stream()) {
      if (event.type === "assistant") {
        // observe only
      }
    }
  }
  const result = await run.wait();
  if (result.status === "error") {
    process.exit(2);
  }
} finally {
  await agent[Symbol.asyncDispose]();
}
```

## What the launched agent gets

Cloud agents clone `startingRef`, then load:

- `.cursor/settings.json` → pstack plugin (`/poteto-mode`)
- `.cursor/skills/lauren-mode/` → this Custom Mode
- `.cursor/rules/` → SAI coordination plus `pstack-models.mdc`
- `AGENTS.md` → Cloud-specific checks

They do **not** get the operator's `~/.cursor` skills or `/setup-pstack` home rule. That is why model routing is committed.

Inline `mcpServers` on `Agent.create` are not persisted across `Agent.resume`. Pass them again on resume.

## Traps

- Distinguish `CursorAgentError` (never started) from `result.status === "error"` (started, failed).
- Log `run.id` and `agent.agentId` before streaming. Cloud ids start with `bc-`. A `bc-` id is not a run id.
- Guard `run.supports("cancel")` and `run.supports("conversation")`.
- Set `skipReviewerRequest: true` in CI unless a human should be requested.
