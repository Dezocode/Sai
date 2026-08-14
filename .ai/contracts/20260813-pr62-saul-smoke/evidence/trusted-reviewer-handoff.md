# Trusted-reviewer promotion handoff (INFORMATION only)

This file does **not** confer trust. It does **not** claim
`/opt/sai/trusted-reviewer` is populated. Cursor must not provision
that directory, must not write production keys, and must not SSH
Hostinger.

Blob hashes live in `trusted-reviewer-manifest.yaml`. Operator promotes
**after** independent review of the introducing commit SHA as DATA.

## Next Hostinger steps

1. Independently review this SHA's listed files as DATA (not as a live
   trusted tree). Compare `git hash-object` and sha256 to the manifest.
2. Human copies those blobs to `/opt/sai/trusted-reviewer` with the
   dest paths in the manifest. Repo must not declare that path populated.
3. Place the Ed25519 key at `/opt/sai/saul-attest/ed25519.pem` **outside
   git**. Never commit production private keys.
4. Run the bootstrap binary **from the trusted tree**, not from the
   candidate:

```
SAI_SAUL_BOOTSTRAP=1 \
SAI_TRUSTED_TREE=/opt/sai/trusted-reviewer \
SAI_CANDIDATE_TREE=<pr-worktree-as-data> \
SAI_SAUL_ATTEST_KEY=/opt/sai/saul-attest/ed25519.pem \
/opt/sai/trusted-reviewer/scripts/saul-hostinger-bootstrap-review \
  --head <NEW_SHA>
```

`SAI_CANDIDATE_TREE` is required. `--head` must be a full 40-hex SHA
equal to `git -C "$SAI_CANDIDATE_TREE" rev-parse HEAD`. Missing trusted
invoke/attest is `TRUSTED_REVIEWER_UNAVAILABLE` (exit 1), not
`NOT_HOSTINGER_SAUL` (exit 2).
