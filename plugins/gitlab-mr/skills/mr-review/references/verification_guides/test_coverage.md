# 테스트 커버리지 평가 가이드

## 목표

변경된 코드에 대한 테스트가 충분히 작성되었는지 평가합니다.

## Sequential Thinking MCP 예시

### 예시 1: 단위 테스트 존재 여부 검증

```typescript
await mcp__plugin_sequential-thinking_sequential-thinking__sequentialthinking({
  thought: "새로운 함수 createUser()에 대한 단위 테스트가 있는가? 성공 케이스, 실패 케이스, Edge case를 모두 테스트하는가? 각 테스트 케이스가 독립적으로 실행 가능한가?",
  thoughtNumber: 1,
  totalThoughts: 7,
  nextThoughtNeeded: true
})
```

### 예시 2: Edge Case 테스트 검증

```typescript
await mcp__plugin_sequential-thinking_sequential-thinking__sequentialthinking({
  thought: "Edge Case 테스트: null, undefined, 빈 배열, 빈 문자열, 0, -1 등 특수 값에 대한 테스트가 있는가? Boundary 조건(최소값, 최대값)이 테스트되는가?",
  thoughtNumber: 2,
  totalThoughts: 7,
  nextThoughtNeeded: true
})
```

### 예시 3: 에러 케이스 테스트 검증

```typescript
await mcp__plugin_sequential-thinking_sequential-thinking__sequentialthinking({
  thought: "에러 케이스 테스트: 예외 상황(네트워크 에러, DB 에러, validation 실패)이 올바르게 테스트되는가? 에러 메시지가 명확한가? 에러 핸들링이 적절한가?",
  thoughtNumber: 3,
  totalThoughts: 7,
  nextThoughtNeeded: true
})
```

### 예시 4: 통합 테스트 필요성 검증

```typescript
await mcp__plugin_sequential-thinking_sequential-thinking__sequentialthinking({
  thought: "통합 테스트 필요성: 여러 모듈이 함께 동작하는 기능인가? API 엔드포인트의 전체 flow가 테스트되는가? 데이터베이스와의 연동이 테스트되는가?",
  thoughtNumber: 4,
  totalThoughts: 7,
  nextThoughtNeeded: true
})
```

### 예시 5: Mock/Stub 사용 적절성 검증

```typescript
await mcp__plugin_sequential-thinking_sequential-thinking__sequentialthinking({
  thought: "Mock/Stub 사용: 외부 의존성(DB, API, File System)이 적절히 mocking되었는가? Mock이 과도하게 사용되어 실제 동작과 괴리가 발생하지 않는가?",
  thoughtNumber: 5,
  totalThoughts: 7,
  nextThoughtNeeded: true
})
```

### 예시 6: 테스트 가독성 및 유지보수성 검증

```typescript
await mcp__plugin_sequential-thinking_sequential-thinking__sequentialthinking({
  thought: "테스트 품질: 테스트 이름이 명확한가? Given-When-Then 패턴을 따르는가? 테스트가 독립적이고 재실행 가능한가? 테스트가 너무 복잡하지 않은가?",
  thoughtNumber: 6,
  totalThoughts: 7,
  nextThoughtNeeded: true
})
```

### 예시 7: 커버리지 메트릭 검증

```typescript
await mcp__plugin_sequential-thinking_sequential-thinking__sequentialthinking({
  thought: "커버리지 메트릭: 코드 커버리지가 프로젝트 기준(예: 80%)을 충족하는가? 중요한 비즈니스 로직이 100% 커버되는가? 커버리지 도구(Jest, Istanbul)가 적절히 사용되는가?",
  thoughtNumber: 7,
  totalThoughts: 7,
  nextThoughtNeeded: false
})
```

## Serena MCP 예시

### 예시 1: 테스트 파일 검색

```typescript
await mcp__plugin_serena_serena__find_file({
  file_mask: "*.test.ts|*.spec.ts|*.test.tsx|*.spec.tsx",
  relative_path: "."
})
```

### 예시 2: 테스트 패턴 메모리 읽기

```typescript
await mcp__plugin_serena_serena__read_memory({
  memory_file_name: "testing_patterns.md"
})
```

### 예시 3: 테스트되지 않은 함수 찾기

```typescript
await mcp__plugin_serena_serena__find_symbol({
  symbol_name: "exported.*function.*without.*test"
})
```

### 예시 4: 특정 파일의 테스트 파일 찾기

```typescript
// user.service.ts -> user.service.test.ts 찾기
await mcp__plugin_serena_serena__find_file({
  file_mask: "user.service.test.ts|user.service.spec.ts",
  relative_path: "."
})
```

## 검증 항목 체크리스트

### 단위 테스트 (Unit Test)

- [ ] 모든 새 함수/메서드에 단위 테스트 존재
- [ ] Public 함수는 모두 테스트됨
- [ ] Private 함수는 Public 함수를 통해 간접적으로 테스트됨
- [ ] 각 함수의 핵심 로직이 테스트됨

### 테스트 케이스 완성도

- [ ] **성공 케이스 (Happy Path)**: 정상적인 입력과 출력 테스트
- [ ] **실패 케이스 (Unhappy Path)**: 에러 상황 테스트
- [ ] **Edge Case**: null, undefined, 빈 값, 경계 값 테스트
- [ ] **경계 조건 (Boundary Conditions)**: 최소값, 최대값 테스트

### 통합 테스트 (Integration Test)

- [ ] 여러 모듈이 함께 동작하는 기능 테스트
- [ ] API 엔드포인트의 전체 flow 테스트
- [ ] 데이터베이스 연동 테스트 (필요 시)
- [ ] 외부 API 호출 테스트 (필요 시)

### E2E 테스트 (End-to-End Test)

- [ ] 사용자 시나리오 기반 테스트 (필요 시)
- [ ] 프론트엔드와 백엔드 통합 테스트 (필요 시)
- [ ] 주요 비즈니스 플로우 E2E 테스트

### 테스트 품질

- [ ] 테스트 이름이 명확함 (should/it describes what is tested)
- [ ] Given-When-Then 패턴 준수
- [ ] 각 테스트가 하나의 기능만 검증 (Single Responsibility)
- [ ] 테스트가 독립적임 (테스트 간 의존성 없음)
- [ ] 테스트가 재실행 가능함 (Idempotent)
- [ ] 테스트가 빠름 (단위 테스트는 밀리초 단위)

### Mock/Stub 사용

- [ ] 외부 의존성(DB, API, File System)이 mocking됨
- [ ] Mock이 과도하지 않음 (실제 동작과 유사)
- [ ] Mock 객체가 명확하게 정의됨
- [ ] Spy를 사용하여 함수 호출 검증 (필요 시)

### 커버리지 메트릭

- [ ] 코드 커버리지가 프로젝트 기준 충족 (예: 80% 이상)
- [ ] Statement coverage (모든 문장 실행)
- [ ] Branch coverage (모든 분기 조건 테스트)
- [ ] Function coverage (모든 함수 호출)
- [ ] Line coverage (모든 코드 라인 실행)

### 테스트 유지보수성

- [ ] 테스트 코드가 읽기 쉬움
- [ ] 중복 코드가 최소화됨 (beforeEach, helper 함수 사용)
- [ ] Magic number/string 대신 상수 사용
- [ ] 테스트 설명이 명확함

## TypeScript 코드 예시

### 단위 테스트 - 성공/실패/Edge Case

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

  // 성공 케이스 (Happy Path)
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

  // 실패 케이스 (Unhappy Path)
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
      const password = 'short'; // 5자 (8자 미만)

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

  // Edge Case
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

      // 경계 조건: 정확히 8자
      const user = await userService.createUser('user@example.com', '12345678');
      expect(user).toBeDefined();
    });
  });
});
```

### 통합 테스트 예시

```typescript
// ✅ GOOD: API 엔드포인트 통합 테스트
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
    // Given: 테스트 사용자 생성
    await testDb.users.create({
      email: 'user@example.com',
      password: await bcrypt.hash('password123', 10)
    });

    // When: 로그인 API 호출
    const response = await request(app)
      .post('/api/auth/login')
      .send({
        email: 'user@example.com',
        password: 'password123'
      });

    // Then: 응답 검증
    expect(response.status).toBe(200);
    expect(response.body.token).toBeDefined();
    expect(typeof response.body.token).toBe('string');

    // JWT 토큰 검증
    const decoded = jwt.verify(response.body.token, process.env.JWT_SECRET);
    expect(decoded.email).toBe('user@example.com');
  });

  it('should return 401 with invalid password', async () => {
    // Given
    await testDb.users.create({
      email: 'user@example.com',
      password: await bcrypt.hash('password123', 10)
    });

    // When: 잘못된 비밀번호로 로그인 시도
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

### Given-When-Then 패턴

```typescript
// ✅ GOOD: Given-When-Then 패턴 사용
describe('calculateDiscount', () => {
  it('should apply 20% discount for premium users', () => {
    // Given: 프리미엄 사용자와 상품 가격
    const user = { role: 'premium' } as User;
    const price = 100;

    // When: 할인 계산
    const discountedPrice = calculateDiscount(user, price);

    // Then: 20% 할인 적용됨
    expect(discountedPrice).toBe(80);
  });
});

// ❌ BAD: 패턴 없이 작성
it('test discount', () => {
  expect(calculateDiscount({ role: 'premium' } as User, 100)).toBe(80);
});
```

### Mock 사용 예시

```typescript
// ✅ GOOD: Mock을 사용하여 외부 의존성 제거
describe('PaymentService', () => {
  it('should process payment via Stripe', async () => {
    // Given: Stripe API를 mocking
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

// ❌ BAD: 실제 Stripe API 호출 (느리고 불안정)
describe('PaymentService', () => {
  it('should process payment via Stripe', async () => {
    const paymentService = new PaymentService(realStripe); // ❌ 실제 API
    const result = await paymentService.processPayment(100, 'usd');
    // 실제 결제가 발생하고, 네트워크 의존성이 생김
  });
});
```

### 테스트 독립성 보장

```typescript
// ✅ GOOD: 각 테스트가 독립적
describe('UserService', () => {
  let userService: UserService;

  beforeEach(() => {
    // 각 테스트마다 새로운 인스턴스 생성
    userService = new UserService();
  });

  it('test 1', () => {
    userService.addUser('user1');
    expect(userService.getUserCount()).toBe(1);
  });

  it('test 2', () => {
    // test 1의 영향을 받지 않음 (독립적)
    expect(userService.getUserCount()).toBe(0);
  });
});

// ❌ BAD: 테스트 간 의존성 발생
describe('UserService', () => {
  const userService = new UserService(); // 공유 인스턴스

  it('test 1', () => {
    userService.addUser('user1');
    expect(userService.getUserCount()).toBe(1);
  });

  it('test 2', () => {
    // ❌ test 1의 영향을 받음 (의존성 발생)
    expect(userService.getUserCount()).toBe(1); // test 1에서 추가한 user
  });
});
```

## 실제 검증 절차

1. **변경된 파일에 대응하는 테스트 파일 확인**
   - `user.service.ts` → `user.service.test.ts` 또는 `user.service.spec.ts`
   - Serena로 테스트 파일 검색

2. **Sequential Thinking으로 테스트 품질 검증**
   - 성공/실패/Edge Case 테스트 존재 확인
   - 테스트 가독성, 독립성, 유지보수성 검증

3. **Serena memory에서 테스트 패턴 확인**
   - 프로젝트의 테스트 작성 가이드라인 확인
   - 기존 테스트 패턴과 일관성 검증

4. **커버리지 메트릭 확인**
   ```bash
   npm test -- --coverage
   # 또는
   jest --coverage
   ```

5. **검증 결과 문서화**
   - 테스트가 누락된 함수/파일 목록 작성
   - 커버리지가 낮은 부분 강조
   - 권장 테스트 케이스 제안
