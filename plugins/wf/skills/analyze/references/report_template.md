# Issue Analysis Report Template

이 템플릿으로 `[ISSUE_ID]_REPORT.md` 파일을 작성한다.

---

# Issue Analysis: [Issue Title/ID]

**Date**: [YYYY-MM-DD]
**Analyzer**: Claude Code
**Issue ID**: [JIRA-123 or descriptive name]
**Severity**: [Critical / High / Medium / Low]

## Summary

[요약 (한 문단):
- 이슈 내용
- 원인
- 영향 범위
- 해결 방향]

---

## Context

### JIRA Issue
- **Link**: [Issue URL]
- **Reporter**: [Name]
- **Affected Version**: [Version]
- **Environment**: [Production / Staging / Development]
- **Key Details**: [설명에서 중요 정보]

### Sentry Error (해당 시)
- **Error Link**: [Sentry URL]
- **First Seen**: [Date/Time]
- **Last Seen**: [Date/Time]
- **Frequency**: [Count / Rate]
- **Affected Users**: [Count or percentage]
- **Error Message**:
  ```
  [실제 에러 메시지]
  ```

### Additional Context
- **사용자 보고**: [증상 요약]
- **재현 절차**: [있는 경우]
- **관련 파일**: [사용자 제공 파일]
- **스크린샷/로그**: [첨부 참조]

---

## First Principles 분석

### 식별된 가정
- [가정 1]: 검증 여부 (✅ 검증됨 / ❌ 미검증)
- [가정 2]: 검증 여부 (✅/❌)

### 근본 사실
- [사실 1]: 출처 (로그/코드/메트릭)
- [사실 2]: 출처

### 시스템 분해
- 입력 → [Component A] → [Component B] → 출력
- 정상 동작 조건 중 위반된 것: [조건]

---

## Investigation Process

### 조사 단계

1. **Step 1**: [조사 내용]
   - 도구: [Serena / Sentry / JIRA / etc.]
   - 발견: [결과]

2. **Step 2**: [조사 내용]
   - 도구: [도구명]
   - 발견: [결과]

---

## 가설 평가

| 가설 | 가능성 | 검증 비용 | 영향도 | 근거 유형 | 우선순위 | 상태 |
|------|--------|----------|--------|-----------|----------|------|
| [가설 1] | 높/중/낮 | 낮/중/높 | 낮/중/높 | 사실/유추 | ★~★★★ | 채택/기각 |
| [가설 2] | 높/중/낮 | 낮/중/높 | 낮/중/높 | 사실/유추 | ★~★★★ | 채택/기각 |

---

## Root Cause

### Primary Root Cause

**Location**: [`file_path.ts:123`](path/to/file.ts#L123)

**Code Snippet**:
```typescript
// 문제 코드
function problematicFunction() {
  // Line 123: 이슈 발생 지점
  const result = nullableValue.property; // No null check
  return result;
}
```

**Explanation**:

[기술적 원인 설명:
- 문제를 일으키는 코드 패턴
- 왜 이 패턴이 문제인지
- 런타임에서 이슈가 발현되는 과정]

**Trigger Conditions**:

이슈 발생 조건:
1. [조건 1]
2. [조건 2]
3. [조건 3]

```
사용자 행동: [행동]
↓
Component: [A 처리]
↓
Component: [B에서 null 수신]  ← 이슈 발생
↓
Result: [에러 발생]
```

### Contributing Factors

**Factor 1: [설명]**
- **Location**: [`file.ts:45`](path/to/file.ts#L45)
- **Impact**: [문제 악화 방식]
- **Recommendation**: [해결 방안]

### Impact Assessment

**영향 범위**:
- **Users**: [전체 / 특정 그룹 / 비율]
- **Frequency**: [매번 / 간헐적 / 드물게]
- **Reproducibility**: [항상 / 자주 / 간헐적 / 재현 어려움]

**비즈니스 영향**:
- **UX**: [저하 / 중단 / 사용 불가]
- **데이터 무결성**: [위험 / 안전]
- **성능**: [저하 / 정상]
- **보안**: [취약 / 안전]

**Risk Level**: [Critical / High / Medium / Low]

---

## 삭제 가능성 평가

- [x/□] 이 코드/기능은 현재도 필요한가?
- [x/□] 삭제하면 버그가 구조적으로 불가능해지는가?
- [x/□] Dead code / 미사용 feature flag / 불필요한 추상화가 원인인가?

**결론**: [삭제 가능: 구체적 삭제 대상과 이유 / 삭제 불가: 사유]

---

## 5 Why 분석 (해당 시)

> 적용 조건: 구조적/시스템적 문제, 반복 이슈, 복합 원인

```
Why 1: 왜 이 문제가 발생하는가? → [직접적 원인]
Why 2: 왜 [직접적 원인]이 발생했는가? → [중간 원인]
Why 3: 왜 [중간 원인]이 발생했는가? → [더 깊은 원인]
Why 4: 왜 [더 깊은 원인]이 발생했는가? → [구조적 원인]
Why 5: 왜 [구조적 원인]이 존재하는가? → [근본 원인]
```

→ 표면적 원인: [Why 1]
→ 근본 원인: [Why 5]

---

## 반증 시도 (해당 시)

| 가설 | 반증 조건 | 검증 방법 | 결과 |
|------|-----------|-----------|------|
| [가설] | [참이어야 하는 조건] | [코드/로그/데이터] | 반증 실패(가설 강화) / 반증 성공(가설 기각) |

---

## 분석 품질 체크

- [x/□] 근본 원인이 "검증된 사실"에 기반하는가?
- [x/□] 표면적 원인에서 멈추지 않았는가? (구조적 원인까지 파악)
- [x/□] 유추가 아닌 이 시스템의 고유한 사실에서 도출했는가?
- [x/□] 반증 시도를 수행했는가? (해당하는 경우)
- [x/□] 권장사항이 증상이 아닌 근본 원인을 해결하는가?

---

## 5단계 알고리즘 평가

| Step | 질문 | 답변 |
|------|------|------|
| 1. 요구사항 질의 | 이 기능의 요구사항이 현재도 유효한가? | [구체적 답변] |
| 2. 삭제 | 코드 삭제로 해결 가능한가? | [삭제 가능성 평가 결과 참조] |
| 3. 단순화 | 더 간단하게 재구성 가능한가? | [구체적 방안] |
| 4. 가속 | 재현-검증 사이클 단축 방법? | [구체적 방안] |
| 5. 자동화 | 자동 감지 방법? | [테스트/린터 제안] |

→ 권장 접근: Step [N]에서 해결 ([이유])

---

## Recommendations

### Immediate Actions (Hotfix)

**Priority**: P0

```typescript
// 즉시 수정
function problematicFunction() {
  if (!nullableValue) {
    return defaultValue;
  }
  const result = nullableValue.property;
  return result;
}
```

**Deployment Strategy**:
1. [배포 절차]
2. [검증 단계]
3. [롤백 계획]

### Long-term Solution

**Priority**: P1

**Approach**: [근본 수정 접근법]

**Implementation Details**:
1. [컴포넌트 수정 사항 + 코드 예시]
2. [추가 수정 사항]

**Edge Cases**:
- [ ] Case 1: [설명 및 처리 방안]
- [ ] Case 2: [설명 및 처리 방안]

### Efficiency Evaluation

| 권장사항 | 구현 복잡도 | 해결 범위 | 효율성 |
|----------|------------|-----------|--------|
| [즉시 수정] | 낮/중/높 | 이 이슈만/유사 이슈/근본적 | ★~★★★ |
| [장기 해결] | 낮/중/높 | 이 이슈만/유사 이슈/근본적 | ★~★★★ |

→ 가장 단순하면서 근본 원인을 해결하는 방안 우선 권장

### Testing

**Unit Tests**:
```typescript
describe('[function]', () => {
  it('should handle null values gracefully', () => {
    const result = problematicFunction(null);
    expect(result).toBe(defaultValue);
  });
});
```

**Manual Testing Checklist**:
- [ ] 데이터 누락 시 테스트
- [ ] 잘못된 데이터 테스트
- [ ] 엣지 케이스 테스트
- [ ] 에러 핸들링 및 복구 확인

### Prevention

- [ ] 코드 리뷰 체크리스트 항목 추가
- [ ] 린팅 규칙 추가
- [ ] API 문서 업데이트
- [ ] 모니터링/알림 설정

### Related Areas to Review

**유사 패턴**:
1. [`file1.ts:45`](path/to/file1.ts#L45) - 유사 패턴
   - **Risk**: Medium
   - **Action**: [조치]

**Upstream/Downstream Dependencies**:
- [`data-provider.ts`](path/to/data-provider.ts) - [영향]
- [`consumer-a.ts`](path/to/consumer-a.ts) - [영향]

---

## Code Complexity Assessment (해당 시)

> Phase 4D에서 복잡도 문제 발견 시 작성

- **Cyclomatic Complexity**: [수치]
- **Function Length**: [줄 수]
- **SRP Violations**: [설명]
- **Refactoring Suggestion**: [방안]

---

## AC Reverse Tracing (해당 시)

> Phase 4E에서 JIRA AC 역추적 시 작성

| AC # | 설명 | 관련 코드 | 상태 |
|------|------|-----------|------|
| AC#1 | [설명] | [`file:line`] | ✅/❌ |

---

## Appendix

### Stack Trace
```
[Sentry 스택 트레이스 (해당 시)]
```

### Related Issues
- [ISSUE-456] - [관련 이슈 설명]

### References
- [관련 문서 링크]
- [유사 해결 사례 링크]

---

**Report Generated**: [Timestamp]
**Tools Used**: Serena, Sentry, JIRA, Sequential Thinking
**Next Steps**: `plan` 스킬로 구현 계획 작성
