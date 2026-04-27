#!/bin/bash
# wf-review-gate.sh — PostToolUse(Write) hook for the wf workflow plugin
#
# Purpose
#   Detect when wf-managed artifacts (*_REPORT.md, *_PLAN.md, *_REVIEW.md) are
#   written and inject a systemMessage prompting the Worker to spawn the matching
#   external review agent (wf:wf-review-{analyze,plan}). This replaces the old
#   Pack-A pattern where plan/SKILL.md ran a self-review loop in the same session
#   that authored the plan — independent agent verdicts prevent self-approval bias.
#
# Path discipline (CWD-robust)
#   `tool_input.file_path` is consumed as-is. The Write tool emits absolute paths
#   in normal operation, so this hook does not depend on CWD. ${CLAUDE_PROJECT_DIR}
#   is not required by this script — but absolute paths in the JSON input mean
#   the systemMessage's `artifact_path` reference will continue to work even if
#   the Worker has `cd`'d into a subdirectory mid-iteration. If a relative path
#   is ever passed in, the hook simply lets the Worker handle resolution because
#   the systemMessage just echoes whatever path was written.
#
# Flow
#   *_REPORT.md  → spawn wf:wf-review-analyze
#   *_PLAN.md    → spawn wf:wf-review-plan
#   CHANGELOG.md → spawn wf:wf-review-record
#   *_REVIEW.md  → read VERDICT line, route REVISE/LGTM follow-up
#
# Input
#   JSON via stdin with `tool_input.file_path` (Claude Code PostToolUse contract).
#
# Output
#   JSON with `systemMessage` to inject. Empty stdout (exit 0) means no match —
#   the hook stays silent on unrelated Writes.

set -euo pipefail

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

# Exit early when no file path is present (e.g. malformed input or unrelated tool)
if [ -z "$file_path" ]; then
  exit 0
fi

filename=$(basename "$file_path")

# --- Pattern 1: *_REPORT.md written → spawn wf:wf-review-analyze ---
if [[ "$filename" =~ _REPORT\.md$ ]] && [[ ! "$filename" =~ _REVIEW ]]; then
  cat <<EOF
{
  "systemMessage": "[wf-review-gate] ${filename} 작성 감지. wf:wf-review-analyze 에이전트를 소환하여 리뷰해주세요.\n\nAgent(\n  subagent_type: \"wf:wf-review-analyze\",\n  description: \"Analyze REPORT 리뷰\",\n  prompt: \"phase: analyze\\nartifact_path: ${file_path}\\n\\n위 파일을 Analyze 리뷰 체크리스트에 따라 평가해주세요. VERDICT: LGTM 또는 REVISE로 반환하고, 결과를 같은 디렉토리에 {ISSUE_ID}_REVIEW.md로 저장해주세요.\"\n)"
}
EOF
  exit 0
fi

# --- Pattern 2: *_PLAN.md written (not REVIEW) → spawn wf:wf-review-plan ---
if [[ "$filename" =~ _PLAN\.md$ ]] && [[ ! "$filename" =~ _REVIEW ]] && [[ ! "$filename" =~ _PLAN_REVIEW ]]; then
  cat <<EOF
{
  "systemMessage": "[wf-review-gate] ${filename} 작성 감지. wf:wf-review-plan 에이전트를 소환하여 리뷰해주세요.\n\nAgent(\n  subagent_type: \"wf:wf-review-plan\",\n  description: \"Plan 리뷰\",\n  prompt: \"phase: plan\\nartifact_path: ${file_path}\\n\\n위 파일을 Plan 리뷰 체크리스트에 따라 평가해주세요. VERDICT: LGTM 또는 REVISE로 반환하고, 결과를 같은 디렉토리에 {FEATURE}_PLAN_REVIEW.md로 저장해주세요.\"\n)"
}
EOF
  exit 0
fi

# --- Pattern 3: CHANGELOG.md written → spawn wf:wf-review-record ---
# Trigger only on CHANGELOG.md (not README.md / ARCHITECTURE.md) to avoid
# false-positives — record skill always updates CHANGELOG.md last, so it's
# the canonical "record-done" signal. README/ARCHITECTURE are read-only checks
# inside the review-record agent itself.
if [[ "$filename" = "CHANGELOG.md" ]]; then
  cat <<EOF
{
  "systemMessage": "[wf-review-gate] ${filename} 작성 감지. wf:wf-review-record 에이전트를 소환하여 문서화 정합성을 리뷰해주세요.\n\nAgent(\n  subagent_type: \"wf:wf-review-record\",\n  description: \"Record/문서화 리뷰\",\n  prompt: \"phase: record\\nartifact_path: ${file_path}\\n\\n위 CHANGELOG와 함께 수정된 README / ARCHITECTURE / CLAUDE.md 등 docs를 Record 리뷰 체크리스트에 따라 평가해주세요. VERDICT: LGTM 또는 REVISE로 반환하고, 결과를 같은 디렉토리에 CHANGELOG_REVIEW.md로 저장해주세요.\"\n)"
}
EOF
  exit 0
fi

# --- Pattern 4: *_REVIEW.md written → inspect VERDICT and route follow-up ---
if [[ "$filename" =~ _REVIEW\.md$ ]] || [[ "$filename" =~ _PLAN_REVIEW ]]; then
  if [ -f "$file_path" ]; then
    verdict=$(grep -o 'VERDICT: [A-Z]*' "$file_path" 2>/dev/null | tail -1 | awk '{print $2}')
  else
    verdict=""
  fi

  if [ "$verdict" = "REVISE" ]; then
    original=$(echo "$file_path" | sed 's/_REVIEW\.md$/.md/' | sed 's/_PLAN_REVIEW\.md$/_PLAN.md/')
    cat <<EOF
{
  "systemMessage": "[wf-review-gate] 리뷰 결과: REVISE. ${filename}의 수정 요청을 읽고 원본 파일(${original})에 피드백을 반영해주세요. 수정 완료 후 원본 파일을 다시 Write하면 자동으로 재리뷰됩니다."
}
EOF
    exit 0
  elif [ "$verdict" = "LGTM" ]; then
    cat <<EOF
{
  "systemMessage": "[wf-review-gate] 리뷰 통과! (LGTM) 다음 단계로 진행하세요."
}
EOF
    exit 0
  fi
fi

# No match — silent pass
exit 0
