# Common Bug Patterns Catalog

A reference guide for frequently encountered bug patterns, their characteristics, and how to identify them during root cause analysis.

---

## Null/Undefined Reference Errors

### Pattern Characteristics
- **Symptoms**: `TypeError: Cannot read property 'X' of null/undefined`
- **Common in**: JavaScript/TypeScript, Java, C#
- **Frequency**: Very High

### How to Identify
1. Look for stack traces with "Cannot read property" or "NullPointerException"
2. Check if error occurs sporadically (suggests race condition or edge case)
3. Trace back to where the null value originates

### Search Patterns
```regex
\.[a-zA-Z_]+\s+(?!&&|\|\||if|while|for)
(?<!\?)\.[a-zA-Z_]+(?!\?)
```

### Root Causes
- Missing null checks before property access
- API returning null unexpectedly
- Uninitialized variables
- Failed async operations not handled

### Quick Verification
- Add null check: `if (obj && obj.property)`
- Use optional chaining: `obj?.property`
- Check API contract for null returns

---

## Race Conditions

### Pattern Characteristics
- **Symptoms**: Intermittent failures, "works on my machine", timing-dependent
- **Common in**: Concurrent systems, async code, multi-threaded apps
- **Frequency**: Medium-High

### How to Identify
1. Issue is not consistently reproducible
2. Frequency increases under load
3. Involves shared state or resources
4. Multiple async operations on same data

### Search Patterns
```regex
(setTimeout|setInterval|Promise\.all|async.*await)
(let|var)\s+\w+\s*=.*\n.*\1\s*=
```

### Root Causes
- Unsynchronized access to shared resources
- Callback hell with state mutations
- Multiple async operations without proper sequencing
- Missing locks or semaphores

### Quick Verification
- Add locks/mutexes around critical sections
- Use atomic operations
- Sequence operations with async/await
- Add logging to track operation order

---

## Off-by-One Errors

### Pattern Characteristics
- **Symptoms**: Array index out of bounds, missing first/last item
- **Common in**: Array/list operations, loops
- **Frequency**: Medium

### How to Identify
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

### Root Causes
- Wrong loop boundary condition
- Incorrect array indexing
- Mixing zero-based and one-based indexing
- Copy-paste errors in loop bounds

### Quick Verification
- Check loop conditions carefully
- Verify array access at boundaries
- Test with single-element arrays
- Test with empty arrays

---

## Memory Leaks

### Pattern Characteristics
- **Symptoms**: Gradual performance degradation, increasing memory usage
- **Common in**: Long-running applications, event handlers
- **Frequency**: Medium

### How to Identify
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

### Root Causes
- Event listeners not removed
- Timers not cleared
- Circular references
- Closures capturing large objects
- Cache without eviction policy

### Quick Verification
- Ensure cleanup in unmount/destroy
- Use weak references where appropriate
- Profile memory usage over time
- Check for detached DOM nodes (browser)

---

## Type Coercion Issues

### Pattern Characteristics
- **Symptoms**: Unexpected behavior with comparisons, "0" === 0
- **Common in**: JavaScript, PHP, dynamic languages
- **Frequency**: Medium

### How to Identify
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

### Root Causes
- Using `==` instead of `===`
- Implicit type conversion
- Concatenating instead of adding
- Boolean context misuse

### Quick Verification
- Use strict equality (`===`)
- Add explicit type conversion
- Enable strict mode
- Use TypeScript for static typing

---

## Configuration Errors

### Pattern Characteristics
- **Symptoms**: Works locally but fails in production
- **Common in**: Deployment, environment-specific code
- **Frequency**: High

### How to Identify
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

### Root Causes
- Hardcoded localhost URLs
- Missing environment variables
- Env-specific configuration not loaded
- Secrets hardcoded or not injected
- Different dependency versions

### Quick Verification
- Check environment variables
- Compare config across environments
- Verify external service endpoints
- Check dependency versions

---

## Database Query Issues

### Pattern Characteristics
- **Symptoms**: Slow queries, N+1 problem, deadlocks
- **Common in**: ORM usage, database-heavy apps
- **Frequency**: High

### How to Identify
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

### Root Causes
- N+1 query problem
- Missing indexes
- Inefficient joins
- Large result sets without pagination
- Missing query optimization

### Quick Verification
- Enable query logging
- Check for loops with DB calls
- Use eager loading
- Add appropriate indexes
- Profile slow queries

---

## Authentication/Authorization Bugs

### Pattern Characteristics
- **Symptoms**: Unauthorized access, permission bypass
- **Common in**: API endpoints, middleware
- **Frequency**: Medium (High severity)

### How to Identify
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

### Root Causes
- Missing authentication middleware
- Authorization checks in wrong order
- Token not validated properly
- CORS misconfiguration
- Insecure direct object references

### Quick Verification
- Audit all API endpoints
- Test with different user roles
- Verify token validation
- Check permission checks
- Review CORS configuration

---

## Async/Await Misuse

### Pattern Characteristics
- **Symptoms**: Unhandled promise rejections, unexpected timing
- **Common in**: Modern JavaScript/TypeScript
- **Frequency**: High

### How to Identify
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

### Root Causes
- Missing `await` keyword
- Not catching promise rejections
- Mixing callbacks and promises
- Fire-and-forget promises
- Async function without try-catch

### Quick Verification
- Add `await` to async calls
- Wrap in try-catch
- Use Promise.all for parallel ops
- Enable unhandled rejection detection
- Use linter for async patterns

---

## Input Validation Issues

### Pattern Characteristics
- **Symptoms**: SQL injection, XSS, data corruption
- **Common in**: User input processing, API endpoints
- **Frequency**: High (High severity)

### How to Identify
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

### Root Causes
- SQL injection via string concatenation
- XSS via innerHTML
- Command injection
- Path traversal
- No input sanitization

### Quick Verification
- Use parameterized queries
- Sanitize all user input
- Validate input types
- Use content security policy
- Escape output properly

---

## State Management Issues

### Pattern Characteristics
- **Symptoms**: UI out of sync, stale data displayed
- **Common in**: React, Vue, Angular apps
- **Frequency**: Medium

### How to Identify
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

### Root Causes
- Direct state mutation
- Missing state updates
- Shallow comparison issues
- Closure capturing stale state
- Not using setState/dispatch

### Quick Verification
- Use immutable update patterns
- Check for direct mutations
- Verify state updates trigger re-render
- Use Redux DevTools or similar
- Add React.memo where appropriate

---

## Error Handling Gaps

### Pattern Characteristics
- **Symptoms**: Unhandled exceptions, app crashes
- **Common in**: All languages/frameworks
- **Frequency**: Very High

### How to Identify
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

### Root Causes
- Empty catch blocks
- Swallowed exceptions
- Missing error boundaries
- No fallback handling
- Errors not logged

### Quick Verification
- Add proper error handling
- Log all errors
- Add user-friendly error messages
- Implement error boundaries
- Test error scenarios

---

## Caching Issues

### Pattern Characteristics
- **Symptoms**: Stale data, cache inconsistency
- **Common in**: APIs, database layers, CDNs
- **Frequency**: Medium

### How to Identify
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

### Root Causes
- Cache not invalidated on update
- No TTL set
- Cache key collisions
- Missing cache-busting
- Stale-while-revalidate issues

### Quick Verification
- Add cache invalidation
- Set appropriate TTL
- Use versioned cache keys
- Test cache behavior
- Monitor cache hit rates

---

## Using This Catalog

When analyzing an issue:

1. **Match Symptoms**: Compare error symptoms with patterns above
2. **Search Code**: Use provided regex patterns to find potential issues
3. **Verify Root Cause**: Follow "How to Identify" steps
4. **Quick Check**: Use "Quick Verification" to confirm hypothesis
5. **Multiple Patterns**: Issues often involve multiple patterns (e.g., null reference + race condition)

Remember: This is a starting point. Use systematic investigation with sequential thinking to thoroughly analyze each unique issue.
