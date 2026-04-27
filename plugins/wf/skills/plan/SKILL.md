---
name: plan
description: Create high-quality implementation plans through iterative refinement until all quality standards are met. Use when creating implementation plans from analysis reports or requirements, especially for complex features or critical bug fixes. Generates [FEATURE]_PLAN.md with task breakdown, dependencies, and success criteria. Korean triggers: 구현 계획, 실행 계획, 개발 계획, 플랜 작성, 계획 수립, 작업 계획, 태스크 분해, 계획 세워줘, 플랜 만들어줘, 어떻게 구현할지, 작업 분해해줘.
user-invocable: true
---

# Plan - Externally-Gated Plan Refinement

## ⛔ MANDATORY: External Review Gate (no self-review)

> **The Worker that writes the plan must NOT review the plan.**
>
> Pre-v3.30 versions of this skill ran a self-review loop inside the same session that wrote the plan. That pattern is structurally biased — the author of a plan is incentivized to declare it done. v3.30 replaces self-review with an external gate:
>
> 1. Worker writes `[FEATURE]_PLAN.md` (Phase 2 output).
> 2. The wf plugin's `wf-review-gate.sh` hook (`PostToolUse(Write)`) detects the write and injects a `systemMessage` requesting the Worker to spawn the `wf:wf-review-plan` agent.
> 3. Worker spawns the agent. The agent reads the plan in a fresh context, applies `references/review_checklist.md`, and writes `[FEATURE]_PLAN_REVIEW.md` with `VERDICT: LGTM` or `VERDICT: REVISE`.
> 4. Worker reads the verdict file. **REVISE → apply feedback, Write the plan again (re-triggers the gate). LGTM → proceed to Phase 4.**
>
> The hook + external agent pair is the load-bearing mechanism that prevents premature "Approve". The Worker never produces its own LGTM.

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

Create production-ready implementation plans, gated by an independent external reviewer (`wf:wf-review-plan` agent) that runs after each plan write. The Worker writes the plan; the agent judges it; the Worker applies feedback if needed and writes again. The skill exits only when the latest external `[FEATURE]_PLAN_REVIEW.md` carries `VERDICT: LGTM`.

**Process**: Plan → (Worker Writes) → External Review Gate → REVISE → Apply Feedback → Write again → External Review Gate → ... → LGTM → Finalize

**Output**:

- `[FEATURE]_PLAN.md` — production-ready implementation plan, externally approved
- `[FEATURE]_PLAN_REVIEW.md` — most recent external verdict (kept as audit artifact)

**Key Feature**: Worker never self-approves. The exit gate is an external agent's verdict file, not the Worker's own judgment.

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

### Startup: Mode Detection *(Run First, Every Time)*

Before any phase, detect whether this is a normal first run or a ralph-loop restart.

**1. Check Ralph Loop State**

Attempt to read `.claude/ralph-loop.local.md` using the Read tool.

- **File not found**: → **NORMAL MODE** → Proceed to Phase 0
- **File found, `active: false`**: → **NORMAL MODE** → Proceed to Phase 0
- **File found, `active: true`**: → **RALPH LOOP ITERATION MODE**

**2. Ralph Loop Iteration Mode**

Extract from `.claude/ralph-loop.local.md`:
- `iteration:` field → current iteration number N
- File content below frontmatter → PLAN filename (e.g. `ASK_YT_PLAN.md`)

Output:
```
🔄 Ralph Loop Iteration #[N] detected
   Plan: [FEATURE]_PLAN.md
   → Skipping to Phase 3 (review only)
```

**⛔ SKIP Phase 0, Phase 1, Phase 2 entirely.**
**→ Jump directly to Phase 3: External Review Gate.**

---

### Phase 0: Task Registration

⚠️ **CRITICAL: DO NOT SKIP PHASE 0**

**Objective**: Register all Phases as Tasks to track progress throughout the plan workflow.

Register the following Phases in order using `TaskCreate`:

| Task    | subject               | activeForm                 |
| ------- | --------------------- | -------------------------- |
| Phase 1 | Branch Validation     | Validating branch          |
| Phase 2 | Initial Plan Creation | Creating initial plan      |
| Phase 3 | External Review Gate  | Awaiting external review   |
| Phase 4 | Finalization          | Finalizing plan            |

**Task Tracking Rules**:

- On Phase entry: `TaskUpdate(taskId, status: "in_progress")`
- On Phase completion: `TaskUpdate(taskId, status: "completed")`
- Only **one Phase** should be `in_progress` at any time

---

### Phase 1: Branch Validation

> 📋 **Task Tracking**: Mark this Phase's Task as `in_progress` on entry, `completed` on completion.

> **MANDATORY REQUIREMENT**:
>
> - **DO NOT** assume you are on the correct branch
> - **ALWAYS** verify branch status using the MCP tool below
> - **NEVER** start plan creation (Phase 2) without completing Phase 1
>
> **Why this matters**:
>
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
  - Output: `⚠️ 보호된 브랜치({branch})에서 작업합니다. 변경사항이 직접 반영됩니다.`

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

- If REPORT file exists: Suggest `feature/{ID_from_REPORT}` format
- If JIRA ID exists: Suggest `feature/JIRA-123` format
- Otherwise: Suggest `feature/plan-{YYYYMMDD}` format

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

### Phase 2: Initial Plan Creation (5-Step Algorithm)

> 📋 **Task Tracking**: Mark this Phase's Task as `in_progress` on entry, `completed` on completion.

Create a structured task plan using the **5-Step Algorithm** as the core thinking methodology. Each step builds on the previous — follow in strict order.

> For detailed process, examples, and Sequential Thinking invocation patterns, see `references/planning_mental_model.md`

**Step 1: Context Gathering**

Collect all necessary context before thinking about tasks:

- **Analysis Reports**: Read `*_REPORT.md` files, extract root cause and recommendations
- **JIRA/Atlassian**: Use `mcp__plugin_atlassian_atlassian__jira_get_issue` for requirements and AC
- **Codebase**: Use Serena tools (`check_onboarding_performed`, `list_memories`, `find_symbol`, `search_for_pattern`)
- **Framework Docs**: Use Context7 (`resolve-library-id`, `query-docs`) for best practices

> **⚠️ Evidence Trail**: After collecting context, record ALL sources and key findings in a Context Log table. This log will be included in the final PLAN's "Context & Reasoning" section.
>
> | #   | 소스     | 핵심 발견   |
> | --- | -------- | ----------- |
> | 1   | [소스명] | [발견 내용] |

**Step 2: Requirement Questioning** (Musk Step 1)

Use `mcp__plugin_seq-think_st__sequentialthinking` to question every requirement:

- Trace each requirement to a **named person** (not a department)
- Challenge cargo-culted conventions ("we always do it this way")
- Verify each requirement is **still valid today**
- Flag requirements without a named owner as deletion candidates

> "Requirements from smart people are the most dangerous — nobody questions them."

> **⚠️ Evidence Trail**: Record the key reasoning from this step in the Context Log (which requirements were questioned, validated, or flagged).

**Step 3: Deletion Pass** (Musk Step 2)

Use `mcp__plugin_seq-think_st__sequentialthinking` to perform aggressive deletion:

- List all planned components/tasks and attempt to delete each one
- Target: remove **20-30%** of initial scope
- Apply the **10% restoration rule**: if nothing is added back later, deletion was too conservative
- Delete: premature abstractions, future-proofing, unnecessary admin panels, feature flags for one-time deploys

> "If you don't end up adding back at least 10% of what you deleted, you didn't delete enough."

> **⚠️ Evidence Trail**: Record what was deleted and why in the Context Log.

**Step 4: Simplification** (Musk Step 3)

Use `mcp__plugin_seq-think_st__sequentialthinking` to simplify remaining tasks:

- Replace custom solutions with standard libraries where possible
- Merge overlapping tasks, flatten unnecessary hierarchies
- Remove over-abstraction layers
- ⚠️ Only simplify tasks that survived Step 3 — never optimize what should be deleted

> **⚠️ Evidence Trail**: Record simplification decisions in the Context Log.

**Step 5: Plan Structure Creation** (with Zero-Context Principle)

Reference `references/plan_template.md` for complete structure. Apply **Zero-Context Principle**:

- Every task specifies **exact file paths**, **specific code references**, **runnable test commands**
- A reader with zero codebase familiarity must be able to execute each task

**Critical Requirements**:

- ✅ Every task MUST have Testing Strategy (Given/When/Then)
- ✅ Tasks must be independently verifiable
- ✅ Clear success criteria for each task
- ✅ Explicit dependencies (or "None")

**Step 6: Acceleration Analysis** (Musk Step 4)

Use `mcp__plugin_seq-think_st__sequentialthinking` to optimize execution speed:

- Identify parallelizable work streams
- Remove artificial sequential dependencies
- Plan for incremental delivery (small PRs, early integration)
- Document critical path and parallel opportunities in the plan

**Step 7: Save Initial Plan with Idiot Index Self-Check**

- Save as `[FEATURE]_PLAN.md` (UPPERCASE feature name)
- Before saving, calculate **Idiot Index** (see `references/planning_mental_model.md`):
  - Idiot Index = Total plan effort / Core functionality effort
  - If > 3x: re-run Step 3 (Deletion Pass)
  - If > 5x: fundamental redesign needed

> **⚠️ Evidence Trail**: Include the accumulated Context Log as the "Context & Reasoning" section in the PLAN document (after "Constraints", before "Task Breakdown").

### Phase 3: External Review Gate

> 📋 **Task Tracking**: Mark this Phase's Task as `in_progress` on entry, `completed` on completion.

> **Replaces the pre-v3.30 self-review loop.** The Worker that wrote `[FEATURE]_PLAN.md` does **not** review it — `wf:wf-review-plan` does, in a separate context, via the plugin's `wf-review-gate.sh` PostToolUse(Write) hook.

---

#### How the gate works

When `[FEATURE]_PLAN.md` is written via the Write tool, `wf-review-gate.sh` (registered in `plugins/wf/hooks/hooks.json`) intercepts the PostToolUse event and emits a `systemMessage` of the form:

```
[wf-review-gate] [FEATURE]_PLAN.md 작성 감지. wf:wf-review-plan 에이전트를 소환하여 리뷰해주세요.
Agent(subagent_type: "wf:wf-review-plan", description: "Plan 리뷰", prompt: "...")
```

The Worker follows that message verbatim. The agent reads the PLAN in a fresh context (no anchoring on the Worker's reasoning), applies the checklist defined in `plugins/wf/agents/wf-review-plan.md`, and writes `[FEATURE]_PLAN_REVIEW.md` (or `[FEATURE]_PLAN_REVIEW_v[N].md` if iterating) ending with `VERDICT: LGTM` or `VERDICT: REVISE`.

When the review file is written, the same hook fires again on Pattern 4 (`*_REVIEW.md`). It reads the VERDICT line and emits one of:

- **REVISE** → Worker is told to apply the feedback and Write `[FEATURE]_PLAN.md` again, which re-triggers the review cycle.
- **LGTM** → Worker proceeds to Phase 4 (Finalization).

There is no internal `WHILE total_issues > 0` loop in this skill. The Worker's only job each cycle is: write/edit the plan, follow the hook's spawn prompt, read the verdict, and either revise or proceed.

---

#### Step 0: Initial PLAN.md write

After Phase 2 produced the plan content in memory, save it:

```
Tool: Write
Args:
  file_path: "[FEATURE]_PLAN.md"
  content: "<full plan body from Phase 2 — including Evidence Trail / Context Log>"
```

This Write triggers Pattern 2 of `wf-review-gate.sh` and produces a `systemMessage` requesting `wf:wf-review-plan` spawn. **Follow that systemMessage.**

If the gate is unavailable for any reason (plugin disabled, hook misconfigured), spawn the agent manually:

```
Tool: Agent
Args:
  subagent_type: "wf:wf-review-plan"
  description: "Plan 리뷰"
  prompt: |
    phase: plan
    artifact_path: [FEATURE]_PLAN.md
    report_path: [ISSUE_ID]_REPORT.md   # if exists, for cross-reference

    위 파일을 Plan 리뷰 체크리스트에 따라 평가해주세요.
    VERDICT: LGTM 또는 REVISE로 반환하고, 결과를 같은 디렉토리에
    [FEATURE]_PLAN_REVIEW.md로 저장해주세요.
```

#### Step 1: Read the verdict file

After the agent finishes, Read `[FEATURE]_PLAN_REVIEW.md`. Locate the final `VERDICT:` line.

#### Step 2: Verdict gate

| Verdict | Action |
|---------|--------|
| `LGTM` | Phase 4 (Finalization)로 진행. 이 skill은 자체적으로 LGTM을 발행하지 않으며, 외부 agent의 verdict만 인정한다. |
| `REVISE` | review 본문의 "수정 요청" 섹션을 읽고 PLAN의 해당 섹션을 Edit한다. 모든 요청 처리 후 PLAN.md를 다시 Write한다 → Pattern 2 hook 재발화 → 새 review-* 생성 → Step 1로 복귀. |

#### Step 3: AC Coverage Check (when JIRA / issue ID linked)

Independent of the LGTM/REVISE cycle above, when an issue ID is present in the PLAN's metadata, after the first LGTM run the requirement-validator agent for AC coverage:

```
Tool: Task
Args:
  subagent_type: "wf:requirement-validator"
  description: "AC pre-validation"
  prompt: |
    Mode 2: Pre-validation

    계획이 모든 AC를 커버하는지 검증합니다.

    Input:
    - PLAN 파일: [FEATURE]_PLAN.md
    - Issue key: {ISSUE_KEY}

    Output:
    - AC Coverage 퍼센트
    - 누락된 AC 목록
```

If AC Coverage < 100%, inject the missing AC into the PLAN, Write again to re-trigger the gate, and loop back to Step 1. If AC Coverage = 100%, proceed to Phase 4.

#### Why this is structurally safer than the old self-review loop

- **Independence**: the agent runs with no memory of why the Worker chose particular tasks, so it judges the plan on its own merits.
- **Bounded latency**: the Worker no longer iterates internally on the same context for hours. Each cycle is one Write + one agent spawn + one verdict read + one Edit pass.
- **Auditable**: every cycle leaves a `[FEATURE]_PLAN_REVIEW*.md` artifact behind, so the verdict trail is inspectable post-hoc.
- **No fake "Approve" pressure**: the Worker cannot self-declare LGTM. The skill's exit gate is literally the agent's verdict file.

#### Legacy notes

The old Phase 3 contained an internal Step A → Step B → Step C → Step D loop that repeated until "ZERO issues" — and a parallel "ralph-loop integration" branch that delegated the loop to the ralph-loop plugin. Both are removed in v3.30. If you find pre-v3.30 prompts referencing those steps, treat them as obsolete; the external gate above is the only supported review path.


### Phase 4: Finalization

> 📋 **Task Tracking**: Mark this Phase's Task as `in_progress` on entry, `completed` on completion.

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

- **Review File**: [FEATURE]\_PLAN_REVIEW_v1.md
- **Issues Found**: [X] Required Changes, [Y] Suggested Improvements
- **Key Changes Applied**: [Summary]

### Iteration 2

- **Review File**: [FEATURE]\_PLAN_REVIEW_v2.md
- **Issues Found**: [X] Required Changes, [Y] Suggested Improvements
- **Key Changes Applied**: [Summary]

### Iteration N (Final)

- **Review File**: [FEATURE]\_PLAN_REVIEW_FINAL.md
- **Issues Found**: ZERO ✅
- **Result**: Approved - Ready for execution
```

**4. Final Output Summary**

```markdown
# ✅ Plan Creation Complete

## Final Plan

- **File**: [FEATURE]\_PLAN.md
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

**External Review Gate (⚠️ CRITICAL):**

- **Never self-approve.** The Worker does not produce LGTM. Only `wf:wf-review-plan`'s `[FEATURE]_PLAN_REVIEW.md` does.
- **Do not paraphrase the verdict.** Read the literal `VERDICT:` line from the review file. `LGTM` proceeds to Phase 4; anything else (REVISE, ambiguous) means apply feedback and Write the plan again.
- **One Write per cycle.** Each plan Write triggers the gate exactly once. Don't pre-emptively iterate locally before writing — let the agent see the actual saved file each cycle.
- **Keep the review artifact.** `[FEATURE]_PLAN_REVIEW.md` is the audit trail. Don't delete it after applying feedback; it documents *why* the plan changed.
- **Quality over speed** — when REVISE feedback is dense, address every required change before re-writing. A pre-emptive Write to "see if it passes" wastes a review cycle.

**When to Ask User:**

- Clarifying ambiguous requirements
- Choosing between valid approaches
- Confirming major architectural decisions
- Resolving conflicting constraints

---

### Phase 5: Next Step Confirmation

After finalizing the plan, ask the user whether to proceed to the next workflow step.

**Use `AskUserQuestion` tool:**

```yaml
questions:
  - question: "구현 계획이 완성되었습니다. 다음 단계로 진행할까요?"
    header: "Next"
    options:
      - label: "execute 스킬 실행 (Recommended)"
        description: "계획을 바탕으로 코드를 구현합니다"
      - label: "여기서 종료"
        description: "계획 수립만 완료하고 종료합니다"
```

- **If "execute 스킬 실행" selected**: Invoke the `execute` skill with the generated plan
  - Output: `✅ execute 스킬을 실행합니다...`
- **If "여기서 종료" selected**: End the workflow
  - Output: `✅ 계획 수립이 완료되었습니다. 플랜: {PLAN_FILE}`

---

## Integration with Workflow

```
1. analyze [JIRA]
   └─> [ISSUE_ID]_REPORT.md

2. plan [uses REPORT]
   └─> [FEATURE]_PLAN.md (approved)
   └─> External review gate (wf:wf-review-plan) until LGTM

3. execute [PLAN]
   └─> Implementation

4. record
   └─> Final documentation
```

**Key Benefit**: Automatically ensures plan quality before execution.

## Common External-Review Cycles

**Why multiple Write→Review cycles are normal:**

- First draft almost always gets REVISE — that's the gate working as intended
- The external agent reads the plan in a fresh context each cycle, so it surfaces issues the Worker didn't anticipate
- Fixing one REVISE item often exposes adjacent ones in the next cycle
- Quality compounds across cycles, so don't try to short-circuit by writing the perfect first draft

**Typical pattern (REVISE feedback shape per cycle):**
| Cycle | Common REVISE feedback shape | Worker action |
|-------|------------------------------|---------------|
| 1 | Missing testing strategies, vague acceptance criteria | Read review file → Edit plan → Write again |
| 2 | Task coupling, missing edge cases, incomplete error handling | Read review file → Edit plan → Write again |
| 3 | Minor polish, edge cases, documentation gaps | Read review file → Edit plan → Write again |
| 4+ | Residual edge cases | Continue until LGTM verdict |

**⚠️ Red Flag**: If the external agent returns LGTM on cycle 1, double-check that the agent actually applied `references/review_checklist.md` end-to-end — a too-lenient agent run is the new failure mode that replaces "self-approving Worker".

## Resources

### references/

- `plan_template.md` - Comprehensive template for task plans
- `review_checklist.md` - Detailed review evaluation criteria
- `testing_strategy_guide.md` - How to write effective testing strategies
- `task_independence_guide.md` - Ensuring tasks can be developed and tested independently

These references support each phase of the planning and review cycle.
