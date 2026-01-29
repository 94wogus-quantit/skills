# Task Independence Guide

Comprehensive guide for ensuring tasks can be developed and tested independently. Task independence is critical for successful plan execution.

---

## Why Task Independence Matters

**Without Independence**:
- ❌ Can't work on tasks in parallel
- ❌ Can't verify completion of individual tasks
- ❌ Failures cascade across tasks
- ❌ Hard to isolate bugs
- ❌ Testing requires executing multiple tasks
- ❌ Can't reorder or skip tasks safely

**With Independence**:
- ✅ Tasks can be developed in parallel
- ✅ Can verify each task individually
- ✅ Failures are contained
- ✅ Easy to isolate and fix bugs
- ✅ Tests run independently with mocks
- ✅ Flexible execution order

---

## What is Task Independence?

A task is independent when:

1. **Can be implemented without other tasks**
   - Doesn't require other tasks to be completed first (except explicit dependencies)
   - Can be developed in isolation
   - Shared code is factored out or mocked

2. **Has clear boundaries**
   - Input and output are well-defined
   - Responsibility scope is explicit
   - No overlap with other tasks

3. **Can be tested in isolation**
   - Tests don't need other tasks completed
   - Dependencies can be mocked
   - Success is verifiable independently

4. **Success is independently measurable**
   - Completion criteria don't depend on other tasks
   - Can determine "done" without running other tasks

---

## Red Flags for Task Coupling

### 1. Shared Mutable State

❌ **Bad Example**:
```markdown
Task 1: Update user profile
- Modifies global user state

Task 2: Display user dashboard
- Reads from same global user state
- Assumes Task 1 has run
```

**Problem**: Task 2 depends on Task 1's runtime state

✅ **Good Example**:
```markdown
Task 1: Create User Profile API
- Input: User data
- Output: User ID, profile object
- No global state modification

Task 2: Create User Dashboard API
- Input: User ID
- Fetches user data independently
- No dependency on Task 1's execution
```

### 2. "...and also..." Pattern

❌ **Bad Example**:
```markdown
Task: Implement user authentication **and also** set up email notifications
```

**Problem**: Task does two unrelated things

✅ **Good Example**:
```markdown
Task 1: Implement user authentication
- Focuses only on auth

Task 2: Set up email notification service
- Focuses only on notifications
- Can use mocked auth service
```

### 3. Implicit Dependencies

❌ **Bad Example**:
```markdown
Task 1: Create database schema

Task 2: Implement user service
- (Implicitly assumes Task 1 created user table)
```

**Problem**: Dependency is not explicit

✅ **Good Example**:
```markdown
Task 1: Create database schema
- Creates user table

Task 2: Implement user service
- **Dependencies**: Task 1 (user table must exist)
- Can use test database/mock for testing
```

### 4. Test Dependencies

❌ **Bad Example**:
```markdown
Task 1: Implement login

**Testing Strategy**:
- Test assumes user registration (Task 2) is complete
- Cannot test login without Task 2
```

**Problem**: Tests require other tasks to run

✅ **Good Example**:
```markdown
Task 1: Implement login

**Testing Strategy**:
- Mock user repository with test data
- Create test users in setup
- Test independently of Task 2
```

### 5. Unclear Boundaries

❌ **Bad Example**:
```markdown
Task 1: Handle user input
- Validates input
- Saves to database
- Sends email
- Updates UI
```

**Problem**: Task has too many responsibilities, overlaps with other tasks

✅ **Good Example**:
```markdown
Task 1: Validate user input
- Only validation logic
- Returns validation result

Task 2: Save user data
- Takes validated data
- Only database operations

Task 3: Send notification
- Takes user data
- Only email logic
```

---

## Patterns for Achieving Independence

### Pattern 1: Dependency Injection

Instead of tasks depending on each other's implementation, define interfaces:

❌ **Coupled**:
```markdown
Task 1: Implement UserService
- class UserService {
    saveUser() { /* ... */ }
  }

Task 2: Implement OrderService
- Directly imports UserService
- Can't test without UserService implementation
```

✅ **Independent**:
```markdown
Task 0: Define shared interfaces
- interface IUserRepository {
    saveUser(user): Promise<User>
  }

Task 1: Implement UserService
- implements IUserRepository

Task 2: Implement OrderService
- depends on IUserRepository interface
- Can mock IUserRepository for testing
- Independent of Task 1's implementation
```

### Pattern 2: Extract Shared Logic

When multiple tasks need common functionality, extract it:

❌ **Coupled**:
```markdown
Task 1: Implement feature A
- Includes validation logic

Task 2: Implement feature B
- Needs same validation
- Duplicates logic OR depends on Task 1
```

✅ **Independent**:
```markdown
Task 0: Create validation utility
- Shared validation functions
- Tested independently

Task 1: Implement feature A
- Uses validation utility
- Independent of Task 2

Task 2: Implement feature B
- Uses validation utility
- Independent of Task 1
```

### Pattern 3: Clear Input/Output Contracts

Define what each task produces and consumes:

❌ **Unclear**:
```markdown
Task 1: Process user data
- (Unclear what it produces)

Task 2: Generate report
- (Unclear what it needs from Task 1)
```

✅ **Clear**:
```markdown
Task 1: Process user data
- **Input**: Raw user data (CSV format)
- **Output**: UserData[] (validated, typed)
- **Interface**: ProcessedUser { id, name, email }

Task 2: Generate report
- **Input**: ProcessedUser[] or mock data
- **Output**: Report file (PDF)
- Can test with mock ProcessedUser data
```

### Pattern 4: Database Abstraction

Don't let tasks share database concerns:

❌ **Coupled**:
```markdown
Task 1: Create users table
- SQL schema

Task 2: User registration
- Direct SQL queries
- Tightly coupled to Task 1's schema
```

✅ **Independent**:
```markdown
Task 0: Define User data access interface
- interface IUserRepository {
    create(user): Promise<User>
    findByEmail(email): Promise<User | null>
  }

Task 1: Implement User repository
- implements IUserRepository
- Handles database details

Task 2: User registration service
- depends on IUserRepository interface
- Can test with mock repository
```

---

## Examples of Independent Tasks

### Example 1: User Authentication Feature

❌ **Poorly Structured (Coupled)**:
```markdown
Task 1: Implement authentication
- Create login endpoint
- Create registration endpoint
- Set up email notifications
- Create user dashboard
- (Too many responsibilities)
```

✅ **Well Structured (Independent)**:
```markdown
Task 0: Define authentication interfaces
- IAuthService, IUserRepository, IEmailService
- Interfaces allow independent development

Task 1: Implement user repository
- **Input**: User data
- **Output**: User object or error
- **Dependencies**: None (database can be mocked)
- **Test**: Use test database

Task 2: Implement authentication service
- **Input**: Credentials
- **Output**: JWT token or error
- **Dependencies**: IUserRepository (mockable)
- **Test**: Mock user repository

Task 3: Create login API endpoint
- **Input**: HTTP request with credentials
- **Output**: HTTP response with token
- **Dependencies**: IAuthService (mockable)
- **Test**: Mock auth service

Task 4: Create registration API endpoint
- **Input**: HTTP request with user data
- **Output**: HTTP response with user ID
- **Dependencies**: IUserRepository (mockable)
- **Test**: Mock user repository

Task 5: Set up email notification service
- **Input**: Email template and recipient
- **Output**: Email sent confirmation
- **Dependencies**: None (email provider mocked)
- **Test**: Mock email provider
```

**Why this is better**:
- Each task focuses on one thing
- All tasks can be developed in parallel
- Each task can be tested independently with mocks
- Easy to isolate bugs
- Flexible execution order

### Example 2: E-commerce Checkout

❌ **Poorly Structured (Coupled)**:
```markdown
Task 1: Implement checkout
- Validate cart
- Process payment
- Update inventory
- Send order confirmation
- Generate invoice
- (Too many responsibilities, can't test independently)
```

✅ **Well Structured (Independent)**:
```markdown
Task 0: Define checkout interfaces
- ICartService, IPaymentService, IInventoryService, IOrderService

Task 1: Implement cart validation service
- **Input**: Cart items
- **Output**: Validation result
- **Dependencies**: None
- **Test**: Unit tests with sample carts

Task 2: Implement payment processing service
- **Input**: Payment details, amount
- **Output**: Payment confirmation or error
- **Dependencies**: None (payment gateway mocked)
- **Test**: Mock payment gateway

Task 3: Implement inventory update service
- **Input**: Order items
- **Output**: Inventory updated confirmation
- **Dependencies**: None (database mocked)
- **Test**: Test database

Task 4: Implement order creation service
- **Input**: Cart, payment confirmation
- **Output**: Order ID
- **Dependencies**: IPaymentService, IInventoryService (mockable)
- **Test**: Mock dependencies

Task 5: Implement order notification service
- **Input**: Order details
- **Output**: Email/SMS sent
- **Dependencies**: None (notification service mocked)
- **Test**: Mock notification service
```

---

## How to Split Coupled Tasks

### Step 1: Identify Responsibilities

List everything the task does:
```markdown
Current Task: Implement user profile
- Validates user data
- Saves to database
- Uploads profile photo
- Sends welcome email
- Logs activity
```

### Step 2: Group Related Operations

```markdown
Group 1: Data validation
- Validates user data

Group 2: Data persistence
- Saves to database
- Logs activity

Group 3: File handling
- Uploads profile photo

Group 4: Notifications
- Sends welcome email
```

### Step 3: Create Separate Tasks with Clear Interfaces

```markdown
Task 1: Create user validation service
- **Input**: User data object
- **Output**: Validation result (pass/fail + errors)
- **Dependencies**: None
- **Test**: Unit tests with various inputs

Task 2: Create user repository
- **Input**: Validated user data
- **Output**: User ID
- **Dependencies**: None (database mockable)
- **Test**: Test database

Task 3: Create profile photo upload service
- **Input**: File upload
- **Output**: Photo URL
- **Dependencies**: None (storage mockable)
- **Test**: Mock storage service

Task 4: Create user notification service
- **Input**: User data
- **Output**: Email sent confirmation
- **Dependencies**: None (email service mockable)
- **Test**: Mock email service

Task 5: Create user registration orchestrator
- **Input**: User registration request
- **Output**: Complete registration result
- **Dependencies**: Tasks 1-4 (all mockable)
- **Test**: Mock all dependencies, test orchestration logic
```

---

## Testing Independent Tasks

### Pattern: Test with Mocks

Each task should be testable without executing other tasks:

```markdown
### Task: Implement Order Service

**Testing Strategy**:
- **Test Type**: Unit tests with mocked dependencies
- **Test Cases**:
  1. Create order with valid data
     - **Given**: Mock payment service returns success
     - **When**: Create order with valid cart
     - **Then**: Order created with correct details
  2. Create order with payment failure
     - **Given**: Mock payment service returns failure
     - **When**: Create order
     - **Then**: Order not created, error returned
  3. Create order with inventory shortage
     - **Given**: Mock inventory service returns insufficient stock
     - **When**: Create order
     - **Then**: Order not created, specific error message
- **Acceptance Criteria**:
  - [ ] All tests pass with mocked dependencies
  - [ ] No actual payment/inventory calls during tests
  - [ ] Tests run in <100ms (unit test speed)
- **Test Commands**:
  \`\`\`bash
  npm test src/services/order-service.test.ts
  \`\`\`

**Mocking Strategy**:
\`\`\`typescript
// Test setup
const mockPaymentService = {
  processPayment: jest.fn().mockResolvedValue({ success: true })
};

const mockInventoryService = {
  checkStock: jest.fn().mockResolvedValue({ available: true })
};

const orderService = new OrderService(
  mockPaymentService,
  mockInventoryService
);

// Can test OrderService independently
\`\`\`
```

---

## Checklist for Task Independence

Use this checklist when reviewing or creating tasks:

### Can Be Implemented Independently
- [ ] Task doesn't require other tasks to be completed first (except explicit dependencies)
- [ ] Shared code is factored out to separate task or utility
- [ ] No implicit dependencies on other tasks' implementation

### Has Clear Boundaries
- [ ] Input is well-defined and explicit
- [ ] Output is well-defined and explicit
- [ ] Responsibility scope is clear and focused
- [ ] No overlap with other tasks

### Can Be Tested in Isolation
- [ ] Tests don't require other tasks to run first
- [ ] Dependencies can be mocked or stubbed
- [ ] Test setup is self-contained
- [ ] Tests run independently without shared state

### Success Is Independently Measurable
- [ ] Success criteria don't mention other tasks
- [ ] Can determine "done" without running other tasks
- [ ] Verification doesn't depend on other tasks' state

### Quality Indicators
- [ ] Task description doesn't say "...and also..."
- [ ] Task has single, focused responsibility
- [ ] Testing strategy includes mocking approach
- [ ] Clear interfaces defined for task boundaries

---

## Common Questions

### Q: What if tasks genuinely depend on each other?

**A**: Make dependencies explicit and define interfaces:

```markdown
Task 1: Define shared interfaces
- interface IUserService { ... }

Task 2: Implement user authentication
- **Dependencies**: None
- implements IUserService

Task 3: Implement user profile
- **Dependencies**: IUserService (can mock for testing)
- uses IUserService
```

### Q: Isn't extracting shared logic extra work?

**A**: Yes, but benefits outweigh costs:
- Tasks can be developed in parallel (faster overall)
- Easier testing and debugging
- More maintainable code
- Reduced risk of bugs
- Better code reuse

### Q: How small should tasks be?

**A**: As small as possible while remaining meaningful:
- Single responsibility
- Can be completed in reasonable time (hours to days, not weeks)
- Can be tested independently
- Has clear deliverable

### Q: What about sequential workflows?

**A**: Even sequential workflows can have independent tasks:

```markdown
Task 1: Parse user input
- **Output**: ParsedData
- Can test with sample inputs

Task 2: Validate parsed data
- **Input**: ParsedData (can mock)
- **Output**: ValidationResult
- Can test independently

Task 3: Process validated data
- **Input**: ValidatedData (can mock)
- **Output**: ProcessingResult
- Can test independently
```

---

## Summary

**Task Independence Principles**:

1. **One Responsibility**: Each task does one thing well
2. **Clear Interfaces**: Well-defined inputs and outputs
3. **Explicit Dependencies**: No hidden coupling
4. **Mockable Boundaries**: Can test with mocks
5. **Independent Verification**: Success measured independently

**Red Flags to Avoid**:
- "...and also..." pattern
- Shared mutable state
- Implicit dependencies
- Tests requiring other tasks
- Unclear responsibilities

**How to Achieve Independence**:
- Use dependency injection
- Extract shared logic
- Define clear contracts
- Abstract data access
- Design for testability

When tasks are independent, development is faster, testing is easier, and bugs are contained. Always design for independence from the start.
