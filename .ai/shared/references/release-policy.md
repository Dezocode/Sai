# Release policy reference (Layer 3)

## Current state

SAI has no release pipeline yet (no application code as of 2026-07-14). The
rules below are binding now; the mechanics will be added by decision record
when a stack exists.

## Binding rules

1. Publishing a release, tagging a version, or deploying to any production
   environment is a **hard human review gate**
   (`.ai/_config/security-policy.md`): it requires explicit approval from
   dezocode or monaecode for the specific release.
2. Releases are cut only from `Dezocode/Sai:main` (the canonical repository),
   never from the fork.
3. A release commit must be preceded by a completed run with stages 04
   (verify) and 05 (review) recorded, and a VERIFY report in #agentupdates.
4. Release artifacts and their checksums are mirrored to Drive under
   `SAI/repositories/dezocode-sai/snapshots/<sha>/` after GitHub verification.
5. Never attribute a release to a human who did not approve it.
