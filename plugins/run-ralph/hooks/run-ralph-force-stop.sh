#!/bin/bash
# run-ralph force-stop (PostToolUse hook, matcher: Bash)
#
# Purpose
#   Force-terminate the ralph-loop iteration whenever the Worker removes the
#   Phase 6 report sentinel. Removing `.ralph/.report-pending` is the explicit
#   "this run is done" signal the choo-choo SKILL teaches the Worker to use,
#   so we piggyback on it: deleting the ralph-loop state file at the same
#   moment guarantees that the next Stop event lets the session exit cleanly,
#   regardless of whether ralph-loop's own stop-hook can detect the
#   `<promise>...</promise>` tag.
#
# Why this exists
#   `claude-plugins-official/ralph-loop` 1.0.0 stop-hook detects completion by
#   parsing the transcript JSONL with `jq -rs ... last`, then perl-extracting
#   `<promise>...</promise>` from the last assistant text block. Two failure
#   modes are documented (memory/project_ralph_loop_promise_detection_bug.md):
#     1. Transcript thinking-signature lines contain raw control characters
#        that break `jq -rs` slurp parsing.
#     2. The last text block is not the one carrying the promise tag (e.g.,
#        Worker added an acknowledgment after the promise).
#   Either failure causes the loop to silently re-inject the same prompt up to
#   --max-iterations. Upstream (anthropics/claude-plugins-public@main) has the
#   same code as our 1.0.0 cache, so a fix needs to come from us.
#
# Trigger contract
#   - Hook event: PostToolUse, matcher "Bash"
#   - Stdin: JSON payload {tool_name, tool_input.command, ...}
#   - Reaction: only when tool_name == "Bash" AND command contains an `rm`
#     of a path ending in `.ralph/.report-pending`. Anything else: silent exit.
#   - Effect: if `${CLAUDE_PROJECT_DIR}/.claude/ralph-loop.local.md` exists,
#     remove it. Next Stop event sees no state file → ralph-loop's stop-hook
#     exits 0 → session ends.
#
# CWD-independence
#   Anchors paths to ${CLAUDE_PROJECT_DIR}, never to CWD. A Worker that `cd`d
#   into a sub-directory mid-loop must still trigger correctly.
#
# Idempotency
#   If the state file is already gone (loop was never running, or another hook
#   beat us to it), this is a silent no-op.
#
# Disable
#   Toggle the run-ralph plugin off via `/plugin`. The Phase 6 instruction in
#   choo-choo's SKILL.md remains as a weaker fallback (Worker still emits the
#   promise tag, ralph-loop still tries to detect it).

set -euo pipefail

HOOK_INPUT=$(cat)

# PostToolUse fires for every tool. React only to Bash.
TOOL_NAME=$(echo "$HOOK_INPUT" | jq -r '.tool_name // ""')
[[ "$TOOL_NAME" == "Bash" ]] || exit 0

COMMAND=$(echo "$HOOK_INPUT" | jq -r '.tool_input.command // ""')

# Trigger only when the Phase 6 report sentinel is being removed.
# Match `rm` (with any flags / quoting) followed by a path ending in
# `.ralph/.report-pending`. Both single- and multi-rm bash lines work.
if ! echo "$COMMAND" | grep -qE 'rm[[:space:]].*\.ralph/\.report-pending'; then
  exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
STATE_FILE="${PROJECT_DIR}/.claude/ralph-loop.local.md"

if [[ -f "$STATE_FILE" ]]; then
  rm -- "$STATE_FILE"
  echo "[run-ralph-force-stop] ralph-loop state file removed (Phase 6 sentinel cleared) — loop terminated." >&2
fi

exit 0
