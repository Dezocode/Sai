# Pilot contract dogfood — splunk-clone

## Contract

- ID: `20260715-splunk-clone-monaecode`
- Principal: monaecode
- Isolation: prototype on `monaecode/Sai`
- Runtime: claude-code-cli

## Multi-contractor branch isolation

| Contractor | Branch | Status |
|---|---|---|
| ctr-code-splunk1 (Alpha) | `proj/splunk-clone/ctr-code-splunk1/pilot-intake` | claimed |
| ctr-code-splunk2 (slot) | `proj/splunk-clone/ctr-code-splunk2/ingest-pipeline` | claimed |

Same `project_slug`, unique `<contractor-agent-id>` — no CONFLICT.

## Slack channel approval flow

`#proj-splunk-clone` status: `pending_owner_approval` in
`.ai/projects/splunk-clone/coordination/slack-channel.json`.

Contract Admin must post BLOCKED/approval request; owner approves before channel use.

## Sai audit

Review: `contracts/20260715-splunk-clone-monaecode/reviews/20260715T162500Z-sai-audit.json`

Overall: `conditional_pass` — Alpha remains `provisional` until persona gate.

## PR contract review

Run after contractor branch exists with commits:

```bash
SAI_AGENT_ID=ctr-code-splunk1 scripts/agent-contract-pr-review \
  --contract-id 20260715-splunk-clone-monaecode \
  --branch proj/splunk-clone/ctr-code-splunk1/pilot-intake
```

Pilot dry-run on naming validation performed during implementation.
