# Git workflow reference (Layer 3)

## Remotes

Use explicit remote names. Recommended configuration:

```bash
# In a clone of the canonical repo:
git remote add dezocode https://github.com/Dezocode/Sai
# In a clone of the fork:
git remote add monaecode https://github.com/monaecode/Sai
git remote add upstream  https://github.com/Dezocode/Sai
```

`origin` may exist from the initial clone; know which repository it points to
before every push (`git remote -v`).

## Branch and worktree lifecycle

Before creating a worktree:

1. `git fetch <remote> <base-branch>` — fetch the intended base.
2. Verify the branch name is unclaimed: no remote branch of that name and no
   active run's `metadata.json` claiming it.
3. Post a WORKTREE report announcing branch, worktree ID, task, and files.
4. `git branch <branch> <remote>/<base>` — create a unique branch.
5. `git worktree add <local-non-synced-path> <branch>` — the path must be
   outside Google Drive or any cloud-synchronized directory.

Never have two agents edit the same working tree. Report worktree creation,
branch changes, removal, renaming, rebases, history rewrites, conflicts, and
abandonment. Remove worktrees with `git worktree remove` when the task ends.

Never synchronize active worktrees or `.git` directories through Google
Drive. Exchange changes only through pushed branches, PRs, or immutable Git
bundles (`git bundle create <file> <range>`).

## Commits

- Smallest coherent change; one logical change per commit.
- Message: imperative summary line describing the outcome, then a body
  explaining why, then trailers:

```
Add parental-consent flow to onboarding

Explains why, not what.

Task-ID: 20260714-0900-consent-flow-dezo-sec
Agent: dezo-sec
Plan: .ai/runs/20260714-0900-consent-flow-dezo-sec/02_plan/output/plan.md
Report-Event: <event_id of the CHANGE report>
```

## Pushing and PRs

- `git push -u <remote> <branch>`; retry transient network failures with
  backoff (4s, 8s, 16s, 32s).
- After pushing, verify the remote SHA:
  `git ls-remote <remote> refs/heads/<branch>` must equal the local HEAD.
- Open PRs against `Dezocode/Sai:main` unless the task brief says otherwise.
- Never force-push, merge, close, or mark ready for review without explicit
  co-founder authorization.
- Git has no native post-push hook: after every push, run
  `scripts/agent-report push-confirm` (or let CI confirm) so remote state is
  verified rather than assumed.

## Fork synchronization (monaecode/Sai <-> Dezocode/Sai)

Synchronize by SHA, never by re-created commits:

```bash
git fetch upstream main
git checkout main
git merge --ff-only upstream/main   # fast-forward only
git push monaecode main
```

If fast-forward is impossible, the histories have diverged: stop, post a
CONFLICT report, and coordinate before touching either `main`.
