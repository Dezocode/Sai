# Plan — Saul PR #54 remediation (agent initialization standards)

## Trigger

Saul CTO governance review (20260731-0310) published REQUEST_CHANGES on PR #54
at head `738379b` with four P1 inline findings.

## Findings and remediation

| # | Finding | Remediation |
|---|---------|-------------|
| 1 | macOS Bash 3.2 `${ROOT@Q}` portability in `verify-semantic-hierarchy` | Pass repo root via `SAI_REPO_ROOT` env + quoted heredoc |
| 2 | `validate-agent-event.py` does not load schema it claims to enforce | Load `.ai/shared/schemas/agent-event.schema.json` at startup; derive enums/required from schema |
| 3 | Two completed CEO runs remain `in_progress` | Set `status: completed` on `20260715-1620-*` and `20260715-2130-*` metadata |
| 4 | Historical malformed event rewritten in place | Append explicit HANDOFF correction event documenting original `--help` payload |

## Scope

No merge, close, or credential changes. Push to `cursor/agent-initialization-standards-9991`.

## Verification

- `scripts/verify-semantic-hierarchy`
- `scripts/verify-agent-audit origin/main..HEAD`
- `scripts/lib/validate-agent-event.py --self-test`
- `scripts/agent-init` (AGENT-INIT: PASS)
