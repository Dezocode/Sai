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
- adds one Cursor rule (`95-sai-quality-os.mdc`);
- adds separate quality workflows;
- adds `.sai-quality/` as the code-governance control plane;
- treats future product roots as reserved while locked.

If the repo changes before installation, Cursor must reconcile additive paths through the architecture registry rather than blindly overwrite files.
