# SAI Phase 0 Quality OS — Cursor Build Bundle v1.0.0

This bundle is designed to be extracted at the root of `Dezocode/Sai` **without replacing the existing ICM agent-governance system**.

Its purpose is to build a self-policing, recursively verified software factory **before any SAI product feature or UI is permitted**.

## Non-negotiable outcome

Until Phase 0 passes, `.sai-quality/FEATURES_LOCKED` remains present and product roots (`apps/`, `services/`, `packages/`, `evals/`, `infrastructure/`) may contain only documentation or placeholders. The Cursor skill and CI workflow both enforce this.

Phase 0 is complete only when:

1. canonical architecture ownership is machine-readable and validated;
2. dependency direction can be enforced for every enabled language adapter;
3. quality/security/supply-chain scanners are pinned and reproducible;
4. central health metrics and ratchets are available;
5. CI and scheduled deep-health monitoring are installed;
6. deliberate fault injection proves the guardrails fail closed;
7. recursive checks have passed from Gate G00 through G15;
8. `qualityctl unlock` independently re-runs the unlock contract and emits signed-by-evidence state.

## Start

Give Cursor `.sai-quality/docs/CURSOR_START_PROMPT.md` or run `/sai-quality-build`.

The **executable slice is G03**. G04+ is deferred until co-founder approval of tool pinning (decision 0005).

```bash
python3 scripts/qualityctl.py init
python3 scripts/qualityctl.py status
python3 scripts/qualityctl.py build --through G03
```

`build --through G15` must print `DEFERRED` at G04 and exit 3. Do not run `qualityctl unlock`. `FEATURES_LOCKED` remains.

`build` never marks a gate passed because a file exists. Each executable gate has verification commands and evidence. A failing gate remains failing; after three unsuccessful same-gate attempts the orchestrator blocks and requires a changed strategy.

## Design principle

Open-source tools do the generic analysis. SAI-owned code only expresses SAI-specific invariants and orchestrates evidence. Do not reimplement Semgrep, Trivy, Gitleaks, SonarQube, dependency-cruiser, Knip, jscpd, Renovate, OpenSSF Scorecard, or Dependency-Track.
