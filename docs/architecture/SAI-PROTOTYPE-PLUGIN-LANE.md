# Sai prototype plugin lane

Status: **enabling contract — this PR is contract-only (documentation)**. It
defines the safe prototype-plugin lane; the Sai Author bootstrap itself,
the verifier enforcement, and the mechanical isolation proofs are successor
work under separately identified PRs. No production authority boundary is
weakened by this document.

## Goal

Monaecode must be able to build real SwiftUI product prototypes under one canonical non-shipping plugin root while production remains protected by the Sai Design Language and `featureUIAllowed=false`.

Preferred prototype root:

`prototypes/plugins/`

Sai Author is the first prototype plugin. **This PR contains the lane
contract only**; it deliberately does not include the Author shell, build
targets, verifier changes, or isolation tests. Those are delivered by the
successor PRs listed below, which must satisfy every requirement stated
here before they can be considered owner-ready.

### Successor work (explicitly out of scope for this PR)

1. `prototype/lane-enforcement`: verifier-owned fail-closed exemption for
   `prototypes/plugins/` in the design-check/verify kernel, near-prefix
   rejection, candidate-JSON hardening, and mechanical production→prototype
   dependency-isolation tests.
2. `prototype/sai-author-shell`: minimal runnable/buildable Sai Author
   prototype (root/editor placeholder plus settings placeholder) under
   `prototypes/plugins/author/`, with macOS/iOS Simulator build proof and
   `sai-verify` surface mapping.
3. Follow-on product prototyping per the direction below.

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

The smallest real Sai Author prototype establishes a continuation point for
product development across macOS and iOS/iPadOS. A root/editor placeholder
and settings/configuration placeholder are sufficient for the
`prototype/sai-author-shell` successor PR; this contract only fixes the
requirements that shell must satisfy.

Do not build the full editor, AI workflows, persistence, collaboration,
marketplace, downloadable-code runtime, or final plugin platform in any
enabling or successor PR.

## Adversarial acceptance

The successor implementation PRs must prove at least that:

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

This contract PR is owner-ready when all of the following hold on its exact
final HEAD:

- the contract is complete, unambiguous, and consistent with the merged
  foundation's authority boundaries;
- exact-head CI/preservation evidence is green;
- independent quality review has no unresolved blocker;
- genuine exact-head Saul reports P0=P1=P2=0.

The successor implementation PRs additionally carry, on their own exact
final HEADs, every item below before owner merge approval:

- minimal runnable/buildable Sai Author prototype exists;
- relevant macOS and iOS Simulator build coverage passes;
- production feature UI remains locked;
- prototype authority is verifier-owned and fail-closed;
- production/prototype dependency isolation is mechanically proven;
- `sai-verify` recognizes and proves the new surface.

Remain draft and unmerged until those conditions are satisfied and an owner explicitly chooses to merge.
