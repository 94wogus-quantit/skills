# Planning Mental Model Guide

## Overview

This guide provides a structured thinking framework for plan creation, based on Elon Musk's 5-Step Algorithm adapted for software implementation planning. The core insight: most planning failures happen because people skip to optimization or automation before questioning whether the work should exist at all.

**Key Principle**: "The most common error of a smart engineer is to optimize a thing that should not exist."

The 5 steps MUST be followed **in strict order**. Each step builds on the previous one.

---

## 5-Step Algorithm for Planning

### Step 1: Question Every Requirement

Before writing any implementation task, trace each requirement back to a specific person. If nobody can be named, the requirement is suspect.

**Checklist**:
1. **Who** requested this requirement? (individual name, not department)
2. Is the requirement **still valid today**?
3. Is this a **cargo-culted convention** ("we always do it this way")?
4. Would the system work **without** this requirement?
5. Has the requirement been **directly confirmed** with its owner?

> ⚠️ Requirements from smart/senior people are the most dangerous — nobody questions them.

**Sequential Thinking Call Example**:

```typescript
mcp__plugin_seq-think_st__sequentialthinking({
  thought: "요구사항 질의: 1) '모든 API에 rate limiting 필요' - 누가 요청? PM 김XX → 확인 필요. 2) 'Redis 캐시 레이어 추가' - 요청자 없음, '항상 하는 것'이라 추가됨 → 삭제 후보. 3) '사용자 인증 JWT 사용' - CTO 이XX → 유효. 4) 'OpenAPI 문서 자동생성' - 요청자 불명 → 질의 필요.",
  thoughtNumber: 1,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

---

### Step 2: Delete the Part or Process

After listing all planned tasks/components, perform a **deletion pass**: remove every task that is not strictly necessary for the core deliverable.

**Rules**:
- Delete more than feels comfortable
- If you don't end up adding back at least 10% of what you deleted, you didn't delete enough
- Target: remove 20-30% of initial scope

**What to delete from plans**:
- Premature abstraction layers nobody requested
- "Future-proofing" interfaces for hypothetical requirements
- Admin panels that can use database queries
- Custom error handling frameworks when standard ones suffice
- Feature flags for one-time deployments
- Elaborate configuration systems for 2-3 config values

**Sequential Thinking Call Example**:

```typescript
mcp__plugin_seq-think_st__sequentialthinking({
  thought: "삭제 패스: 초기 태스크 8개 중 삭제 후보: 1) 'Redis 캐시 레이어' - 요청자 없음, 현재 트래픽에서 불필요 → 삭제. 2) 'Admin 대시보드' - DB 쿼리로 대체 가능 → 삭제. 3) 'Feature flag 시스템' - 일회성 배포, 불필요 → 삭제. 결과: 8개 → 5개 (37.5% 삭제). 10% 복원 규칙: 나중에 1개는 복원할 수 있음.",
  thoughtNumber: 2,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

---

### Step 3: Simplify and Optimize

Only after the deletion pass, simplify remaining tasks. Do NOT simplify before deleting — optimizing something that should not exist is waste.

**Simplification Checklist**:
- Can a complex state machine be replaced with a simple boolean?
- Can a custom service be replaced with a library call?
- Can multiple tasks be merged into one?
- Can deep nesting be flattened?
- Can an abstraction layer be removed?

**Sequential Thinking Call Example**:

```typescript
mcp__plugin_seq-think_st__sequentialthinking({
  thought: "단순화 패스: 남은 5개 태스크 검토: 1) '커스텀 인증 미들웨어 구현' → passport.js 라이브러리로 대체 가능 (3일 → 0.5일). 2) 'Task 3과 Task 4 (DB 스키마 설계 + 마이그레이션)' → 하나로 병합 가능. 3) '에러 핸들링 프레임워크' → Express 기본 에러 핸들러로 충분. 결과: 5개 → 4개, 복잡도 대폭 감소.",
  thoughtNumber: 3,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

---

### Step 4: Accelerate Cycle Time

After simplification, identify parallelizable work streams and shorten the critical path.

**Acceleration Checklist**:
- Which tasks can run in parallel?
- Are there artificial sequential dependencies?
- Can the feedback loop be shortened (small PRs, incremental deployment)?
- Can integration testing start earlier?

**Sequential Thinking Call Example**:

```typescript
mcp__plugin_seq-think_st__sequentialthinking({
  thought: "가속 분석: 병렬화 기회: Task 1 (API 구현)과 Task 2 (프론트엔드)는 인터페이스만 합의하면 병렬 가능. 인위적 순차 의존성: Task 3 → Task 4는 실제로는 독립적, 순차 제약 제거. 크리티컬 패스: Task 1 → Task 3 (2개). 피드백 루프: 각 태스크 완료 시 즉시 PR 생성, big-bang 통합 방지.",
  thoughtNumber: 4,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

---

### Step 5: Automate (Last)

Only now decide what to automate. Do NOT plan elaborate automation for processes that might not survive steps 1-4.

**Rules**:
- Manual-first for new or uncertain workflows
- Automate only after the process stabilizes
- One-time tasks don't need automation frameworks

**Sequential Thinking Call Example**:

```typescript
mcp__plugin_seq-think_st__sequentialthinking({
  thought: "자동화 결정: 1) CI/CD 파이프라인 - 이미 존재, 활용만 하면 됨 → 별도 태스크 불필요. 2) E2E 테스트 자동화 - 기능이 안정화된 후에 추가 → 현재 계획에 포함 안 함. 3) DB 마이그레이션 - 일회성이므로 스크립트만 작성, 프레임워크 불필요. 결론: 자동화 관련 별도 태스크 0개.",
  thoughtNumber: 5,
  totalThoughts: 5,
  nextThoughtNeeded: false
})
```

---

## Idiot Index for Plans

### Definition

**Idiot Index** = Total estimated effort of the plan / Effort for core functionality only

This metric, adapted from SpaceX's manufacturing cost analysis, measures how much overhead exists in a plan beyond the essential work.

### Calculation

```
Plan Idiot Index = (전체 계획 예상 노력) / (핵심 기능만의 노력)
```

**Per-task Idiot Index**:
```
Task Idiot Index = (태스크 예상 노력) / ("그냥 동작하게만" 하는 노력)
```

### Thresholds

| Idiot Index | Assessment | Action |
|-------------|-----------|--------|
| 1x - 2x | ✅ 효율적 | 유지 |
| 2x - 3x | ⚠️ 주의 | 불필요한 추상화 검토 |
| 3x - 5x | 🔴 비대 | 삭제 패스 재실행 필수 |
| 5x+ | ⛔ 과잉 설계 | 계획 근본 재설계 필요 |

### Example

```
핵심 기능: 로그인 API + DB 스키마 = 2일
전체 계획: 로그인 API + DB + Redis 캐시 + Admin 대시보드 + Feature Flag + 문서화 = 12일
Idiot Index = 12 / 2 = 6x → ⛔ 과잉 설계!

삭제 후: 로그인 API + DB + 문서화 = 3일
Idiot Index = 3 / 2 = 1.5x → ✅ 효율적
```

---

## Zero-Context Plan Writing

### Principle

Every task in the plan must be executable by someone with **zero prior knowledge** of the codebase. This principle is adapted from the [obra/superpowers](https://github.com/obra/superpowers) skill approach.

### Checklist

For each task, verify:
- [ ] **Exact file paths** specified (not "the auth module")
- [ ] **Specific code snippets** or function names referenced
- [ ] **Runnable test commands** provided (not "run the tests")
- [ ] **Expected outputs** described (not "it should work")
- [ ] **Dependencies** listed with install commands if needed

### Good vs Bad Examples

| Aspect | ❌ Bad (Vague) | ✅ Good (Zero-Context) |
|--------|---------------|----------------------|
| 위치 | "인증 모듈 수정" | "`src/auth/service.ts`의 `AuthService.login()` 메서드 수정" |
| 변경 | "에러 핸들링 추가" | "try-catch 블록으로 `TokenExpiredError` 캐치, 401 반환" |
| 테스트 | "테스트 실행" | "`npm test src/auth/service.test.ts -- --verbose`" |
| 결과 | "정상 동작 확인" | "로그인 성공 시 `{ token: string, expiresIn: 3600 }` 반환" |

---

## Anti-Patterns in Planning

### 1. Optimizing Before Deleting
- **Problem**: Spending time making a plan item detailed and well-structured before asking if it should exist
- **Fix**: Every plan review starts with a deletion pass, not a quality/detail pass

### 2. Unnamed Requirements
- **Problem**: Tasks justified by "best practice" or "convention" with no named stakeholder
- **Fix**: Every task traces to a named person. "The architecture team" is not a person.

### 3. Premature Automation
- **Problem**: Planning CI/CD pipelines, code generators, and testing frameworks before the process stabilizes
- **Fix**: Step 5 (Automate) comes last. Manual-first for new workflows.

### 4. Comfort-Zone Scope
- **Problem**: Deleting nothing because every item "might be needed"
- **Fix**: Apply the 10% restoration rule — if nothing was restored, deletion was too conservative.

### 5. Plan Template Bloat
- **Problem**: Filling every section of a template because it exists, even when not applicable
- **Fix**: Mark optional sections clearly. Not every plan needs Deployment or Communication sections.
