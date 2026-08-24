# Settings: Secrets & credential structure

| Field | Value |
|---|---|
| **Deliverable** | A11 (extends auth hub) |
| **Security doctrine** | [secrets-security.md](../../docs/secrets-security.md) |
| **Matrix** | [auth-matrix.md](../../docs/auth-matrix.md) |
| **Desktop route** | `/settings/secrets` |
| **VPS schema** | [secrets-store.schema.json](../../../.ai/agents/alfred/runtimes/openclaw/gateway/config/secrets-store.schema.json) |

## Owner requirement

PR #45 **controls** all secret structure for OpenClaw + dashboard:

- Env var **names** and store paths documented in Git
- Secret **values** only on VPS (Hostinger) or platform keychains
- Dashboard shows masked status — never plaintext export
- Rotation requires human MCQ (Telegram + Slack)

## UI surfaces

| Panel | Content |
|---|---|
| **Secret slots** | Env name, provider, status dot, last rotated |
| **Store map** | Which VPS path holds which provider (read-only diagram) |
| **Compliance** | Last `verify-secrets-compliance.sh` result |
| **Rotation log** | ICM task-ids for rotation events (no values) |

## Dependencies

- A0 Gateway bootstrap (`/etc/openclaw/sai.env` template)
- A11 Auth hub (OAuth flows)
- `secrets-security.md` + smoke gates

Build: [BUILD.md](./BUILD.md)
