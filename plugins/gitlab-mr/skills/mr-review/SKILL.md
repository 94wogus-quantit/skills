---
name: mr-review
description: Perform context-aware comprehensive code review on GitLab MR changes. Validates architecture consistency, business logic accuracy, historical issue patterns, JIRA requirements, security, and test coverage. Generates INLINE_DISCUSSION.json for GitLab inline comments and SUMMARY_COMMENT.md for overall summary. Korean triggers: MR 리뷰, 코드 리뷰, 머지 리퀘스트, PR 리뷰, 코드 검토, 리뷰해줘, 코드 봐줘, MR 확인해줘.
user-invocable: true
---

# MR Code Review

## ⚠️ CRITICAL LANGUAGE POLICY

**DEFAULT LANGUAGE: KOREAN (한국어)**

ALL outputs, reports, analysis, and communications MUST be in **KOREAN** unless explicitly requested otherwise by the user.

- ✅ **INLINE_DISCUSSION.json / SUMMARY_COMMENT.md**: Write in Korean
- ✅ **Issue descriptions**: Write in Korean
- ✅ **Improvement suggestions**: Write in Korean
- ✅ **Analysis comments**: Write in Korean
- ✅ **User communication**: Respond in Korean

**Exception**: If the user writes in another language, match that language for responses.

**This is a MANDATORY requirement. Do NOT default to English.**

---

## Overview

Analyzes GitLab MR (Merge Request) changes to perform context-based comprehensive code review beyond simple syntax checks and generates **2 reports**:
- `INLINE_DISCUSSION.json` - For GitLab Inline Discussion automation
- `SUMMARY_COMMENT.md` - Overall summary

**Key Differentiator**: In-depth analysis leveraging project documentation (README, CHANGELOG, CLAUDE.md), Serena memory, JIRA, and Confluence

**Key Features**:
- 📋 **7-Point Comprehensive Verification**: Architecture, business logic, conventions, issue patterns, JIRA requirements, security, tests
- 🎯 **Business Logic Verification**: Validates implementation accuracy against JIRA objectives (detects incorrect logic, missing edge cases)
- 🔐 **Dependency Security Analysis** (Optional): Automatic detection of CRITICAL/HIGH vulnerabilities based on npm audit
- 🤖 **MCP-Based Deep Analysis**: Actively leverages Sequential Thinking + Serena Context7 + Atlassian
- 📝 **2 Report Generation**: JSON (inline discussion) + MD (summary) (3-level severity: 🔴 Critical, 🟡 High, 🟢 Medium)
- 💡 **Improvement Suggestions**: Provides location, description, and improvement methods for each issue

---

## ⚠️ CRITICAL MCP USAGE POLICY

> **You MUST actively utilize Sequential Thinking and Serena MCP in all analysis phases.**

### Sequential Thinking MCP (Required)

**Purpose**: Multi-perspective systematic thinking and hypothesis verification

**✅ DO - Scenarios where you MUST use**:
- Architecture consistency verification: Systematic review of layer separation and dependency direction
- Convention compliance check: Step-by-step verification of naming, style, import order
- Security review: Sequential analysis of each OWASP Top 10 item
- JIRA requirement verification: Individual verification of each Acceptance Criteria
- Historical issue pattern matching: Pattern-by-pattern comparison with known_issues

**Usage Examples**:
```typescript
mcp__plugin_sequential-thinking_sequential-thinking__sequentialthinking({
  thought: "Does the changed code comply with existing architecture layer separation principles? Does it follow the Controller → Service → Repository pattern?",
  thoughtNumber: 1,
  totalThoughts: 7,
  nextThoughtNeeded: true
})

mcp__plugin_sequential-thinking_sequential-thinking__sequentialthinking({
  thought: "SQL Injection vulnerability: Is user input used directly in queries? Are Prepared Statements being used?",
  thoughtNumber: 3,
  totalThoughts: 10,
  nextThoughtNeeded: true
})
```

**❌ DON'T - Cases where you should NOT use**:
- Simple file reading or basic information lookup
- MCP calls themselves (tool usage is separate)
- Simple logging or status updates

### Serena Context7 MCP (Required)

**Purpose**: Deep codebase understanding and memory management

**✅ DO - Scenarios where you MUST use**:
- Understanding overall project context: Use `get_project_context`
- Querying architecture decisions: `read_memory({memory_file_name: "architecture_decisions.md"})`
- Searching code patterns: Use `search_for_pattern`
- Checking symbol dependencies: Use `find_referencing_symbols`
- Querying past bug patterns: `read_memory({memory_file_name: "known_issues.md"})`

**Usage Examples**:
```typescript
// Read historical issue patterns from memory
mcp__plugin_serena_serena__read_memory({
  memory_file_name: "known_issues.md"
})

// Search symbol dependencies
mcp__plugin_serena_serena__find_referencing_symbols({
  name_path: "UserService",
  relative_path: "src/services/user.service.ts"
})

// Search code patterns
mcp__plugin_serena_serena__search_for_pattern({
  substring_pattern: "async.*await",
  paths_include_glob: "**/*.ts"
})
```

**❌ DON'T - Cases where you should use other tools instead**:
- General file reading: Use `Read` tool
- Git operations: Use git commands via `Bash` tool
- Simple code search: Use `Grep` tool

### Atlassian MCP (Optional, Required for JIRA-related tasks)

**Purpose**: JIRA issue and Confluence document integration

**✅ DO**:
- Query JIRA issues linked to MR: `getJiraIssue`
- Check Acceptance Criteria: Parse JIRA issue description
- Search Confluence technical docs: `searchConfluence`

**Usage Examples**:
```typescript
// Query JIRA issue
mcp__plugin_atlassian_atlassian__jira_get_issue({
  issue_key: "PROJ-123"
})

// Search Confluence
mcp__plugin_atlassian_atlassian__confluence_search({
  query: "title ~ \"API Spec\" AND space = \"TECH\""
})
```

---

## When to Use This Skill

**✅ When to use**:
- When GitLab MR code review is needed
- For important MRs requiring context-based comprehensive review (architecture changes, new features)
- When you need to verify project documentation and JIRA requirements together
- When you want systematic verification of security, quality, and test coverage

**❌ When NOT to use**:
- MRs with only simple typo fixes or documentation changes
- When quick review is needed (use basic code-reviewer agent)
- Simple hotfixes unrelated to JIRA issues

**How to use**:
```bash
# Run directly from local
claude-code exec "Use mr-review skill to review this MR. Branch: feature/user-auth"

# Or interactively
# "Review this MR with mr-review skill"
```

---

## Review Workflow

### Phase 1: Context Gathering

**Objective**: Collect all context information related to MR and **clarify branch objectives**

**Primary MCPs**: Serena (Context7, Memory), Atlassian

**Process**:

0. **Verify Current Timestamp**

   > Check current time before starting review and record in report.

   ```bash
   date '+%Y-%m-%d %H:%M:%S %Z'
   ```

   **Record in report header**:
   - **Review Start Time**: `2025-12-12 20:58:20 KST`

1. **Identify Branch Objective - Top Priority**

   > ⚠️ **CRITICAL**: Before code analysis, you MUST first understand "what this branch should achieve."

   **1-1. Extract JIRA issue from branch name**
   ```bash
   # Branch name pattern: feature/PROJ-123-description, bugfix/PROJ-456
   git branch --show-current | grep -oE '[A-Z]+-[0-9]+'
   ```

   **1-2. Extract JIRA issue from MR description**
   ```bash
   # Check GitLab MR description
   glab mr view --json description | jq -r '.description' | grep -oE '[A-Z]+-[0-9]+'
   ```

   **1-3. Query JIRA issue details (Atlassian MCP)**
   ```typescript
   // Query JIRA issue
   mcp__plugin_atlassian_atlassian__jira_get_issue({
     issue_key: "PROJ-123"
   })
   ```

   **1-4. Organize branch objectives (Sequential Thinking)**
   ```typescript
   mcp__plugin_sequential-thinking_sequential-thinking__sequentialthinking({
     thought: "Branch objective analysis: What is the purpose of PROJ-123? What are the Acceptance Criteria? What specific goals should this MR achieve?",
     thoughtNumber: 1,
     totalThoughts: 3,
     nextThoughtNeeded: true
   })
   ```

   **1-5. Write branch objective summary**

   Collect the following information and place at the top of the report:
   - **JIRA issue key and title**
   - **Issue type** (Story / Bug / Task / Epic)
   - **Acceptance Criteria list**
   - **Related issues** (Parent Epic, Linked Issues)
   - **Sprint/Milestone** (if applicable)

2. **Analyze Git changes**
   - Run `git diff` to check list of changed files
   - Analyze change scope and impact with Sequential Thinking
   - Identify changed symbols and dependencies with Serena

3. **Collect project documentation**
   - Read README.md, CHANGELOG, CLAUDE.md
   - Understand overall project context with Serena Context7
   - Read all related memories from Serena memory (`architecture_decisions.md`, `code_patterns.md`, `known_issues.md`)

4. **Search Confluence documentation** (if needed)
   - Search related technical docs with Atlassian MCP
   - Extract technical specifications with Sequential Thinking

**Output File**: `.mr-review/1_CONTEXT.md`

```markdown
# Phase 1: Context Gathering

## Review Metadata
- **Review Start Time**: 2025-12-12 20:58:20 KST

## Branch Information
- **Branch Name**: feature/PROJ-123-user-auth
- **MR ID**: !456
- **Target Branch**: main

## JIRA Issue
- **Issue Key**: PROJ-123
- **Title**: Implement user email login
- **Type**: Story
- **Sprint**: Sprint 15

## Acceptance Criteria
1. AC#1: Email format validation
2. AC#2: Account lock after 5 failed attempts
3. AC#3: JWT token issuance

## Changed Files List
- src/services/auth.ts (Modified)
- src/api/login.ts (Added)
- tests/auth.test.ts (Modified)

## Project Context
- Architecture: Clean Architecture
- Authentication: JWT
- Related Serena Memory: architecture_decisions.md, known_issues.md
```

---

### Phase 2: Code Analysis

**Objective**: Systematically analyze 7 verification items

**Primary MCPs**: Sequential Thinking (Required), Serena

**7 Verification Items**:

Detailed processes for each verification item are in `references/verification_guides/`:

1. **[Architecture Consistency Verification](references/verification_guides/architecture_check.md)**
   - Compare with architecture decisions in CLAUDE.md and Serena memory
   - Verify layer separation principles with Sequential Thinking
   - Check dependency relationships with Serena

2. **Business Logic Accuracy Verification** ⭐ NEW

   **Purpose**: Verify implementation accuracy against JIRA objectives (detect incorrect logic, missing edge cases)

   **Process**:

   **2-1. Extract business requirements from JIRA**

   Use JIRA information collected in Phase 1:
   - Acceptance Criteria (AC)
   - Business rule descriptions
   - Expected behavior scenarios

   **2-2. Analyze logic with Sequential Thinking**

   ```typescript
   mcp__plugin_sequential-thinking_sequential-thinking__sequentialthinking({
     thought: "AC#1 'Account lock after 5 failures' analysis: How does current code count failures? Does it check exactly 5? What are the reset conditions?",
     thoughtNumber: 1,
     totalThoughts: 5,
     nextThoughtNeeded: true
   })

   mcp__plugin_sequential-thinking_sequential-thinking__sequentialthinking({
     thought: "Edge case review: Concurrent login attempts, counter reset after 4 failures then success, missing unlock conditions",
     thoughtNumber: 2,
     totalThoughts: 5,
     nextThoughtNeeded: true
   })
   ```

   **2-3. Verification Checklist**

   | Verification Item | Description |
   |-------------------|-------------|
   | **Logic Accuracy** | Are conditions specified in AC accurately implemented in code? |
   | **Boundary Value Handling** | Is boundary value handling correct (5 = exactly 5? 5 or more?)? |
   | **Edge Cases** | Are exceptional situations (concurrency, timeout, null) considered? |
   | **Negative Cases** | Are "must not" conditions implemented? |
   | **Data Integrity** | Are calculations, aggregations, state changes accurate? |

   **2-4. Record issues in JSON format when found**

   ```json
   {
     "file": "src/services/auth.ts",
     "line": 45,
     "severity": "🔴 Critical",
     "title": "Missing unlock condition",
     "description": "According to AC, should auto-unlock after 30 minutes, but unlock logic is missing",
     "current_code": "if (failCount >= 5) { lockAccount(userId); }",
     "suggested_code": "if (failCount >= 5) {\n  lockAccount(userId, { unlockAfter: 30 * 60 * 1000 });\n}",
     "reason": "Need to fulfill '30-minute auto-unlock' requirement specified in AC#1"
   }
   ```

3. **[Convention Compliance Check](references/verification_guides/convention_check.md)**
   - Verify coding convention compliance with README and CLAUDE.md
   - Systematic verification of naming, style with Sequential Thinking
   - Search similar code patterns with Serena

4. **[Known Issue Pattern Matching](references/verification_guides/known_issues_check.md)**
   - Read known_issues from Serena memory
   - Match past bug patterns with Sequential Thinking
   - Search patterns similar to past bugs with Serena

5. **JIRA Requirement Verification (Automated)**

   **Purpose**: Automatically verify if MR fulfills JIRA AC

   **Process**:

   **4-1. Call requirement-validator Agent (Mode 4: Final Gate)**

   ```typescript
   // Notify user
   "🤖 Verifying AC with requirement-validator agent..."

   // Collect MR branch changes
   Bash({ command: "git diff main...HEAD --name-only" })

   // Agent call
   // Mode 4: Final Gate
   // Input: JIRA issue key, MR full changes
   // Output: Detailed AC verification report (including code quality, security, tests)
   ```

   **4-2. Integrate report into SUMMARY_COMMENT.md**

   Include requirement-validator output as-is:

   ```markdown
   ## 🎯 JIRA Requirement Verification

   ### AC Achievement Summary
   - **Total AC**: 3
   - **Implemented**: 2 (66%)
   - **Not Implemented**: 1 (AC#2)

   ### Detailed Analysis

   #### AC#1: Email Login ✅
   [See requirement-validator Mode 4 output]

   #### AC#2: Account Lock After 5 Failures ❌
   [See requirement-validator Mode 4 output]

   ### Final Verdict

   🔴 **MR BLOCKED** - Merge prohibited due to AC#2 not implemented
   ```

   **4-3. Additional Verification (Maintain existing logic)**

   In addition to requirement-validator results:
   - Security vulnerabilities (OWASP Top 10)
   - Code convention compliance
   - Test coverage

   These continue to be performed in existing Phase 2-6, 2-7

6. **[Security and Quality Review](references/verification_guides/security_review.md)**
   - Systematic OWASP Top 10 analysis with Sequential Thinking
   - Search security patterns and vulnerabilities with Serena
   - Key security items: SQL Injection, XSS, CSRF, Authentication, Authorization

7. **[Test Coverage Evaluation](references/verification_guides/test_coverage.md)**
   - Evaluate test quality with Sequential Thinking
   - Find test files and untested functions with Serena
   - Verify test coverage of changed code

**Output File**: `.mr-review/2_CODE_ANALYSIS.md`

```markdown
# Phase 2: Code Analysis

## Verification Summary
- **Total Issues**: 5
- 🔴 Critical: 1
- 🟡 High: 2
- 🟢 Medium: 2

## 1. Architecture Consistency ✅
- Layer separation compliance
- Dependency direction normal

## 2. Business Logic Accuracy ❌
### Issue #1: Missing Unlock Condition
- **File**: src/services/auth.ts:45
- **Severity**: 🔴 Critical
- **Description**: According to AC#2, should auto-unlock after 30 minutes, but unlock logic is missing
- **Current Code**: `if (failCount >= 5) { lockAccount(userId); }`
- **Suggested Code**: `lockAccount(userId, { unlockAfter: 30 * 60 * 1000 });`
- **Reason**: Need to fulfill AC#2 requirement

## 3. Convention Compliance ⚠️
### Issue #2: Naming Convention Violation
- **File**: src/api/login.ts:12
- **Severity**: 🟢 Medium
- **Description**: Function name uses snake_case instead of camelCase
...

## 4. Known Issue Patterns ✅
- No matching patterns with known_issues.md

## 5. JIRA Requirements ❌
- AC#1: ✅ Implemented
- AC#2: ❌ Not implemented (unlock logic)
- AC#3: ✅ Implemented

## 6. Security and Quality ⚠️
### Issue #3: Possible SQL Injection
- **File**: src/services/user.ts:78
- **Severity**: 🟡 High
...

## 7. Test Coverage ⚠️
### Issue #4: Missing Tests
- **File**: src/services/auth.ts
- **Severity**: 🟡 High
- **Description**: No tests for lockAccount function
```

---

### Phase 3: Dependency Security Analysis

**Objective**: Automated detection of dependency vulnerabilities

**Primary MCP**: Sequential Thinking

**Process**:

**1. Universal Security Scan Execution**

Use tools that can scan all dependencies regardless of language:

**Recommended Tool: Trivy** (Free, Open-source, All Languages Supported)

```bash
# Scan entire project with Trivy (auto language detection)
trivy fs --scanners vuln --format json -o trivy-result.json .

# Filter Critical/High vulnerabilities only
trivy fs --scanners vuln --severity CRITICAL,HIGH --format json -o trivy-result.json .
```

**Supported Languages/Package Managers**:
- JavaScript/Node.js: npm, yarn, pnpm
- Python: pip, pipenv, poetry
- Go: go mod
- Java/Kotlin: Maven, Gradle
- Ruby: Bundler
- Rust: Cargo
- PHP: Composer
- .NET: NuGet
- And many more

**Alternative Tools**:

| Tool | Features | Command |
|------|----------|---------|
| **Trivy** | Free, Fast, CI/CD friendly | `trivy fs --format json .` |
| **Snyk** | Detailed fix guides | `snyk test --json` |
| **Grype** | Lightweight, SBOM support | `grype dir:. -o json` |
| **OSV-Scanner** | Google-provided, Free | `osv-scanner --format json -r .` |

**Trivy Installation (if not installed)**:
```bash
# macOS
brew install trivy

# Linux
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Docker (use without installation)
docker run --rm -v $(pwd):/app aquasec/trivy fs --format json /app
```

**2. Vulnerability Analysis (Using Sequential Thinking)**

Analyze each vulnerability with Sequential Thinking:

```typescript
// When vulnerability is found
mcp__plugin_sequential-thinking_sequential-thinking__sequentialthinking({
  thought: "CVE-2021-3749 (SSRF) vulnerability found in axios@0.21.0. severity: CRITICAL. Impact: Server-Side Request Forgery possible",
  thoughtNumber: 1,
  totalThoughts: 3,
  nextThoughtNeeded: true
})

mcp__plugin_sequential-thinking_sequential-thinking__sequentialthinking({
  thought: "Resolution: Update to axios@0.21.2 or higher. No breaking changes (verified in CHANGELOG). Immediate application recommended",
  thoughtNumber: 2,
  totalThoughts: 3,
  nextThoughtNeeded: true
})

mcp__plugin_sequential-thinking_sequential-thinking__sequentialthinking({
  thought: "Impact scope: Used in 11 src/api/*.ts files. Includes production environment. Urgent fix required",
  thoughtNumber: 3,
  totalThoughts: 3,
  nextThoughtNeeded: false
})
```

**Best Practices**:
- Recommend holding MR approval when CRITICAL vulnerabilities are found
- Mark HIGH vulnerabilities as warning but do not block

**Output File**: `.mr-review/3_SECURITY_ANALYSIS.md`

```markdown
# Phase 3: Dependency Security Analysis

## 스캔 도구
- **도구**: Trivy v0.48.0
- **스캔 시간**: 2024-01-15 14:30:00 UTC

## 취약점 요약
- **총 취약점**: 3개
- 🔴 CRITICAL: 1개
- 🟡 HIGH: 1개
- 🟢 MEDIUM: 1개

## 🔴 CRITICAL 취약점

### CVE-2021-3749: axios SSRF
- **패키지**: axios@0.21.0
- **위치**: package.json:15
- **영향**: Server-Side Request Forgery 공격 가능
- **수정 버전**: 0.21.2 이상
- **영향 범위**:
  - src/api/user.ts:12
  - src/api/payment.ts:8
  - src/utils/http-client.ts:5
  - (총 11개 파일)

## 🟡 HIGH 취약점

### CVE-2021-23337: lodash Prototype Pollution
- **패키지**: lodash@4.17.19
- **위치**: package.json:18
- **영향**: 객체 프로토타입 오염
- **수정 버전**: 4.17.21 이상

## 권장사항
1. `npm install axios@latest lodash@latest`
2. CRITICAL 취약점 0개 될 때까지 MR merge 금지
```

---

### Phase 4: Report Generation

**Objective**: Read Phase 1~3 intermediate outputs and generate final 2 report files

**Input Files** (Phase 1~3 outputs):
- `.mr-review/1_CONTEXT.md` - Context information
- `.mr-review/2_CODE_ANALYSIS.md` - Code analysis results
- `.mr-review/3_SECURITY_ANALYSIS.md` - Security analysis results

**Output Files**:
- `INLINE_DISCUSSION.json` - JSON for GitLab Inline Discussion automation
- `SUMMARY_COMMENT.md` - Overall summary markdown

**Process**:

#### Step 1: Generate INLINE_DISCUSSION.json

Structure all issues from Phase 2 (code analysis) + Phase 3 (security analysis) as a JSON array (see references/inline_discussion_template.json):

```json
[
  {
    "file": "app/services/cognito.py",
    "line": 116,
    "severity": "🔴 Critical",
    "title": "이슈 제목",
    "description": "이슈에 대한 상세 설명. 왜 이것이 문제인지, 어떤 영향을 미치는지",
    "current_code": "// 문제가 되는 코드 (있는 경우)",
    "suggested_code": "// 권장하는 코드 (있는 경우)",
    "reason": "왜 이렇게 수정해야 하는지 설명"
  }
]
```

**Field Descriptions**:
- `file`: File path (relative to project root)
- `line`: Line number where issue occurs
- `severity`: Severity level (`🔴 Critical`, `🟡 High`, `🟢 Medium`)
- `title`: Issue title (concise)
- `description`: Detailed description (problem, impact, etc.)
- `current_code`: Current problematic code (optional)
- `suggested_code`: Recommended fix code (optional)
- `reason`: Explanation of why this fix is needed

**Sort Order**: By severity (Critical → High → Medium)

#### Step 2: Generate SUMMARY_COMMENT.md

> ⚠️ **CRITICAL**: This file is a **summary**. Detailed content is in `INLINE_DISCUSSION.json`, so only write **one-line summaries** here.

Write overall review summary in markdown (see references/summary_comment_template.md):

**Writing Principles**:
- Each issue: **title + file:line + one-line summary** only
- Detailed descriptions, code examples, fix methods go only in `INLINE_DISCUSSION.json`
- Must include "See INLINE_DISCUSSION.json for details" statement

```markdown
# MR Code Review Summary

## 🎯 브랜치 목표
- JIRA 이슈 연결
- AC 달성 현황

## 📋 리뷰 요약
| 위험도 | 개수 |
|--------|------|
| 🔴 Critical | N개 |
| 🟡 High | N개 |
| 🟢 Medium | N개 |

## 🔴 Critical Issues 요약
1. **[이슈 제목]** - `file.ts:123`

## 🔐 의존성 보안 분석
### CRITICAL 취약점
- axios@0.21.0: CVE-2021-3749 (SSRF)

### HIGH 취약점
- lodash@4.17.19: Prototype Pollution

## ✅ 잘된 점
...

## 다음 단계
...

## 📎 관련 파일
- **Inline Discussion**: `INLINE_DISCUSSION.json`
```

#### Step 3: File Generation (MANDATORY)

⚠️ **CRITICAL**: Both files must be generated using the Write tool.

```
1. Write INLINE_DISCUSSION.json
   - JSON array format
   - Include all issues

2. Write SUMMARY_COMMENT.md
   - Markdown format
   - Include overall summary
```

**Verification**: Confirm both files are generated before completing Phase 4

**Output Files**:
- `INLINE_DISCUSSION.json` - Can auto-generate discussions via GitLab API
- `SUMMARY_COMMENT.md` - For MR description or general comments

---

## Resources

This skill includes the following resources:

### references/

Documents and guides:

- `inline_discussion_template.json`: INLINE_DISCUSSION.json template (for GitLab Inline Discussion)
- `summary_comment_template.md`: SUMMARY_COMMENT.md template (for overall summary)
- `review_checklist.md`: Checklist for 7 verification items
- `inline_comment_format.md`: GitLab discussion format guide (optional)

### references/verification_guides/

Detailed processes for 7 verification items (each in separate file):

1. `architecture_check.md`: Architecture consistency verification process
2. `business_logic_check.md`: Business logic accuracy verification process ⭐ NEW
3. `convention_check.md`: Convention compliance check process
4. `known_issues_check.md`: Known issue pattern matching process
5. `jira_validation.md`: JIRA requirement verification process
6. `security_review.md`: Security and quality review process
7. `test_coverage.md`: Test coverage evaluation process

Each file includes:
- Sequential Thinking MCP usage examples (minimum 3)
- Serena MCP usage examples (minimum 3)
- Atlassian MCP usage examples (when applicable)
- Verification item checklist
- TypeScript code examples

---

## Best Practices

### Improving Review Quality

1. **Active Use of Sequential Thinking**
   - Break down each verification item into 7-10 thought steps
   - Set thoughtNumber and totalThoughts clearly
   - Prevent omissions through systematic sequential analysis

2. **Leverage Serena Memory**
   - Maintain architecture_decisions.md, code_patterns.md, known_issues.md per project
   - Save new patterns/issues discovered during review to memory
   - Utilize accumulated knowledge in subsequent MR reviews

3. **JIRA Integration**
   - Include JIRA issue ID in MR description (e.g., "Closes PROJ-123")
   - Verify each Acceptance Criteria individually
   - Mark unmet requirements as Critical issues

### Performance Optimization

1. **API Cost Reduction**
   - Minimize Serena Context7 calls (utilize caching)
   - Use Sequential Thinking only when necessary
   - Use Read tool for simple file reading

2. **Execution Time Reduction**
   - Focus analysis on changed files only
   - Full project scan only when necessary
   - Execute parallelizable verification items simultaneously

### Reducing False Positives

1. **Prompt Tuning**
   - Improve Sequential Thinking prompts in verification_guides/*.md
   - Reflect project-specific characteristics
   - Collect and incorporate developer feedback

2. **Context Accuracy**
   - Keep CLAUDE.md up to date
   - Update Serena memory periodically
   - Reflect project rule changes immediately

---

## Troubleshooting

### MCP Server Connection Failure

**Symptom**: "MCP server not available" error

**Solution**:
1. Check environment variables (`ANTHROPIC_API_KEY`, `ATLASSIAN_CLOUD_ID`)
2. Run `claude-code mcp list` to check server list
3. Run `claude-code mcp test serena` to test connection

### JIRA/Confluence Query Failure

**Symptom**: JIRA issue or Confluence document query fails

**Solution**:
1. Check `ATLASSIAN_CLOUD_ID`, `ATLASSIAN_API_TOKEN` environment variables
2. Verify token permissions (read:jira-user, read:confluence-content.summary required)
3. Test Atlassian MCP: `claude-code mcp test atlassian`

### Serena Memory Read Failure

**Symptom**: "Memory file not found" error

**Solution**:
1. Check Serena memory directory
2. Run `mcp__plugin_serena_serena__list_memories()` to check available memories
3. Create required memory files (architecture_decisions.md, code_patterns.md, known_issues.md)

---

## Versioning & Updates

**Current Version**: 1.0.0

**Update Strategy**:
- **Prompt Tuning**: Modify verification_guides/*.md files
- **Workflow Changes**: Modify Phase sections in SKILL.md
- **Repackaging**: Run `package_skill.py mr-review`

**Feedback Loop**:
- When false positives are found:
  1. Analyze feedback patterns
  2. Improve Sequential Thinking prompts in verification_guides/*.md
  3. Repackage and local test
  4. Verify improvement effectiveness
