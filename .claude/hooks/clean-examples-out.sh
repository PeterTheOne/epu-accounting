#!/bin/bash
# SessionEnd hook: remove generated test output from examples/out/, keeping .keep.
dir="${CLAUDE_PROJECT_DIR:-.}/examples/out"
[ -d "$dir" ] || exit 0
find "$dir" -mindepth 1 -maxdepth 1 ! -name '.keep' -exec rm -rf {} +
exit 0
