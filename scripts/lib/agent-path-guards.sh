#!/usr/bin/env bash
# agent-path-guards.sh — shared argument and path validation for scaffold scripts.
# Sourced by agent-scaffold, agent-memory-scaffold, agent-contract-scaffold.
set -euo pipefail

# Portable equivalent of GNU realpath -m (path need not exist; do not follow symlinks).
# Always use python3 so Linux (realpath -m) and macOS (no -m) behave identically.
guard_normalize_path() {
  local path=$1
  python3 - "$path" <<'PY'
import os, sys
path = os.path.expanduser(sys.argv[1])
if not os.path.isabs(path):
    path = os.path.join(os.getcwd(), path)
print(os.path.normpath(path))
PY
}

# Reject when any existing component under repo_root/rel_path is a symlink.
# Prevents scaffold scripts from writing outside the repository through link hops.
guard_reject_symlink_components() {
  local repo_root=$1 rel_path=$2
  python3 - "$repo_root" "$rel_path" <<'PY'
import os, sys
root, rel = sys.argv[1], sys.argv[2]
cur = root
for part in rel.replace("\\", "/").split("/"):
    if not part or part == ".":
        continue
    if part == "..":
        print(f"guard: path traversal in {rel}", file=sys.stderr)
        sys.exit(1)
    cur = os.path.join(cur, part)
    if os.path.islink(cur):
        print(f"guard: symlink not allowed in repository path: {cur}", file=sys.stderr)
        sys.exit(1)
PY
}

# When rel_path (or ancestors) exist, verify realpath stays under base_rel.
guard_realpath_under_base() {
  local repo_root=$1 rel_path=$2 base_rel=$3
  python3 - "$repo_root" "$rel_path" "$base_rel" <<'PY'
import os, sys
root, rel, base_rel = sys.argv[1], sys.argv[2], sys.argv[3]
parts = [p for p in rel.replace("\\", "/").split("/") if p and p != "."]
if ".." in parts:
    print(f"guard: path traversal in {rel}", file=sys.stderr)
    sys.exit(1)
full = os.path.join(root, *parts) if parts else root
base = os.path.join(root, base_rel)
prefix = root
for part in parts:
    prefix = os.path.join(prefix, part)
    if os.path.exists(prefix):
        real = os.path.realpath(full)
        real_base = os.path.realpath(base)
        if not (real == real_base or real.startswith(real_base + os.sep)):
            print(f"guard: resolved path escapes {base_rel}: {rel}", file=sys.stderr)
            sys.exit(1)
        break
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
  guard_reject_symlink_components "$repo_root" "$folder_rel"
  guard_realpath_under_base "$repo_root" "$folder_rel" ".ai/agents"
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
  guard_reject_symlink_components "$repo_root" "$rel_path"
  guard_realpath_under_base "$repo_root" "$rel_path" ".ai/$subtree"
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
  case "$value" in
    *$'\n'*|*$'\r'*|*$'\t'*|*\\*|*\"*)
      echo "guard: $label contains disallowed control or quote characters" >&2
      return 1
      ;;
  esac
}
