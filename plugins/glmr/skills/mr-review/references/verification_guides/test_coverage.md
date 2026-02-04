# Test Coverage Evaluation Guide

## Goal

Evaluate whether sufficient tests have been written for the changed code.

## Sequential Thinking MCP Examples

### Example 1: Unit Test Existence Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "새로운 함수 createUser()에 대한 단위 테스트가 있는가? 성공 케이스, 실패 케이스, Edge case를 모두 테스트하는가? 각 테스트 케이스가 독립적으로 실행 가능한가?",
  thoughtNumber: 1,
  totalThoughts: 7,
  nextThoughtNeeded: true
})
```

### Example 2: Edge Case Test Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "Edge Case 테스트: null, undefined, 빈 배열, 빈 문자열, 0, -1 등 특수 값에 대한 테스트가 있는가? Boundary 조건(최소값, 최대값)이 테스트되는가?",
  thoughtNumber: 2,
  totalThoughts: 7,
  nextThoughtNeeded: true
})
```

### Example 3: Error Case Test Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "에러 케이스 테스트: 예외 상황(네트워크 에러, DB 에러, validation 실패)이 올바르게 테스트되는가? 에러 메시지가 명확한가? 에러 핸들링이 적절한가?",
  thoughtNumber: 3,
  totalThoughts: 7,
  nextThoughtNeeded: true
})
```

### Example 4: Integration Test Necessity Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "통합 테스트 필요성: 여러 모듈이 함께 동작하는 기능인가? API 엔드포인트의 전체 flow가 테스트되는가? 데이터베이스와의 연동이 테스트되는가?",
  thoughtNumber: 4,
  totalThoughts: 7,
  nextThoughtNeeded: true
})
```

### Example 5: Mock/Stub Usage Appropriateness Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "Mock/Stub 사용: 외부 의존성(DB, API, File System)이 적절히 mocking되었는가? Mock이 과도하게 사용되어 실제 동작과 괴리가 발생하지 않는가?",
  thoughtNumber: 5,
  totalThoughts: 7,
  nextThoughtNeeded: true
})
```

### Example 6: Test Readability and Maintainability Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "테스트 품질: 테스트 이름이 명확한가? Given-When-Then 패턴을 따르는가? 테스트가 독립적이고 재실행 가능한가? 테스트가 너무 복잡하지 않은가?",
  thoughtNumber: 6,
  totalThoughts: 7,
  nextThoughtNeeded: true
})
```

### Example 7: Coverage Metric Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "커버리지 메트릭: 코드 커버리지가 프로젝트 기준(예: 80%)을 충족하는가? 중요한 비즈니스 로직이 100% 커버되는가? 커버리지 도구(Jest, Istanbul)가 적절히 사용되는가?",
  thoughtNumber: 7,
  totalThoughts: 7,
  nextThoughtNeeded: false
})
```

## Serena MCP Examples

### Example 1: Search Test Files

```typescript
await mcp__plugin_serena_serena__find_file({
  file_mask: "*.test.ts|*.spec.ts|*.test.tsx|*.spec.tsx",
  relative_path: "."
})
```

### Example 2: Read Test Pattern Memory

```typescript
await mcp__plugin_serena_serena__read_memory({
  memory_file_name: "testing_patterns.md"
})
```

### Example 3: Find Untested Functions

```typescript
await mcp__plugin_serena_serena__find_symbol({
  symbol_name: "exported.*function.*without.*test"
})
```

### Example 4: Find Test File for Specific File

```typescript
// user.service.ts -> user.service.test.ts
await mcp__plugin_serena_serena__find_file({
  file_mask: "user.service.test.ts|user.service.spec.ts",
  relative_path: "."
})
```

## Verification Checklist

### Unit Tests

- [ ] Unit tests exist for all new functions/methods
- [ ] All public functions are tested
- [ ] Private functions are indirectly tested through public functions
- [ ] Core logic of each function is tested

### Test Case Completeness

- [ ] **Success cases (Happy Path)**: Normal input and output tested
- [ ] **Failure cases (Unhappy Path)**: Error scenarios tested
- [ ] **Edge cases**: null, undefined, empty values, boundary values tested
- [ ] **Boundary conditions**: Minimum and maximum values tested

### Integration Tests

- [ ] Features involving multiple modules working together are tested
- [ ] Full flow of API endpoints is tested
- [ ] Database integration tested (when applicable)
- [ ] External API calls tested (when applicable)

### E2E Tests (End-to-End)

- [ ] User scenario-based tests (when applicable)
- [ ] Frontend and backend integration tests (when applicable)
- [ ] E2E tests for critical business flows

### Test Quality

- [ ] Test names are clear (should/it describes what is tested)
- [ ] Given-When-Then pattern followed
- [ ] Each test verifies only one feature (Single Responsibility)
- [ ] Tests are independent (no dependencies between tests)
- [ ] Tests are re-runnable (Idempotent)
- [ ] Tests are fast (unit tests in milliseconds)

### Mock/Stub Usage

- [ ] External dependencies (DB, API, File System) are mocked
- [ ] Mocking is not excessive (similar to actual behavior)
- [ ] Mock objects are clearly defined
- [ ] Spies used for function call verification (when applicable)

### Coverage Metrics

- [ ] Code coverage meets project standards (e.g., 80% or higher)
- [ ] Statement coverage (all statements executed)
- [ ] Branch coverage (all branch conditions tested)
- [ ] Function coverage (all functions called)
- [ ] Line coverage (all code lines executed)

### Test Maintainability

- [ ] Test code is readable
- [ ] Duplicate code is minimized (using beforeEach, helper functions)
- [ ] Constants used instead of magic numbers/strings
- [ ] Test descriptions are clear

## TypeScript Code Examples

### Unit Tests - Success/Failure/Edge Cases

```typescript
// user.service.ts
export class UserService {
  async createUser(email: string, password: string): Promise<User> {
    if (!email || !password) {
      throw new ValidationError('Email and password are required');
    }

    if (password.length < 8) {
      throw new ValidationError('Password must be at least 8 characters');
    }

    const existingUser = await this.userRepository.findByEmail(email);
    if (existingUser) {
      throw new DuplicateEmailError('Email already exists');
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    return this.userRepository.create({ email, password: hashedPassword });
  }
}

// ✅ GOOD: 성공/실패/Edge Case 테스트
// user.service.test.ts
describe('UserService', () => {
  let userService: UserService;
  let mockUserRepository: jest.Mocked<UserRepository>;

  beforeEach(() => {
    mockUserRepository = {
      findByEmail: jest.fn(),
      create: jest.fn()
    } as any;

    userService = new UserService(mockUserRepository);
  });

  // Success cases (Happy Path)
  describe('createUser - success cases', () => {
    it('should create user with valid email and password', async () => {
      // Given
      mockUserRepository.findByEmail.mockResolvedValue(null);
      mockUserRepository.create.mockResolvedValue({ id: '1', email: 'user@example.com' } as User);

      // When
      const user = await userService.createUser('user@example.com', 'password123');

      // Then
      expect(user).toBeDefined();
      expect(user.email).toBe('user@example.com');
      expect(mockUserRepository.create).toHaveBeenCalledTimes(1);
    });
  });

  // Failure cases (Unhappy Path)
  describe('createUser - error cases', () => {
    it('should throw ValidationError when email is empty', async () => {
      // Given
      const email = '';
      const password = 'password123';

      // When & Then
      await expect(
        userService.createUser(email, password)
      ).rejects.toThrow(ValidationError);
    });

    it('should throw ValidationError when password is too short', async () => {
      // Given
      const email = 'user@example.com';
      const password = 'short'; // 5 chars (less than 8)

      // When & Then
      await expect(
        userService.createUser(email, password)
      ).rejects.toThrow('Password must be at least 8 characters');
    });

    it('should throw DuplicateEmailError when email already exists', async () => {
      // Given
      mockUserRepository.findByEmail.mockResolvedValue({ id: '1' } as User);

      // When & Then
      await expect(
        userService.createUser('user@example.com', 'password123')
      ).rejects.toThrow(DuplicateEmailError);
    });
  });

  // Edge Cases
  describe('createUser - edge cases', () => {
    it('should handle null email', async () => {
      await expect(
        userService.createUser(null as any, 'password123')
      ).rejects.toThrow(ValidationError);
    });

    it('should handle undefined password', async () => {
      await expect(
        userService.createUser('user@example.com', undefined as any)
      ).rejects.toThrow(ValidationError);
    });

    it('should accept password with exactly 8 characters', async () => {
      mockUserRepository.findByEmail.mockResolvedValue(null);
      mockUserRepository.create.mockResolvedValue({ id: '1' } as User);

      // Boundary condition: exactly 8 characters
      const user = await userService.createUser('user@example.com', '12345678');
      expect(user).toBeDefined();
    });
  });
});
```

### Integration Test Example

```typescript
// ✅ GOOD: API endpoint integration test
// auth.integration.test.ts
describe('POST /api/auth/login', () => {
  let app: Express;
  let testDb: TestDatabase;

  beforeAll(async () => {
    testDb = await setupTestDatabase();
    app = createApp(testDb);
  });

  afterAll(async () => {
    await testDb.cleanup();
  });

  it('should login with valid credentials and return JWT token', async () => {
    // Given: Create test user
    await testDb.users.create({
      email: 'user@example.com',
      password: await bcrypt.hash('password123', 10)
    });

    // When: Call login API
    const response = await request(app)
      .post('/api/auth/login')
      .send({
        email: 'user@example.com',
        password: 'password123'
      });

    // Then: Verify response
    expect(response.status).toBe(200);
    expect(response.body.token).toBeDefined();
    expect(typeof response.body.token).toBe('string');

    // Verify JWT token
    const decoded = jwt.verify(response.body.token, process.env.JWT_SECRET);
    expect(decoded.email).toBe('user@example.com');
  });

  it('should return 401 with invalid password', async () => {
    // Given
    await testDb.users.create({
      email: 'user@example.com',
      password: await bcrypt.hash('password123', 10)
    });

    // When: Login attempt with wrong password
    const response = await request(app)
      .post('/api/auth/login')
      .send({
        email: 'user@example.com',
        password: 'wrongpassword'
      });

    // Then
    expect(response.status).toBe(401);
    expect(response.body.error).toBe('Invalid credentials');
  });
});
```

### Given-When-Then Pattern

```typescript
// ✅ GOOD: Given-When-Then pattern
describe('calculateDiscount', () => {
  it('should apply 20% discount for premium users', () => {
    // Given: Premium user and product price
    const user = { role: 'premium' } as User;
    const price = 100;

    // When: Calculate discount
    const discountedPrice = calculateDiscount(user, price);

    // Then: 20% discount applied
    expect(discountedPrice).toBe(80);
  });
});

// ❌ BAD: Written without pattern
it('test discount', () => {
  expect(calculateDiscount({ role: 'premium' } as User, 100)).toBe(80);
});
```

### Mock Usage Example

```typescript
// ✅ GOOD: Using mocks to remove external dependencies
describe('PaymentService', () => {
  it('should process payment via Stripe', async () => {
    // Given: Mock Stripe API
    const mockStripe = {
      charges: {
        create: jest.fn().mockResolvedValue({
          id: 'ch_123',
          status: 'succeeded'
        })
      }
    };

    const paymentService = new PaymentService(mockStripe as any);

    // When
    const result = await paymentService.processPayment(100, 'usd');

    // Then
    expect(result.status).toBe('succeeded');
    expect(mockStripe.charges.create).toHaveBeenCalledWith({
      amount: 10000, // cents
      currency: 'usd'
    });
  });
});

// ❌ BAD: Calling actual Stripe API (slow and unstable)
describe('PaymentService', () => {
  it('should process payment via Stripe', async () => {
    const paymentService = new PaymentService(realStripe); // ❌ Real API
    const result = await paymentService.processPayment(100, 'usd');
    // Actual payment occurs, network dependency introduced
  });
});
```

### Test Independence Guarantee

```typescript
// ✅ GOOD: Each test is independent
describe('UserService', () => {
  let userService: UserService;

  beforeEach(() => {
    // New instance for each test
    userService = new UserService();
  });

  it('test 1', () => {
    userService.addUser('user1');
    expect(userService.getUserCount()).toBe(1);
  });

  it('test 2', () => {
    // Not affected by test 1 (independent)
    expect(userService.getUserCount()).toBe(0);
  });
});

// ❌ BAD: Dependencies between tests
describe('UserService', () => {
  const userService = new UserService(); // Shared instance

  it('test 1', () => {
    userService.addUser('user1');
    expect(userService.getUserCount()).toBe(1);
  });

  it('test 2', () => {
    // ❌ Affected by test 1 (dependency)
    expect(userService.getUserCount()).toBe(1); // user added in test 1
  });
});
```

## Actual Verification Procedure

1. **Check test files corresponding to changed files**
   - `user.service.ts` → `user.service.test.ts` or `user.service.spec.ts`
   - Search test files with Serena

2. **Verify test quality with Sequential Thinking**
   - Check existence of success/failure/edge case tests
   - Verify test readability, independence, and maintainability

3. **Check test patterns in Serena memory**
   - Check project test writing guidelines
   - Verify consistency with existing test patterns

4. **Check coverage metrics**
   ```bash
   npm test -- --coverage
   # or
   jest --coverage
   ```

5. **Document verification results**
   - List functions/files with missing tests
   - Highlight areas with low coverage
   - Suggest recommended test cases
