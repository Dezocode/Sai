#!/usr/bin/env bash
#
# scripts/generate-arch-docs.sh — deterministic architecture documentation generator.
#
# Parses function definitions (shell, Go, Python, Swift), computes textual
# call-references between repo-defined functions, applies deterministic tag
# heuristics, and emits:
#   docs/architecture/functions.json
#   docs/architecture/functions.md
#   docs/architecture/architecture.md
#   docs/architecture/functions-intent.md   (created only if missing; NEVER overwritten)
#
# Deterministic: no LLM, no network. generated_at is derived from the source
# commit's commit date, and every listing is sorted (LC_ALL=C). Re-running on
# the same commit produces byte-identical output.
#
# Internal TSV uses ASCII 0x1F (unit separator) as the field delimiter, because
# tab/space/newline are IFS whitespace and `read` would silently collapse empty
# fields and shift every column after them.
#
# Usage: bash scripts/generate-arch-docs.sh
# Exits non-zero with a clear error message if parsing fails.

set -euo pipefail
export LC_ALL=C

VERSION="1.0.0"
REPO_NAME="Sai"
OUT_DIR="docs/architecture"
INTENT_FILE="$OUT_DIR/functions-intent.md"
SEP=$'\x1f'

die() { printf 'error: generate-arch-docs.sh: %s\n' "$*" >&2; exit 1; }

# --- repo root & commit metadata -------------------------------------------
cd "$(dirname "${BASH_SOURCE[0]}")/.." || die "cannot cd to repo root"
command -v git >/dev/null 2>&1 || die "git not found in PATH"
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "not inside a git work tree"

SOURCE_COMMIT="$(git rev-parse HEAD)" || die "git rev-parse HEAD failed"
COMMIT_DATE_RAW="$(git show -s --format=%ci HEAD)" || die "git show --format=%ci failed"
GENERATED_AT="$(date -u -d "$COMMIT_DATE_RAW" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null)" \
  || die "cannot parse commit date '$COMMIT_DATE_RAW' as UTC ISO-8601"

mkdir -p "$OUT_DIR" || die "cannot create $OUT_DIR"
TMP="$(mktemp -d)" || die "cannot create temp dir"
trap 'rm -rf "$TMP"' EXIT

# --- file discovery (tracked files only, sorted) ----------------------------
# shell: *.sh anywhere, plus extensionless scripts under scripts/
mapfile -t SH_FILES < <(git ls-files | grep -E '\.sh$' | sort)
mapfile -t SCRIPT_FILES < <(git ls-files | grep -E '^scripts/' | grep -vE '\.(sh|py)$' | sort)
mapfile -t GO_FILES < <(git ls-files | grep -E '\.go$' | sort)
mapfile -t PY_FILES < <(git ls-files | grep -E '\.py$' | sort)
mapfile -t SWIFT_FILES < <(git ls-files | grep -E '\.swift$' | sort)

TOTAL_FILES=$((${#SH_FILES[@]} + ${#SCRIPT_FILES[@]} + ${#GO_FILES[@]} + ${#PY_FILES[@]} + ${#SWIFT_FILES[@]}))
(( TOTAL_FILES > 0 )) || die "no parseable source files found"

# --- parsers: each emits SEP-separated "line<SEP>name<SEP>signature" ---------
# --- (name may be empty for boundary-only lines, e.g. Python class stmts) ---
parse_shell() {
  awk -v S="\x1f" '{
    s=$0; name=""
    if (match(s, /^function[ \t]+[A-Za-z_][A-Za-z0-9_]*/)) {
      name=substr(s, RSTART, RLENGTH); sub(/^function[ \t]+/, "", name)
    } else if (match(s, /^[A-Za-z_][A-Za-z0-9_]*[ \t]*\(\)/)) {
      name=substr(s, RSTART, RLENGTH); sub(/[ \t]*\(\)$/, "", name)
    }
    if (name != "") {
      sig=s; sub(/^[ \t]+/, "", sig); sub(/[ \t]+$/, "", sig)
      printf "%d%s%s%s%s\n", NR, S, name, S, sig
    }
  }' "$1"
}

parse_go() {
  awk -v S="\x1f" '/^func / {
    s=$0; rest=substr(s, 6); name=""
    if (match(rest, /^\([^)]*\)[ \t]*[A-Za-z_][A-Za-z0-9_]*/)) {
      m=substr(rest, RSTART, RLENGTH); sub(/^\([^)]*\)[ \t]*/, "", m); name=m
    } else if (match(rest, /^[A-Za-z_][A-Za-z0-9_]*/)) {
      name=substr(rest, RSTART, RLENGTH)
    }
    if (name != "") {
      sig=s; sub(/^[ \t]+/, "", sig); sub(/[ \t]+$/, "", sig)
      printf "%d%s%s%s%s\n", NR, S, name, S, sig
    }
  }' "$1"
}

parse_python() {
  awk -v S="\x1f" '{
    s=$0
    tmp=s; sub(/[^ \t].*/, "", tmp); ind=length(tmp)
    rest=s; sub(/^[ \t]*/, "", rest)
    if (match(rest, /^class[ \t]+[A-Za-z_][A-Za-z0-9_]*/)) {
      cn=substr(rest, RSTART, RLENGTH); sub(/^class[ \t]+/, "", cn)
      while (nstack>0 && sind[nstack] >= ind) nstack--
      nstack++; sind[nstack]=ind; snames[nstack]=cn
      printf "%d%s%s%s%s\n", NR, S, "", S, cn   # boundary-only (empty name)
    } else if (match(rest, /^def[ \t]+[A-Za-z_][A-Za-z0-9_]*/)) {
      dn=substr(rest, RSTART, RLENGTH); sub(/^def[ \t]+/, "", dn)
      cn=""
      for (i=nstack; i>=1; i--) if (sind[i] < ind) { cn=snames[i]; break }
      if (cn != "" && ind > 0) name=cn"."dn; else name=dn
      sig=s; sub(/^[ \t]+/, "", sig); sub(/[ \t]+$/, "", sig)
      printf "%d%s%s%s%s\n", NR, S, name, S, sig
    }
  }' "$1"
}

parse_swift() {
  awk -v S="\x1f" '{
    s=$0
    cpos=index(s, "//"); fpos=index(s, "func ")
    if (fpos > 0 && (cpos == 0 || fpos < cpos)) {
      prev=(fpos > 1) ? substr(s, fpos-1, 1) : " "
      if (prev !~ /[.A-Za-z0-9_]/) {
        rest=substr(s, fpos+5)
        if (match(rest, /^[A-Za-z_][A-Za-z0-9_]*/)) {
          name=substr(rest, RSTART, RLENGTH)
          sig=s; sub(/^[ \t]+/, "", sig); sub(/[ \t]+$/, "", sig)
          printf "%d%s%s%s%s\n", NR, S, name, S, sig
        }
      }
    }
  }' "$1"
}

# --- collect definitions: all.tsv = file<SEP>line<SEP>name<SEP>signature -----
: > "$TMP/all.tsv"
emit_defs() { # parser, then files...
  local parser=$1 out f; shift
  for f in "$@"; do
    [ -n "$f" ] || continue
    [ -f "$f" ] || die "source file vanished: $f"
    out=$("$parser" "$f") || die "parser $parser failed on $f"
    while IFS="$SEP" read -r line name sig; do
      printf '%s\x1f%s\x1f%s\x1f%s\n' "$f" "$line" "$name" "$sig"
    done <<< "$out" >> "$TMP/all.tsv"
  done
}
emit_defs parse_shell "${SH_FILES[@]}" "${SCRIPT_FILES[@]}"
emit_defs parse_go "${GO_FILES[@]}"
emit_defs parse_python "${PY_FILES[@]}"
emit_defs parse_swift "${SWIFT_FILES[@]}"
sort -t "$SEP" -k1,1 -k2,2n -o "$TMP/all.tsv" "$TMP/all.tsv"

FUNC_COUNT=$(awk -F"$SEP" '$3 != ""' "$TMP/all.tsv" | wc -l)
(( FUNC_COUNT > 0 )) || die "parsers found zero functions in $TOTAL_FILES files"

# --- calls: textual references to other repo-defined base names in body -----
# body(def) = lines (defline+1) .. (next boundary line - 1) in the same file
awk -F"$SEP" '$3 != "" { n=$3; sub(/.*\./, "", n); print n }' "$TMP/all.tsv" \
  | sort -u > "$TMP/basenames.txt"

declare -A CALLS_OF   # key: "file<SEP>line" -> space-separated sorted calls
while IFS="$SEP" read -r file line name sig; do
  [ -n "$name" ] || continue
  next=$(awk -F"$SEP" -v f="$file" -v l="$line" '$1==f && $2>l {print $2; exit}' "$TMP/all.tsv")
  total=$(wc -l < "$file")
  if [ -n "$next" ]; then body_end=$((next - 1)); else body_end=$total; fi
  body_start=$((line + 1))
  base=${name##*.}
  calls=""
  if (( body_start <= body_end )); then
    calls=$(sed -n "${body_start},${body_end}p" "$file" \
      | grep -o -w -F -f "$TMP/basenames.txt" \
      | grep -v -x -F "$base" \
      | sort -u | tr '\n' ' ' || true)
    calls=$(printf '%s' "$calls" | sed 's/ *$//')
  fi
  CALLS_OF["$file$SEP$line"]="$calls"
done < <(awk -F"$SEP" '$3 != ""' "$TMP/all.tsv")

# --- tags: EXACT rule set, applied in listed order; else `logic` ------------
tag_function() { # name file sig
  local name=$1 file=$2 sig=$3
  local hay tags=()
  hay="$(printf '%s %s %s' "$name" "$file" "$sig" | tr '[:upper:]' '[:lower:]')"
  local fbase=${file##*/}
  local mode
  mode=$(git ls-files -s -- "$file" | awk '{print $1}')
  if [[ $name == "main" || $mode == "100755" ]]; then tags+=(entrypoint); fi
  [[ $hay =~ listen|serve|http|ws|fetch|request|gateway ]] && tags+=(network)
  [[ $hay =~ auth|login|token|secret|credential ]] && tags+=(auth)
  [[ $hay =~ sudo|setuid|chmod|chown|root ]] && tags+=(privileged)
  [[ $hay =~ input|argv|args|param|prompt|flag|read ]] && tags+=(user-input)
  [[ $hay =~ save|write|store|state|db|persist|mkdir ]] && tags+=(persistence)
  [[ $hay =~ tmux|socket|pipe|ipc|message|channel|signal ]] && tags+=(ipc)
  [[ $hay =~ render|display|ui|html|view ]] && tags+=(rendering)
  [[ $hay =~ exec|spawn|popen|system|command|run ]] && tags+=(process-spawn)
  [[ $hay =~ config|env|option|setting ]] && tags+=(config)
  [[ $hay =~ valid|guard|check|verify|lint|audit ]] && tags+=(validation)
  [[ ${file,,} =~ _test|test_ ]] && tags+=(test)
  if ((${#tags[@]} == 0)); then tags+=(logic); fi
  printf '%s' "${tags[*]}"
}

slugify() {
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[^a-z0-9_-]+/-/g; s/^-+//; s/-+$//'
}

json_escape() {
  local s=$1
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}
  s=${s//$'\r'/\\r}
  printf '%s' "$s" | tr -d '\000-\010\013\014\016-\037'
}

# --- master record: file<SEP>line<SEP>name<SEP>sig<SEP>calls<SEP>tags<SEP>anchor
: > "$TMP/records.tsv"
declare -A ANCHOR_SEEN
while IFS="$SEP" read -r file line name sig; do
  [ -n "$name" ] || continue
  calls=${CALLS_OF["$file$SEP$line"]}
  tags=$(tag_function "$name" "$file" "$sig")
  base_anchor=$(slugify "$name")
  [ -n "$base_anchor" ] || base_anchor="fn"
  anchor=$base_anchor
  if [ -n "${ANCHOR_SEEN[$base_anchor]:-}" ]; then
    anchor="${base_anchor}-${ANCHOR_SEEN[$base_anchor]}"
  fi
  ANCHOR_SEEN[$base_anchor]=$(( ${ANCHOR_SEEN[$base_anchor]:-1} + 1 ))
  printf '%s\x1f%s\x1f%s\x1f%s\x1f%s\x1f%s\x1f%s\n' \
    "$file" "$line" "$name" "$sig" "$calls" "$tags" "$anchor" >> "$TMP/records.tsv"
done < <(awk -F"$SEP" '$3 != ""' "$TMP/all.tsv")

component_of() {
  local f=$1
  if [[ $f == */* ]]; then printf '%s' "${f%%/*}"; else printf 'root'; fi
}

# --- functions.json ---------------------------------------------------------
{
  printf '{\n'
  printf '  "generator": "generate-arch-docs.sh",\n'
  printf '  "generator_version": "%s",\n' "$VERSION"
  printf '  "source_commit": "%s",\n' "$SOURCE_COMMIT"
  printf '  "generated_at": "%s",\n' "$GENERATED_AT"
  printf '  "repo": "%s",\n' "$REPO_NAME"
  printf '  "functions": [\n'
  first=1
  while IFS="$SEP" read -r file line name sig calls tags anchor; do
    if (( first )); then first=0; else printf ',\n'; fi
    printf '    {"name": "%s", "file": "%s", "line": %s, "signature": "%s", "calls": [' \
      "$(json_escape "$name")" "$(json_escape "$file")" "$line" "$(json_escape "$sig")"
    cfirst=1
    for c in $calls; do
      if (( cfirst )); then cfirst=0; else printf ', '; fi
      printf '"%s"' "$(json_escape "$c")"
    done
    printf '], "tags": ['
    tfirst=1
    for t in $tags; do
      if (( tfirst )); then tfirst=0; else printf ', '; fi
      printf '"%s"' "$t"
    done
    printf ']}'
  done < "$TMP/records.tsv"
  printf '\n  ]\n}\n'
} > "$OUT_DIR/functions.json"

if command -v python3 >/dev/null 2>&1; then
  python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$OUT_DIR/functions.json" \
    || die "generated functions.json is not valid JSON"
else
  printf 'warning: python3 not found; skipping JSON validation\n' >&2
fi

# --- functions.md -----------------------------------------------------------
GENHDR="<!-- GENERATED by scripts/generate-arch-docs.sh v$VERSION from commit $SOURCE_COMMIT ($GENERATED_AT). DO NOT EDIT — regenerate. Model-written intents: functions-intent.md -->"
{
  printf '%s\n# Functions — %s\n\n' "$GENHDR" "$REPO_NAME"
  prev_file=""
  while IFS="$SEP" read -r file line name sig calls tags anchor; do
    if [[ $file != "$prev_file" ]]; then
      printf '## %s\n\n' "$file"
      prev_file=$file
    fi
    printf '### `%s` — line %s\n\n' "$name" "$line"
    printf -- '- signature: `%s`\n' "$sig"
    printf -- '- tags: %s\n' "$(printf '%s' "$tags" | tr ' ' ', ')"
    if [ -n "$calls" ]; then
      printf -- '- calls: %s\n' "$(printf '%s' "$calls" | sed 's/ /, /g')"
    else
      printf -- '- calls: none\n'
    fi
    printf -- '- component: %s\n' "$(component_of "$file")"
    printf -- '- [intent](functions-intent.md#%s)\n\n' "$anchor"
  done < "$TMP/records.tsv"
} > "$OUT_DIR/functions.md"

# --- architecture.md --------------------------------------------------------
{
  printf '%s\n# Architecture — %s\n\n' "$GENHDR" "$REPO_NAME"
  printf 'Functions grouped by top-level component (directory). Each entry links back to its definition in [functions.md](functions.md).\n\n'
  prev_comp=""
  while IFS="$SEP" read -r file line name sig calls tags anchor; do
    comp=$(component_of "$file")
    if [[ $comp != "$prev_comp" ]]; then
      printf '## Component: %s\n\n' "$comp"
      prev_comp=$comp
    fi
    printf -- '- [[functions.md#%s|%s]] — `%s` line %s\n' "$anchor" "$name" "$file" "$line"
  done < <(sort -t "$SEP" -k1,1 "$TMP/records.tsv" | awk -F"$SEP" '{
      if ($1 ~ /\//) comp=substr($1,1,index($1,"/")-1); else comp="root";
      printf "%s\x1f%s\n", comp, $0
    }' | sort -t "$SEP" -k1,1 -k3,3n | cut -d "$SEP" -f2-)
} > "$OUT_DIR/architecture.md"

# --- functions-intent.md: create ONLY if missing -----------------------------
if [ ! -f "$INTENT_FILE" ]; then
  {
    printf '> MODEL-WRITTEN — not regenerated by scripts/generate-arch-docs.sh. Edit freely.\n\n'
    printf '# Function intents — %s\n\n' "$REPO_NAME"
    printf 'One row per function parsed by the generator. The Intent column is intentionally left empty for a human or agent to fill.\n\n'
    printf '| Function | Intent |\n'
    printf '|---|---|\n'
    while IFS="$SEP" read -r file line name sig calls tags anchor; do
      printf '| <a id="%s"></a> `%s` — `%s:%s` |  |\n' "$anchor" "$name" "$file" "$line"
    done < "$TMP/records.tsv"
  } > "$INTENT_FILE"
  printf 'created %s (model-written intents placeholder)\n' "$INTENT_FILE" >&2
else
  printf 'left existing %s untouched\n' "$INTENT_FILE" >&2
fi

printf 'generated %d functions from %d files (commit %s)\n' "$FUNC_COUNT" "$TOTAL_FILES" "$SOURCE_COMMIT" >&2
