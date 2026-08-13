# Changes

- Orchestrator: argv via shlex (no shell=True); verify writes unless `--no-state-write`; default build `--through G03`; G04+ `deferred` exits 3.
- toolchain_manager: honors `--allow-unresolved-disabled`; native-contract compiles scripts; missing service templates fail; check-capability is pin-only.
- Docs moved to `.sai-quality/docs/`; BUNDLE_* removed.
- Gitignore runtime/tooling/venvs/__pycache__.
- Quality workflows pin checkout v4.2.2 SHA; CI `--through G03`.
- Fail-closed JS adapter; real feature-lock fixture; glob-scoped Cursor rule; DR 0005 proposed.
