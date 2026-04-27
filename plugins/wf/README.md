# Workflow Bundle Plugin (v3.30.0)

체계적인 소프트웨어 개발 워크플로우 — Skills + Agents + Git MCP + 외부 review 게이트 hook 번들. v3.30.0에서 wf2 통합으로 self-approval 차단 패턴 도입.

## 설치

```bash
/plugin install wogus-plugins:wf
```

## 워크플로우 (5단계, 외부 게이트로 self-approval 차단)

```
analyze → *_REPORT.md  (PostToolUse hook → wf:wf-review-analyze → LGTM 까지 반복)
   ↓
plan    → *_PLAN.md    (PostToolUse hook → wf:wf-review-plan → LGTM 까지 반복)
   ↓
execute → 코드 변경 + tests + AC Achievement Report
   ↓ (Phase 7.5: 자동 wf:qa spawn — PASS 필수)
qa      → [ISSUE_ID]_QA.md (실제 환경 acceptance 검증, PASS/FAIL)
   ↓
record  → README / CHANGELOG / ARCHITECTURE / CLAUDE.md 동기화
          (CHANGELOG.md write → wf:wf-review-record 게이트)
```

**핵심 원칙**: "the executor is never the verifier" — 각 단계의 산출물은 그 산출물을 만든 세션이 아닌 외부 review agent / qa skill이 판정.

## 포함된 Skills (5개)

| Skill | 설명 | 외부 게이트 |
|-------|------|-------------|
| **analyze** | 이슈 분석 + root cause 파악, First Principles Thinking | `wf:wf-review-analyze` (REPORT) |
| **plan** | 구현 계획 수립 (5단계 알고리즘 + Idiot Index + Zero-Context). v3.30에서 자기검토 루프 제거 → 외부 게이트 의존 | `wf:wf-review-plan` (PLAN) |
| **execute** | 계획 실행 + TodoList + auto-recovery. Phase 7.5에서 `wf:qa` 자동 spawn | `wf:qa` skill (Phase 7.5) |
| **qa** *(NEW v3.30)* | 독립 acceptance 검증 (test / API / agent-browser UI / DB). 실제 환경에서 REPORT의 재현 시나리오 + PLAN의 성공 기준 재실행 | (게이트 자체) |
| **record** | 문서화 (README / CHANGELOG / ARCHITECTURE / CLAUDE.md) + Serena 메모리 | `wf:wf-review-record` (CHANGELOG) |
| ~~mr-review~~ | (별도 플러그인 또는 deprecated) | — |

## 포함된 Agents (4개)

| Agent | 역할 |
|-------|------|
| **requirement-validator** | JIRA / GitHub issue AC ↔ 코드 매핑 추적 (4-mode: Reverse / Pre / Post / Final) |
| **wf-review-analyze** *(NEW v3.30)* | `*_REPORT.md` Level 2 review (First Principles, Evidence quality, Hypothesis methodology) |
| **wf-review-plan** *(NEW v3.30)* | `*_PLAN.md` Level 2 review (Task Decomposition, Dependencies, Success Criteria, REPORT alignment, Zero-Context) |
| **wf-review-record** *(NEW v3.30)* | CHANGELOG / PR / docs Level 2 review (CHANGELOG accuracy, Categorization, Code-doc Match) |

## 포함된 Hook *(NEW v3.30)*

- **`hooks/wf-review-gate.sh`** (`PostToolUse(Write)` matcher): `*_REPORT.md` / `*_PLAN.md` / `CHANGELOG.md` / `*_REVIEW.md` 변경 감지 시 외부 review agent spawn 권유 systemMessage 주입. `${CLAUDE_PLUGIN_ROOT}` 자동 로드 — 사용자 `.claude/settings.json` 편집 불필요.

## 포함된 MCP

- **git** (`git_local_server.py`): branch protection 검사, commit/diff/squash 등 12개 git tool. 대표 도구:
  - `mcp__plugin_wf_git__check_branch_protection`
  - `mcp__plugin_wf_git__create_feature_branch`
  - `mcp__plugin_wf_git__git_commit`
  - `mcp__plugin_wf_git__git_squash`

## choo-choo (run-ralph) 통합

`run-ralph:choo-choo` Phase 1.5 Auto-dispatch가 task 복잡도를 자동 분류:
- **trivial** (typo / 단일 파일 / JIRA-less / 새 추상화 없음 등) → wf 우회, ralph 직행
- **full** (cross-file / JIRA / schema·API 변경 / 새 파일·의존성 / 메타·설계) → `wf:analyze → plan → execute → qa → record` 순차 후 ralph

자세한 dispatch 룰: `plugins/run-ralph/skills/choo-choo/SKILL.md` Phase 1.5 섹션.

## 언어

지시문은 영어, 사용자 대면 출력은 한국어가 기본.

## v3.30.0 주요 변경

- **wf2 통합**: 외부 review agents + Stop hook으로 self-approval 차단 패턴 흡수
- **`qa` skill 신규**: 독립 acceptance 검증 게이트
- **`plan` 자기검토 루프 제거**: 449줄 제거 → 외부 게이트 71줄로 교체
- **`execute` Phase 7.5**: `wf:qa` 자동 spawn으로 QA 게이트 강제
- **0 breaking changes**: 기존 `wf:analyze` / `wf:plan` / `wf:execute` / `wf:record` 호출 그대로 작동

상세 변경 이력은 [`changelogs/v3.30.md`](../../changelogs/v3.30.md) 참조.
