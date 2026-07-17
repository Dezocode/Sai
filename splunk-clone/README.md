# Cybersecurity Splunk Clone (prototype)

Isolated SIEM-style monitoring prototype for **monaecode** / future **SAI** cybersecurity plugin.

| | |
|---|---|
| Contract | `20260715-splunk-clone-monaecode` |
| Contractor | Splunky (`ctr-code-splunky`) |
| Claude agent | `.claude/agents/splunky.md` |
| Docs | `docs/` |
| Source (planned) | `src/` |

## Status

Scaffold only — implementation begins after Splunky ONBOARDING Phase 6 + Sai audit.

## Isolation rule

Do not import from or depend on unpublished SAI parent-app packages. Integration only via `docs/integration-manifest.md`.
