# Sai prototype plugin lane

Status: **enabling contract**. This branch exists to create a safe prototype-plugin lane and bootstrap Sai Author without weakening the merged Sai application foundation.

## Goal

Monaecode must be able to build real SwiftUI product prototypes under one canonical non-shipping plugin root while production remains protected by the Sai Design Language and `featureUIAllowed=false`.

Preferred prototype root:

`prototypes/plugins/`

Sai Author is the first prototype plugin. This enabling PR proves the lane with a minimal runnable/buildable Author shell; it does not implement the word processor itself or freeze a permanent production plugin SDK.

## Required architecture

1. Production `SaiDesignLanguage`, `SaiFeatures`, `SaiMac`, and `SaiIOS` authority boundaries remain intact.
2. `featureUIAllowed=false` is not globally changed merely to permit prototypes.
3. The prototype exemption/root is verifier-owned, fail-closed, and cannot be relocated or widened by candidate JSON or plugin metadata.
4. SwiftUI may be used in the canonical prototype lane without making all Apple code exempt from production design enforcement.
5. Shipping Sai targets must not depend on prototype modules; this isolation must be mechanically tested.
6. `sai-verify` must map the prototype tree and meaningful prototype build/proof surface without weakening trusted-kernel semantics.
7. Prototype visual/product decisions are exploratory evidence, not production Sai Design Language authority.
8. Prototype code cannot graduate to production by file move alone; graduation requires an explicit production PR and normal production verification.

## Sai Author bootstrap

Create the smallest real Sai Author prototype that establishes a continuation point for product development across macOS and iOS/iPadOS. A root/editor placeholder and settings/configuration placeholder are sufficient for this PR.

Do not build the full editor, AI workflows, persistence, collaboration, marketplace, downloadable-code runtime, or final plugin platform here.

## Adversarial acceptance

The implementation must prove at least that:

- production SwiftUI remains blocked where the merged foundation blocks it;
- SwiftUI is permitted only in the canonical prototype scope intended by this PR;
- near-prefix or candidate-selected paths cannot become prototype exemptions;
- production manifests cannot add prototype dependencies without detection;
- prototype files do not become unmapped `sai-verify` surface;
- removing/breaking the Author prototype causes its intended build/proof to fail rather than no-op.

## Independent review gate

This PR is not merge-ready merely because candidate CI is green.

The exact final PR HEAD must receive a **genuine independent Saul review** after candidate verification converges. The authoritative Saul result must be bound to the exact current HEAD and must represent the real Hostinger/Codex reviewer path (historically `reviewer=hostinger-saul-cto`, `synthetic=false`, `codex_invoked=true`, or the repository's current equivalent).

Required terminal Saul disposition before owner merge approval:

- P0 = 0
- P1 = 0
- P2 = 0
- no unresolved product findings

Older-head Saul results are historical only. Synthetic/fallback/sandbox-provisioning results are infrastructure evidence, not product approval. If HEAD changes after Saul begins or completes, the new HEAD returns to pending and requires its own authoritative review.

## Merge gate

Owner-ready requires all of the following on the exact final HEAD:

- minimal runnable/buildable Sai Author prototype exists;
- relevant macOS and iOS Simulator build coverage passes;
- production feature UI remains locked;
- prototype authority is verifier-owned and fail-closed;
- production/prototype dependency isolation is mechanically proven;
- `sai-verify` recognizes and proves the new surface;
- exact-head CI/preservation evidence is green;
- independent quality review has no unresolved blocker;
- genuine exact-head Saul reports P0=P1=P2=0.

Remain draft and unmerged until those conditions are satisfied and an owner explicitly chooses to merge.
