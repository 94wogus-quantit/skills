# Claude Code Tools Reference

Skill 작성 시 활용 가능한 Claude Code 내장 도구들의 레퍼런스 문서입니다.

> **Note**: Skill에서는 도구를 직접 호출하지 않고, Claude가 적절한 도구를 선택하도록 **지시(instruction)**를 작성합니다.

---

## Table of Contents

- [File Operations](#file-operations)
- [Search Tools](#search-tools)
- [Shell Execution](#shell-execution)
- [User Interaction](#user-interaction)
- [Web Tools](#web-tools)
- [Agent & Task Tools](#agent--task-tools)
- [Todo Management](#todo-management)
- [Plan Mode](#plan-mode)
- [MCP & Plugin Tools](#mcp--plugin-tools)
- [Skill 작성 시 활용 가이드](#skill-작성-시-활용-가이드)

---

## File Operations

### Read

파일 내용을 읽습니다. 이미지, PDF, Jupyter 노트북도 지원합니다.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | ✅ | 절대 경로 |
| `offset` | number | ❌ | 시작 라인 번호 |
| `limit` | number | ❌ | 읽을 라인 수 |

**Skill 활용 예시:**
```markdown
## Phase 1: 코드 분석
Read the target file to understand its structure.

**Example:**
- `src/auth/login.ts` 파일을 읽어 현재 구현 파악
- 에러 발생 위치 주변 코드 확인
```

---

### Write

새 파일을 생성하거나 기존 파일을 덮어씁니다.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | ✅ | 절대 경로 |
| `content` | string | ✅ | 파일 내용 |

**주의사항:**
- 기존 파일 수정 시 반드시 먼저 `Read`로 읽어야 함
- 새 파일 생성보다 기존 파일 수정 권장

**Skill 활용 예시:**
```markdown
## Phase 3: 결과물 생성
Generate the analysis report as a markdown file.

**Output:**
- `[ISSUE_ID]_REPORT.md` 파일로 분석 결과 저장
```

---

### Edit

파일 내 특정 문자열을 교체합니다. 정확한 문자열 매칭이 필요합니다.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | ✅ | 절대 경로 |
| `old_string` | string | ✅ | 교체할 원본 문자열 |
| `new_string` | string | ✅ | 새 문자열 |
| `replace_all` | boolean | ❌ | 모든 occurrence 교체 여부 (default: false) |

**주의사항:**
- `old_string`이 파일 내에서 고유해야 함
- 고유하지 않으면 더 많은 컨텍스트 포함 필요

**Skill 활용 예시:**
```markdown
## Phase 2: 코드 수정
Apply the fix by editing the specific function.

**Example:**
- `validateUser` 함수의 에러 처리 로직 수정
- 기존 `throw new Error()` → `throw new AuthError()` 변경
```

---

### NotebookEdit

Jupyter 노트북(.ipynb) 셀을 편집합니다.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `notebook_path` | string | ✅ | 노트북 절대 경로 |
| `new_source` | string | ✅ | 새 셀 내용 |
| `cell_id` | string | ❌ | 편집할 셀 ID |
| `cell_type` | string | ❌ | `code` 또는 `markdown` |
| `edit_mode` | string | ❌ | `replace`, `insert`, `delete` |

---

## Search Tools

### Glob

파일 패턴으로 파일을 검색합니다. 결과는 수정 시간순 정렬됩니다.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pattern` | string | ✅ | Glob 패턴 (예: `**/*.ts`) |
| `path` | string | ❌ | 검색 시작 디렉토리 |

**Skill 활용 예시:**
```markdown
## Phase 1: 관련 파일 탐색
Find all TypeScript files in the auth module.

**Example:**
- `src/auth/**/*.ts` 패턴으로 인증 관련 파일 검색
- `**/*test*.ts` 패턴으로 테스트 파일 검색
```

---

### Grep

파일 내용에서 패턴을 검색합니다. Regex 지원, ripgrep 기반입니다.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pattern` | string | ✅ | 검색 패턴 (regex) |
| `path` | string | ❌ | 검색 경로 |
| `glob` | string | ❌ | 파일 필터 (예: `*.js`) |
| `type` | string | ❌ | 파일 타입 (예: `ts`, `py`) |
| `output_mode` | string | ❌ | `content`, `files_with_matches`, `count` |
| `-A`, `-B`, `-C` | number | ❌ | 컨텍스트 라인 수 |
| `-i` | boolean | ❌ | 대소문자 무시 |
| `multiline` | boolean | ❌ | 멀티라인 매칭 |

**Skill 활용 예시:**
```markdown
## Phase 1: 사용처 검색
Search for all usages of the target function.

**Example:**
- `validateUser` 함수 호출 위치 검색
- `import.*auth` 패턴으로 인증 모듈 import 추적
```

---

## Shell Execution

### Bash

셸 명령을 실행합니다. Git, npm, docker 등 터미널 작업에 사용합니다.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `command` | string | ✅ | 실행할 명령 |
| `description` | string | ❌ | 명령 설명 |
| `timeout` | number | ❌ | 타임아웃 (ms, max 600000) |
| `run_in_background` | boolean | ❌ | 백그라운드 실행 |

**주의사항:**
- 파일 읽기/쓰기는 전용 도구 사용 권장 (`cat`, `echo` 대신 `Read`, `Write`)
- 검색은 `Glob`, `Grep` 사용 권장

**Skill 활용 예시:**
```markdown
## Phase 2: 테스트 실행
Run the test suite to verify the fix.

**Example:**
- `npm test -- --grep "auth"` 로 인증 관련 테스트 실행
- `git diff HEAD~1` 로 변경사항 확인
```

---

## User Interaction

### AskUserQuestion

사용자에게 질문하고 선택지를 제공합니다.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `questions` | array | ✅ | 질문 목록 (1-4개) |
| `questions[].question` | string | ✅ | 질문 내용 |
| `questions[].header` | string | ✅ | 짧은 라벨 (max 12자) |
| `questions[].options` | array | ✅ | 선택지 (2-4개) |
| `questions[].options[].label` | string | ✅ | 선택지 표시 텍스트 |
| `questions[].options[].description` | string | ✅ | 선택지 설명 |
| `questions[].multiSelect` | boolean | ❌ | 다중 선택 허용 |

**Skill 활용 예시:**
```markdown
## Phase 2: 구현 방향 결정
If multiple fix approaches exist, ask the user for preference.

**Example:**
- 수정 방식이 여러 개일 때 사용자에게 선택 요청
- "기존 API 유지 vs Breaking Change 허용" 결정
```

---

## Web Tools

### WebFetch

URL에서 콘텐츠를 가져와 분석합니다.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | ✅ | 가져올 URL |
| `prompt` | string | ✅ | 콘텐츠 분석 프롬프트 |

**주의사항:**
- 인증이 필요한 URL은 실패함 (Google Docs, Jira 등)
- GitHub URL은 `gh` CLI 사용 권장

---

### WebSearch

웹 검색을 수행합니다.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | ✅ | 검색 쿼리 |
| `allowed_domains` | array | ❌ | 허용 도메인 목록 |
| `blocked_domains` | array | ❌ | 차단 도메인 목록 |

**Skill 활용 예시:**
```markdown
## Phase 1: 외부 정보 수집
Search for known issues or solutions related to the error.

**Example:**
- 에러 메시지로 관련 GitHub issues 검색
- 라이브러리 버전 호환성 정보 검색
```

---

## Agent & Task Tools

### Task

서브에이전트를 실행합니다. 복잡한 작업을 위임할 때 사용합니다.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | ✅ | 에이전트에게 전달할 작업 |
| `description` | string | ✅ | 작업 설명 (3-5 단어) |
| `subagent_type` | string | ✅ | 에이전트 타입 |
| `model` | string | ❌ | 모델 선택 (`sonnet`, `opus`, `haiku`) |
| `run_in_background` | boolean | ❌ | 백그라운드 실행 |
| `resume` | string | ❌ | 이전 에이전트 ID로 재개 |

#### Available Subagent Types

| Type | Description | Tools Available |
|------|-------------|-----------------|
| `Bash` | 명령 실행 전문 | Bash |
| `general-purpose` | 범용 에이전트, 복잡한 멀티스텝 작업 | All |
| `Explore` | 코드베이스 탐색 전문 (빠름) | Read-only tools |
| `Plan` | 구현 계획 설계 | Read-only tools |
| `claude-code-guide` | Claude Code 기능 질문 응답 | Glob, Grep, Read, WebFetch, WebSearch |
| `statusline-setup` | 상태줄 설정 | Read, Edit |
| `plugin-dev:agent-creator` | 플러그인 에이전트 생성 | All |
| `plugin-dev:skill-reviewer` | 스킬 리뷰 | All |
| `plugin-dev:plugin-validator` | 플러그인 검증 | All |
| `agent-sdk-dev:agent-sdk-verifier-ts` | TS Agent SDK 검증 | All |
| `agent-sdk-dev:agent-sdk-verifier-py` | Python Agent SDK 검증 | All |
| `wf:requirement-validator` | 요구사항 검증 | All |

**Skill 활용 예시:**
```markdown
## Phase 1: 코드베이스 탐색
Use Explore agent to understand the codebase structure.

**Example:**
- Explore 에이전트로 인증 모듈 구조 파악
- "src/auth 디렉토리의 아키텍처 분석" 요청
```

---

### TaskOutput

백그라운드 태스크의 결과를 조회합니다.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | string | ✅ | 태스크 ID |
| `block` | boolean | ✅ | 완료 대기 여부 |
| `timeout` | number | ✅ | 대기 시간 (ms) |

---

### TaskStop

실행 중인 백그라운드 태스크를 중지합니다.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | string | ✅ | 중지할 태스크 ID |

---

## Todo Management

복잡한 작업의 진행 상황을 추적합니다.

### TaskCreate

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `subject` | string | ✅ | 작업 제목 (명령형) |
| `description` | string | ✅ | 상세 설명 |
| `activeForm` | string | ❌ | 진행 중 표시 문구 (현재진행형) |

### TaskGet

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `taskId` | string | ✅ | 조회할 작업 ID |

### TaskUpdate

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `taskId` | string | ✅ | 업데이트할 작업 ID |
| `status` | string | ❌ | `pending`, `in_progress`, `completed`, `deleted` |
| `addBlockedBy` | array | ❌ | 선행 작업 ID 목록 |
| `addBlocks` | array | ❌ | 후행 작업 ID 목록 |

### TaskList

파라미터 없음. 전체 작업 목록을 반환합니다.

**Skill 활용 예시:**
```markdown
## Execution Tracking
Use TodoList to track multi-step implementation progress.

**Example:**
1. "코드 분석" 태스크 생성 및 완료 처리
2. "테스트 작성" 태스크는 "코드 수정" 완료 후 시작
3. 각 Phase 완료 시 상태 업데이트
```

---

## Plan Mode

구현 전 계획을 수립하고 사용자 승인을 받습니다.

### EnterPlanMode

계획 모드로 진입합니다. 파라미터 없음.

### ExitPlanMode

계획 모드를 종료하고 사용자 승인을 요청합니다.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `allowedPrompts` | array | ❌ | 필요한 권한 목록 |

---

## MCP & Plugin Tools

### ToolSearch

Deferred(지연 로드) 도구를 검색하고 로드합니다.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | ✅ | 검색어 또는 `select:<tool_name>` |
| `max_results` | number | ❌ | 최대 결과 수 (default: 5) |

**사용 패턴:**
```
# 키워드 검색
query: "slack message"

# 직접 선택
query: "select:mcp__plugin_slack_slack__channels_list"

# 필수 키워드 포함
query: "+github create issue"
```

---

### Skill

등록된 Skill을 실행합니다.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `skill` | string | ✅ | 스킬 이름 (예: `commit`, `wf:analyze`) |
| `args` | string | ❌ | 스킬 인자 |

---

### ListMcpResourcesTool

MCP 서버의 리소스 목록을 조회합니다.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `server` | string | ❌ | 특정 서버만 조회 |

---

### ReadMcpResourceTool

MCP 서버의 특정 리소스를 읽습니다.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `server` | string | ✅ | MCP 서버 이름 |
| `uri` | string | ✅ | 리소스 URI |

---

## Skill 작성 시 활용 가이드

### 도구 활용 원칙

1. **직접 호출하지 않음**: Skill은 도구를 직접 호출하지 않고, Claude가 선택하도록 지시
2. **명확한 의도 전달**: 어떤 작업을 해야 하는지 명확히 기술
3. **적절한 도구 힌트**: 특정 도구가 적합할 때 언급 가능

### 도구별 Skill 지시문 패턴

#### 파일 읽기
```markdown
<!-- ✅ Good -->
Read the configuration file to understand current settings.

<!-- ❌ Bad -->
Use the Read tool with file_path="/path/to/config.json".
```

#### 코드 검색
```markdown
<!-- ✅ Good -->
Search for all usages of `AuthService` class across the codebase.

<!-- ❌ Bad -->
Call Grep with pattern="AuthService" and type="ts".
```

#### 사용자 질문
```markdown
<!-- ✅ Good -->
If the fix approach is ambiguous, ask the user to choose between:
- Option A: Backward-compatible fix
- Option B: Breaking change with migration

<!-- ❌ Bad -->
Use AskUserQuestion tool with options array...
```

#### 에이전트 위임
```markdown
<!-- ✅ Good -->
Use the Explore agent to investigate the authentication module structure.

<!-- ❌ Bad -->
Call Task tool with subagent_type="Explore" and prompt="..."
```

### Phase별 권장 도구 조합

| Phase | 주요 작업 | 권장 도구 |
|-------|----------|----------|
| **Context Collection** | 파일 탐색, 코드 검색 | Glob, Grep, Read, Task(Explore) |
| **Analysis** | 코드 분석, 의존성 추적 | Read, Grep, Task(Explore) |
| **Decision** | 사용자 확인, 방향 결정 | AskUserQuestion |
| **Implementation** | 코드 수정, 파일 생성 | Edit, Write, Bash |
| **Verification** | 테스트, 검증 | Bash, Read |
| **Documentation** | 결과 정리, 보고서 | Write |

### 주의사항

1. **Read 먼저**: 파일 수정 전 반드시 읽기 지시
2. **Edit 우선**: 새 파일 생성보다 기존 파일 수정 권장
3. **Bash 제한**: 파일 작업은 전용 도구 사용 지시
4. **병렬 처리**: 독립적인 작업은 병렬 실행 가능함을 인지

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code Tools                        │
├─────────────────────────────────────────────────────────────┤
│ FILE OPS     │ Read, Write, Edit, NotebookEdit              │
│ SEARCH       │ Glob (files), Grep (content)                 │
│ SHELL        │ Bash                                         │
│ USER         │ AskUserQuestion                              │
│ WEB          │ WebFetch, WebSearch                          │
│ AGENTS       │ Task (subagent_type), TaskOutput, TaskStop   │
│ TODO         │ TaskCreate, TaskGet, TaskUpdate, TaskList    │
│ PLAN         │ EnterPlanMode, ExitPlanMode                  │
│ MCP          │ ToolSearch, Skill, ListMcp*, ReadMcp*        │
└─────────────────────────────────────────────────────────────┘

Subagent Types:
  Explore    → 코드베이스 탐색 (빠름, read-only)
  Plan       → 구현 계획 설계 (read-only)
  Bash       → 명령 실행 전문
  general-purpose → 범용 (모든 도구)
```

---

*Last Updated: 2026-02-04*
