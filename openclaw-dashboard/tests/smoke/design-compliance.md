# Smoke test — design compliance

Alfred must PASS before UI PR merge.

## Checks

1. `design/tokens.json` validates as JSON
2. Every tab route imports `@/design-system/tokens` (grep gate)
3. No raw `#007acc`-style hex in `apps/desktop/src/tabs/` except token file
4. AppShell renders on all tab routes (visual snapshot optional)
5. iOS `DesignTokens.swift` exists and matches token count

## Command

```bash
openclaw-dashboard/tests/smoke/design-tokens.sh
```

Exit 0 when compliant; exit 1 with file:line violations.
