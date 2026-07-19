---
name: splunk-siem-expertise
description: Splunk Enterprise/Cloud and SIEM competitor expertise — use when designing ingest, search, dashboards, alerts, CIM/data models, or writing competitive-landscape and architecture docs for splunk-clone.
---

# Splunk & SIEM expertise

## When to use

- Deliverables D1, D2, D3–D6 design decisions
- Any question about Splunk vs Elastic/Wazuh/Graylog/Sentinel
- Detection rules, correlation, network/security status dashboards

## Splunk reference areas (MVP mapping)

| Splunk concept | Prototype direction |
|---|---|
| Universal Forwarder / HEC | Lightweight agent or HTTP ingest in `src/ingest/` |
| Indexes & sourcetypes | Partitioned storage + schema in architecture doc |
| SPL | Document subset or alternative query API in `src/search/` |
| CIM / ES | Field normalization + use-case templates in docs |
| Dashboards & alerts | `src/ui/` + `src/alerts/` |
| RBAC | Roles in integration manifest for future SAI plugin |

## Output standards

- Cite official Splunk docs and competitor docs when making parity claims.
- Record decisions in `splunk-clone/docs/` with date and owner-visible rationale.
- Prefer operable MVP over full Enterprise parity unless monaecode expands scope via contract amendment.
