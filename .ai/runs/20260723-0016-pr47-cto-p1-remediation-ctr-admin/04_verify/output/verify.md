# Verify — P1 remediation

Pre-commit checks planned:

- `git diff origin/main -- .ai/INITIALIZE.md` → empty (restored)
- deepdive `metadata.json` `head_sha` == `739b3f4ffe12d98e6dd4fd65a9475ed91e8f78e4`
- `scripts/verify-semantic-hierarchy`
- `scripts/verify-agent-audit -n 10 HEAD`
- `scripts/verify-merge-handoff origin/main..HEAD`
- remote SHA after push
