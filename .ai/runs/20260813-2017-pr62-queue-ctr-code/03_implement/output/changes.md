# Implement — CTO-029 introducer provenance

- `sha_bound_rows()` no longer accepts a HEAD pin because issuer is an
  officer and `issuer_grant` matches a HEAD grant.
- Each pin requires non-empty `source` and 40-hex `introduced_by_sha`.
- Loader `git cat-file -e` the intro SHA and pin path, extracts the pin
  blob from that commit (not dirty WT), and requires the same
  sha/agent_id/task_id/authorization_id.
- Introducing commit Agent must be `ceo` or `ctr-admin`. `matching_grant`
  at intro SHA (commit-time grants, `use_pins=False`) must cover that
  officer+task_id. Pin `issuer_grant` must match intro Authorization-ID.
- `source` and `issuer_grant` are bound from the intro blob.
- Negatives: missing/wrong `introduced_by_sha`; rewritten HEAD grant.
- Did not write `.ai/authorizations/**` (Sai `e84e5d7` → `2a57842`).
- Appended CTO-029 `IMPLEMENTED_AWAITING_SAUL`. CTO-025 stays
  `BLOCKED_EXTERNAL`. Did not disable `saul-review.yml` `pull_request`.
- Did not PASS. Did not merge.
