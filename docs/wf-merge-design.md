# wf + wf2 통합 설계 문서 (v3.30.0)

> **상태**: Iteration 1 산출물 — Reviewer/QA 게이트 통과 후 적용 단계로 진행.
> **Slug**: `wf-merge`
> **Promise**: `WF MERGED v3.30.0`
> **목표**: Pack A (현 wf 플러그인) + Pack B (arkraft의 wf2 스킬 팩) 강점 보존, 약점 제거. choo-choo가 task 복잡도를 자동 분류해 trivial은 ralph 직행 / 그 외는 new wf 풀 파이프라인.

---

## 1. 두 팩 비교 매트릭스

### 1.1 강점

| 항목 | Pack A (`plugins/wf/`) | Pack B (arkraft `wf2-*`) |
|---|---|---|
| First Principles methodology | ✅ Phase 3 sequential thinking loop | ✅ 동일 (둘 다 동일 방법론) |
| Evidence Trail enforcement | ✅ Mandatory Evidence Log 표 | ✅ 동일 포맷 |
| **Git MCP** | ✅ `git_local_server.py` 12 tools | ❌ 없음 |
| **`requirement-validator` agent** | ✅ AC 4-mode (reverse / pre / post / final) | ❌ 없음 |
| **`record` skill** | ✅ 1391-LOC, matklad ARCH 패턴, Serena 메모리, 멀티 문서 동기화 | ❌ 없음 |
| **외부 review agent** | ❌ Worker 자기검토 루프 (자기승인 위험) | ✅ `wf2-review-{analyze,plan,record}` 독립 spawn, LGTM/REVISE machine-parseable |
| **외부 review gate hook** | ❌ 없음 | ✅ `wf2-review-gate.sh` |
| **독립 QA 게이트** | ❌ execute의 test auto-recovery만 (acceptance 게이트 부재) | ✅ `wf2-qa-agent` 독립 acceptance 판정 |
| Phase 구조 일관성 | ✅ analyze→plan→execute→record 4단계 | ✅ 5단계 (qa 추가) |

### 1.2 약점

| 항목 | Pack A 약점 | Pack B 약점 |
|---|---|---|
| Self-approval | 🔴 plan/SKILL.md Phase 3 Step A-D "REPEAT until zero issues" — 같은 세션이 자기 plan 리뷰 → 인지 편향, 무한 iteration 위험 | ✅ 외부 agent로 해결됨 |
| QA 게이트 부재 | 🔴 acceptance 검증 없음 (test pass ≠ requirements met) | ✅ wf2-qa-agent로 해결됨 |
| 문서화 깊이 | ✅ record 1391 LOC | 🔴 record 등가 없음 |
| AC traceability | ✅ requirement-validator | 🔴 없음 |
| 브랜치 안전 | ✅ git MCP `check_branch_protection` | 🔴 없음 |
| dispatch 자동화 | 🔴 choo-choo와 연결 없음 | 🔴 동일 |

### 1.3 결론

**Pack B의 외부 게이트 패턴이 load-bearing.** 자기승인 방지가 구조적으로 보장됨. 다만 record / git MCP / requirement-validator는 없으므로 Pack A에서 그대로 가져와야 함.

→ **new wf = Pack A 백본 + Pack B 게이트.**

---

## 2. New wf 디렉토리 구조 (v3.30.0 목표)

```
plugins/wf/
├── .claude-plugin/plugin.json        # description 갱신: "5 skills + 4 agents + git MCP + Stop hook"
├── .mcp.json                          # 변경 없음 (git MCP)
├── git_local_server.py                # 변경 없음
├── README.md                          # 갱신 (qa skill / 외부 review 흐름 반영)
├── agents/
│   ├── requirement-validator.md       # 변경 없음 (Pack A 그대로)
│   ├── wf-review-analyze.md           # 신규 — wf2-review-analyze.md 베이스 + generic 치환
│   ├── wf-review-plan.md              # 신규 — wf2-review-plan.md 베이스 + generic 치환
│   └── wf-review-record.md            # 신규 — wf2-review-record.md 베이스 + generic 치환
├── hooks/
│   ├── hooks.json                     # 신규 — Stop matcher 등록 (PostToolUse 또는 Stop)
│   └── wf-review-gate.sh              # 신규 — wf2-review-gate.sh 베이스 + ${CLAUDE_PROJECT_DIR} anchor + plugins/wf/... 경로 조정
└── skills/
    ├── analyze/                       # Pack A 그대로 (검증만)
    ├── plan/                          # 패치 — Phase 3 자기검토 루프 제거 → 외부 게이트 의존
    ├── execute/                       # 패치 — Phase 7.5 신설 → `Skill(wf:qa)` 호출
    ├── qa/                            # 신규 — wf2-qa-agent 본문을 skill 포맷으로 재구성
    └── record/                        # Pack A 그대로
```

**Pack A에서 그대로 가져오는 것 (변경 0줄)**: `git_local_server.py`, `.mcp.json`, `agents/requirement-validator.md`, `skills/analyze/SKILL.md`, `skills/record/SKILL.md`.

**Pack B에서 가져오되 generic 치환**: `wf2-review-{analyze,plan,record}.md` → `wf-review-*.md` (arkraft / arkraft-api / arkraft-web 같은 repo-specific 텍스트는 generic으로).

**Pack B에서 가져와 변환**: `wf2-qa-agent.md`(agent) → `skills/qa/SKILL.md`(skill, user-invocable, frontmatter + Phase 구조).

**Pack A에 패치 적용**: `plan/SKILL.md` (자기검토 → 외부 게이트), `execute/SKILL.md` (Phase 7.5 추가).

---

## 3. 마이그레이션 Step List (iteration ↔ AC 매핑)

| Iteration | 작업 | 충족 가능 AC | 산출물 |
|---|---|---|---|
| 1 | 본 설계 문서 작성 | (게이트 검증) | `docs/wf-merge-design.md` |
| 2 | review agents 3종 + hook 셋업 | L1: agents/wf-review-* 존재, hook 존재/실행권한, hooks.json 유효, hook smoke-pass | 4 신규 파일 |
| 3 | review agents의 arkraft-specific 텍스트 generic 치환 검증 | L1: `rg "arkraft" plugins/wf/` → 0 hits; `rg "wf2-" plugins/wf/` → 0 hits | (수정) |
| 4 | qa skill 신규 (wf2-qa-agent → skill 변환) | L1: skills/qa/SKILL.md 존재; L2: frontmatter + Phase 구조 일관성 | `plugins/wf/skills/qa/SKILL.md` |
| 5 | qa skill Reader-Persona 통과 (5분 mental model) | L3 #1 일부 | (검증만) |
| 6 | plan/SKILL.md 자기검토 루프 제거 | L1: `rg "REPEAT until zero issues"` → 0 hits | `plugins/wf/skills/plan/SKILL.md` |
| 7 | plan/SKILL.md 외부 게이트 의존 패턴 명시 | L1: `rg "wf-review-plan|wf-review-gate"` ≥1; L2: 자기검토 잔재 없음 | (수정) |
| 8 | execute/SKILL.md Phase 7.5 신설 (`Skill(wf:qa)` 호출) | L1: `rg "wf:qa"` ≥1; L2: 위치 검증 (Phase 7과 8 사이) | `plugins/wf/skills/execute/SKILL.md` |
| 9 | choo-choo SKILL.md "Phase 1.5 Auto-dispatch" 섹션 추가 | L1: `rg "trivial|full-pipeline|dispatch"` ≥3 | `plugins/run-ralph/skills/choo-choo/SKILL.md` |
| 10 | choo-choo dispatch heuristic 응집성 + threshold 정당화 | L2: 단일 섹션, threshold inline-justified | (수정) |
| 11 | 메타데이터 동기화 (marketplace v3.29.0→3.30.0, plugin.json description, CLAUDE.md 트리/ADR/Notes, CHANGELOG, changelogs/v3.30.md) + 커밋 (`feat(wf): ...`) | L1: marketplace.json 버전 == 3.30.0; jq 유효성; 모든 메타 일관; `git log -1 --pretty=%B` 첫 줄 `feat(wf):` 프리픽스 | 5+ 파일 수정 + 커밋 |
| 12+ | Reader-Persona Round (`.md` 변경 누적 → CLEAR 게이트) | L3 #1, L3 #2 충족 | (검증) |
| N | 모든 AC 게이트 통과 → Phase 6 보고서 → sentinel 제거 → promise emit | 모든 AC 충족 | (없음) |

각 iteration은 **하나의 미충족 criterion 또는 하나의 REVISE 항목만** 해결한다 (큰 덩어리 변경 시 Reviewer가 의미있는 verdict 못 냄).

---

## 4. choo-choo Auto-dispatch 의사코드

`plugins/run-ralph/skills/choo-choo/SKILL.md`의 **Phase 1 종료 후 / Phase 2 진입 전** 단일 섹션 "Phase 1.5: Auto-dispatch classification"으로 응집.

### 4.1 분류 신호

```
# trivial threshold = 3: 5개 신호 중 과반(50% 초과) 충족 시 trivial 분류 — 명확한 다수결
# full 신호 가중치 ×2: 구조적 변경(schema/API/cross-file)은 단순 패턴 신호보다 정책 영향이 크므로 가중
# full threshold = 4: 가중치 +2 신호 2개만으로도 도달 — 단 하나의 강한 구조적 신호도 full 강제 가능
# diff < 50 lines: 단일 함수/변수 수정 수준 (한 화면 내 검토 가능) — 경험적 기준

trivial 신호 (각 +1; 누적 ≥ 3 → trivial):
  - 단일 파일 수정 의도 (사용자 발언에 1 file path만 있고 cross-file 언급 없음)
  - diff 예상 < 50 lines (e.g. typo, color value, 임계값 1개)
  - JIRA-ID 미언급 (PROJ-NNN 형태 없음)
  - 새 추상화 (class/function/file) 도입 안 함
  - 외부 인터페이스/스키마 영향 없음 (purely internal detail)

full-pipeline 신호 (각 +2; 누적 ≥ 4 → full):
  - cross-file refactor 또는 ≥3 file 변경 의도
  - JIRA-ID 명시
  - 사용자 발언에 "기능 추가 / feat / 새로 / refactor / migrate / 통합 / merge" 류 키워드
  - schema / API / migration / DB / 인프라 변경 신호
  - 새 파일 생성 또는 의존성 추가
  - 메타/설계/문서 작업 (ADR, integration design 등 — Pack B의 Design/Meta 카테고리)
```

### 4.2 결정 로직

```
trivial_score = sum(trivial_signals) where signals are detected from user input + initial repo grep
full_score   = sum(full_signals)

if trivial_score >= 3 AND full_score < 4:
    mode = "TRIVIAL"            # → ralph 직행 (현 6 phase 그대로, wf 호출 없음)
elif full_score >= 4:
    mode = "FULL"               # → wf:analyze → plan → execute → qa → record 순차 호출 후 ralph
else:
    # ambiguous (둘 다 약하거나 둘 다 강함)
    mode = ASK_USER             # AskUserQuestion 1회 over-ride
    # default-on-uncertainty = "FULL" (안전 쪽 — 시간 약간 더 들지만 품질 보장)
```

### 4.3 FULL 모드 흐름

```
Phase 1: Clarify (그대로)
Phase 1.5: Auto-dispatch → mode == "FULL"
Phase 1.6: wf 풀 파이프라인 실행:
   Skill(wf:analyze)   → *_REPORT.md (Reviewer/QA 게이트 by wf-review-gate.sh)
   Skill(wf:plan)      → *_PLAN.md   (외부 wf-review-plan agent 게이트)
   Skill(wf:execute)   → 코드 변경 + tests
   Skill(wf:qa)        → acceptance gate (PASS 필요)
   Skill(wf:record)    → 문서 동기화 (PR 안 함; 그건 사용자 결정)
Phase 2-5: ralph 표준 흐름 — wf 산출물(`*_PLAN.md`, AC 정의, 변경 파일 목록)을 컨텍스트로
           composition + acceptance criteria 재구성
           이미 wf가 검증한 항목은 Ralph의 L1/L2/L3에서 중복 제거 (예: wf:qa의 PASS 결과 그대로 인용)
```

### 4.4 TRIVIAL 모드 흐름

기존과 동일 — Phase 1 → 2 → 3 → 4 → 5 → 6. wf 호출 0건.

### 4.5 ambiguous → AskUserQuestion

```
"이 작업이 새 wf 풀 파이프라인을 거쳐야 할지 모호합니다.
어떻게 진행할까요?
  - FULL: wf 5단계 (analyze → plan → execute → qa → record) 후 ralph
  - TRIVIAL: ralph 직행
  - 자세히: 어떻게 분류했는지 보여줘"
```

---

## 5. 게이트 패턴 — 외부 review agent + Stop hook

### 5.1 wf-review-gate.sh의 책임

```
1. Stop event (또는 PostToolUse on Write)에 fire
2. ${CLAUDE_PROJECT_DIR} 기준 절대경로로:
   - .wf/.review-pending sentinel 검사
   - 또는 plugins/wf 안의 *_REPORT.md / *_PLAN.md 변경 검사
3. Worker가 review를 마치지 않았으면 Stop block + 외부 agent spawn 권유 메시지 inject
4. CWD-drift 무관 (run-ralph 훅과 동일 path discipline)
```

### 5.2 wf-review-* agents의 trigger 패턴

| Agent | Spawn trigger | 입력 | 출력 |
|---|---|---|---|
| `wf-review-analyze` | analyze 종료 시 (`*_REPORT.md` 생성됨) | REPORT.md 본문, 작업 컨텍스트 | LGTM / REVISE + 구체 피드백 |
| `wf-review-plan` | plan 종료 시 (`*_PLAN.md` 생성됨) | PLAN.md 본문, REPORT.md 참조 | LGTM / REVISE |
| `wf-review-record` | record 종료 시 (README/CHANGELOG/ARCHITECTURE 변경) | 변경된 docs 목록 | LGTM / REVISE |

기존 plan/SKILL.md의 Phase 3 Step A-D 자기검토 루프는 **삭제**, 대신 "PLAN.md 작성 후 wf-review-gate가 wf-review-plan agent를 spawn하고 LGTM verdict이 나올 때까지 PLAN을 수정한다"로 교체.

---

## 6. backward compatibility

| 항목 | 변경 전 | 변경 후 | 영향 |
|---|---|---|---|
| `wf:analyze`, `wf:plan`, `wf:execute`, `wf:record` skill 이름 | 존재 | 존재 (그대로) | 없음 |
| `wf:qa` skill | 없음 | 신규 | 추가 — 호출 안 하면 영향 없음 |
| `requirement-validator` agent | 존재 | 존재 (그대로) | 없음 |
| Git MCP 도구 (`get_current_branch` 등) | 12개 | 12개 (그대로) | 없음 |
| MCP 도구명 64자 제한 | `mcp__plugin_wf_git__*` | 동일 | 없음 |
| marketplace 버전 | 3.29.0 | **3.30.0** | minor bump |
| 외부 review hook | 없음 | 신규 (`wf-review-gate.sh`) | 사용자가 wf 플러그인 enable한 상태에서만 동작 — opt-in |

→ **breaking change 0개**. minor version bump (3.29.0 → 3.30.0)로 충분.

---

## 7. 위험 + mitigation

| 위험 | 가능성 | mitigation |
|---|---|---|
| 외부 review agent의 latency가 단순 작업에서 과도함 | 중 | choo-choo Phase 1.5 dispatch가 trivial을 정확히 분류 → wf 안 거침 |
| heuristic 오분류 (trivial을 full로 보거나 반대) | 중 | ambiguous → AskUserQuestion over-ride |
| arkraft 텍스트 잔재 (generic 치환 누락) | 중 | L1 검증: `rg "arkraft" plugins/wf/` → 0 hits |
| plan 자기검토 루프의 잔재 라인 | 중 | L1 검증: `rg "REPEAT until zero issues|Step A.*review.*Step D"` → 0 hits |
| `requirement-validator`가 외부 review agent와 책임 중복 | 낮 | 기능 분리 — requirement-validator는 AC↔코드 매핑, review agent는 patterns/structure 판정. 충돌 없음. SKILL.md에 명시. |
| Stop hook이 사용자 settings.json 수정 필요 | 낮 | 플러그인의 `hooks/hooks.json`에 등록 — `${CLAUDE_PLUGIN_ROOT}` 자동 로드 (run-ralph와 동일 패턴) |

---

## 8. 다음 iteration 진입 체크리스트

- [x] iteration 1 산출물: 본 문서 (`docs/wf-merge-design.md`)
- [ ] Reviewer (ralph-reviewer) 게이트 통과 — 본 설계의 self-consistency 판정
- [ ] QA (ralph-qa) 게이트 통과 — Level 1 (현 시점 binary check 수: 본 문서 존재) + Level 3 (perception)
- [ ] Reader-Persona 게이트 통과 — `wf 처음 쓰는 백엔드 개발자` 페르소나로 본 문서를 5분 내 이해 가능

게이트 통과 시 → iteration 2로 진입 (review agents + hook 셋업).
