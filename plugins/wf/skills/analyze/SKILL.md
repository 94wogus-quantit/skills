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

---

### Phase 1: Context Gathering

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

---

### Phase 2: First Principles Decomposition

**Objective**: 수집된 컨텍스트에서 "사실"과 "가정"을 분리하고, 근본 사실만 추출한다.

> 상세 프로세스 및 Sequential Thinking 호출 예시는 `references/first_principles_guide.md` 참조

**Step 1: 가정 식별 (Assumption Identification)**

Use `mcp__plugin_seq-think_st__sequentialthinking` to:

1. 이 이슈에 대해 "당연하다고 믿는 것"을 모두 나열
2. 각 항목을 **검증된 사실**(로그/메트릭/코드로 확인 가능) vs **미검증 가정**(추론/경험 기반)으로 분류
3. 미검증 가정을 명시적으로 표시

**Step 2: 근본 원리 분해 (Decomposition)**

Use `mcp__plugin_seq-think_st__sequentialthinking` to:

1. 버그가 발생하는 시스템의 동작 원리를 기본 구성요소로 분해 (입력 → 처리 → 출력)
2. "이 시스템이 정상 동작하려면 반드시 참이어야 하는 것"을 나열
3. 그 중 "참이 아닌 것"을 식별 → 근본 원인 후보

**Step 3: 사실 기반 요약 (Fact-Based Summary)**

Phase 3으로 넘기는 정보를 정리:
- 검증된 사실 목록
- 미검증 가정 목록 (검증 필요 표시)
- 시스템 분해 결과
- 정상 동작 조건 중 위반 가능성이 있는 것

---

### Phase 3: Hypothesis Generation

Use `mcp__plugin_seq-think_st__sequentialthinking` to systematically explore multiple perspectives:

**1. Generate Hypotheses**

Consider various possible root causes based on **Phase 2에서 식별한 검증된 사실**:
- Code logic errors (off-by-one, null checks, type mismatches)
- Race conditions or concurrency issues
- Resource leaks or memory problems
- Configuration issues
- Dependency version conflicts
- Environmental differences
- Data quality or edge cases
- Integration issues with external services

**2. Tag Evidence Type**

각 가설 생성 시 근거 유형을 명시:
- **사실 기반**: Phase 2에서 식별한 검증된 사실에서 도출 → 우선 조사
- **유추 기반(미검증)**: 경험이나 패턴 매칭으로 추론 → 우선순위 하향

**3. Deletion Step**

생성된 가설을 정리:
1. 각 가설의 "근거"를 명시 (근거 없으면 삭제 대상)
2. Phase 2에서 검증된 사실과 모순되는 가설 삭제
3. 남은 가설이 "편하게 느껴지는 것보다 적다면" 올바른 방향

**4. Hypothesis Evaluation Matrix**

| 가설 | 가능성 | 검증 비용 | 영향도 | 근거 유형 | 우선순위 |
|------|--------|----------|--------|-----------|----------|
| ... | 높/중/낮 | 낮/중/높 | 낮/중/높 | 사실/유추 | ★~★★★ |

우선순위 = 가능성 × 영향도 / 검증 비용
→ 높은 순서대로 Phase 4에서 조사

---

### Phase 4: Codebase Investigation

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

### Phase 4D: Code Complexity Assessment (Conditional)

**Execution Condition**:
- After confirming affected files in Phase 4
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

### Phase 4E: Requirement Reverse Tracing (Optional)

**Execution Condition**:
- When linked to a JIRA issue
- After confirming bug location in Phase 4

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

### Phase 5: Root Cause Determination

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

**4. Deletion Assessment (삭제 가능성 평가)**

> 상세 가이드는 `references/root_cause_techniques.md` 참조

근본 원인 확정 후, 수정이 아닌 삭제로 해결 가능한지 평가:

- □ 이 버그가 발생하는 코드/기능은 현재도 필요한가?
- □ 이 코드를 삭제하면 버그가 구조적으로 불가능해지는가?
- □ Dead code, 미사용 feature flag, 불필요한 추상화 레이어가 원인인가?

> "최고의 부품은 없는 부품이다" — 삭제가 수정보다 근본적인 해결일 수 있다.

**5. 5 Why Analysis (Conditional)**

> 상세 프로세스 및 예시는 `references/root_cause_techniques.md` 참조

**적용 조건** — 다음 중 하나 이상 해당 시 수행:
- 직접적 원인이 구조적/시스템적 문제로 의심되는 경우
- 단일 코드 수정으로 해결되지 않는 반복 이슈인 경우
- 여러 구성요소에 걸친 복합 원인이 의심되는 경우

단순 버그(오타, off-by-one, null check 누락 등)에는 불필요.

```
Why 1: 왜 이 문제가 발생하는가? → [직접적 원인]
Why 2: 왜 [직접적 원인]이 발생했는가? → [중간 원인]
...
Why 5: 왜 [구조적 원인]이 존재하는가? → [근본 원인]
```

**6. Logical Falsification**

확정된 근본 원인에 대해 반증을 시도:

1. "이 원인이 맞다면 논리적으로 참이어야 하는 조건"을 가능한 한 나열
2. 각 조건이 코드/로그/데이터로 확인 가능한지 검증
3. 확인 불가능한 조건은 "execute 단계에서 검증 필요"로 표시
4. 확인 가능한 조건 중 하나라도 거짓이면 → 근본 원인 재검토

※ 정적 분석(코드 읽기) 범위 내에서 수행. 실행/테스트가 필요한 검증은 execute 스킬에서 수행.

**7. Analysis Quality Checklist**

근본 원인 확정 전 다음을 확인:

- □ 근본 원인이 "검증된 사실"에 기반하는가?
- □ 표면적 원인에서 멈추지 않았는가? (구조적 원인까지 파악했는가?)
- □ 유추가 아닌 이 시스템의 고유한 사실에서 도출했는가?
- □ 반증 시도를 수행했는가? (해당하는 경우)
- □ 권장사항이 증상이 아닌 근본 원인을 해결하는가?

→ 미충족 항목이 있으면 해당 분석을 이 Phase 내에서 즉시 보완

---

### Phase 6: Recommendations

권장사항 도출 시 다음 **5단계 알고리즘** 순서를 따른다 (**순서 엄수**):

**Step 1. 요구사항 질의 (Question Requirements)**
- 이 버그가 발생하는 기능의 요구사항은 누가 만들었는가?
- 그 요구사항은 현재에도 유효한가?
- 요구사항 자체가 잘못된 것은 아닌가?

**Step 2. 삭제 (Delete)**
- 이 코드/기능을 삭제하면 버그가 사라지는가?
- Phase 5의 삭제 가능성 평가 결과 반영

**Step 3. 단순화 (Simplify)**
- 남은 코드를 더 간단하게 재구성할 수 있는가?
- 과도한 추상화나 불필요한 레이어가 있는가?

**Step 4. 가속 (Accelerate)**
- 이 버그의 재현-수정-검증 사이클을 단축하는 방법은?

**Step 5. 자동화 (Automate)**
- 이 유형의 버그를 자동 감지하는 테스트/린터를 **마지막에** 추가

> ⚠️ 흔한 실수: Step 5(자동화)부터 시작하는 것. 존재하지 말아야 할 코드를 테스트하는 것은 낭비다.

위 프레임워크를 적용한 후, 구체적 권장사항을 작성:

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

각 권장사항의 효율성을 평가:

| 권장사항 | 구현 복잡도 | 해결 범위 | 효율성 |
|----------|------------|-----------|--------|
| ... | 낮/중/높 | 이 이슈만/유사 이슈/근본적 | ★~★★★ |

→ 가장 단순하면서 근본 원인을 해결하는 방안을 우선 권장
→ "존재하지 않아야 할 것을 최적화하고 있지 않은가?" 자문

---

## Report Generation

Create a comprehensive markdown report:

### Report Structure

```markdown
# Issue Analysis: [Issue Title/ID]

## Summary
[One-paragraph executive summary]

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
- `first_principles_guide.md` - First Principles Decomposition 상세 가이드 (ST 호출 예시 포함)
- `root_cause_techniques.md` - 5 Why, 반증, 가설 관리, 효율성 평가 상세 가이드
