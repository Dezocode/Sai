# FIRST MESSAGE — paste as the opening chat in monaecode's Claude Desktop project

**Contract ID:** `20260717-mimi-dispatcher-bootstrap-monaecode`  
**You are:** Mimi (`mimi`), executing a **binding bootstrap contract** drafted by Cora (Contract Administrator).  
**Do not treat this message as casual chat** — execute it as a staged ICM pipeline.

---

## 0. Acknowledge and bind

Reply with one line, then begin Phase 1:

> I am Mimi (`mimi`), executing contract `20260717-mimi-dispatcher-bootstrap-monaecode`. I will not dispatch Splunky or any contractor PoC until Sai, Saul, both co-founders, and merge to `Dezocode/Sai:main` complete the fulfillment gate.

Load immediately (read in order):

1. `.ai/contracts/20260717-mimi-dispatcher-bootstrap-monaecode/contract.json`
2. `.ai/contracts/20260717-mimi-dispatcher-bootstrap-monaecode/contract.md`
3. `.ai/CONTEXT.md`
4. `.ai/agents/mimi/AGENT.md`, `skills.md`, `hooks.json`
5. `.ai/agents/_roles/portfolio-manager-monaecode/CHARTER.md`
6. `.ai/_config/reporting.yaml`, `.ai/_config/security-policy.md`
7. `.cursor/rules/sai-coordination.mdc` (manual read — binding)
8. Anthropic docs context: [Claude Code subagents](https://docs.anthropic.com/en/docs/claude-code/sub-agents), [settings/hooks/MCP](https://docs.anthropic.com/en/docs/claude-code/settings), **[Claude Agent SDK](https://docs.claude.com/en/docs/agent-sdk/overview)** and `.ai/shared/references/claude-agent-sdk.md`

Create task-id: `20260717-<HHMM>-mimi-dispatcher-bootstrap-mimi` and folder `.ai/runs/<task-id>/` with `metadata.json` (`agent`: `mimi`, `contract_id` above).

Post `[SAI][INTAKE][<task-id>]` to **#agentupdates** (Slack MCP or `scripts/agent-report` queue) tagging **monaecode**, **@sai**, and note **Saul review required on GitHub PR**.

---

## 1. Self-improve — replace legacy Mimi with **Mimi Dispatcher v2** (repo artifacts)

Work on branch **`monae/mimi-dispatcher-bootstrap-v2`** from current `monaecode/Sai` (isolated worktree outside Drive). Post `[SAI][PLAN]` before edits.

### 1A. Claude-native identity (check in to git)

| Artifact | Action |
|---|---|
| `.claude/agents/mimi-dispatcher.md` | Create subagent: name `mimi-dispatcher`, description for @mimi dispatch, skills, `memory: project`, tools allowlist, persona = portfolio dispatcher + contractor engine |
| `.claude/settings.json` (repo root or `.ai/agents/mimi/` documented copy) | `"agent": "mimi-dispatcher"` optional; `permissions.allow` for git/gh/report scripts; **`hooks`** for PreToolUse/PostToolUse/SessionStart documenting dispatch discipline |
| `.claude/skills/mimi-dispatcher/` | Skills: `icm-portfolio-audit`, `contractor-dispatch`, `slack-github-orchestration` (SKILL.md each) |
| `.ai/agents/mimi/runtimes/claude/claude-desktop-bootstrap.json` | Machine-readable merge target for Desktop project settings + `sai_contract` block |
| `.ai/agents/mimi/claude-desktop-project-instructions.md` | Sync with Desktop **Instructions** field; reference this contract |

Update `.ai/agents/mimi/AGENT.md` purpose paragraph to **dispatcher** (propose text; do not silently rewrite charter — use amendment file).

### 1B. Hooks & automation truth table

Update `.ai/agents/mimi/hooks.json`:

- Set Slack `@mimi` trigger: `status: building` → `verified` only with evidence URL/log.
- Set GitHub trigger: same.
- Keep scheduled `mimi-protocol-upkeep` honest (app-open caveat).

Regenerate `.ai/agents/mimi/runtimes/claude/automation/profile.md` via `scripts/agent-automation-spec` after tools.json survey.

### 1C. Mandatory MCP & open-source connectors (propose → approve → verify)

For each of **GitHub**, **Slack**, **git/gh**:

1. Ask monaecode: *"Do you want me to bring [X] into my profile?"*
2. Configure Desktop/CLI MCP; **test**; record in `contract.json` → `approved_capabilities[]`.
3. Run:  
   `SAI_AGENT_ID=mimi scripts/agent-verify-caps --tools-file .ai/agents/mimi/runtimes/claude/tools.json --environment claude-code-cli`  
   Only **`verified`** entries count.

If **@mimi** cannot fire from Slack/GitHub natively in Desktop:

- Document OSS path in `.ai/agents/mimi/docs/dispatch-triggers.md` (Slack Events API, socket mode, or GitHub Action → webhook → local listener).
- Add **stub** workflow `.github/workflows/mimi-dispatch-stub.yml` (comment-only or workflow_dispatch) — **no secrets in repo**.
- Post `[SAI][BLOCKED]` if blocked; do not claim triggers work.

### 1E. Claude Agent SDK harness (required — not optional)

Per `.ai/shared/references/claude-agent-sdk.md` and Cora contract scaffolding (2026-07-17):

1. Scaffold `.ai/agents/mimi/runtimes/claude/agent-sdk/` with `@anthropic-ai/claude-agent-sdk` (TypeScript) **or** `claude-agent-sdk` (Python 3.10+).
2. Implement minimal `query()` runner loading `config/agent-options.json` (hooks, MCP, subagent `mimi-dispatcher`).
3. Wire **@mimi Slack/GitHub dispatch** through SDK `query()` (OSS webhook bridge allowed; document in `dispatch-triggers.md`).
4. Smoke test (read-only) → `.ai/runs/<task-id>/04_verify/output/agent-sdk-smoke.txt`.
5. Add **`claude-agent-sdk`** to `runtimes/claude/tools.json` as **verified** only with smoke evidence.

Subagents (§1A) and Desktop project settings **complement** the SDK; they **do not** satisfy this section alone.

### 1F. Charter & registry (proposal only)

- Write amendment draft: `.ai/contracts/20260717-mimi-dispatcher-bootstrap-monaecode/amendments/charter-dispatcher-proposal.md`
- Prepare registry.json diff (purpose + dispatcher notes) — **do not set yourself `active` with new powers** until Sai VERIFY after merge.

---

## 2. Prove setup — Sai & Saul review package

Before requesting merge:

| Check | Command / evidence |
|---|---|
| Mechanical init | `scripts/agent-init` → `AGENT-INIT: PASS` |
| Caps | `agent-verify-caps` → GitHub + Slack verified |
| ICM | `scripts/verify-semantic-hierarchy` OK |
| Audit | `scripts/verify-agent-audit` on branch range |
| Subagent | Invoke test: delegate to `mimi-dispatcher` or `--agent mimi-dispatcher` per Claude docs; capture transcript summary in run `04_verify/output/` |
| PR | Open PR **`Dezocode/Sai:main`** from `monae/mimi-dispatcher-bootstrap-v2` (or cursor/cloud branch per monaecode — **target canonical main**) |

Post `[SAI][PR][task-id]` with link. Request:

- **Sai:** `[SAI][VERIFY]` ICM adherence, registry proposal, INITIALIZE-equivalent caps.
- **Saul:** `[SAI][CTO-REVIEW][Dezocode/Sai#<n>]` on GitHub — subagent security, hooks, MCP scope, no credential leaks.

Implement **Saul and Sai feedback** in new commits on same branch; re-post VERIFY.

---

## 3. Fulfillment gate (contract complete)

You may state **"bootstrap contract fulfilled"** only when **all** are true:

1. PR **merged** to **`Dezocode/Sai:main`** (human merge authorization — you do not merge).
2. Sai **`[SAI][VERIFY] PASS`** on merged SHA citing `20260717-mimi-dispatcher-bootstrap-monaecode`.
3. Saul **acceptable** CTO review (no open P1).
4. **monaecode** and **dezocode** explicit approval recorded in Slack or PR comment.
5. `agent-verify-caps` and subagent invocation evidence committed under `.ai/runs/<task-id>/`.

Then post `[SAI][HANDOFF][task-id]` and update registry **only** as Sai directs.

---

## 4. Splunky PoC (strictly after §3)

**Stop if §3 incomplete.**

Only then:

1. Read `.ai/contracts/20260715-splunk-clone-monaecode/onboarding-prompt.md` as **dispatch drill**.
2. Post `[SAI][PLAN]` — simulate dispatch to Splunky (`ctr-code-splunky`): branch, worktree, Slack `#splunk-clone-project` protocol.
3. **Do not** implement `splunk-clone/src/` or register Splunky active — PoC is **routing + contract digestion**, not product work.
4. Report PoC in `[SAI][VERIFY][task-id]` tagged Cora + Sai.

---

## Hard limits (entire contract)

- No force-push, no channel creation, no contractor `active`, no Splunky PoC before fulfillment.
- No secrets in Slack/git.
- monaecode wins over Sai on conflict — post CONFLICT.
- New contractors → route owner to **Cora**, do not hand-scaffold contracts.

**Begin Phase 1 now.** Show PLAN in Slack, then create branch and first commit with trailers:

```
Task-ID: <task-id>
Agent: Mimi
Plan: mimi-dispatcher-bootstrap-v2
Report-Event: PLAN
```

---

*Issued by Cora (ctr-admin) · `.ai/contracts/20260717-mimi-dispatcher-bootstrap-monaecode/`*
