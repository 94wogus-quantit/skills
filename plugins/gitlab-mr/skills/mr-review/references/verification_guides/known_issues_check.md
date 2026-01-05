# 알려진 이슈 패턴 대조 가이드

## 목표

과거 버그 패턴이 재발하지 않도록 Serena memory의 known_issues와 대조 검증합니다.

## Sequential Thinking MCP 예시

### 예시 1: Null Pointer 패턴 검증

```typescript
await mcp__plugin_workflow-bundle_sequential-thinking__sequentialthinking({
  thought: "과거 known_issues에서 발견된 null pointer exception 패턴이 이번 MR 코드에 재현되지 않았는가? Optional chaining(?.) 또는 null check가 적절히 사용되었는가?",
  thoughtNumber: 1,
  totalThoughts: 6,
  nextThoughtNeeded: true
})
```

### 예시 2: Race Condition 패턴 검증

```typescript
await mcp__plugin_workflow-bundle_sequential-thinking__sequentialthinking({
  thought: "과거 race condition 이슈가 있었던 비동기 처리 패턴이 반복되지 않았는가? Promise.all() 사용 시 에러 핸들링이 올바른가? async/await의 순서가 적절한가?",
  thoughtNumber: 2,
  totalThoughts: 6,
  nextThoughtNeeded: true
})
```

### 예시 3: Memory Leak 패턴 검증

```typescript
await mcp__plugin_workflow-bundle_sequential-thinking__sequentialthinking({
  thought: "과거 memory leak 이슈가 있었던 패턴이 재현되지 않았는가? Event listener가 적절히 제거되는가? Subscription이 unsubscribe되는가?",
  thoughtNumber: 3,
  totalThoughts: 6,
  nextThoughtNeeded: true
})
```

### 예시 4: Off-by-One Error 패턴 검증

```typescript
await mcp__plugin_workflow-bundle_sequential-thinking__sequentialthinking({
  thought: "과거 off-by-one error가 발생했던 loop/array 접근 패턴이 반복되지 않았는가? Array 인덱스 접근 시 경계 조건(< vs <=)이 올바른가?",
  thoughtNumber: 4,
  totalThoughts: 6,
  nextThoughtNeeded: true
})
```

## Serena MCP 예시

### 예시 1: 알려진 이슈 메모리 읽기

```typescript
await mcp__plugin_serena_serena__read_memory({
  memory_file_name: "known_issues.md"
})
```

### 예시 2: 과거 버그 패턴 검색

```typescript
await mcp__plugin_serena_serena__search_for_pattern({
  pattern: "null check patterns|async race conditions|memory leak patterns",
  file_mask: "*.ts"
})
```

### 예시 3: 변경된 코드의 참조 추적 (영향 범위 파악)

```typescript
await mcp__plugin_serena_serena__find_referencing_symbols({
  symbol_name: "processPayment" // 변경된 함수명
})
```

### 예시 4: 특정 버그가 있었던 파일과 유사 패턴 검색

```typescript
await mcp__plugin_serena_serena__search_for_pattern({
  pattern: "addEventListener.*without.*removeEventListener",
  file_mask: "*.ts"
})
```

## 검증 항목 체크리스트

### Null/Undefined 관련 이슈

- [ ] Null pointer exception이 자주 발생했던 패턴 사용 여부
- [ ] Optional chaining(`?.`) 또는 Nullish coalescing(`??`) 사용
- [ ] `null`과 `undefined` 구분이 명확함
- [ ] `array.length > 0` 체크 없이 `array[0]` 접근 방지

### 비동기 처리 관련 이슈

- [ ] Race condition이 발생했던 비동기 패턴 재사용 여부
- [ ] `Promise.all()` 사용 시 적절한 에러 핸들링
- [ ] `async/await` 순서가 올바름 (데이터 의존성 고려)
- [ ] Callback hell 방지 (Promise/async-await 사용)
- [ ] Timeout 설정이 적절함

### Memory Leak 관련 이슈

- [ ] Event listener 등록 후 제거 누락 여부
- [ ] Subscription이 적절히 unsubscribe됨
- [ ] Closure로 인한 메모리 누수 방지
- [ ] Timer(`setInterval`, `setTimeout`)가 적절히 clear됨
- [ ] 대용량 데이터 캐싱 시 메모리 제한 고려

### API 호출 관련 이슈

- [ ] 과거 API 호출 실패 처리 누락 이슈 재발 방지
- [ ] Retry 로직이 적절함 (무한 재시도 방지)
- [ ] Rate limiting 고려
- [ ] API 응답 validation (예상치 못한 데이터 구조 처리)

### 데이터베이스 관련 이슈

- [ ] SQL Injection 취약점이 있었던 패턴 재사용 여부
- [ ] N+1 query 문제 발생 가능성
- [ ] Transaction 처리 누락
- [ ] Connection pool 고갈 가능성

### 타입 관련 이슈

- [ ] Type coercion으로 인한 버그 패턴 재발 방지
- [ ] `==` 대신 `===` 사용 (strict equality)
- [ ] Type guard 누락으로 런타임 에러 발생 여부
- [ ] Any type 남용 방지

### Edge Case 관련 이슈

- [ ] 빈 배열/빈 객체 처리 누락
- [ ] Off-by-one error (loop 경계 조건)
- [ ] 0, -1, null, undefined 등 특수 값 처리
- [ ] 문자열 길이 0인 경우 처리

## TypeScript 코드 예시

### Null/Undefined 처리 - 올바른 예시

```typescript
// ✅ GOOD: Optional chaining과 Nullish coalescing 사용
function getUserName(user: User | null): string {
  return user?.name ?? 'Anonymous'; // ✅ 안전한 접근
}

// ✅ GOOD: 명시적인 null check
function processUser(user: User | null): void {
  if (!user) {
    console.log('User is null');
    return;
  }

  // user는 이제 User 타입으로 확정
  console.log(user.name);
}

// ❌ BAD: Null check 없이 접근
function getUserName(user: User | null): string {
  return user.name; // ❌ user가 null일 경우 에러
}
```

### Race Condition 방지 - 올바른 예시

```typescript
// ✅ GOOD: Promise.all()로 병렬 처리 + 에러 핸들링
async function fetchAllData(): Promise<void> {
  try {
    const [users, products, orders] = await Promise.all([
      fetchUsers(),
      fetchProducts(),
      fetchOrders()
    ]);

    // 모든 데이터가 준비된 후 처리
    processData(users, products, orders);
  } catch (error) {
    console.error('Failed to fetch data:', error);
  }
}

// ❌ BAD: 순차 처리로 성능 저하 또는 race condition
async function fetchAllData(): Promise<void> {
  const users = await fetchUsers();
  const products = await fetchProducts(); // 순차 처리로 느림
  const orders = await fetchOrders();

  // 또는
  fetchUsers(); // await 없이 실행하면 race condition
  fetchProducts();
  fetchOrders();
}
```

### Memory Leak 방지 - 올바른 예시

```typescript
// ✅ GOOD: Event listener 제거
class Component {
  private handleClick = () => {
    console.log('Clicked');
  };

  mount() {
    document.addEventListener('click', this.handleClick);
  }

  unmount() {
    document.removeEventListener('click', this.handleClick); // ✅ 제거
  }
}

// ✅ GOOD: RxJS Subscription unsubscribe
class DataService {
  private subscription: Subscription;

  start() {
    this.subscription = dataStream$.subscribe(data => {
      console.log(data);
    });
  }

  stop() {
    this.subscription?.unsubscribe(); // ✅ unsubscribe
  }
}

// ❌ BAD: Event listener 제거 누락
class Component {
  mount() {
    document.addEventListener('click', () => {
      console.log('Clicked');
    }); // ❌ 제거하지 않음 - memory leak
  }
}
```

### Off-by-One Error 방지 - 올바른 예시

```typescript
// ✅ GOOD: 배열 경계 조건 체크
function getLastThreeItems<T>(array: T[]): T[] {
  if (array.length < 3) {
    return array;
  }

  return array.slice(array.length - 3); // ✅ slice 사용으로 안전
}

// ✅ GOOD: Loop 경계 조건이 명확
for (let i = 0; i < array.length; i++) { // ✅ < 사용
  console.log(array[i]);
}

// ❌ BAD: Off-by-one error
function getLastThreeItems<T>(array: T[]): T[] {
  return [
    array[array.length - 3], // ❌ length가 3 미만일 경우 undefined
    array[array.length - 2],
    array[array.length - 1]
  ];
}

// ❌ BAD: Loop 경계 조건 오류
for (let i = 0; i <= array.length; i++) { // ❌ <= 사용으로 초과 접근
  console.log(array[i]); // array[array.length]는 undefined
}
```

### API 호출 에러 처리 - 올바른 예시

```typescript
// ✅ GOOD: Retry 로직 + 에러 핸들링
async function fetchWithRetry(
  url: string,
  maxRetries = 3
): Promise<Response> {
  let lastError: Error;

  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return response;
    } catch (error) {
      lastError = error as Error;
      console.log(`Retry ${i + 1}/${maxRetries}`);
      await sleep(1000 * Math.pow(2, i)); // Exponential backoff
    }
  }

  throw new Error(`Failed after ${maxRetries} retries: ${lastError.message}`);
}

// ❌ BAD: 무한 재시도 또는 에러 무시
async function fetchWithRetry(url: string): Promise<Response> {
  while (true) { // ❌ 무한 루프
    try {
      return await fetch(url);
    } catch (error) {
      // ❌ 에러를 무시하고 계속 재시도
    }
  }
}
```

### Type Safety - 올바른 예시

```typescript
// ✅ GOOD: Type guard로 안전한 타입 체크
function isUser(obj: any): obj is User {
  return obj && typeof obj.name === 'string' && typeof obj.email === 'string';
}

function processData(data: unknown): void {
  if (isUser(data)) {
    console.log(data.name); // ✅ data는 User 타입으로 확정
  }
}

// ❌ BAD: Type assertion으로 unsafe
function processData(data: unknown): void {
  const user = data as User; // ❌ 런타임에 User가 아닐 수 있음
  console.log(user.name); // 런타임 에러 가능
}
```

## 실제 검증 절차

1. **Serena로 알려진 이슈 확인**
   - `mcp__plugin_serena_serena__read_memory()`로 `known_issues.md` 읽기
   - 과거 버그 패턴, 취약점, 자주 발생하는 이슈 파악

2. **Sequential Thinking으로 패턴 대조**
   - 각 이슈 패턴에 대해 단계별로 검증
   - MR 코드에 유사 패턴이 있는지 체계적 확인

3. **Serena로 유사 패턴 검색**
   - `mcp__plugin_serena_serena__search_for_pattern()`으로 버그 패턴 검색
   - 변경된 코드와 과거 버그 코드 비교

4. **영향 범위 추적**
   - `mcp__plugin_serena_serena__find_referencing_symbols()`로 변경 영향 범위 확인
   - 과거 버그가 있었던 모듈에 영향을 주는지 검증

5. **검증 결과 문서화**
   - 재발 위험이 있는 패턴 발견 시 경고
   - 권장 수정 방향 및 과거 이슈 참조 제공
