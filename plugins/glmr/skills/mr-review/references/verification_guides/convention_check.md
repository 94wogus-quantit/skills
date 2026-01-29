# 컨벤션 준수 확인 가이드

## 목표

README.md와 CLAUDE.md의 코딩 컨벤션을 준수하는지 확인합니다.

## Sequential Thinking MCP 예시

### 예시 1: 네이밍 컨벤션 검증

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "네이밍 컨벤션 검증: 변수명이 camelCase인가? 상수는 UPPER_CASE인가? 클래스는 PascalCase인가? 타입은 PascalCase + Type 접미사인가?",
  thoughtNumber: 1,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

### 예시 2: 코드 스타일 검증

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "코드 스타일 검증: import 순서가 프로젝트 가이드를 따르는가? (외부 라이브러리 → 내부 모듈 → 타입 순서) 들여쓰기는 2spaces/4spaces 중 어떤 것을 사용하는가?",
  thoughtNumber: 2,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

### 예시 3: 주석 및 문서화 스타일 검증

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "주석 및 문서화 검증: JSDoc이 필요한 public 함수에 작성되었는가? 주석이 코드의 '무엇'이 아닌 '왜'를 설명하는가?",
  thoughtNumber: 3,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

### 예시 4: 에러 핸들링 패턴 검증

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "에러 핸들링 패턴 검증: 프로젝트의 에러 핸들링 방식(try-catch vs Either 모나드)을 따르는가? Custom Error 클래스를 사용하는가?",
  thoughtNumber: 4,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

## Serena MCP 예시

### 예시 1: 코드 패턴 메모리 읽기

```typescript
await mcp__plugin_serena_serena__read_memory({
  memory_file_name: "code_patterns.md"
})
```

### 예시 2: 기존 유사 코드 패턴 검색

```typescript
await mcp__plugin_serena_serena__search_for_pattern({
  pattern: "similar function patterns",
  file_mask: "*.ts"
})
```

### 예시 3: 네이밍 컨벤션 확인용 심볼 검색

```typescript
await mcp__plugin_serena_serena__find_symbol({
  symbol_name: "User.*Service|.*Controller|.*Repository"
})
```

### 예시 4: Import 구조 패턴 검색

```typescript
await mcp__plugin_serena_serena__search_for_pattern({
  pattern: "import.*from",
  file_mask: "*.ts"
})
```

## 검증 항목 체크리스트

### 네이밍 컨벤션

- [ ] 변수명: `camelCase` (예: `userName`, `userId`)
- [ ] 함수명: `camelCase` (예: `getUserById`, `createUser`)
- [ ] 클래스명: `PascalCase` (예: `UserService`, `ProductController`)
- [ ] 인터페이스명: `PascalCase` + `I` 접두사 또는 그냥 `PascalCase` (프로젝트 규칙 따름)
- [ ] 타입명: `PascalCase` (예: `UserDto`, `CreateUserRequest`)
- [ ] 상수: `UPPER_SNAKE_CASE` (예: `MAX_RETRY_COUNT`, `API_BASE_URL`)
- [ ] Enum: `PascalCase` (예: `UserRole`, `OrderStatus`)
- [ ] Private 필드: `_` 접두사 또는 `#` (프로젝트 규칙 따름)

### 코드 스타일

- [ ] 들여쓰기: 2 spaces 또는 4 spaces (프로젝트 설정 따름)
- [ ] 세미콜론: 사용 여부가 프로젝트 규칙과 일치
- [ ] 따옴표: single quote(`'`) 또는 double quote(`"`) (프로젝트 규칙 따름)
- [ ] 줄 길이: 프로젝트 ESLint/Prettier 설정 준수 (예: 80자, 100자, 120자)
- [ ] 빈 줄: 함수 사이, 논리적 블록 사이에 적절한 공백
- [ ] 중괄호: same-line(`{`) vs next-line 스타일 (프로젝트 규칙 따름)

### Import 구조 및 순서

- [ ] Import 순서:
  1. 외부 라이브러리 (`react`, `express` 등)
  2. 내부 모듈 (`@/components`, `@/services` 등)
  3. 상대 경로 (`./`, `../`)
  4. 타입 import (`import type {}`)
- [ ] Import 정렬: 알파벳순 정렬 (ESLint 규칙 따름)
- [ ] Unused imports 없음
- [ ] Absolute path vs Relative path 규칙 준수

### 주석 및 문서화

- [ ] JSDoc/TSDoc: Public 함수/클래스에 작성
- [ ] JSDoc 포맷: `@param`, `@returns`, `@throws` 포함
- [ ] 주석 내용: "무엇"이 아닌 "왜"를 설명
- [ ] TODO/FIXME: 필요 시 JIRA 이슈 번호와 함께 작성
- [ ] 복잡한 로직: 알고리즘 설명 주석 포함

### 에러 핸들링 패턴

- [ ] 프로젝트의 에러 핸들링 방식 준수 (try-catch, Either, Result 등)
- [ ] Custom Error 클래스 사용 (프로젝트에 정의된 경우)
- [ ] 에러 메시지: 명확하고 일관된 형식
- [ ] 에러 로깅: 프로젝트의 로깅 라이브러리 사용

### 파일 구조

- [ ] 파일명: kebab-case (예: `user-service.ts`) 또는 PascalCase (예: `UserService.ts`) (프로젝트 규칙 따름)
- [ ] 파일당 하나의 주요 Export (Single Responsibility)
- [ ] 파일 크기: 너무 크지 않음 (일반적으로 300줄 이하 권장)

## TypeScript 코드 예시

### 올바른 네이밍 컨벤션

```typescript
// ✅ GOOD: 네이밍 컨벤션 준수
const MAX_RETRY_COUNT = 3; // 상수: UPPER_SNAKE_CASE
const userName = 'John'; // 변수: camelCase

class UserService { // 클래스: PascalCase
  private _database: Database; // Private 필드: _ 접두사

  constructor(database: Database) {
    this._database = database;
  }

  async getUserById(userId: string): Promise<User> { // 함수: camelCase
    return this._database.users.findOne({ id: userId });
  }
}

interface IUserRepository { // 인터페이스: I + PascalCase
  findById(id: string): Promise<User>;
}

type CreateUserDto = { // 타입: PascalCase
  name: string;
  email: string;
};

enum UserRole { // Enum: PascalCase
  Admin,
  User,
  Guest
}
```

### 올바른 Import 순서

```typescript
// ✅ GOOD: Import 순서 준수
// 1. 외부 라이브러리
import express from 'express';
import { Request, Response } from 'express';
import bcrypt from 'bcrypt';

// 2. 내부 모듈 (Absolute path)
import { UserService } from '@/services/user.service';
import { UserRepository } from '@/repositories/user.repository';
import { validateEmail } from '@/utils/validation';

// 3. 상대 경로
import { AuthMiddleware } from './auth.middleware';
import { config } from '../config';

// 4. 타입 import
import type { User } from '@/types/user';
import type { AuthConfig } from './types';
```

### 잘못된 Import 순서

```typescript
// ❌ BAD: Import 순서가 뒤섞임
import { config } from '../config'; // 상대 경로가 먼저 나옴
import express from 'express'; // 외부 라이브러리가 뒤에 나옴
import type { User } from '@/types/user'; // 타입이 중간에 나옴
import { UserService } from '@/services/user.service'; // 순서 뒤바뀜
```

### 올바른 JSDoc 문서화

```typescript
// ✅ GOOD: JSDoc 문서화 완료
/**
 * 사용자를 생성합니다.
 *
 * @param userData - 생성할 사용자 정보
 * @returns 생성된 사용자 객체
 * @throws {ValidationError} 이메일 형식이 잘못된 경우
 * @throws {DuplicateEmailError} 이미 존재하는 이메일인 경우
 */
async function createUser(userData: CreateUserDto): Promise<User> {
  // 이메일 중복 확인 (단순 validation이 아닌, 비즈니스 규칙)
  // 왜냐하면 동일 이메일로 여러 계정 생성을 방지해야 하기 때문
  await validateUniqueEmail(userData.email);

  return userRepository.save(userData);
}

// ❌ BAD: JSDoc 없거나 불충분
async function createUser(userData: CreateUserDto): Promise<User> {
  await validateUniqueEmail(userData.email);
  return userRepository.save(userData);
}
```

### 올바른 에러 핸들링 패턴

```typescript
// ✅ GOOD: 프로젝트의 Custom Error 클래스 사용
class UserNotFoundError extends Error {
  constructor(userId: string) {
    super(`User not found: ${userId}`);
    this.name = 'UserNotFoundError';
  }
}

async function getUserById(userId: string): Promise<User> {
  const user = await userRepository.findById(userId);

  if (!user) {
    throw new UserNotFoundError(userId); // ✅ Custom Error 사용
  }

  return user;
}

// ❌ BAD: 일반적인 Error 사용
async function getUserById(userId: string): Promise<User> {
  const user = await userRepository.findById(userId);

  if (!user) {
    throw new Error('User not found'); // ❌ 구체적인 에러 타입 없음
  }

  return user;
}
```

### 파일 구조 예시

```typescript
// ✅ GOOD: 파일당 하나의 주요 Export
// src/services/user.service.ts
export class UserService {
  // UserService 관련 로직만
}

// src/services/product.service.ts
export class ProductService {
  // ProductService 관련 로직만
}

// ❌ BAD: 한 파일에 여러 주요 클래스
// src/services/services.ts
export class UserService {
  // ...
}

export class ProductService {
  // ...
}

export class OrderService {
  // ...
}
```

## 실제 검증 절차

1. **프로젝트 컨벤션 문서 읽기**
   - README.md에서 Coding Style 섹션 확인
   - CLAUDE.md에서 프로젝트 가이드라인 확인
   - ESLint/Prettier 설정 파일 확인

2. **Serena로 기존 패턴 파악**
   - `mcp__plugin_serena_serena__read_memory()`로 코드 패턴 확인
   - `mcp__plugin_serena_serena__search_for_pattern()`으로 유사 코드 검색

3. **Sequential Thinking으로 체계적 검증**
   - 네이밍 컨벤션 단계별 확인
   - Import 순서 검증
   - 주석 및 문서화 확인
   - 에러 핸들링 패턴 검증

4. **위반 사항 문서화**
   - 파일명:라인번호 형식으로 기록
   - 올바른 예시 제공
