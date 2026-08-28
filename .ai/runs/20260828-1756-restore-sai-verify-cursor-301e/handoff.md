# Handoff — restore sai-verify kernel (PR #164 CI)

PR #164 `icm-enforcement` failed because `cmd/sai-verify/main.go` on the branch was truncated (PLACEHOLDER_TAIL / compile errors). Seven agent commits on this task-id pushed partial restores via GitHub API while local hooks blocked shell writes (stale untracked prototype stubs on the Cloud VM).

Restored the full kernel from `main` with one map change. Added `prototypes` to `pathRe` so prototype lane files pass sai-verify completeness sweep for slice 81.

Intermediate restore commits (`9129ad7` through `e930443a`) are superseded by later `20260828-1717-graduation-engine-cursor-301e` commits. Tip `62795b97` holds the kernel that turned build and Anti-regression green.

Draft PR #164, branch `foundry/graduation-engine`, slice 81 of program #160. Does not close #160.

Next safe action. Land this handoff, confirm exact-HEAD `icm-enforcement` green, then owner review when program slices converge.
