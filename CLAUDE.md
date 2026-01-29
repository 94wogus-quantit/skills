# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Personal plugin collection repository containing Claude Code Skills, Agents, and custom commands for systematic software development workflows.

**Key Artifacts (v3.20.0):**
- **Skills**: Workflow orchestrators for multi-step processes (분석, 계획, 실행, 문서화)
- **Agents**: AC (Acceptance Criteria) traceability (requirement-validator만 유지)
- **Custom Commands**: Workflow automation commands (별도 설치)
- **Reference Materials**: Templates and pattern catalogs

## Repository Structure

```
wogus-plugin/  (v3.20.0)
├── .claude-plugin/
│   └── marketplace.json       # 카탈로그 (8 plugins)
│
├── plugins/                   # 모든 플러그인
│   ├── wf/                    # 메인 워크플로우 플러그인
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/            # 자동 인식
│   │   │   ├── analyze/
│   │   │   ├── plan/
│   │   │   ├── execute/
│   │   │   └── record/
│   │   └── agents/
│   │       └── requirement-validator.md
│   ├── glmr/                  # GitLab MR 관리
│   ├── seq-think/             # Sequential Thinking MCP
│   ├── terraform/
│   ├── amplitude/
│   ├── slack/
│   ├── atlassian/
│   └── github/                # GitHub MCP (v3.14.0 NEW)
│
├── CLAUDE.md            # This file
├── README.md            # User-facing documentation
└── CHANGELOG.md         # Version history
```

## Available Skills

### analyze (v3.18.0)
Systematic root cause analysis with branch validation and Elon Musk's thinking methodology.
- **브랜치 자동 생성** (main/master/staging 감지 시)
- **일론 머스크 사고법**: 5단계 알고리즘, 삭제 원칙, Idiot Index, 요구사항 질의
- **Output**: `[ISSUE_ID]_REPORT.md`
- **Integration**: First step in workflow

### plan (v3.8.0)
Create high-quality, thoroughly reviewed implementation plans.
- **Iterative review loop** (ZERO 이슈까지 반복)
- **브랜치 검증** (feature 브랜치 확인)
- **Output**: `[FEATURE]_PLAN.md`
- **Integration**: Second step in workflow

### execute (v3.8.0)
Execute approved implementation plans with TodoList tracking.
- **브랜치 검증** (보호된 브랜치 경고)
- **Output**: Code implementation + test results
- **Integration**: Third step in workflow

### record (v3.8.0)
Consolidate workflow artifacts and update project documentation.
- **브랜치 검증** + Git commit/push
- **Output**: Updated README, CHANGELOG, CLAUDE docs
- **Integration**: Final step in workflow

### mr-review (v3.8.0)
GitLab MR의 코드 변경사항을 분석하여 맥락 기반 종합 리뷰 수행.
- **7가지 검증**: 아키텍처, 비즈니스 로직, 컨벤션, 이슈 패턴, JIRA, 보안, 테스트
- **2개 파일 출력**: `INLINE_DISCUSSION.json` + `SUMMARY_COMMENT.md`
- **Trivy 범용 보안 스캔**: 모든 언어 지원
- **Phase별 중간 산출물**: `.mr-review/` 디렉토리

## Available Agents

### requirement-validator (v3.0.0)
JIRA Acceptance Criteria와 코드를 자동 매핑하여 요구사항 달성 여부 검증.

**4가지 실행 모드**:
- **Mode 1 (Reverse)**: 코드 → AC 역매핑 (analyze)
- **Mode 2 (Pre)**: 계획 → AC coverage (plan)
- **Mode 3 (Post)**: git diff → AC 구현 확인 (execute)
- **Mode 4 (Final)**: MR → AC 최종 게이트 (mr-review)

**Integration**: 4개 Skills에서 자동 호출

## Git MCP (v3.15.0)

로컬 Git 저장소 관리를 위한 MCP 서버. wf에 포함.

### 브랜치 관리 도구
- **get_current_branch**: 현재 브랜치 이름 반환
- **check_branch_protection**: 보호된 브랜치(main/master/staging) 여부 확인
- **create_feature_branch**: 새 feature 브랜치 생성 및 체크아웃
- **list_branches**: 모든 브랜치 목록 조회 (원격 브랜치 옵션)
- **switch_branch**: 브랜치 전환

### Git 작업 도구 (v3.15.0 NEW)
- **git_status**: 파일 상태 확인 (staged, modified, untracked, deleted)
- **git_log**: 최근 커밋 히스토리 조회
- **git_add**: 파일 스테이징
- **git_commit**: 커밋 생성 (메시지 검증 포함)
- **git_diff**: 변경 내용 통계 (staged 옵션)
- **git_push**: 원격 저장소 푸시 (set_upstream, force 옵션)
- **git_squash**: 여러 커밋을 하나로 합치기

### 사용 예시
```python
# 브랜치 검증 후 feature 브랜치 생성
check_branch_protection()  # → {"is_protected": true, ...}
create_feature_branch("feature/JIRA-123")  # → {"success": true, "branch": "feature/JIRA-123"}

# Git 작업 워크플로우
git_status()     # → {"staged": [], "modified": ["file.py"], ...}
git_add(".")     # → {"added_files": ["file.py"], ...}
git_commit("feat: add new feature")  # → {"commit_hash": "abc1234", ...}
git_push(set_upstream=True)  # → {"remote": "origin", "branch": "feature/JIRA-123"}

# Squash & Force Push (히스토리 정리)
git_squash(commit_count=3)   # → {"commit_hash": "def5678", "squashed_count": 3}
git_push(force=True)         # → {"remote": "origin", ...} ⚠️ 보호 브랜치 제외
```

**Integration**: analyze, plan, execute, record 스킬의 Phase 0에서 자동 호출

## CI MCP (v3.16.0)

GitLab CI/CD 및 MR Discussion 관리를 위한 MCP 서버. glmr에 포함.

### CI 파이프라인 조회 도구
- **ci_status**: 현재 파이프라인 상태 조회
- **ci_list**: 최근 파이프라인 목록
- **ci_jobs**: job 목록 (status_filter 옵션)
- **ci_trace**: job 로그 조회

### CI 파이프라인 제어 도구
- **ci_cancel_job**: 특정 job 취소
- **ci_cancel_pipeline**: 파이프라인 취소
- **ci_trigger_job**: 수동 job 트리거
- **ci_run**: 새 파이프라인 시작
- **ci_retry_job**: 실패 job 재시도

### MR Discussion 도구
- **mr_get**: 현재 브랜치 또는 지정 MR 정보 조회
- **mr_discussions**: Discussion 전체 목록 조회
  - `resolved_filter`: "all" | "unresolved" | "resolved"
  - 내부적으로 pagination 처리하여 전체 반환
- **mr_resolve_discussion**: Discussion 해결 처리

### 사용 예시
```python
# CI 파이프라인 상태
ci_status()  # → {"success": true, "status": "running", "pipeline_id": 12345}
ci_jobs(status_filter="failed")  # → {"jobs": [...], "count": 2}

# MR Discussion 조회
mr_discussions(resolved_filter="unresolved")  # → {"discussions": [...], "count": 5}
mr_resolve_discussion(mr_iid=123, discussion_id="abc123")  # → {"success": true}
```

**Integration**: fix-discussion 스킬에서 discussion 조회 시 사용

## Skills vs Agents

| Aspect | Skills | Agents |
|--------|--------|--------|
| **Purpose** | Orchestrate multi-step workflows | AC traceability |
| **Scope** | Broad (analysis → execution) | Narrow (AC 추적 전용) |
| **File Format** | `SKILL.md` in skill directory | `.md` files in `agents/` |
| **Invocation** | User explicitly uses skill | Skills call automatically |
| **Count** | 5개 | 1개 |

## AC Traceability Example

```
JIRA-123: "사용자 이메일 로그인"
├─ AC#1: 이메일 validation
├─ AC#2: 5회 실패 시 계정 잠금
└─ AC#3: JWT 토큰 발급

1. analyze → Mode 1: "이 버그는 AC#2 미충족"
2. plan → Mode 2: "계획이 AC#1,2,3 모두 커버 ✅"
3. execute → Mode 3: "AC#1 ✅, AC#2 ❌ 미구현"
4. mr-review → Mode 4: "AC#2 미구현 → MR BLOCKED"
```

## Skill Development

### Creating New Skills

1. Initialize with skill-creator template
2. Customize `SKILL.md` (metadata, workflow instructions, tool references)
3. Add resources (optional): `references/`, `scripts/`, `assets/`
4. Package for distribution

### Skill Writing Guidelines

**Metadata Quality:**
- `description` determines when Claude uses the skill
- Be specific about trigger scenarios
- Use third-person (not "you should")

**⚠️ Language Rule (MANDATORY - DO NOT IGNORE):**
- **적용 범위: SKILL.md, references/*.md, agents/*.md, 템플릿 등 모든 지시 파일**
- **지시문(instructions), Phase 설명, 워크플로우 단계는 반드시 영어로 작성**
- **예시(examples), 출력 템플릿, 사용자 안내 메시지만 한국어로 작성**
- 이유: Claude는 영어 지시문을 가장 정확하게 해석함. 한국어 지시문은 의도가 왜곡될 수 있음
- ✅ 올바른 예: `"Phase 1: Collect context by reading the target file and identifying symbols"` → 지시문은 영어
- ✅ 올바른 예: `"Output example: ## 근본 원인 분석"` → 출력 템플릿은 한국어
- ❌ 잘못된 예: `"Phase 1: 대상 파일을 읽고 심볼을 식별하여 컨텍스트를 수집한다"` → 지시문을 한국어로 쓰면 안 됨

**Instruction Style:**
- Use imperative/infinitive form (verb-first)
- "To accomplish X, do Y" not "You should do X"
- Objective, instructional language

**Progressive Disclosure:**
- Keep SKILL.md lean (<5k words)
- Move detailed info to `references/`

## Agent Development (v3.0.0)

**Current Status**: v3.0.0에서 1개 Agent만 유지 (requirement-validator)

**Creating New Agents** (if needed):
- Agent는 여러 Skills에서 공유할 때만 생성
- 단독 호출 전용이면 Skills Phase로 구현
- All content in Korean (한국어 필수)
- 4-5 phases maximum

For detailed guidelines, see historical ADRs.

## Integration with Custom Commands

**Workflow**: `analyze → plan → execute → record`

Skills work alongside custom commands in `~/.claude/commands/` for seamless workflow automation.

## Marketplace Distribution

This repository is distributed as a **Claude Code Marketplace**.

### Configuration

- **File**: `.claude-plugin/marketplace.json`
- **Version**: Semantic versioning (current: v3.20.0)
- **Plugins**: 8개 독립 플러그인 (wf, glmr, seq-think, terraform, amplitude, slack, atlassian, github)
- **MCP Servers**: seq-think 별도 플러그인으로 분리 (외부 MCP는 별도 설치)

### Publishing Workflow

1. Develop: Create/modify skills or agents
2. Update Version: Increment `metadata.version`
3. Commit & Push: Push to GitHub
4. Users Update: `/marketplace refresh`

### User Installation

```bash
/marketplace add git@github.com:94wogus-quantit/wogus-plugin.git
/plugin install wogus-plugins:wf                   # 4 skills + agent
/plugin install wogus-plugins:glmr                 # GitLab MR 관리 (7 skills)
/plugin install wogus-plugins:seq-think            # Sequential Thinking MCP
/plugin install wogus-plugins:terraform            # Terraform MCP
/plugin install wogus-plugins:amplitude            # Amplitude MCP
/plugin install wogus-plugins:slack                # Slack MCP
/plugin install wogus-plugins:atlassian            # Atlassian MCP
/plugin install wogus-plugins:github               # GitHub MCP
```

## Development Best Practices

**For Skills:**
- Focus on procedural knowledge and domain expertise
- Reference bundled resources explicitly
- Test with realistic scenarios

**For Agents:**
- Single responsibility principle (여러 Skills에서 공유할 때만 생성)
- Clear trigger conditions in description
- All content in Korean (mandatory)

**For This Repository:**
- One skill per directory, one agent per `.md` file
- Document integrations with other skills/commands/agents
- Architecture decisions → Serena 메모리에 저장

---

## 아키텍처 결정사항 (Architecture Decisions)

### 최신 결정사항 (Latest ADRs)

이 섹션에는 최신 3개의 아키텍처 결정사항만 포함합니다.
이전 버전의 ADR은 Serena 메모리 또는 CHANGELOG.md를 참조하세요.

---

### v3.20.0 - plan_template에 Task Registration Guide 섹션 추가 (2026-01-30)

**컨텍스트**:
plan 스킬이 생성하는 `*_PLAN.md` 출력물의 템플릿(`plan_template.md`)에 Task Registration 절차가 구체적이지 않아, execute 스킬이 plan을 실행할 때 태스크를 빠짐없이 등록하도록 보장하는 명시적 구조가 부재했음.

**문제점**:
- **Task Registration 가이드 부재**: plan_template.md의 "Execution Notes" 섹션에 TaskCreate/TaskUpdate 언급만 있고 구체적 등록 절차 없음
- **execute 연계 약함**: execute Phase 3에서 plan 문서의 Task Breakdown을 파싱할 때 구조화된 등록 체크리스트 부재

**결정**: plan_template.md에 Task Registration Guide 섹션 추가

1. **`## Task Registration Guide` 섹션 신설**: Task Breakdown과 Dependencies & Critical Path 사이에 배치
2. **`### Registration Table` 템플릿**: subject, activeForm 컬럼으로 모든 태스크 등록 가이드
3. **`### Task Tracking Rules`**: TaskCreate → TaskUpdate(in_progress) → TaskUpdate(completed) 워크플로우 명시

**영향**:
- plan 스킬이 생성하는 PLAN.md에 명시적 Task Registration 가이드 포함
- execute 스킬의 Phase 0에서 모든 태스크를 빠짐없이 등록 가능
- 기존 워크플로우와 완전 호환 (Breaking Change 없음)
- 1개 파일 수정 (+20줄)

**버전**: v3.19.0 → v3.20.0

---

### v3.19.0 - 스킬 전체 영어 지시문 점검 및 TaskTracking·Phase 정합성 개선 (2026-01-30)

**컨텍스트**:
v3.17.0에서 Plugin/MCP 이름을 단축했으나, 스킬 SKILL.md 파일 내부의 MCP 도구명은 업데이트되지 않았음. 또한 execute 스킬에서 deprecated된 TodoWrite API와 잘못된 Phase 개수 표기가 발견됨.

**문제점**:
- **OLD MCP 이름 잔존**: 4개 스킬 + 1 agent에 `mcp__plugin_workflow-skills_*` 형식 37개 잔존
- **TodoWrite 미마이그레이션**: execute 스킬에서 deprecated TodoWrite 9개 사용 중 (TaskCreate/TaskUpdate로 전환 필요)
- **Phase 라벨 불일치**: execute 스킬이 실제 9-Phase인데 "7-Phase"로 표기
- **TodoList 용어 미통일**: execute 스킬에서 TodoList 7개 잔존 (TaskList로 통일 필요)

**결정**: 4가지 일괄 수정

1. **MCP 도구명 37개 교체** (5개 파일)
2. **TodoWrite → TaskCreate/TaskUpdate 마이그레이션** (9개, execute 스킬)
3. **TodoList → TaskList 용어 통일** (7개, execute 스킬)
4. **"7-Phase" → "9-Phase" 수정** (3개, execute 스킬)

**영향**:
- 스킬 지시문이 현재 API와 정확히 일치
- 기존 워크플로우와 완전 호환 (Breaking Change 없음)
- 5개 파일 수정

**버전**: v3.18.0 → v3.19.0

---

### v3.18.0 - analyze 스킬 강화: 일론 머스크 사고법 도입 (2026-01-30)

**컨텍스트**:
analyze 스킬의 근본 원인 분석 프로세스에 일론 머스크의 핵심 사고법을 체계적으로 통합하여 분석 품질을 향상시킬 필요가 있었음.

**문제점**:
- **5단계 알고리즘 부재**: 권장사항이 자동화부터 시작하는 경향 (가장 흔한 실수)
- **삭제 관점 부재**: 버그를 패치하려는 접근만 있고, 코드 삭제로 구조적 해결하는 관점 부족
- **효율성 지표 부재**: 수정 비용 대비 변경량 비율(Idiot Index) 미평가
- **요구사항 질의 부재**: "스펙대로 동작하지만 스펙이 잘못된" 가장 비싼 버그 미식별

**결정**: 5가지 주요 변경

1. **SKILL.md Phase 5에 삭제 가능성 평가 추가**
2. **SKILL.md Phase 6에 5단계 알고리즘 프레임워크 추가**
3. **report_template.md 전면 재작성** (한국어화 + 8개 신규 섹션)
4. **common_bug_patterns.md에 삭제 관점 추가** (13개 패턴 모두)
5. **reference 파일 확장** (first_principles_guide.md, root_cause_techniques.md)

**영향**:
- 분석 리포트에 삭제 가능성, 5단계 알고리즘, Idiot Index 평가 포함
- 기존 워크플로우와 호환 (추가 기능, Breaking Change 없음)
- +457줄 / -252줄 (6개 파일)

**버전**: v3.17.0 → v3.18.0

---

## 이전 버전 ADRs

v3.0.0 ~ v3.2.1, v2.0.0 ~ v2.4.0, v1.6.0 등의 아키텍처 결정사항은 다음 디렉토리에서 확인하세요:

📁 **[docs/architecture/decisions/](docs/architecture/decisions/)**
- [ADR-0001](docs/architecture/decisions/ADR-0001-v2.0.0-agents-introduction.md): v2.0.0 Agents 시스템 도입
- [ADR-0002](docs/architecture/decisions/ADR-0002-v2.4.0-mcp-server-expansion-1.md): v2.4.0 MCP 서버 확장 (Sentry + Atlassian)
- [ADR-0003](docs/architecture/decisions/ADR-0003-v3.0.0-agents-reduction.md): v3.0.0 Agents 시스템 축소 리팩토링
- [ADR-0004-0007](docs/architecture/decisions/ADR-0004-0007-v3.0-v3.2.md): v3.0.1 ~ v3.2.0 MCP 관련 개선사항
- [HISTORICAL_ADRS](docs/architecture/decisions/HISTORICAL_ADRS.md): v2.1.0 ~ v2.3.0, v1.6.0

---

## Known Issues & Guidelines

### MCP Tool Name 64자 제한

Claude API는 tool name을 **최대 64자**로 제한합니다. MCP 도구 이름은 다음 패턴으로 자동 생성됩니다:

```
mcp__plugin_<PLUGIN_NAME>_<SERVER_NAME>__<TOOL_NAME>
│           │              │               │
└─ 12자 ───┘              │               │
            고정 prefix    MCP 서버 키     도구 함수명
```

**네이밍 가이드라인** (64자 초과 방지):
- Plugin name (`plugin.json`의 `name`): **최대 10자** 권장
- MCP server name (`.mcp.json`의 key): **최대 5자** 권장
- Tool function name: **최대 30자** 권장
- 합계: 12 + 10 + 1 + 5 + 2 + 30 = 60자 (4자 여유)

**v3.17.0 단축 매핑**:
| 이전 이름 | 새 이름 | 이유 |
|-----------|---------|------|
| `workflow-bundle` (15자) | `wf` (2자) | Plugin name |
| `sequential-thinking` (19자) | `seq-think` (9자) | Plugin name |
| `gitlab-mr` (9자) | `glmr` (4자) | Plugin name |
| `git-local` (9자) | `git` (3자) | MCP server key |
| `gitlab-ci` (9자) | `ci` (2자) | MCP server key |
| `sequential-thinking` (19자) | `st` (2자) | MCP server key |

**에러 증상**: `invalid_request_error` - `tool_reference.tool_name: String should have at most 64 characters`

---

## Notes

- **Current version**: v3.20.0 (plan_template에 Task Registration Guide 섹션 추가)
- **wf**: 4 skills + agent + git MCP (12개 도구)
- **seq-think**: 별도 MCP 플러그인
- **glmr/terraform/amplitude/slack/atlassian/github**: 독립 플러그인
- 외부 MCP (serena, context7, sentry)는 별도 플러그인으로 설치
- All skills and agents designed for Korean language output
- Reference files loaded on-demand to manage context efficiently
- Marketplace distribution requires GitHub public repository
- Version updates reflected when users run `/marketplace refresh`
