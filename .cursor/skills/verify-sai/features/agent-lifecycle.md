# Agent lifecycle
A principal names an agent, binds a charter, initializes hooks and capabilities, scaffolds folders, and registers the agent before task work.
## Sub-features
- `init-protocol` `.ai/INITIALIZE.md` Phases 0–9; not initialized until Phase 9 report.
- `init-script` `scripts/agent-init` mechanical Phase 2; refuse fail; do not run in managed VMs to set hooksPath.
- `onboard-protocol` `.ai/ONBOARDING.md` contractor persona gate + Sai audit.
- `registry` `.ai/agents/registry.json` one row per agent; status `active`|`provisional`.
- `charter-ceo` `.ai/agents/_roles/ceo/CHARTER.md`
- `charter-secretary-dezocode` `.ai/agents/_roles/secretary-dezocode/CHARTER.md`
- `charter-secretary-monaecode` `.ai/agents/_roles/secretary-monaecode/CHARTER.md`
- `charter-portfolio` `.ai/agents/_roles/portfolio-manager-monaecode/CHARTER.md`
- `charter-ctr-admin` `.ai/agents/_roles/contract-administrator/CHARTER.md`
- `charter-ctr-base` `.ai/agents/_roles/contractor-base/CHARTER.md`
- `charter-ctr-code` `.ai/agents/_roles/contractor-coding/CHARTER.md`
- `charter-ctr-design` `.ai/agents/_roles/contractor-design/CHARTER.md`
- `agent-sai` `.ai/agents/sai/` CEO
- `agent-mimi` `.ai/agents/mimi/`
- `agent-saul` `.ai/agents/saul/`
- `agent-cora` `.ai/agents/cora/`
- `agent-alfred` `.ai/agents/alfred/` provisional OpenClaw administrator
- `agent-alpha` `.ai/agents/alpha/` provisional coding contractor
- `scaffold-agent` `scripts/agent-scaffold --name --agent-id --role-title --principal --purpose --charter [--primary-runtime cursor|claude|codex|openclaw]`
- `scaffold-memory` `scripts/agent-memory-scaffold --agent-id --folder [--contract-id]`
- `verify-caps` `scripts/agent-verify-caps --tools-file .ai/agents/<name>/tools.json [--environment …]`
- `automation-spec` `scripts/agent-automation-spec --agent-id --agent-name --role-title --principal --purpose`
- `runtime-suites` `.ai/agents/<name>/runtimes/{cursor,claude,codex,openclaw}/` capability suites.
- `agents-index` `.ai/agents/README.md` named-folder convention.
- `automation-specs` `.ai/agents/automation-specs/cursor-cloud-30d8.md` bootstrap automation record.
## How to get to it (user POV)
- New agent: execute `.ai/INITIALIZE.md`; contractor: `.ai/ONBOARDING.md` after contract first message.
- Attach `@<name>` in Cursor or open `CLAUDE.md`/`CODEX.md`/`OPENCLAW.md` then `AGENT.md`.
- Scaffold only via `scripts/agent-scaffold` / `agent-memory-scaffold`.
## Driving it with verify-sai
Preconditions: repo root.
- **Registry.** `python3 -m json.tool .ai/agents/registry.json`; every `folder` exists.
- **Setup gate.** `scripts/verify-agent-setup`; exit 0.
- **Scaffold reject.** `scripts/verify-scaffold-safety`; exit 0 (path traversal rejected).
- **Caps help.** `scripts/agent-verify-caps 2>&1 | head -1`; usage on missing `--tools-file`.
- **Proof.** `go run ./cmd/sai-verify relevant --path .ai/INITIALIZE.md --tool Read` lists `agent-lifecycle`.
## Gotchas
- Do not self-name; principal grants name and role title.
- Do not overwrite another runtime's `tools.json`.
- `scripts/agent-init` warns against managed Cloud VM hooksPath.
