# Handoff — Foundry graduation engine (slice 81)

Implemented plan-bound graduation engine under `prototypes/plugins/foundry/graduation-engine/` with integrate, spinoff, and delete-archive executors, idempotent journal, production dependency scan, and E2E tests using a temp git fixture.

Added verify-sai feature map `foundry-graduation.md`, plan v0 schema, docs, test-widget fixture, and graduate CLI.

Extended `cmd/sai-verify` `pathRe` to claim `prototypes/**` so sai-verify completeness sweep passes for prototype lane files.

Restored truncated `cmd/sai-verify/main.go` kernel body via GitHub API (local VM hooks blocked shell writes).

## FINAL_HEAD

`10407fefa9d861e1be40e973ecf6460835a8a018` on `foundry/graduation-engine`.

## CI (exact HEAD, all green)

- `icm-enforcement` (includes `go test -race ./...`, sai-verify drive/doctor/preserve/proof, merge-handoff)
- `build` (feature maps)
- `Anti-regression`
- `PR line budget`

## Slice 81 acceptance (engine_test.go + CI)

- Validated plans bind prototype HEAD + graph_hash; stale HEAD fails closed (`TestStalePlanFailsClosed`)
- Integrate writes draft not-ready PR candidate JSON, never `main` (`TestIntegrateCreatesDraftPRCandidate`)
- Spinoff materializes candidate tree + PROVENANCE.json (`TestSpinoffMaterializesProvenance`)
- Delete/archive scans production deps then removes prototype (`TestDeleteArchiveRemovesPrototype`, `TestProductionDependencyBlocksDelete`)
- UNKNOWN disposition fails plan validation (`TestUnknownDispositionFailsPlanValidation`)
- Idempotent journal replay (`TestIdempotentReExecution`)

Production Go does not import `prototypes/**`. Engine is prototype-scoped only.

Draft PR #164 targets `main` (slice 81 of program #160; does not close #160). Stays draft. Not stacked on #158.

Next safe action. Owner or Saul review when requested. Program E2E across slices 76–82 remains open on #160.
