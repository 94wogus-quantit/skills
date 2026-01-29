---
name: plan
description: Create high-quality implementation plans through iterative refinement until all quality standards are met. Use when creating implementation plans from analysis reports or requirements, especially for complex features or critical bug fixes. Generates [FEATURE]_PLAN.md with task breakdown, dependencies, and success criteria. Korean triggers: 구현 계획, 실행 계획, 개발 계획, 플랜 작성, 계획 수립, 작업 계획, 태스크 분해, 계획 세워줘, 플랜 만들어줘, 어떻게 구현할지, 작업 분해해줘.
user-invocable: true
---

# Plan - Iterative Plan Refinement

## ⛔ MANDATORY: Feedback Loop Until Perfect

> **NEVER stop after just one feedback cycle.**
>
> After reviewing the plan, if there are any changes needed:
> 1. Apply feedback
> 2. Review again
> 3. Still have changes? → Go back to step 1
> 4. **Only exit when there are ZERO remaining issues**
>
> It is NORMAL to iterate **at least 2-3 times**.
> If the first review gives "Approve", the review was too lenient.

---

## ⚠️ CRITICAL LANGUAGE POLICY

**DEFAULT LANGUAGE: KOREAN (한국어)**

ALL outputs, plans, review comments, and communications MUST be in **KOREAN** unless explicitly requested otherwise by the user.

- ✅ **Plan documents**: Write in Korean
- ✅ **Task descriptions**: Write in Korean
- ✅ **Success criteria**: Write in Korean
- ✅ **Review comments**: Write in Korean
- ✅ **User communication**: Respond in Korean

**Exception**: If the user writes in another language, match that language for responses.

**This is a MANDATORY requirement. Do NOT default to English.**

---

## Overview

Create production-ready implementation plans through systematic refinement cycles. This skill combines plan creation, critical review, and feedback application in an automated loop, continuously improving the plan until it achieves high quality standards.

**Process**: Plan → Review → Apply Feedback → Review Again → Apply Feedback → Review Again → ... → Final Approved Plan

**Output**:
- `[FEATURE]_PLAN.md` - Thoroughly reviewed, production-ready implementation plan
- Intermediate review artifacts automatically cleaned up

**Key Feature**: Iterates automatically until **zero issues remain** in the review process. NOT just once, but repeatedly until perfect.

## When to Use This Skill

Use this skill when:
- Creating implementation plans from `*_REPORT.md` analysis files
- Planning complex features or architectural changes
- Need high-confidence plans before execution
- User requests "create a plan", "plan this feature", "how should we implement this"
- Starting from JIRA requirements or GitHub issues
- Want automated quality assurance before plan execution

**vs. Simple Planning**: Use this skill when quality and thoroughness matter more than speed.

## Planning Workflow

### Phase 0: Branch Validation

⚠️ **CRITICAL: DO NOT SKIP PHASE 0**

> **MANDATORY REQUIREMENT**:
>
> - Phase 0 is the **FIRST step** of this skill
> - You **MUST** execute Phase 0 **BEFORE** proceeding to Phase 1
> - **DO NOT** assume you are on the correct branch
> - **ALWAYS** verify branch status using the MCP tool below
> - **NEVER** start plan creation (Phase 1) without completing Phase 0
>
> **Why this matters**:
> - Plan files (PLAN.md) should be committed in feature branches, not main/master
> - Running in main/master may cause merge conflicts later
> - Branch isolation ensures clean separation of work

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

**2. Handle Protected Branch**

If `is_protected` is `true`:
- Display warning message
- Recommend: "먼저 `analyze [JIRA-ID]`를 실행하여 feature 브랜치를 생성하세요"
- Ask user: "보호된 브랜치에서 계속 진행하시겠습니까?"
- If user declines: Abort skill execution

**3. Proceed to Phase 1**

- Execute existing Phase 1-3
- Save PLAN file in Phase 3 (Finalization)

---

### Phase 1: Initial Plan Creation

Create a structured task plan from requirements or analysis reports.

**1. Context Gathering**

Collect all necessary context:

- **Analysis Reports** (if available):
  - Read `*_REPORT.md` files using Read tool
  - Extract root cause, affected code locations
  - Identify recommended fixes and testing requirements

- **JIRA/Atlassian**:
  - Use `mcp__plugin_workflow-skills_atlassian__jira_get_issue` for requirements
  - Extract acceptance criteria and constraints
  - Check linked issues and dependencies

- **Codebase** (using Serena):
  - Use `mcp__plugin_workflow-skills_serena__check_onboarding_performed`
  - Use `mcp__plugin_workflow-skills_serena__list_memories` for project knowledge
  - Use `mcp__plugin_workflow-skills_serena__find_symbol` for affected components
  - Use `mcp__plugin_workflow-skills_serena__search_for_pattern` for similar code

- **Framework Documentation** (using Context7):
  - Use `mcp__plugin_workflow-skills_context7__get-library-docs` for best practices
  - Verify API usage and patterns

**2. Plan Structure Creation**

Use `mcp__plugin_seq-think_st__sequentialthinking` to organize the plan.

Reference the template in `references/plan_template.md` for complete structure.

**Critical Requirements**:
- ✅ Every task MUST have Testing Strategy
- ✅ Tasks must be independently verifiable
- ✅ Clear success criteria for each task
- ✅ Explicit dependencies (or "None")

**3. Save Initial Plan**

- Save as `[FEATURE]_PLAN.md`
- Use UPPERCASE for feature name
- Examples: `USER_AUTH_PLAN.md`, `API_REFACTOR_PLAN.md`

### Phase 2: ITERATIVE REVIEW LOOP

⚠️ **CRITICAL**: This is a LOOP, not a single pass-through phase!

This phase implements an explicit WHILE-style loop that repeats until ZERO issues remain.

### Loop Entry Condition
- Initial plan exists: `[FEATURE]_PLAN.md`
- Iteration counter: N = 1

### Loop Body (REPEAT these steps until exit condition met):

#### Step A: Review (Iteration #N)

1. **Read Previous Review (if N > 1)**
   - **Try** to load `[FEATURE]_PLAN_REVIEW_v[N-1].md` using Read tool
   - **If file not found** (may have been deleted):
     - Output warning: "⚠️ Previous review file not found (v[N-1]). Treating as first iteration."
     - Proceed as if N=1 (all issues will be tagged as [NEW])
     - Skip to Step 2
   - **If file found**:
     - Note what issues were identified last iteration
     - ⚠️ **CRITICAL**: This context helps verify fixes, NOT to limit current review scope
     - Purpose: Track progress and ensure previous Required Changes were addressed

2. **Read Current Plan**
   - Load `[FEATURE]_PLAN.md` using Read tool
   - Review all sections comprehensively

3. **Perform FULL FRESH Critical Review** ⚠️ MANDATORY
   - Use `mcp__plugin_seq-think_st__sequentialthinking` to analyze
   - Apply **ENTIRE** `references/review_checklist.md` systematically

   **⛔ CRITICAL INSTRUCTION**:
   - **DO NOT assume** sections are OK just because previous review didn't flag them
   - **APPLY FULL CHECKLIST FROM SCRATCH** every time - not just previous issue categories
   - **LOOK FOR NEW PROBLEMS** - each iteration should discover different types of issues

   **Review Focus Areas:**
   - **GitHub Repository Validation** (if applicable)
     - Code style alignment
     - Architecture compatibility
     - Dependency conflicts
     - Test coverage impact

   - **Completeness Analysis**
     - Missing components or steps
     - Overlooked edge cases
     - Error handling
     - Rollback procedures
     - Data migration needs
     - Backward compatibility

   - **Task Independence Review** (CRITICAL)
     - See `references/task_independence_guide.md`
     - Verify each task can be implemented independently
     - Check dependencies are explicit and clear
     - Ensure isolated test scope
     - Confirm success measurable without other tasks

   - **Testing Strategy Verification** (CRITICAL)
     - See `references/testing_strategy_guide.md`
     - Verify Testing Strategy section exists for each task
     - Check test type appropriate
     - Ensure test cases specific and concrete
     - Confirm acceptance criteria measurable
     - Verify test commands provided
     - Check coverage of happy path AND edge cases

   - **Feasibility Assessment**
     - Technical viability
     - Resource requirements
     - Time estimates
     - Required skills

   - **Risk Analysis**
     - Critical risks identified
     - Likelihood and impact assessed
     - Mitigation strategies present

   - **Quality & Best Practices**
     - Code quality standards
     - Security considerations
     - Performance implications
     - Maintainability

4. **Categorize Findings**

   For each issue found, mark its origin:
   - **[CARRYOVER]** - Also found in previous review (not fixed or insufficiently fixed)
   - **[NEW]** - Newly discovered in this iteration

   **How to determine**:
   - If N=1 (first iteration): All issues are [NEW]
   - If N>1: Compare with previous review file
     - Issue mentioned in previous review → [CARRYOVER]
     - Issue NOT mentioned in previous review → [NEW]

   **Purpose of tracking**:
   - **Progress verification**: Are fixes working? (CARRYOVER count should decrease)
   - **Continuous improvement**: Are we finding new problems? (NEW count should be >0 in early iterations)
   - **Audit trail**: What improved each iteration?

   **Example**:
   ```markdown
   ### Required Changes (Must Fix) 🔴

   #### Testing Strategy Issues (CRITICAL)
   1. [CARRYOVER] **Task A**: Test cases still too generic - need specific Given/When/Then
   2. [NEW] **Task C**: Missing edge case testing for null inputs
   3. [NEW] **Task D**: No test commands provided
   ```

5. **Save Review with Version Number**
   - Save as: `[FEATURE]_PLAN_REVIEW_v[N].md` (keep version number!)
   - **Include both CARRYOVER and NEW issues in findings**
   - Maintain the structure below

   **Required format for findings**:
   - Each issue must have [CARRYOVER] or [NEW] prefix
   - Group by category (Testing Strategy, Task Independence, etc.)
   - Clear task reference (Task ID or name)

   Example structure:

   ```markdown
   # Plan Review: [Plan Name] (Iteration [N])

   ## Executive Summary
   - **Overall Assessment**: Strong / Good / Needs Improvement / Major Concerns
   - **Recommendation**: Approve / Needs Iteration

   ## Critical Findings

   ### Required Changes (Must Fix) 🔴

   #### Testing Strategy Issues
   1. [CARRYOVER] **Task A**: Test cases still too generic - need specific Given/When/Then
   2. [NEW] **Task C**: Missing edge case testing for null inputs

   ### Suggested Improvements (Should Fix) 🟡
   1. [CARRYOVER] **Task B**: Consider adding integration tests
   2. [NEW] **Task D**: Enhance error messages

   ### Optional Enhancements (Nice to Have) 🟢
   1. [Enhancement]

   ### Questions for Clarification ❓
   1. [Ambiguous aspect]
   ```

6. **Output Iteration Status** (see template in Loop Exit Condition section)

#### Step B: Count Issues

Parse `[FEATURE]_PLAN_REVIEW_v[N].md` and count:

```
required_changes_count = count of 🔴 Required Changes
suggested_improvements_count = count of 🟡 Suggested Improvements
total_issues = required_changes_count + suggested_improvements_count
```

Extract from review:
- Overall Assessment value
- Recommendation value

#### Step C: Decision Gate (STRICT)

**Step C-1: Basic Checks**

```
IF (total_issues == 0 AND
    Overall Assessment == "Strong" AND
    Recommendation == "Approve"):
    → Continue to Step C-2
ELSE:
    → Go to Step D (Apply Feedback)
```

**Step C-2: AC Coverage Check (When JIRA issue linked)**

```
IF (JIRA issue linked):
    1. 🤖 Call requirement-validator agent (Mode 2: Pre-validation)
       Input: [FEATURE]_PLAN.md, JIRA issue key

    2. Check AC Completeness:
       IF (AC Completeness < 100%):
           → Add Required Change to review file:
             "AC#X missing - Task addition needed"
           → Recommendation: "Needs Iteration"
           → Go to Step D (Apply Feedback)
       ELSE:
           → AC Completeness: 100% ✅
           → EXIT LOOP → Go to Phase 3

ELSE:
    → No JIRA issue, skip AC Check
    → EXIT LOOP → Go to Phase 3
```

**⛔ STRICT Approval Criteria (ALL must be true):**
- Overall Assessment: "Strong"
- Recommendation: "Approve"
- Required Changes: ZERO
- Suggested Improvements: ZERO or trivial
- **AC Completeness: 100%** (when JIRA issue linked)

**If ANY issues remain → Continue to Step D!**

#### Step D: Apply Feedback

1. **Parse Review Feedback**

   Extract and categorize from `[FEATURE]_PLAN_REVIEW_v[N].md`:
   - Required Changes (Must Fix) - Priority 1
   - Testing Strategy Issues - Priority 1
   - Task Independence Issues - Priority 1
   - Suggested Improvements - Priority 2
   - Optional Enhancements - Priority 3

2. **Address Required Changes**

   For each required change:
   - Locate section in plan using Read tool
   - Apply recommended change using Edit tool
   - Verify change addresses feedback
   - Ensure consistency with rest of plan

3. **Fix Testing Strategies**

   For tasks missing or having inadequate testing:
   - Refer to `references/testing_strategy_guide.md` for examples
   - Add: Test type, specific test cases, measurable acceptance criteria, runnable test commands
   - Ensure coverage of happy path AND edge cases

4. **Resolve Task Independence Issues**

   Refer to `references/task_independence_guide.md` for guidance on:
   - Splitting tightly coupled tasks
   - Defining clear interfaces
   - Extracting shared functionality
   - Making tasks independently testable

5. **Apply Suggested Improvements**

   Evaluate and apply improvements that add value while maintaining plan consistency.

6. **Verification After Changes**

   Use `mcp__plugin_seq-think_st__sequentialthinking` to verify:
   - [ ] All required changes applied
   - [ ] All testing strategies complete
   - [ ] All task independence issues resolved
   - [ ] Plan structure maintained
   - [ ] Dependencies still correct

7. **Update and Track Iteration**

   - Save updated `[FEATURE]_PLAN.md`
   - **KEEP review file `[FEATURE]_PLAN_REVIEW_v[N].md`** (do NOT delete yet!)
   - Increment iteration counter: N = N + 1
   - Output iteration transition message (see template below)

8. **MANDATORY: Loop Back to Step A**

   - **Do NOT skip this step!**
   - **Do NOT ask user for approval** - automatic iteration is the core principle
   - Go back to Step A with new iteration number (N+1)
   - Perform another review to verify applied changes
   - Continue loop until review finds ZERO issues

   **⚠️ CRITICAL**: This is an **automatic** loop. Do NOT:
   - Ask "Should I continue to next iteration?"
   - Wait for user confirmation
   - Stop mid-iteration

   **ONLY exit when**: Step C Decision Gate determines "total_issues == 0"

**Iteration Transition Message Template:**

```
🔄 Iteration Transition
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Completed: Iteration [N]
  - Applied: [X] Required Changes
  - Applied: [Y] Suggested Improvements
  - Review file saved: [FEATURE]_PLAN_REVIEW_v[N].md

Next: Iteration [N+1]
  → Proceeding to Step A (Review updated plan)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Iteration Status Template (MUST output after each Step B)

```
📊 Iteration Status Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Iteration Number: [N]
Review File: [FEATURE]_PLAN_REVIEW_v[N].md

Issues Found:
  🔴 Required Changes: [X]
  🟡 Suggested Improvements: [Y]
  📊 Total Issues: [X + Y]

Overall Assessment: [Strong / Good / Needs Improvement / Major Concerns]
Recommendation: [Approve / Needs Iteration]

Decision:
  [❌ NOT READY - Proceeding to Step D, then Iteration [N+1]]
  [OR]
  [✅ READY - ZERO issues found, exiting loop to Phase 3]

Next Action:
  [→ Step D: Apply feedback, then loop back to Step A for Iteration [N+1]]
  [OR]
  [→ Exit to Phase 3 (Finalization)]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Loop Exit Condition (ALL must be true)

- ✅ total_issues == 0
- ✅ Overall Assessment == "Strong" (NOT "Good")
- ✅ Recommendation == "Approve" (NOT "Needs Iteration")
- ✅ required_changes_count == 0
- ✅ suggested_improvements_count == 0 OR only trivial ones

⛔ **FORBIDDEN**: Exiting loop if ANY issue remains!

### Loop Visualization

```
WHILE (total_issues > 0 OR Overall Assessment != "Strong") DO:

  ┌─────────────────────────────────────────────────────────┐
  │  Step A: Review Plan (Iteration #N)                     │
  │  - Read current plan                                    │
  │  - Perform critical review                              │
  │  - Save as [FEATURE]_PLAN_REVIEW_v[N].md                │
  │  - Output iteration status                              │
  └────────────────────┬────────────────────────────────────┘
                       ▼
  ┌─────────────────────────────────────────────────────────┐
  │  Step B: Count Issues                                   │
  │  - required_changes_count = count of 🔴                 │
  │  - suggested_improvements_count = count of 🟡           │
  │  - total_issues = sum                                   │
  │  - Extract Overall Assessment                           │
  │  - Extract Recommendation                               │
  └────────────────────┬────────────────────────────────────┘
                       ▼
  ┌─────────────────────────────────────────────────────────┐
  │  Step C: Check Exit Condition                           │
  │                                                          │
  │  IF (total_issues == 0 AND                              │
  │      Overall Assessment == "Strong" AND                 │
  │      Recommendation == "Approve"):                      │
  │                                                          │
  │      ✅ EXIT LOOP → Go to Phase 3                       │
  │                                                          │
  │  ELSE:                                                  │
  │      ❌ CONTINUE → Go to Step D                         │
  └────────────────────┬────────────────────────────────────┘
                       ▼
  ┌─────────────────────────────────────────────────────────┐
  │  Step D: Apply Feedback                                 │
  │  - Parse review feedback                                │
  │  - Address required changes                             │
  │  - Fix testing strategies                               │
  │  - Resolve task independence issues                     │
  │  - Apply suggested improvements                         │
  │  - Verify all changes                                   │
  │  - Save updated plan                                    │
  │  - KEEP review file (do NOT delete)                     │
  │  - Increment N: N = N + 1                               │
  │  - Output iteration transition message                  │
  │  - **MANDATORY: LOOP BACK TO STEP A**                   │
  └────────────────────┬────────────────────────────────────┘
                       │
                       └──────► LOOP BACK TO STEP A (Iteration N+1)

END WHILE

✅ Exit to Phase 3: Finalization
```

**⚠️ Red Flags to Watch:**
- If iteration 1 shows "Approve" → Review was too lenient, be more critical!
- If iteration > 5 → Plan may need fundamental restructuring
- If same issues reappear → Changes not addressing root cause

### Phase 3: Finalization

When plan receives approval, finalize and clean up.

**1. Final Quality Check**

Verify approved plan meets all standards using checklist in `references/review_checklist.md`.

**2. Clean Up Review Artifacts**

After loop completion, clean up iteration review files:

**Option A: Archive Review History** (Recommended for audit trail)

```bash
# Rename final approved review
mv [FEATURE]_PLAN_REVIEW_v[N].md [FEATURE]_PLAN_REVIEW_FINAL.md

# Create archive directory
mkdir -p .archive

# Move intermediate review versions to archive
mv [FEATURE]_PLAN_REVIEW_v*.md .archive/

# Result: Only FINAL review visible, history preserved in .archive/
```

**Option B: Delete Intermediate Reviews** (Clean workspace)

```bash
# Keep only final approved review
mv [FEATURE]_PLAN_REVIEW_v[N].md [FEATURE]_PLAN_REVIEW_FINAL.md

# Delete all intermediate versions
rm [FEATURE]_PLAN_REVIEW_v[1-9].md [FEATURE]_PLAN_REVIEW_v[0-9][0-9].md

# Result: Only FINAL review remains
```

**Why preserve review history?**
- Audit trail of iterative improvements
- Learning resource for future planning
- Evidence of thorough review process
- Debugging if issues arise during execution

**3. Document Iteration History**

Include review iteration summary in final output:

```markdown
## Review Iterations History

### Iteration 1
- **Review File**: [FEATURE]_PLAN_REVIEW_v1.md
- **Issues Found**: [X] Required Changes, [Y] Suggested Improvements
- **Key Changes Applied**: [Summary]

### Iteration 2
- **Review File**: [FEATURE]_PLAN_REVIEW_v2.md
- **Issues Found**: [X] Required Changes, [Y] Suggested Improvements
- **Key Changes Applied**: [Summary]

### Iteration N (Final)
- **Review File**: [FEATURE]_PLAN_REVIEW_FINAL.md
- **Issues Found**: ZERO ✅
- **Result**: Approved - Ready for execution
```

**4. Final Output Summary**

```markdown
# ✅ Plan Creation Complete

## Final Plan
- **File**: [FEATURE]_PLAN.md
- **Quality**: Approved after [N] review iterations
- **Tasks**: [X] tasks across [Y] priorities

## Review Iterations
1. Initial Plan → [Issues found]
2. Iteration 1 → [Improvements made]
3. Iteration N → [Approved] ✅

## Key Improvements Made
- [Improvement 1]
- [Improvement 2]

## Ready for Execution
Run: `execute [FEATURE]_PLAN.md`
```

## Best Practices

**Planning:**
- Start with comprehensive context gathering
- Use sequential thinking for organization
- Be specific about testing requirements
- Make tasks independently verifiable

**Reviewing:**
- Be thorough and critical
- Focus on Required Changes vs Nice-to-Have
- Verify every task has testing strategy
- Check task independence carefully

**Applying Feedback:**
- Address Required Changes first
- Don't skip testing strategy fixes
- Verify changes after applying
- Maintain plan consistency

**Iteration (⚠️ CRITICAL):**
- **NEVER stop after just 1 iteration** - this is almost always wrong
- Minimum 2-3 iterations is NORMAL and expected
- Complex plans may need 4-5+ iterations
- Each iteration should show improvement
- Only stop when review shows **ZERO remaining issues**
- Delete review file after each feedback application
- Quality over speed - rushing leads to bad plans

**When to Ask User:**
- Clarifying ambiguous requirements
- Choosing between valid approaches
- Confirming major architectural decisions
- Resolving conflicting constraints

## Integration with Workflow

```
1. analyze [JIRA]
   └─> [ISSUE_ID]_REPORT.md

2. plan [uses REPORT]
   └─> [FEATURE]_PLAN.md (approved)
   └─> Auto-iterates until high quality

3. execute [PLAN]
   └─> Implementation

4. record
   └─> Final documentation
```

**Key Benefit**: Automatically ensures plan quality before execution.

## Common Iteration Patterns

**Why Multiple Iterations Are Necessary:**
- First draft ALWAYS has issues - that's normal
- Each review catches different problems
- Fixing one issue often reveals others
- Quality compounds with each iteration

**Typical Pattern:**
| Iteration | Common Issues Found | Action |
|-----------|---------------------|--------|
| 1 | Missing testing strategies, vague acceptance criteria | Apply feedback → Review again |
| 2 | Task coupling, missing edge cases, incomplete error handling | Apply feedback → Review again |
| 3 | Minor polish, edge cases, documentation gaps | Apply feedback → Review again |
| 4+ | Complex edge cases (if any remain) | Continue until ZERO issues |

**⚠️ Red Flag**: If iteration 1 shows "Approve" → Review was too lenient, be more critical!

## Resources

### references/

- `plan_template.md` - Comprehensive template for task plans
- `review_checklist.md` - Detailed review evaluation criteria
- `testing_strategy_guide.md` - How to write effective testing strategies
- `task_independence_guide.md` - Ensuring tasks can be developed and tested independently

These references support each phase of the planning and review cycle.
