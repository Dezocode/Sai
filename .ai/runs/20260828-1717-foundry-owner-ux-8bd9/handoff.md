# Handoff — 20260828-1717-foundry-owner-ux-8bd9

## Summary

Slice 82 Foundry owner UX on `foundry/owner-ux`: dry-run-first Integrate / Spin Off / Delete controls, manifest-driven flags for any `prototypes/plugins/<plugin>/` path, and thin CLI bridge to #164 graduation engine.

**Draft PR:** https://github.com/Dezocode/Sai/pull/169 (`foundry/owner-ux` → `main`)

## Delivered

- `FoundryOwnerView` foundation-draft screen descriptor + `FoundryOwnerModel` (dry-run → preview → confirm → execute)
- `FoundryPrototypeManifest` reads `prototype.manifest.json` graduation flags
- `FoundryPlanTemplate` parameterized per prototype path; UNKNOWN disposition fails closed
- `FoundryEngineBridge` invokes #164 `graduate` CLI (`owner_confirmed=false` on dry-run)
- `FoundryHarnessFixture` entry point for harness wiring
- verify-sai feature map (`foundry-owner-ux`) + roadmap at `docs/roadmap/foundry/10-owner-ux-v1.md`
- `cmd/sai-verify` pathRe claims `prototypes/` for completeness sweep (slice 81 precedent)

## Scope boundary

- Production verifier files (`cmd/sai-design-check`, `.github/workflows/sai-design-language.yml`) unchanged. Slice 76 (#136) owns lane enforcement.
- `cmd/sai-verify/main.go` one-line `prototypes` pathRe addition only (slice-owned verify touchpoint).

## Verification

- Swift tests in `prototypes/plugins/foundry/owner-ux/Tests/`
- PR CI: `icm-enforcement`, anti-regression, line budget

## Next

- End-to-end harness fixture with Sai Author through dry-run + confirm paths
- SwiftUI owner surface after slice 76 prototype lane lands
- Owner-ready requires exact-head CI, preservation, and independent review
