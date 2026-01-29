---
name: analyze
description: Systematically analyze the root cause of bugs and issues using multi-perspective investigation with First Principles Thinking. Use when analyzing JIRA issues, Sentry errors, or investigating bug reports. Generates [ISSUE_ID]_REPORT.md with root cause analysis, code locations, reproduction steps, and fix recommendations.
user-invocable: true
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

Systematically analyze bugs and issues to identify root causes using a structured, multi-perspective approach. This skill combines JIRA/Atlassian integration, Sentry error tracking, codebase investigation with Serena, and **First Principles Thinking** to produce comprehensive analysis reports.

**Output**: `[ISSUE_ID]_REPORT.md` file containing root cause analysis, affected code locations, reproduction steps, and remediation recommendations.

## When to Use This Skill

Use this skill when:
- Analyzing JIRA issues or bug reports
- Investigating Sentry errors or production incidents
- User requests "analyze this issue", "what's causing this bug", "investigate [ISSUE-ID]"
- Need systematic root cause analysis before planning a fix
- Debugging complex problems requiring multi-source investigation

## Analysis Workflow

### Phase 0: Task Registration

⚠️ **CRITICAL: DO NOT SKIP PHASE 0**

**Objective**: Register all Phases as Tasks to track progress throughout the analysis workflow.

Register the following Phases in order using `TaskCreate`:

| Task | subject | activeForm |
|------|---------|------------|
| Phase 1 | Branch Validation | Validating branch |
| Phase 2 | Context Gathering | Gathering context |
| Phase 3 | First Principles Decomposition | Decomposing first principles |
| Phase 4 | Hypothesis Generation | Generating hypotheses |
| Phase 5 | Codebase Investigation | Investigating codebase |
| Phase 5D | Code Complexity Assessment (conditional) | Assessing code complexity |
| Phase 5E | Requirement Reverse Tracing (conditional) | Tracing requirements |
| Phase 6 | Root Cause Determination | Determining root cause |
| Phase 7 | Recommendations | Generating recommendations |
| Phase 8 | Report Generation | Generating report |

**Task Tracking Rules**:
- On Phase entry: `TaskUpdate(taskId, status: "in_progress")`
- On Phase completion: `TaskUpdate(taskId, status: "completed")`
- Conditional Phases (5D, 5E) not executed: `TaskUpdate(taskId, status: "deleted")`
- Only **one Phase** should be `in_progress` at any time

---

### Phase 1: Branch Validation

> 📋 **Task Tracking**: Mark this Phase's Task as `in_progress` on entry, `completed` on completion.

> **MANDATORY REQUIREMENT**:
>
> - **DO NOT** assume you are on the correct branch
> - **ALWAYS** verify branch status using the MCP tool below
> - **NEVER** start analysis (Phase 2) without completing Phase 1
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

---

### Evidence Trail Rules (All Phases)

> **MANDATORY**: Throughout the analysis, maintain an **Evidence Log** that tracks all collected information and reasoning.
> This log ensures the final REPORT documents not just conclusions, but the full path of discovery.

**What to record in the Evidence Log:**

1. **Sources Collected** (Phase 2): Table of every source accessed, with type, path/tool, purpose, and key finding
2. **Thinking Process** (Phase 3-4): Key assumptions identified (verified/unverified), fundamental facts, hypothesis generation and evaluation reasoning
3. **Investigation Results** (Phase 5): Files read, symbols explored, patterns searched, and what each revealed

**Format for Sources Table:**

| # | 소스 유형 | 파일/도구 | 수집 목적 | 핵심 발견 |
|---|-----------|-----------|-----------|-----------|
| 1 | [JIRA/Sentry/파일/ST 등] | [경로 또는 도구명] | [왜 수집했는지] | [무엇을 발견했는지] |

Each Phase MUST append its findings to the Evidence Log.
The Evidence Log is included in the final REPORT's "Evidence Trail" section (Phase 8).

---

### Phase 2: Context Gathering

> 📋 **Task Tracking**: Mark this Phase's Task as `in_progress` on entry, `completed` on completion.

Gather comprehensive context from all available sources:

**1. JIRA Issue Analysis** (if JIRA link/ID provided)
- Use JIRA MCP tool to fetch issue details
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

- Search for related errors by natural language query
- Search by error type, component, time range
- Get detailed error information (stack traces, breadcrumbs, context)
- Analyze error counts, frequency, and trends

From Sentry results, extract:
- **Stack traces**: Exact error location (filename, line number)
- **Error messages**: Error message and type
- **Breadcrumbs**: User behavior tracking before error
- **Context**: Request info, environment variables, user data
- **Frequency**: Error frequency and affected user count
- **Trends**: Error increase/decrease patterns over time
- **Related events**: Other errors from same user/session

**3. Additional Context**
- Read any file paths or code references provided
- Analyze error logs or screenshots
- Check Confluence documentation if referenced

> **⚠️ Evidence Trail**: After collecting context, record ALL sources in the Evidence Log table (source type, path/tool, purpose, key finding for each).

---

### Phase 3: First Principles Decomposition

> 📋 **Task Tracking**: Mark this Phase's Task as `in_progress` on entry, `completed` on completion.

**Objective**: Separate "facts" from "assumptions" in the collected context, and extract only fundamental facts.

> For detailed process and Sequential Thinking invocation examples, see `references/first_principles_guide.md`

**Step 1: Assumption Identification**

Use `mcp__plugin_seq-think_st__sequentialthinking` to:

1. List everything assumed to be "obviously true" about this issue
2. Classify each item as **verified fact** (confirmable via logs/metrics/code) vs **unverified assumption** (based on inference/experience)
3. Explicitly mark unverified assumptions

**Step 2: Fundamental Decomposition**

Use `mcp__plugin_seq-think_st__sequentialthinking` to:

1. Decompose the system's operating principles into basic components (input → processing → output)
2. List "what must be true for this system to work correctly"
3. Identify which of those are "not true" → root cause candidates

**Step 3: Fact-Based Summary**

Organize the information to pass to Phase 4:
- List of verified facts
- List of unverified assumptions (marked as needing verification)
- System decomposition results
- Normal operating conditions that may be violated

> **⚠️ Evidence Trail**: Record assumptions (verified/unverified) and fundamental facts in the Evidence Log, including their sources.

---

### Phase 4: Hypothesis Generation

> 📋 **Task Tracking**: Mark this Phase's Task as `in_progress` on entry, `completed` on completion.

Use `mcp__plugin_seq-think_st__sequentialthinking` to systematically explore multiple perspectives:

**1. Generate Hypotheses**

Consider various possible root causes based on **verified facts identified in Phase 3**:
- Code logic errors (off-by-one, null checks, type mismatches)
- Race conditions or concurrency issues
- Resource leaks or memory problems
- Configuration issues
- Dependency version conflicts
- Environmental differences
- Data quality or edge cases
- Integration issues with external services

**2. Tag Evidence Type**

Tag each hypothesis with its evidence type:
- **Fact-based**: Derived from verified facts in Phase 3 → investigate first
- **Inference-based (unverified)**: Inferred from experience or pattern matching → lower priority

**3. Deletion Step**

Prune the generated hypotheses:
1. State the "evidence" for each hypothesis (no evidence = candidate for deletion)
2. Delete hypotheses that contradict verified facts from Phase 3
3. If fewer hypotheses remain than feels comfortable, you are on the right track

**4. Hypothesis Evaluation Matrix**

| 가설 | 가능성 | 검증 비용 | 영향도 | 근거 유형 | 우선순위 |
|------|--------|----------|--------|-----------|----------|
| ... | 높/중/낮 | 낮/중/높 | 낮/중/높 | 사실/유추 | ★~★★★ |

Priority = Likelihood × Impact / Verification Cost
→ Investigate in Phase 5, highest priority first

> **⚠️ Evidence Trail**: Record hypothesis evaluation results (adopted/rejected with reasoning) in the Evidence Log.

---

### Phase 5: Codebase Investigation

> 📋 **Task Tracking**: Mark this Phase's Task as `in_progress` on entry, `completed` on completion.

Use Serena tools efficiently for targeted code exploration:

**1. Targeted Code Exploration**
- `mcp__plugin_serena_serena__get_symbols_overview` - Understand file structure
- `mcp__plugin_serena_serena__find_symbol` - Locate specific functions/classes
- `mcp__plugin_serena_serena__find_referencing_symbols` - Trace execution flow
- `mcp__plugin_serena_serena__search_for_pattern` - Find error messages or patterns

**2. Execution Flow Tracing**
- Map the path from user action to error
- Identify all components in the flow
- Look for conditional branches
- Check error handling and validation logic

**3. Recent Changes Analysis** (if applicable)
- Use GitHub MCP to find recent changes
- Correlate timing with issue occurrence
- Review related code modifications

> **⚠️ Evidence Trail**: Record all investigated files, symbols, search patterns, and key findings in the Evidence Log.

### Phase 5D: Code Complexity Assessment (Conditional)

> 📋 **Task Tracking**: Mark as `in_progress`/`completed` if condition met. Mark as `deleted` if skipped.

**Execution Condition**:
- After confirming affected files in Phase 5
- **Conditional**: When code with Cyclomatic complexity > 10 OR function length > 50 lines is found

**Steps**:

**1. Analyze Complexity with Serena**

```typescript
mcp__plugin_serena_serena__find_symbol({
  name_path_pattern: "ClassName/methodName",
  relative_path: "src/path/to/file.ts",
  include_body: true
})
```

**2. Measure Complexity with Sequential Thinking**

Use `mcp__plugin_seq-think_st__sequentialthinking` to:
- Measure cyclomatic complexity
- Analyze function length
- Perform responsibility analysis (SRP)
- Detect code smells (duplication, magic numbers)
- Determine refactoring strategy

**3. Refactoring Decision Criteria**

| Metric | Threshold | Description |
|------|--------|------|
| **Cyclomatic complexity** | > 10 | Too many conditionals/loops |
| **Function length** | > 50 lines | Reduced readability |
| **SRP violation** | > 2 responsibilities | Multiple responsibilities |
| **Duplicate code** | > 2 occurrences | Extract Method needed |
| **Magic Numbers** | > 0 | Named Constant needed |

**4. Add Refactoring Suggestions to Report** (if applicable)

### Phase 5E: Requirement Reverse Tracing (Optional)

> 📋 **Task Tracking**: Mark as `in_progress`/`completed` if condition met. Mark as `deleted` if skipped.

**Execution Condition**:
- When linked to a JIRA issue
- After confirming bug location in Phase 5

**Steps**:

**1. Call requirement-validator Agent (Mode 1)**

```
"🤖 Running requirement-validator agent for AC reverse tracing..."
// Mode 1: Reverse Tracing
// Input: Bug file path, function name
// Output: Related AC list
```

**2. Add Results to Report**

---

### Phase 6: Root Cause Determination

> 📋 **Task Tracking**: Mark this Phase's Task as `in_progress` on entry, `completed` on completion.

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

**4. Deletion Assessment**

> For detailed guide, see `references/root_cause_techniques.md`

After confirming the root cause, evaluate whether deletion (not patching) can resolve the issue:

- □ Is the code/feature where this bug occurs still needed?
- □ Would deleting this code make the bug structurally impossible?
- □ Is the root cause dead code, unused feature flags, or unnecessary abstraction layers?

> "The best part is no part." — Deletion may be a more fundamental solution than patching.

**5. 5 Why Analysis (Conditional)**

> For detailed process and examples, see `references/root_cause_techniques.md`

**Execution Condition** — Perform when one or more of the following apply:
- The direct cause is suspected to be a structural/systemic issue
- A recurring issue not resolvable by a single code fix
- A compound cause spanning multiple components

Not needed for simple bugs (typos, off-by-one, missing null checks, etc.).

```
Why 1: 왜 이 문제가 발생하는가? → [직접적 원인]
Why 2: 왜 [직접적 원인]이 발생했는가? → [중간 원인]
...
Why 5: 왜 [구조적 원인]이 존재하는가? → [근본 원인]
```

**6. Logical Falsification**

Attempt to falsify the confirmed root cause:

1. List all conditions that "must be logically true if this cause is correct"
2. Verify whether each condition is confirmable via code/logs/data
3. Mark unverifiable conditions as "needs verification in execute phase"
4. If any verifiable condition is false → revisit root cause

※ Perform within the scope of static analysis (code reading). Verification requiring execution/testing is deferred to the execute skill.

**7. Analysis Quality Checklist**

Verify the following before confirming root cause:

- □ Is the root cause based on "verified facts"?
- □ Did you go beyond surface-level causes? (structural cause identified?)
- □ Was it derived from facts specific to this system, not inference?
- □ Was falsification attempted? (if applicable)
- □ Do recommendations address the root cause, not just symptoms?

→ If any item is unmet, immediately supplement the analysis within this Phase

---

### Phase 7: Recommendations

> 📋 **Task Tracking**: Mark this Phase's Task as `in_progress` on entry, `completed` on completion.

Follow this **5-step algorithm** in strict order when generating recommendations:

**Step 1. Question Requirements**
- Who created the requirements for the feature where this bug occurs?
- Are those requirements still valid today?
- Could the requirements themselves be wrong?

**Step 2. Delete**
- Would deleting this code/feature eliminate the bug?
- Incorporate the Deletion Assessment results from Phase 6

**Step 3. Simplify**
- Can the remaining code be restructured more simply?
- Are there excessive abstractions or unnecessary layers?

**Step 4. Accelerate**
- How to shorten the reproduce-fix-verify cycle for this bug?

**Step 5. Automate**
- Add tests/linters to auto-detect this type of bug — **only as the last step**

> ⚠️ Common mistake: Starting with Step 5 (Automate). Testing code that should not exist is waste.

After applying the above framework, write concrete recommendations:

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

**5. Efficiency Evaluation**

Evaluate the efficiency of each recommendation:

| Recommendation | Implementation Complexity | Resolution Scope | Efficiency |
|----------------|--------------------------|-------------------|------------|
| ... | Low/Med/High | This issue only / Similar issues / Fundamental | ★~★★★ |

→ Prioritize the simplest approach that resolves the root cause
→ Ask yourself: "Am I optimizing something that should not exist?"

---

### Phase 8: Report Generation

> 📋 **Task Tracking**: Mark this Phase's Task as `in_progress` on entry, `completed` on completion.

Create a comprehensive markdown report.

> **⚠️ Evidence Trail**: Include the accumulated Evidence Log as the "Evidence Trail" section in the report, placed after "Summary" and before "Context" (matching report_template.md layout).

### Report Structure

```markdown
# Issue Analysis: [Issue Title/ID]

## Summary
[One-paragraph executive summary]

## Evidence Trail
[Include accumulated Evidence Log here - see report_template.md for format]

## Context
- JIRA: [link and key details]
- Sentry: [error details if applicable]
- Additional files: [user-provided context]

## First Principles 분석
### 식별된 가정
- [가정 1]: 검증 여부 (✅/❌)
- [가정 2]: 검증 여부 (✅/❌)
### 근본 사실
- [사실 1]: 출처
- [사실 2]: 출처

## Investigation Process
[Summary of hypotheses considered and eliminated]

## 가설 평가
| 가설 | 가능성 | 근거 유형 | 상태 |
|------|--------|-----------|------|
| ... | 높/중/낮 | 사실/유추 | 채택/기각 |

## Root Cause
**Location**: [file.ts:123](file.ts#L123)
**Explanation**: [Why this happens]
**Trigger**: [What causes it]

## 삭제 가능성 평가
- □ 코드/기능이 현재도 필요한가?
- □ 삭제하면 버그가 구조적으로 불가능해지는가?
→ 결론: [삭제 가능/불가 - 사유]

## 5 Why 분석 (해당 시)
Why 1: ...
Why 2: ...
...

## 반증 시도 (해당 시)
| 가설 | 반증 조건 | 결과 |
|------|-----------|------|
| ... | ... | 반증 실패(강화)/반증 성공(기각) |

## 분석 품질 체크
- [x] 사실 기반 분석
- [x] 구조적 원인 파악
- [x] 유추 거부 확인
- [x] 반증 시도 완료
- [x] 근본 원인 해결 권장

## 5단계 알고리즘 평가
| Step | 질문 | 답변 |
|------|------|------|
| 1. 요구사항 질의 | 요구사항이 현재도 유효한가? | [답변] |
| 2. 삭제 | 코드 삭제로 해결 가능한가? | [답변] |
| 3. 단순화 | 더 간단하게 재구성 가능한가? | [답변] |
| 4. 가속 | 재현-검증 사이클 단축 방법? | [답변] |
| 5. 자동화 | 자동 감지 방법? | [답변] |

## Recommendations

### Immediate Fix
[Specific code changes or workarounds]

### Long-term Solution
[Architectural or design improvements]

### Efficiency Evaluation
| 권장사항 | 구현 복잡도 | 해결 범위 | 효율성 |
|----------|------------|-----------|--------|

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
- `common_bug_patterns.md` - Catalog of frequently encountered bug patterns
- `first_principles_guide.md` - Detailed guide for First Principles Decomposition (includes ST invocation examples)
- `root_cause_techniques.md` - Detailed guide for 5 Why, falsification, hypothesis management, and efficiency evaluation
