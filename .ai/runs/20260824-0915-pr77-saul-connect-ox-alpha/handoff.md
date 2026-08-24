# Handoff — 20260824-0915-pr77-saul-connect-ox-alpha

## What changed - headMismatch(s,prHead) helper: session head prefixes can no longer suppress the mismatch flag; head_full or exact head must equal authoritative HEAD (Saul 97373399655). Four unit locks. - probeSessions(): periodic GET of SESSIONS_URL on every load cycle even when /prs is preferred — acceptance requires the live read-only sessions GET regardless of preferred plane (Saul 9737663828
