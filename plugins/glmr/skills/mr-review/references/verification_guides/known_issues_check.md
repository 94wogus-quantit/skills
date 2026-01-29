# Known Issue Pattern Matching Guide

## Goal

Cross-reference with known_issues in Serena memory to prevent recurrence of past bug patterns.

## Sequential Thinking MCP Examples

### Example 1: Null Pointer Pattern Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "과거 known_issues에서 발견된 null pointer exception 패턴이 이번 MR 코드에 재현되지 않았는가? Optional chaining(?.) 또는 null check가 적절히 사용되었는가?",
  thoughtNumber: 1,
  totalThoughts: 6,
  nextThoughtNeeded: true
})
```

### Example 2: Race Condition Pattern Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "과거 race condition 이슈가 있었던 비동기 처리 패턴이 반복되지 않았는가? Promise.all() 사용 시 에러 핸들링이 올바른가? async/await의 순서가 적절한가?",
  thoughtNumber: 2,
  totalThoughts: 6,
  nextThoughtNeeded: true
})
```

### Example 3: Memory Leak Pattern Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "과거 memory leak 이슈가 있었던 패턴이 재현되지 않았는가? Event listener가 적절히 제거되는가? Subscription이 unsubscribe되는가?",
  thoughtNumber: 3,
  totalThoughts: 6,
  nextThoughtNeeded: true
})
```

### Example 4: Off-by-One Error Pattern Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "과거 off-by-one error가 발생했던 loop/array 접근 패턴이 반복되지 않았는가? Array 인덱스 접근 시 경계 조건(< vs <=)이 올바른가?",
  thoughtNumber: 4,
  totalThoughts: 6,
  nextThoughtNeeded: true
})
```

## Serena MCP Examples

### Example 1: Read Known Issues Memory

```typescript
await mcp__plugin_serena_serena__read_memory({
  memory_file_name: "known_issues.md"
})
```

### Example 2: Search Past Bug Patterns

```typescript
await mcp__plugin_serena_serena__search_for_pattern({
  pattern: "null check patterns|async race conditions|memory leak patterns",
  file_mask: "*.ts"
})
```

### Example 3: Track References of Changed Code (Impact Scope)

```typescript
await mcp__plugin_serena_serena__find_referencing_symbols({
  symbol_name: "processPayment" // Changed function name
})
```

### Example 4: Search Similar Patterns to Past Bug Files

```typescript
await mcp__plugin_serena_serena__search_for_pattern({
  pattern: "addEventListener.*without.*removeEventListener",
  file_mask: "*.ts"
})
```

## Verification Checklist

### Null/Undefined Related Issues

- [ ] Check for patterns that frequently caused null pointer exceptions
- [ ] Optional chaining(`?.`) or Nullish coalescing(`??`) usage
- [ ] Clear distinction between `null` and `undefined`
- [ ] Prevent `array[0]` access without `array.length > 0` check

### Async Processing Related Issues

- [ ] Check for reuse of async patterns that previously caused race conditions
- [ ] Proper error handling when using `Promise.all()`
- [ ] Correct `async/await` ordering (considering data dependencies)
- [ ] Prevent callback hell (use Promise/async-await)
- [ ] Appropriate timeout settings

### Memory Leak Related Issues

- [ ] Check for missing event listener removal after registration
- [ ] Subscriptions are properly unsubscribed
- [ ] Prevent memory leaks from closures
- [ ] Timers (`setInterval`, `setTimeout`) are properly cleared
- [ ] Memory limits considered when caching large data

### API Call Related Issues

- [ ] Prevent recurrence of past API call failure handling omissions
- [ ] Appropriate retry logic (prevent infinite retries)
- [ ] Rate limiting considered
- [ ] API response validation (handle unexpected data structures)

### Database Related Issues

- [ ] Check for reuse of patterns that previously had SQL Injection vulnerabilities
- [ ] Check for N+1 query problem potential
- [ ] Transaction handling not omitted
- [ ] Connection pool exhaustion possibility checked

### Type Related Issues

- [ ] Prevent recurrence of bugs caused by type coercion
- [ ] Use `===` instead of `==` (strict equality)
- [ ] Check for runtime errors from missing type guards
- [ ] Prevent `any` type overuse

### Edge Case Related Issues

- [ ] Empty array/empty object handling not omitted
- [ ] Off-by-one error (loop boundary conditions)
- [ ] Special value handling (0, -1, null, undefined)
- [ ] Zero-length string handling

## TypeScript Code Examples

### Null/Undefined Handling - Correct Examples

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

### Race Condition Prevention - Correct Examples

```typescript
// ✅ GOOD: Promise.all()로 병렬 처리 + 에러 핸들링
async function fetchAllData(): Promise<void> {
  try {
    const [users, products, orders] = await Promise.all([
      fetchUsers(),
      fetchProducts(),
      fetchOrders()
    ]);

    processData(users, products, orders);
  } catch (error) {
    console.error('Failed to fetch data:', error);
  }
}

// ❌ BAD: 순차 처리로 성능 저하 또는 race condition
async function fetchAllData(): Promise<void> {
  const users = await fetchUsers();
  const products = await fetchProducts();
  const orders = await fetchOrders();

  // 또는
  fetchUsers(); // await 없이 실행하면 race condition
  fetchProducts();
  fetchOrders();
}
```

### Memory Leak Prevention - Correct Examples

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

### Off-by-One Error Prevention - Correct Examples

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

### API Call Error Handling - Correct Examples

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

### Type Safety - Correct Examples

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

## Actual Verification Procedure

1. **Check known issues with Serena**
   - Read `known_issues.md` with `mcp__plugin_serena_serena__read_memory()`
   - Identify past bug patterns, vulnerabilities, and frequently occurring issues

2. **Match patterns with Sequential Thinking**
   - Step-by-step verification for each issue pattern
   - Systematically check if similar patterns exist in MR code

3. **Search similar patterns with Serena**
   - Search for bug patterns with `mcp__plugin_serena_serena__search_for_pattern()`
   - Compare changed code with past buggy code

4. **Track impact scope**
   - Confirm change impact scope with `mcp__plugin_serena_serena__find_referencing_symbols()`
   - Verify whether changes affect modules that had past bugs

5. **Document verification results**
   - Warn when patterns with recurrence risk are found
   - Provide recommended fix direction and references to past issues
