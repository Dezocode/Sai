# Handoff — 20260828-1717-foundry-owner-ux-8bd9

## Summary

Slice 82 Foundry owner UX: verify-sai feature map, roadmap PR contract, prototype package under `prototypes/plugins/foundry/owner-ux/` with dry-run-first owner model/view, `FoundryPlanTemplate` for engine-compatible plan JSON, and `FoundryEngineBridge` consuming #164 graduation engine CLI (stub fallback). Verifier adds `prototypes` pathRe and `inFoundryOwnerUXScope` lane exemption.

## Files

- `.cursor/skills/verify-sai/features/foundry-owner-ux.md`
- `.cursor/skills/verify-sai/features/README.md`
- `docs/roadmap/foundry/10-owner-ux-v1.md`
- `prototypes/plugins/foundry/owner-ux/prototype.manifest.json`
- `prototypes/plugins/foundry/owner-ux/Package.swift`
- `prototypes/plugins/foundry/owner-ux/Sources/FoundryOwnerUX/*.swift`
- `prototypes/plugins/foundry/owner-ux/Tests/FoundryOwnerUXTests/FoundryOwnerUXTests.swift`
- `cmd/sai-verify/main.go` (prototypes pathRe)
- `cmd/sai-design-check/main.go` + `main_test.go` (owner-ux scope)
- `.github/workflows/sai-design-language.yml` (prototypes/** triggers)

## Verification

- `go test ./cmd/sai-design-check/...`
- `go test ./cmd/sai-verify/...`

## Next

- Wire owner shell into Foundry harness fixture.
- Owner-ready requires exact-head CI, preservation, and independent review per roadmap contract.
