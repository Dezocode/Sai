# 0009 — Trusted Saul Comptroller + nested SHA-bound product-quality loop

- Date: 2026-08-15
- Task-ID: 20260813-2015-pr62-queue-ceo
- Status: accepted
- Approver: dezocode
- Depends on: 0005 (quality registry), 0006 (authorization / Saul identity),
  0007 (Runtime Intelligence), 0008 (persistent Primary / Ralph)
- Appends: 0005, 0006, 0008 and principal REQs `5300146420`, `5300187244`
- Supersedes: only the 2026-08-14 Decision 0008 amendment clause
  "No Decision 0009"
- Does not supersede: 0005, 0006, 0007, or 0008 (those records stay accepted)
- Does not PASS: any technical or readiness blocker
- Source (FINAL architecture, updated in place):
  https://github.com/Dezocode/Sai/pull/62#issuecomment-5303750100
- Also binds: 5303751556, 5303753512 (amended), 5303755356 (amended),
  5303757105, 5303804678, 5303809236, 5300146420, 5300187244
- Observed head at original post:
  `abae75d42e675d781be8b4041ea62fc8773defdc`
  (bind live exact state, not this snapshot)

## Decision

SAI keeps **one** quality/control architecture (0005) and **one** persistent
logical Primary (0008). This record adds the **Trusted Saul Comptroller** and a
**nested SHA-bound product-quality loop**. The two loops must not collapse.

Cursor can never be Saul. Sai does not technically PASS. Human review/merge
is outside Ralph.

### 1. Relationship to 0005–0008

This record **appends** 0005/0006/0008 plus REQs 5300146420 and 5300187244.
It does **not** weaken their safety, authorization, trusted-reviewer, or
orchestration invariants, and does **not** fully supersede 0005–0008. The
only superseded text is 0008's 2026-08-14 sentence "No Decision 0009".
`B-SAUL-QUALITY-LOOP-001` remains a separate blocker.

### 2. Two loops (must not collapse)

**OUTER — Ralph / logical Primary**

```text
while READY_FOR_HUMAN_REVIEW != true:
  observe current GitHub/repo truth
  integrate worker / CI / Saul / Sai events
  REASSESS_BLOCKERS
  if machine-actionable work:
    named Cora → named contractor(s)
    Primary integrates exact state
    require real Hostinger Saul inner loop
  continue
```

**INNER — real Hostinger Saul** (existing `saul-runner`: Codex CLI, trusted
Comptroller MCP, GitHub App bridge, Hostinger Ed25519 identity)

```text
exact state Hn
  → trusted Comptroller manifest
  → SHA-bound shards + LOCAL_ARCH + IMPACT_ARCH
  → findings + GitHub Checks
  → Ralph remediation
  → Hn+1
  → Saul again
SYSTEM_ARCH is mandatory before technical convergence.
```

Sai wakes **only** on cryptographic real-Saul technical convergence of the
exact current state. Sai FAIL → Ralph continues. Only
`READY_FOR_HUMAN_REVIEW == true` terminates Ralph. Human review/merge is
outside Ralph.

### 3. Physical ≠ logical primary

Physical Cursor `bcId` runtimes are disposable. The logical Primary
(`pr62-primary` for PR #62) is durable.

A physical turn/runtime ending, emptied todos, CI green, `SAUL_PENDING`,
Saul APPROVE alone, or Sai APPROVE alone **must not** set `DONE` /
`COMPLETE` / `FULFILLED` / `TERMINAL` / `READY` unless
`READY_FOR_HUMAN_REVIEW` is true.

Resume observes live repo/GitHub truth and enters `REASSESS_BLOCKERS`.
Conversational memory is not the program.

### 4. REASSESS_BLOCKERS is the universal nonterminal return edge

`REASSESS_BLOCKERS` is Primary-only and remains the last control todo while
the program is nonterminal. Empty todos are not exit. `BLOCKERS>0` continues
Ralph. `SAUL_PENDING` is not idle-stop: continue every safe
machine-actionable Cora→contractor item. Cheap wait only when the frontier
is genuinely externally blocked.

### 5. SHA-bound shards

A shard is a bounded review unit **derived from the exact Git SHA** Saul is
reviewing, not a worker bucket. Bind at minimum: repo, `base_sha`,
`head_sha`, `diff_digest`, unit identity, content digest, semantic/context
digest, dependency/architecture context.

Unchanged **and** context-equivalent proof MAY carry forward. Otherwise
`STALE` (`STALE_CODE` | `STALE_CONTEXT` | `STALE_ARCHITECTURE`). One failed
shard must not stop independent shard/architecture discovery. Moving HEAD
invalidates only proof whose code/context/dependency/architecture binding
changed.

### 6. Nested architecture review

Every material integrated exact state requires
`CODE + LOCAL_ARCH + IMPACT_ARCH`. `SYSTEM_ARCH` is required before
technical convergence. 100% current shard PASS without current architecture
PASS is not technical convergence.

`SYSTEM_ARCH` (and LOCAL/IMPACT where in scope) must cover: source-of-truth,
authorization, trust, identity, persistent Primary, multi-runtime isolation,
Ralph, Cora, contractor isolation, blockers, Saul trust, Sai, GitHub events,
resume, CI, workflow security, persistence, schemas, dependency direction,
observability, concurrency, failure topology, resource bounds, simplicity,
reviewability, anti-ballooning.

### 7. GitHub Checks and authenticity

One aggregate Check: `Saul / Product Quality`. Generated per-blocker Checks:
`Saul / Blocker / <ID>` from the **canonical ledger**. Not one workflow per
blocker.

`IMPLEMENTED_AWAITING_SAUL` is not success. Ordinary CI is not Saul
clearance. The `saul-runner-comptroller` GitHub App is GitHub transport
identity, **not** Saul identity. Hostinger Ed25519 exact-state attestation
(`codex_invoked=true`, `synthetic=false`) is technical identity proof.

Candidate must not contain the App private key, JWT, installation token, or
Saul signing key. Cursor/Cora/contractor/ordinary CI/Sai must not mint
substitute Saul evidence. Candidate-generated keys fail. Ordinary CI may
verify public Ed25519 evidence; it may not mint PASS.

### 8. Domain-aware quality REFERENCES (not imported frameworks)

Keep **ONE** Decision-0005 quality system. External repositories are
**reference exemplars**. Do **not** treat `rust-lang/rust` as a universal
product template. Do **not** create rust/go/swift/openssf quality
subsystems.

| Domain | Reference |
|---|---|
| Control-plane / quality-as-code | `rust-lang/rust` |
| Go core/backend/runtime | `tailscale/tailscale` |
| Swift/SwiftUI product | `element-hq/element-x-ios` |
| Swift state/effect/testability principles | `pointfreeco/swift-composable-architecture` (**principles only**, not a mandatory dependency) |
| Modular SwiftUI example | `pointfreeco/isowords` |
| Swift-native tooling | `swiftlang/swift-format`, `swiftlang/swift-testing` |
| Security / supply chain | OpenSSF OSPS Baseline + Scorecard |

Mapping (machine-readable; feeds 0005; contractors encode — not this write):

```text
domain → properties → 0005 invariant → detector/CI → Saul judgment → blocker Check
```

Statuses: `IMPLEMENTED` | `NOT_APPLICABLE` (+ reason) | `BLOCKER` |
`DEFERRED_NONBLOCKING` (+ Saul-approved rationale). Documentation alone
does not satisfy an executable property. Saul selects applicable properties
by changed domain and rejects blind copying, framework proliferation, and
incompatible architecture importation.

### 9. Anti-ballooning

One quality backbone, one blocker universe, one readiness predicate, one
Check projection. Reuse-before-add. Prefer deletion/consolidation. Reference
breadth must reduce sprawl, not multiply frameworks. Classify additions
`REQUIRED_FOR_CURRENT_BLOCKER` | `REQUIRED_FOR_FINAL_MERGE_QUALITY` |
`DEFER_TO_FOLLOWUP`. Do not create a second anti-ballooning framework.

Finding → CI: Saul finding → canonical blocker → remediation → smallest
0005 guard → mandatory CI → Saul exact-state revalidation.

### 10. Clearance ordering

`B-RALPH-BLOCKER-CI-CONVERGENCE-001` clears **last** among required
technical/quality/architecture/readiness blockers. Saul must not PASS it
while another required blocker remains non-passing. A new Saul-discovered
blocker immediately falsifies technical convergence and returns work to
Ralph.

Technical PASS requires authentic Hostinger Saul on the exact current state
(`PASSED_BY_SAUL`). Implementation actors may only reach
`IMPLEMENTED_AWAITING_SAUL`. Sai may PASS governance only (`PASSED_BY_SAI`).
This officer record does **not** PASS any blocker.

### 11. Repo-enforced rejects (not prompt-enforced)

The repository must reject:

1. `READY_FOR_HUMAN_REVIEW=false` AND program marked complete
2. required blocker remains AND program terminal
3. required blocker exists AND absent from canonical Check/ledger projection
4. technical blocker exists AND no corresponding Saul gate

### Terminal invariant

```text
logical_program_terminal = READY_FOR_HUMAN_REVIEW == true
```

READY_FOR_HUMAN_REVIEW requires current requirements/CI; every required
technical/quality/architecture/readiness blocker current authentic Saul
PASS; complete current shard coverage; LOCAL/IMPACT/SYSTEM architecture
PASS; valid Hostinger Ed25519 evidence; Sai approval of the same exact
state; no hidden/stale blocker or approval. Then stop for Dezocode. Do not
merge. Do not mark ready.

## Context

PR #62 already had registry-driven health (0005), repo-native authorization
and independent Saul (0006), Runtime Intelligence (0007), and a persistent
Primary/Ralph loop (0008). Comments 5300146420/5300187244 required a nested
SHA-bound Saul product-quality loop with cryptographic attestation. Comment
5303750100 (updated 2026-08-15) is the FINAL architecture, amended by
5303804678/5303809236 so `rust-lang/rust` is the control-plane reference
only. Cora ingested four P0s on contract v12 without A-013/v13. This
officer record persists the architecture; it does not implement it and does
not PASS those blockers.

## Alternatives considered

- Collapse Ralph and Saul into one Cursor loop — rejected; Cursor can never be Saul.
- rust-lang/rust as universal product template — rejected; domain-aware references, one 0005 system.
- Decision 0010 for quality references — rejected; this record is the single 0009.
- One workflow per blocker — rejected; generate Checks from the canonical ledger.
- Prompt-only READY/DONE discipline — rejected; repo-enforced rejects required.
- Idle-wait on SAUL_PENDING or empty todos — rejected.
- Sai/Cursor self-pass of technical blockers — rejected; `TECHNICAL_CLEARANCE_REQUIRES_SAUL`.

## Rationale

Physical Cloud turns end. Quality and blockers must remain reconstructible
from Git + GitHub Checks + cryptographic Saul evidence. Nested SHA-bound
review plus domain-aware references let Saul judge each change against the
right exemplar without importing foreign control planes.

## Consequences

- Officer: this record, architecture.md projection, 0008 one-sentence supersession, optional orchestration pointer.
- Cora: v12 reuse; four DISCOVERED P0s; no v13.
- Contractors implement the executable loop, Check projection, mapping YAML, anti-balloon guards, and readiness rejects under existing leases. Not this officer write.
- Saul remains the only technical clearance authority. Sai wakes only after cryptographic technical convergence.
- Do not merge. Do not mark ready. Agents never merge PR #62.
