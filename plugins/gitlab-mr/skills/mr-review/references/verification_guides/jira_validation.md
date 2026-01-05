# JIRA 요구사항 검증 가이드

## 목표

JIRA 티켓의 Acceptance Criteria와 요구사항이 MR 코드에 모두 구현되었는지 검증합니다.

## Sequential Thinking MCP 예시

### 예시 1: Acceptance Criteria 1 검증

```typescript
await mcp__plugin_workflow-bundle_sequential-thinking__sequentialthinking({
  thought: "JIRA Acceptance Criteria 1: '사용자는 이메일로 로그인할 수 있어야 한다' - 이 요구사항이 구현되었는가? 이메일 입력 필드, 로그인 API 호출, 인증 로직이 모두 포함되었는가?",
  thoughtNumber: 1,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

### 예시 2: Acceptance Criteria 2 검증

```typescript
await mcp__plugin_workflow-bundle_sequential-thinking__sequentialthinking({
  thought: "JIRA Acceptance Criteria 2: '비밀번호는 최소 8자 이상이어야 한다' - 검증 로직이 있는가? 프론트엔드와 백엔드 모두에서 검증하는가? 에러 메시지가 명확한가?",
  thoughtNumber: 2,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

### 예시 3: Edge Case 요구사항 검증

```typescript
await mcp__plugin_workflow-bundle_sequential-thinking__sequentialthinking({
  thought: "JIRA에 명시된 Edge Case: '잘못된 비밀번호 5회 입력 시 계정 잠금' - 이 요구사항이 구현되었는가? 시도 횟수 추적, 잠금 로직, 잠금 해제 방법이 있는가?",
  thoughtNumber: 3,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

### 예시 4: 비기능적 요구사항 검증

```typescript
await mcp__plugin_workflow-bundle_sequential-thinking__sequentialthinking({
  thought: "JIRA 비기능적 요구사항: '로그인 API 응답 시간은 500ms 이하여야 한다' - 성능 최적화가 되었는가? 캐싱, 인덱스, 쿼리 최적화가 적용되었는가?",
  thoughtNumber: 4,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

## Atlassian MCP 예시

### 예시 1: JIRA 이슈 조회

```typescript
const issue = await mcp__plugin_atlassian_atlassian__jira_get_issue({
  issue_key: 'PROJ-123'
})
```

### 예시 2: JIRA 이슈 검색

```typescript
const issues = await mcp__plugin_atlassian_atlassian__jira_search({
  jql: "project = PROJ AND status = 'In Progress'"
})
```

### 예시 3: JIRA 코멘트 추가

```typescript
await mcp__plugin_atlassian_atlassian__jira_add_comment({
  issue_key: 'PROJ-123',
  comment: 'MR 리뷰 완료: AC 모두 충족됨'
})
```

## Serena MCP 예시

### 예시 1: 요구사항 관련 코드 구현 확인

```typescript
await mcp__plugin_serena_serena__find_symbol({
  name_path_pattern: "login",
  substring_matching: true
})
```

### 예시 2: 관련 테스트 파일 검색

```typescript
await mcp__plugin_serena_serena__find_file({
  file_mask: "login*.test.ts",
  relative_path: "."
})
```

### 예시 3: 요구사항 관련 패턴 검색

```typescript
await mcp__plugin_serena_serena__search_for_pattern({
  substring_pattern: "password.*validation|email.*login",
  paths_include_glob: "**/*.ts"
})
```

## 검증 항목 체크리스트

### Acceptance Criteria 충족

- [ ] JIRA 티켓의 모든 Acceptance Criteria가 구현됨
- [ ] 각 Acceptance Criteria에 대응하는 코드가 명확히 존재
- [ ] AC에 명시된 모든 조건이 코드로 구현됨
- [ ] AC에 명시된 UI/UX 요구사항이 반영됨

### 기능 요구사항 충족

- [ ] JIRA Description에 명시된 기능이 모두 구현됨
- [ ] 필수 기능과 선택 기능이 구분되어 구현됨
- [ ] 사용자 스토리의 시나리오가 코드로 구현됨
- [ ] 요구된 API 엔드포인트가 모두 구현됨

### Edge Case 및 예외 처리

- [ ] JIRA에 명시된 Edge Case가 처리됨
- [ ] 에러 시나리오가 모두 구현됨
- [ ] 예외 상황에 대한 에러 메시지가 명확함
- [ ] Fallback 로직이 적절히 구현됨

### 제약사항 준수

- [ ] JIRA에 명시된 기술적 제약사항 준수 (예: 특정 라이브러리 사용, 특정 API 버전)
- [ ] 성능 요구사항 준수 (예: 응답 시간, 처리량)
- [ ] 보안 요구사항 준수 (예: 인증 방식, 암호화)
- [ ] 호환성 요구사항 준수 (예: 브라우저 지원, 모바일 대응)

### 테스트 요구사항

- [ ] JIRA에 명시된 테스트 시나리오가 구현됨
- [ ] 각 AC에 대응하는 테스트 케이스가 존재
- [ ] Edge Case에 대한 테스트가 작성됨
- [ ] 통합 테스트/E2E 테스트가 요구사항을 검증함

### 문서화 요구사항

- [ ] JIRA에 요구된 문서가 작성됨 (API 문서, 사용자 가이드 등)
- [ ] 코드 주석이 요구사항을 명확히 설명함
- [ ] README 또는 CHANGELOG 업데이트가 필요한 경우 완료됨

## TypeScript 코드 예시

### JIRA AC를 코드로 구현하는 예시

**JIRA Acceptance Criteria:**
1. 사용자는 이메일과 비밀번호로 로그인할 수 있어야 한다
2. 비밀번호는 최소 8자 이상이어야 한다
3. 잘못된 비밀번호 5회 입력 시 계정이 잠긴다
4. 로그인 성공 시 JWT 토큰이 발급된다

```typescript
// ✅ GOOD: AC 1, 4 구현
// src/api/auth.controller.ts
export class AuthController {
  async login(req: Request, res: Response): Promise<void> {
    const { email, password } = req.body;

    // AC 1: 이메일과 비밀번호로 로그인
    const user = await this.authService.authenticateUser(email, password);

    // AC 4: JWT 토큰 발급
    const token = this.authService.generateJwtToken(user);

    res.json({ token, user });
  }
}

// ✅ GOOD: AC 2 구현
// src/validators/password.validator.ts
export function validatePassword(password: string): void {
  // AC 2: 비밀번호는 최소 8자 이상
  if (password.length < 8) {
    throw new ValidationError('Password must be at least 8 characters');
  }
}

// ✅ GOOD: AC 3 구현
// src/services/auth.service.ts
export class AuthService {
  private readonly MAX_LOGIN_ATTEMPTS = 5;

  async authenticateUser(email: string, password: string): Promise<User> {
    const user = await this.userRepository.findByEmail(email);

    if (!user) {
      throw new UserNotFoundError(email);
    }

    // AC 3: 계정 잠금 확인
    if (user.isLocked) {
      throw new AccountLockedError('Account is locked due to too many failed login attempts');
    }

    const isPasswordValid = await this.comparePassword(password, user.passwordHash);

    if (!isPasswordValid) {
      // AC 3: 잘못된 시도 횟수 증가
      user.failedLoginAttempts += 1;

      // AC 3: 5회 실패 시 계정 잠금
      if (user.failedLoginAttempts >= this.MAX_LOGIN_ATTEMPTS) {
        user.isLocked = true;
        await this.userRepository.save(user);
        throw new AccountLockedError('Account locked after 5 failed attempts');
      }

      await this.userRepository.save(user);
      throw new InvalidPasswordError('Invalid password');
    }

    // 로그인 성공 시 실패 횟수 리셋
    user.failedLoginAttempts = 0;
    await this.userRepository.save(user);

    return user;
  }

  generateJwtToken(user: User): string {
    // AC 4: JWT 토큰 생성
    return jwt.sign(
      { userId: user.id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: '24h' }
    );
  }
}
```

### JIRA AC에 대응하는 테스트 코드

```typescript
// ✅ GOOD: 각 AC에 대응하는 테스트 케이스
// src/services/auth.service.test.ts
describe('AuthService', () => {
  // AC 1: 이메일과 비밀번호로 로그인
  it('should authenticate user with valid email and password', async () => {
    const user = await authService.authenticateUser('user@example.com', 'password123');
    expect(user).toBeDefined();
    expect(user.email).toBe('user@example.com');
  });

  // AC 2: 비밀번호는 최소 8자 이상
  it('should reject password shorter than 8 characters', () => {
    expect(() => validatePassword('short')).toThrow('Password must be at least 8 characters');
  });

  it('should accept password with 8 or more characters', () => {
    expect(() => validatePassword('longpassword')).not.toThrow();
  });

  // AC 3: 잘못된 비밀번호 5회 입력 시 계정 잠금
  it('should lock account after 5 failed login attempts', async () => {
    // 5회 잘못된 비밀번호 입력
    for (let i = 0; i < 5; i++) {
      try {
        await authService.authenticateUser('user@example.com', 'wrongpassword');
      } catch (error) {
        // Expected to fail
      }
    }

    // 6번째 시도 시 계정 잠금 확인
    await expect(
      authService.authenticateUser('user@example.com', 'correctpassword')
    ).rejects.toThrow(AccountLockedError);
  });

  // AC 4: JWT 토큰 발급
  it('should generate JWT token on successful login', () => {
    const user = { id: '123', email: 'user@example.com' } as User;
    const token = authService.generateJwtToken(user);

    expect(token).toBeDefined();
    expect(typeof token).toBe('string');

    // 토큰 검증
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    expect(decoded.userId).toBe('123');
    expect(decoded.email).toBe('user@example.com');
  });
});
```

### Edge Case 처리 예시

**JIRA Edge Cases:**
- 이메일이 존재하지 않을 경우
- 계정이 이미 잠겨 있을 경우
- JWT secret이 설정되지 않은 경우

```typescript
// ✅ GOOD: Edge Case 처리
export class AuthService {
  async authenticateUser(email: string, password: string): Promise<User> {
    // Edge Case: 이메일이 존재하지 않을 경우
    const user = await this.userRepository.findByEmail(email);
    if (!user) {
      throw new UserNotFoundError(`User with email ${email} not found`);
    }

    // Edge Case: 계정이 이미 잠겨 있을 경우
    if (user.isLocked) {
      throw new AccountLockedError(
        'Account is locked. Please contact support to unlock.'
      );
    }

    // ... 나머지 로직
  }

  generateJwtToken(user: User): string {
    // Edge Case: JWT secret이 설정되지 않은 경우
    if (!process.env.JWT_SECRET) {
      throw new ConfigurationError('JWT_SECRET is not configured');
    }

    return jwt.sign(
      { userId: user.id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: '24h' }
    );
  }
}
```

## 실제 검증 절차

1. **브랜치명에서 JIRA 이슈 ID 추출**
   ```typescript
   // 예: feature/PROJ-123-add-login -> PROJ-123
   const issueId = extractJiraId(branchName);
   ```

2. **Atlassian MCP로 JIRA 이슈 조회**
   ```typescript
   const issue = await mcp__plugin_atlassian_atlassian__jira_get_issue({
     issue_key: issueId
   });
   ```

3. **Acceptance Criteria 추출 및 파싱**
   ```typescript
   const acceptanceCriteria = parseAcceptanceCriteria(issue.description);
   // 예: ["사용자는 이메일로 로그인할 수 있어야 한다", ...]
   ```

4. **Sequential Thinking으로 각 AC 검증**
   - 각 AC에 대해 단계별로 코드 구현 확인
   - 누락된 AC가 있는지 체계적 검증

5. **Serena로 관련 코드 구현 확인**
   - `mcp__plugin_serena_serena__find_symbol()`로 AC 관련 함수/클래스 찾기
   - 요구사항이 코드로 구현되었는지 확인

6. **테스트 코드 확인**
   - 각 AC에 대응하는 테스트 케이스가 있는지 확인
   - Edge Case 테스트가 작성되었는지 확인

7. **검증 결과 문서화**
   - 충족된 AC와 미충족 AC를 명확히 구분
   - 누락된 요구사항에 대한 권장 구현 방향 제시
   - JIRA 이슈 링크와 함께 검증 결과 기록
