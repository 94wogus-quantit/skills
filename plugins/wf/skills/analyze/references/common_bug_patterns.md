# Common Bug Patterns Catalog

A reference guide for frequently encountered bug patterns, their characteristics, and how to identify them during root cause analysis.

---

## Null/Undefined Reference Errors

### Pattern Characteristics (패턴 특성)
- **Symptoms**: `TypeError: Cannot read property 'X' of null/undefined`
- **Common in**: JavaScript/TypeScript, Java, C#
- **Frequency**: Very High

### How to Identify (식별 방법)
1. Look for stack traces with "Cannot read property" or "NullPointerException"
2. Check if error occurs sporadically (suggests race condition or edge case)
3. Trace back to where the null value originates

### Search Patterns
```regex
\.[a-zA-Z_]+\s+(?!&&|\|\||if|while|for)
(?<!\?)\.[a-zA-Z_]+(?!\?)
```

### Root Causes (근본 원인)
- Missing null checks before property access
- API returning null unexpectedly
- Uninitialized variables
- Failed async operations not handled

### Quick Verification (빠른 검증)
- Add null check: `if (obj && obj.property)`
- Use optional chaining: `obj?.property`
- Check API contract for null returns

### 삭제 관점 (Deletion Perspective)
- nullable 필드가 정말 필요한가? non-null 설계로 전환 가능한가?
- null 발생 소스 자체를 삭제할 수 있는가?

---

## Race Conditions

### Pattern Characteristics (패턴 특성)
- **Symptoms**: Intermittent failures, "works on my machine", timing-dependent
- **Common in**: Concurrent systems, async code, multi-threaded apps
- **Frequency**: Medium-High

### How to Identify (식별 방법)
1. Issue is not consistently reproducible
2. Frequency increases under load
3. Involves shared state or resources
4. Multiple async operations on same data

### Search Patterns
```regex
(setTimeout|setInterval|Promise\.all|async.*await)
(let|var)\s+\w+\s*=.*\n.*\1\s*=
```

### Root Causes (근본 원인)
- Unsynchronized access to shared resources
- Callback hell with state mutations
- Multiple async operations without proper sequencing
- Missing locks or semaphores

### Quick Verification (빠른 검증)
- Add locks/mutexes around critical sections
- Use atomic operations
- Sequence operations with async/await
- Add logging to track operation order

### 삭제 관점 (Deletion Perspective)
- 공유 상태(shared state)가 정말 필요한가? 상태 제거 시 race condition 자체가 불가능
- 비동기 병렬 처리가 정말 필요한가? 순차 처리로 충분하지 않은가?

---

## Off-by-One Errors

### Pattern Characteristics (패턴 특성)
- **Symptoms**: Array index out of bounds, missing first/last item
- **Common in**: Array/list operations, loops
- **Frequency**: Medium

### How to Identify (식별 방법)
1. Error mentions index out of range
2. Last or first element not processed
3. Look for `< vs <=` or `> vs >=`
4. Zero-based vs one-based indexing confusion

### Search Patterns
```regex
\[\s*\w+\s*[+-]\s*1\s*\]
for.*<(?!=).*length
for.*<=.*length\s*-\s*1
```

### Root Causes (근본 원인)
- Wrong loop boundary condition
- Incorrect array indexing
- Mixing zero-based and one-based indexing
- Copy-paste errors in loop bounds

### Quick Verification (빠른 검증)
- Check loop conditions carefully
- Verify array access at boundaries
- Test with single-element arrays
- Test with empty arrays

### 삭제 관점 (Deletion Perspective)
- 수동 인덱스 관리가 정말 필요한가? 고수준 API(map, forEach)로 대체 가능한가?
- 커스텀 루프를 삭제하고 라이브러리 함수로 대체할 수 있는가?

---

## Memory Leaks

### Pattern Characteristics (패턴 특성)
- **Symptoms**: Gradual performance degradation, increasing memory usage
- **Common in**: Long-running applications, event handlers
- **Frequency**: Medium

### How to Identify (식별 방법)
1. Memory usage grows over time
2. Performance degrades gradually
3. Eventually runs out of memory
4. Profiler shows retained objects

### Search Patterns
```regex
addEventListener.*(?!removeEventListener)
setInterval.*(?!clearInterval)
new\s+\w+\(.*\)(?!.*=\s*null)
```

### Root Causes (근본 원인)
- Event listeners not removed
- Timers not cleared
- Circular references
- Closures capturing large objects
- Cache without eviction policy

### Quick Verification (빠른 검증)
- Ensure cleanup in unmount/destroy
- Use weak references where appropriate
- Profile memory usage over time
- Check for detached DOM nodes (browser)

### 삭제 관점 (Deletion Perspective)
- 이 이벤트 리스너/타이머가 정말 필요한가?
- 수동 메모리 관리 대신 프레임워크의 자동 정리 메커니즘을 사용할 수 있는가?

---

## Type Coercion Issues

### Pattern Characteristics (패턴 특성)
- **Symptoms**: Unexpected behavior with comparisons, "0" === 0
- **Common in**: JavaScript, PHP, dynamic languages
- **Frequency**: Medium

### How to Identify (식별 방법)
1. Unexpected comparison results
2. String vs number confusion
3. Truthy/falsy value misunderstandings
4. Check for `==` instead of `===`

### Search Patterns
```regex
==(?!=)
!=(?!=)
\+\s*["'].*["']\s*\+
```

### Root Causes (근본 원인)
- Using `==` instead of `===`
- Implicit type conversion
- Concatenating instead of adding
- Boolean context misuse

### Quick Verification (빠른 검증)
- Use strict equality (`===`)
- Add explicit type conversion
- Enable strict mode
- Use TypeScript for static typing

### 삭제 관점 (Deletion Perspective)
- 동적 타입이 정말 필요한가? TypeScript 등 정적 타이핑으로 전환하면 문제 자체가 불가능
- 암시적 변환 코드를 삭제하고 명시적 변환으로 교체할 수 있는가?

---

## Configuration Errors

### Pattern Characteristics (패턴 특성)
- **Symptoms**: Works locally but fails in production
- **Common in**: Deployment, environment-specific code
- **Frequency**: High

### How to Identify (식별 방법)
1. Different behavior across environments
2. Missing environment variables
3. Hardcoded values for specific env
4. Connection failures

### Search Patterns
```regex
localhost:\d+
127\.0\.0\.1
http://(?!.*process\.env)
(API_KEY|SECRET|PASSWORD)\s*=\s*["'][^"']+["']
```

### Root Causes (근본 원인)
- Hardcoded localhost URLs
- Missing environment variables
- Env-specific configuration not loaded
- Secrets hardcoded or not injected
- Different dependency versions

### Quick Verification (빠른 검증)
- Check environment variables
- Compare config across environments
- Verify external service endpoints
- Check dependency versions

### 삭제 관점 (Deletion Perspective)
- 환경별 분기가 정말 필요한가? 환경 차이 자체를 줄일 수 있는가?
- 하드코딩된 설정 코드를 삭제할 수 있는가?

---

## Database Query Issues

### Pattern Characteristics (패턴 특성)
- **Symptoms**: Slow queries, N+1 problem, deadlocks
- **Common in**: ORM usage, database-heavy apps
- **Frequency**: High

### How to Identify (식별 방법)
1. Slow API responses
2. Database CPU spike
3. Many small queries in logs
4. Query timeout errors

### Search Patterns
```regex
for.*\.(find|get|query)
map.*async.*\.(find|save)
SELECT.*\n.*SELECT
```

### Root Causes (근본 원인)
- N+1 query problem
- Missing indexes
- Inefficient joins
- Large result sets without pagination
- Missing query optimization

### Quick Verification (빠른 검증)
- Enable query logging
- Check for loops with DB calls
- Use eager loading
- Add appropriate indexes
- Profile slow queries

### 삭제 관점 (Deletion Perspective)
- 이 쿼리가 정말 필요한가? 캐시나 비정규화로 쿼리 자체를 제거할 수 있는가?
- N+1 패턴의 루프를 삭제하고 JOIN으로 대체할 수 있는가?

---

## Authentication/Authorization Bugs

### Pattern Characteristics (패턴 특성)
- **Symptoms**: Unauthorized access, permission bypass
- **Common in**: API endpoints, middleware
- **Frequency**: Medium (High severity)

### How to Identify (식별 방법)
1. User accessing resources they shouldn't
2. Missing auth checks in endpoints
3. Token validation skipped
4. Role checks incomplete

### Search Patterns
```regex
app\.(get|post|put|delete).*(?!.*auth)
router\.\w+\(["']/api.*(?!.*authenticate)
req\.user(?!.*permission)
```

### Root Causes (근본 원인)
- Missing authentication middleware
- Authorization checks in wrong order
- Token not validated properly
- CORS misconfiguration
- Insecure direct object references

### Quick Verification (빠른 검증)
- Audit all API endpoints
- Test with different user roles
- Verify token validation
- Check permission checks
- Review CORS configuration

### 삭제 관점 (Deletion Perspective)
- 인증이 필요 없는 공개 API로 전환 가능한가?
- 커스텀 인증 로직을 삭제하고 프레임워크 기본 미들웨어를 사용할 수 있는가?

---

## Async/Await Misuse

### Pattern Characteristics (패턴 특성)
- **Symptoms**: Unhandled promise rejections, unexpected timing
- **Common in**: Modern JavaScript/TypeScript
- **Frequency**: High

### How to Identify (식별 방법)
1. Unhandled promise rejection warnings
2. Operations executing out of order
3. Missing `await` keywords
4. Incorrect error handling

### Search Patterns
```regex
async.*\{[^}]*(?<!await)\s*\w+\(
\.then\(.*\.catch\(.*\)(?!\s*\))
Promise\.(all|race).*(?!await)
```

### Root Causes (근본 원인)
- Missing `await` keyword
- Not catching promise rejections
- Mixing callbacks and promises
- Fire-and-forget promises
- Async function without try-catch

### Quick Verification (빠른 검증)
- Add `await` to async calls
- Wrap in try-catch
- Use Promise.all for parallel ops
- Enable unhandled rejection detection
- Use linter for async patterns

### 삭제 관점 (Deletion Perspective)
- 비동기 처리가 정말 필요한가? 동기 처리로 충분하지 않은가?
- 콜백/프로미스 혼용 코드를 삭제하고 async/await로 통일할 수 있는가?

---

## Input Validation Issues

### Pattern Characteristics (패턴 특성)
- **Symptoms**: SQL injection, XSS, data corruption
- **Common in**: User input processing, API endpoints
- **Frequency**: High (High severity)

### How to Identify (식별 방법)
1. User input used directly in queries
2. No sanitization before rendering
3. Missing type validation
4. Dangerous characters not escaped

### Search Patterns
```regex
\$\{.*req\.(body|query|params)
innerHTML\s*=\s*\w+
sql\s*=\s*["'].*\+
eval\(
```

### Root Causes (근본 원인)
- SQL injection via string concatenation
- XSS via innerHTML
- Command injection
- Path traversal
- No input sanitization

### Quick Verification (빠른 검증)
- Use parameterized queries
- Sanitize all user input
- Validate input types
- Use content security policy
- Escape output properly

### 삭제 관점 (Deletion Perspective)
- 사용자 입력을 직접 처리하는 코드가 정말 필요한가? 검증 라이브러리로 대체 가능한가?
- 직접 SQL 문자열 조합을 삭제하고 ORM/파라미터화 쿼리로 대체할 수 있는가?

---

## State Management Issues

### Pattern Characteristics (패턴 특성)
- **Symptoms**: UI out of sync, stale data displayed
- **Common in**: React, Vue, Angular apps
- **Frequency**: Medium

### How to Identify (식별 방법)
1. UI doesn't update after action
2. Old data displayed
3. Component doesn't re-render
4. Mutations to immutable state

### Search Patterns
```regex
this\.state\.\w+\s*=
\w+\.push\(.*\)\s*(?!.*set)
splice\(.*\)\s*(?!.*set)
```

### Root Causes (근본 원인)
- Direct state mutation
- Missing state updates
- Shallow comparison issues
- Closure capturing stale state
- Not using setState/dispatch

### Quick Verification (빠른 검증)
- Use immutable update patterns
- Check for direct mutations
- Verify state updates trigger re-render
- Use Redux DevTools or similar
- Add React.memo where appropriate

### 삭제 관점 (Deletion Perspective)
- 이 상태가 정말 필요한가? 서버에서 항상 최신 데이터를 가져오면 클라이언트 상태가 불필요
- 수동 상태 관리를 삭제하고 상태 관리 라이브러리를 사용할 수 있는가?

---

## Error Handling Gaps

### Pattern Characteristics (패턴 특성)
- **Symptoms**: Unhandled exceptions, app crashes
- **Common in**: All languages/frameworks
- **Frequency**: Very High

### How to Identify (식별 방법)
1. Application crashes unexpectedly
2. Generic error messages
3. Stack traces in production
4. Silent failures

### Search Patterns
```regex
try\s*\{[^}]*\}\s*catch\s*\([^)]*\)\s*\{\s*\}
\.catch\(\)
throw\s+new\s+Error\(["']TODO
```

### Root Causes (근본 원인)
- Empty catch blocks
- Swallowed exceptions
- Missing error boundaries
- No fallback handling
- Errors not logged

### Quick Verification (빠른 검증)
- Add proper error handling
- Log all errors
- Add user-friendly error messages
- Implement error boundaries
- Test error scenarios

### 삭제 관점 (Deletion Perspective)
- 빈 catch 블록이 정말 필요한가? 에러를 삼키는 코드를 삭제하라
- 커스텀 에러 핸들링을 삭제하고 프레임워크의 글로벌 에러 핸들러를 사용할 수 있는가?

---

## Caching Issues

### Pattern Characteristics (패턴 특성)
- **Symptoms**: Stale data, cache inconsistency
- **Common in**: APIs, database layers, CDNs
- **Frequency**: Medium

### How to Identify (식별 방법)
1. Old data returned after update
2. Inconsistent responses
3. Cache never invalidated
4. TTL too long

### Search Patterns
```regex
cache\.(get|set).*(?!.*expire|TTL|invalidate)
Redis.*(?!.*del|expire)
localStorage\.setItem.*(?!.*clear)
```

### Root Causes (근본 원인)
- Cache not invalidated on update
- No TTL set
- Cache key collisions
- Missing cache-busting
- Stale-while-revalidate issues

### Quick Verification (빠른 검증)
- Add cache invalidation
- Set appropriate TTL
- Use versioned cache keys
- Test cache behavior
- Monitor cache hit rates

### 삭제 관점 (Deletion Perspective)
- 이 캐시가 정말 필요한가? 캐시 없이도 충분한 성능이 나오는가?
- 커스텀 캐시 로직을 삭제하고 CDN이나 프레임워크 캐시를 사용할 수 있는가?

---

## Using This Catalog

When analyzing an issue:

1. **Match Symptoms**: Compare error symptoms with patterns above
2. **Search Code**: Use provided regex patterns to find potential issues
3. **Verify Root Cause**: Follow "How to Identify" steps
4. **Quick Check**: Use "Quick Verification" to confirm hypothesis
5. **Multiple Patterns**: Issues often involve multiple patterns (e.g., null reference + race condition)
6. **Apply First Principles**: Identify "assumptions taken for granted" in each pattern, classify into verified facts and unverified assumptions
7. **Deletion Perspective**: Ask "if this code did not exist, would this bug also not exist?" Deletion may be a more fundamental fix than patching
8. **Evidence Tagging**: Tag all hypotheses as "fact-based" vs "analogy-based (unverified)" to prevent confirmation bias

Remember: This is a starting point. Use systematic investigation with sequential thinking to thoroughly analyze each unique issue.
