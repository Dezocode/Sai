# Plan
Allow only the exact BASE cache name `sai-verify-$merge-base-$srcid` in `TestLinkedWorktreeHook` (`srcid` is the first 16 hex chars of sha256 of BASE `main.go` plus `go.mod`, same as the wrapper). Reject a planted `sai-verify-$HEAD-cafec0decafe0000` decoy. Fail any other `sai-verify-$HEAD-*` key. Restores `go test` on `main` after PR 69 landed the kernel.
