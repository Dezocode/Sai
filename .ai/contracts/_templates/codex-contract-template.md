# Codex Desktop contractor contract template

Use with `scripts/agent-contract-scaffold --runtime codex`.

## Runtime-specific notes

- **primary_runtime:** `codex-desktop`
- **Capability survey:** Codex Desktop tools; read `CODEX.md` first
- **Verify command:**
  ```bash
  SAI_AGENT_ID=<ctr-agent-id> scripts/agent-verify-caps \
    --tools-file .ai/agents/<name>/runtimes/codex/tools.json \
    --environment codex-desktop
  ```
- **Automation profile:** `runtimes/codex/automation/profile.md` — session-driven
- **Invoke:** Open repo in Codex Desktop; read `CODEX.md` → `AGENT.md`

## ONBOARDING focus

1. Enumerate Codex Desktop capabilities relevant to contract scope.
2. Ask owner approval for each before adding to `runtimes/codex/tools.json`.
3. Document session-driven automation in `hooks.json`.
4. Persona gate requires live demonstration of verified Codex tools.

## Branch pattern

`proj/<project-slug>/<ctr-agent-id>/<task-slug>`

Example: `proj/feature-plugin/ctr-code-beta1/api-layer`
