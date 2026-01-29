# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 문서 역할 정의

| 문서 | 독자 | 포함 내용 | 포함하지 않는 것 |
|------|------|----------|-----------------|
| **CLAUDE.md** | AI Agent | 구조, 규칙, 개발 가이드라인, Known Issues, ADR 요약 | MCP 도구 목록, 설치 가이드, 상세 ADR 전문 |
| **README.md** | 사용자(사람) | 설치, 사용법, 기능 소개, Marketplace 배포 | 아키텍처 결정사항, 개발 가이드라인 |
| **CHANGELOG.md** | 둘 다 | 버전 인덱스 + changelogs/ 링크 | 상세 변경 내용 (changelogs/에 위임) |

## Repository Overview

Personal plugin collection repository containing Claude Code Skills, Agents, and custom commands for systematic software development workflows.

**Key Artifacts (v3.21.0):**
- **Skills**: Workflow orchestrators for multi-step processes (분석, 계획, 실행, 문서화)
- **Agents**: AC (Acceptance Criteria) traceability (requirement-validator만 유지)
- **Custom Commands**: Workflow automation commands (별도 설치)
- **Reference Materials**: Templates and pattern catalogs

## Repository Structure

```
wogus-plugin/  (v3.21.0)
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

Claude Code Marketplace로 배포. 8개 독립 플러그인 (wf, glmr, seq-think, terraform, amplitude, slack, atlassian, github).
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
| v3.21.0 | 문서 구조 개선: CLAUDE.md 경량화, README.md 정리, 역할 분리 |
| v3.20.0 | plan_template에 Task Registration Guide 섹션 추가 |
| v3.19.0 | 스킬 전체 영어 지시문 점검 및 TaskTracking·Phase 정합성 개선 |

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

---

## Notes

- **Current version**: v3.21.0 (문서 구조 개선: CLAUDE.md 경량화, README.md 정리)
- **wf**: 4 skills + agent + git MCP (12개 도구)
- **seq-think**: 별도 MCP 플러그인
- **glmr/terraform/amplitude/slack/atlassian/github**: 독립 플러그인
- 외부 MCP (serena, context7, sentry)는 별도 플러그인으로 설치
- All skills and agents designed for Korean language output
- Reference files loaded on-demand to manage context efficiently
- Marketplace distribution requires GitHub public repository
- Version updates reflected when users run `/marketplace refresh`
