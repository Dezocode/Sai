---
name: sai-quality-os
description: Build, verify, repair, and unlock SAI Phase-0 quality infrastructure before product development.
---

# SAI Quality OS Skill

## Preamble

```bash
python3 scripts/qualityctl.py init
python3 scripts/qualityctl.py status
```

Read `MASTER_EXECUTION.md`, `PSTACK_INTEGRATION.md`, `.sai-quality/gates.json`, and `.sai-quality/policies/quality-policy.json`.

## Workflow

PLAN -> inspect existing owners -> BUILD one gate -> VERIFY gate -> cumulative FAST -> DEEP checkpoint when required -> evidence -> atomic ICM handoff -> next gate.

For a failing gate, follow `RALPH_REPAIR_PROTOCOL.md`. Three same-strategy failures means BLOCKED, not threshold weakening.

Use open-source tools as engines. Do not replace deterministic scanners with an LLM review. LLM review may explain findings or propose repairs, never manufacture a PASS.

Before creating a path, consult `.sai-quality/architecture/registry.json` and search the repo for existing responsibility. New architectural roots require registry change plus architecture verification.

Final completion requires `python3 scripts/qualityctl.py unlock` and a valid `.sai-quality/FEATURES_UNLOCKED.json` certificate.
