#!/usr/bin/env bash
# Grok RI container entrypoint — high-reasoning experiment path only.
set -euo pipefail
export PATH="/home/ri/.grok/bin:/opt/grok/bin:${PATH:-/usr/bin}"
MODEL="${RI_GROK_MODEL:-grok-4.5}"
EFFORT="${RI_GROK_EFFORT:-high}"
cmd="${1:-status}"
shift || true
case "$cmd" in
  status)
    echo "ri_role=${RI_ROLE:-unknown}"
    echo "org_status=${RI_ORG_STATUS:-PROVISIONAL}"
    echo "never_merge_main=${RI_NEVER_MERGE_MAIN:-1}"
    echo "model=${MODEL}"
    echo "effort=${EFFORT}"
    if command -v grok >/dev/null 2>&1; then
      echo "grok_bin=$(command -v grok)"
      # resolve symlink target for evidence
      if [[ -L "$(command -v grok)" ]]; then
        echo "grok_link=$(readlink -f "$(command -v grok)" 2>/dev/null || readlink "$(command -v grok)")"
      fi
      grok --version 2>&1 | head -5 || true
    else
      echo "grok_bin=MISSING"
      exit 2
    fi
    ;;
  models)
    grok models 2>&1 | head -40
    ;;
  deep-findings)
    if [[ "${EFFORT}" != "high" && "${EFFORT}" != "xhigh" ]]; then
      echo "REFUSED: final RI findings require reasoning_effort=high (got ${EFFORT})" >&2
      exit 3
    fi
    prompt="${*:-Report Runtime Intelligence status only. Do not claim organizational ACTIVE.}"
    exec grok -m "$MODEL" --effort "$EFFORT" -p "$prompt"
    ;;
  deny-merge)
    echo "DENIED: Runtime Intelligence subprocess may never merge to main" >&2
    exit 13
    ;;
  *)
    echo "usage: ri-entrypoint status|models|deep-findings|deny-merge" >&2
    exit 64
    ;;
esac
