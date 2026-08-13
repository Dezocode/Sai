# Integration with Existing SAI Repository

This bundle was designed against the current repository shape where:

- `.ai/` is the ICM coordination/memory/run system;
- `.cursor/rules/sai-coordination.mdc` is an existing always-applied coordination rule;
- `.github/workflows/agent-audit.yml` enforces ICM metadata/handoffs/scaffold safety;
- `openclaw-dashboard/` is existing governance/agent infrastructure, not SAI product code;
- product application code has not yet been established.

Therefore this bundle:

- does not replace `AGENTS.md`;
- does not replace `.ai/`;
- does not replace `agent-audit.yml`;
- adds one Cursor rule (`95-sai-quality-os.mdc`, glob-scoped, not alwaysApply);
- adds separate quality workflows (verify `--through G03`; checkout pinned by SHA);
- adds `.sai-quality/` as the code-governance control plane, with docs under `.sai-quality/docs/`;
- treats future product roots as reserved while locked;
- does not outrank ICM or the `openclaw-dashboard/` prototype boundary (DR-20260724).

If the repo changes before installation, Cursor must reconcile additive paths through the architecture registry rather than blindly overwrite files.
