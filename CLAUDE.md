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

**Key Artifacts (v3.33.0):**
- **Skills**: Workflow orchestrators for multi-step processes (분석, 계획, 실행, 문서화)
- **Agents**: AC (Acceptance Criteria) traceability (requirement-validator만 유지)
- **Custom Commands**: Workflow automation commands (별도 설치)
- **Reference Materials**: Templates and pattern catalogs

## Repository Structure

```
wogus-plugin/  (v3.33.0)
├── .claude-plugin/
│   └── marketplace.json       # 카탈로그 (9 plugins)
│
├── plugins/                   # 모든 플러그인
│   ├── wf/                    # 메인 워크플로우 플러그인 (v3.30.0)
│   │   ├── .claude-plugin/plugin.json
│   │   ├── git_local_server.py + .mcp.json   # 12 git tools
│   │   ├── skills/            # 자동 인식 (5개)
│   │   │   ├── analyze/
│   │   │   ├── plan/          # External review gate (wf:wf-review-plan)
│   │   │   ├── execute/       # Phase 7.5: wf:qa spawn
│   │   │   ├── qa/            # NEW: independent acceptance gate
│   │   │   └── record/
│   │   ├── agents/
│   │   │   ├── requirement-validator.md
│   │   │   ├── wf-review-analyze.md          # NEW
│   │   │   ├── wf-review-plan.md             # NEW
│   │   │   └── wf-review-record.md           # NEW
│   │   └── hooks/                            # NEW
│   │       ├── hooks.json                    # PostToolUse(Write) matcher
│   │       └── wf-review-gate.sh             # *_REPORT/PLAN/CHANGELOG/REVIEW.md routing
│   ├── run-ralph/             # Ralph Loop wrapper (choo-choo skill + agents + Stop hook)
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/choo-choo/  # 사용자 트리거: /run-ralph:choo-choo
│   │   ├── agents/            # ralph-reviewer, ralph-qa
│   │   └── hooks/             # report-gate.sh + record-gate.sh + hooks.json (v1.2)
│   ├── seq-think/             # Sequential Thinking MCP
│   ├── terraform/
│   ├── atlassian/
│   ├── github/                # GitHub MCP (v3.14.0)
│   ├── slack/                 # Slack MCP
│   ├── arkraft-wiki/          # v3.32: wikify thin wrapper (run-ralph:choo-choo 위임)
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/wikify/     # SKILL + 4 references + settings template
│   └── blogpost/              # NEW v3.33: multi-agent 블로그 작성 + 이미지 큐레이션 + S3 sync
│       ├── .claude-plugin/plugin.json
│       ├── agents/            # 6 agents (researcher / research-reviewer / image-curator / writer / writing-reviewer / html-renderer)
│       ├── commands/          # create.md, update.md
│       ├── scripts/           # render.py + sync_s3.sh + test_fixture/
│       ├── templates/         # blog.html.j2 (Jinja layout, floating TOC + figure styling)
│       └── README.md
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

### plan (v3.30.0)
Create high-quality implementation plans through **external review gate** (replaces v3.26 self-review loop).
- **5단계 알고리즘**: 요구사항 질의 → 삭제 → 단순화 → 가속 → 자동화
- **Idiot Index**: 계획 효율성 메트릭 (과잉 설계 방지)
- **Zero-Context 원칙**: 정확한 파일 경로·코드 스니펫·테스트 커맨드 필수
- **External review gate (v3.30 신규)**: PLAN.md Write → wf-review-gate hook PostToolUse → wf:wf-review-plan agent spawn → LGTM verdict 받을 때까지 Write→Review 사이클. Worker는 자체 LGTM 발행 금지.
- **AC pre-validation**: requirement-validator Mode 2 호출 (LGTM 후)
- **브랜치 검증** (feature 브랜치 확인)
- **Output**: `[FEATURE]_PLAN.md` + `[FEATURE]_PLAN_REVIEW.md` (audit artifact)
- **Integration**: Second step in workflow

### execute (v3.30.0)
Execute approved implementation plans with TodoList tracking, auto-recovery, and **independent QA gate** (v3.30 신규).
- **Auto-recovery loop**: 테스트/검증 실패 시 자동 복구 (최대 3회, 8가지 실패 타입)
- **Phase 7.5 (v3.30 신규)**: AC Achievement Report 직후 `Skill(wf:qa)` 자동 spawn. PASS verdict 받아야 Phase 8 (Testing) → record 진행. Worker 자체 PASS 발행 금지.
- **브랜치 검증** (보호된 브랜치 경고)
- **Output**: Code implementation + test results + `[ISSUE_ID]_QA.md` (외부 검증)
- **Integration**: Third step in workflow

### qa (v3.30.0 — NEW)
Independent acceptance verification — runs after execute completes, validates implementation against original REPORT's reproduction scenarios + PLAN's success criteria via actual environment (test runs, API calls, agent-browser UI, DB state).
- **Dual-mode**: execute가 Phase 7.5에서 자동 spawn / 사용자가 직접 호출
- **5 phases**: Context collection → Test scenario design → Test execution (pytest / API / UI / DB / build) → Write `[ISSUE_ID]_QA.md` → Verdict return
- **Bias 차단**: executor와 verifier 분리 ("the executor is never the verifier"). plan의 외부 게이트와 대칭 구조.
- **Output**: `[ISSUE_ID]_QA.md` with PASS/FAIL verdict + verbatim evidence
- **Integration**: Step between execute and record

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

Claude Code Marketplace로 배포. 9개 독립 플러그인 (wf, run-ralph, seq-think, terraform, atlassian, github, slack, arkraft-wiki, blogpost).
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
| v3.33.0 | **`blogpost` plugin 신규** (v1.0.0): multi-agent 블로그 작성 + CC 라이선스 이미지 큐레이션 + S3 sync. `/blogpost:create`는 6-agent 파이프라인(researcher → research-reviewer → image-curator → writer → writing-reviewer → html-renderer)으로 자료 조사·이미지 다운로드·초안·HTML 렌더까지 자동화하고 aws CLI로 폴더째 업로드. `/blogpost:update`는 round-trip 편집 (sync down → 사용자 편집 → 재렌더 → sync up). 버킷/프리픽스는 `~/.claude/blogpost.local.md` frontmatter (`bucket` + `prefix`)로 지정. html-renderer 에이전트가 figure/figcaption + callout + section semantics 부여 후 Jinja layout으로 wrap (markdown→HTML 1:1 변환 금지). 이미지 라이선스 hard rule: Unsplash > Pexels > Wikimedia Commons CC만, 출처 metadata.json 기록 필수. plugins 8 → **9**. |
| v3.32.0 | **`arkraft-wiki` plugin 신규** (v1.0.0): arkraft-wiki repo에 지식 문서 생성하는 wikify thin wrapper. plugin은 wiki content를 직접 작성하지 않고 wiki section 구조 / lifecycle / harness 검사 항목 / repo scan 목록을 references로 묶어 `Skill(run-ralph:choo-choo, ...)` 위임. wiki repo의 10 hooks + 6 skills는 source of truth (dual-source 방지). `wiki_root`는 `.claude/arkraft-wiki.local.md` settings frontmatter로 사용자별 지정. plugins 7 → 8. |
| v3.31.0 | run-ralph **record harness** 강화 + Phase 1.5 dispatch cache invalidation. (1) `.ralph/.record-pending` sentinel + `run-ralph-record-gate.sh` Stop hook 신설 — origin 대비 commits에 코드 변경 있는데 CHANGELOG.md / changelogs/v*.md 변경 0이면 Stop block. git diff 자체 검사로 doc-only / experiment-only 작업은 false-positive 0. (2) `run-ralph` plugin.json 1.1.0 → **1.2.0** bump으로 marketplace cache 강제 갱신 (v3.30에서 Phase 1.5 wf auto-dispatch가 SKILL.md에 들어갔으나 plugin version 동결로 사용자 cache가 옛 1.1.0 그대로 사용 중이던 문제 해소). (3) `choo-choo/SKILL.md` Phase 5 step 2에서 두 sentinel 동시 touch, Phase 6 4-step 흐름으로 확장 (record decision step 신설). |
| v3.30.0 | (1) run-ralph(choo-choo) 일반화: 코드 변경 외 ADR/설계/통합/문서 작업도 1급 task type으로. 매 run의 산출물을 `.ralph/<slug>/`로 격리. (2) **wf + arkraft wf2 통합**: Pack A 백본(git MCP / requirement-validator / record)에 Pack B 게이트(외부 wf-review-{analyze,plan,record} agents + wf-review-gate.sh PostToolUse hook + wf:qa skill) 흡수. plan/SKILL.md의 자기검토 루프(`Step A→D`, `REPEAT until zero issues`) 449줄 제거 → 외부 게이트 71줄로 교체. execute/SKILL.md Phase 7.5 신설: `Skill(wf:qa)` spawn으로 acceptance gate. choo-choo Phase 1.5 auto-dispatch: trivial → ralph 직행 / full → wf 5단계 → ralph. wf plugin.json (no version) → 3.30.0. |
| v3.29.0 | run-ralph 플러그인 신규 추가: Ralph Loop을 multi-agent team(Reviewer + QA) + 3-level AC + iteration 게이트로 안전 실행하는 choo-choo 스킬. 모든 sentinel/프롬프트 경로를 PROJECT_ROOT 절대경로로 anchor하여 Worker가 sub-dir로 cd해도 게이트가 깨지지 않음. Stop hook은 `${CLAUDE_PROJECT_DIR}` 기준으로 검사. |
| v3.27.0 | ask-yt 플러그인 신규 추가: YouTube 내장 AI(Ask/질문하기) CDP 자동화 |

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

### Workflow Summary

```
analyze → *_REPORT.md (external review gate → LGTM)
    ↓
plan    → *_PLAN.md   (external review gate → LGTM)
    ↓
execute → Code implementation + tests
    ↓
qa      → [ISSUE_ID]_QA.md (independent acceptance, PASS required)
    ↓
record  → README, ARCHITECTURE.md, CHANGELOG, CLAUDE docs update
```

---

## Notes

- **Current version**: v3.33.0
- **wf** (3.30.0): 5 skills (analyze / plan / execute / qa / record) + 4 agents (requirement-validator + wf-review-{analyze,plan,record}) + git MCP (12 도구) + PostToolUse hook (wf-review-gate.sh). plan은 외부 게이트 의존 (자기검토 루프 제거됨), execute Phase 7.5에서 wf:qa 자동 spawn.
- **run-ralph (1.2.0)**: choo-choo skill + ralph-reviewer/ralph-qa agents + **2 Stop hooks** (report-gate + record-gate). 의존: `ralph-loop@claude-plugins-official`. ADR/설계/통합/문서 작업 1급 지원, 매 run 산출물 `.ralph/<slug>/` 격리, Sentinel은 `.ralph/.report-pending` + `.ralph/.record-pending` 둘 다 top-level. record-gate는 origin 대비 commits에 코드 변경 + CHANGELOG 미수정이면 Stop block (git diff 자체 검사로 doc-only 작업 false-positive 0).
- **arkraft-wiki (1.0.0, v3.32)**: wikify thin wrapper. settings (`.claude/arkraft-wiki.local.md`)에서 wiki_root 읽고 wiki section 구조 / lifecycle / harness 검사 항목 / repo scan 목록을 references로 묶어 `Skill(run-ralph:choo-choo, args: ...)` 위임. plugin은 wiki content를 직접 작성 안 함 — wiki repo의 10 PreToolUse/Stop hooks가 source of truth.
- **blogpost (1.0.0, v3.33 신규)**: multi-agent 블로그 작성 + 이미지 큐레이션 + S3 sync. 6 agents (researcher / research-reviewer / image-curator / writer / writing-reviewer / html-renderer) + 2 commands (create / update) + render.py + Jinja2 layout + sync_s3.sh. 설정: `~/.claude/blogpost.local.md` frontmatter `bucket` + `prefix`. 의존: aws CLI / curl / python3+jinja2. 이미지 라이선스 hard rule (Unsplash/Pexels/Wikimedia CC만), html-renderer가 markdown 1:1 변환 금지하고 figure/callout semantics 부여. v1.0.0 update는 round-trip 수동 편집 fallback.
- **seq-think**: 별도 MCP 플러그인
- **terraform/atlassian/github/slack**: 독립 플러그인
- 외부 MCP (serena, context7, sentry)는 별도 플러그인으로 설치
- All skills and agents designed for Korean language output
- Reference files loaded on-demand to manage context efficiently
- Marketplace distribution requires GitHub public repository
- Version updates reflected when users run `/marketplace refresh`
