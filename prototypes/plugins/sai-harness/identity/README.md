# identity
Canonical identity registry. One registered agent = one persistent channel = one
canonical ID. `aliases.json` maps legacy handles to canonical IDs; `resolve.sh`
fails closed on unknown handles (zero authority for unregistered identities).
