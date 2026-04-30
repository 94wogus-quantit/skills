# Changelog

이 프로젝트의 모든 주요 변경사항은 이 파일에 문서화됩니다.

이 형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.0.0/)를 기반으로 하며,
이 프로젝트는 [Semantic Versioning](https://semver.org/lang/ko/)을 따릅니다.

---

## 버전 목록

각 버전의 상세 변경 이력은 `changelogs/` 폴더를 참조하세요.

### v3.x (Current)

| 버전 | 날짜 | 주요 변경 |
|------|------|----------|
| [v3.34.0](changelogs/v3.34.0.md) | 2026-04-30 | **run-ralph v1.3.0**: `claude-plugins-official/ralph-loop` 1.0.0 stop-hook 의 `<promise>` 미감지 한계(transcript control char + last-text-block 위치 문제) 우회용 PostToolUse force-stop hook 신설. Phase 6 의 `rm .ralph/.report-pending` 명령을 trigger 로 사용해 ralph-loop state 파일을 같은 turn 에 강제 제거 → 다음 Stop 이벤트에서 loop 깨끗하게 종료. SKILL.md Phase 4 에 promise position rule (absolute last text block) 명시 — 1차 방어선 + force-stop hook 1차 fallback 의 2중 안전망. plugin.json 1.2.0 → **1.3.0**, marketplace.json 3.33.0 → **3.34.0**. |
| [v3.33.0](changelogs/v3.33.0.md) | 2026-04-27 | **`blogpost` plugin 신규** (v1.0.0): multi-agent 블로그 작성 + CC 라이선스 이미지 큐레이션 + S3 sync. `/blogpost:create`는 6-agent 파이프라인(researcher → research-reviewer → image-curator → writer → writing-reviewer → html-renderer)으로 자료 조사·이미지 다운로드·초안·HTML 렌더까지 자동화하고 aws CLI로 폴더째 업로드. `/blogpost:update`는 round-trip 편집. 버킷/프리픽스는 `~/.claude/blogpost.local.md` frontmatter로 지정. plugins 8 → **9**. |
| [v3.32](changelogs/v3.32.md) | 2026-04-27 | **`arkraft-wiki` plugin 신규** (v1.0.0): wikify thin wrapper. wiki section 구조 / lifecycle / harness 검사 항목을 컨텍스트로 묶어 `run-ralph:choo-choo`에 위임. wiki repo의 10 hooks + 6 skills는 source of truth로 둠 (dual-source 방지). `wiki_root`는 `.claude/arkraft-wiki.local.md` settings로 사용자별 지정. |
| [v3.31](changelogs/v3.31.md) | 2026-04-27 | run-ralph **record harness** 강화: `.ralph/.record-pending` sentinel + `run-ralph-record-gate.sh` Stop hook으로 "코드 변경 후 CHANGELOG 누락" 차단 (git diff 자체 검사로 false-positive 차단). plugin.json 1.1.0 → **1.2.0** (cache invalidation으로 v3.30 Phase 1.5 dispatch 활성화) |
| [v3.30](changelogs/v3.30.md) | 2026-04-27 | (1) run-ralph(choo-choo) 일반화 + per-run `.ralph/<slug>/` 격리. (2) **wf + wf2 통합**: 외부 review agents + Stop hook 게이트로 self-approval 차단, qa skill 신설, choo-choo Phase 1.5 auto-dispatch (5 skills + 4 agents + git MCP + PostToolUse hook) |
| [v3.27](changelogs/v3.27.md) | 2026-02-19 | ask-yt 플러그인 신규 추가: YouTube 내장 AI(Ask/질문하기) CDP 자동화 |
| [v3.26](changelogs/v3.26.md) | 2026-02-13 | ralph-loop 통합 + auto-recovery: plan/execute 스킬 자동화 대폭 개선 |
| [v3.25](changelogs/v3.25.md) | 2026-02-12 | record 스킬 ARCHITECTURE.md 지원 추가 (matklad 패턴) |
| [v3.24](changelogs/v3.24.md) | 2026-02-04 | SKILL UX 개선: AskUserQuestion/Task 패턴, 도구 레퍼런스 추가 |
| [v3.23](changelogs/v3.23.md) | 2026-01-30 | Evidence Trail 기능: analyze/plan 스킬에 수집 context·사고 과정 추적 기능 추가 |
| [v3.22](changelogs/v3.22.md) | 2026-01-30 | plan 스킬 업그레이드: 5단계 알고리즘, Idiot Index, Zero-Context 원칙 통합 |
| [v3.21](changelogs/v3.21.md) | 2026-01-30 | 문서 구조 개선: CLAUDE.md 경량화, README.md 정리, 역할 분리 |
| [v3.20](changelogs/v3.20.md) | 2026-01-30 | plan_template에 Task Registration Guide 섹션 추가 |
| [v3.19](changelogs/v3.19.md) | 2026-01-30 | 스킬 전체 영어 지시문 점검 및 TaskTracking·Phase 정합성 개선 |
| [v3.18](changelogs/v3.18.md) | 2026-01-30 | analyze 스킬 강화: 일론 머스크 사고법 도입 |
| [v3.17](changelogs/v3.17.md) | 2026-01-29 | Plugin/MCP 이름 단축 (API 64자 제한 대응) |
| [v3.16](changelogs/v3.16.md) | 2026-01-19 | GitLab CI MCP 전환, CI 스킬 5개 삭제 |
| [v3.15](changelogs/v3.15.md) | 2026-01-19 | git-local MCP 확장, Skills user-invocable 추가 |
| [v3.14](changelogs/v3.14.md) | 2026-01-12 | GitHub MCP 플러그인 추가 |
| [v3.13](changelogs/v3.13.md) | 2026-01-05 | gitlab-mr CI/CD 스킬 추가 (ci-status, ci-retry, ci-trigger, ci-cancel) |
| [v3.12](changelogs/v3.12.md) | 2026-01-05 | gitlab-mr 플러그인 신규, sequential-thinking 분리 |
| [v3.11](changelogs/v3.11.md) | 2026-01-02 | 저장소 구조 개편 (plugins/, skills/ 폴더) |
| [v3.10](changelogs/v3.10.md) | 2026-01-02 | Atlassian 플러그인 추가 |
| [v3.9](changelogs/v3.9.md) | 2025-12-31 | Slack 플러그인 추가 |
| [v3.7](changelogs/v3.7.md) | 2025-12-19 | Plugins 모듈화 (3개 독립 플러그인) |
| [v3.6](changelogs/v3.6.md) | 2025-12-12 | mr-code-review 대규모 개선 |
| [v3.5](changelogs/v3.5.md) | 2025-12-11 | 브랜치 검증으로 단순화 |
| [v3.0-3.4](changelogs/v3.0-3.4.md) | 2025-12-10~11 | MCP 서버 통합, 도구 권한 관리 |

### v2.x

| 버전 | 날짜 | 주요 변경 |
|------|------|----------|
| [v2.x](changelogs/v2.md) | 2025-12-09~10 | Agents 시스템 도입, MCP 서버 확장 |

### v1.x

| 버전 | 날짜 | 주요 변경 |
|------|------|----------|
| [v1.x](changelogs/v1.md) | 2025-12-01~09 | 초기 릴리스, plan-builder 개선 |
