#!/bin/bash
# PreToolUse hook (Bash|Read|Grep|Glob): blocks access to private financial data —
# the input/ and output/ directories and any .csv, .pdf, .db or .sqlite file
# (including -journal/-wal side files), wherever it lives (e.g. *.db in the repo root).
# Exception: anything under examples/ (test fixtures; examples/out/ is scratch space).
payload=$(cat)
tool=$(jq -r '.tool_name // empty' <<<"$payload")
root="${CLAUDE_PROJECT_DIR:-$PWD}"

ext_re='\.(csv|pdf|db|sqlite3?)([^[:alnum:]_]|$)'
dir_re="(^|[[:space:]'\"=./])(input|output)(/|\$|[[:space:]'\";|&)])"

block() {
  echo "Blocked by project hook: $1 (private financial data: input/, output/, or a .csv/.pdf/.db file). Use the fixtures in examples/ for testing and write temp output to examples/out/, or ask the user to run it themselves." >&2
  exit 2
}

# Is a path (relative to the repo root) private?
is_private_path() {
  local rel="${1#"$root"/}"; rel="${rel#./}"
  [[ "$rel" != *..* && "$rel" == examples/* ]] && return 1
  grep -Eiq "$ext_re" <<<"$rel" || grep -Eiq '^(input|output)(/|$)' <<<"$rel"
}

case "$tool" in
  Read|Grep|Glob)
    p=$(jq -r '.tool_input.file_path // .tool_input.path // empty' <<<"$payload")
    if [ -n "$p" ] && is_private_path "$p"; then
      block "this path references it"
    fi
    # Grep/Glob filters that target private files (e.g. glob "*.db", type "csv"),
    # unless the search is scoped to examples/
    [ "$tool" = Read ] && exit 0
    rel="${p#"$root"/}"; rel="${rel#./}"
    [[ "$rel" != *..* && "$rel" == examples* ]] && exit 0
    filt=$(jq -r '[.tool_input.glob, .tool_input.type, (if .tool_name == "Glob" then .tool_input.pattern else null end)]
                  | map(select(. != null)) | join(" ")' <<<"$payload")
    if grep -Eiq '(^|[^[:alnum:]])(csv|pdf|db|sqlite3?)([^[:alnum:]_]|$)|(^|/)(input|output)(/|$)' <<<"$filt"; then
      block "this search filter targets it"
    fi
    ;;
  Bash)
    cmd=$(jq -r '.tool_input.command // empty' <<<"$payload")
    [ -z "$cmd" ] && exit 0
    cmd="${cmd//"$root"\//}"   # treat absolute project paths like relative ones
    # Drop examples/... path tokens before checking (never when ".." could escape examples/)
    if [[ "$cmd" != *..* ]]; then
      cmd=$(sed -E "s#(^|[[:space:]'\"=])(\./)?examples/[^[:space:]'\";|&)]*#\1#g" <<<"$cmd")
    fi
    if grep -Eiq "$dir_re" <<<"$cmd" || grep -Eiq "$ext_re" <<<"$cmd"; then
      block "this command references it"
    fi
    # Wildcards that expand to private files (e.g. "sqlite3 *.d?", "cat */*")
    cd "$root" 2>/dev/null || exit 0
    shopt -s nullglob
    set -f; toks=($(tr "'\"();|&<>\`" ' ' <<<"$cmd")); set +f
    for tok in "${toks[@]}"; do
      [[ "$tok" == *[\*\?\[]* ]] || continue
      for f in $tok; do
        is_private_path "$f" && block "the wildcard '$tok' matches $f"
      done
    done
    # Recursive searches that don't honour .gitignore read private files in the repo
    if grep -Eq '(^|[^[:alnum:]_-])(e|f)?grep[[:space:]]([^|;&]*[[:space:]])?(-[[:alnum:]]*[rR][[:alnum:]]*|--recursive|--dereference-recursive)([[:space:]]|$)' <<<"$cmd" \
       || grep -Eq '(^|[^[:alnum:]_-])rg[[:space:]][^|;&]*(-[[:alnum:]]*u|--no-ignore|--binary|-a([[:space:]]|$))' <<<"$cmd"; then
      block "recursive grep (or rg without .gitignore) would read it — use the Grep tool or 'git grep' instead"
    fi
    ;;
esac
exit 0
