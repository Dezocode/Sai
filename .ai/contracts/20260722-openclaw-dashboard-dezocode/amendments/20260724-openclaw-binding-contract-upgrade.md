# Amendment: OpenClaw binding contract full upgrade (dezocode)

| Field | Value |
|---|---|
| **Date** | 2026-07-24 |
| **Authority** | dezocode — binding document must be fully upgraded before merge |
| **CEO gate** | `[SAI][VERIFY][20260724-0311-pr45-architecture-decision-ceo]` |
| **Applied by** | Cora (ctr-admin) |

## Requirement

Alfred's OpenClaw binding contract set must reflect DR-20260724, architecture
classification, Parts A–C lifecycle, and proposed-not-canonical stack boundary —
not only `contract.json` and product banners.

## Files upgraded

| File | Change |
|---|---|
| `contract.md` | Full rewrite — binding doc with DR, Parts A–C, stack status, reviewers |
| `first-message-to-openclaw.md` | DR first in load order; ack line; Part C vs Part A; A9 proposed stack |
| `first-prompt-attach-contract.md` | Full rewrite — lifecycle table, binding load order |
| `onboarding-prompt.md` | DR + architecture + Part B activation gate |
| `contract.json` | `binding_documents[]` manifest |

## Merge gate

Part A scaffold merge requires this amendment on PR branch + Saul confirm + cofounder M3/M4.
