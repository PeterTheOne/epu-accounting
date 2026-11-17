#!/bin/bash
# PreToolUse hook (Bash|Read|Grep): blocks access to private financial data —
# the input/ and output/ directories and any .csv, .pdf or .db file.
# Exception: anything under examples/ (test fixtures; examples/out/ is scratch space).
payload=$(cat)
tool=$(jq -r '.tool_name // empty' <<<"$payload")
root="${CLAUDE_PROJECT_DIR:-$PWD}"

ext_re='\.(csv|pdf|db)([^[:alnum:]_]|$)'
dir_re="(^|[[:space:]'\"=./])(input|output)(/|\$|[[:space:]'\";|&)])"

block() {
  echo "Blocked by project hook: $1 references input/, output/, or a .csv/.pdf/.db file (private financial data). Use the fixtures in examples/ for testing and write temp output to examples/out/, or ask the user to run it themselves." >&2
  exit 2
}

case "$tool" in
  Read|Grep)
    p=$(jq -r '.tool_input.file_path // .tool_input.path // empty' <<<"$payload")
    [ -z "$p" ] && exit 0
    rel="${p#"$root"/}"; rel="${rel#./}"
    [[ "$rel" != *..* && "$rel" == examples/* ]] && exit 0
    if grep -Eiq "$ext_re" <<<"$rel" || grep -Eiq '^(input|output)(/|$)' <<<"$rel"; then
      block "this path"
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
      block "this command"
    fi
    ;;
esac
exit 0
