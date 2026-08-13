# Review — PR #59 Add SAI Phase 0 Quality OS

- Reviewer: cursor-cloud (this run `20260813-0245-pr59-review-cursor-cloud`)
- Diff range: `40efe0a0724764fc1cf3c45ed8498b5606a0f453...c6736d1b9c967decb9124ed5b8a3d0818d68f3d5` (`origin/main...origin/agent/sai-phase0-quality-os`)
- Subject: https://github.com/Dezocode/Sai/pull/59 (draft)
- Plan: `.ai/runs/20260813-0245-pr59-review-cursor-cloud/02_plan/output/plan.md`
- Disposition: **block merge** (keep draft). Return the Quality OS to implementers for the blocking findings below. Do not treat green CI as unlock evidence.

PR #59 is a serious, additive attempt to put a quality control plane in place before parent/child product UI. Preservation of `.ai/`, `AGENTS.md`, `agent-audit.yml`, and root `README.md` is real. The bundle is not yet a mergeable control plane: several gates are stubs, CI contradicts G14, repo-root docs fight ICM, and an alwaysApply Cursor rule would bind every future agent.

---

## 1. Full diff — every hunk intended and justified?

**Finding: not fully justified as a merge to `main`.**

Intended: chronological G00–G15 quality OS, feature lock, OSS tool adapters, Cursor skill/commands, CI.

Observed problems in the hunks:

### Blocking

1. **Gates check pinning, not scanners.** `scripts/toolchain_manager.py check-capability` passes once `version` is not `UNRESOLVED`. It does not run Semgrep, Trivy, Gitleaks, jscpd, Knip, or dependency-cruiser. G05 `verify-native-contract` always prints PASS. G08 `health_report.py verify-ratchet` always prints PASS if a baseline file exists. G11/G13 “services” copy templates; they do not start or health-check SonarQube or Dependency-Track.

2. **G14 is already failed by this PR’s own workflows.** `scripts/workflow_guard.py` requires `uses:` refs to be a 40-char commit SHA. Both new workflows use `actions/checkout@v4`. There is no `scorecard` template, so G12 `render-service scorecard` copies nothing.

3. **Fail-open JS adapter.** `.sai-quality/adapters/registry.json` runs dependency-cruiser with `2>/dev/null || true`.

4. **`qualityctl.py` `run_cmd` uses `shell=True`** on strings from `gates.json`. Orchestrator trust is the whole file set; still the wrong primitive for a security-minded control plane.

5. **`--allow-unresolved-disabled` is dead.** Assigned in `verify-lock` and never read. G04 therefore cannot do what its command line claims.

6. **`qualityctl verify` never writes state** because of `write=not a.no_state_write and False`. The `and False` makes `--no-state-write` redundant and hides a logic bug.

7. **Repo-root overlay.** `CURSOR_START_PROMPT.md`, `MASTER_EXECUTION.md`, `QUALITY_OS_README.md`, `BUNDLE_MANIFEST.json`, `BUNDLE_SHA256SUMS.txt`, and ~12 other Markdown files sit at the repository root. ICM keeps durable contracts under `.ai/` (or, for this overlay, under `.sai-quality/`). Zip-bundle leftovers do not belong on `main`.

8. **Always-apply Cursor rule** `.cursor/rules/95-sai-quality-os.mdc` tells every agent that Phase 0 quality infrastructure is the only build target. That collides with live ICM, contractor, and `openclaw-dashboard/` work unless scoped or decided in a memory decision record.

9. **No architecture decision record.** CEO memory rules require a DR for a second control plane. `.ai/shared/memory/` is untouched.

10. **Feature lock is path-token shallow.** `product_roots` are only `apps/services/packages/evals/infrastructure`. Existing `openclaw-dashboard/` is listed as a “governance root” and is not locked. `architecture_guard.py` does not implement `forbid_unregistered_product_subroots`. Fault injection’s “feature-lock” case is a policy-key presence check, not a locked-file fixture.

11. **No gitignore for runtime/evidence/tooling.** `.sai-quality/runtime/`, generated evidence, venvs, and isolated `node_modules` would be easy to commit after G04.

12. **Actor `chatgpt` is not in `registry.json`.** Trailers satisfy CI; protocol still expects named agents.

### Non-blocking / keep

- Additive `.sai-quality/` tree and refusal to overwrite `README.md` / `.ai/` / `agent-audit.yml`.
- Feature-lock *intent* for future product roots; Sonar compose uses env-required passwords; workflow `permissions: contents: read`.
- Draft status and handoff that already say “do not merge merely because bootstrap files exist.”

---

## 2. Changed file list vs claimed files

**Finding: mostly matches, with extras.**

PR run `20260813-0228-sai-phase0-quality-os-chatgpt` claims `.sai-quality/**`, selected `.cursor/` paths, quality workflows, and a subset of scripts plus `CURSOR_START_PROMPT.md` / `MASTER_EXECUTION.md`.

Unclaimed but present: the other ~12 root Markdown files, `BUNDLE_*`, remaining `scripts/*.py` guards, templates, provenance JSON. Exception is explainable as a zip overlay, not as a tight ICM claim list.

This review run claims only its own `.ai/runs/20260813-0245-pr59-review-cursor-cloud/`.

---

## 3. Secrets, generated files, binaries, machine paths

**Finding: no committed secrets observed.** No `.env`, tokens, or private keys in the diff. Sonar compose requires `SONAR_DB_PASSWORD` outside git.

Risks, not current leaks:

- Port `9000:9000` on the Sonar template if someone runs compose locally.
- Knip schema URL on `unpkg.com`.
- Future G04 installs into `.sai-quality/runtime/venv` and tooling `node_modules` with no ignore rules.
- `BUNDLE_SHA256SUMS.txt` is generator residue; 58 checksum lines vs 62 files in the PR.

No large binaries.

---

## 4. Tests and documentation

**Finding: docs are plentiful; tests are thin relative to claims.**

- `architecture_guard.py self-test` and `fault_injection.py` exist; the latter is mostly synthetic registry JSON, not real scanner fixtures (the matrix document itself says Cursor must extend them).
- CI `phase0-or-quality` runs G00–G02-equivalent via `--current-policy` on empty `passed` (falls back to G02). That is why CI is green while G04+ cannot pass.
- `VALIDATION_REPORT.md` describes pre-PR zip generation, not this repository’s CI after merge.
- Durable SAI memory/docs (`architecture.md`, decision records, `testing.md`) were not updated.

---

## 5. Commit boundaries and trailers

**Finding: one commit, trailers present, scope too large for one logical change.**

```
c6736d1 Add SAI Phase 0 Quality OS
Task-ID: 20260813-0228-sai-phase0-quality-os-chatgpt
Agent: chatgpt
Plan: MASTER_EXECUTION.md
Report-Event: HANDOFF
```

`handoff.md` is >20 bytes; HANDOFF event is schema-valid JSON. `verify-agent-audit` / `verify-merge-handoff` should pass (CI already did).

Branch name `agent/sai-phase0-quality-os` is outside documented conventions (`cursor/…`, `ceo/…`, `proj/…`). Acceptable for a human/ChatGPT draft; not a merge blocker by itself.

---

## 6. Compatibility (fork pair and existing branches)

**Finding: additive, but behavior-changing for every later PR.**

- Does not rewrite `monaecode/Sai` history.
- After merge, every PR/push to `main` runs `sai-quality-os` (config integrity, architecture check, feature lock, qualityctl verify through last passed / G02).
- Nightly cron `17 8 * * *` adds a scheduled job.
- AlwaysApply rule changes agent behavior in Cursor Desktop and Cloud without a DR.
- `openclaw-dashboard/` remains unlocked (consistent with DR-20260724 prototype boundary) but contradicts “no product implementation until unlock” if dashboard work continues.

---

## 7. Durable memory

**Finding: untouched.** Required for a new control plane; missing.

---

## 8. Conflicts with other runs’ file ownership

**Finding: no semantic conflict with this review’s claims.**

PR #59 claims quality overlay paths. Recent `cursor-cloud` pstack work claimed `.cursor/settings.json` / `.ai/plugins/` — different files. `.cursor/rules/95-sai-quality-os.mdc` is new. Stale `in_progress` runs from July claiming `.cursor/rules/sai-coordination.mdc` or `scripts/**` are historical; they do not own this overlay.

---

## Security-policy hard gates

None of the listed hard actions (force-push, credential/protection changes, release, production deploy, access/billing, private-data mirroring) are performed by merging the *bootstrap files*. Bringing up SonarQube/Dependency-Track, pinning/installing third-party binaries, or enabling Renovate on the canonical repo **would** need explicit co-founder approval at G04/G11/G12. Do not let a later agent treat this PR as that approval.

---

## What CI green actually means

`phase0-or-quality` SUCCESS means JSON parses, architecture registry uniqueness holds on current empty product roots, feature lock sees no `apps/` tree, and cumulative verify through G02 passes. It does **not** mean G04–G15, tool provenance, SAST, SBOM, or unlock.

---

## Required changes before merge (or before treating this as the factory)

1. Move root bundle docs under `.sai-quality/docs/` (or `.ai/projects/…`); drop `BUNDLE_*` from the git tree.
2. Add a decision record for the Quality OS vs ICM split; update `architecture.md`.
3. Pin Actions by SHA or relax/align G14 with what is actually committed; add a scorecard template or drop G12’s render.
4. Remove `|| true` / `2>/dev/null` from adapter commands; make `check-capability` invoke real tools or stop claiming those gates.
5. Fix `shell=True`, the unused `--allow-unresolved-disabled` flag, and `and False` verify-write.
6. Implement or delete `forbid_unregistered_product_subroots`; add a real feature-lock negative fixture.
7. Gitignore `.sai-quality/runtime/`, `tooling/node_modules`, venvs, evidence dumps.
8. Narrow the alwaysApply rule (frontmatter glob / explicit exception for `.ai/` and `openclaw-dashboard/`) or get a co-founder DR that this rule outranks ongoing ICM work.
9. Keep the PR **draft** until G04 pin policy is either executed with co-founder approval or explicitly deferred with gates marked optional.

## Disposition

**block** — do not merge PR #59. Keep draft. Next safe action is co-founder decision: (a) request the changes above on this branch, or (b) run a *scoped* G00–G03 harden pass without installing Sonar/DT/Renovate until approved.
