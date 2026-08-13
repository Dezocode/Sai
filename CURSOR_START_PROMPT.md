# Cursor Cloud Start Prompt — SAI Quality OS Phase 0

You are operating inside the canonical SAI repository. The repository already contains an ICM agent coordination framework. **Do not replace it, create a parallel agent-governance system, or rewrite existing human/agent work.** Integrate this Phase 0 bundle additively.

## Mission

Build and verify the SAI Quality Operating System before writing any product feature or UI.

Read, in order:

1. existing repository `AGENTS.md`
2. existing `.ai/CONTEXT.md`
3. existing `.cursor/rules/sai-coordination.mdc`
4. this file
5. `MASTER_EXECUTION.md`
6. `PSTACK_INTEGRATION.md`
7. `SCALABILITY_CONTRACT.md`
8. `.cursor/skills/sai-quality-os/SKILL.md`
9. `.sai-quality/gates.json`
10. `.sai-quality/policies/quality-policy.json`

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
- Existing debt may be baselined only at the dedicated baseline gate, with evidence and a ratchet that forbids regression.
- Third-party tools are installed from official sources only, resolved once to a concrete version/digest, then pinned in `.sai-quality/toolchain.lock.json`.
- Do not use mutable `latest` in committed CI or runtime configuration.
- Never vendor third-party source into the SAI product tree merely to make setup convenient.
- Every gate rechecks all prior FAST invariants. Every third gate and the final unlock run DEEP cumulative verification.
- If a gate fails three times with the same approach, stop that approach, write evidence, change strategy or escalate per pstack completion semantics.
- Security-sensitive uncertainty blocks progress; do not reason around it.

## Build loop

For each gate:

1. understand prerequisites;
2. inspect canonical owners and existing implementation;
3. make the smallest additive change;
4. run the gate's build actions;
5. run its verification;
6. run cumulative FAST verification;
7. at deep checkpoints run cumulative DEEP verification;
8. record evidence;
9. commit atomically under existing SAI ICM conventions;
10. continue only after PASS.

Use:

```bash
python3 scripts/qualityctl.py build --through G15
```

When an external tool requires environment-specific setup, implement the adapter, resolve/pin the official version, and continue. Do not replace the tool with an LLM judgment.

## Final unlock

Only after all required gates pass:

```bash
python3 scripts/qualityctl.py unlock
```

The unlock command must itself run the fault-injection suite and deep cumulative checks. If it fails, product development remains locked.

End with the exact pstack-style completion state: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`, followed by the evidence paths and next safe action.
