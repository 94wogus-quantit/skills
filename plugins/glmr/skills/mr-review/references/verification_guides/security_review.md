# 보안 검증 가이드

## 목표

OWASP Top 10 및 일반적인 보안 취약점을 체계적으로 검증합니다.

## Sequential Thinking MCP 예시

### 예시 1: SQL Injection 검증

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "SQL Injection 취약점: 사용자 입력이 직접 SQL 쿼리에 사용되는가? Prepared statement 또는 ORM의 parameterized query를 사용하는가? raw query 사용 시 입력 검증이 충분한가?",
  thoughtNumber: 1,
  totalThoughts: 10,
  nextThoughtNeeded: true
})
```

### 예시 2: XSS 검증

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "XSS 취약점: 사용자 입력이 렌더링 전에 sanitize되는가? innerHTML 대신 textContent를 사용하는가? React/Vue는 기본적으로 escape하지만, dangerouslySetInnerHTML이나 v-html 사용 시 검증이 있는가?",
  thoughtNumber: 2,
  totalThoughts: 10,
  nextThoughtNeeded: true
})
```

### 예시 3: 인증/인가 검증

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "인증/인가: JWT 토큰 검증이 올바른가? 권한 체크가 모든 보호된 엔드포인트에 있는가? Role-based 또는 Permission-based 접근 제어가 적절한가? 토큰 만료 시간이 적절한가?",
  thoughtNumber: 3,
  totalThoughts: 10,
  nextThoughtNeeded: true
})
```

### 예시 4: 민감 정보 노출 검증

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "민감 정보 노출: API 키, 비밀번호, JWT secret, 토큰이 하드코딩되지 않았는가? 환경변수 사용이 적절한가? 로그에 민감 정보(비밀번호, 토큰, 개인정보)가 남지 않는가? Git에 .env 파일이 커밋되지 않았는가?",
  thoughtNumber: 4,
  totalThoughts: 10,
  nextThoughtNeeded: true
})
```

### 예시 5: CSRF 검증

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "CSRF 보호: 상태 변경 요청(POST, PUT, DELETE)에 CSRF 토큰이 있는가? SameSite 쿠키 속성이 적절히 설정되었는가? CORS 설정이 안전한가?",
  thoughtNumber: 5,
  totalThoughts: 10,
  nextThoughtNeeded: true
})
```

### 예시 6: 입력 검증

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "입력 검증: 모든 사용자 입력에 대한 validation이 있는가? 타입 검증, 길이 제한, 허용 문자 제한이 적절한가? 화이트리스트 방식으로 검증하는가?",
  thoughtNumber: 6,
  totalThoughts: 10,
  nextThoughtNeeded: true
})
```

### 예시 7: 암호화

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "암호화: 비밀번호가 bcrypt, argon2 등 안전한 해싱 알고리즘으로 저장되는가? HTTPS 사용이 강제되는가? 민감 데이터 전송 시 암호화가 되는가?",
  thoughtNumber: 7,
  totalThoughts: 10,
  nextThoughtNeeded: true
})
```

### 예시 8: 에러 메시지 보안

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "에러 메시지 보안: 에러 메시지가 내부 구조나 민감 정보를 노출하지 않는가? 프로덕션 환경에서 스택 트레이스가 노출되지 않는가?",
  thoughtNumber: 8,
  totalThoughts: 10,
  nextThoughtNeeded: true
})
```

### 예시 9: Rate Limiting

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "Rate Limiting: 브루트 포스 공격 방지를 위한 rate limiting이 있는가? 로그인, API 호출에 적절한 제한이 설정되었는가?",
  thoughtNumber: 9,
  totalThoughts: 10,
  nextThoughtNeeded: true
})
```

### 예시 10: 의존성 보안

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "의존성 보안: 알려진 취약점이 있는 패키지를 사용하지 않는가? npm audit, Snyk 등으로 검증되었는가? 불필요한 의존성이 없는가?",
  thoughtNumber: 10,
  totalThoughts: 10,
  nextThoughtNeeded: false
})
```

## Serena MCP 예시

### 예시 1: 보안 관련 패턴 검색 (하드코딩된 secrets)

```typescript
await mcp__plugin_serena_serena__search_for_pattern({
  pattern: "API_KEY|PASSWORD|SECRET|token|private.*key",
  file_mask: "*.ts"
})
```

### 예시 2: 과거 보안 이슈 확인

```typescript
await mcp__plugin_serena_serena__read_memory({
  memory_file_name: "security_incidents.md"
})
```

### 예시 3: SQL Injection 위험 패턴 검색

```typescript
await mcp__plugin_serena_serena__search_for_pattern({
  pattern: "query.*\\+|execute.*\\$\\{|raw.*sql",
  file_mask: "*.ts"
})
```

### 예시 4: XSS 위험 패턴 검색

```typescript
await mcp__plugin_serena_serena__search_for_pattern({
  pattern: "innerHTML|dangerouslySetInnerHTML|v-html",
  file_mask: "*.ts|*.tsx|*.vue"
})
```

## 검증 항목 체크리스트

### SQL Injection (A03:2021 - Injection)

- [ ] Prepared statement 또는 ORM parameterized query 사용
- [ ] Raw SQL 사용 시 입력 검증 및 escape 처리
- [ ] 사용자 입력이 직접 쿼리에 연결되지 않음
- [ ] NoSQL injection 방지 (MongoDB 등)

### XSS (A03:2021 - Injection)

- [ ] 사용자 입력이 렌더링 전에 sanitize됨
- [ ] `innerHTML`, `dangerouslySetInnerHTML`, `v-html` 사용 최소화
- [ ] DOMPurify 등 sanitization 라이브러리 사용
- [ ] Content-Security-Policy 헤더 설정

### 인증/인가 (A01:2021 - Broken Access Control, A07:2021 - Identification and Authentication Failures)

- [ ] JWT 토큰 검증이 올바름 (signature, expiration)
- [ ] 모든 보호된 엔드포인트에 인증 체크
- [ ] Role/Permission 기반 접근 제어
- [ ] 토큰 만료 시간이 적절함 (너무 길지 않음)
- [ ] Refresh token 사용 시 적절한 보안 처리

### 민감 정보 노출 (A02:2021 - Cryptographic Failures)

- [ ] API 키, 비밀번호, secret이 환경변수로 관리됨
- [ ] `.env` 파일이 `.gitignore`에 포함됨
- [ ] 로그에 민감 정보(비밀번호, 토큰, 개인정보) 없음
- [ ] 에러 응답에 내부 정보 노출 없음

### CSRF (A01:2021 - Broken Access Control)

- [ ] 상태 변경 요청(POST, PUT, DELETE)에 CSRF 토큰
- [ ] SameSite 쿠키 속성 설정 (Strict 또는 Lax)
- [ ] CORS 설정이 안전함 (와일드카드 사용 최소화)

### 입력 검증 (A03:2021 - Injection)

- [ ] 모든 사용자 입력에 validation
- [ ] 타입 검증, 길이 제한, 허용 문자 제한
- [ ] 화이트리스트 방식 검증 (블랙리스트 방식 지양)
- [ ] 서버 측 검증 (클라이언트 검증만으로 부족)

### 암호화 (A02:2021 - Cryptographic Failures)

- [ ] 비밀번호가 bcrypt, argon2 등으로 해싱됨 (MD5, SHA1 사용 금지)
- [ ] HTTPS 사용 강제
- [ ] 민감 데이터 저장 시 암호화
- [ ] Salt 사용 (비밀번호 해싱 시)

### 에러 메시지 보안 (A05:2021 - Security Misconfiguration)

- [ ] 에러 메시지가 내부 구조 노출 방지
- [ ] 프로덕션 환경에서 스택 트레이스 비노출
- [ ] Generic 에러 메시지 사용 (구체적인 정보 최소화)

### Rate Limiting (A04:2021 - Insecure Design)

- [ ] 브루트 포스 방지를 위한 rate limiting
- [ ] 로그인 시도 제한
- [ ] API 호출 제한 (DDoS 방지)

### 의존성 보안 (A06:2021 - Vulnerable and Outdated Components)

- [ ] `npm audit` 또는 `yarn audit`로 검증됨
- [ ] 알려진 취약점이 있는 패키지 사용 안 함
- [ ] 불필요한 의존성 제거
- [ ] 정기적인 의존성 업데이트

### 기타 보안

- [ ] Session fixation 방지
- [ ] Clickjacking 방지 (X-Frame-Options 헤더)
- [ ] MIME sniffing 방지 (X-Content-Type-Options 헤더)
- [ ] XXE (XML External Entity) 방지

## TypeScript 코드 예시

### SQL Injection 방지

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

### XSS 방지

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

### 인증/인가

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

### 민감 정보 보호

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

### CSRF 방지

```typescript
// ✅ GOOD: CSRF 토큰 사용 (Express)
import csrf from 'csurf';

const csrfProtection = csrf({ cookie: true });

app.post('/api/users', csrfProtection, async (req, res) => {
  // CSRF 토큰 검증 완료
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

### 입력 검증

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

### 비밀번호 해싱

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
  windowMs: 15 * 60 * 1000, // 15분
  max: 5, // 최대 5번 시도
  message: 'Too many login attempts, please try again later'
});

app.post('/api/auth/login', loginLimiter, async (req, res) => {
  // 로그인 로직
});

// ❌ BAD: Rate limiting 없음
app.post('/api/auth/login', async (req, res) => {
  // ❌ 브루트 포스 공격에 취약
});
```

## 실제 검증 절차

1. **Sequential Thinking으로 10가지 보안 항목 체계적 검증**
   - SQL Injection, XSS, 인증/인가, 민감 정보 노출, CSRF, 입력 검증, 암호화, 에러 메시지, Rate Limiting, 의존성 보안

2. **Serena로 보안 위험 패턴 검색**
   - 하드코딩된 secrets, raw SQL, innerHTML, dangerouslySetInnerHTML 검색

3. **Serena memory에서 과거 보안 이슈 확인**
   - `security_incidents.md`에서 과거 보안 취약점 확인
   - 동일한 패턴이 재발하지 않았는지 검증

4. **의존성 보안 검증**
   ```bash
   npm audit
   # 또는
   yarn audit
   ```

5. **검증 결과 문서화**
   - 발견된 보안 취약점을 severity 별로 분류 (Critical, High, Medium, Low)
   - 각 취약점에 대한 수정 방법 제시
   - OWASP Top 10 참조 링크 제공
