# Security Verification Guide

## Goal

Systematically verify OWASP Top 10 and common security vulnerabilities.

## Sequential Thinking MCP Examples

### Example 1: SQL Injection Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "SQL Injection 취약점: 사용자 입력이 직접 SQL 쿼리에 사용되는가? Prepared statement 또는 ORM의 parameterized query를 사용하는가? raw query 사용 시 입력 검증이 충분한가?",
  thoughtNumber: 1,
  totalThoughts: 10,
  nextThoughtNeeded: true
})
```

### Example 2: XSS Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "XSS 취약점: 사용자 입력이 렌더링 전에 sanitize되는가? innerHTML 대신 textContent를 사용하는가? React/Vue는 기본적으로 escape하지만, dangerouslySetInnerHTML이나 v-html 사용 시 검증이 있는가?",
  thoughtNumber: 2,
  totalThoughts: 10,
  nextThoughtNeeded: true
})
```

### Example 3: Authentication/Authorization Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "인증/인가: JWT 토큰 검증이 올바른가? 권한 체크가 모든 보호된 엔드포인트에 있는가? Role-based 또는 Permission-based 접근 제어가 적절한가? 토큰 만료 시간이 적절한가?",
  thoughtNumber: 3,
  totalThoughts: 10,
  nextThoughtNeeded: true
})
```

### Example 4: Sensitive Information Exposure Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "민감 정보 노출: API 키, 비밀번호, JWT secret, 토큰이 하드코딩되지 않았는가? 환경변수 사용이 적절한가? 로그에 민감 정보(비밀번호, 토큰, 개인정보)가 남지 않는가? Git에 .env 파일이 커밋되지 않았는가?",
  thoughtNumber: 4,
  totalThoughts: 10,
  nextThoughtNeeded: true
})
```

### Example 5: CSRF Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "CSRF 보호: 상태 변경 요청(POST, PUT, DELETE)에 CSRF 토큰이 있는가? SameSite 쿠키 속성이 적절히 설정되었는가? CORS 설정이 안전한가?",
  thoughtNumber: 5,
  totalThoughts: 10,
  nextThoughtNeeded: true
})
```

### Example 6: Input Validation Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "입력 검증: 모든 사용자 입력에 대한 validation이 있는가? 타입 검증, 길이 제한, 허용 문자 제한이 적절한가? 화이트리스트 방식으로 검증하는가?",
  thoughtNumber: 6,
  totalThoughts: 10,
  nextThoughtNeeded: true
})
```

### Example 7: Encryption Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "암호화: 비밀번호가 bcrypt, argon2 등 안전한 해싱 알고리즘으로 저장되는가? HTTPS 사용이 강제되는가? 민감 데이터 전송 시 암호화가 되는가?",
  thoughtNumber: 7,
  totalThoughts: 10,
  nextThoughtNeeded: true
})
```

### Example 8: Error Message Security Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "에러 메시지 보안: 에러 메시지가 내부 구조나 민감 정보를 노출하지 않는가? 프로덕션 환경에서 스택 트레이스가 노출되지 않는가?",
  thoughtNumber: 8,
  totalThoughts: 10,
  nextThoughtNeeded: true
})
```

### Example 9: Rate Limiting Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "Rate Limiting: 브루트 포스 공격 방지를 위한 rate limiting이 있는가? 로그인, API 호출에 적절한 제한이 설정되었는가?",
  thoughtNumber: 9,
  totalThoughts: 10,
  nextThoughtNeeded: true
})
```

### Example 10: Dependency Security Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "의존성 보안: 알려진 취약점이 있는 패키지를 사용하지 않는가? npm audit, Snyk 등으로 검증되었는가? 불필요한 의존성이 없는가?",
  thoughtNumber: 10,
  totalThoughts: 10,
  nextThoughtNeeded: false
})
```

## Serena MCP Examples

### Example 1: Search Security-Related Patterns (Hardcoded Secrets)

```typescript
await mcp__plugin_serena_serena__search_for_pattern({
  pattern: "API_KEY|PASSWORD|SECRET|token|private.*key",
  file_mask: "*.ts"
})
```

### Example 2: Check Past Security Incidents

```typescript
await mcp__plugin_serena_serena__read_memory({
  memory_file_name: "security_incidents.md"
})
```

### Example 3: Search SQL Injection Risk Patterns

```typescript
await mcp__plugin_serena_serena__search_for_pattern({
  pattern: "query.*\\+|execute.*\\$\\{|raw.*sql",
  file_mask: "*.ts"
})
```

### Example 4: Search XSS Risk Patterns

```typescript
await mcp__plugin_serena_serena__search_for_pattern({
  pattern: "innerHTML|dangerouslySetInnerHTML|v-html",
  file_mask: "*.ts|*.tsx|*.vue"
})
```

## Verification Checklist

### SQL Injection (A03:2021 - Injection)

- [ ] Prepared statement or ORM parameterized query used
- [ ] Input validation and escape handling for raw SQL usage
- [ ] User input not directly concatenated into queries
- [ ] NoSQL injection prevention (MongoDB, etc.)

### XSS (A03:2021 - Injection)

- [ ] User input sanitized before rendering
- [ ] Minimize `innerHTML`, `dangerouslySetInnerHTML`, `v-html` usage
- [ ] Sanitization library (e.g., DOMPurify) used
- [ ] Content-Security-Policy header configured

### Authentication/Authorization (A01:2021 - Broken Access Control, A07:2021 - Identification and Authentication Failures)

- [ ] JWT token validation is correct (signature, expiration)
- [ ] Authentication check on all protected endpoints
- [ ] Role/Permission based access control
- [ ] Token expiration time is appropriate (not too long)
- [ ] Proper security handling for refresh tokens

### Sensitive Information Exposure (A02:2021 - Cryptographic Failures)

- [ ] API keys, passwords, secrets managed via environment variables
- [ ] `.env` file included in `.gitignore`
- [ ] No sensitive information (passwords, tokens, PII) in logs
- [ ] No internal information exposure in error responses

### CSRF (A01:2021 - Broken Access Control)

- [ ] CSRF token on state-changing requests (POST, PUT, DELETE)
- [ ] SameSite cookie attribute set (Strict or Lax)
- [ ] CORS configuration is secure (minimize wildcard usage)

### Input Validation (A03:2021 - Injection)

- [ ] Validation on all user inputs
- [ ] Type validation, length limits, allowed character restrictions
- [ ] Whitelist-based validation (avoid blacklist approach)
- [ ] Server-side validation (client-side validation alone is insufficient)

### Encryption (A02:2021 - Cryptographic Failures)

- [ ] Passwords hashed with bcrypt, argon2, etc. (no MD5, SHA1)
- [ ] HTTPS enforced
- [ ] Sensitive data encrypted at rest
- [ ] Salt used (for password hashing)

### Error Message Security (A05:2021 - Security Misconfiguration)

- [ ] Error messages do not expose internal structure
- [ ] Stack traces not exposed in production
- [ ] Generic error messages used (minimize specific information)

### Rate Limiting (A04:2021 - Insecure Design)

- [ ] Rate limiting for brute force prevention
- [ ] Login attempt limits
- [ ] API call limits (DDoS prevention)

### Dependency Security (A06:2021 - Vulnerable and Outdated Components)

- [ ] Verified with `npm audit` or `yarn audit`
- [ ] No packages with known vulnerabilities
- [ ] Unnecessary dependencies removed
- [ ] Regular dependency updates

### Other Security

- [ ] Session fixation prevention
- [ ] Clickjacking prevention (X-Frame-Options header)
- [ ] MIME sniffing prevention (X-Content-Type-Options header)
- [ ] XXE (XML External Entity) prevention

## TypeScript Code Examples

### SQL Injection Prevention

```typescript
// ✅ GOOD: Prepared statement 사용 (TypeORM)
async function getUserByEmail(email: string): Promise<User> {
  return await userRepository.findOne({
    where: { email } // Parameterized query
  });
}

// ✅ GOOD: Prepared statement 사용 (Raw SQL)
async function getUserByEmail(email: string): Promise<User> {
  const [rows] = await db.execute(
    'SELECT * FROM users WHERE email = ?', // ? placeholder
    [email] // 파라미터로 전달
  );
  return rows[0];
}

// ❌ BAD: SQL Injection 취약
async function getUserByEmail(email: string): Promise<User> {
  const query = `SELECT * FROM users WHERE email = '${email}'`; // ❌ 직접 연결
  const [rows] = await db.execute(query);
  return rows[0];
}
```

### XSS Prevention

```typescript
// ✅ GOOD: React는 기본적으로 escape (안전)
function UserProfile({ userName }: { userName: string }) {
  return <div>{userName}</div>; // ✅ 자동 escape
}

// ✅ GOOD: Sanitization 라이브러리 사용
import DOMPurify from 'dompurify';

function UserBio({ bio }: { bio: string }) {
  const cleanBio = DOMPurify.sanitize(bio); // ✅ Sanitize
  return <div dangerouslySetInnerHTML={{ __html: cleanBio }} />;
}

// ❌ BAD: XSS 취약
function UserBio({ bio }: { bio: string }) {
  return <div dangerouslySetInnerHTML={{ __html: bio }} />; // ❌ Sanitize 없음
}
```

### Authentication/Authorization

```typescript
// ✅ GOOD: JWT 검증
import jwt from 'jsonwebtoken';

function verifyToken(token: string): TokenPayload {
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET) as TokenPayload;
    return decoded;
  } catch (error) {
    throw new UnauthorizedError('Invalid token');
  }
}

// ✅ GOOD: 권한 체크 미들웨어
function requireAdmin(req: Request, res: Response, next: NextFunction) {
  const user = req.user;

  if (!user || user.role !== 'admin') {
    return res.status(403).json({ error: 'Forbidden' });
  }

  next();
}

// ❌ BAD: 인증 없이 민감 데이터 접근
app.get('/admin/users', async (req, res) => {
  // ❌ 권한 체크 없음
  const users = await userRepository.find();
  res.json(users);
});
```

### Sensitive Information Protection

```typescript
// ✅ GOOD: 환경변수 사용
const jwtSecret = process.env.JWT_SECRET;
const apiKey = process.env.API_KEY;

// ✅ GOOD: 로그에서 민감 정보 제거
function sanitizeLog(obj: any): any {
  const sanitized = { ...obj };
  delete sanitized.password;
  delete sanitized.token;
  delete sanitized.apiKey;
  return sanitized;
}

console.log('User login:', sanitizeLog(user));

// ❌ BAD: 하드코딩
const jwtSecret = 'my-super-secret-key'; // ❌ 하드코딩
const apiKey = 'sk-1234567890abcdef'; // ❌ 하드코딩

// ❌ BAD: 로그에 민감 정보
console.log('User login:', user); // password, token 포함
```

### CSRF Prevention

```typescript
// ✅ GOOD: CSRF 토큰 사용 (Express)
import csrf from 'csurf';

const csrfProtection = csrf({ cookie: true });

app.post('/api/users', csrfProtection, async (req, res) => {
  const user = await createUser(req.body);
  res.json(user);
});

// ✅ GOOD: SameSite 쿠키 설정
res.cookie('token', jwtToken, {
  httpOnly: true,
  secure: true,
  sameSite: 'strict' // ✅ CSRF 방지
});

// ❌ BAD: CSRF 보호 없음
app.post('/api/users', async (req, res) => {
  // ❌ CSRF 토큰 검증 없음
  const user = await createUser(req.body);
  res.json(user);
});
```

### Input Validation

```typescript
// ✅ GOOD: 입력 검증
import { z } from 'zod';

const CreateUserSchema = z.object({
  email: z.string().email().max(255),
  password: z.string().min(8).max(100),
  age: z.number().int().min(0).max(150)
});

function createUser(data: unknown) {
  const validated = CreateUserSchema.parse(data); // ✅ 검증
  return userRepository.create(validated);
}

// ❌ BAD: 입력 검증 없음
function createUser(data: any) {
  return userRepository.create(data); // ❌ 검증 없음
}
```

### Password Hashing

```typescript
// ✅ GOOD: bcrypt 사용
import bcrypt from 'bcrypt';

async function hashPassword(password: string): Promise<string> {
  const saltRounds = 10;
  return await bcrypt.hash(password, saltRounds); // ✅ bcrypt
}

async function comparePassword(password: string, hash: string): Promise<boolean> {
  return await bcrypt.compare(password, hash);
}

// ❌ BAD: MD5/SHA1 사용 (취약)
import crypto from 'crypto';

function hashPassword(password: string): string {
  return crypto.createHash('md5').update(password).digest('hex'); // ❌ MD5는 안전하지 않음
}
```

### Rate Limiting

```typescript
// ✅ GOOD: Rate limiting (Express)
import rateLimit from 'express-rate-limit';

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // Max 5 attempts
  message: 'Too many login attempts, please try again later'
});

app.post('/api/auth/login', loginLimiter, async (req, res) => {
  // Login logic
});

// ❌ BAD: Rate limiting 없음
app.post('/api/auth/login', async (req, res) => {
  // ❌ Vulnerable to brute force attacks
});
```

## Actual Verification Procedure

1. **Systematically verify 10 security items with Sequential Thinking**
   - SQL Injection, XSS, Authentication/Authorization, Sensitive Information Exposure, CSRF, Input Validation, Encryption, Error Messages, Rate Limiting, Dependency Security

2. **Search security risk patterns with Serena**
   - Search for hardcoded secrets, raw SQL, innerHTML, dangerouslySetInnerHTML

3. **Check past security issues in Serena memory**
   - Verify past vulnerabilities in `security_incidents.md`
   - Confirm the same patterns are not recurring

4. **Verify dependency security**
   ```bash
   npm audit
   # or
   yarn audit
   ```

5. **Document verification results**
   - Classify discovered vulnerabilities by severity (Critical, High, Medium, Low)
   - Provide fix recommendations for each vulnerability
   - Provide OWASP Top 10 reference links
