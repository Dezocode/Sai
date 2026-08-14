# Plan — live contract revision on Saul callers

`qualifying_saul_review` already binds exact HEAD + revision.
Two callers compared the review to itself:

1. `attempt_clear` passed `doc.contract_revision` instead of the live
   pointer `current_revision`.
2. `consume` passed `review.implementation_head` and
   `review.contract_revision` instead of `a.head_sha(root)` and pointer
   `current`.

Fix: pointer revision required when present; hermetic fixtures without
a pointer fall back to the review revision. Consume writes tracked YAML
only after qualification. Fixture: signed rev 11 vs live v12 → REJECT
INVALID_SAUL_IDENTITY. Do not PASS. Do not push. Keep
`sai_auth_review.py` at 500 lines. Do not change qualify predicates.
