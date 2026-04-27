#!/bin/bash
# run-ralph-record-gate.sh — Stop hook
#
# Purpose
#   Catch the most common harness-failure: code shipped without the matching
#   record/CHANGELOG update. After /ralph-loop emits its completion promise,
#   it's easy to skip `wf:record` and let the docs drift. This gate fires on
#   Stop, looks at the diff between origin/{base} and HEAD, and refuses to
#   let Stop succeed when:
#     - The Ralph run is fully done (not still iterating)
#     - The branch has commits ahead of origin/{base} that touch non-doc
#       files (i.e. real code/config changes)
#     - But none of those commits modified CHANGELOG.md or changelogs/*.md
#
#   In that state it injects a Korean prompt asking the Worker to spawn
#   `wf:record` (or write the docs manually + remove the record-pending
#   sentinel).
#
# Sentinel convention
#   ${CLAUDE_PROJECT_DIR}/.ralph/.record-pending
#     - touched by run-ralph:choo-choo Phase 5 alongside .report-pending
#     - removed by `wf:record` skill on success, or manually by the user
#       (`rm "$PROJECT_ROOT/.ralph/.record-pending"`) if record is genuinely
#       not needed (doc-only runs, .ralph cleanup, experiments)
#
#   The sentinel is a "this run might owe a record" hint. The git-diff check
#   inside this hook is the actual decision: if the branch has no
#   non-doc changes, the gate stays silent regardless of the sentinel.
#
# Decision logic
#   1. ${CLAUDE_PROJECT_DIR}/.claude/ralph-loop.local.md exists
#         → /ralph-loop still iterating. Defer. Exit 0.
#   2. ${CLAUDE_PROJECT_DIR}/.ralph/.record-pending absent
#         → no recent ralph run, or wf:record already cleared. Exit 0.
#   3. branch has 0 commits ahead of origin/{base}
#         → nothing to record yet. Exit 0.
#   4. ahead-commits touch only doc files (.md, changelogs/, .ralph/)
#         → silent (probably ADR-only / design-only run). Exit 0.
#   5. ahead-commits include CHANGELOG.md or changelogs/v*.md change
#         → docs already updated. Exit 0.
#   6. otherwise → real code shipped, no doc update → block Stop.
#
# Disable
#   Toggle the `run-ralph` plugin off (`/plugin`). The choo-choo SKILL.md's
#   Phase 6 record-spawn instruction remains as a weaker fallback.

set -uo pipefail
# Note: `-e` is intentionally OFF. We want git failures (non-repo, missing
# upstream, etc.) to fall through to a silent exit, not crash the hook.

# Drain stdin (Claude Code feeds hook input JSON; unused by this gate).
cat > /dev/null

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"

# Step 1: defer while /ralph-loop is still iterating.
[[ -f "${PROJECT_DIR}/.claude/ralph-loop.local.md" ]] && exit 0

# Step 2: no record-pending sentinel → not our concern.
[[ ! -f "${PROJECT_DIR}/.ralph/.record-pending" ]] && exit 0

# Step 3-6: git diff inspection. Fall back to silent exit on any git error
# (we'd rather miss a record than block Stop on a non-git directory).
cd "$PROJECT_DIR" 2>/dev/null || exit 0

# Detect base branch (origin/HEAD if available, else main, else master).
BASE_REF=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
if [[ -z "${BASE_REF:-}" ]]; then
  if git rev-parse --verify origin/main >/dev/null 2>&1; then
    BASE_REF="main"
  elif git rev-parse --verify origin/master >/dev/null 2>&1; then
    BASE_REF="master"
  else
    exit 0  # no usable base — bail silently
  fi
fi

BASE="origin/${BASE_REF}"

# Commits on this branch beyond the base.
AHEAD_COUNT=$(git rev-list --count "${BASE}..HEAD" 2>/dev/null || echo 0)
[[ "${AHEAD_COUNT}" -eq 0 ]] && exit 0  # nothing committed yet

# All files touched by ahead-commits.
CHANGED_FILES=$(git diff --name-only "${BASE}..HEAD" 2>/dev/null || echo "")
[[ -z "${CHANGED_FILES}" ]] && exit 0

# Doc patterns that DON'T require a record:
#   - any *.md (README, plugin docs, design notes)
#   - changelogs/* (release notes themselves)
#   - .ralph/* (ralph artifacts — gitignored normally but defensive)
#   - docs/* (general documentation)
NON_DOC_FILES=$(echo "${CHANGED_FILES}" | grep -v -E '(\.md$|^changelogs/|^\.ralph/|^docs/)' || true)
[[ -z "${NON_DOC_FILES}" ]] && exit 0  # doc-only run — no record obligation

# Check if any CHANGELOG.md or changelogs/v*.md was touched.
HAS_CHANGELOG_UPDATE=$(echo "${CHANGED_FILES}" | grep -E '(^|/)CHANGELOG\.md$|^changelogs/v[0-9]' || true)
[[ -n "${HAS_CHANGELOG_UPDATE}" ]] && exit 0  # docs already done

# Step 6: real code shipped, CHANGELOG missing → block.
jq -n --arg pd "$PROJECT_DIR" --arg base "${BASE_REF}" '{
  "decision": "block",
  "reason": ("Ralph 실행이 끝났고 origin/" + $base + " 대비 코드 변경이 있지만 CHANGELOG.md / changelogs/ 갱신이 누락됐습니다. 이 turn에서 (1) `Skill(skill: \"wf:record\")` 호출(권장 — README/CHANGELOG/ARCHITECTURE/CLAUDE 일괄 동기화)하거나 CHANGELOG.md를 직접 갱신하고, (2) `rm \"" + $pd + "/.ralph/.record-pending\"` 실행한 뒤 (sentinel은 top-level), (3) 다시 정지 시도하세요. 만약 이 변경에 record가 정말 필요 없다면(예: hotfix 직전 임시 / .ralph 자체 정리 / 외부 PR 안 가는 실험) sentinel만 제거해도 게이트는 통과합니다."),
  "systemMessage": "run-ralph record gate: 코드 변경에 대한 wf:record가 누락 — 문서화 또는 sentinel 제거 필요"
}'
