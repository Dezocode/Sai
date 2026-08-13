---
name: sai-quality-os
description: Build and verify SAI Phase-0 quality infrastructure through G03. G04+ is deferred.
---

# SAI Quality OS Skill

## Preamble

```bash
python3 scripts/qualityctl.py init
python3 scripts/qualityctl.py status
```

Read `.sai-quality/docs/MASTER_EXECUTION.md`, `.sai-quality/docs/PSTACK_INTEGRATION.md`, `.sai-quality/gates.json`, and `.sai-quality/policies/quality-policy.json`.

## Executable slice

Run only through G03 unless co-founders have explicitly approved G04 tool pinning:

```bash
python3 scripts/qualityctl.py build --through G03
```

`build --through G15` must stop at G04 with `DEFERRED` (exit 3). Do not pin/install Semgrep, Trivy, Gitleaks, SonarQube, Dependency-Track, or Renovate to clear that deferral.

## Workflow

PLAN -> inspect existing owners -> BUILD one gate -> VERIFY gate -> cumulative FAST -> DEEP checkpoint when required -> evidence -> atomic ICM handoff -> next gate.

For a failing gate, follow `.sai-quality/docs/RALPH_REPAIR_PROTOCOL.md`. Three same-strategy failures means BLOCKED, not threshold weakening.

Do not replace deterministic scanners with an LLM review. Do not call `qualityctl unlock` until G04–G15 are approved and actually execute those tools.
