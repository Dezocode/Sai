# BUILD — Secrets settings panel

## Phase 0: Doctrine + matrix (scaffold — PR #45)

1. Maintain [secrets-security.md](../../docs/secrets-security.md) as controlling spec
2. Keep [auth-matrix.md](../../docs/auth-matrix.md) status columns updated — **never values**
3. Wire smoke: `tests/smoke/secrets-compliance.sh`

## Phase 1: VPS secret store (Alfred on Hostinger)

1. Create `/etc/openclaw/sai.env` from schema (0600, root-owned)
2. Template `openclaw.json` uses `${ENV_VAR}` references only
3. Document in `.ai/runs/<task-id>/04_verify/output/secrets-store.txt` — paths only

## Phase 2: Dashboard UI

1. Route `/settings/secrets` — `SecretSlotList` from design system
2. Each row: provider icon, env name, status, last rotated — **masked value `••••`**
3. Copy-to-clipboard for values: **disabled**
4. Link to `/settings/auth` for OAuth Connect flows

## Phase 3: Config mirror guard (A7)

1. `config-expert` rejects JSON5 with literal tokens (regex gate)
2. Dashboard config tab shows `${VAR}` placeholders only

## Phase 4: Rotation SOP

1. User clicks Rotate → Telegram MCQ to dezocode
2. On approval: Alfred rotates on VPS, updates auth-matrix status + `last_rotated`
3. Post `[SAI][CHANGE][task-id]` — no secret values in message

## Phase 5: Verify

```bash
openclaw-dashboard/scripts/verify-secrets-compliance.sh
openclaw-dashboard/tests/smoke/secrets-compliance.sh
```

Evidence in `fulfillment-evidence.md`.
