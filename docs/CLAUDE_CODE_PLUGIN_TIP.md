# Claude Code Plugin 개발 팁

> 플러그인 개발하면서 정리한 내용

---

## 목차

1. [플러그인 기본 구조](#1-플러그인-기본-구조)
2. [Skill 개발](#2-skill-개발)
3. [Skill UX 향상 (내장 도구 활용)](#3-skill-ux-향상-내장-도구-활용)
4. [Agent 개발](#4-agent-개발)
5. [MCP 서버 설정](#5-mcp-서버-설정)
6. [Command 개발](#6-command-개발)
7. [Hook 개발](#7-hook-개발)
8. [주의사항 및 팁](#8-주의사항-및-팁)

---

## 1. 플러그인 기본 구조

### 최소 구조

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json      # 필수: 플러그인 메타데이터
└── README.md            # 권장: 사용법 설명
```

### 전체 구조 (모든 컴포넌트 포함)

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json            # MCP 서버 설정
├── skills/              # 자동 인식
│   └── my-skill/
│       ├── SKILL.md
│       └── references/
├── agents/              # 자동 인식
│   └── my-agent.md
├── commands/            # 자동 인식
│   └── my-command.md
├── hooks/               # 자동 인식
│   └── my-hook.md
└── my_mcp_server.py     # 커스텀 MCP 서버
```

### plugin.json 예시

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "플러그인 설명"
}
```

**필수 필드:** `name`만 필수, `version`과 `description`은 선택사항

> **Tip**: `skills/`, `agents/`, `commands/`, `hooks/` 폴더는 자동 인식됩니다. plugin.json에 별도 등록 불필요.

---

## 2. Skill 개발

Skill은 Claude가 특정 상황에서 자동으로 사용하는 워크플로우입니다.

### 2.1 기본 구조

```
skills/
└── my-skill/
    ├── SKILL.md           # 필수: 스킬 정의
    └── references/        # 선택: 참조 문서
        ├── template.md
        └── guide.md
```

### 2.2 SKILL.md 구조

```markdown
---
name: my-skill
description: |
  Skill description in English for accurate interpretation.
  Korean triggers: 한국어 트리거 키워드들
user-invocable: true
---

# My Skill

## Overview
Brief description of what this skill does.

## Phase 0: Initialize
- Use TaskCreate to register all phases as tasks
- Set first task to in_progress

## Phase 1: Collect Context
1. Read necessary files using Read tool
2. Gather information using Grep/Glob
3. Update task status when complete

## Phase 2: Process
1. Analyze collected information
2. Apply business logic
3. Generate intermediate results

## Phase 3: Output
1. Format results according to template
2. Write output file
3. Mark all tasks as completed

## Output Format
Describe expected output structure.

## References
- [Template](references/template.md): 출력 템플릿
- [Guide](references/guide.md): 상세 가이드
```

### 2.3 Description 작성 팁

```yaml
# ✅ 좋은 예: 구체적인 트리거 조건
description: |
  Analyze bug reports and create root cause analysis documents.
  Use when investigating JIRA issues, Sentry errors, or debugging complex bugs.
  Korean: 버그 분석, 원인 분석, 이슈 분석, 에러 분석

# ❌ 나쁜 예: 모호한 설명
description: "분석을 수행합니다"
```

### 2.4 언어 규칙

| 구성요소 | 언어 | 이유 |
|---------|------|------|
| description | 영어 + 한국어 키워드 | Claude 해석 정확도 |
| Phase 설명 | 영어 | 지시문 정확도 |
| 출력 템플릿 | 한국어 | 사용자 가독성 |
| references/ | 한국어 | 사용자 문서 |

### 2.5 Phase 0: Task Registration 패턴

실제 Skill들은 Phase 0에서 모든 Phase를 Task로 등록하여 진행 상황을 추적합니다:

```markdown
## Phase 0: Task Registration

⚠️ **CRITICAL: DO NOT SKIP PHASE 0**

Register all Phases using `TaskCreate`:

| Task | subject | activeForm |
|------|---------|------------|
| Phase 1 | Branch Validation | Validating branch |
| Phase 2 | Context Gathering | Gathering context |
| Phase 3 | Analysis | Analyzing |
| Phase 4 | Output Generation | Generating output |

**Task Tracking Rules**:
- On Phase entry: `TaskUpdate(taskId, status: "in_progress")`
- On Phase completion: `TaskUpdate(taskId, status: "completed")`
- Only **one Phase** should be `in_progress` at any time
```

### 2.6 Progressive Disclosure (references/)

Skill이 길어지면 핵심만 SKILL.md에 두고 나머지는 references/로 분리:

```
skills/
└── my-skill/
    ├── SKILL.md              # 핵심 워크플로우 (5,000 words 이하 권장)
    └── references/
        ├── template.md       # 출력 템플릿
        ├── checklist.md      # 검증 체크리스트
        └── guides/           # 상세 가이드
            └── detail.md
```

**SKILL.md에서 참조:**
```markdown
> For detailed guide, see `references/guides/detail.md`
```

---

## 3. Skill UX 향상 (내장 도구 활용)

Claude Code에는 Skill에서 활용 가능한 **내장 도구들**이 있습니다. 이를 활용하면 단순 실행이 아닌 **인터랙티브한 워크플로우**를 만들 수 있습니다.

> 📚 **전체 도구 레퍼런스**: [CLAUDE_CODE_TOOLS.md](CLAUDE_CODE_TOOLS.md)

### 3.1 핵심 도구

| 도구 | 용도 | Skill 활용 |
|------|------|-----------|
| `AskUserQuestion` | 사용자에게 선택지 제공 | 브랜치 선택, 다음 단계 확인 |
| `Task` | 서브에이전트 호출 | Agent 실행, 병렬 작업 위임 |
| `TaskCreate/Update` | 진행 상황 추적 | Phase별 Todo 관리 |

### 3.2 Task의 description = 상태 메시지

`Task` 도구의 `description` 파라미터는 **사용자에게 보이는 상태 메시지**입니다.

```yaml
Tool: Task
Args:
  subagent_type: "Explore"
  description: "인증 모듈 구조 파악"   # ← UI에 표시되는 메시지
  prompt: |
    ...
```

**작성 팁:**
- **3-5 단어**로 짧게
- 현재 **뭘 하는지** 명확하게
- 한국어/영어 모두 가능

**예시:**
| 상황 | description |
|------|-------------|
| 코드 탐색 | `"인증 모듈 구조 파악"` |
| AC 추적 | `"AC reverse tracing"` |
| 테스트 검색 | `"테스트 파일 검색"` |
| 빌드 실행 | `"프로젝트 빌드 중"` |

### 3.3 예시: AskUserQuestion - 브랜치 선택

보호된 브랜치(main/master) 감지 시 사용자에게 선택권 제공:

```markdown
## Phase 1: Branch Validation

**1. Check Branch Protection Status**

Use `check_branch_protection` MCP tool to verify current branch.

**2. Ask User - Branch Action**

If on protected branch, use `AskUserQuestion` tool:

\`\`\`yaml
questions:
  - question: "현재 보호된 브랜치({branch})에서 작업 중입니다. 어떻게 진행할까요?"
    header: "Branch"
    options:
      - label: "새 브랜치 생성 (Recommended)"
        description: "feature 브랜치를 생성하여 안전하게 작업합니다"
      - label: "현재 브랜치에서 계속"
        description: "⚠️ 보호된 브랜치에서 직접 작업합니다 (권장하지 않음)"
\`\`\`

**3. Ask User - Branch Name** (if creating new branch)

\`\`\`yaml
questions:
  - question: "생성할 브랜치 이름을 선택하세요"
    header: "Name"
    options:
      - label: "feature/{JIRA-ID}"
        description: "JIRA ID 기반 추천 브랜치 이름"
      - label: "직접 입력"
        description: "원하는 브랜치 이름을 직접 입력합니다"
\`\`\`
```

### 3.4 예시: Task - Agent 호출

Skill 내에서 별도 Agent를 서브태스크로 실행:

```markdown
## Phase 5E: Requirement Reverse Tracing (Optional)

**Execution Condition**: When linked to a JIRA issue

**1. Call requirement-validator Agent (Mode 1)**

Use `Task` tool to invoke the agent:

\`\`\`yaml
Tool: Task
Args:
  subagent_type: "wf:requirement-validator"
  description: "AC reverse tracing"
  prompt: |
    Mode 1: Reverse Tracing

    버그 위치에서 관련 AC를 역추적합니다.

    Input:
    - 버그 파일 경로: {bug_file_path}
    - 함수명: {function_name}

    Output:
    - 관련 AC 목록과 매핑 결과
\`\`\`

**2. Add Results to Report**
```

### 3.5 예시: 다음 단계 확인

워크플로우 완료 후 다음 Skill 실행 여부 확인:

```markdown
## Phase 9: Next Step Confirmation

After completing the report, ask user for next action:

\`\`\`yaml
questions:
  - question: "분석 리포트가 완성되었습니다. 다음 단계로 진행할까요?"
    header: "Next"
    options:
      - label: "plan 스킬 실행 (Recommended)"
        description: "분석 결과를 바탕으로 구현 계획을 수립합니다"
      - label: "여기서 종료"
        description: "분석만 완료하고 종료합니다"
\`\`\`
```

### 3.6 예시: Explore 에이전트로 코드베이스 탐색

복잡한 탐색 작업을 빠른 read-only 에이전트에 위임:

```markdown
## Phase 1: 코드베이스 탐색

Use `Task` tool with Explore agent for fast codebase investigation:

\`\`\`yaml
Tool: Task
Args:
  subagent_type: "Explore"
  description: "인증 모듈 구조 파악"
  prompt: |
    src/auth 디렉토리의 구조를 분석하세요.

    확인할 내용:
    - 주요 파일과 역할
    - 클래스/함수 관계
    - 외부 의존성

    Output: 구조 요약
\`\`\`
```

### 3.7 Subagent Types 선택 가이드

| Type | 용도 | 접근 도구 | 언제 사용? |
|------|------|----------|-----------|
| `Explore` | 코드베이스 탐색 | Read-only (Glob, Grep, Read) | 구조 파악, 파일 검색 (빠름) |
| `Plan` | 구현 계획 설계 | Read-only | 아키텍처 설계, 계획 수립 |
| `Bash` | 명령 실행 | Bash만 | 빌드, 테스트, git 명령 |
| `general-purpose` | 범용 멀티스텝 | All | 복잡한 작업, 파일 수정 포함 |
| `{plugin}:{agent}` | 커스텀 에이전트 | Agent 설정에 따름 | 플러그인 Agent 호출 |

**선택 기준:**
- 읽기만 필요? → `Explore` (가장 빠름)
- 명령 실행만? → `Bash`
- 파일 수정 포함? → `general-purpose`
- 특수 로직 필요? → 커스텀 Agent (`wf:requirement-validator`)

### 3.8 작성 팁

- **영어로 지시문 작성**: `Use AskUserQuestion tool to provide options:`
- **한국어로 사용자 메시지**: `question: "현재 보호된 브랜치에서..."`
- **Recommended 표시**: 권장 옵션에 `(Recommended)` 붙이기
- **description 활용**: 각 선택지의 결과를 명확히 설명

---

## 4. Agent 개발

Agent는 여러 Skill에서 공유하는 자율 실행 컴포넌트입니다.

### 4.1 기본 구조

```
agents/
└── my-agent.md
```

### 4.2 Agent 파일 구조

```markdown
---
name: my-agent
description: |
  Agent description for triggering conditions.
  Korean: 한국어 트리거 키워드
tools: Read, Write, Grep, Glob, Bash, WebFetch
model: sonnet
---

# My Agent

## 개요
에이전트가 수행하는 작업에 대한 설명.

## 실행 모드

### Mode 1: 모드명
**트리거**: 언제 이 모드가 실행되는지
**입력**: 필요한 입력 정보
**출력**: 생성되는 결과물

### Mode 2: 다른 모드
...

## Phase 1: 컨텍스트 수집
- 필요한 정보 수집 단계

## Phase 2: 분석
- 수집된 정보 분석

## Phase 3: 결과 생성
- 최종 결과물 생성

## 출력 형식
결과물 형식 정의.
```

### 4.3 Agent vs Skill 선택 기준

| 상황 | 선택 |
|------|------|
| 단일 워크플로우 | Skill |
| 여러 Skill에서 공유 | Agent |
| 자율적 판단 필요 | Agent |
| 순차적 단계 실행 | Skill |

---

## 5. MCP 서버 설정

플러그인 내부에 MCP 서버를 등록하여 커스텀 도구를 제공할 수 있습니다.

### 5.1 `.mcp.json` 기본 구조

```json
{
  "server-name": {
    "command": "실행 명령",
    "args": ["인자", "목록"],
    "env": {
      "ENV_VAR": "${SYSTEM_ENV_VAR:-기본값}"
    }
  }
}
```

### 5.2 실행 방식별 패턴

#### Pattern 1: uvx (Python 패키지)

**단일 패키지 실행**
```json
{
  "atlassian": {
    "command": "uvx",
    "args": ["mcp-atlassian"],
    "env": {
      "JIRA_URL": "${ATLASSIAN_URL:-}",
      "JIRA_USERNAME": "${ATLASSIAN_USERNAME:-}",
      "JIRA_API_TOKEN": "${ATLASSIAN_API_TOKEN:-}"
    }
  }
}
```

**커스텀 서버 + 의존성 설치**
```json
{
  "git": {
    "command": "uvx",
    "args": [
      "--from", "mcp[cli]",
      "mcp", "run", "${CLAUDE_PLUGIN_ROOT}/git_local_server.py"
    ]
  }
}
```

**여러 패키지 설치 (--with)**
```json
{
  "gitlab": {
    "command": "uvx",
    "args": [
      "--from", "mcp[cli]",
      "--with", "python-gitlab",
      "--with", "requests>=2.28.0",
      "mcp", "run", "${CLAUDE_PLUGIN_ROOT}/gitlab_server.py"
    ]
  }
}
```

**버전 지정**
```json
{
  "my-server": {
    "command": "uvx",
    "args": [
      "--from", "mcp[cli]>=1.0.0",
      "--with", "pandas==2.0.0",
      "--with", "numpy>=1.24,<2.0",
      "mcp", "run", "${CLAUDE_PLUGIN_ROOT}/server.py"
    ]
  }
}
```

#### Pattern 2: npx (npm 패키지)

**기본 사용**
```json
{
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN:-}"
    }
  }
}
```

**옵션 포함**
```json
{
  "slack": {
    "command": "npx",
    "args": ["-y", "slack-mcp-server@latest", "--transport", "stdio"],
    "env": {
      "SLACK_MCP_XOXB_TOKEN": "${SLACK_BOT_TOKEN:-}"
    }
  }
}
```

#### Pattern 3: Docker

```json
{
  "terraform": {
    "type": "stdio",
    "command": "docker",
    "args": ["run", "-i", "--rm", "hashicorp/terraform-mcp-server"]
  }
}
```

#### Pattern 4: 로컬 스크립트 직접 실행

```json
{
  "local": {
    "command": "python",
    "args": ["${CLAUDE_PLUGIN_ROOT}/my_server.py"]
  }
}
```

#### Pattern 5: args에 환경변수 직접 전달

```json
{
  "amplitude": {
    "command": "npx",
    "args": [
      "-y",
      "amplitude-mcp-server",
      "--api-key",
      "${AMPLITUDE_API_KEY:-}"
    ]
  }
}
```

> **Tip**: `env` 블록 대신 `args`에 직접 `${VAR:-}` 형식으로 환경변수 전달 가능

### 5.3 환경변수 문법

```json
"env": {
  "REQUIRED_VAR": "${SYSTEM_VAR}",           // 필수 (없으면 에러)
  "OPTIONAL_VAR": "${SYSTEM_VAR:-}",         // 선택 (없으면 빈 문자열)
  "WITH_DEFAULT": "${SYSTEM_VAR:-default}"   // 기본값 지정
}
```

### 5.4 커스텀 MCP 서버 구현 (Python)

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def my_tool(param1: str, param2: int = 10) -> dict:
    """도구 설명 (한국어 권장)

    Args:
        param1: 첫 번째 파라미터 설명
        param2: 두 번째 파라미터 (기본값: 10)

    Returns:
        결과 딕셔너리
    """
    try:
        # 비즈니스 로직
        result = do_something(param1, param2)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def another_tool(items: list[str]) -> dict:
    """리스트를 받는 도구 예시"""
    return {"success": True, "count": len(items)}

if __name__ == "__main__":
    mcp.run()
```

**의존성이 필요한 경우:**

```python
# gitlab_server.py
import gitlab  # --with python-gitlab 으로 설치됨
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("gitlab")

@mcp.tool()
def get_project(project_id: int) -> dict:
    """GitLab 프로젝트 정보 조회"""
    gl = gitlab.Gitlab(
        url=os.environ.get("GITLAB_URL"),
        private_token=os.environ.get("GITLAB_TOKEN")
    )
    project = gl.projects.get(project_id)
    return {"success": True, "name": project.name, "url": project.web_url}
```

---

## 6. Command 개발

Command는 사용자가 `/명령어`로 직접 호출하는 기능입니다.

### 6.1 기본 구조

```
commands/
└── my-command.md
```

### 6.2 Command 파일 구조

```markdown
---
name: my-command
description: "커맨드 설명"
arguments:
  - name: target
    description: "대상 지정"
    required: true
  - name: options
    description: "추가 옵션"
    required: false
    default: "default-value"
---

# My Command

## 사용법
/my-command <target> [options]

## 동작
1. target 파라미터 검증
2. 작업 수행
3. 결과 출력

## 예시
/my-command src/main.py --verbose
```

---

## 7. Hook 개발

Hook은 특정 이벤트 발생 시 자동 실행되는 로직입니다.

### 7.1 지원 이벤트

| 이벤트 | 설명 |
|--------|------|
| `PreToolUse` | 도구 실행 전 |
| `PostToolUse` | 도구 실행 후 |
| `Stop` | 에이전트 종료 시 |
| `SubagentStop` | 서브에이전트 종료 시 |
| `SessionStart` | 세션 시작 시 |
| `SessionEnd` | 세션 종료 시 |
| `UserPromptSubmit` | 사용자 입력 제출 시 |
| `PreCompact` | 컨텍스트 압축 전 |
| `Notification` | 알림 발생 시 |

### 7.2 Hook 파일 구조

```markdown
---
name: dangerous-command-blocker
description: "위험한 명령어 차단"
event: PreToolUse
tools: [Bash]
---

# Dangerous Command Blocker

## 검사 대상
- `rm -rf /`
- `git push --force`
- `DROP TABLE`

## 동작
위험한 명령어 감지 시 실행을 차단하고 경고 메시지 출력.

## 차단 조건
```json
{
  "block": true,
  "message": "위험한 명령어가 감지되었습니다: {command}"
}
```
```

---

## 8. 주의사항 및 팁

### 8.1 Tool Name 64자 제한

Claude API는 tool name을 **최대 64자**로 제한합니다.

**자동 생성 패턴:**
```
mcp__plugin_<PLUGIN_NAME>_<SERVER_NAME>__<TOOL_NAME>
│           │              │               │
└─ 12자 ───┘              │               │
            고정 prefix    MCP 서버 키     도구 함수명
```

**권장 길이:**
- Plugin name: **최대 10자**
- MCP server name: **최대 5자**
- Tool function name: **최대 30자**

**예시:**
```
# ❌ 너무 긴 이름 (64자 초과)
mcp__plugin_workflow-bundle_sequential-thinking__analyze_requirements
           ↑ 15자              ↑ 19자                 ↑ 20자

# ✅ 짧은 이름 (64자 이내)
mcp__plugin_wf_st__analyze_req
           ↑ 2자   ↑ 2자   ↑ 11자
```

### 8.2 `${CLAUDE_PLUGIN_ROOT}` 변수

플러그인 루트 경로를 자동으로 치환합니다.

```json
{
  "my-server": {
    "command": "python",
    "args": ["${CLAUDE_PLUGIN_ROOT}/server.py"]
  }
}
```

> **주의**: 이 변수는 `.mcp.json`과 일부 설정 파일에서만 동작합니다.

### 8.3 uvx vs npx 선택

| 기준 | uvx | npx |
|------|-----|-----|
| 언어 | Python | JavaScript/TypeScript |
| 패키지 저장소 | PyPI | npm |
| 의존성 추가 | `--with package` | 지원 안 함 |
| 속도 | 빠름 (uv 기반) | 보통 |

### 8.4 디버깅 팁

**MCP 서버 로컬 테스트:**
```bash
# uvx로 직접 실행
uvx --from "mcp[cli]" mcp run ./my_server.py

# 또는 mcp dev 모드
uvx --from "mcp[cli]" mcp dev ./my_server.py
```

**로그 확인:**
```python
import sys

def log(message):
    print(message, file=sys.stderr)

@mcp.tool()
def my_tool():
    log("Debug: tool called")
    ...
```

### 8.5 버전 관리

플러그인 버전 업데이트 시 동기화 필요:
- `plugin.json` → version 필드
- `marketplace.json` → 해당 플러그인 버전
- `CHANGELOG.md` → 변경 이력

---

## 부록: 실제 플러그인 예시

### A. wf (워크플로우 번들)

```
wf/
├── .claude-plugin/plugin.json
├── .mcp.json                    # git MCP 서버
├── git_local_server.py          # 커스텀 Git 도구 (12개)
├── skills/
│   ├── analyze/                 # 근본 원인 분석
│   ├── plan/                    # 구현 계획 수립
│   ├── execute/                 # 계획 실행
│   └── record/                  # 문서화
└── agents/
    └── requirement-validator.md # AC 검증 에이전트
```

### B. glmr (GitLab MR 관리)

```
glmr/
├── .claude-plugin/plugin.json
├── .mcp.json                    # GitLab CI MCP 서버
├── gitlab_ci_server.py          # CI/MR 도구 (12개)
└── skills/
    ├── mr-review/               # MR 코드 리뷰
    └── fix-discussion/          # Discussion 해결
```

### C. 외부 MCP만 사용하는 플러그인

```
github/
├── .claude-plugin/plugin.json
└── .mcp.json
```

```json
// .mcp.json
{
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN:-}"
    }
  }
}
```

---

## 참고 자료

- [Claude Code 공식 문서](https://docs.anthropic.com/claude-code)
- [MCP 프로토콜 스펙](https://modelcontextprotocol.io)
- [FastMCP 라이브러리](https://github.com/jlowin/fastmcp)
- [uv/uvx 문서](https://docs.astral.sh/uv/)
