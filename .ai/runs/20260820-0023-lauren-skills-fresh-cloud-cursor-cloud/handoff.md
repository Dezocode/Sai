# Handoff — 20260820-0023-lauren-skills-fresh-cloud-cursor-cloud

## Done

PR 70 skills were already on `Dezocode/Sai:main` (`8a30202`). A fresh Cloud Agent still missed them because of snapshot reuse plus slash mismatch. This branch adds `/lauren`, description matching, and an always-on discovery rule.

## Evidence

- Fresh agent `bc-01a01c89-0d79-709c-aacf-ba84185f18aa`: `branchName` null, `gitSetup` reuse of `bld-20260819-500928d1-8214-4bc0-9bb9-e36884ef51f0`, install exit 0 at 00:19:04Z after PR 70 merged at 00:12:17Z.
- This session loaded `.cursor/skills/lauren-mode/` from a post-PR-70 tree. Cloud does scan that path when files exist.
- User typed `/lauren mode` (space).

## Next safe action

Merge draft [PR 71](https://github.com/Dezocode/Sai/pull/71) after review. Start a **new** Cloud Agent on latest `main` (explicit branch from `origin/main`). Type `/lauren` or `/lauren-mode`. If the skill files are missing in that VM, `git fetch origin main` and check out that SHA. Do not expect snapshot `bld-20260819-500928d1-…` to contain PR 70 until git moves.

Do not commit `.cursor/environment.json`. Do not mark ready or merge without a co-founder.

## Drive

pending (`rclone` / `SAI_DRIVE_REMOTE` not configured on this VM)
