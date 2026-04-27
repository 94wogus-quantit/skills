# Example: Vague Request → Structured Ralph Loop Prompt

Each example shows the full transformation: clarify → team → criteria → composed prompt.

> Examples below use `<PROJECT_ROOT>` as a placeholder. In real Phase 5 invocation, substitute the captured absolute path (e.g. `/Users/dev/Project/myrepo`) before writing the file.
>
> Per-run artifacts (prompt, review, qa, custom-role logs) all live under `<PROJECT_ROOT>/.ralph/<slug>/`. The session-level sentinel `<PROJECT_ROOT>/.ralph/.report-pending` is the one file that stays at the top level — see SKILL.md "Storage convention" for why.

## Example 1: Refactoring (full team, all 3 levels active)

### User input

```
auth 로직 리팩토링해줘
```

### Phase 1: Clarify

Questions:
1. "auth 로직에서 구체적으로 어떤 문제가 있나요? (중복 코드, 복잡도, 성능, 보안?)"
2. "어느 파일/모듈 범위인가요? (예: presentation/middleware, infrastructure/auth)"

User answers:
- "Cognito JWT 검증 로직이 middleware랑 route 양쪽에 중복돼있어. middleware로 통일하고 싶어"
- "presentation/ 하위만 건드려줘"

### Phase 2: Team Composition

Detected task type: **Refactoring**. No special triggers (no IAM/cost/persona).

Proposed team:
- Worker (main)
- Reviewer: `ralph-reviewer`
- QA: `ralph-qa`

User: approved.

### Phase 3: Acceptance Criteria

- L1: ALWAYS active
- L2: ACTIVE (multi-file, structural pattern unification)
- L3: ACTIVE (auth flow가 다른 개발자에게 읽히는 코드 — 가독성/명확성이 작업 목적의 일부)

### Phase 4: Composed prompt

```
# Task: Cognito JWT 검증 로직 통합

## Context
현재 Cognito JWT 검증이 presentation/middleware와 개별 route 핸들러 양쪽에 중복 구현되어 있다.
유지보수 시 양쪽 모두 수정해야 하는 문제가 있다.

## Objective
JWT 검증 로직을 presentation/middleware로 단일화하고, route 핸들러에서는 middleware가 주입한 인증 정보만 사용하도록 변경한다.

## Team Roster
- Worker: (이 Ralph Loop 세션 본체)
- Reviewer: ralph-reviewer
- QA: ralph-qa

## Acceptance Criteria

### Level 1: Concrete
- [ ] `rg "verify_jwt|decode_jwt" src/presentation/routes/` → 0 hits
- [ ] `rg "class AuthMiddleware" src/presentation/middleware/` → exactly 1
- [ ] `pytest tests/auth/ -v` → exit 0
- [ ] `pytest tests/integration/protected_routes/ -v` → exit 0

### Level 2: Structural
- [ ] 모든 protected route 핸들러가 `Depends(get_current_user)` 패턴으로 인증 정보 받음 (개별 검증 호출 0건)
- [ ] AuthMiddleware는 SRP 준수 — 토큰 검증만 수행, 권한 체크/유저 lookup은 별도 dependency
- [ ] Auth layer 구분(Public/Internal/Agent/Protected) 유지 — 미들웨어 분기 로직 보존
- [ ] 제거된 legacy 검증 함수가 import/호출/주석 어디에도 흔적 없음

### Level 3: Holistic
- [ ] Persona: 이 코드베이스를 처음 보는 백엔드 개발자
      Outcome: presentation/ 하위 파일 5분 읽기로 "auth는 middleware에서 단방향 처리, route는 결과만 사용"이라는 mental model 형성
      Verification: QA가 해당 페르소나로 middleware + 임의 route 1개 + auth dependency를 순서대로 읽고 self-report

## Constraints
- presentation/ 하위만 수정 (domain/, application/, infrastructure/ 변경 금지)
- API response format 변경 금지
- 기존 protected 엔드포인트 동작 변경 금지 (검증 위치만 이동)

## Steps (per iteration)
1. 현재 JWT 검증이 존재하는 모든 위치 파악 (rg 사용)
2. middleware의 JWT 검증을 canonical 구현으로 확정 (필요 시 보강)
3. route 핸들러 한 군데에서 중복 검증 제거 + Depends 패턴으로 전환
4. 해당 route의 테스트 실행
5. Reviewer/QA 호출 (Iteration Workflow 참조)

## Iteration Workflow (Mandatory)
> Run directory: `<PROJECT_ROOT>/.ralph/auth-jwt-merge/`

1. Worker: 위 Steps 진행
2. Spawn Reviewer:
   Agent(subagent_type: "ralph-reviewer", prompt: "iteration={N}, prompt_path='<PROJECT_ROOT>/.ralph/auth-jwt-merge/prompt.md', output_path='<PROJECT_ROOT>/.ralph/auth-jwt-merge/review-{N}.md', diff_command='git diff', previous_review_path='<PROJECT_ROOT>/.ralph/auth-jwt-merge/review-{N-1}.md'")
   → 출력을 <PROJECT_ROOT>/.ralph/auth-jwt-merge/review-{N}.md로 저장
3. Spawn QA:
   Agent(subagent_type: "ralph-qa", prompt: "iteration={N}, prompt_path='<PROJECT_ROOT>/.ralph/auth-jwt-merge/prompt.md', output_path='<PROJECT_ROOT>/.ralph/auth-jwt-merge/qa-{N}.md', level1_checks=<L1 목록>, level3_targets='presentation/middleware/*, presentation/routes/protected/*', previous_qa_path='<PROJECT_ROOT>/.ralph/auth-jwt-merge/qa-{N-1}.md'")
   → 출력을 <PROJECT_ROOT>/.ralph/auth-jwt-merge/qa-{N}.md로 저장
4. Reviewer == LGTM AND QA == PASS AND 모든 Acceptance Criteria 충족
   → Phase 6 보고서 → `rm "<PROJECT_ROOT>/.ralph/.report-pending"` (sentinel은 top-level) → emit promise (같은 메시지 내)
   그 외 → 다음 iteration에서 수정. promise emit 금지.

## Completion
All criteria met + Reviewer LGTM + QA PASS → Phase 6 보고서 → sentinel 제거 → output <promise>AUTH REFACTOR COMPLETE</promise>
```

### Phase 5: Execute

```
⚙️ Options:
- max-iterations: 15
- completion-promise: "AUTH REFACTOR COMPLETE"
```

---

## Example 2: Infra (custom role added — Cost-Auditor)

### User input

```
alpha-pool에 새 Redis 인스턴스 추가해줘
```

### Phase 1: Clarify

Questions:
1. "어떤 용도의 Redis인가요? (캐시, 세션, 큐?) 기존 Redis와 별도로 필요한 이유가 있나요?"
2. "인스턴스 스펙은? (node type, 클러스터 모드 여부)"

User answers:
- "agent 작업 큐용. 기존 캐시 Redis와 분리해야 함"
- "cache.t3.micro, 단일 노드"

### Phase 2: Team Composition

Detected task type: **Infra**. Trigger: cost-sensitive resource (ElastiCache) → Cost-Auditor 추가.

Proposed team:
- Worker (main)
- Reviewer: `ralph-reviewer`
- QA: `ralph-qa`
- Cost-Auditor: ad-hoc (mandate: 월 비용 산출 + $50 초과 시 정당화)

User: approved.

### Phase 3: Acceptance Criteria

- L1: ALWAYS active
- L2: ACTIVE (새 리소스 정의 — 모듈 재사용 패턴 적용 여부 등)
- L3: SKIP — pure infra change, no human-read artifact

### Phase 4: Composed prompt

```
# Task: Alpha Pool에 Agent 큐용 Redis 인스턴스 추가

## Context
alpha-pool-infra에 agent 작업 큐 전용 Redis가 필요하다.
기존 캐시용 Redis와 용도가 달라 별도 인스턴스로 분리한다.

## Objective
ElastiCache Redis 인스턴스를 Terraform으로 정의한다.

## Team Roster
- Worker: (이 Ralph Loop 세션 본체)
- Reviewer: ralph-reviewer
- QA: ralph-qa
- Cost-Auditor: ad-hoc agent
  - Spawning: Agent(subagent_type: "general-purpose", name: "cost-auditor")
  - Mandate: 추가/변경된 AWS 리소스의 월 예상 비용 산출. $50/월 초과 리소스는 명시적 정당화 요구.
  - Output: <PROJECT_ROOT>/.ralph/alpha-pool-redis/cost-{iter}.md + VERDICT: APPROVED / JUSTIFY-NEEDED

## Acceptance Criteria

### Level 1: Concrete
- [ ] `make fmt` exit 0, no diff
- [ ] `make validate` exit 0
- [ ] `terraform plan` 출력에 정확히 1개의 `aws_elasticache_cluster` resource 추가, 0개 modify, 0개 destroy
- [ ] 신규 리소스 이름이 `alpha-pool-agent-queue` 패턴
- [ ] output `agent_queue_redis_endpoint` 정의됨

### Level 2: Structural
- [ ] 기존 VPC/subnet/security group module 재사용 (신규 정의 0건)
- [ ] 기존 캐시 Redis 리소스 정의는 unchanged (diff 0줄)
- [ ] tag 컨벤션 일치 (Environment, Service, ManagedBy 등 기존 패턴)

### Level 3: N/A — pure infra, no human-read artifact

## Constraints
- 기존 캐시 Redis 리소스 수정 금지
- `terraform apply` 직접 실행 금지 (Atlantis가 PR 기반으로 처리)
- state 파일 직접 수정 금지
- region: ap-northeast-2

## Steps (per iteration)
1. 기존 Redis 리소스 구조 파악 (모듈, naming, tag)
2. 새 Redis 리소스 정의 (naming: alpha-pool-agent-queue)
3. security group rule 추가 (필요 시)
4. output 추가
5. `make fmt && make validate` 실행
6. Reviewer/QA/Cost-Auditor 호출

## Iteration Workflow (Mandatory)
> Run directory: `<PROJECT_ROOT>/.ralph/alpha-pool-redis/`

1. Worker: 위 Steps 진행
2. Spawn Reviewer (ralph-reviewer) → <PROJECT_ROOT>/.ralph/alpha-pool-redis/review-{N}.md
3. Spawn QA (ralph-qa) → <PROJECT_ROOT>/.ralph/alpha-pool-redis/qa-{N}.md
4. Spawn Cost-Auditor (general-purpose, cost-auditor) → <PROJECT_ROOT>/.ralph/alpha-pool-redis/cost-{N}.md
5. Reviewer == LGTM AND QA == PASS AND Cost-Auditor == APPROVED AND 모든 Acceptance Criteria 충족
   → Phase 6 보고서 → `rm "<PROJECT_ROOT>/.ralph/.report-pending"` (sentinel은 top-level) → emit promise
   그 외 → 다음 iteration에서 수정

## Completion
All criteria met + LGTM + PASS + APPROVED → Phase 6 보고서 → sentinel 제거 → output <promise>REDIS ADDED</promise>
```

### Phase 5: Execute

```
⚙️ Options:
- max-iterations: 10
- completion-promise: "REDIS ADDED"
```

---

## Example 3: Trivial fix (no clarification, L2/L3 SKIP)

### User input

```
web의 domains/alpha/components/TopicCard.tsx에서
loading skeleton이 실제 카드 사이즈와 안 맞아.
카드 높이 148px인데 skeleton은 120px임. 맞춰줘.
```

### Phase 1: Clarify → SKIP (already specific)

### Phase 2: Team Composition

Detected: trivial single-file fix. Default team still mandatory (Worker + Reviewer + QA), no custom roles.

### Phase 3: Acceptance Criteria

- L1: ALWAYS active
- L2: SKIP — single file, no new abstraction
- L3: SKIP — internal visual detail, no human-read artifact

### Phase 4: Composed prompt

```
# Task: TopicCard loading skeleton 높이 수정

## Context
TopicCard의 loading skeleton 높이(120px)가 실제 카드 높이(148px)와 불일치하여 layout shift가 발생한다.

## Objective
skeleton 높이를 실제 카드와 동일하게 148px로 맞춘다.

## Team Roster
- Worker: (이 Ralph Loop 세션 본체)
- Reviewer: ralph-reviewer (변경 거의 없을 것 — N/A 판정 예상)
- QA: ralph-qa (L1만 활성)

## Acceptance Criteria

### Level 1: Concrete
- [ ] `rg "h-\[120px\]|height:\s*120" web/domains/alpha/components/TopicCard.tsx` → 0 hits
- [ ] `rg "h-\[148px\]|height:\s*148" web/domains/alpha/components/TopicCard.tsx` → ≥1 hit (skeleton 영역)
- [ ] `pnpm --filter web build` exit 0

### Level 2: N/A — single-file edit, no new abstraction

### Level 3: N/A — internal visual detail

## Constraints
- TopicCard.tsx만 수정
- 다른 컴포넌트의 skeleton에 영향 없음

## Steps (per iteration)
1. TopicCard.tsx에서 skeleton 관련 코드 확인
2. 높이값 148px로 수정
3. pnpm build 확인
4. Reviewer/QA 호출

## Iteration Workflow (Mandatory)
> Run directory: `<PROJECT_ROOT>/.ralph/topic-card-skeleton/`

1. Worker: 위 Steps 진행
2. Spawn Reviewer → <PROJECT_ROOT>/.ralph/topic-card-skeleton/review-{N}.md (대부분 N/A 또는 LGTM 예상)
3. Spawn QA → <PROJECT_ROOT>/.ralph/topic-card-skeleton/qa-{N}.md (L1만 검증)
4. Reviewer == LGTM AND QA == PASS AND 모든 L1 충족
   → Phase 6 보고서 → `rm "<PROJECT_ROOT>/.ralph/.report-pending"` (sentinel은 top-level) → emit promise

## Completion
All L1 criteria met + Reviewer LGTM + QA PASS → Phase 6 보고서 → sentinel 제거 → output <promise>SKELETON FIXED</promise>
```

### Phase 5: Execute

```
⚙️ Options:
- max-iterations: 5
- completion-promise: "SKELETON FIXED"
```

> 참고: 이 trivial 케이스에서도 Reviewer/QA는 생략하지 않는다. Worker가 "다 됐다"고 자기 판정하는 시나리오를 막기 위함.

---

## Example 4: Design / Integration ADR (메타 작업 — 코드 변경 0건)

이 예시의 목적은 **choo-choo가 "코드 변경 작업" 전용이 아니라는 점**을 보여주기 위함. 결과물은 ADR 한 개 — 코드는 한 줄도 안 바뀜. 그래도 동일한 6 phase / 3-level AC / Reviewer + QA 게이트가 그대로 적용된다.

### User input

```
서로 비슷한 두 워크플로우 스킬(skill-A, skill-B)을 어떻게 합칠지 ADR로 정리해줘.
결과는 새로운 통합 스킬을 만들고 두 스킬은 deprecate 하는 방향으로 가고 싶은데,
근거랑 마이그레이션 경로까지 같이 적어줘.
```

### Phase 1: Clarify

Questions:
1. "결과 ADR을 어디에 둘까요? (`docs/adr/NNNN-skill-merge.md` 같은 형식으로 새 파일?)"
2. "두 스킬 각각의 기존 사용자(호출 트리거 표현, 외부에서 의존하는 인터페이스)를 보존해야 하나요, 아니면 통합 스킬 기준으로 새 트리거 셋만 정의하면 되나요?"
3. "이번 iteration은 ADR까지만인가요, 통합 스킬 구현까지인가요?"

User answers:
- "`docs/adr/0042-skill-A-B-merge.md`로 새로 만들어"
- "기존 트리거 표현은 통합 스킬에서도 다 인식되게 보존해야 함. 사용자가 옛날 표현 그대로 써도 동작해야 함."
- "이번엔 ADR까지만. 구현은 다음 choo-choo run에서."

### Phase 2: Team Composition

Detected task type: **Design / Meta** (ADR 작성, 코드 변경 없음, 통합 대상 = 기존 스킬 2개).

Trigger: 통합 대상이 되는 기존 시스템의 계약(트리거 표현, 인터페이스)을 보존해야 함 → **Domain-Expert** 추가.
Trigger: ADR의 명시된 독자(미래 메인테이너) 있음 → **Reader-Persona** 추가.

Proposed team:
- Worker (main)
- Reviewer: `ralph-reviewer`
- QA: `ralph-qa`
- Domain-Expert: ad-hoc (mandate: skill-A, skill-B 각각의 기존 트리거/인터페이스 invariant이 새 설계에 보존됐는지 검증)
- Reader-Persona: ad-hoc (페르소나: 6개월 후 합류한 메인테이너)

User: approved.

### Phase 3: Acceptance Criteria

- L1: ALWAYS active (ADR 파일 존재, 필수 섹션 존재, TODO 0건 등 — design_artifact 케이스에서 L1은 "문서 자체의 기계 검증")
- L2: ACTIVE (design_artifact → SKIP 룰 우회. 결정 항목과 제약의 1:1 추적 등 구조적 검증)
- L3: ACTIVE (ADR은 사람이 읽는 산출물 — Reader-Persona가 핵심)

### Phase 4: Composed prompt

```
# Task: skill-A와 skill-B 통합 ADR 작성

## Context
워크플로우 스킬 skill-A와 skill-B가 트리거 표현·내부 동작이 거의 동일해 사용자가 어느 쪽을
호출해야 할지 매번 헷갈린다. 통합이 필요하지만 두 스킬 각각의 기존 사용자가 있어,
"그냥 합친다"가 아니라 "왜 / 어떻게 / 무엇을 보존하고 무엇을 버리는가"를 결정 문서로 남겨야 한다.

이번 iteration의 산출물은 ADR 한 개. 코드 변경 없음. 통합 스킬 구현은 별도 후속 작업.

## Objective
`docs/adr/0042-skill-A-B-merge.md`를 작성한다. ADR은 다음을 담아야 한다:
- 두 스킬 각각의 현재 계약(트리거 표현, 인터페이스, 사용 시나리오) 정리
- 통합이 필요한 이유 (Context)
- 결정 (Decision): 새 통합 스킬을 만들고 두 스킬은 deprecate
- 검토했지만 기각된 대안 (Alternatives Considered) — 최소 2개
- 결과/영향 (Consequences) — 보존되는 것, 깨지는 것, 마이그레이션 경로

## Team Roster
- Worker: (이 Ralph Loop 세션 본체)
- Reviewer: ralph-reviewer
- QA: ralph-qa
- Domain-Expert: ad-hoc agent
  - Spawning: Agent(subagent_type: "general-purpose", name: "domain-expert")
  - Mandate: skill-A, skill-B 각각의 기존 트리거 표현·인터페이스를 모두 추출해 새 ADR의 결정/마이그레이션 경로에서 명시적으로 다뤄지는지 1:1 추적. 누락 = REVISE.
  - Output: <PROJECT_ROOT>/.ralph/skill-A-B-merge-adr/domain-{iter}.md + VERDICT: PRESERVED / GAPS-FOUND
- Reader-Persona: ad-hoc agent
  - Spawning: Agent(subagent_type: "general-purpose", name: "reader-persona")
  - Mandate: 페르소나 "6개월 후 합류한 신규 메인테이너 (skill-A/B 무경험)"로 ADR 처음부터 끝까지 읽고:
    - 5분 내에 통합 결정 이유를 자연어로 설명 가능한가?
    - 기각된 대안 각각이 왜 기각됐는지 떠올릴 수 있는가?
    - 이 결정을 뒤집으려면 어떤 제약이 무너져야 하는지 알 수 있는가?
  - Output: 페르소나 노트 + VERDICT: CLEAR / UNCLEAR

## Acceptance Criteria

### Level 1: Concrete
- [ ] `test -f docs/adr/0042-skill-A-B-merge.md`
- [ ] `rg "^## (Context|Decision|Alternatives Considered|Consequences)$" docs/adr/0042-skill-A-B-merge.md | wc -l` → 정확히 4
- [ ] `rg "TODO|TBD|FIXME|\?\?\?" docs/adr/0042-skill-A-B-merge.md` → 0 hits
- [ ] `rg "^### Alternative" docs/adr/0042-skill-A-B-merge.md | wc -l` → ≥ 2 (대안 최소 2개)
- [ ] ADR 안에서 참조하는 모든 기존 파일/스킬 경로가 실재 (cross-ref 깨짐 0건)

### Level 2: Structural
- [ ] "Decision" 섹션의 각 결정 항목이 "Context" 섹션의 제약/문제와 1:1 추적 가능 (orphan decision 0건)
- [ ] "Alternatives Considered"의 각 대안마다 reject 사유가 1줄 이상 명시
- [ ] skill-A의 기존 트리거 표현 N개, skill-B의 기존 트리거 표현 M개가 모두 "Consequences > Migration Path"에서 다뤄짐 (보존/리매핑/명시적 drop 중 하나로 분류)
- [ ] 용어 일관성: "skill" / "command" / "workflow" 혼용 없음 (한 가지로 통일)
- [ ] ADR 형식이 기존 `docs/adr/` 하위 다른 ADR과 동일한 헤더 위계·메타데이터 블록 사용

### Level 3: Holistic
- [ ] Persona: 6개월 후 합류한 신규 메인테이너 (skill-A/B 무경험)
      Outcome: ADR 5분 읽기 후 "왜 두 스킬을 합쳤는지", "기각된 대안이 왜 기각됐는지", "이 결정을 뒤집으려면 무엇이 바뀌어야 하는지" 세 질문에 자연어 답변 가능
      Verification: Reader-Persona agent가 해당 페르소나로 ADR을 읽고 세 질문에 self-report

## Constraints
- 코드 변경 금지. 산출물은 ADR 1개 파일뿐.
- 기존 ADR 파일 수정 금지 (새 파일만 추가).
- "통합 스킬을 어떻게 구현할지"의 코드 레벨 디테일은 이번 ADR 범위 밖 — "Migration Path" 섹션에서 후속 작업으로 명시만.
- skill-A, skill-B의 기존 트리거 표현은 보존 결정이 default (사용자 호환성 깨짐 금지)

## Steps (per iteration)
1. skill-A, skill-B의 현재 트리거 표현·인터페이스를 모두 추출 (rg + 파일 읽기)
2. ADR 초안의 부족한 섹션을 한 단계 진전 (한 iteration당 1~2개 섹션)
3. 작성한 섹션을 자체 검토하고 cross-ref / 용어 일관성 1차 점검
4. Reviewer / QA / Domain-Expert / Reader-Persona 호출

## Iteration Workflow (Mandatory)
> Run directory: `<PROJECT_ROOT>/.ralph/skill-A-B-merge-adr/`

1. Worker: 위 Steps 진행. "diff"는 ADR 파일의 변경.
2. Spawn Reviewer (ralph-reviewer) → <PROJECT_ROOT>/.ralph/skill-A-B-merge-adr/review-{N}.md
3. Spawn QA (ralph-qa) → <PROJECT_ROOT>/.ralph/skill-A-B-merge-adr/qa-{N}.md
4. Spawn Domain-Expert → <PROJECT_ROOT>/.ralph/skill-A-B-merge-adr/domain-{N}.md
5. Spawn Reader-Persona → <PROJECT_ROOT>/.ralph/skill-A-B-merge-adr/reader-{N}.md
6. Reviewer == LGTM AND QA == PASS AND Domain-Expert == PRESERVED AND Reader-Persona == CLEAR AND 모든 Acceptance Criteria 충족
   → Phase 6 보고서 → `rm "<PROJECT_ROOT>/.ralph/.report-pending"` (sentinel은 top-level) → emit promise
   그 외 → 다음 iteration에서 수정

## Completion
All criteria met + LGTM + PASS + PRESERVED + CLEAR → Phase 6 보고서 → sentinel 제거 → output <promise>SKILL MERGE ADR DRAFTED</promise>
```

### Phase 5: Execute

```
⚙️ Options:
- max-iterations: 12
- completion-promise: "SKILL MERGE ADR DRAFTED"
```

> 핵심 포인트: 코드 변경이 0건인데도 Reviewer/QA + 커스텀 역할 2개 + 3-level AC가 모두 의미 있게 작동한다. choo-choo의 게이트 메커니즘은 "변경되는 산출물이 코드인가 문서인가"와 무관하다 — "Worker 자기 판정 방지 + 단계적 검증"이라는 본질이 동일하게 유효하기 때문.
