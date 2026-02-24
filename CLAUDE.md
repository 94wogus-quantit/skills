# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 문서 역할 정의

| 문서 | 독자 | 포함 내용 | 포함하지 않는 것 |
|------|------|----------|-----------------|
| **CLAUDE.md** | AI Agent | 구조, 규칙, 개발 가이드라인, Known Issues, ADR 요약 | MCP 도구 목록, 설치 가이드, 상세 ADR 전문 |
| **ARCHITECTURE.md** | 모든 개발자 | 조감도, 코드맵, 아키텍처 불변성, 횡단 관심사 | 모듈 내부 구현 세부사항, 자주 변하는 정보 |
| **README.md** | 사용자(사람) | 설치, 사용법, 기능 소개, Marketplace 배포 | 아키텍처 결정사항, 개발 가이드라인 |
| **CHANGELOG.md** | 둘 다 | 버전 인덱스 + changelogs/ 링크 | 상세 변경 내용 (changelogs/에 위임) |

## Repository Overview

Personal plugin collection repository containing Claude Code Skills, Agents, and custom commands for systematic software development workflows.

**Key Artifacts (v3.28.0):**
- **Skills**: Workflow orchestrators for multi-step processes (분석, 계획, 실행, 문서화)
- **Agents**: AC (Acceptance Criteria) traceability (requirement-validator만 유지)
- **Custom Commands**: Workflow automation commands (별도 설치)
- **Reference Materials**: Templates and pattern catalogs

## Repository Structure

```
wogus-plugin/  (v3.28.0)
├── .claude-plugin/
│   └── marketplace.json       # 카탈로그 (10 plugins)
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
│   ├── github/                # GitHub MCP (v3.14.0)
│   ├── ask-yt/                # YouTube Ask CDP 자동화 (v3.27.0)
│   └── notify/                # macOS 알림 + TTS 훅 플러그인 (v3.28.0 NEW)
│
├── ARCHITECTURE.md      # High-level codebase mental map (matklad pattern)
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

### plan (v3.26.0)
Create high-quality, thoroughly reviewed implementation plans with 5-Step Algorithm methodology.
- **5단계 알고리즘**: 요구사항 질의 → 삭제 → 단순화 → 가속 → 자동화
- **Idiot Index**: 계획 효율성 메트릭 (과잉 설계 방지)
- **Zero-Context 원칙**: 정확한 파일 경로·코드 스니펫·테스트 커맨드 필수
- **ralph-loop 통합**: 자동 반복 검토 (optional, graceful degradation)
- **Iterative review loop** (ZERO 이슈까지 반복, 11개 섹션 체크리스트)
- **브랜치 검증** (feature 브랜치 확인)
- **Output**: `[FEATURE]_PLAN.md`
- **Integration**: Second step in workflow

### execute (v3.26.0)
Execute approved implementation plans with TodoList tracking and auto-recovery.
- **Auto-recovery loop**: 테스트/검증 실패 시 자동 복구 (최대 3회, 8가지 실패 타입)
- **브랜치 검증** (보호된 브랜치 경고)
- **Output**: Code implementation + test results
- **Integration**: Third step in workflow

### record (v3.25.0)
Consolidate workflow artifacts and update project documentation.
- **ARCHITECTURE.md 자동 생성/업데이트** (matklad 패턴: 조감도, 코드맵, 불변성, 횡단 관심사)
- **브랜치 검증** + Git commit/push
- **Output**: Updated README, ARCHITECTURE.md, CHANGELOG, CLAUDE docs
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

Claude Code Marketplace로 배포. 9개 독립 플러그인 (wf, glmr, seq-think, terraform, amplitude, slack, atlassian, github, ask-yt).
설치 및 배포 방법은 [README.md](README.md) 참조.

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

최근 3개 ADR 요약:

| 버전 | 변경 요약 |
|------|----------|
| v3.28.0 | notify 플러그인 신규 추가: macOS 음성+팝업 알림 (Stop + Notification 훅, 훅 전용 플러그인 첫 사례) |
| v3.27.0 | ask-yt 플러그인 신규 추가: YouTube 내장 AI(Ask/질문하기) CDP 자동화 |
| v3.26.0 | ralph-loop 통합 + auto-recovery: plan/execute 스킬 자동화 대폭 개선 |

상세 내용은 [docs/architecture/decisions/](docs/architecture/decisions/) 참조.
이전 버전 ADR (v1.x ~ v3.17.0)도 동일 디렉토리에서 확인 가능.

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

### 버전 업데이트 시 marketplace.json 동기화

버전을 올릴 때 (record 스킬 등으로 문서화 시) **반드시 `.claude-plugin/marketplace.json`의 해당 플러그인 버전도 함께 업데이트**할 것. CLAUDE.md, README.md, CHANGELOG.md와 marketplace.json 간 버전 불일치가 발생하지 않도록 확인.

### Optional Dependency: ralph-loop

**wf:plan** 스킬은 `ralph-loop@claude-plugins-official` 플러그인과 통합되어 더 나은 성능을 제공합니다:

- ✅ **With ralph-loop**: 완전 자동화된 반복 검토 루프 (권장)
- ⚠️ **Without ralph-loop**: 수동 피드백 적용 방식으로 fallback (여전히 작동)

**활성화 방법**: `~/.claude/settings.json`에 `"ralph-loop@claude-plugins-official": true` 추가

**호출 방식**: `Skill(ralph-loop:ralph-loop)` 형식으로 트리거

---

## Quick Reference

### Available MCP Tools

**Git MCP (wf 포함):**
- `get_current_branch`, `check_branch_protection`, `create_feature_branch`
- `git_status`, `git_add`, `git_commit`, `git_diff`, `git_push`, `git_squash`

**CI MCP (glmr 포함):**
- `ci_status`, `ci_list`, `ci_jobs`, `ci_trace`
- `ci_cancel_job`, `ci_cancel_pipeline`, `ci_trigger_job`, `ci_run`, `ci_retry_job`
- `mr_get`, `mr_discussions`, `mr_resolve_discussion`

### Workflow Summary

```
analyze → *_REPORT.md
    ↓
plan → *_PLAN.md (iterative review until ZERO issues)
    ↓
execute → Code implementation + tests
    ↓
record → README, ARCHITECTURE.md, CHANGELOG, CLAUDE docs update
```

---

## Slack MCP Usage

### Critical: content_type Setting

**Always use `text/plain`** for Slack messages (never `text/markdown`):

```python
mcp__plugin_slack_slack__conversations_add_message(
    channel_id="CHANNEL_ID",
    payload="Message with <@USER_ID> mention",
    content_type="text/plain"  # REQUIRED for mentions to work
)
```

**Warning**: If `content_type` is omitted or set to `text/markdown`, `<@USER_ID>` format gets escaped and mentions won't work.

### Slack Formatting

| Element | Format | Example |
|---------|--------|---------|
| User mention | `<@USER_ID>` | `<@U08P1RR2996>` |
| Team mention | `<!subteam^ID>` | `<!subteam^S04D8GC39F0>` |
| Channel link | `<#CHANNEL_ID>` | `<#C0518DH4DHU>` |
| URL with text | `<URL\|display>` | `<https://example.com\|링크>` |

### Message Template Example

```
cc <!subteam^TEAM_ID>

[Project] Task Title (JIRA-XXX)

Description here

Key Points:
• Item 1
• Item 2

JIRA: <https://atlassian.net/browse/XXX|JIRA-XXX>
PR: <https://github.com/org/repo/pull/123|PR#123>
```

### Check Thread Replies

```python
mcp__plugin_slack_slack__conversations_replies(
    channel_id="CHANNEL_ID",
    thread_ts="message_timestamp"
)
```

---

## Notes

- **Current version**: v3.28.0 (notify 플러그인 신규 추가: macOS 음성+팝업 알림)
- **wf**: 4 skills + agent + git MCP (12개 도구)
- **seq-think**: 별도 MCP 플러그인
- **glmr/terraform/amplitude/slack/atlassian/github/ask-yt/notify**: 독립 플러그인
- 외부 MCP (serena, context7, sentry)는 별도 플러그인으로 설치
- All skills and agents designed for Korean language output
- Reference files loaded on-demand to manage context efficiently
- Marketplace distribution requires GitHub public repository
- Version updates reflected when users run `/marketplace refresh`
