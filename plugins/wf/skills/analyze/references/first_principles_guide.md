# First Principles Decomposition Guide

## Overview

First Principles Decomposition identifies assumptions taken for granted during bug analysis and traces root causes using only verified facts.

## Process

### Step 0: Question Requirements

Before starting analysis, verify the **requirements themselves** of the feature where the bug occurs.

**Checklist**:
1. **Who** created the requirements for this feature? (individual, not department)
2. Are those requirements **still valid today**?
3. If this feature **did not exist**, would the bug also not exist?
4. Are there any requirements where "we've always done it this way" is the only justification?
5. Have you **directly confirmed** with the person who created the requirement?

> Requirements themselves can be the cause of bugs.
> "Working as specified, but the specification is wrong" is the most expensive bug.

**Sequential Thinking Call Example**:

```typescript
mcp__plugin_seq-think_st__sequentialthinking({
  thought: "이 버그가 발생하는 기능의 요구사항 검증: 1) 요구사항 출처: [JIRA-XXX, 담당자 이름] 2) 현재 유효성: [유효/의문점] 3) 기능 삭제 시 버그 소멸 여부: [예/아니오] 4) '항상 이렇게 해왔다' 근거 여부: [확인 필요]",
  thoughtNumber: 1,
  totalThoughts: 4,
  nextThoughtNeeded: true
})
```

---

### Step 1: Assumption Identification

List everything "taken for granted" about the issue and classify into "verified facts" and "unverified assumptions".

**Classification Criteria**:

| Category | Definition | Example |
|----------|-----------|---------|
| **Verified Fact** | Directly confirmable from logs, metrics, or code | "로그에 Timeout 3회 기록됨" |
| **Unverified Assumption** | Judgment based on inference or experience | "DB 부하가 원인일 것" |

**Sequential Thinking Call Example**:

```typescript
mcp__plugin_seq-think_st__sequentialthinking({
  thought: "이 이슈에 대해 당연하다고 믿는 것 나열: 1) API는 항상 200을 반환해야 함 2) DB 연결은 안정적 3) 입력값은 프론트에서 검증됨. 분류: [검증된 사실] 로그에 500 에러 3회 기록 - 직접 확인됨. [미검증 가정] 'DB 부하 때문일 것' - 추정일 뿐 확인 안 됨.",
  thoughtNumber: 1,
  totalThoughts: 3,
  nextThoughtNeeded: true
})
```

### Step 2: Decomposition into Fundamental Principles

Decompose the operating principles of the system where the bug occurs into basic components.

**Decomposition Process**:
1. Identify the Input → Processing → Output flow
2. List the normal operating conditions for each component
3. List "what must be true for this system to function correctly"
4. Find which of those are "not true" → root cause candidates

**Sequential Thinking Call Example**:

```typescript
mcp__plugin_seq-think_st__sequentialthinking({
  thought: "시스템 분해: 요청 수신(Controller) → 인증 확인(AuthMiddleware) → 비즈니스 로직(Service) → DB 조회(Repository) → 응답 반환. 정상 동작 조건: 1) Controller가 요청을 파싱 가능 2) 인증 토큰이 유효 3) Service 로직이 예외 없이 완료 4) DB 연결 활성 5) 응답 직렬화 성공. 위반 가능성: 조건 4 - 로그에서 Timeout 확인됨.",
  thoughtNumber: 2,
  totalThoughts: 3,
  nextThoughtNeeded: true
})
```

### Step 3: Fact-Based Summary

Organize the information to pass to Phase 3 (hypothesis generation).

```typescript
mcp__plugin_seq-think_st__sequentialthinking({
  thought: "Phase 3으로 넘기는 정보: [검증된 사실] 1) DB Timeout 로그 3회 2) 17:00-18:00에 집중 3) 특정 API 엔드포인트에서만 발생. [미검증 가정] 1) DB 부하 추정(검증 필요) 2) 네트워크 이슈(검증 필요). [시스템 분해 결과] 정상 동작 조건 중 'DB 연결 활성' 위반 가능성 높음. [근본 원인 후보] DB 연결 관리 로직.",
  thoughtNumber: 3,
  totalThoughts: 3,
  nextThoughtNeeded: false
})
```

## Analogical Thinking vs First Principles Thinking

| Analogical Thinking (Caution) | First Principles Thinking (Recommended) |
|-------------------------------|----------------------------------------|
| "A similar bug existed before, so it must be the same cause" | First verify facts unique to this system |
| "This type of error is usually caused by X" | Collect evidence directly confirmable from logs/code |
| "Stack Overflow solved the same error with Y" | Analyze the cause within this system's context |

Analogical thinking is not inherently bad, but it should be **tagged as an unverified assumption** to prevent confirming it without verification.
