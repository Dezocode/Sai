# Verification — symlink containment hardening

## Protocol checks (workspace main @ 8fbacb7)

- `git fetch origin main` — OK; HEAD matches origin/main
- `scripts/agent-report flush` — no queued deliveries (1 SYNC event queued by agent-sync-drive)
- `scripts/verify-agent-audit origin/main..HEAD` — OK
- `scripts/verify-semantic-hierarchy` — OK
- `scripts/agent-sync-drive` — pending (SAI_DRIVE_REMOTE unset)
- `scripts/agent-init` — AGENT-INIT: PASS

## PR #10 symlink escape (745c686)

Reproduced: `guard_normalize_path` python fallback used `os.path.abspath`, which does not follow existing symlinks. On macOS (Codex Desktop), `.ai/agents/<slug>` symlinks passing prefix checks could write outside `.ai/agents/`.

Fix: use `os.path.realpath(..., strict=False)` in python fallback (GNU `realpath -m` already follows symlinks).

## Post-fix verification (branch cursor/agent-initialization-compliance-a9c9)

```
verify-scaffold-safety: OK (includes symlink-escape regression)
verify-semantic-hierarchy: OK
verify-agent-audit origin/main..HEAD: OK
```

## CI coherence

- `main` @ 8fbacb7: `agent-audit.yml` lacks `verify-scaffold-safety` (PR #10 adds it)
- PR #10 `icm-enforcement`: pass on GitHub Actions
- `monaecode/Sai`: `agent-audit` workflow active (2 successful runs)

## gh authentication

Valid in this cloud VM (`gh auth status` — cursor account). CTO HANDOFF noted invalid gh on Codex Desktop host; Saul must re-auth locally.
