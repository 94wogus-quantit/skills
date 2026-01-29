# Testing Strategy Guide

Comprehensive guide for writing effective testing strategies in task plans. Every task MUST have a testing strategy before the plan can be approved.

---

## Why Testing Strategy Matters

**Without Testing Strategy**:
- ❌ Don't know when task is "done"
- ❌ Can't verify correctness independently
- ❌ Risk of bugs in production
- ❌ Difficult to maintain code
- ❌ Hard to refactor safely

**With Testing Strategy**:
- ✅ Clear definition of "done"
- ✅ Can verify each task independently
- ✅ Catch bugs early
- ✅ Safe to refactor
- ✅ Documentation of expected behavior

---

## Testing Strategy Template

Every task should have this structure:

```markdown
**Testing Strategy**: [How to verify this task is correctly implemented]
- **Test Type**: [Unit / Integration / Manual / E2E]
- **Test Cases**:
  1. [Specific test scenario 1]
     - **Given**: [Initial state]
     - **When**: [Action performed]
     - **Then**: [Expected result]
  2. [Specific test scenario 2]
  3. [Edge case scenario]
- **Acceptance Criteria**:
  - [ ] [Measurable pass condition 1]
  - [ ] [Measurable pass condition 2]
  - [ ] [Code coverage if applicable]
- **Test Commands**:
  \`\`\`bash
  npm test src/path/test.spec.ts
  # or
  pytest tests/test_module.py -v
  \`\`\`
```

---

## Choosing the Right Test Type

### Unit Tests
**When to use**: Testing individual functions, classes, or modules in isolation

**Characteristics**:
- Fast execution (milliseconds)
- No external dependencies (database, API, file system)
- Tests one thing at a time
- Easy to pinpoint failures

**Example Scenarios**:
- Testing a utility function
- Testing business logic
- Testing data transformation
- Testing validation logic

**Example**:
```markdown
- **Test Type**: Unit tests
- **Test Cases**:
  1. Valid email format validation
     - **Given**: Email validator function
     - **When**: Called with "user@example.com"
     - **Then**: Returns true
  2. Invalid email format validation
     - **Given**: Email validator function
     - **When**: Called with "invalid-email"
     - **Then**: Returns false
  3. Null email handling
     - **Given**: Email validator function
     - **When**: Called with null
     - **Then**: Returns false or throws ValidationError
```

### Integration Tests
**When to use**: Testing interactions between multiple components

**Characteristics**:
- Moderate execution time (seconds)
- Tests multiple units working together
- May use test databases or mocked external services
- Verifies component boundaries

**Example Scenarios**:
- Testing API endpoint with database
- Testing service layer with repository
- Testing multiple modules interacting
- Testing data flow through system

**Example**:
```markdown
- **Test Type**: Integration tests
- **Test Cases**:
  1. Create user flow
     - **Given**: Empty test database
     - **When**: POST /api/users with valid data
     - **Then**: User created in database, returns 201 with user ID
  2. Duplicate user handling
     - **Given**: User exists with email "test@example.com"
     - **When**: POST /api/users with same email
     - **Then**: Returns 409 Conflict error
  3. Database connection failure
     - **Given**: Database is unavailable
     - **When**: POST /api/users with valid data
     - **Then**: Returns 503 Service Unavailable
```

### End-to-End (E2E) Tests
**When to use**: Testing complete user workflows through the entire application

**Characteristics**:
- Slow execution (seconds to minutes)
- Tests full stack (frontend + backend + database)
- Simulates real user interactions
- Verifies user journeys

**Example Scenarios**:
- Testing complete user registration flow
- Testing checkout process
- Testing search and filter workflow
- Testing multi-step forms

**Example**:
```markdown
- **Test Type**: E2E tests
- **Test Cases**:
  1. Complete user registration journey
     - **Given**: User on homepage
     - **When**: Click "Sign Up" → Fill form → Submit → Verify email → Login
     - **Then**: User can access dashboard
  2. Registration with existing email
     - **Given**: User on registration page
     - **When**: Submit with existing email
     - **Then**: See "Email already registered" error
  3. Password strength validation
     - **Given**: User on registration form
     - **When**: Enter weak password
     - **Then**: See password strength indicator and requirements
```

### Manual Tests
**When to use**: When automation isn't feasible or cost-effective

**Use sparingly for**:
- Visual/UX verification
- Complex user interactions
- Third-party integrations (initially)
- Exploratory testing

**Example**:
```markdown
- **Test Type**: Manual tests
- **Test Cases**:
  1. Visual alignment verification
     - **Given**: Dashboard with new widget
     - **When**: View on desktop (1920x1080) and mobile (375x667)
     - **Then**: Widget displays correctly without layout issues
  2. Color contrast accessibility
     - **Given**: New color scheme applied
     - **When**: Check with WCAG contrast checker
     - **Then**: All text meets AA standards (4.5:1 contrast)
```

---

## Writing Specific Test Cases

### Bad Examples (Too Generic)

❌ **Bad**: "Test that login works"
- Not specific about what "works" means
- No clear pass/fail condition
- Could mean many different scenarios

❌ **Bad**: "Test all edge cases"
- Doesn't specify which edge cases
- No clear test scenarios
- Can't verify if complete

❌ **Bad**: "Make sure the API handles errors"
- Which errors?
- How should it handle them?
- What's the expected behavior?

### Good Examples (Specific & Concrete)

✅ **Good**:
```markdown
1. Successful login with valid credentials
   - **Given**: User exists with email "test@example.com" and password "Pass123!"
   - **When**: POST /api/auth/login with correct credentials
   - **Then**: Returns 200 OK with JWT token, token expires in 24h
```

✅ **Good**:
```markdown
2. Login with invalid password
   - **Given**: User exists with email "test@example.com"
   - **When**: POST /api/auth/login with wrong password
   - **Then**: Returns 401 Unauthorized, error message "Invalid credentials"
```

✅ **Good**:
```markdown
3. Login with non-existent user
   - **Given**: No user with email "nonexistent@example.com"
   - **When**: POST /api/auth/login with that email
   - **Then**: Returns 401 Unauthorized (same as invalid password for security)
```

---

## Writing Measurable Acceptance Criteria

### Bad Examples (Vague)

❌ **Bad**: "All tests pass"
- Which tests? How many?
- No coverage requirement
- Can't verify completeness

❌ **Bad**: "Feature works correctly"
- What defines "correctly"?
- No measurable criteria
- Subjective assessment

❌ **Bad**: "No bugs"
- Impossible to verify
- Doesn't specify what was tested
- Not actionable

### Good Examples (Measurable)

✅ **Good**:
```markdown
- [ ] All 15 unit tests pass (test_auth_service.ts)
- [ ] Code coverage for authentication module >80%
- [ ] Integration test verifies JWT token generation
- [ ] Manual test confirms error messages display correctly
```

✅ **Good**:
```markdown
- [ ] API returns 200 status for valid requests
- [ ] API returns 401 status for unauthorized requests
- [ ] Response time <200ms for 95th percentile
- [ ] No errors in error tracking for 24h after deployment
```

✅ **Good**:
```markdown
- [ ] User can complete registration in <2 minutes
- [ ] Form validation displays within 100ms of input
- [ ] Confirmation email arrives within 30 seconds
- [ ] Zero console errors during E2E test execution
```

---

## Providing Runnable Test Commands

### Bad Examples

❌ **Bad**: "Run the tests"
- Which tests?
- What command?
- Any parameters needed?

❌ **Bad**: "Use the test script"
- Which script?
- Where is it?
- How to run it?

❌ **Bad**: "Test manually"
- Not reproducible
- No specific steps
- Can't verify independently

### Good Examples

✅ **Good** (JavaScript/TypeScript):
```bash
# Run specific test file
npm test src/auth/login.test.ts

# Run all auth tests
npm test -- --testPathPattern=auth

# Run with coverage
npm test src/auth/login.test.ts -- --coverage

# Run in watch mode during development
npm test -- --watch --testPathPattern=login
```

✅ **Good** (Python):
```bash
# Run specific test module
pytest tests/test_auth.py -v

# Run specific test function
pytest tests/test_auth.py::test_login_success -v

# Run with coverage
pytest tests/test_auth.py --cov=src/auth --cov-report=html

# Run integration tests
pytest tests/integration/ -v -m integration
```

✅ **Good** (Manual with automation script):
```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Run E2E tests
npm run test:e2e

# Cleanup
docker-compose -f docker-compose.test.yml down
```

---

## Complete Examples

### Example 1: Backend API Endpoint

```markdown
### Task: Implement User Registration API

**Testing Strategy**: Verify registration endpoint handles all cases correctly
- **Test Type**: Integration tests
- **Test Cases**:
  1. Successful registration with valid data
     - **Given**: No existing user with email "newuser@example.com"
     - **When**: POST /api/users with {name, email, password}
     - **Then**: Returns 201 Created, user ID, and email verification sent
  2. Registration with existing email
     - **Given**: User exists with email "existing@example.com"
     - **When**: POST /api/users with same email
     - **Then**: Returns 409 Conflict with error "Email already registered"
  3. Registration with invalid email format
     - **Given**: Request with email "invalid-email"
     - **When**: POST /api/users
     - **Then**: Returns 400 Bad Request with validation error
  4. Registration with weak password
     - **Given**: Request with password "123"
     - **When**: POST /api/users
     - **Then**: Returns 400 Bad Request with "Password must be at least 8 characters"
  5. Database connection failure during registration
     - **Given**: Database is unavailable (simulated)
     - **When**: POST /api/users with valid data
     - **Then**: Returns 503 Service Unavailable, transaction rolled back
- **Acceptance Criteria**:
  - [ ] All 5 integration tests pass
  - [ ] API endpoint returns correct status codes
  - [ ] Password is hashed before storage (verified in test)
  - [ ] Email verification email is queued (mocked in test)
  - [ ] No plaintext passwords in logs (verified)
- **Test Commands**:
  \`\`\`bash
  # Run integration tests for user registration
  npm test tests/integration/user-registration.test.ts

  # Run with database debugging
  DEBUG=db:* npm test tests/integration/user-registration.test.ts

  # Check test coverage
  npm test tests/integration/user-registration.test.ts -- --coverage
  \`\`\`
```

### Example 2: Frontend Component

```markdown
### Task: Create Login Form Component

**Testing Strategy**: Verify form handles all user interactions correctly
- **Test Type**: Unit tests for component logic, E2E for full flow
- **Test Cases (Unit)**:
  1. Form validation on submit
     - **Given**: Empty form
     - **When**: Click submit button
     - **Then**: Display validation errors for required fields
  2. Email format validation
     - **Given**: Form with invalid email "notanemail"
     - **When**: Blur email field
     - **Then**: Show "Invalid email format" error
  3. Password visibility toggle
     - **Given**: Password field has value
     - **When**: Click show/hide password icon
     - **Then**: Input type toggles between password/text
  4. Loading state during submission
     - **Given**: Form is submitting
     - **When**: During API call
     - **Then**: Submit button disabled, shows spinner
  5. Error message display
     - **Given**: API returns 401 error
     - **When**: Login fails
     - **Then**: Display "Invalid credentials" error message
- **Test Cases (E2E)**:
  1. Successful login flow
     - **Given**: User on login page
     - **When**: Enter valid credentials and submit
     - **Then**: Redirected to dashboard, auth token stored
- **Acceptance Criteria**:
  - [ ] All 5 unit tests pass
  - [ ] E2E test verifies complete login flow
  - [ ] Component coverage >90%
  - [ ] No accessibility violations (aXe)
  - [ ] Visual regression test passes
- **Test Commands**:
  \`\`\`bash
  # Run component unit tests
  npm test src/components/LoginForm.test.tsx

  # Run E2E login tests
  npm run test:e2e -- --spec=cypress/e2e/login.cy.ts

  # Check accessibility
  npm test src/components/LoginForm.test.tsx -- --testNamePattern="accessibility"
  \`\`\`
```

### Example 3: Database Migration

```markdown
### Task: Add User Preferences Table

**Testing Strategy**: Verify migration runs successfully and data integrity maintained
- **Test Type**: Integration tests for migration, Unit tests for ORM
- **Test Cases**:
  1. Migration runs successfully on empty database
     - **Given**: Fresh database with existing migrations applied
     - **When**: Run new migration
     - **Then**: user_preferences table created with correct schema
  2. Migration preserves existing data
     - **Given**: Database with existing users
     - **When**: Run migration
     - **Then**: All existing user records intact
  3. Rollback migration
     - **Given**: Migration has been applied
     - **When**: Run rollback
     - **Then**: user_preferences table dropped, no orphaned data
  4. Migration is idempotent
     - **Given**: Migration already applied
     - **When**: Attempt to run again
     - **Then**: No errors, no duplicate data
  5. ORM can query new table
     - **Given**: Migration applied
     - **When**: Use ORM to create/read user preferences
     - **Then**: Operations succeed, data persisted correctly
- **Acceptance Criteria**:
  - [ ] All 5 migration tests pass
  - [ ] Migration script has no SQL syntax errors
  - [ ] Rollback script tested and works
  - [ ] ORM models updated and tested
  - [ ] No data loss in test scenarios
- **Test Commands**:
  \`\`\`bash
  # Run migration tests
  npm test tests/migrations/add-user-preferences.test.ts

  # Test migration on clean database
  npm run db:reset:test && npm run migrate:test

  # Test rollback
  npm run migrate:test && npm run migrate:rollback:test

  # Verify ORM integration
  npm test tests/models/UserPreferences.test.ts
  \`\`\`
```

---

## Common Mistakes to Avoid

### 1. No Testing Strategy at All
❌ Task has no testing section
✅ Every task must have a testing strategy before approval

### 2. Generic Test Descriptions
❌ "Test that it works"
✅ "Test login with valid credentials returns JWT token"

### 3. Missing Edge Cases
❌ Only tests happy path
✅ Tests happy path + error cases + edge cases

### 4. Vague Acceptance Criteria
❌ "Tests pass"
✅ "All 10 unit tests pass with >80% code coverage"

### 5. No Test Commands
❌ No information on how to run tests
✅ Exact commands: `npm test src/module.test.ts`

### 6. Wrong Test Type
❌ Using E2E tests for simple logic
✅ Unit tests for logic, E2E for workflows

### 7. Untestable Task
❌ Task is too large or coupled to test independently
✅ Split task or define clear mocking strategy

---

## Checklist for Reviewers

When reviewing a task's testing strategy:

- [ ] Testing Strategy section exists
- [ ] Test type is appropriate for the task
- [ ] At least 3 specific test cases listed
- [ ] Test cases use Given/When/Then format
- [ ] Edge cases and error scenarios included
- [ ] Acceptance criteria are measurable
- [ ] Acceptance criteria include coverage if applicable
- [ ] Test commands are provided
- [ ] Test commands are runnable and complete
- [ ] Task can be verified independently with these tests

If any checkbox is unchecked, the testing strategy needs improvement.

---

## Summary

**Every task MUST have**:
1. ✅ Testing Strategy section
2. ✅ Appropriate test type
3. ✅ Specific, concrete test cases (minimum 3)
4. ✅ Measurable acceptance criteria
5. ✅ Runnable test commands

**Use this format consistently** to ensure every task can be verified independently and the plan can be approved for execution.
