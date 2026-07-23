# Scaffolding critique matrix (evidence snapshot)

Base: `Dezocode/Sai` `@8da8530` (+ this research run only).

## Legend

- **High:** primary suite has evidence-backed `tools.json` + honest automation
  narrative aligned to that runtime’s real mechanism.
- **Medium:** survey exists but advanced docs (e.g. Agent SDK harness) unmet,
  or mixed verified/unverified caps.
- **Low:** stub README, empty caps, or wrong-runtime automation template.

## Matrix

| Agent | Suite | Score | Top gaps |
|---|---|---|---|
| sai | cursor (primary) | High | Keep automation Tools list synced with `tools.json` |
| sai | claude / codex | Low | Intentional stubs; OK if README states non-primary |
| mimi | claude (primary) | Medium | Caps ok; Agent SDK package/runner/smoke missing vs `claude-agent-sdk.md` |
| mimi | claude/agent-sdk | Low | README+config only; no dispatch harness verified |
| mimi | cursor / codex | Low | Optional stubs |
| saul | codex (primary) | High | Model for honesty; still no unattended automation (correctly) |
| saul | cursor / claude | Low | Optional stubs |
| cora | cursor (primary) | High | Role-tailored caps; `hooks.json` automation still generic scaffold text |
| cora | claude / codex | Low | Generic README stubs |
| alpha | claude (primary) | Low | `capabilities: []`; Cursor-shaped automation profile; provisional |
| alpha | claude/agent-sdk | Low | Placeholder only |
| alpha | cursor / codex | Low | Generic stubs |
| _(none)_ | grok | **Absent** | No Layer 0 `GROK.md`, suite, enum, or templates |

## Doc vs enforcement mismatch

| Doc requirement | Enforcement today |
|---|---|
| Claude SDK layout with package + `query()` | Scaffold creates README/config only |
| Verified `claude-agent-sdk` capability | Manual; CI smoke optional via env flag |
| Runtime-specific automation profiles | `agent-automation-spec` Cursor-centric |
| Closed `primary_runtime` enum | Correctly blocks Grok until decision+schema |

## Target scaffolding depth (recommended rubric)

For each **primary** runtime suite, agents should eventually have:

1. `tools.json` with verified caps + evidence dates  
2. `automation/profile.md` naming the **real** mechanism (or explicit none)  
3. `hooks.json` truth table matching that profile  
4. Harness extras when docs require them (Claude Agent SDK; future Grok
   `.grok` inspect notes)  
5. Non-primary suites: stub README with missing-file checklist, not silence
