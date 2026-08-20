# Verification — 20260820-0023-lauren-skills-fresh-cloud-cursor-cloud

- Task-ID: `20260820-0023-lauren-skills-fresh-cloud-cursor-cloud`
- Commit verified: `5785d4786cb46dedd8750cd4df8797637c0c72b4`
- Log: `.ai/runs/20260820-0023-lauren-skills-fresh-cloud-cursor-cloud/04_verify/output/icm-verify.log`

## Repro (git, matching the missing-slash / no-invocation bug)

On `origin/main` (`8a30202`, PR 70):

- `.cursor/skills/lauren-mode/SKILL.md` has `disable-model-invocation: true`
- `.cursor/skills/lauren/SKILL.md` is absent
- `.cursor/rules/lauren-mode.mdc` is absent

On `HEAD` (`5785d47`):

- `disable-model-invocation: true` is gone
- `/lauren` skill is present
- discovery rule is present

Fresh-agent snapshot reuse (`gitSetup: reuse`, `branchName: null` on `bc-01a01c89-0d79-709c-aacf-ba84185f18aa`) is documented, not re-staged. This VM cannot rewrite that agent's checkout.

## Commands and results

| Check | Command | Result |
|---|---|---|
| JSON | `python3 -m json.tool` on pstack `manifest.json` and run manifests | OK |
| Frontmatter | Python assert on the two SKILL.md files and `lauren-mode.mdc` | OK |
| Hierarchy | `scripts/verify-semantic-hierarchy` | OK (after removing an empty `06_publish_sync/` dir that had been mkdir'd early) |
| Audit | `scripts/verify-agent-audit origin/main..HEAD` | OK |
| Handoff | `scripts/verify-merge-handoff origin/main..HEAD` | OK (1 task-id) |
| Setup | `scripts/verify-agent-setup` | OK |

## Skips

- Desktop `/` picker listing `/lauren`. Needs a new Cloud Agent or window reload on this commit.
- Restaging agent `bc-01a01c89-0d79-709c-aacf-ba84185f18aa`. That VM reused snapshot `bld-20260819-500928d1-8214-4bc0-9bb9-e36884ef51f0`. Evidence is `batch-fetch-details` environment-info, not a re-run.
- `scripts/verify-scaffold-safety`. No scaffold/contract files touched.
- YAML app configs. None changed.

## Limitations

A Cloud Agent that still boots the pre-merge snapshot and does not check out a SHA containing this commit will still lack the files. In-repo discovery cannot appear in a tree that does not contain it.
