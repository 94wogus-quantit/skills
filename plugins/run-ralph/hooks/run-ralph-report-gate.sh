#!/bin/bash
# run-ralph report gate (Stop hook)
#
# Purpose
#   Force the Worker to write a Phase 6 report when a run-ralph session ends,
#   rather than letting the session exit silently after /ralph-loop emits its
#   completion promise.
#
# CWD-independence
#   This hook anchors every check to ${CLAUDE_PROJECT_DIR}, not CWD. A Worker
#   that `cd`s into a sub-directory (e.g. arkraft-wiki/) during the loop must
#   still trip the gate when Stop fires from anywhere — the sentinel and the
#   ralph-loop state file live at the project root regardless of where the
#   Worker happened to be standing.
#
# Sentinel convention
#   ${CLAUDE_PROJECT_DIR}/.ralph/.report-pending
#     - created by run-ralph:choo-choo Phase 5 (before invoking /ralph-loop)
#     - removed by Phase 6 (after the report is written in the final iteration)
#
# Decision logic
#   1. ${CLAUDE_PROJECT_DIR}/.claude/ralph-loop.local.md exists
#         → /ralph-loop still iterating, defer to ralph-loop plugin's own
#           Stop hook. We exit 0.
#   2. ${CLAUDE_PROJECT_DIR}/.ralph/.report-pending absent
#         → not a run-ralph session (or already reported & cleaned up). Exit 0.
#   3. otherwise
#         → ralph ended AND report missing. Block Stop and inject a prompt.
#
# Disable
#   Disable the run-ralph plugin (`/plugin` toggle). The Phase 6 instruction
#   in choo-choo's SKILL.md remains as a weaker fallback.
#
# Orphan sentinel recovery
#   If a previous run-ralph session crashed and left .ralph/.report-pending
#   behind, a fresh /run-ralph:choo-choo will overwrite it (Phase 5 `touch` is
#   idempotent), or you can `rm` it manually before running.

set -euo pipefail

# Drain stdin (Claude Code feeds hook input JSON here — unused by this gate).
cat > /dev/null

# Fall back to current dir if CLAUDE_PROJECT_DIR is unset (defensive — Claude
# Code normally sets it for hook invocations).
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"

[[ -f "${PROJECT_DIR}/.claude/ralph-loop.local.md" ]] && exit 0
[[ ! -f "${PROJECT_DIR}/.ralph/.report-pending" ]] && exit 0

jq -n --arg pd "$PROJECT_DIR" '{
  "decision": "block",
  "reason": ("Ralph 종료가 감지됐지만 run-ralph Phase 6 report가 아직 없습니다. 이 turn에서 (1) " + $pd + "/.ralph/review-{N}.md / " + $pd + "/.ralph/qa-{N}.md / git diff 기반으로 `## Ralph Loop 실행 결과` 보고서를 작성하고, (2) `rm \"" + $pd + "/.ralph/.report-pending\"` 실행한 뒤, (3) 다시 정지 시도하세요. Phase 6 형식은 run-ralph 플러그인의 choo-choo 스킬 SKILL.md 참고."),
  "systemMessage": "run-ralph report gate: Phase 6 보고서 + sentinel 삭제 필요"
}'
