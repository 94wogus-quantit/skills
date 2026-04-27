# Ralph Loop Prompt Template

The composed prompt is what Ralph re-injects every iteration, so the structure must be self-contained: criteria, team workflow, and constraints all live inside the prompt.

> **Path discipline.** All `.ralph/*` paths in this template assume substitution with the absolute project root captured in Phase 5 (`PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"`). Never leave CWD-relative `.ralph/...` paths in the saved prompt — the Worker may `cd` mid-loop and Reviewer/QA spawns receive whatever path is in the prompt verbatim.

## Template structure

```
# Task: {task_title}

## Context
{왜 이 작업이 필요한지, 현재 상태는 어떤지}

## Objective
{구체적으로 무엇을 달성해야 하는지}

## Team Roster
- Worker: (이 Ralph Loop 세션 본체)
- Reviewer: ralph-reviewer (Level 2 판정)
- QA: ralph-qa (Level 1 + Level 3 판정)
{필요 시 커스텀 역할 추가:
- Cost-Auditor: ad-hoc agent — 새 AWS 리소스 비용 검토
- Reader-Persona: ad-hoc agent — "신규 백엔드 개발자" 페르소나로 문서 perception 평가}

## Acceptance Criteria

### Level 1: Concrete (always)
- [ ] {명령어 + 기대 결과}
- [ ] {명령어 + 기대 결과}

### Level 2: Structural (active when files_changed≥2 or new abstraction)
- [ ] {패턴/구조 기준}
- [ ] {패턴/구조 기준}
{또는} N/A — 단일 파일 수정, 새 추상화 없음

### Level 3: Holistic (active when human-read artifact involved)
- [ ] Persona: {구체 페르소나}
      Outcome: {그 사람이 할 수 있어야 하는 행동/사고}
      Verification: {QA가 어떻게 페르소나를 시뮬레이션하는지}
{또는} N/A — 사람이 직접 읽는 산출물 없음

## Constraints
- {지켜야 할 제약사항}
- {건드리면 안 되는 범위}

## Steps (per iteration)
1. {단계 1}
2. {단계 2}
3. {단계 3}

## Iteration Workflow (Mandatory)
각 iteration 끝에 다음을 순서대로 수행:

1. Worker가 `{PROMPT_PATH}` (절대경로)를 읽고 위 Steps를 진행, git diff에 변경 반영
2. Spawn Reviewer:
   `Agent(subagent_type: "ralph-reviewer", prompt: "iteration={N}, prompt_path='{PROMPT_PATH}', diff_command='git diff', previous_review_path='{PROJECT_ROOT}/.ralph/review-{N-1}.md'")`
   → 결과를 `{PROJECT_ROOT}/.ralph/review-{N}.md`로 저장. VERDICT 라인 확인.
3. Spawn QA:
   `Agent(subagent_type: "ralph-qa", prompt: "iteration={N}, prompt_path='{PROMPT_PATH}', level1_checks=<L1 명령어 목록>, level3_targets=<L3 페르소나/대상>, previous_qa_path='{PROJECT_ROOT}/.ralph/qa-{N-1}.md'")`
   → 결과를 `{PROJECT_ROOT}/.ralph/qa-{N}.md`로 저장. VERDICT 라인 확인.
4. 판정 게이트:
   - Reviewer == LGTM AND QA == PASS → 모든 Acceptance Criteria 충족 여부 확인
     - 모두 충족 → Phase 6 보고서 작성 → `rm "{PROJECT_ROOT}/.ralph/.report-pending"` → output `<promise>{COMPLETION_PROMISE}</promise>` (같은 메시지 내 순서 준수)
     - 일부 미충족 → 다음 iteration에서 미충족 항목 진행
   - 그 외 (REVISE / FAIL) → 사유 읽고 다음 iteration에서 수정. promise emit 금지.
5. 최신 review/qa 파일이 없거나 outdated면 promise emit 금지 (강제력).

## Completion
모든 Acceptance Criteria 충족 + 최신 Reviewer LGTM + 최신 QA PASS → Phase 6 보고서 → sentinel 제거 → output <promise>{COMPLETION_PROMISE}</promise>
```

> Phase 5의 `PROJECT_ROOT` 캡처 결과로 `{PROMPT_PATH}` / `{PROJECT_ROOT}` 두 placeholder 모두 절대경로로 치환 후 파일에 기록한다. 저장된 프롬프트에 literal `{PROJECT_ROOT}` 또는 `{PROMPT_PATH}`가 남아있으면 안 된다.

## Prompt quality checklist

A valid Ralph Loop prompt must satisfy ALL of:

### Specificity
- Task scope is bounded — exact files, modules, or functions named.
- No vague verbs ("improve", "clean up", "refactor") without operational definition.
- Inputs and outputs are explicit.

### Measurability
- Every L1 criterion is binary (pass/fail) and verifiable by a single command.
- Every L2 criterion names an observable pattern, not a feeling.
- Every L3 criterion names a persona AND an outcome AND a verification method.
- The completion promise maps 1:1 to all active criteria being met.

### Actionability
- Steps are ordered and dependency-aware.
- Each step is small enough to fit one iteration.
- No step requires human judgment or out-of-band input.

### Boundedness
- Constraints prevent scope creep.
- Files outside scope are explicitly excluded.
- Max iterations matches complexity:
  - Simple fix: 5–10
  - Feature addition: 10–20
  - Complex refactor: 20–40

### Team integrity
- Reviewer and QA are present in the Team Roster (mandatory).
- Iteration Workflow names the spawn calls explicitly.
- Promise emission is gated on the latest Reviewer + QA verdicts.
- Custom roles, if any, declare trigger / mandate / output explicitly.

### Path integrity (CWD-robust)
- All `.ralph/*` paths in the prompt are absolute (substituted from `PROJECT_ROOT`).
- Sentinel touch/rm commands use the absolute path.
- Pointer prompt to `/ralph-loop` references the absolute prompt-file path.

## Anti-patterns

### Too vague

```text
❌ "리팩토링해줘"
❌ "성능 개선해줘"
❌ "코드 정리해줘"
```

### Too broad

```text
❌ "전체 API를 TypeScript로 마이그레이션해줘"
❌ "모든 테스트 커버리지 90%로 올려줘"
```

### No success criteria

```text
❌ "auth 로직 수정해줘"   (무엇이 수정된 상태인지 정의 없음)
```

### Self-approving prompt (반드시 회피)

```text
❌ "Worker가 작업 완료되면 promise emit"
   → Worker 자기검증, Reviewer/QA 게이트 우회
✅ "Reviewer LGTM AND QA PASS이고 모든 Acceptance Criteria 충족 시 promise emit"
```

### Fake levels (조건부 강제 무시)

```text
❌ (단일 파일 1줄 수정에)
   ## L2: 컴포넌트 패턴 일관성
   ## L3: 사용자가 layout shift를 인지하지 못함
   → Reviewer/QA가 형식적 PASS — self-approval 부활
✅ ## L2: N/A — single-file edit
   ## L3: N/A — internal visual detail
```

### CWD-relative path (loop-breaking)

```text
❌ ".ralph/review-{N}.md"          (Worker가 sub-dir로 cd하면 다른 위치에 저장됨)
❌ "touch .ralph/.report-pending"  (sentinel이 잘못된 dir에 생기면 Stop hook 무력화)
✅ "/Users/.../project/.ralph/review-{N}.md"  (Phase 5에서 캡처한 절대경로)
```

## Clarification questions by task type

### Refactoring
- 어떤 구체적인 문제가 있는지? (중복 코드, 복잡도, 성능?)
- 어느 파일/모듈 범위인지?
- 리팩토링 후 기대하는 구조는?
- 기존 테스트가 있는지?

### Bug fix
- 재현 단계는?
- 예상 동작 vs 실제 동작?
- 관련 에러 로그나 스택 트레이스?
- 어느 환경에서 발생하는지?

### Feature addition
- 기능의 입력/출력은?
- 어느 레이어에 추가하는지? (domain/application/infrastructure/presentation)
- 기존 기능과의 의존성은?
- API 스펙이나 디자인이 있는지?

### Test writing
- 어떤 종류의 테스트? (unit, integration, e2e)
- 어떤 모듈/함수를 테스트하는지?
- edge case 포함 범위는?
- mocking 전략은?

### Documentation
- 대상 독자는? (페르소나 명시)
- 다 읽고 무엇을 할 수 있어야 하는가?
- 어디에 위치하는가? (`README.md`, `docs/`, wiki 등)
- 기존 문서와의 관계는? (대체, 보완, 중복 제거)
