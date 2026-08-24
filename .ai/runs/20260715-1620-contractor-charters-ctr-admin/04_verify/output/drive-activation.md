# Drive activation verification

**Date:** 2026-07-15
**Agent:** ctr-admin
**Environment:** cloud-agent VM

## Configuration status

| Check | Result |
|---|---|
| `SAI_DRIVE_REMOTE` set | **unset** — operator must configure rclone remote |
| `rclone` installed | checked at sync time |
| Extended mirror paths | contracts/, agents/*/memory/, projects/ implemented in `agent-sync-drive` |

## Sync test

When `SAI_DRIVE_REMOTE` is unset, `scripts/agent-sync-drive` records `pending` and
exits 0 per policy — Git work is never blocked.

```bash
# Operator setup (not committed):
export SAI_DRIVE_REMOTE="gdrive:SAI"
rclone config  # configure gdrive remote
scripts/agent-sync-drive --repo-key dezocode-sai
```

## Expected mirror after live sync

- `SAI/contracts/20260715-splunk-clone-monaecode/`
- `SAI/agents/ctr-admin/memory/`
- `SAI/agents/ctr-code-splunk1/memory/`
- `SAI/projects/splunk-clone/`

## Verification evidence

Run `scripts/agent-sync-drive` after push; SYNC event must show `pending` until
credentials configured. Never claim `synced` without checksum evidence.
