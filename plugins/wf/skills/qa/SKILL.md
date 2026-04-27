---
name: qa
description: Independent acceptance verification skill. Run after execute completes to validate the implementation against the original REPORT's reproduction scenarios and the PLAN's success criteria — using actual environment verification (test runs, API calls, UI checks via agent-browser, DB state inspection), not just self-reported "tests pass". Generates [ISSUE_ID]_QA.md with PASS/FAIL verdict and evidence. Korean triggers: QA 검증, 품질 검증, qa 실행, 인수 검증, 시나리오 검증, qa 돌려, 검증해줘, 인수 테스트, 수용 검증.
user-invocable: true
---

# QA — Independent Acceptance Verification

## ⚠️ CRITICAL LANGUAGE POLICY

- **Skill instructions, Phase descriptions, workflow steps**: English (this file's prose)
- **User-facing output, QA documents, verdict messages, examples**: Korean (한국어)

QA writes verdict reports that humans read. The QA process itself runs with English instructions to keep the procedure mechanical and unambiguous.

## Why this skill exists

`execute` skill verifies its own work via auto-recovery test loops — but a Worker that wrote the code is structurally biased to declare it done. `qa` is an **independent acceptance gate** that re-runs the original REPORT's reproduction scenario and the PLAN's success criteria from scratch, using the actual deployed/built artifact, before `record` can document the work as complete.

This is the load-bearing pattern of the new wf v3.30: **executor and verifier must be different sessions**. Without that separation, `record` could publish a CHANGELOG entry for a "fix" that never actually fixed anything.

## When this skill runs

- **Inside the wf pipeline**: invoked by `execute` after Phase 7 (AC Achievement Report) and before Phase 8 (record handoff). `wf:qa` must return PASS for `execute` to hand off cleanly to `record`.
- **Standalone**: user invokes directly when they want to verify a branch's actual behavior matches a previously written REPORT/PLAN — no need to re-run analyze/plan.

## Inputs

When spawned (either by `execute` or standalone), the skill expects:

- `issue_id`: Issue tracker ID (e.g., `JIRA-1333`, `ISSUE-456`, or repo-specific pattern)
- `report_path`: Path to `[ISSUE_ID]_REPORT.md` produced by `analyze`
- `plan_path`: Path to `*_PLAN.md` produced by `plan`
- `branch`: Working branch name

If any of these are missing, the skill asks for them once via AskUserQuestion before proceeding.

## Phase 1: Context collection

1. **Read the REPORT** — extract root cause, reproduction scenario, and impact scope
2. **Read the PLAN** — extract success criteria and the planned testing strategy
3. **Inspect actual changes** — `git diff origin/main...HEAD` (or the project's base branch) to see what was actually committed on the branch
4. **Note discrepancies** — if PLAN says "modify file X" but git diff shows X unchanged, flag it. The verdict cannot be PASS if the branch doesn't even contain the planned changes.

## Phase 2: Test scenario design

Build the scenario list from REPORT + PLAN content (do not invent new criteria; QA's job is verification, not redesign):

1. **Bug-reproduction scenarios** — re-run the exact reproduction steps from the REPORT and confirm "the bug no longer occurs"
2. **Success-criteria scenarios** — for each success criterion in the PLAN, design a verification scenario
3. **Edge-case scenarios** — derived from the REPORT's impact-scope section
4. **Regression scenarios** — verify nearby existing functionality wasn't broken by the changes

Tag each scenario as `핵심` (critical — required for PASS) or `보조` (auxiliary — informational).

## Phase 3: Test execution

Pick the right verification method per scenario type. **Run the commands; do not paraphrase or assume**.

### 3A. Automated tests

```bash
# Repo-specific test runner
make test                # if Makefile present
pnpm test                # JS/TS monorepo
uv run pytest -v         # Python uv-managed
pytest tests/ -v         # plain Python
```

Capture verbatim stdout/stderr.

### 3B. API direct verification

```bash
curl -i -X GET http://localhost:8000/api/endpoint
http GET localhost:8000/api/endpoint   # if httpie available
```

Compare HTTP status code, response shape, headers — exactly what the PLAN's success criterion specifies.

### 3C. UI verification (`agent-browser`)

For UI-affecting changes:

```bash
# Connect to existing Chrome (preferred — reuses logged-in session, avoids bot detection)
agent-browser --auto-connect open http://localhost:3000/target-page
agent-browser --auto-connect snapshot -i
agent-browser --auto-connect screenshot qa-screenshot.png
```

**agent-browser usage rules**:
- Prefer `--auto-connect` over `--head` (reuses real Chrome session)
- For login-required flows, rely on the existing browser session
- Capture a screenshot at each verification step — screenshots are evidence, not optional

### 3D. Data / DB verification

```bash
# Local Docker postgres example
docker exec <container> psql -U <user> -d <db> -c "SELECT ..."
# Local Docker app container with embedded shell
docker exec <container> python -c "..."
```

Replace `<container>` with the project's actual container name (check `docker ps` first).

### 3E. Build / typecheck (often the cheapest L1 signal)

```bash
make validate            # if Makefile present
pnpm build               # JS/TS
mypy src/                # Python type check
```

## Phase 4: Write the QA document

Save to `[ISSUE_ID]_QA.md` (same convention as REPORT/PLAN — colocated with the analyze/plan artifacts).

```markdown
# QA Report — {ISSUE_ID}

## 검증 대상
- **Issue**: {ISSUE_ID}
- **브랜치**: {branch}
- **REPORT**: {report_path}
- **PLAN**: {plan_path}
- **검증 일시**: {timestamp}

## 코드 변경 요약
| 파일 | 변경 유형 | 설명 |
|------|----------|------|
| path/to/file.py | Modified | 한 줄 설명 |

## 테스트 시나리오 및 결과

### 시나리오 1: 버그 재현 검증 (핵심)
- **목적**: 보고된 버그가 더 이상 발생하지 않음을 확인
- **단계**:
  1. 구체 단계 (URL/입력값/클릭 대상 명시)
  2. 구체 단계
- **예상 결과**: 정상 동작 설명
- **실제 결과**: 관찰된 동작 (verbatim)
- **판정**: PASS / FAIL

### 시나리오 2: 성공 기준 검증 (핵심)
...

### 시나리오 3: 엣지케이스 (보조)
...

### 시나리오 4: 회귀 (보조)
...

## 검증 결과 요약
| # | 시나리오 | 유형 | 결과 | 비고 |
|---|---------|------|------|------|
| 1 | 버그 재현 | 핵심 | PASS/FAIL | |
| 2 | 성공 기준 A | 핵심 | PASS/FAIL | |
| 3 | 엣지케이스 | 보조 | PASS/FAIL | |
| 4 | 회귀 | 보조 | PASS/FAIL | |

## 자동 테스트 출력 (verbatim)
```
[pytest/jest 출력 그대로 붙여넣기]
```

## 스크린샷
- agent-browser 캡처: `qa-screenshot.png`

## 최종 판정

### PASS 조건
- 모든 **핵심** 시나리오가 PASS
- **보조** 시나리오 중 FAIL이 있어도 핵심 기능에 영향 없으면 PASS (이유 코멘트 첨부)

### FAIL 조건
- 하나 이상의 **핵심** 시나리오가 FAIL
- 또는 git diff에 PLAN과 다른 변경이 발견됨 (스코프 외 파일/누락 파일)

**VERDICT: PASS** 또는 **VERDICT: FAIL**

### FAIL 시 수정 요청 (FAIL일 때만)
- **실패 시나리오**: [번호]
- **원인 분석**: 왜 실패했는지
- **수정 제안**: 어떻게 고쳐야 하는지 — patch-level
→ Execute 단계로 복귀하여 수정 필요
```

## Phase 5: Verdict return

- **PASS** → 호출자(`execute` 또는 사용자)에게 PASS 반환. `record` 단계 진행 가능.
- **FAIL** → Execute로 복귀하고 수정 요청 사항(원인 + patch-level 제안)을 전달. record 진행 금지.

## QA Principles

1. **실제 환경 검증** — `pytest`만으로 끝내지 않고 실제 사용자 플로우 (UI/API/DB)를 확인
2. **재현 우선** — REPORT의 버그 재현 시나리오를 최우선으로 검증. 재현이 안 되면 그게 진짜 fix인지 의심
3. **증거 기반** — 모든 판정에 스크린샷/로그/verbatim output 첨부. 자기 인상 기반 PASS 금지
4. **보수적 판정** — 의심스러우면 FAIL. False PASS는 record를 잘못 트리거하고 PR이 나가게 한다
5. **구체적 피드백** — FAIL 시 "뭘 고쳐야 하는지" patch-level로 명확히. "테스트가 안 되네요" 수준이면 Execute가 처리 못함
6. **자기 검증 금지** — QA는 execute가 아닌 다른 세션이 돌리는 게 원칙. 같은 세션에서 돌려야 한다면 최소한 `git diff`만 보지 말고 실제 명령을 실행할 것
