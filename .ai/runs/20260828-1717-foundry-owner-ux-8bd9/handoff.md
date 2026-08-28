# Handoff — 20260828-1717-foundry-owner-ux-8bd9

## Summary

Slice 82 Foundry owner UX on `foundry/owner-ux`: dry-run-first Integrate / Spin Off / Delete controls via SaiDesignLanguage, manifest-driven flags for any `prototypes/plugins/<plugin>/` path, and thin CLI bridge to #164 graduation engine.

**Draft PR:** https://github.com/Dezocode/Sai/pull/169 (`foundry/owner-ux` → `main`)

## Delivered

- `FoundryOwnerView` + `FoundryOwnerModel` (dry-run → preview → confirm → execute)
- `FoundryPrototypeManifest` reads `prototype.manifest.json` graduation flags
- `FoundryPlanTemplate` parameterized per prototype path; UNKNOWN disposition fails closed
- `FoundryEngineBridge` invokes #164 `graduate` CLI (`owner_confirmed=false` on dry-run)
- `FoundryHarnessFixture` entry point for harness wiring
- Verifier lane: `prototypes` pathRe + `inFoundryOwnerUXScope` + CI `prototypes/**` trigger
- verify-sai feature map + roadmap at `docs/roadmap/foundry/10-owner-ux-v1.md`

## Verification

- `go test ./cmd/sai-design-check/...`
- `go test ./cmd/sai-verify/...`
- Swift tests in `prototypes/plugins/foundry/owner-ux/Tests/`

## Next

- End-to-end harness fixture with Sai Author through dry-run + confirm paths
- Owner-ready requires exact-head CI, preservation, and independent review
