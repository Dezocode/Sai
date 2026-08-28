# Graduation plan schema draft (v0)

Plan-bound executor contract. Engine executes ONLY validated plans bound to exact prototype HEAD.

plan_id = SHA256(schema_version, repo, base, prototype_head, graph_hash, operations)

Operations: integrate | spinoff | delete-archive

Dispositions: REUSE, PROMOTE, EXPORT, REMOTE, PROMOTE_SHARED, DROP (UNKNOWN fails closed).
