# Architecture

이 문서는 프로젝트의 고수준 아키텍처를 설명합니다.
모든 기여자가 읽어야 하므로 간결하게 유지합니다.

> 참고: [matklad's ARCHITECTURE.md](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html) 패턴을 따릅니다.

## Bird's Eye View

Claude Code를 확장하는 플러그인 컬렉션입니다. 핵심은 **워크플로우 스킬**(analyze → plan → execute → record)로, 이슈 분석부터 문서화까지 소프트웨어 개발의 전체 사이클을 체계적으로 자동화합니다. 워크플로우 외에도 GitLab, JIRA 등 외부 서비스 통합을 위한 MCP 플러그인을 제공합니다.

## Code Map

### `.claude-plugin/marketplace.json`

마켓플레이스 카탈로그. 10개 독립 플러그인의 메타데이터(이름, 설명, 소스 경로, 태그)를 정의합니다. 사용자가 `/marketplace` 명령으로 설치할 플러그인 목록을 결정합니다.

### `plugins/wf/`

메인 워크플로우 플러그인. 4개 스킬 + 1개 에이전트 + Git MCP를 포함합니다.

- `skills/analyze/` — 이슈/버그 근본 원인 분석. `*_REPORT.md` 생성. 일론 머스크 5단계 사고법 적용.
- `skills/plan/` — 구현 계획 생성. `*_PLAN.md` 생성. 자동 반복 검토(review loop)로 품질 보장.
- `skills/execute/` — 승인된 계획 실행. TaskList 추적. 코드 구현과 테스트에만 집중.
- `skills/record/` — 워크플로우 산출물 수집 → 프로젝트 문서 종합 업데이트 (README, ARCHITECTURE, CHANGELOG, CLAUDE.md, Serena 메모리, JIRA).
- `agents/requirement-validator.md` — JIRA AC ↔ 코드 매핑. 4가지 모드로 4개 스킬에서 자동 호출.
- `.mcp.json` — Git MCP 서버 설정 (`git_status`, `git_commit`, `create_feature_branch` 등 12개 도구).

### `plugins/glmr/`

GitLab MR 관리 플러그인. CI/CD MCP(12개 도구) + 2개 스킬(`mr-review`, `fix-discussion`).

### `plugins/seq-think/`

Sequential Thinking MCP. 체계적 단계별 사고를 위한 MCP 서버 래퍼.

### `plugins/atlassian/`, `plugins/github/`, `plugins/amplitude/`, `plugins/terraform/`

각각 외부 서비스 통합 MCP 플러그인. `plugin.json` + `.mcp.json`으로 구성되며 스킬 없이 MCP 도구만 제공.

### `plugins/ask-yt/`

YouTube 내장 AI "질문하기(Ask)" CDP 자동화 플러그인. `youtube_ask_server.py` (Python Playwright MCP 서버) + `ask-yt` 스킬로 구성.

- `youtube_ask_server.py` — FastMCP 서버. 3개 도구: `open_ask_panel` (패널 열기), `ask_video` (질문), `close_session` (종료). 글로벌 `_pw`/`_page` 상태로 멀티턴 대화 지원.
- `skills/ask-yt/SKILL.md` — Chrome CDP 설정 가이드(Phase 0) 포함. URL+질문 → AI 응답 자동화 플로우.
- `.mcp.json` — `uvx --from mcp[cli] --with playwright mcp run` 패턴으로 실행. `--with playwright` 필수.

### `plugins/notify/`

macOS 알림 + TTS 훅 전용 플러그인. MCP·스킬·에이전트 없이 훅(`Stop`, `Notification`)만으로 구성된 최소 설계.

- `hooks/notify.sh` — 핵심 스크립트. stdin JSON 파싱(Python3 단일 호출) → 4단계 fallback으로 알림 내용 추출 → osascript 팝업 + `say -v Yuna` TTS 비동기 발송. Python `subprocess.Popen(['osascript', '-e', ...])` 패턴으로 shell injection 완전 차단.
- `hooks/hooks.json` — `Stop`(작업 완료) + `Notification`(확인 요청) 훅 설정. `timeout: 10`, `bash ${CLAUDE_PLUGIN_ROOT}/hooks/notify.sh` 실행.

### `changelogs/`

버전별 상세 변경 이력. `CHANGELOG.md`는 인덱스 역할, 실제 내용은 이 디렉토리의 개별 파일에 위임.

## Architectural Invariants

- **플러그인 독립성**: 각 `plugins/*/`는 완전히 독립적으로 설치/제거 가능. 플러그인 간 직접 의존 없음.
- **워크플로우 순서**: `analyze → plan → execute → record` 순서는 강제되지 않지만, 각 스킬의 입력은 이전 스킬의 출력(`*_REPORT.md`, `*_PLAN.md`)에 의존.
- **MCP 도구명 64자 제한**: `mcp__plugin_{NAME}_{SERVER}__{TOOL}` 패턴. Plugin name ≤10자, MCP server key ≤5자, Tool name ≤30자.
- **지시문은 영어, 출력은 한국어**: SKILL.md의 워크플로우 지시문은 영어, 사용자 대면 출력/템플릿은 한국어.
- **브랜치 보호**: 모든 스킬은 보호된 브랜치(main/master/staging) 감지 시 경고 또는 feature 브랜치 생성을 강제.
- **훅 전용 플러그인 패턴**: MCP·스킬 없이 훅(`hooks.json` + `notify.sh`)만으로 구성 가능. `notify` 플러그인이 첫 사례. 훅 스크립트는 항상 `exit 0` (Claude 블로킹 방지).
- **훅 스크립트 보안**: osascript 호출 시 heredoc 대신 Python `subprocess.Popen(['osascript', '-e', script])` 사용 (backtick/shell injection 방지). TTS 문자 절단은 `head -c` 대신 Python `[:N]` 사용 (UTF-8 안전).

## Cross-cutting Concerns

### 한국어 정책

모든 스킬의 출력(리포트, 계획서, 문서, JIRA 코멘트)은 한국어가 기본. `SKILL.md`의 `⚠️ CRITICAL LANGUAGE POLICY` 섹션으로 강제.

### 브랜치 검증

`check_branch_protection` MCP 도구를 통해 모든 스킬의 Phase 1에서 현재 브랜치를 검증. `AskUserQuestion`으로 사용자에게 브랜치 생성을 안내.

### TaskList 추적

`execute`와 `record` 스킬은 Phase 0에서 모든 Phase를 `TaskCreate`로 등록하고, 진행 상태를 `TaskUpdate`로 추적.

### 버전 동기화

버전 변경 시 `marketplace.json`, `CLAUDE.md`, `README.md`, `CHANGELOG.md` 4곳을 동시에 업데이트해야 함. `record` 스킬이 이를 자동화.
