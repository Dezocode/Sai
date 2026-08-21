# Handoff — 20260821-1954-pr73-foundation-cursor-cloud

PR 73 on `foundation/sai-app-skeleton`. No new PR/branch. Not merged. Not marked ready.

## Heads

- START_HEAD=`7aa423f31a4084afb73d2ca3d5c981ea47bbff73` (intact kernel)
- OBSERVED truncated blob SHA=`838b5a9934d7ab0cacdc47bdb02e2ff5dd3efb02` at `1ef0940` (~1295 bytes, 578 deletions)
- HEAD_DISCREPANCY=none vs OBSERVED after restore: kernel rewritten from START_HEAD with pathRe only expanded
- Restore commit=`c181ea585208d6cf70dadb4e7b760d22a0e50a08` (~38KB, `func driveCmd` present)

## CI root cause

1. `pathRe` did not claim `apps|api|design|docs|internal|deploy|migrations`, so product-root globs were unmapped / recipes failed to bind.
2. Feature proofs used illegal `::exec go` (not in allowBin). Maps were already fixed in `4e445a4080bd18eec94d15d45c6f5198b64f31e5` (`::gotest` / tree globs). Not reverted.
3. Accidental truncated `cmd/sai-verify/main.go` placeholder at `1ef0940` removed the kernel (driveCmd/recipe/allowBin). Restored; frozen recipe/allowBin bodies unchanged. `go.mod` unchanged. No manufactured `sai-verify-proof.json`.

## Remediation landed

1. Full kernel restore + pathRe expansion.
2. `TestFoundationRootsAreClaimable` (sibling file; adversarial `main_test.go` not rewritten).
3. GET-only `/health` `/ready` (204; POST 405); `DefaultAddr`/`Addr`/`Handler`; OpenAPI `servers` loopback.
4. Swift: SaiConfiguration, SaiHTTPClient GET 204, design tokens, silent shell ping, xcconfig Info.plist keys. `SaiFeatures` remains empty enum. `featureUIAllowed=false`.

## Remaining

Saul independent review of PR 73. Co-founders decide ready/merge. Drive sync pending without rclone.
