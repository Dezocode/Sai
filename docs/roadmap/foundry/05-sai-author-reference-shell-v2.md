# PR contract — Sai Author native reference shell v2

PRD: [`docs/prd/SAI-PROTOTYPE-FOUNDRY-PRD-v1-reference.md`](../../prd/SAI-PROTOTYPE-FOUNDRY-PRD-v1-reference.md)
Roadmap: [`00-sai-harness-foundry-sequence.md`](00-sai-harness-foundry-sequence.md)

## Mission

Retain the original Foundry PRD's native-product proof by creating the smallest real **Sai Author** macOS + iOS/iPadOS-capable prototype shell under the canonical lane. It is the product reference fixture complementing the systems-oriented Sai Harness fixture.

## Acceptance

- [ ] Canonical tree is `prototypes/plugins/author/`; all shipping production targets remain independent.
- [ ] Buildable macOS application structure exists.
- [ ] Buildable iOS Simulator target exists; adaptive structure covers iPadOS as appropriate.
- [ ] Minimal UX only: root/editor placeholder + settings/config placeholder; no full editor/persistence/collaboration/provider marketplace.
- [ ] Ordinary UI reuses SaiDesignLanguage first; plugin-local `PrototypeDesign/` is used only for genuine gaps.
- [ ] Reuse appropriate SaiKit modules (`SaiDesignLanguage`, `SaiFoundation`, `SaiAPI`) rather than cloning production abstractions.
- [ ] Prototype domain behavior reaches production authority through typed API/OpenAPI where appropriate; prototype mocks/local state remain explicitly exploratory.
- [ ] Prototype-only Go helpers are allowed only in-lane and never become production dependencies.
- [ ] Any production Go/OpenAPI gap discovered here is recorded for a separate production-authority PR.
- [ ] Sai Harness/Crosscom may assist development, telemetry and agent coordination but is **not required to build/run the Author product surface**.
- [ ] Removing the Author tree leaves production build/test green.
- [ ] Breaking/removing the intended Author app/target causes its own proof to fail meaningfully rather than silently no-op.
- [ ] `sai-verify` maps Author entry points/source roots/build proofs.
- [ ] Native build proof is deterministic enough for CI; no undeclared local workspace links.
- [ ] Exact-head lane/design/native-build/preservation evidence + genuine independent review converge before owner-ready.

## Non-goals

- No rich editor workflows, persistence, collaboration, provider marketplace or final aesthetic approval.
- No Foundry manifest/planner/executor implementation yet.
- No production integration.
