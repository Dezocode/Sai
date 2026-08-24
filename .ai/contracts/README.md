# SAI Contracts

Versioned contract artifacts for contractor agents. Canonical in Git;
mirrored to Drive per `.ai/_config/sync-policy.md`.

## Layout

```
.ai/contracts/
  README.md
  _templates/           <- runtime-specific contract frameworks
  <contract-id>/
    contract.json       <- validated by contract.schema.json
    contract.md         <- human-readable; owner-editable
    onboarding-prompt.md <- paste-ready prompt for owner
    amendments/
    reviews/            <- CONTRACT_REVIEW and Sai audit records
```

## Contract ID format

`YYYYMMDD-<project-slug>-<principal-slug>`

Example: `20260715-splunk-clone-monaecode`

## Creating a contract

```bash
scripts/agent-contract-scaffold \
  --project-name "Cybersecurity Splunk Clone" \
  --project-slug splunk-clone \
  --principal monaecode \
  --contractor-type coding \
  --isolation-mode prototype \
  --runtime claude \
  --repository monaecode/Sai
```

## Reviewing contractor work

```bash
scripts/agent-contract-pr-review \
  --contract-id 20260715-splunk-clone-monaecode \
  --branch proj/splunk-clone/ctr-code-alpha1/auth-pipeline
```

## References

- `.ai/ONBOARDING.md` — contractor persona protocol
- `.ai/shared/schemas/contract.schema.json`
- `.ai/agents/_roles/contract-administrator/CHARTER.md`
- Decision 0003 — contractor charters and per-agent memory
