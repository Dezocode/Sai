#!/usr/bin/env bash
# agent-path-guards.sh — shared argument and path validation for scaffold scripts.
# Sourced by agent-scaffold, agent-memory-scaffold, agent-contract-scaffold.
set -euo pipefail

# Resolve paths for containment checks: normalize missing tail components and
# follow existing symlinks so out-of-subtree targets cannot pass prefix checks.
# macOS realpath lacks -m; python3 realpath(strict=False) is the portable fallback.
guard_normalize_path() {
  local path=$1
  if command -v realpath >/dev/null 2>&1 && realpath -m / >/dev/null 2>&1; then
    realpath -m "$path"
    return
  fi
  python3 - "$path" <<'PY'
import os, sys
print(os.path.realpath(sys.argv[1], strict=False))
PY
}

guard_slug() {
  local label=$1 value=$2
  if [ -z "$value" ]; then
    echo "guard: $label is empty" >&2
    return 1
  fi
  case "$value" in
    *[!a-z0-9-]*|*--*|-*|*-)
      echo "guard: invalid $label '$value' (lowercase slug [a-z0-9-] only)" >&2
      return 1 ;;
  esac
  case "$value" in
    [a-z0-9]*) ;;
    *)
      echo "guard: invalid $label '$value' (must start with [a-z0-9])" >&2
      return 1 ;;
  esac
}

guard_agent_id() {
  local value=$1
  if [ -z "$value" ]; then
    echo "guard: agent-id is empty" >&2
    return 1
  fi
  case "$value" in
    *[!a-z0-9-]*|*--*|-*|*-)
      echo "guard: invalid agent-id '$value'" >&2
      return 1 ;;
  esac
  case "$value" in
    [a-z]*) ;;
    *)
      echo "guard: invalid agent-id '$value' (must start with a letter)" >&2
      return 1 ;;
  esac
}

guard_contract_id() {
  local value=$1
  case "$value" in
    [0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-*)
      local rest="${value#????????-}"
      case "$rest" in
        *..*|*/*|' '*|*'\\'*)
          echo "guard: invalid contract-id '$value'" >&2
          return 1 ;;
      esac
      case "$rest" in
        *-dezocode)
          local body="${rest%-dezocode}"
          body="${body%-}"
          guard_slug contract-id-body "$body" || return 1
          ;;
        *-monaecode)
          local body="${rest%-monaecode}"
          body="${body%-}"
          guard_slug contract-id-body "$body" || return 1
          ;;
        *)
          echo "guard: contract-id must end with -dezocode or -monaecode: $value" >&2
          return 1 ;;
      esac
      ;;
    *)
      echo "guard: invalid contract-id '$value' (expected YYYYMMDD-<slug>-<principal>)" >&2
      return 1 ;;
  esac
}

guard_repo_name() {
  local value=$1
  case "$value" in
    Dezocode/Sai|monaecode/Sai) ;;
    *)
      echo "guard: repository must be Dezocode/Sai or monaecode/Sai, got '$value'" >&2
      return 1 ;;
  esac
}

guard_charter_path() {
  local repo_root=$1 charter=$2
  case "$charter" in
    .ai/agents/_roles/*) ;;
    *)
      echo "guard: charter must be under .ai/agents/_roles/: $charter" >&2
      return 1 ;;
  esac
  local resolved roles_root
  resolved=$(guard_normalize_path "$repo_root/$charter")
  roles_root=$(guard_normalize_path "$repo_root/.ai/agents/_roles")
  case "$resolved" in
    "$roles_root"/*) ;;
    *)
      echo "guard: charter escapes _roles subtree: $charter" >&2
      return 1 ;;
  esac
  if [ ! -f "$resolved" ]; then
    echo "guard: charter file not found: $charter" >&2
    return 1
  fi
}

guard_agent_folder_rel() {
  local repo_root=$1 folder_rel=$2
  case "$folder_rel" in
    .ai/agents/[a-z0-9]*) ;;
    *)
      echo "guard: folder must match .ai/agents/<slug>: $folder_rel" >&2
      return 1 ;;
  esac
  local slug="${folder_rel#.ai/agents/}"
  guard_slug folder-slug "$slug" || return 1
  local resolved agents_root
  resolved=$(guard_normalize_path "$repo_root/$folder_rel")
  agents_root=$(guard_normalize_path "$repo_root/.ai/agents")
  case "$resolved" in
    "$agents_root"/*) ;;
    *)
      echo "guard: folder escapes .ai/agents/: $folder_rel" >&2
      return 1 ;;
  esac
}

guard_under_ai_subtree() {
  local repo_root=$1 rel_path=$2 subtree=$3
  case "$rel_path" in
    *..*)
      echo "guard: path traversal in $rel_path" >&2
      return 1 ;;
  esac
  local resolved base
  resolved=$(guard_normalize_path "$repo_root/$rel_path")
  base=$(guard_normalize_path "$repo_root/.ai/$subtree")
  case "$resolved" in
    "$base"/*|"$base") ;;
    *)
      echo "guard: path '$rel_path' not under .ai/$subtree/" >&2
      return 1 ;;
  esac
}

guard_json_safe_string() {
  local label=$1 value=$2
  if ! printf '%s' "$value" | python3 -c "
import sys
for ch in sys.stdin.read():
    if ord(ch) < 32 or ch in '\\\\\"':
        sys.exit(1)
" 2>/dev/null; then
    echo "guard: $label contains disallowed control or quote characters" >&2
    return 1
  fi
}
