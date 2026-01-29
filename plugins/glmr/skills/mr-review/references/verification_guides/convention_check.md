# Convention Compliance Verification Guide

## Goal

Verify that changed code follows the coding conventions defined in README.md and CLAUDE.md.

## Sequential Thinking MCP Examples

### Example 1: Naming Convention Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "네이밍 컨벤션 검증: 변수명이 camelCase인가? 상수는 UPPER_CASE인가? 클래스는 PascalCase인가? 타입은 PascalCase + Type 접미사인가?",
  thoughtNumber: 1,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

### Example 2: Code Style Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "코드 스타일 검증: import 순서가 프로젝트 가이드를 따르는가? (외부 라이브러리 → 내부 모듈 → 타입 순서) 들여쓰기는 2spaces/4spaces 중 어떤 것을 사용하는가?",
  thoughtNumber: 2,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

### Example 3: Comment and Documentation Style Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "주석 및 문서화 검증: JSDoc이 필요한 public 함수에 작성되었는가? 주석이 코드의 '무엇'이 아닌 '왜'를 설명하는가?",
  thoughtNumber: 3,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

### Example 4: Error Handling Pattern Verification

```typescript
await mcp__plugin_seq-think_st__sequentialthinking({
  thought: "에러 핸들링 패턴 검증: 프로젝트의 에러 핸들링 방식(try-catch vs Either 모나드)을 따르는가? Custom Error 클래스를 사용하는가?",
  thoughtNumber: 4,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

## Serena MCP Examples

### Example 1: Read Code Pattern Memory

```typescript
await mcp__plugin_serena_serena__read_memory({
  memory_file_name: "code_patterns.md"
})
```

### Example 2: Search Existing Similar Code Patterns

```typescript
await mcp__plugin_serena_serena__search_for_pattern({
  pattern: "similar function patterns",
  file_mask: "*.ts"
})
```

### Example 3: Search Symbols for Naming Convention Verification

```typescript
await mcp__plugin_serena_serena__find_symbol({
  symbol_name: "User.*Service|.*Controller|.*Repository"
})
```

### Example 4: Search Import Structure Patterns

```typescript
await mcp__plugin_serena_serena__search_for_pattern({
  pattern: "import.*from",
  file_mask: "*.ts"
})
```

## Verification Checklist

### Naming Conventions

- [ ] Variables: `camelCase` (e.g., `userName`, `userId`)
- [ ] Functions: `camelCase` (e.g., `getUserById`, `createUser`)
- [ ] Classes: `PascalCase` (e.g., `UserService`, `ProductController`)
- [ ] Interfaces: `PascalCase` + `I` prefix or plain `PascalCase` (follow project rules)
- [ ] Types: `PascalCase` (e.g., `UserDto`, `CreateUserRequest`)
- [ ] Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_COUNT`, `API_BASE_URL`)
- [ ] Enums: `PascalCase` (e.g., `UserRole`, `OrderStatus`)
- [ ] Private fields: `_` prefix or `#` (follow project rules)

### Code Style

- [ ] Indentation: 2 spaces or 4 spaces (follow project settings)
- [ ] Semicolons: usage matches project rules
- [ ] Quotes: single quote(`'`) or double quote(`"`) (follow project rules)
- [ ] Line length: follows project ESLint/Prettier settings (e.g., 80, 100, 120 chars)
- [ ] Blank lines: appropriate spacing between functions and logical blocks
- [ ] Braces: same-line(`{`) vs next-line style (follow project rules)

### Import Structure and Order

- [ ] Import order:
  1. External libraries (`react`, `express`, etc.)
  2. Internal modules (`@/components`, `@/services`, etc.)
  3. Relative paths (`./`, `../`)
  4. Type imports (`import type {}`)
- [ ] Import sorting: alphabetical order (follow ESLint rules)
- [ ] No unused imports
- [ ] Absolute path vs Relative path rule compliance

### Comments and Documentation

- [ ] JSDoc/TSDoc: written for public functions/classes
- [ ] JSDoc format: includes `@param`, `@returns`, `@throws`
- [ ] Comment content: explains "why" not "what"
- [ ] TODO/FIXME: written with JIRA issue number when needed
- [ ] Complex logic: includes algorithm explanation comments

### Error Handling Patterns

- [ ] Follows project error handling approach (try-catch, Either, Result, etc.)
- [ ] Uses Custom Error classes (if defined in project)
- [ ] Error messages: clear and consistent format
- [ ] Error logging: uses project's logging library

### File Structure

- [ ] Filenames: kebab-case (e.g., `user-service.ts`) or PascalCase (e.g., `UserService.ts`) (follow project rules)
- [ ] One primary export per file (Single Responsibility)
- [ ] File size: not too large (generally 300 lines or less recommended)

## TypeScript Code Examples

### Correct Naming Convention

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

### Correct Import Order

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

### Incorrect Import Order

```typescript
// ❌ BAD: Import 순서가 뒤섞임
import { config } from '../config'; // 상대 경로가 먼저 나옴
import express from 'express'; // 외부 라이브러리가 뒤에 나옴
import type { User } from '@/types/user'; // 타입이 중간에 나옴
import { UserService } from '@/services/user.service'; // 순서 뒤바뀜
```

### Correct JSDoc Documentation

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

### Correct Error Handling Pattern

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

### File Structure Example

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

## Actual Verification Procedure

1. **Read project convention documents**
   - Check Coding Style section in README.md
   - Check project guidelines in CLAUDE.md
   - Check ESLint/Prettier configuration files

2. **Identify existing patterns with Serena**
   - Check code patterns with `mcp__plugin_serena_serena__read_memory()`
   - Search similar code with `mcp__plugin_serena_serena__search_for_pattern()`

3. **Systematically verify with Sequential Thinking**
   - Step-by-step naming convention verification
   - Import order verification
   - Comment and documentation verification
   - Error handling pattern verification

4. **Document violations**
   - Record in filename:line_number format
   - Provide correct examples
