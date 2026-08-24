# Cursor contractor contract template

Use with `scripts/agent-contract-scaffold --runtime cursor`.

## Runtime-specific notes

- **primary_runtime:** `cursor-cloud-vm` or `cursor-desktop`
- **Capability survey:** Cursor Settings → MCP; Cursor marketplace skills
- **Verify command:**
  ```bash
  SAI_AGENT_ID=<ctr-agent-id> scripts/agent-verify-caps \
    --tools-file .ai/agents/<name>/runtimes/cursor/tools.json \
    --environment cursor-cloud-vm
  ```
- **Automation profile:** `runtimes/cursor/automation/profile.md` via
  `scripts/agent-automation-spec`
- **Invoke:** `@<name>` in Cursor Desktop or Cloud Agent

## ONBOARDING focus

1. Enumerate Cursor MCP servers and marketplace skills for contract scope.
2. Ask owner approval for each before adding to `runtimes/cursor/tools.json`.
3. Configure `hooks.json` with Cursor rules and automation triggers.
4. Persona gate requires live demonstration of verified Cursor tools.

## Branch pattern

`proj/<project-slug>/<ctr-agent-id>/<task-slug>`

Example: `proj/splunk-clone/ctr-code-alpha1/auth-pipeline`
