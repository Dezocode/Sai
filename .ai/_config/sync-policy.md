# Google Drive synchronization policy

GitHub is canonical for commits, branches, tags, and PRs. Version-controlled
repository memory (`.ai/shared/memory/`) is canonical for durable decisions.
Google Drive mirrors those records for shared access and recovery — nothing
more.

## Drive layout

```
SAI/
  manifest.json
  repositories/
    dezocode-sai/
      bundles/      <- immutable timestamped git bundles
      snapshots/    <- checksummed source snapshots keyed by commit SHA
      memory/       <- mirror of .ai/shared/memory/
      audit/        <- mirror of committed audit records
    monaecode-sai/
      bundles/
      snapshots/
      memory/
      audit/
  contracts/
    <contract-id>/  <- mirror of .ai/contracts/<contract-id>/
  agents/
    <agent-id>/
      memory/       <- mirror of .ai/agents/<name>/memory/
  projects/
    <project-slug>/
      contract-refs.json
      branches-index.json   <- branch -> contractor -> contract mapping
      coordination/
        slack-channel.json
  coordination/
    events/         <- mirrored agent events (JSON)
    handoffs/       <- mirrored handoff.md files
    conflicts/      <- conflict reports and resolutions
  checksums/        <- SHA-256 manifests for every uploaded artifact
```

## Rules

1. Drive must **never** contain concurrently edited active clones, active
   worktrees, or `.git` directories. Git worktrees contain machine-specific
   paths and shared Git metadata; cloud synchronization can create stale
   locks, split histories, or corruption.
2. Prefer immutable, timestamped Git **bundles** (`git bundle create`) and
   checksummed snapshots. Exchange changes between agents only through pushed
   branches, PRs, or these immutable bundles.
3. Key snapshots by repository identity **and** commit SHA:
   `<owner>-sai/snapshots/<sha>/`.
4. Never overwrite the last known-good bundle. Upload a new artifact, verify
   its integrity and checksum, then update `manifest.json`.
5. Record sync state as exactly one of `pending`, `synced`, `failed`, or
   `diverged`. Never claim atomic equality across GitHub and Drive.
6. Retry transient failures, but never hide divergence.
7. Update the Drive mirror only **after** GitHub verification of the pushed
   commit SHA.
8. Reconcile any Drive-originated memory edits through a Git branch and PR —
   never edit canonical memory directly from Drive.
9. Never copy credentials, environment files, caches, dependencies, build
   outputs, or `.git` lockfiles to Drive.

## Required content of a successful SYNC report

repository, commit SHA, GitHub verification evidence, Drive destination path,
checksum (SHA-256), timestamp (UTC ISO-8601), and status.

## Tooling

`scripts/agent-sync-drive` implements this policy. It requires a configured
Drive remote (e.g. an `rclone` remote named in `SAI_DRIVE_REMOTE`); when
credentials are absent it records the sync as `pending` and exits without
error, so missing Drive access never blocks Git work.
