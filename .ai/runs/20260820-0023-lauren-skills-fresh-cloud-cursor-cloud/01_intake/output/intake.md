# Intake — PR 70 skills missing in a fresh Cloud Agent

- Task-ID: `20260820-0023-lauren-skills-fresh-cloud-cursor-cloud`
- Requester: dezocode (U0BHYH0NMCY)
- Source: follow-up on this Cloud Agent (`bc-01a01c62-2904-7567-b237-4ba571eafd30`) after Dezocode/Sai#70 merged. Screenshot of a second mobile agent titled "Lauren mode cursor runtime".
- Quote: `/lauren-mode fix me not being able to use skills from pr70 in a fresh cursor cloud agent`

## Requested outcome

A fresh Cursor Cloud Agent can use the project skills that landed in PR 70 (`/lauren-mode` and the harness references). Do not leave operators typing `/lauren mode` (space) or starting from a pre-merge snapshot with no way to attach the mode.

## Repository facts (command-backed)

```
git rev-parse --show-toplevel → /workspace
git remote -v → origin https://github.com/dezocode/sai (fetch/push)
gh repo view → Dezocode/Sai, default branch main, not a fork
git fetch origin main → 8a302026ce77e3fb03fbcdc0f6f3a6041df1798c Merge pull request #70
git ls-tree origin/main .cursor/skills/lauren-mode/SKILL.md → present
branch created → cursor/lauren-skills-fresh-fd30 from origin/main
```

Canonical repo is `Dezocode/Sai`. This VM is a Cloud Agent clone, not a Google Drive worktree.

## Runtime evidence (matching surface)

Fresh mobile agent `bc-01a01c89-0d79-709c-aacf-ba84185f18aa` ("Lauren mode cursor runtime"):

- `branchName`: null (no feature branch, no explicit checkout of live `main`)
- Same personal env `6f2ece39-800a-11f1-ba66-0e7d0216e441`
- Same snapshot `bld-20260819-500928d1-8214-4bc0-9bb9-e36884ef51f0` as this parent
- `gitSetup`: reuse, `warmFork`: warm_fork
- Setup install exited 0 in ~0s (reused snapshot; no clone of post-merge `main`)
- Created 2026-08-20T00:19:04Z, after PR 70 merge 2026-08-20T00:12:17Z
- Screenshot thought: "No lauren files in the tree yet"
- User prompt used `/lauren mode` (space), not `/lauren-mode`

This session loaded `.cursor/skills/lauren-mode/` from a checkout that includes PR 70. Cloud Agents **do** scan `.cursor/skills/` when the files are in the working tree. Hypothesis "Cloud never loads `.cursor/skills/`" is refuted.

PR 70 SKILL.md currently has `disable-model-invocation: true`, so description matching will not auto-attach "Lauren mode".

## Constraints

- Do not copy pstack into `.cursor/skills/` (decision 0004).
- Do not commit `.cursor/environment.json` (decision 0005).
- Do not run `scripts/agent-init` / `install-agent-hooks` on this managed VM.
- Do not force-push, merge, or mark the PR ready.
- Commit trailers and merge-handoff required.
- 0005 rejected an always-apply rule that **inlines** poteto-mode. A thin discovery pointer is a different change (decision 0006).

## Acceptance

- `/lauren` exists as a project skill so mobile `/lauren` / "lauren mode" can attach.
- `/lauren-mode` allows model invocation so a prose ask can attach when files are present.
- An always-apply rule tells agents the hyphen command, the paths, and to `git fetch origin main` before claiming the skill is absent.
- Docs state that `gitSetup: reuse` of snapshot `bld-20260819-500928d1-…` can hide commits that landed after the snapshot, including PR 70.
- No `.cursor/environment.json`. No vendored pstack.

## Security / compatibility

No hard gates from `.ai/_config/security-policy.md`. No secrets. Do not commit owner emails from `run-info`.
