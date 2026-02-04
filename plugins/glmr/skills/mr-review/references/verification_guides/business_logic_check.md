# Business Logic Accuracy Verification Guide

## Goal

Verify that the implementation is accurate compared to JIRA objectives. Detect incorrect logic, missed edge cases, and boundary value handling errors.

## Sequential Thinking MCP Examples

### Example 1: AC Condition Accuracy Analysis

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "AC#1 '5회 실패 시 계정 잠금' 분석: 현재 코드에서 실패 횟수를 어떻게 카운트하는가? 5회 정확히 체크하는가? (>= 5 vs == 5) 리셋 조건은 무엇인가?",
  thoughtNumber: 1,
  totalThoughts: 6,
  nextThoughtNeeded: true
})
```

### Example 2: Edge Case Review

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "엣지케이스 검토: 동시 로그인 시도 시 race condition이 있는가? 4회 실패 후 성공 시 카운트가 리셋되는가? 잠금 해제 조건이 명시되어 있는가?",
  thoughtNumber: 2,
  totalThoughts: 6,
  nextThoughtNeeded: true
})
```

### Example 3: Negative Case Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "AC에 '~하면 안 된다'는 조건이 있는가? 예: '잠금된 계정은 로그인 시도가 불가해야 한다'. 이 부정 케이스가 코드에 구현되었는가?",
  thoughtNumber: 3,
  totalThoughts: 6,
  nextThoughtNeeded: true
})
```

### Example 4: Data Consistency Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "계산 로직 검증: 할인율 계산이 정확한가? 소수점 처리는 어떻게 하는가? 집계 값이 개별 항목의 합과 일치하는가?",
  thoughtNumber: 4,
  totalThoughts: 6,
  nextThoughtNeeded: true
})
```

### Example 5: State Transition Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "상태 전이 검증: 주문 상태가 PENDING → CONFIRMED → SHIPPED → DELIVERED 순서로만 변경 가능한가? 잘못된 상태 전이(예: PENDING → DELIVERED)를 방지하는가?",
  thoughtNumber: 5,
  totalThoughts: 6,
  nextThoughtNeeded: true
})
```

### Example 6: Timeout/Expiry Condition Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "시간 관련 조건 검증: AC에 '30분 후 자동 해제'가 있다면, 타이머/스케줄러가 구현되었는가? 시간대(timezone) 처리가 올바른가?",
  thoughtNumber: 6,
  totalThoughts: 6,
  nextThoughtNeeded: false
})
```

## Serena MCP Examples

### Example 1: Search Related Business Logic

```typescript
await mcp__plugin_serena_serena__search_for_pattern({
  substring_pattern: "lockAccount|unlockAccount|failedAttempts",
  paths_include_glob: "**/*.ts"
})
```

### Example 2: Compare Existing Similar Logic

```typescript
await mcp__plugin_serena_serena__find_symbol({
  name_path: "AuthService.login",
  relative_path: "src/services/auth.service.ts"
})
```

### Example 3: Check State Management Patterns

```typescript
await mcp__plugin_serena_serena__search_for_pattern({
  substring_pattern: "status.*=.*|setState|updateState",
  paths_include_glob: "**/services/**/*.ts"
})
```

## Verification Checklist

| Verification Item | Description | Check Points |
|-------------------|-------------|--------------|
| **Logic accuracy** | Are conditions specified in AC accurately implemented in code? | Conditionals, comparison operators, threshold values |
| **Boundary value handling** | Is boundary value handling correct (5 times = exactly 5? 5 or more?) | `>=`, `>`, `==` operator verification |
| **Edge cases** | Are exceptional situations (concurrency, timeout, null) considered? | null check, race condition, timeout |
| **Negative cases** | Are "must not" conditions implemented? | Validation, guard clauses |
| **Data consistency** | Are calculations, aggregations, and state changes accurate? | Decimal points, rounding, sum verification |
| **State transitions** | Is the state change order correct? | State machine, transition conditions |
| **Time conditions** | Are expiry, timeout, and schedule conditions implemented? | Timers, cron, TTL |

## Issue Finding JSON Format

```json
{
  "file": "src/services/auth.ts",
  "line": 45,
  "severity": "🔴 Critical",
  "title": "잠금 해제 조건 누락",
  "description": "AC에 따르면 30분 후 자동 해제되어야 하나, 해제 로직이 구현되지 않았습니다. 현재 코드는 계정을 잠그기만 하고 해제하지 않습니다.",
  "current_code": "if (failCount >= 5) {\n  lockAccount(userId);\n}",
  "suggested_code": "if (failCount >= 5) {\n  lockAccount(userId, { unlockAfter: 30 * 60 * 1000 });\n  scheduleUnlock(userId, 30 * 60 * 1000);\n}",
  "reason": "AC#1에 명시된 '30분 후 자동 해제' 요구사항을 충족하기 위해 타이머 또는 스케줄러 구현이 필요합니다."
}
```

## Common Business Logic Error Patterns

### 1. Boundary Value Error (Off-by-one)

```typescript
// 잘못된 예: 5회 초과에서 잠금 (6회부터)
if (failCount > 5) { lockAccount(); }

// 올바른 예: 5회 이상에서 잠금 (5회부터)
if (failCount >= 5) { lockAccount(); }
```

### 2. Missing State Reset

```typescript
// 잘못된 예: 성공 시 실패 횟수 리셋 안 함
if (loginSuccess) {
  return { success: true };
}

// 올바른 예: 성공 시 실패 횟수 리셋
if (loginSuccess) {
  resetFailCount(userId);
  return { success: true };
}
```

### 3. Missing Concurrency Consideration

```typescript
// 잘못된 예: race condition 가능
const count = await getFailCount(userId);
await setFailCount(userId, count + 1);

// 올바른 예: atomic 연산 사용
await incrementFailCount(userId);
```

### 4. Missing null/undefined Handling

```typescript
// 잘못된 예: null 체크 없음
const discount = user.membership.discountRate * price;

// 올바른 예: optional chaining + default
const discount = (user?.membership?.discountRate ?? 0) * price;
```

### 5. Missing Timezone Consideration

```typescript
// 잘못된 예: 로컬 시간 사용
const expiresAt = new Date();
expiresAt.setMinutes(expiresAt.getMinutes() + 30);

// 올바른 예: UTC 사용
const expiresAt = new Date(Date.now() + 30 * 60 * 1000);
```

## Best Practices

1. **Thoroughly analyze each AC before translating to code**
   - Clearly identify conditions, actions, and exceptions for each AC
   - Identify implicit requirements (e.g., reset conditions)

2. **Verify boundary value test cases**
   - Test 4, 5, and 6 occurrences individually
   - Test 0, negative, and null cases

3. **Verify using state diagrams**
   - List all possible state transitions
   - Confirm logic to prevent invalid transitions

4. **Pay special attention to time-related logic**
   - Consider timezone and DST (Daylight Saving Time)
   - Verify accuracy of expiry/renewal logic
