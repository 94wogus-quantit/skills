# First Principles Decomposition 상세 가이드

## 개요

제1원리 분해(First Principles Decomposition)는 버그 분석 시 "당연하다고 믿는 가정"을 식별하고, 검증된 사실만으로 근본 원인을 추적하는 기법이다.

## 프로세스

### Step 0: 요구사항 질의 (Question Requirements)

분석 시작 전, 버그가 발생하는 기능의 **요구사항 자체**를 검증한다.

**체크리스트**:
1. 이 기능의 요구사항은 **누가** 만들었는가? (부서가 아닌 개인)
2. 그 요구사항은 **현재에도 유효한가?**
3. 이 기능이 **존재하지 않으면** 이 버그도 존재하지 않는가?
4. "항상 이렇게 해왔다"가 유일한 근거인 요구사항은 없는가?
5. 요구사항을 만든 사람에게 **직접 확인**했는가?

> 요구사항 자체가 버그의 원인일 수 있다.
> "스펙대로 동작하지만 스펙이 잘못되었다"는 가장 비싼 버그다.

**Sequential Thinking 호출 예시**:

```typescript
mcp__plugin_seq-think_st__sequentialthinking({
  thought: "이 버그가 발생하는 기능의 요구사항 검증: 1) 요구사항 출처: [JIRA-XXX, 담당자 이름] 2) 현재 유효성: [유효/의문점] 3) 기능 삭제 시 버그 소멸 여부: [예/아니오] 4) '항상 이렇게 해왔다' 근거 여부: [확인 필요]",
  thoughtNumber: 1,
  totalThoughts: 4,
  nextThoughtNeeded: true
})
```

---

### Step 1: 가정 식별 (Assumption Identification)

이슈에 대해 "당연하다고 믿는 것"을 모두 나열하고, "검증된 사실"과 "미검증 가정"으로 분류한다.

**분류 기준**:

| 구분 | 정의 | 예시 |
|------|------|------|
| **검증된 사실** | 로그, 메트릭, 코드에서 직접 확인 가능 | "로그에 Timeout 3회 기록됨" |
| **미검증 가정** | 추론이나 경험에 기반한 판단 | "DB 부하가 원인일 것" |

**Sequential Thinking 호출 예시**:

```typescript
mcp__plugin_seq-think_st__sequentialthinking({
  thought: "이 이슈에 대해 당연하다고 믿는 것 나열: 1) API는 항상 200을 반환해야 함 2) DB 연결은 안정적 3) 입력값은 프론트에서 검증됨. 분류: [검증된 사실] 로그에 500 에러 3회 기록 - 직접 확인됨. [미검증 가정] 'DB 부하 때문일 것' - 추정일 뿐 확인 안 됨.",
  thoughtNumber: 1,
  totalThoughts: 3,
  nextThoughtNeeded: true
})
```

### Step 2: 근본 원리 분해 (Decomposition)

버그가 발생하는 시스템의 동작 원리를 기본 구성요소로 분해한다.

**분해 프로세스**:
1. 입력 → 처리 → 출력 흐름을 파악
2. 각 구성요소의 정상 동작 조건을 나열
3. "이 시스템이 정상 동작하려면 반드시 참이어야 하는 것" 나열
4. 그 중 "참이 아닌 것"을 찾음 → 근본 원인 후보

**Sequential Thinking 호출 예시**:

```typescript
mcp__plugin_seq-think_st__sequentialthinking({
  thought: "시스템 분해: 요청 수신(Controller) → 인증 확인(AuthMiddleware) → 비즈니스 로직(Service) → DB 조회(Repository) → 응답 반환. 정상 동작 조건: 1) Controller가 요청을 파싱 가능 2) 인증 토큰이 유효 3) Service 로직이 예외 없이 완료 4) DB 연결 활성 5) 응답 직렬화 성공. 위반 가능성: 조건 4 - 로그에서 Timeout 확인됨.",
  thoughtNumber: 2,
  totalThoughts: 3,
  nextThoughtNeeded: true
})
```

### Step 3: 사실 기반 요약 (Fact-Based Summary)

Phase 3(가설 생성)으로 넘기는 정보를 정리한다.

```typescript
mcp__plugin_seq-think_st__sequentialthinking({
  thought: "Phase 3으로 넘기는 정보: [검증된 사실] 1) DB Timeout 로그 3회 2) 17:00-18:00에 집중 3) 특정 API 엔드포인트에서만 발생. [미검증 가정] 1) DB 부하 추정(검증 필요) 2) 네트워크 이슈(검증 필요). [시스템 분해 결과] 정상 동작 조건 중 'DB 연결 활성' 위반 가능성 높음. [근본 원인 후보] DB 연결 관리 로직.",
  thoughtNumber: 3,
  totalThoughts: 3,
  nextThoughtNeeded: false
})
```

## 유추적 사고 vs 제1원리 사고

| 유추적 사고 (경계 대상) | 제1원리 사고 (권장) |
|------------------------|-------------------|
| "이전에 비슷한 버그가 있었으니 같은 원인일 것" | 이 시스템의 고유한 사실을 먼저 확인 |
| "이런 에러는 보통 X가 원인이다" | 로그/코드에서 직접 확인 가능한 증거 수집 |
| "Stack Overflow에서 같은 에러는 Y로 해결했다" | 이 시스템의 컨텍스트에서 원인 분석 |

유추적 사고 자체가 나쁜 것은 아니지만, **미검증 가정으로 태깅**하여 검증 없이 확정하지 않도록 한다.
