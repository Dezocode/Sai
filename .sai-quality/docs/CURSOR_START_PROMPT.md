# Cursor Cloud Start Prompt — SAI Quality OS Phase 0

You are operating inside the canonical SAI repository. The repository already contains an ICM agent coordination framework. **Do not replace it, create a parallel agent-governance system, or rewrite existing human/agent work.** Integrate this Phase 0 bundle additively.

## Mission

Verify the SAI Quality Operating System **executable slice (G00–G03)** before writing any product feature or UI. **Do not** pin, download, or stand up third-party quality tools (Semgrep, Trivy, Gitleaks, SonarQube, Dependency-Track, Renovate, Scorecard) unless a co-founder has explicitly approved G04.

Read, in order:

1. existing repository `AGENTS.md`
2. existing `.ai/CONTEXT.md`
3. existing `.cursor/rules/sai-coordination.mdc`
4. this file
5. `.sai-quality/docs/MASTER_EXECUTION.md`
6. `.sai-quality/docs/PSTACK_INTEGRATION.md`
7. `.sai-quality/docs/SCALABILITY_CONTRACT.md`
8. `.cursor/skills/sai-quality-os/SKILL.md`
9. `.sai-quality/gates.json`
10. `.sai-quality/policies/quality-policy.json`
11. `.ai/shared/memory/decisions/0005-quality-os-control-plane.md`

Then initialize:

```bash
python3 scripts/qualityctl.py init
python3 scripts/qualityctl.py status
```

## Hard rules

- `FEATURES_LOCKED` means exactly that. Do not implement product code, UI, child flows, parent flows, judge behavior, messaging, education, or application features.
- One canonical path per responsibility. Search before create.
- New architectural roots require registry ownership and a passed architecture gate.
- Never silently weaken a threshold, add an ignore, suppress a finding, or baseline new debt to make a gate pass.
- Do not use mutable `latest` in committed CI or runtime configuration.
- Never vendor third-party source into the SAI product tree merely to make setup convenient.
- If a gate fails three times with the same approach, stop that approach, write evidence, change strategy or escalate.
- Security-sensitive uncertainty blocks progress; do not reason around it.
- G04+ `DEFERRED` is success of the current slice, not a prompt to install tools.

## Build loop

Use:

```bash
python3 scripts/qualityctl.py build --through G03
```

If you run `--through G15` (or the default is later changed), stop at G04 `DEFERRED` (exit 3). Do **not** call `qualityctl unlock`.

End with the exact pstack-style completion state: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`, followed by the evidence paths and next safe action.
