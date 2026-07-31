# Auth hub — settings/auth

**Deliverable:** A11 (A2 first-pass stub)  
**Route:** `/settings/auth`

## Provider tiles

| Provider | Status | Required | Action |
|---|---|---|---|
| GitHub | `Pending` | Yes | OAuth App → JWT session |
| Sign in with Apple | `Pending` | Optional | Apple OAuth |
| **Composio Telegram** | `Pending` | Yes (A2) | Connect Link → dashboard toolkit |
| **Composio Google Drive** | `Pending` | Yes (A2) | Connect Link → Drive mirror |
| **Composio Gemini/Notebook** | `Pending` | Yes (A2) | Connect Link → export/import |
| OpenClaw Gateway | `Pending` | Yes | Token / pairing QR |

Status values: `Connected` | `Pending` | `Blocked`

## Implementation notes (A2 stub)

- This is a scaffold; the actual desktop UI will render these tiles from the auth matrix API.
- Each tile links to its provider flow.
- OAuth completion is handled by the VPS browser MCP and Composio callback.
- 100% availability gate: if Gateway is healthy and a required provider is `Blocked`, show a dashboard warning and queue a Telegram MCQ to dezocode.

## Verification

- [ ] `auth-matrix.md` updated status-only.
- [ ] `openclaw-dashboard/scripts/verify-secrets-compliance.sh` PASS.
- [ ] Live OAuth smoke test in staging after dezocode toolkit approval.
