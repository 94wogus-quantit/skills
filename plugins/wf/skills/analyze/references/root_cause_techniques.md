# Root Cause Advanced Techniques Guide

## 1. 5 Why Analysis

### When to Apply

Perform 5 Why analysis when one or more of the following conditions are met:
- The direct cause is suspected to be a **structural/systemic problem**
- The issue is a **recurring problem that cannot be resolved with a single code fix**
- A **compound cause spanning multiple components** is suspected

Not necessary for simple bugs (typos, off-by-one errors, missing null checks, etc.).

### How to Perform

```
Why 1: 왜 이 문제가 발생하는가? → [직접적 원인]
Why 2: 왜 [직접적 원인]이 발생했는가? → [중간 원인]
Why 3: 왜 [중간 원인]이 발생했는가? → [더 깊은 원인]
Why 4: 왜 [더 깊은 원인]이 발생했는가? → [구조적 원인]
Why 5: 왜 [구조적 원인]이 존재하는가? → [근본 원인]
```

- Stop before 5 iterations if a fundamental fact is reached
- Continue beyond 5 if needed
- Key focus: **system improvement, not individual blame**

### Example: Intermittent 500 Error on Payment API

```
Why 1: 왜 500 에러? → DB 트랜잭션 타임아웃
Why 2: 왜 타임아웃? → 특정 쿼리가 Lock 대기
Why 3: 왜 Lock 대기? → 동시에 같은 row를 업데이트하는 두 프로세스
Why 4: 왜 동시 업데이트? → 결제 재시도 로직이 동시 실행됨
Why 5: 왜 동시 실행? → 멱등성 키 없이 재시도

→ 표면적 원인: DB 타임아웃 (Why 1에서 멈추면 여기서 끝)
→ 근본 원인: 멱등성 키 미구현 (Why 5까지 가야 발견)
→ 구조적 원인: 재시도 로직의 동시성 설계 미흡
```

### Example: API Response Delay

```
Why 1: 왜 응답이 느린가? → DB 쿼리가 3초 걸린다
Why 2: 왜 DB 쿼리가 느린가? → 인덱스 없이 풀 테이블 스캔
Why 3: 왜 인덱스가 없는가? → 마이그레이션에서 누락됨
Why 4: 왜 마이그레이션에서 누락됐는가? → 쿼리 성능 검증 절차 없음
Why 5: 왜 검증 절차가 없는가? → CI에 슬로우 쿼리 탐지 미구축

→ 근본 원인: CI 파이프라인에 쿼리 성능 게이트 부재
```

---

## 2. Logical Falsification

### Purpose

Actively attempt to disprove the confirmed root cause to prevent confirmation bias.

### How to Perform

```
1. List all conditions that "must logically be true if this cause is correct"
2. Verify whether each condition is confirmable via code/logs/data
3. Mark unverifiable conditions as "needs verification in execute phase"
4. If any verifiable condition is false → re-examine the root cause
```

**Scope**: Perform within the bounds of static analysis (code reading). Verification requiring execution/testing should be done in the execute skill.

### Examples

```
가설: "멱등성 키 미구현이 원인"

반증 조건:
1. 동일 요청의 중복 처리가 로그에 기록되어야 함
   → 코드에서 확인: ✅ 중복 로그 존재
2. 멱등성 키 로직이 코드에 없어야 함
   → 코드에서 확인: ✅ 멱등성 키 미구현 확인
3. 중복 없는 단일 요청에서는 문제가 없어야 함
   → 로그에서 확인: ✅ 단일 요청은 정상

→ 반증 실패 (= 가설 강화): 모든 조건이 참 → 가설 신뢰도 높음
```

```
가설: "DB 연결 풀 고갈이 원인"

반증 조건:
1. 동시 연결 수가 풀 한도에 도달한 로그가 있어야 함
   → 로그에서 확인: ❌ 연결 수가 한도의 30%만 사용
2. 부하가 높은 시간대에 더 빈번해야 함
   → 메트릭 확인: ❌ 부하와 무관하게 발생

→ 반증 성공 (= 가설 기각): 조건이 거짓 → 다른 가설로 전환
```

---

## 3. Analysis Quality Checklist

Confirm the following before finalizing root cause:

```
□ Is the root cause based on "verified facts"?
  (Is it not relying on unverified assumptions?)

□ Did the analysis not stop at surface-level causes?
  (Was the structural cause identified?)

□ Was it derived from facts unique to this system, not from analogy?

□ Was a falsification attempt performed? (when applicable)

□ Do the recommendations address the root cause, not just the symptoms?
```

If any item is not met, immediately supplement that part of the analysis.

---

## 4. Hypothesis Management Techniques

### Hypothesis Evidence Tagging

Specify the evidence type when generating each hypothesis:

| Evidence Type | Definition | Handling |
|---------------|-----------|----------|
| **Fact-based** | Derived from verified facts identified in Phase 2 | Investigate first |
| **Analogy-based** | Inferred from experience or pattern matching | Tag as unverified, lower priority |

### Hypothesis Deletion (Deletion Step)

1. List all generated hypotheses
2. Specify the "evidence" for each hypothesis (candidates for deletion if no evidence)
3. Delete hypotheses that contradict verified facts
4. If the remaining hypotheses are "fewer than feels comfortable", you're on the right track

### Hypothesis Evaluation Matrix

```
| 가설 | 가능성 | 검증 비용 | 영향도 | 근거 유형 | 우선순위 |
|------|--------|----------|--------|-----------|----------|
| ... | 높/중/낮 | 낮/중/높 | 낮/중/높 | 사실/유추 | ★~★★★ |
```

Priority = Likelihood × Impact / Verification Cost

---

## 5. Recommendation Efficiency Evaluation (Simplicity Metric)

```
| 권장사항 | 구현 복잡도 | 해결 범위 | 효율성 |
|----------|------------|-----------|--------|
| ... | 낮/중/높 | 이 이슈만/유사 이슈/근본적 | ★~★★★ |
```

Key question: "Are we optimizing something that should not exist?"

Always prioritize the simplest recommendation that addresses the root cause.

---

## 6. Deletion Principle

### Core Question

"If this code is deleted, does the bug become structurally impossible?"

> "The best part is no part. The best process is no process."

### Deletion Checklist

```
□ Is this code/feature currently still in use?
□ Is a dead code path causing the bug?
□ Is an unused feature flag creating unexpected state?
□ Is an unnecessary abstraction layer hindering debugging?
□ Are there deletable dependencies?
```

### Deletion Verification Rule

If you have not re-added **more than 10%** of what was deleted, you have not deleted enough.

### Deletion vs Fix Decision Criteria

| Situation | Approach |
|-----------|----------|
| Code is no longer used | **Delete** |
| Feature exists but requirements changed | **Delete and redesign** |
| Code is actively used but has bugs | **Fix** (cannot delete) |
| Excessive abstraction increases complexity | **Delete layers and simplify** |

### Example

```
문제: API 응답에서 간헐적 null 반환
일반 접근: null 체크 추가 (방어적 코딩)
삭제 접근: null을 반환하는 레거시 코드 경로 자체를 삭제
  → 삭제 후 null 발생이 구조적으로 불가능해짐
  → try-catch, null 체크 등 방어 코드도 불필요해짐
```

---

## 7. Idiot Index (Software Version)

### Formula

> **Idiot Index = Total cost of bug fix / Actual required code change volume**

Originally a manufacturing metric ("finished product cost / raw material cost"), where a high ratio indicates an inefficient process.

### Interpretation

| Idiot Index | Meaning | Implication |
|-------------|---------|-------------|
| Low (1-3) | Fix cost ≈ Change volume | Reasonable process |
| Medium (3-10) | Fix cost > Change volume | Debugging process needs improvement |
| High (10+) | Fix cost >> Change volume | **Architecture/process problem** |

### Application

- Reference when evaluating efficiency in Phase 6
- Recommendations with high Idiot Index should consider fundamental approaches (deletion/redesign)
- "3 days for a 10-line fix" means the **system design** is the problem, not the code

### Example

```
버그: 결제 API에서 간헐적 타임아웃
수정: DB 쿼리 인덱스 추가 (1줄 변경)
소요: 원인 분석 3일 + 수정 5분

Idiot Index: 매우 높음
→ 시사점: 쿼리 성능 모니터링이 없어서 3일간 원인 추적
→ 근본 해결: 슬로우 쿼리 알림 시스템 구축 (다음부터 5분 만에 발견)
```
