# Runtime maturity rubric (proposed Layer 3 reference)

Research artifact only — **not** filed under `.ai/shared/references/` yet.
Intended to make scaffolding critiques objective before Grok (or any fourth
runtime) is added.

## Dimensions (score each primary suite 0–2)

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| **D1 Survey** | Empty / missing `tools.json` | Caps present but mixed unverified or wrong kinds | All primary caps `verified` with dated evidence |
| **D2 Automation honesty** | Wrong-runtime template (e.g. Cursor UI under Claude) | Generic “configure later” / delegated without stating mechanism | Names real mechanism or explicit none |
| **D3 Hooks truth** | Contradicts profile/registry | Partially filled scaffold text | Matches automation profile + registry |
| **D4 Harness extras** | Required extras missing (Claude SDK package/runner) | README/config stub only | Docs-complete harness + smoke when required |
| **D5 Entry router** | No Layer 0 path for primary runtime | Root router exists; agent README thin | Router + suite README + invoke instructions in registry |
| **D6 Non-primary stubs** | Silent empty dirs | README says non-primary | README lists missing files + “never copy caps” warning |

**Band:** High ≥10 · Medium 6–9 · Low ≤5 (max 12)

## Application snapshot (2026-07-22)

| Agent | D1 | D2 | D3 | D4 | D5 | D6 | Total | Band |
|---|---|---|---|---|---|---|---|---|
| sai (cursor) | 2 | 2 | 2 | 2 (N/A extras) | 2 | 1 | **11** | High |
| cora (cursor) | 2 | 1 | 0 | 2 | 2 | 1 | **8** | Medium |
| saul (codex) | 2 | 2 | 2 | 2 | 2 | 1 | **11** | High |
| mimi (claude) | 1 | 0 | 2 | 0 | 2 | 1 | **6** | Medium |
| alpha (claude) | 0 | 0 | 0 | 0 | 1 | 1 | **2** | Low |
| _(future grok)_ | — | — | — | — | 0 | — | **Absent** | — |

Notes:

- Cora drops from “High inventory” to **Medium** once honesty dimensions
  weight hooks/automation — inventory alone is not maturity.
- Mimi’s hooks are honest; automation profile file is not — D2=0 dominates.
- Claude D4 fails docs bar until package/`query()`/smoke exist.

## Use in contracts

Cora should refuse `primary_runtime` GO for contractors when D1+D2+D4 < 2
each on the primary suite (provisional agents may sit Low until ONBOARDING
completes, but must not claim advanced SDK/automation deliverables).
