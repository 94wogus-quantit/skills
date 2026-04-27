# Example: Vague Request → Structured Ralph Loop Prompt

Each example shows the full transformation: clarify → team → criteria → composed prompt.

> Examples below use `<PROJECT_ROOT>` as a placeholder. In real Phase 5 invocation, substitute the captured absolute path (e.g. `/Users/dev/Project/myrepo`) before writing the file.

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
1. Worker: 위 Steps 진행
2. Spawn Reviewer:
   Agent(subagent_type: "ralph-reviewer", prompt: "iteration={N}, prompt_path='<PROJECT_ROOT>/.ralph/auth-jwt-merge-prompt.md', diff_command='git diff', previous_review_path='<PROJECT_ROOT>/.ralph/review-{N-1}.md'")
   → 출력을 <PROJECT_ROOT>/.ralph/review-{N}.md로 저장
3. Spawn QA:
   Agent(subagent_type: "ralph-qa", prompt: "iteration={N}, prompt_path='<PROJECT_ROOT>/.ralph/auth-jwt-merge-prompt.md', level1_checks=<L1 목록>, level3_targets='presentation/middleware/*, presentation/routes/protected/*', previous_qa_path='<PROJECT_ROOT>/.ralph/qa-{N-1}.md'")
   → 출력을 <PROJECT_ROOT>/.ralph/qa-{N}.md로 저장
4. Reviewer == LGTM AND QA == PASS AND 모든 Acceptance Criteria 충족
   → Phase 6 보고서 → `rm "<PROJECT_ROOT>/.ralph/.report-pending"` → emit promise (같은 메시지 내)
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
  - Output: <PROJECT_ROOT>/.ralph/cost-{iter}.md + VERDICT: APPROVED / JUSTIFY-NEEDED

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
1. Worker: 위 Steps 진행
2. Spawn Reviewer (ralph-reviewer) → <PROJECT_ROOT>/.ralph/review-{N}.md
3. Spawn QA (ralph-qa) → <PROJECT_ROOT>/.ralph/qa-{N}.md
4. Spawn Cost-Auditor (general-purpose, cost-auditor) → <PROJECT_ROOT>/.ralph/cost-{N}.md
5. Reviewer == LGTM AND QA == PASS AND Cost-Auditor == APPROVED AND 모든 Acceptance Criteria 충족
   → Phase 6 보고서 → `rm "<PROJECT_ROOT>/.ralph/.report-pending"` → emit promise
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
1. Worker: 위 Steps 진행
2. Spawn Reviewer → <PROJECT_ROOT>/.ralph/review-{N}.md (대부분 N/A 또는 LGTM 예상)
3. Spawn QA → <PROJECT_ROOT>/.ralph/qa-{N}.md (L1만 검증)
4. Reviewer == LGTM AND QA == PASS AND 모든 L1 충족
   → Phase 6 보고서 → `rm "<PROJECT_ROOT>/.ralph/.report-pending"` → emit promise

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
