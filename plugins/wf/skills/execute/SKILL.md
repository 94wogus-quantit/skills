---
name: execute
description: Execute approved implementation plans with TaskList tracking, test verification, and success criteria validation. Use when you have an approved *_PLAN.md file and need step-by-step implementation with comprehensive tracking. Outputs implemented code, test results, and execution summary. Documentation handled by record skill. Korean triggers: 계획 실행, 플랜 실행, 구현 시작, 개발 시작, 코딩 시작, 작업 시작, 실행해줘, 구현해줘, 만들어줘, 개발해줘, 코드 작성, 기능 구현, 태스크 실행.
user-invocable: true
---

# Execute Plan

## ⚠️ CRITICAL LANGUAGE POLICY

**DEFAULT LANGUAGE: KOREAN (한국어)**

ALL outputs, documentation, code comments, and communications MUST be in **KOREAN** unless explicitly requested otherwise by the user.

- ✅ **Code comments**: Write in Korean
- ✅ **Documentation**: Write in Korean
- ✅ **TaskList items**: Write in Korean
- ✅ **Progress updates**: Provide in Korean
- ✅ **User communication**: Respond in Korean

**Exception**: If the user writes in another language, match that language for responses.

**This is a MANDATORY requirement. Do NOT default to English.**

---

## When to Use This Skill

Use this skill when:
- You have an approved implementation plan file (e.g., `USER_AUTH_PLAN.md`)
- User requests "execute this plan", "implement the plan", "run execute"
- Need to systematically implement multiple related tasks
- Want automatic progress tracking with TaskList
- Need to ensure all success criteria and tests are verified

**Typical Workflow Position**:
```
analyze → plan → **execute** → record
```

## Overview

This skill executes approved implementation plans through a 9-phase systematic process:

0. **Branch Validation**: Verify working on a feature branch
1. **Plan Loading & Validation**: Load plan file, parse tasks, verify prerequisites
2. **TaskList Setup**: Create comprehensive TaskList from all plan tasks
3. **Task Execution**: Execute tasks sequentially, respecting dependencies
4. **Handle Dependencies**: Manage task dependencies and execution order
5. **Automated Test Generation** (Conditional): Detect missing tests and generate them
6. **Testing & Verification**: Run tests and verify success criteria

**Note**:
- Phase 4C (DB Migration Validation) and Phase 5 (Test Generation) are optional
- **Documentation (README, CHANGELOG, Git commit) is handled by `record` skill** - not in execute

---

## Workflow: 9-Phase Execution Process

### Phase 0: Task Registration

⚠️ **CRITICAL: DO NOT SKIP PHASE 0**

**Objective**: Register all Phases as Tasks to track progress throughout the execution workflow.

Register the following Phases in order using `TaskCreate`:

| Task | subject | activeForm |
|------|---------|------------|
| Phase 1 | Branch Validation | Validating branch |
| Phase 2 | Plan Loading and Validation | Loading and validating plan |
| Phase 3 | Setup TaskList from Plan | Setting up TaskList |
| Phase 4 | Execute Tasks Sequentially | Executing tasks |
| Phase 5 | Handle Dependencies | Handling dependencies |
| Phase 5C | Database Migration Validation (conditional) | Validating database migration |
| Phase 6 | Automated Test Generation (conditional) | Generating automated tests |
| Phase 7 | AC Achievement Report | Generating AC report |
| Phase 7.5 | Independent QA Gate (wf:qa spawn) | Awaiting wf:qa verdict |
| Phase 8 | Testing and Verification | Testing and verifying |

**Task Tracking Rules**:
- On Phase entry: `TaskUpdate(taskId, status: "in_progress")`
- On Phase completion: `TaskUpdate(taskId, status: "completed")`
- Conditional Phases (5C, 6) not executed: `TaskUpdate(taskId, status: "deleted")`
- Only **one Phase** should be `in_progress` at any time

---

### Phase 1: Branch Validation

> 📋 **Task Tracking**: Mark this Phase's Task as `in_progress` on entry, `completed` on completion.

> **MANDATORY REQUIREMENT**:
>
> - **DO NOT** assume you are on the correct branch
> - **ALWAYS** verify branch status using the MCP tool below
> - **NEVER** start code modification (Phase 2) without completing Phase 1
>
> **Why this matters**:
> - Code changes in main/master branch can cause merge conflicts
> - Modifying main/master while working on features is dangerous
> - Branch isolation prevents accidental commits to production branches

**Objective**: Verify that you are working on a feature branch.

**Steps**:

**1. Check Branch Protection Status**

Use `check_branch_protection` MCP tool:

```
Tool: check_branch_protection
Returns:
  - branch: 현재 브랜치 이름
  - is_protected: 보호 브랜치 여부 (main/master/staging)
  - needs_new_branch: 새 브랜치 생성 필요 여부
  - message: 상태 메시지
```

**2. Branch Decision**

- **If `is_protected` is `false`**: Proceed directly to Phase 2
- **If `is_protected` is `true`**: Proceed to Step 3

**3. Ask User - Branch Action**

Use `AskUserQuestion` tool to provide options:

```yaml
questions:
  - question: "현재 보호된 브랜치({branch})에서 작업 중입니다. 어떻게 진행할까요?"
    header: "Branch"
    options:
      - label: "새 브랜치 생성 (Recommended)"
        description: "feature 브랜치를 생성하여 안전하게 작업합니다"
      - label: "현재 브랜치에서 계속"
        description: "⚠️ 보호된 브랜치에서 직접 작업합니다 (권장하지 않음)"
```

- **If "새 브랜치 생성" selected**: Proceed to Step 4
- **If "현재 브랜치에서 계속" selected**: Display warning and proceed to Phase 2
  - Output: `⚠️ 보호된 브랜치({branch})에서 코드를 수정합니다. 변경사항이 직접 반영됩니다.`

**4. Ask User - Branch Name**

Use `AskUserQuestion` tool to select branch name:

```yaml
questions:
  - question: "생성할 브랜치 이름을 선택하세요"
    header: "Name"
    options:
      - label: "feature/{PLAN_NAME}"
        description: "PLAN 파일명 기반 추천 브랜치 이름"
      - label: "직접 입력"
        description: "원하는 브랜치 이름을 직접 입력합니다"
```

**Branch Name Suggestion Logic**:
- If PLAN file exists: Suggest `feature/{ID_from_PLAN}` format
- If JIRA ID exists: Suggest `feature/JIRA-123` format
- Otherwise: Suggest `feature/execute-{YYYYMMDD}` format

**5. Create Feature Branch**

Use `create_feature_branch` MCP tool:

```
Tool: create_feature_branch
Args:
  - branch_name: 선택된 또는 입력된 브랜치 이름
Returns:
  - success: 성공 여부
  - branch: 생성된 브랜치 이름
  - message: 결과 메시지
```

---

### Phase 2: Plan Loading and Validation

> 📋 **Task Tracking**: Mark this Phase's Task as `in_progress` on entry, `completed` on completion.

**Objective**: Load and understand the plan, validate prerequisites are met.

**Steps**:

1. **Load the Plan File**
   ```typescript
   // Use Read tool to load the plan
   Read(planFilePath)
   ```

2. **Parse Plan Structure**
   - Use `mcp__plugin_seq-think_st__sequentialthinking` to understand:
     - Task breakdown and priorities (P0 → P1 → P2 → P3)
     - Dependencies between tasks
     - Success criteria for each task
     - Testing strategies
     - Risk mitigations
     - Expected tools and MCP servers

3. **Validate Prerequisites**
   - Check codebase context:
     ```typescript
     mcp__plugin_serena_serena__check_onboarding_performed()
     mcp__plugin_serena_serena__get_current_config()
     ```
   - Verify required MCP servers are accessible
   - Confirm tools specified in plan are available
   - Check that dependencies (libraries, services) are ready

4. **Report Validation Results**
   - ✅ All prerequisites met → Proceed to Phase 2
   - ❌ Blockers found → Report issues, get user guidance

---

### Phase 3: Setup TaskList from Plan

> 📋 **Task Tracking**: Mark this Phase's Task as `in_progress` on entry, `completed` on completion.

**Objective**: Create comprehensive TaskList mirroring the entire plan using `TaskCreate`.

**TaskList Structure**:
```
// Register each plan task using TaskCreate
TaskCreate({subject: "[P0] Setup authentication infrastructure", description: "...", activeForm: "Setting up authentication infrastructure"})
TaskCreate({subject: "[P0] Configure OAuth2 providers", description: "depends on setup", activeForm: "Configuring OAuth2 providers"})
TaskCreate({subject: "[P1] Implement user session management", description: "...", activeForm: "Implementing user session management"})
TaskCreate({subject: "[P1] Create login/logout endpoints", description: "...", activeForm: "Creating login/logout endpoints"})
TaskCreate({subject: "[P2] Add user profile page", description: "...", activeForm: "Adding user profile page"})
TaskCreate({subject: "[P3] Implement remember me feature", description: "...", activeForm: "Implementing remember me feature"})

// Mark first task as in_progress
TaskUpdate({taskId: firstTaskId, status: "in_progress"})
```

**TaskList Principles**:
- Register ALL tasks from the plan using `TaskCreate` (no skipping)
- Order by priority: P0 → P1 → P2 → P3
- Note dependencies in task descriptions
- Mark first task as `in_progress` using `TaskUpdate`
- Exactly ONE task should be `in_progress` at any time

---

### Phase 4: Execute Tasks Sequentially

> 📋 **Task Tracking**: Mark this Phase's Task as `in_progress` on entry, `completed` on completion.

**Objective**: Implement each task following the plan's approach.

**For Each Task:**

#### 3A. Start Task
```typescript
// Mark current task as in_progress
TaskUpdate({taskId: currentTaskId, status: "in_progress"})

// Review task details
- Goal: What this task achieves
- Success Criteria: How to verify completion
- Dependencies: What must be done first
- Implementation Approach: Step-by-step guide
- Testing Strategy: How to test this task
```

#### 3B. Gather Context

Use appropriate tools based on task needs:

**Code Reading/Understanding**:
```typescript
// Get file overview
mcp__plugin_serena_serena__get_symbols_overview({relative_path: "src/auth/service.ts"})

// Find specific symbols
mcp__plugin_serena_serena__find_symbol({name_path: "AuthService/login", include_body: true})

// Find references
mcp__plugin_serena_serena__find_referencing_symbols({name_path: "login", relative_path: "src/auth/service.ts"})

// Search patterns
mcp__plugin_serena_serena__search_for_pattern({substring_pattern: "OAuth.*config"})
```

**Documentation**:
```typescript
// Get library docs
mcp__plugin_context7_context7__resolve-library-id({libraryName: "passport"})
mcp__plugin_context7_context7__get-library-docs({context7CompatibleLibraryID: "/jaredhanson/passport"})
```

**Project Management**:
```typescript
// Get JIRA details
mcp__plugin_atlassian_atlassian__jira_get_issue({issue_key: "PROJ-123"})

// Check Sentry errors
mcp__plugin_sentry_sentry__get_issue_details({organizationSlug, issueId})
```

#### 3C. Implement Task

Follow the implementation approach defined in the plan:

**Code Editing**:
```typescript
// Replace symbol body
mcp__plugin_serena_serena__replace_symbol_body({
  name_path: "AuthService/login",
  relative_path: "src/auth/service.ts",
  body: newImplementation
})

// Insert new code
mcp__plugin_serena_serena__insert_after_symbol({
  name_path: "AuthService",
  relative_path: "src/auth/service.ts",
  body: newMethodCode
})

// Rename symbols
mcp__plugin_serena_serena__rename_symbol({
  name_path: "oldName",
  relative_path: "src/auth/service.ts",
  new_name: "newName"
})
```

**Apply Risk Mitigations**:
- Refer to risk mitigation strategies in the plan
- Implement safeguards as specified
- Add error handling as noted

#### 3D. Verify Success Criteria

Check ALL success criteria for the task:

```typescript
// Use thinking tool to assess
mcp__plugin_serena_serena__think_about_task_adherence()

// For each criterion:
- [ ] Criterion 1: [Check if met]
- [ ] Criterion 2: [Check if met]
- [ ] Criterion 3: [Check if met]
```

**Run Tests**:
```bash
# Execute test commands from task's Testing Strategy
npm test src/auth/login.test.ts
pytest tests/test_auth.py -v
```

**Verify Test Results**:
- All tests pass ✅
- No regressions introduced ✅
- Coverage meets targets ✅

#### 3E. Complete Task

```typescript
// Mark task as completed
TaskUpdate({taskId: currentTaskId, status: "completed"})

// Document deviations (if any)
"✅ Task completed: [Task Name]
 - All success criteria met
 - Tests passing: [Test results]
 - Deviations: [None / List deviations]"

// Move to next task
"🔄 Moving to next task: [Next Task Name]"
```

**Progress Reporting**:
```
📊 Progress: [X/Y tasks completed]
✅ Completed: [Recent task]
🔄 Current: [Next task description]
⏳ Next: [Following task]
🚫 Blocked: [Any blocked tasks]
```

---

### Phase 5: Handle Dependencies

> 📋 **Task Tracking**: Mark this Phase's Task as `in_progress` on entry, `completed` on completion.

**Objective**: Manage task dependencies and execution order.

**Dependency Rules**:
1. Before starting a task, verify ALL dependencies are completed
2. If dependency not met, skip to next available task
3. Track blocked tasks and revisit when unblocked
4. Follow critical path identified in plan

**Example Flow**:
```
Task A (completed) → Task B (in_progress) → Task D (pending, blocked by B)
                  ↘ Task C (pending, no deps) → Can start C in parallel
```

**Handling Blocked Tasks**:
- Mark task as "pending" (not "in_progress" if blocked)
- Document blocker reason
- Move to next unblocked task
- Return to blocked task when dependency resolves

---

### Phase 5C: Database Migration Validation (Optional)

> 📋 **Task Tracking**: Mark as `in_progress`/`completed` if condition met. Mark as `deleted` if skipped.

**Objective**: Automatically detect and block dangerous DB migration patterns

**Execution Condition**: When the plan contains DB migration related tasks

**Steps**:

**1. Detect Migration Files**

```bash
# Find SQL/migration files in migrations/ or db/ directories
find . -path "*/migrations/*.sql" -o -path "*/db/migrate/*.rb" -o -path "*/migrations/*.ts"
```

**2. Analyze Dangerous Patterns**

Detect dangerous patterns using the following regular expressions:

```typescript
const dangerousPatterns = {
  // CRITICAL: Data loss risk
  notNull: /ADD COLUMN .* NOT NULL(?! DEFAULT)/i,
  dropColumn: /DROP COLUMN/i,
  dropTable: /DROP TABLE/i,

  // HIGH: Performance issues
  alterType: /ALTER COLUMN .* TYPE/i,
  addIndex: /CREATE INDEX(?! CONCURRENTLY)/i
};

// Scan each migration file
for (const file of migrationFiles) {
  const content = readFile(file);

  for (const [risk, pattern] of Object.entries(dangerousPatterns)) {
    if (pattern.test(content)) {
      warnings.push({
        file,
        risk,
        severity: (risk === 'notNull' || risk === 'dropColumn' || risk === 'dropTable')
          ? 'CRITICAL'
          : 'HIGH'
      });
    }
  }
}
```

**3. Warning and Approval Request**

When dangerous patterns are found, output warning messages in the following format:

```markdown
## ⚠️ Database Migration Risk Detected

### CRITICAL Risk
- **File**: migrations/20231209_add_user_email.sql
  - **Pattern**: `ADD COLUMN email VARCHAR(255) NOT NULL`
  - **Problem**: Existing rows cannot have NULL → Migration fails
  - **Solution**: Add DEFAULT or 2-step migration (1. ADD COLUMN with DEFAULT, 2. ALTER COLUMN DROP DEFAULT)

### HIGH Risk
- **File**: migrations/20231209_alter_user_type.sql
  - **Pattern**: `ALTER COLUMN user_type TYPE VARCHAR(50)`
  - **Problem**: Table lock occurs, long duration on large tables
  - **Solution**: Add new column → Copy data → Drop old column (Zero-downtime migration)

**Action Required**:
- Stop execution on CRITICAL risk
- Proceed with user approval for HIGH risk
```

**4. Execution Stop Logic**

```typescript
if (warnings.some(w => w.severity === 'CRITICAL')) {
  console.log('❌ CRITICAL migration risk detected - execution stopped');
  console.log('Please fix migration files and try again.');
  // Exit without returning to Phase 3 Task Execution
  process.exit(1);
}

if (warnings.some(w => w.severity === 'HIGH')) {
  console.log('⚠️ HIGH migration risk detected - user approval required');
  // Request user approval
}
```

**5. Detect Dangerous Patterns with Grep (Implementation Example)**

```bash
# NOT NULL without DEFAULT
grep -rE 'ADD COLUMN .* NOT NULL(?! DEFAULT)' migrations/

# DROP COLUMN/TABLE
grep -rE 'DROP (COLUMN|TABLE)' migrations/

# ALTER TYPE
grep -rE 'ALTER COLUMN .* TYPE' migrations/

# Non-concurrent INDEX
grep -rE 'CREATE INDEX(?! CONCURRENTLY)' migrations/
```

**Best Practices**:
- Run Phase 4C right after Phase 4, before Phase 5 (Test Generation)
- Skip this Phase if no migration files exist
- Stop immediately on CRITICAL risk (user safety first)
- For HIGH risk, output warning only and proceed (user judgment)

---

### Phase 6: Automated Test Generation (Conditional)

> 📋 **Task Tracking**: Mark as `in_progress`/`completed` if condition met. Mark as `deleted` if skipped.

**Objective**: Detect files missing tests and generate them

**Execution Condition**:
- After Phase 3 (Task Execution) completion, before Phase 6 (Testing)
- **Conditional**: When test files don't exist for changed files

**Steps**:

**1. Check Changed Files**

```bash
# Get list of modified files via Git
git diff --name-only HEAD
# Or compare with recent commit
git diff --name-only HEAD~1..HEAD
```

**2. Check Test File Existence**

```bash
# Find changed files without corresponding test files
for file in $(git diff --name-only HEAD | grep -E 'src/.*\.(ts|js)$'); do
  testfile=$(echo $file | sed 's/\.ts$/.test.ts/' | sed 's/\.js$/.test.js/')
  if [ ! -f "$testfile" ]; then
    echo "⚠️ Missing test: $file"
  fi
done
```

**3. Design Test Cases with Sequential Thinking**

When files missing tests are found, systematically analyze with Sequential Thinking:

```typescript
// Step 1: Analyze function signature
mcp__plugin_seq-think_st__sequentialthinking({
  thought: "Analyzing processPayment function: input is amount (number), output is Promise<PaymentResult>",
  thoughtNumber: 1,
  totalThoughts: 6,
  nextThoughtNeeded: true
})

// Step 2: Analyze input constraints
mcp__plugin_seq-think_st__sequentialthinking({
  thought: "Input constraints: amount must be >= 0 and <= 1,000,000",
  thoughtNumber: 2,
  totalThoughts: 6,
  nextThoughtNeeded: true
})

// Step 3: Analyze dependencies
mcp__plugin_seq-think_st__sequentialthinking({
  thought: "Dependencies: calls PaymentAPI.process() → needs mocking",
  thoughtNumber: 3,
  totalThoughts: 6,
  nextThoughtNeeded: true
})

// Step 4: Identify Edge Cases
mcp__plugin_seq-think_st__sequentialthinking({
  thought: "Edge cases: 1) amount = 0 (boundary), 2) amount = 1000000 (max), 3) amount = -1 (negative), 4) amount = 1000001 (overflow)",
  thoughtNumber: 4,
  totalThoughts: 6,
  nextThoughtNeeded: true
})

// Step 5: Identify Error Cases
mcp__plugin_seq-think_st__sequentialthinking({
  thought: "Error cases: 1) API call failure, 2) network timeout, 3) invalid response format",
  thoughtNumber: 5,
  totalThoughts: 6,
  nextThoughtNeeded: true
})

// Step 6: Complete test case design
mcp__plugin_seq-think_st__sequentialthinking({
  thought: "Test case design complete: Happy path (2), Edge cases (4), Error cases (2) - Total 8 cases",
  thoughtNumber: 6,
  totalThoughts: 6,
  nextThoughtNeeded: false
})
```

**4. Test Case Classification**

| Category | Test Case | Description |
|----------|--------------|------|
| **Happy path** | Normal amount | Returns expected result with valid input |
| **Happy path** | Minimum amount | Success with minimum valid value |
| **Edge cases** | Boundary (0) | Test minimum boundary value |
| **Edge cases** | Maximum (1000000) | Test maximum allowed value |
| **Edge cases** | Negative (-1) | Test negative input rejection |
| **Edge cases** | Overflow (1000001) | Test max value exceeded rejection |
| **Error handling** | API failure | Handle external API failure |
| **Error handling** | Timeout | Handle network timeout |

**5. Write Test Code with AAA Pattern**

**AAA Pattern (Arrange-Act-Assert)**:
- **Arrange**: Prepare objects and data needed for test
- **Act**: Execute the function/method under test
- **Assert**: Verify result matches expected value

```typescript
// Test code example (Jest)
describe('processPayment', () => {
  // ========== Happy Path ==========
  describe('정상 처리', () => {
    it('정상 금액(100)으로 결제 성공', async () => {
      // Arrange: Prepare test data
      const amount = 100;
      const expectedResult = { success: true, transactionId: 'TX123' };
      (PaymentAPI.process as jest.Mock).mockResolvedValue(expectedResult);

      // Act: Execute function
      const result = await processPayment(amount);

      // Assert: Verify result
      expect(result).toEqual(expectedResult);
      expect(PaymentAPI.process).toHaveBeenCalledWith(expect.objectContaining({
        amount: 100
      }));
    });
  });

  // ========== Edge Cases ==========
  describe('경계값 테스트', () => {
    it('음수 금액(-1)으로 에러 발생', async () => {
      // Arrange
      const amount = -1;

      // Act & Assert
      await expect(processPayment(amount))
        .rejects
        .toThrow('Invalid amount');
    });
  });

  // ========== Error Cases ==========
  describe('에러 처리', () => {
    it('API 호출 실패 시 에러 전파', async () => {
      // Arrange
      const amount = 100;
      const apiError = new Error('API Error');
      (PaymentAPI.process as jest.Mock).mockRejectedValue(apiError);

      // Act & Assert
      await expect(processPayment(amount))
        .rejects
        .toThrow('API Error');
    });
  });
});
```

**6. Given/When/Then Format (Alternative)**

```typescript
// BDD style test
describe('processPayment', () => {
  it('정상 금액으로 결제 성공', async () => {
    // Given: Valid amount is provided
    const amount = 100;
    const expectedResult = { success: true };
    mockPaymentAPI(expectedResult);

    // When: Payment processing is executed
    const result = await processPayment(amount);

    // Then: Success result is returned
    expect(result).toEqual(expectedResult);
  });
});
```

**7. Verify Generated Tests**

```bash
# Run generated test file
npm test -- payment.test.ts

# Check coverage
npm test -- payment.test.ts --coverage
```

**8. Update Report**

Add generated test results to execution report:

```markdown
## 📝 Auto-Generated Tests

### src/api/payment.test.ts (NEW)
- **Test Cases**: 8 generated
- **Coverage**: Line 92%, Branch 88%
- **Result**: ✅ 8/8 passed
- **Generation Time**: 45s

### src/utils/validator.test.ts (NEW)
- **Test Cases**: 12 generated
- **Coverage**: Line 95%, Branch 90%
- **Result**: ✅ 12/12 passed
- **Generation Time**: 30s

**Total Tests Added**: 20
**Average Coverage**: 93.5%
```

**Best Practices**:
- Run Phase 5 right after Phase 3 (Implementation), before Phase 6 (Testing)
- Skip this Phase if no missing tests
- If test generation fails, output warning only and proceed (non-blocking)
- Always run generated tests to verify

---

### Phase 7: AC Achievement Report (Required)

> 📋 **Task Tracking**: Mark this Phase's Task as `in_progress` on entry, `completed` on completion.

**Objective**: Automatically verify and report AC achievement after implementation

**Execution Condition**:
- After Phase 5 (Test Generation) completion
- When linked to a JIRA issue

**Steps**:

**1. Call requirement-validator Agent (Mode 3)**

First, collect changed files via Git diff:

```bash
git diff --name-only HEAD
```

Then use `Task` tool to invoke the requirement-validator agent:

```yaml
Tool: Task
Args:
  subagent_type: "wf:requirement-validator"
  description: "AC post-validation"
  prompt: |
    Mode 3: Post-validation

    구현 결과가 모든 AC를 충족하는지 검증합니다.

    Input:
    - JIRA issue key: {JIRA_KEY}
    - Git diff 결과: {changed_files}

    Output:
    - AC 구현 상태 리포트
    - 미구현 AC 목록 (있는 경우)
```

**2. Analyze Results and Update TaskList**

```typescript
// Add unimplemented AC to TaskList
IF (unimplemented AC exists):
    TaskCreate({
      subject: "Handle unimplemented AC: Implement AC#2 'Account lock after 5 failures'",
      description: "AC#2 미구현 - 5회 실패 시 계정 잠금 기능 구현 필요",
      activeForm: "Handling unimplemented AC"
    })
```

**3. Output AC Achievement Report**

```markdown
## 📊 AC Implementation Status

| AC | Location | Status | Test | Coverage |
|----|----------|--------|------|----------|
| AC#1 | [UserService.ts:42](src/auth/UserService.ts#L42) | ✅ Done | ✅ Yes | 85% |
| AC#2 | ❌ Not implemented | Not implemented | ❌ No | - |
| AC#3 | [TokenService.ts:15](src/auth/TokenService.ts#L15) | ✅ Done | ✅ Yes | 90% |

**Total AC Achievement**: 66% (2/3)

### Next Actions

🔴 **CRITICAL**: AC#2 "Account lock after 5 failures" is not implemented!

**Recommendations**:
1. Implement LoginAttemptService
2. Add failure counter Redis storage logic
3. Implement account lock API after 5 failures
4. Write tests (Happy path + Edge cases)
5. Re-run Phase 6 to re-verify

**Added to TaskList** ✅
```

**4. Graceful Degradation When No JIRA Issue**

```typescript
IF (no JIRA issue):
    "ℹ️ Skipping AC verification - no JIRA issue linked."
    → Skip Phase 6, proceed to Phase 7
```

---

### Phase 7.5: Independent QA Gate (wf:qa skill spawn)

> 📋 **Task Tracking**: Mark this Phase's Task as `in_progress` on entry, `completed` on completion.

> **Why this phase exists**: Phase 6 (auto test recovery) and Phase 7 (AC Achievement Report) are both run by the same session that wrote the code. That session is structurally biased to declare its own work done. Phase 7.5 hands acceptance verification off to **`wf:qa`** — an independent skill that re-executes the original REPORT's reproduction scenarios and the PLAN's success criteria from scratch in the actual environment (test runs, API calls, UI checks via agent-browser, DB state). `wf:qa` must return PASS before this skill hands off to `record`.

This phase is the load-bearing complement to plan's external review gate (Phase 3 of `wf:plan`). Together they enforce: **the executor is never the verifier.**

#### Step A: qa skill spawn

Invoke `wf:qa` as a Skill (not as a sub-agent — qa is user-invocable and runs as a skill):

```
Tool: Skill
Args:
  skill: "wf:qa"
  args: |
    issue_id: {ISSUE_ID}            # JIRA / GitHub / repo-specific issue id
    report_path: {REPORT_PATH}      # [ISSUE_ID]_REPORT.md from analyze
    plan_path: {PLAN_PATH}          # [FEATURE]_PLAN.md from plan (post-LGTM)
    branch: {CURRENT_BRANCH}        # e.g. feat/auth-middleware-merge
```

If `wf:qa` is not installed (skill resolution fails), output:

```
⚠️ wf:qa skill is not available — install the wf plugin's qa skill before
   this phase can run. Falling back to manual verification request.
```

…and ask the user via AskUserQuestion whether to proceed without independent QA (NOT recommended — explain the risk) or stop here.

#### Step B: Read the QA verdict

`wf:qa` writes its result to `[ISSUE_ID]_QA.md` (same convention as REPORT/PLAN). Read that file. Locate the final `VERDICT:` line.

#### Step C: Verdict gate

| Verdict | Action |
|---------|--------|
| `PASS` | Proceed to Phase 8 (Testing and Verification — quick smoke + final commit prep). |
| `FAIL` | Read `[ISSUE_ID]_QA.md` "FAIL 시 수정 요청" section. Apply the patch-level suggestions back in Phase 4 (Execute Tasks). After fixes, re-run `wf:qa` (loop back to Step A). Do NOT proceed to record. Do NOT self-declare PASS. |

The Worker does not produce its own PASS verdict for this phase. The exit gate is literally the contents of `[ISSUE_ID]_QA.md`.

#### Step D: When QA is genuinely not applicable

A small subset of changes legitimately have nothing for `wf:qa` to verify (e.g., a typo fix in a comment, a CHANGELOG-only commit, formatting-only changes). For those, `wf:qa` itself returns PASS quickly with a "trivial / no scenario to verify" note in `[ISSUE_ID]_QA.md`. **Do not skip this phase to save time** — still spawn `wf:qa` and let it produce that note. The audit artifact is what gives `record` (Phase 9) confidence to publish.

> **Anti-pattern alert**: Pre-v3.30 versions of `execute` exited via Phase 7 → Phase 8 → record without any independent acceptance gate. Test pass ≠ requirements met. If you find yourself thinking "Phase 7.5 is overhead, let me skip just this once", stop — that's exactly the failure mode the gate exists to prevent.

---

### Phase 8: Testing and Verification

> 📋 **Task Tracking**: Mark this Phase's Task as `in_progress` on entry, `completed` on completion.

**Objective**: Comprehensively test all implemented functionality with automatic failure recovery.

---

#### Step A: Run All Tests

Execute comprehensive test suite:

1. **Unit Tests**
   ```bash
   # Run unit tests for modified modules
   npm test src/**/*.test.ts --coverage
   pytest tests/unit/ -v --cov
   ```

2. **Integration Tests**
   ```bash
   # Test component interactions
   npm run test:integration
   pytest tests/integration/ -v
   ```

3. **Manual Tests**
   - Follow manual test cases from plan
   - Verify UI/UX behavior
   - Check error messages and edge cases

4. **Performance Tests** (if specified)
   ```bash
   npm run test:performance
   ```

5. **Security Tests** (if specified)
   ```bash
   npm run test:security
   ```

---

#### Step B: Analyze Test Results & Verification

**Comprehensive Verification**:

Run ALL verification checks:

```typescript
const verificationResults = {
  // Test Results
  unitTests: runUnitTests(),
  integrationTests: runIntegrationTests(),
  manualTests: runManualTests(),

  // Quality Checks
  successCriteria: checkAllSuccessCriteria(),
  noRegression: checkNoRegression(),
  codeStandards: checkCodeStandards(),
  noConsoleErrors: checkConsoleErrors(),
  performance: checkPerformance(),
  security: checkSecurity()
};

const allPassed = Object.values(verificationResults).every(result => result.passed);
```

**Exit Condition Check**:

```typescript
IF (allPassed):
  → ✅ All tests & verifications passed!
  → Skip to "Execution Complete" section

ELSE (any check failed):
  → ❌ Failures detected in: {failedChecks}
  → Proceed to Step C (Auto-Recovery Loop)
```

---

#### Step C: Test Failure Auto-Recovery Loop

⚠️ **AUTOMATIC RECOVERY**: This loop automatically analyzes failures and attempts fixes.

**Loop Variables**:
- `retry_count = 0`
- `max_retries = 3`

**WHILE (tests fail AND retry_count < max_retries) DO:**

##### C-1: Analyze Failure Root Cause

Use `mcp__plugin_seq-think_st__sequentialthinking` to classify failure type:

```typescript
// Analyze verification failures
const failureType = classify({
  verificationResults,
  testOutput,
  implementedCode,
  planRequirements
});

// Failure types:
// 1. IMPLEMENTATION_BUG: Code has bugs (wrong logic, syntax error, etc.)
// 2. PLAN_DESIGN_FLAW: Plan itself is flawed (wrong approach, missing requirements)
// 3. SUCCESS_CRITERIA_UNMET: Success criteria not achieved
// 4. CODE_STANDARDS_VIOLATION: Linting, formatting, convention violations
// 5. PERFORMANCE_ISSUE: Performance below acceptable thresholds
// 6. SECURITY_ISSUE: Security vulnerability detected
// 7. REGRESSION: Existing functionality broken
// 8. ENVIRONMENT_ISSUE: External issue (DB not running, API down, etc.)
```

**Classification Criteria**:

| Type | Indicators | Example |
|------|-----------|---------|
| **IMPLEMENTATION_BUG** | Logic error, wrong calculation, missing null check | `Expected 100, got 0` → calculation bug |
| **PLAN_DESIGN_FLAW** | Fundamental approach wrong, missing AC, architectural issue | Test expects feature X, but plan doesn't include X |
| **SUCCESS_CRITERIA_UNMET** | Task completed but success criteria not met | "User can login" criterion failed - login flow broken |
| **CODE_STANDARDS_VIOLATION** | ESLint errors, formatting issues, naming conventions | `Unexpected var, use let/const instead` |
| **PERFORMANCE_ISSUE** | Response time, memory usage, query performance | API response 5s (target: <500ms) |
| **SECURITY_ISSUE** | Vulnerabilities, exposed secrets, injection risks | SQL injection risk, exposed API key |
| **REGRESSION** | Previously working feature now broken | User logout worked before, now throws error |
| **ENVIRONMENT_ISSUE** | Connection errors, missing dependencies, permission issues | `ECONNREFUSED`, `Module not found` |

##### C-2: Apply Fix Strategy

**Strategy 1: Implementation Bug** (코드 수정)

```typescript
IF (failureType === "IMPLEMENTATION_BUG"):
  1. Identify buggy code location from test output
  2. Fix the implementation using Edit/Write tools
  3. Re-run failed tests
  4. IF (tests pass):
       → Continue to Step C-4
     ELSE:
       → retry_count++, continue loop
```

**Strategy 2: Plan Design Flaw** (계획 재작성 → 재실행)

```typescript
IF (failureType === "PLAN_DESIGN_FLAW"):

  Output: "🔄 Plan design flaw detected - invoking plan skill to revise"

  1. ⚠️ **Invoke plan skill with failure context**:

     Tool: Skill
     Args:
       skill: "wf:plan"
       args: |
         REVISION MODE: Fix plan based on test failures

         Original Plan: [FEATURE]_PLAN.md
         Test Failures:
         {failure_details}

         Root Cause: {root_cause_analysis}

         Required Changes:
         - {required_change_1}
         - {required_change_2}

  2. Wait for revised plan: [FEATURE]_PLAN_v2.md

  3. ⚠️ **Re-execute from Phase 3 with revised plan**:
     - Load revised plan
     - Re-setup TaskList from revised plan
     - Re-execute all tasks with new approach
     - Re-run tests

  4. IF (tests pass):
       → ✅ Plan revision successful, exit loop
     ELSE:
       → retry_count++, continue loop
```

**Strategy 3: Success Criteria Unmet** (코드 수정 또는 기준 재검토)

```typescript
IF (failureType === "SUCCESS_CRITERIA_UNMET"):

  Output: "⚠️ Success criteria not met - analyzing gap"

  1. Identify which criteria failed:
     - Compare plan success criteria vs actual behavior
     - Document gaps

  2. Determine if fixable with code changes:
     IF (fixable with implementation):
       → Fix code to meet criteria
       → Re-run verification
     ELSE (criteria unrealistic or plan flaw):
       → Invoke plan skill to revise criteria
       → Re-execute with updated plan

  3. retry_count++, continue loop
```

**Strategy 4: Code Standards Violation** (자동 수정)

```typescript
IF (failureType === "CODE_STANDARDS_VIOLATION"):

  Output: "🔧 Code standards violation - auto-fixing"

  1. Run auto-fixers:
     npm run lint:fix
     npm run format
     prettier --write .

  2. For unfixable violations:
     - Manually fix based on linter output
     - Update code to follow conventions

  3. Re-run verification
  4. retry_count++, continue loop
```

**Strategy 5: Performance Issue** (최적화)

```typescript
IF (failureType === "PERFORMANCE_ISSUE"):

  Output: "⚡ Performance issue - optimizing"

  1. Profile performance bottleneck:
     - Identify slow queries, loops, API calls
     - Use Sequential Thinking to find root cause

  2. Apply optimization strategy:
     - Add caching
     - Optimize queries (add indexes, reduce N+1)
     - Use pagination
     - Lazy loading

  3. IF (optimization insufficient):
       → Invoke plan skill to redesign approach
       → Re-execute with optimized plan

  4. Re-run performance tests
  5. retry_count++, continue loop
```

**Strategy 6: Security Issue** (보안 패치)

```typescript
IF (failureType === "SECURITY_ISSUE"):

  Output: "🔒 Security issue - patching"

  1. Analyze security vulnerability:
     - SQL injection risk → Use parameterized queries
     - XSS risk → Sanitize inputs
     - Exposed secrets → Move to env vars
     - CSRF risk → Add CSRF tokens

  2. Apply security fix:
     - Fix vulnerable code
     - Add validation/sanitization
     - Update dependencies if needed

  3. Re-run security tests
  4. retry_count++, continue loop
```

**Strategy 7: Regression** (롤백 또는 수정)

```typescript
IF (failureType === "REGRESSION"):

  Output: "⏮️ Regression detected - analyzing"

  1. Identify what broke:
     - Use git diff to find changes
     - Identify affected components

  2. Fix regression:
     IF (simple fix):
       → Fix breaking change
       → Ensure both old and new features work
     ELSE (fundamental conflict):
       → Invoke plan skill to redesign
       → Resolve conflict in plan
       → Re-execute

  3. Re-run all tests (including regression tests)
  4. retry_count++, continue loop
```

**Strategy 8: Environment Issue** (사용자 개입 필요)

```typescript
IF (failureType === "ENVIRONMENT_ISSUE"):

  Output: "⚠️ Environment issue detected - user intervention required"

  1. Document environment problem:
     - Error message
     - Missing dependency/service
     - Required fix

  2. Ask user for guidance using AskUserQuestion:
     - "Fix environment and retry"
     - "Skip this test (not recommended)"
     - "Abort execution"

  3. STOP LOOP → Exit to Error Handling
```

##### C-3: Output Retry Status

```markdown
🔄 Auto-Recovery Attempt #{retry_count + 1}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Failure Type: {IMPLEMENTATION_BUG | PLAN_DESIGN_FLAW}
Strategy: {Fix code | Revise plan}
Action Taken: {description}

Next: Re-running tests...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

##### C-4: Increment Retry Counter

```typescript
retry_count++
```

##### C-5: Re-run Tests

Re-execute test suite from Step A

##### C-6: Check Exit Condition

```typescript
IF (all tests pass):
  → ✅ Tests passed after retry!
  → EXIT LOOP → Success

ELSE IF (retry_count >= max_retries):
  → ❌ Max retries (3) reached
  → EXIT LOOP → Ask user for guidance

ELSE:
  → Continue to C-1 (next retry iteration)
```

**END WHILE**

---

#### Step D: Final Decision

After exiting the loop:

```typescript
IF (all tests pass):
  → ✅ Testing successful!
  → Proceed to "Execution Complete" section

ELSE (max retries reached):
  → ❌ Unable to fix after 3 attempts
  → Output failure summary
  → Ask user for manual intervention

  Use AskUserQuestion:
    - "Manually fix and resume"
    - "Abort execution and investigate"
```

---

**Verification Checklist**:
```
- ✓ All tasks marked as completed in TaskList
- ✓ All success criteria met for all tasks
- ✓ Unit tests passing (after auto-recovery if needed)
- ✓ Integration tests passing
- ✓ Manual tests verified
- ✓ No regression in existing functionality
- ✓ Code follows project standards
- ✓ No console errors or warnings
- ✓ Performance acceptable
- ✓ Security checks passed (if applicable)
```

---

## ✅ Execution Complete - Next: Run `record` Skill

**After execute skill completion, you MUST run `record` skill**:

```
Run record skill
```

Tasks handled by `record` skill:
- ✅ Update README
- ✅ Write CHANGELOG
- ✅ Add architectural decisions to CLAUDE.md
- ✅ Save learnings to Serena memory
- ✅ Clean up workflow artifacts (*_PLAN.md, *_REPORT.md)
- ✅ Git commit/push
- ✅ Update JIRA issue

**⚠️ IMPORTANT**: Do not perform documentation in execute. Documentation is handled centrally in record.

---

## Error Handling

### If a Task Fails

1. **Document the Failure**
   ```
   "❌ Task Failed: [Task Name]

   Error Details:
   - Error message: [error]
   - Context: [what was being attempted]
   - Stack trace: [if applicable]
   ```

2. **Check Rollback Procedure**
   - Refer to plan's rollback procedure (if defined)
   - Undo changes if necessary
   - Restore to known good state

3. **Mark Task as Blocked**
   ```typescript
   // Keep task as pending (do NOT mark as completed)
   TaskUpdate({taskId: currentTaskId, status: "pending"})
   ```
   - Do NOT mark as "completed"
   - Document blocker reason

4. **Create Sub-tasks to Resolve**
   ```typescript
   TaskCreate({subject: "[BLOCKER] Fix [specific issue]", description: "...", activeForm: "Fixing blocker"})
   TaskCreate({subject: "[RETRY] [Original Task]", description: "...", activeForm: "Retrying original task"})
   ```

5. **Ask for User Guidance**
   ```
   "⚠️ Blocker Encountered

   I've encountered an issue with [Task Name]:
   [Description of problem]

   Options:
   1. [Option 1 with pros/cons]
   2. [Option 2 with pros/cons]
   3. [Option 3 with pros/cons]

   Which approach would you like me to take?"
   ```

### If Plan Needs Adjustment

1. **Pause Execution**
   ```
   "⏸️ Execution Paused

   I need to adjust the plan because:
   [Reason for adjustment]"
   ```

2. **Explain the Issue**
   ```
   "Issue: [Clear description]

   Why adjustment needed:
   - [Reason 1]
   - [Reason 2]

   Current plan assumes: [assumption]
   Reality: [actual situation]"
   ```

3. **Propose Modifications**
   ```
   "Proposed plan adjustments:

   Original approach:
   [Original plan excerpt]

   Modified approach:
   [Proposed change]

   Impact:
   - Timeline: [change]
   - Dependencies: [affected tasks]
   - Risk: [new risks or mitigations]"
   ```

4. **Wait for Approval**
   - Do NOT proceed without user approval
   - Present options clearly
   - Explain trade-offs

---

## Execution Principles

1. **Follow the Plan**: Stick to defined approach unless blocked
2. **Track Everything**: Use TaskUpdate after EACH task (not in batches)
3. **One Task at a Time**: Exactly ONE task "in_progress" at any moment
4. **Verify Thoroughly**: Check ALL success criteria before marking complete
5. **Communicate Issues**: Report problems immediately, don't guess solutions
6. **Test Continuously**: Verify each task doesn't break existing functionality
7. **Run `record` After Completion**: Documentation and cleanup handled by record skill

---

## Progress Tracking Format

**Continuous Updates** (after each task):
```
📊 Progress: [X/Y tasks completed]

✅ Completed:
- [Task 1]: [Brief result]
- [Task 2]: [Brief result]

🔄 Current: [Task being worked on]

⏳ Next: [Next task in queue]

🚫 Blocked: [Any blocked tasks]
- [Blocked Task]: Waiting for [dependency/resolution]
```

---

## Final Execution Summary Template

```markdown
# Execution Summary: [Plan Name]

**Date**: [Completion date]
**Duration**: [Total time]

---

## ✅ Tasks Completed: [X/Y]

### Priority 0 (Critical)
- [Task 1] ✅ [Brief outcome]
- [Task 2] ✅ [Brief outcome]

### Priority 1 (High)
- [Task 3] ✅ [Brief outcome]

### Priority 2 (Medium)
- [Task 4] ✅ [Brief outcome]

### Priority 3 (Low)
- [Task 5] ✅ [Brief outcome]

---

## ✅ Success Criteria Met: [X/Y]

- [Criterion 1] ✅ Verified
- [Criterion 2] ✅ Verified
- [Criterion 3] ✅ Verified

---

## 🧪 Testing Results

### Unit Tests
- Status: ✅ All passing
- Coverage: [X%]
- Files tested: [count]

### Integration Tests
- Status: ✅ All passing
- Test cases: [count]

### Manual Tests
- Status: ✅ Verified
- Test scenarios: [count]

### Performance Tests
- Status: ✅ Passed (if applicable)
- Metrics: [key metrics]

### Security Tests
- Status: ✅ Passed (if applicable)
- Checks: [security checks performed]

---

## 🔄 Next Step: Run `record` Skill

**⚠️ IMPORTANT**: Run `record` skill after execute completion!

Handled by `record` skill:
- ✅ Update README, CHANGELOG, CLAUDE.md
- ✅ Save learnings to Serena memory
- ✅ Clean up workflow artifacts
- ✅ Git commit/push
- ✅ Update JIRA issue

---

## ⚠️ Issues Encountered

### Issue 1: [Issue description]
- **Impact**: [How it affected execution]
- **Resolution**: [How it was resolved]
- **Prevention**: [How to avoid in future]

### Issue 2: [Issue description]
- **Impact**: [How it affected execution]
- **Resolution**: [How it was resolved]
- **Prevention**: [How to avoid in future]

---

## 🎯 Project Management Updates

### JIRA
- ✅ Issue [ISSUE-ID] updated to "Done"
- ✅ Implementation notes added to issue
- ✅ Time logged (if applicable)

### Sentry
- ✅ Related errors resolved (if applicable)
- ✅ Issues closed: [issue IDs]

### GitHub
- ✅ Pull request created (if applicable): [PR link]
- ✅ Commits linked to issues

---

## 📊 Metrics

- **Total tasks**: [count]
- **Tasks completed**: [count]
- **Success rate**: [X%]
- **Test coverage**: [X%]
- **Time estimate vs actual**: [comparison]
- **Blocked tasks resolved**: [count]

---

## 🔄 Next Steps

### Immediate
- [Next step 1]
- [Next step 2]

### Future Considerations
- [Future consideration 1]
- [Future consideration 2]

---

## 💡 Lessons Learned

### What Went Well
- [Success 1]
- [Success 2]

### What Could Be Improved
- [Improvement area 1]
- [Improvement area 2]

### Recommendations for Future Plans
- [Recommendation 1]
- [Recommendation 2]

---

**Execution Complete** ✅

All plan objectives achieved. Project documentation updated. Temporary files cleaned up.
```

---

## Tips for Successful Execution

### Before Starting
- ✓ Ensure plan is approved (not draft)
- ✓ Verify all dependencies available
- ✓ Check required tools and access
- ✓ Review risk mitigations in plan
- ✓ Understand critical path

### During Execution
- ✓ Update TaskList after EACH task (not batched)
- ✓ Keep exactly ONE task as "in_progress"
- ✓ Verify success criteria before marking complete
- ✓ Run tests continuously, not just at the end
- ✓ Document issues as they occur
- ✓ Ask for guidance when blocked, don't guess

### After Execution
- ✓ Verify ALL tests pass
- ✓ Present comprehensive execution summary
- ✓ **Run `record` skill** for documentation and cleanup

---

### Phase 9: Next Step Confirmation

After completing all tests and verification, ask the user whether to proceed to documentation.

**Use `AskUserQuestion` tool:**

```yaml
questions:
  - question: "구현이 완료되었습니다. 다음 단계로 진행할까요?"
    header: "Next"
    options:
      - label: "record 스킬 실행 (Recommended)"
        description: "문서화, CHANGELOG 작성, Git commit/push를 수행합니다"
      - label: "여기서 종료"
        description: "구현만 완료하고 종료합니다 (문서화는 나중에)"
```

- **If "record 스킬 실행" selected**: Invoke the `record` skill
  - Output: `✅ record 스킬을 실행합니다...`
- **If "여기서 종료" selected**: End the workflow with reminder
  - Output: `✅ 구현이 완료되었습니다. 나중에 record 스킬을 실행하여 문서화를 완료하세요.`

**Tasks handled by `record` skill:**
- Update README
- Write CHANGELOG
- Add architectural decisions to CLAUDE.md
- Save learnings to Serena memory
- Clean up workflow artifacts (*_PLAN.md, *_REPORT.md)
- Git commit/push
- Update JIRA issue

**⚠️ IMPORTANT**: Do not perform documentation in execute. Documentation is handled centrally in record.

---

## Resources

This skill does not require additional resource directories (scripts/, references/, or assets/). All execution logic is contained within this SKILL.md file, and the skill relies on Claude's ability to:

1. Use TaskCreate/TaskUpdate for task tracking
2. Use Serena MCP tools for code operations
3. Use Atlassian MCP tools for project management
4. Use Sentry MCP tools for error tracking
5. Use Context7 MCP tools for documentation
6. Follow the 9-phase systematic execution process
7. Maintain comprehensive progress tracking

**Note**: Documentation and file cleanup are handled by `record` skill.
