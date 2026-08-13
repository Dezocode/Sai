# Plan — improve Quality OS executable slice

Make `qualityctl` honest: G00–G03 are the executable slice. G04+ stay in the catalog, remain required for unlock, and **defer** (do not install tools) until co-founder approval.

## Changes

1. Orchestrator: no `shell=True`; honor `--allow-unresolved-disabled`; fix verify write; default `--through G03`; deferred gates return exit 3 without false PASS.
2. `verify-native-contract` compiles quality/governance Python and `bash -n` bootstrap. `render-service` fails if the template is missing. `check-capability` states pin-only.
3. Relocate root docs to `.sai-quality/docs/`; delete `BUNDLE_*`.
4. `.gitignore` for runtime/tooling venvs/node_modules.
5. Pin quality workflow checkout to `actions/checkout` SHA v4.2.2. CI verify `--through G03`.
6. Remove adapter `|| true`. Real feature-lock negative fixture.
7. Narrow Cursor rule (globs, not alwaysApply). Decision record 0005 proposed.
8. Start prompt / skill / commands: `build --through G03`, then stop.
