# Saul review authenticity and anti-spoof clearance

This specification extends Decision 0005, Decisions 0006/0008, `REQ-5300146420`, and principal P0 comment `5300187244`.

## Trust primitive

Do not publish or depend on a secret/API token as proof of Saul identity. Saul authenticity is Ed25519 public-key verification:

- production private key: Hostinger-only, outside Git and candidate worktrees;
- public key / fingerprint: non-secret and auditable;
- candidate code is never authoritative for selecting or replacing the public trust anchor used to clear itself.

The current canonical verifier default path is `.ai/authorizations/saul-attestation-ed25519.pub`, but production clearance must resolve that trust anchor from a protected/default-branch or independently trusted reviewer source, not blindly from candidate HEAD. Before protected-main activation, the trusted Hostinger verifier/public-key source is authoritative.

## Signed review envelope

Every shard result and architecture result that contributes to technical PASS must carry an Ed25519 attestation over a canonical payload that binds at least:

- `attestation.version`;
- `attestation.alg = ed25519`;
- `key_id` / SHA-256 public-key fingerprint;
- repository and PR/program identity;
- contract id and immutable revision;
- base SHA;
- exact implementation HEAD SHA;
- full diff digest;
- review type and scope;
- SHA-bound shard id;
- shard input / manifest digest;
- reviewed-unit digest root;
- architecture domain / architecture proof digest where applicable;
- findings digest;
- disposition;
- real Codex invocation evidence (`codex_invoked=true`, `synthetic=false`);
- review id;
- timestamp.

Any change to a signed field invalidates the signature.

## GitHub Check publication

The single authoritative current-head Check is `Saul / Product Quality`.

The Check publishes no secret material. It must expose enough non-secret proof for audit and deterministic consumption:

- exact base/head;
- key id / public-key fingerprint;
- shard/architecture evidence digests;
- current coverage and blocker summary;
- signature or signature digest plus a retrievable signed envelope;
- final technical convergence state.

A Check name, GitHub actor, PR comment, commit status, YAML `reviewer: saul`, or `runtime: codex` is never sufficient clearance.

## Trusted verification

A canonical deterministic verifier recomputes the exact-state payload and validates the Ed25519 signature using the trusted Saul public key.

The same verifier is consumed by:

1. shard PASS accounting;
2. architecture PASS accounting;
3. technical blocker clearance;
4. `merge_viable_saul` / technical convergence;
5. `READY_FOR_HUMAN_REVIEW`.

No duplicate weaker identity logic may exist.

Fail closed on:

- unsigned evidence;
- wrong key or key id;
- candidate-generated key substitution;
- Cursor/Cora/contractor/Sai fake Saul evidence;
- wrong base or head;
- wrong diff digest;
- wrong shard manifest/input/unit root;
- tampered architecture proof;
- stale proof;
- `synthetic=true`;
- `codex_invoked=false`;
- unparseable or incomplete canonical payload.

## Decision-0005 CI learning guard

This authenticity invariant must become an active Decision-0005 health detector with unconditional CI wiring and positive/negative fixtures.

Positive fixture:

- exact-state shard + architecture evidence signed by a fixture Ed25519 private key validates against its pinned fixture public key.

Required negative fixtures include:

- Cursor-authored fake Saul result;
- unsigned result;
- candidate keypair/public-key substitution;
- wrong trusted public key;
- wrong HEAD;
- wrong base/diff digest;
- tampered shard evidence;
- tampered architecture digest;
- stale review;
- `synthetic=true`;
- `codex_invoked=false`.

Fixture private keys are test-only. The production Hostinger private key is never committed, copied to Cursor, logged, placed in GitHub Check output, or passed to candidate code.

## Clearance invariant

`PASSED_BY_SAUL` means cryptographically authenticated **real Hostinger Saul evidence for the exact current review state**, not a role string.

Therefore Cursor may create arbitrary fake comments, YAML, statuses or similarly named checks and they still cannot clear a technical blocker unless the canonical signed payload validates against the trusted Saul public key and all exact-state proof requirements pass.
