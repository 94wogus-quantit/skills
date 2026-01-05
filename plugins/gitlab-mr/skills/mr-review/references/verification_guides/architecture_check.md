# Architecture Consistency Verification Guide

## Goal

Verify that changed code follows the project's architecture principles and layer separation rules.

## Sequential Thinking MCP Examples

### Example 1: Layer Separation Principle Verification

```typescript
await mcp__plugin_workflow-bundle_sequential-thinking__sequentialthinking({
  thought: "Does the changed code follow the existing architecture layer separation principles? Does it follow the Controller → Service → Repository pattern?",
  thoughtNumber: 1,
  totalThoughts: 7,
  nextThoughtNeeded: true
})
```

### Example 2: Dependency Direction Verification

```typescript
await mcp__plugin_workflow-bundle_sequential-thinking__sequentialthinking({
  thought: "Is the dependency direction correct? Does the high-level module not depend on the low-level module? Does the Domain layer not directly reference the Infrastructure layer?",
  thoughtNumber: 2,
  totalThoughts: 7,
  nextThoughtNeeded: true
})
```

### Example 3: Directory Structure Rule Verification

```typescript
await mcp__plugin_workflow-bundle_sequential-thinking__sequentialthinking({
  thought: "Do newly added files follow the project's directory structure rules? Are API endpoints in src/api/ and business logic in src/services/?",
  thoughtNumber: 3,
  totalThoughts: 7,
  nextThoughtNeeded: true
})
```

### Example 4: Architecture Pattern Consistency Verification

```typescript
await mcp__plugin_workflow-bundle_sequential-thinking__sequentialthinking({
  thought: "If the project uses Clean Architecture/Hexagonal Architecture, does the new code respect those pattern boundaries? Are Ports and Adapters clearly separated?",
  thoughtNumber: 4,
  totalThoughts: 7,
  nextThoughtNeeded: true
})
```

## Serena MCP Examples

### Example 1: Reading Architecture Decisions Memory

```typescript
await mcp__plugin_serena_serena__read_memory({
  memory_file_name: "architecture_decisions.md"
})
```

### Example 2: Tracking Symbols and Dependencies of Changed Files

```typescript
await mcp__plugin_serena_serena__find_referencing_symbols({
  name_path: "UserService", // Newly added class/function name
  relative_path: "src/services/user.service.ts"
})
```

### Example 3: Searching Existing Patterns

```typescript
await mcp__plugin_serena_serena__search_for_pattern({
  substring_pattern: "service layer patterns",
  paths_include_glob: "*.service.ts"
})
```

## Verification Checklist

### Directory Structure Rules

- [ ] API endpoints are in correct directory (`src/api/`, `src/routes/`)
- [ ] Business logic is implemented in service layer (`src/services/`, `src/domain/`)
- [ ] Data access logic is separated in Repository/DAO layer
- [ ] Utility functions are in `src/utils/`
- [ ] Type definitions are in `src/types/`

### Layer Separation Principles

- [ ] Controller only handles HTTP request/response (no business logic)
- [ ] Service only handles business logic (no database access)
- [ ] Repository only handles data access (no business logic)
- [ ] Each layer is clearly distinguished with separated responsibilities

### Dependency Direction Rules

- [ ] Low-level modules depend on high-level modules (no reverse dependencies)
- [ ] Domain layer does not directly reference Infrastructure layer
- [ ] No circular dependencies
- [ ] Dependency Inversion Principle followed via interfaces

### Consistency with Existing Patterns

- [ ] Same type of functionality is implemented with the same pattern
- [ ] Naming conventions are consistent with existing code (e.g., `UserController`, `ProductService`)
- [ ] Error handling approach is consistent with existing code
- [ ] DI (Dependency Injection) approach is consistent with existing code

### Architecture Documentation Compliance

- [ ] Follows CLAUDE.md architecture guidelines
- [ ] Matches README.md project structure description
- [ ] Follows ADR (Architecture Decision Record) decisions

## TypeScript Code Examples

### Correct Layer Separation Example

```typescript
// ✅ GOOD: Controller only handles HTTP
// src/api/user.controller.ts
export class UserController {
  constructor(private userService: UserService) {}

  async createUser(req: Request, res: Response) {
    const userData = req.body;
    const user = await this.userService.createUser(userData);
    res.status(201).json(user);
  }
}

// ✅ GOOD: Service only handles business logic
// src/services/user.service.ts
export class UserService {
  constructor(private userRepository: UserRepository) {}

  async createUser(userData: CreateUserDto): Promise<User> {
    // Business logic: email duplication check, password hashing, etc.
    await this.validateEmail(userData.email);
    const hashedPassword = await this.hashPassword(userData.password);

    return this.userRepository.save({
      ...userData,
      password: hashedPassword
    });
  }
}

// ✅ GOOD: Repository only handles data access
// src/repositories/user.repository.ts
export class UserRepository {
  async save(user: User): Promise<User> {
    // Database access logic only
    return await this.db.users.create(user);
  }
}
```

### Incorrect Layer Separation Example

```typescript
// ❌ BAD: Controller has business logic
// src/api/user.controller.ts
export class UserController {
  async createUser(req: Request, res: Response) {
    const userData = req.body;

    // ❌ Business logic should not be in Controller
    if (await this.db.users.findByEmail(userData.email)) {
      throw new Error('Email already exists');
    }

    // ❌ Database access should not be in Controller
    const user = await this.db.users.create(userData);
    res.status(201).json(user);
  }
}

// ❌ BAD: Service directly accesses database
// src/services/user.service.ts
export class UserService {
  async createUser(userData: CreateUserDto): Promise<User> {
    // ❌ Service should not directly access DB
    return await this.db.users.create(userData);
  }
}
```

### Correct Dependency Direction Example

```typescript
// ✅ GOOD: Dependency Inversion Principle compliance
// src/domain/user.service.ts
export class UserService {
  // Depends on interface (not concrete implementation)
  constructor(private userRepository: IUserRepository) {}

  async findUser(id: string): Promise<User> {
    return this.userRepository.findById(id);
  }
}

// src/domain/interfaces/user-repository.interface.ts
export interface IUserRepository {
  findById(id: string): Promise<User>;
  save(user: User): Promise<User>;
}

// src/infrastructure/user.repository.ts
export class UserRepository implements IUserRepository {
  // Concrete implementation
  async findById(id: string): Promise<User> {
    return await this.db.users.findOne({ id });
  }

  async save(user: User): Promise<User> {
    return await this.db.users.create(user);
  }
}
```

## Actual Verification Procedure

1. **Understand project architecture with Serena**
   - Check stored architecture info with `mcp__plugin_serena_serena__list_memories()`
   - Check architecture decisions with `mcp__plugin_serena_serena__read_memory()`

2. **Verify each layer with Sequential Thinking**
   - Systematically verify layer separation principles for each changed file
   - Step-by-step confirmation that dependency direction is correct

3. **Compare with existing patterns using Serena**
   - Find similar code patterns with `mcp__plugin_serena_serena__search_for_pattern()`
   - Compare if new code is consistent with existing patterns

4. **Document verification results**
   - Record violations in file_path:line_number format
   - Provide recommended fix directions
