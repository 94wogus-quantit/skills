# JIRA Requirements Validation Guide

## Goal

Verify that all Acceptance Criteria and requirements from the JIRA ticket are implemented in the MR code.

## Sequential Thinking MCP Examples

### Example 1: Acceptance Criteria 1 Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "JIRA Acceptance Criteria 1: '사용자는 이메일로 로그인할 수 있어야 한다' - 이 요구사항이 구현되었는가? 이메일 입력 필드, 로그인 API 호출, 인증 로직이 모두 포함되었는가?",
  thoughtNumber: 1,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

### Example 2: Acceptance Criteria 2 Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "JIRA Acceptance Criteria 2: '비밀번호는 최소 8자 이상이어야 한다' - 검증 로직이 있는가? 프론트엔드와 백엔드 모두에서 검증하는가? 에러 메시지가 명확한가?",
  thoughtNumber: 2,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

### Example 3: Edge Case Requirements Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "JIRA에 명시된 Edge Case: '잘못된 비밀번호 5회 입력 시 계정 잠금' - 이 요구사항이 구현되었는가? 시도 횟수 추적, 잠금 로직, 잠금 해제 방법이 있는가?",
  thoughtNumber: 3,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

### Example 4: Non-Functional Requirements Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "JIRA 비기능적 요구사항: '로그인 API 응답 시간은 500ms 이하여야 한다' - 성능 최적화가 되었는가? 캐싱, 인덱스, 쿼리 최적화가 적용되었는가?",
  thoughtNumber: 4,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

## Atlassian MCP Examples

### Example 1: Fetch JIRA Issue

```typescript
const issue = await mcp__plugin_atlassian_atlassian__jira_get_issue({
  issue_key: 'PROJ-123'
})
```

### Example 2: Search JIRA Issues

```typescript
const issues = await mcp__plugin_atlassian_atlassian__jira_search({
  jql: "project = PROJ AND status = 'In Progress'"
})
```

### Example 3: Add JIRA Comment

```typescript
await mcp__plugin_atlassian_atlassian__jira_add_comment({
  issue_key: 'PROJ-123',
  comment: 'MR 리뷰 완료: AC 모두 충족됨'
})
```

## Serena MCP Examples

### Example 1: Verify Code Implementation for Requirements

```typescript
await mcp__plugin_serena_serena__find_symbol({
  name_path_pattern: "login",
  substring_matching: true
})
```

### Example 2: Search Related Test Files

```typescript
await mcp__plugin_serena_serena__find_file({
  file_mask: "login*.test.ts",
  relative_path: "."
})
```

### Example 3: Search Patterns Related to Requirements

```typescript
await mcp__plugin_serena_serena__search_for_pattern({
  substring_pattern: "password.*validation|email.*login",
  paths_include_glob: "**/*.ts"
})
```

## Verification Checklist

### Acceptance Criteria Fulfillment

- [ ] All Acceptance Criteria from JIRA ticket are implemented
- [ ] Code clearly exists corresponding to each Acceptance Criteria
- [ ] All conditions specified in AC are implemented as code
- [ ] UI/UX requirements specified in AC are reflected

### Functional Requirements Fulfillment

- [ ] All features described in JIRA Description are implemented
- [ ] Required and optional features are distinguished and implemented
- [ ] User story scenarios are implemented as code
- [ ] All required API endpoints are implemented

### Edge Cases and Exception Handling

- [ ] Edge cases specified in JIRA are handled
- [ ] All error scenarios are implemented
- [ ] Error messages for exceptional situations are clear
- [ ] Fallback logic is appropriately implemented

### Constraint Compliance

- [ ] Technical constraints specified in JIRA are followed (e.g., specific library, specific API version)
- [ ] Performance requirements are met (e.g., response time, throughput)
- [ ] Security requirements are met (e.g., authentication method, encryption)
- [ ] Compatibility requirements are met (e.g., browser support, mobile responsiveness)

### Test Requirements

- [ ] Test scenarios specified in JIRA are implemented
- [ ] Test cases exist corresponding to each AC
- [ ] Tests for edge cases are written
- [ ] Integration/E2E tests validate requirements

### Documentation Requirements

- [ ] Documents required by JIRA are written (API docs, user guide, etc.)
- [ ] Code comments clearly explain requirements
- [ ] README or CHANGELOG updates are completed if needed

## TypeScript Code Examples

### Example: Implementing JIRA AC as Code

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

### Test Code Corresponding to JIRA AC

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
    for (let i = 0; i < 5; i++) {
      try {
        await authService.authenticateUser('user@example.com', 'wrongpassword');
      } catch (error) {
        // Expected to fail
      }
    }

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

    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    expect(decoded.userId).toBe('123');
    expect(decoded.email).toBe('user@example.com');
  });
});
```

### Edge Case Handling Example

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

    // ... rest of logic
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

## Actual Verification Procedure

1. **Extract JIRA issue ID from branch name**
   ```typescript
   // e.g., feature/PROJ-123-add-login -> PROJ-123
   const issueId = extractJiraId(branchName);
   ```

2. **Fetch JIRA issue via Atlassian MCP**
   ```typescript
   const issue = await mcp__plugin_atlassian_atlassian__jira_get_issue({
     issue_key: issueId
   });
   ```

3. **Extract and parse Acceptance Criteria**
   ```typescript
   const acceptanceCriteria = parseAcceptanceCriteria(issue.description);
   // e.g., ["사용자는 이메일로 로그인할 수 있어야 한다", ...]
   ```

4. **Verify each AC with Sequential Thinking**
   - Step-by-step code implementation verification for each AC
   - Systematically verify if any ACs are missing

5. **Confirm related code implementation with Serena**
   - Find AC-related functions/classes with `mcp__plugin_serena_serena__find_symbol()`
   - Confirm requirements are implemented as code

6. **Check test code**
   - Verify test cases exist corresponding to each AC
   - Verify edge case tests are written

7. **Document verification results**
   - Clearly distinguish fulfilled and unfulfilled ACs
   - Provide recommended implementation direction for missing requirements
   - Record verification results with JIRA issue links
