---
name: analyze
description: Systematically analyze the root cause of bugs and issues using multi-perspective investigation. Use when analyzing JIRA issues, Sentry errors, or investigating bug reports. Generates [ISSUE_ID]_REPORT.md with root cause analysis, code locations, reproduction steps, and fix recommendations.
---

# Analyze Issue Root Cause

## ⚠️ CRITICAL LANGUAGE POLICY

**DEFAULT LANGUAGE: KOREAN (한국어)**

ALL outputs, reports, analysis, and communications MUST be in **KOREAN** unless explicitly requested otherwise by the user.

- ✅ **Analysis reports**: Write in Korean
- ✅ **Root cause explanations**: Write in Korean
- ✅ **Reproduction steps**: Write in Korean
- ✅ **Recommendations**: Write in Korean
- ✅ **User communication**: Respond in Korean

**Exception**: If the user writes in another language, match that language for responses.

**This is a MANDATORY requirement. Do NOT default to English.**

---

## Overview

Systematically analyze bugs and issues to identify root causes using a structured, multi-perspective approach. This skill combines JIRA/Atlassian integration, Sentry error tracking, codebase investigation with Serena, and sequential thinking to produce comprehensive analysis reports.

**Output**: `[ISSUE_ID]_REPORT.md` file containing root cause analysis, affected code locations, reproduction steps, and remediation recommendations.

## When to Use This Skill

Use this skill when:
- Analyzing JIRA issues or bug reports
- Investigating Sentry errors or production incidents
- User requests "analyze this issue", "what's causing this bug", "investigate [ISSUE-ID]"
- Need systematic root cause analysis before planning a fix
- Debugging complex problems requiring multi-source investigation

## Analysis Workflow

### Phase 0: Branch Validation

⚠️ **CRITICAL: DO NOT SKIP PHASE 0**

> **MANDATORY REQUIREMENT**:
>
> - Phase 0 is the **FIRST step** of this skill
> - You **MUST** execute Phase 0 **BEFORE** proceeding to Phase 1
> - **DO NOT** assume you are on the correct branch
> - **ALWAYS** verify branch status using the MCP tool below
> - **NEVER** start analysis (Phase 1) without completing Phase 0
>
> **Why this matters**:
> - Prevents accidental commits to main/master branch
> - Ensures work is isolated in a feature branch
> - Maintains clean git history

**Objective**: Verify that you are working on a feature branch, and create one if needed.

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

**2. Create Feature Branch (If Needed)**

If `is_protected` is `true`, use `create_feature_branch` MCP tool:

```
Tool: create_feature_branch
Args:
  - branch_name: "feature/JIRA-123" (JIRA ID에서 추출)
Returns:
  - success: 성공 여부
  - branch: 생성된 브랜치 이름
  - message: 결과 메시지
```

**Branch Naming Convention**:
- JIRA ID가 있으면: `feature/JIRA-123`
- JIRA ID가 없으면: 사용자에게 브랜치 이름 요청

**3. Proceed to Phase 1**

- Execute existing Phase 1-6
- Save REPORT file in Phase 6

---

### Phase 1: Context Gathering

Gather comprehensive context from all available sources:

**1. JIRA Issue Analysis** (if JIRA link/ID provided)
- Use `mcp__plugin_workflow-skills_atlassian__jira_get_issue` to fetch issue details
- Extract:
  - Issue summary and description
  - Reproduction steps
  - Expected vs actual behavior
  - Environment details
  - Attachments and linked resources
  - Comments and discussion threads
- Check for linked issues or sub-tasks

**2. Sentry Error Investigation** (if Sentry URL or error mentioned)

⚠️ **IMPORTANT**: ALWAYS search Sentry for related errors, even if not explicitly mentioned in JIRA.

**A. Search for Related Errors by Natural Language**

```typescript
// Search for errors related to the issue description
// Use natural language queries based on the issue
mcp__plugin_workflow-skills_sentry__search_events({
  organizationSlug: 'your-org',
  naturalLanguageQuery: 'database connection timeout errors in the last 7 days'
  // or: 'authentication failures for user login'
  // or: 'null pointer exceptions in payment service'
})
```

**B. Search for Specific Error Patterns**

```typescript
// If you have error message or stack trace
mcp__plugin_workflow-skills_sentry__search_events({
  organizationSlug: 'your-org',
  naturalLanguageQuery: 'TypeError Cannot read property of undefined in checkout.js'
})

// Search by time range
mcp__plugin_workflow-skills_sentry__search_events({
  organizationSlug: 'your-org',
  naturalLanguageQuery: 'all errors in payment-service from last 24 hours'
})
```

**C. Get Detailed Error Information**

```typescript
// If Sentry URL provided (e.g., https://sentry.io/issues/PROJECT-123/)
mcp__plugin_workflow-skills_sentry__get_issue_details({
  issueUrl: 'https://sentry.io/issues/PROJECT-123/'
})

// Or use issue ID
mcp__plugin_workflow-skills_sentry__get_issue_details({
  organizationSlug: 'your-org',
  issueId: 'PROJECT-123'
})
```

**D. Analyze Error Counts and Statistics**

```typescript
// Count frequency of specific errors
mcp__plugin_workflow-skills_sentry__search_events({
  organizationSlug: 'your-org',
  naturalLanguageQuery: 'count of database timeout errors today'
})

// Check error trends
mcp__plugin_workflow-skills_sentry__search_events({
  organizationSlug: 'your-org',
  naturalLanguageQuery: 'total errors in authentication module this week'
})
```

**E. Extract Key Information**

From Sentry results, extract:
- **Stack traces**: Exact error location (filename, line number)
- **Error messages**: Error message and type
- **Breadcrumbs**: User behavior tracking before error
- **Context**: Request info, environment variables, user data
- **Frequency**: Error frequency and affected user count
- **Trends**: Error increase/decrease patterns over time
- **Related events**: Other errors from same user/session

**F. Common Search Patterns**

```typescript
// By component/service
'errors in payment-service'
'exceptions in user-authentication'

// By error type
'TypeError exceptions'
'database connection errors'
'404 not found errors'

// By time and severity
'critical errors in the last hour'
'all exceptions since deployment yesterday'

// By user impact
'errors affecting more than 100 users'
'high frequency errors today'
```

**3. Additional Context**
- Read any file paths or code references provided
- Analyze error logs or screenshots
- Check Confluence documentation if referenced

### Phase 2: Hypothesis Generation

Use `mcp__plugin_sequential-thinking_sequential-thinking__sequentialthinking` to systematically explore multiple perspectives:

**Generate Initial Hypotheses**

Consider various possible root causes:
- Code logic errors (off-by-one, null checks, type mismatches)
- Race conditions or concurrency issues
- Resource leaks or memory problems
- Configuration issues
- Dependency version conflicts
- Environmental differences
- Data quality or edge cases
- Integration issues with external services

**Multi-Perspective Analysis**

For each hypothesis, evaluate:
- **Likelihood**: How probable given the symptoms?
- **Evidence**: What observations support or contradict this?
- **Impact**: How severe would this issue be?
- **Complexity**: How difficult to fix?

**Systematic Elimination**

Use logical reasoning to eliminate unlikely causes:
- Cross-reference with stack traces
- Check timing of deployments vs issue occurrence
- Verify affected components
- Consider scope (all users vs specific conditions)

### Phase 3: Codebase Investigation

Use Serena tools efficiently for targeted code exploration:

**1. Targeted Code Exploration**
- `mcp__plugin_workflow-skills_serena__get_symbols_overview` - Understand file structure
- `mcp__plugin_workflow-skills_serena__find_symbol` - Locate specific functions/classes
- `mcp__plugin_workflow-skills_serena__find_referencing_symbols` - Trace execution flow
- `mcp__plugin_workflow-skills_serena__search_for_pattern` - Find error messages or patterns

**2. Execution Flow Tracing**
- Map the path from user action to error
- Identify all components in the flow
- Look for conditional branches
- Check error handling and validation logic

**3. Recent Changes Analysis** (if applicable)
- Use GitHub MCP to find recent changes
- Correlate timing with issue occurrence
- Review related code modifications

### Phase 3D: Code Complexity Assessment (Conditional)

**Objective**: Detect complex code and generate refactoring suggestions

**Execution Condition**:
- After confirming affected files in Phase 3
- **Conditional**: When code with Cyclomatic complexity > 10 OR function length > 50 lines is found

**Steps**:

**1. Analyze Complexity with Serena**

```typescript
// Get symbol info for affected files
mcp__plugin_workflow-skills_serena__find_symbol({
  name_path_pattern: "UserService/login",
  relative_path: "src/services/UserService.ts",
  include_body: true
})
```

**2. Measure Complexity and Establish Refactoring Strategy with Sequential Thinking**

```typescript
// Step 1: Measure complexity
mcp__plugin_sequential-thinking_sequential-thinking__sequentialthinking({
  thought: "Measuring cyclomatic complexity of UserService/login function: 8 if statements, 2 for loops, 1 switch statement → complexity = 11 (exceeds threshold of 10)",
  thoughtNumber: 1,
  totalThoughts: 5,
  nextThoughtNeeded: true
})

// Step 2: Analyze function length
mcp__plugin_sequential-thinking_sequential-thinking__sequentialthinking({
  thought: "Measuring function length: 85 lines total → exceeds threshold (50 lines). Reduced readability, possibly multiple responsibilities",
  thoughtNumber: 2,
  totalThoughts: 5,
  nextThoughtNeeded: true
})

// Step 3: Responsibility analysis (SRP)
mcp__plugin_sequential-thinking_sequential-thinking__sequentialthinking({
  thought: "Responsibility analysis: 1) User authentication, 2) Session management, 3) Logging, 4) Error handling → 4 responsibilities (SRP violation)",
  thoughtNumber: 3,
  totalThoughts: 5,
  nextThoughtNeeded: true
})

// Step 4: Code Smells detection
mcp__plugin_sequential-thinking_sequential-thinking__sequentialthinking({
  thought: "Code Smells detected: Duplicate code found 3 times (validateUser logic), Magic Numbers 2 instances (3.14, 0.05)",
  thoughtNumber: 4,
  totalThoughts: 5,
  nextThoughtNeeded: true
})

// Step 5: Determine refactoring strategy
mcp__plugin_sequential-thinking_sequential-thinking__sequentialthinking({
  thought: "Refactoring strategy: 1) Extract Method for validateUser(), 2) Extract Class for SessionManager, 3) Replace Magic Number with Named Constant",
  thoughtNumber: 5,
  totalThoughts: 5,
  nextThoughtNeeded: false
})
```

**3. Refactoring Decision Criteria**

| Metric | Threshold | Description |
|------|--------|------|
| **Cyclomatic complexity** | > 10 | Too many conditionals/loops, increases test complexity |
| **Function length** | > 50 lines | Reduced readability, possibly multiple responsibilities |
| **SRP violation** | > 2 responsibilities | Single function/class handling multiple responsibilities |
| **Duplicate code** | > 2 occurrences | Same logic repeated → Extract Method needed |
| **Magic Numbers** | > 0 | Hardcoded constants → Named Constant needed |

**4. Refactoring Technique Selection Guide**

| Problem | Technique | Application Condition |
|------|------|----------|
| Long function | **Extract Method** | Function > 50 lines or logical blocks can be separated |
| Multiple responsibilities | **Extract Class** | Class handles 2+ responsibilities |
| Duplicate code | **Extract Method** | Same logic repeated 2+ times |
| Magic Numbers | **Replace with Constant** | Hardcoded numbers/strings |
| Complex conditionals | **Decompose Conditional** | Complex if/else chains |

**5. Add Refactoring Suggestions to Report**

When high complexity files are found, add to the "Recommendations" section in the following format:

```markdown
## 🔧 Refactoring Suggestions

### Complexity Analysis Results

#### `src/services/UserService.ts:15-110` - `login()` function

**Metrics**:
| Metric | Current | Threshold | Status |
|------|------|--------|------|
| Cyclomatic Complexity | 12 | 10 | ⚠️ Exceeded |
| Function Length | 95 lines | 50 lines | ⚠️ Exceeded |
| Responsibilities (SRP) | 4 | 2 | ⚠️ Violated |

**Detected Code Smells**:
- Duplicate code: `validateUser` logic repeated 3 times
- Magic Numbers: `3.14`, `0.05` hardcoded

**Recommended Refactoring**:

1. **Extract Method: `validateUser()`**
   - Extract duplicate validation logic to separate function
   - Expected effect: Remove duplication, improve testability

2. **Extract Class: `SessionManager`**
   - Separate session management logic to separate class
   - Expected effect: SRP compliance, improved cohesion

3. **Replace Magic Numbers**
   - `3.14` → `SESSION_TIMEOUT_HOURS`
   - `0.05` → `RETRY_INTERVAL_SECONDS`

**Expected Improvement**:
- Complexity: 12 → 5 (-58%)
- Function length: 95 lines → 40 lines (-58%)
- Testability: Improved (smaller units)
```

### Phase 3E: Requirement Reverse Tracing (Optional)

**Objective**: Reverse trace JIRA AC related to the bug

**Execution Condition**:
- When linked to a JIRA issue
- After confirming bug location in Phase 3 (Codebase Investigation)

**Steps**:

**1. Call requirement-validator Agent (Mode 1)**

```typescript
// Notify user
"🤖 Running requirement-validator agent for AC reverse tracing..."

// Agent invocation (automatic in Claude Code)
// Mode 1: Reverse Tracing
// Input: Bug file path, function name
// Output: Related AC list
```

**2. Add Results to Report**

Add to Phase 4 (Root Cause Analysis) section of `[ISSUE_ID]_REPORT.md` report:

```markdown
## 🎯 Requirement Tracing

### Related AC
- **AC#2**: "Lock account after 5 failed attempts"
  - **Related code**: [LoginAttemptService.ts:15-45](src/auth/LoginAttemptService.ts#L15-L45)
  - **Bug cause**: Counter logic error (Redis key TTL not set)
  - **AC fulfillment**: ❌ Not fulfilled - Account not locked

### Impact
- This bug prevents AC#2 from being fulfilled
- Security requirement violation (Brute force attack defense failure)

### Recommended Actions
1. Set counter TTL in LoginAttemptService (5 minutes)
2. Add test case for AC#2 (currently missing)
3. Re-verify with requirement-validator during MR review
```

### Phase 4: Root Cause Determination

Based on systematic analysis, identify:

**1. Primary Root Cause**
- Exact location: `[file_path:line_number](file_path#Lline_number)`
- Technical mechanism explaining why it occurs
- Trigger conditions

**2. Contributing Factors**
- Secondary issues exacerbating the problem
- Missing safeguards or error handling
- Architectural weaknesses

**3. Impact Assessment**
- Affected users and use cases
- Frequency and reproducibility
- Data integrity implications
- Performance or security considerations

### Phase 5: Recommendations

Provide actionable recommendations:

**1. Immediate Actions**
- Quick fixes or workarounds
- Rollback considerations
- Monitoring or alerting to add

**2. Proper Fix**
- Detailed solution with code-level specifics
- Files and functions requiring modification
- Edge cases to handle
- Testing strategy

**3. Prevention**
- Unit tests to add (specific assertions)
- Integration tests for the flow
- Code review checklist items
- Documentation updates needed

**4. Related Areas to Review**
- Similar code patterns with same issue
- Related features sharing problematic code
- Upstream/downstream dependencies

## Report Generation

Create a comprehensive markdown report using the template in `references/report_template.md`:

### Report Structure

```markdown
# Issue Analysis: [Issue Title/ID]

## Summary
[One-paragraph executive summary]

## Context
- JIRA: [link and key details]
- Sentry: [error details if applicable]
- Additional files: [user-provided context]

## Investigation Process
[Summary of hypotheses considered and eliminated]

## Root Cause
**Location**: [file.ts:123](file.ts#L123)
**Explanation**: [Why this happens]
**Trigger**: [What causes it]

## Recommendations

### Immediate Fix
[Specific code changes or workarounds]

### Long-term Solution
[Architectural or design improvements]

### Testing
- [ ] Unit test: [specific test case]
- [ ] Integration test: [specific scenario]

### Related Code to Review
- [file1.ts:45](file1.ts#L45) - Similar pattern
- [file2.ts:89](file2.ts#L89) - Shared dependency
```

### File Naming Convention

Save the report as:
- `[ISSUE_ID]_REPORT.md` (e.g., `PROJ-1234_REPORT.md`)
- If no JIRA ID: `[DESCRIPTIVE_NAME]_REPORT.md` (e.g., `LOGIN_ERROR_REPORT.md`)

Save in current working directory or `docs/` folder if it exists.

## Best Practices

**Efficiency**
- Use symbolic tools to read only necessary code, not entire files
- Start with high-level overview before diving into details
- Use pattern search for quick discovery

**Thoroughness**
- Use sequential thinking to explore all angles
- Document reasoning process
- Include eliminated hypotheses (shows rigor)

**Specificity**
- Always provide exact file paths and line numbers
- Include code snippets as evidence
- Link to external resources (JIRA, Sentry)

**Actionability**
- Focus on concrete, implementable recommendations
- Provide code examples for fixes
- Suggest specific tests to add

**Documentation**
- Create detailed `*_REPORT.md` file at the end
- Use proper markdown formatting
- Include clickable code location links
- Format actionable items as checklists

## Integration with Workflow

This skill is typically the first step in a larger workflow:

```
analyze [JIRA]
  → Creates: [ISSUE_ID]_REPORT.md
  → Next: plan [REPORT]
  → Next: execute [PLAN]
  → Next: record
```

The generated report becomes input for the `plan` skill to create an implementation plan.

## Resources

### references/

This skill includes reference materials to support the analysis process:

- `report_template.md` - Detailed template for analysis reports
- `common_bug_patterns.md` - Catalog of frequently encountered bug patterns and their characteristics

These references can be loaded into context when needed for comprehensive analysis.
