# Review Iteration Fresh Exploration Test

**Purpose**: Verify that plan's Step A explores new issues in each iteration

**Version**: v2.2.0
**Date Created**: 2025-12-10

---

## Test Case 1: New Issue Exploration Verification

### Scenario

Verify that plan doesn't just re-check issues found in previous iterations, but also explores new types of issues

### Preconditions (Given)

- Create incomplete initial plan file:
  - Task A: Missing Testing Strategy
  - Task B: Missing Testing Strategy
  - Task C: Task Independence issue exists (Task C and Task D are tightly coupled)
  - Task D: Missing edge case handling

### Execution (When)

1. Run plan (Iteration 1)
2. Iteration 1 review finds missing Testing Strategy in Task A, B
3. Apply Feedback: Add Testing Strategy to Task A, B
4. Run Iteration 2

### Expected Results (Then)

In Iteration 2 review file `*_PLAN_REVIEW_v2.md`:

- ✅ [CARRYOVER] Verify Task A, B Testing Strategy fixes (quality improvement)
- ✅ [NEW] Discover Task C's Task Independence issue
- ✅ [NEW] Discover Task D's missing edge case handling
- ❌ Do NOT terminate early with "Previous issues resolved, Approve"

### Success Criteria

- **At least 1 [NEW] tag in Iteration 2** ⚠️ **CRITICAL**
  - **If [NEW] count == 0**: Test FAIL - Evidence of exploration failure (Risk 5 triggered)
  - **Verification command**: `grep -c "\[NEW\]" *_PLAN_REVIEW_v2.md` → Result should be 1 or more
- Task C, D related issues first discovered in Iteration 2
- Iteration 2 recommends "Needs Iteration"
- (Not simply "Previous issues resolved, Approve" early termination)

---

## Test Case 2: Full Checklist Reapplication Verification

### Scenario

Verify that plan also re-reviews checklist sections that were not checked in previous iterations

### Preconditions (Given)

- Create incomplete initial plan file:
  - Section 1 (Completeness) related issue exists
  - Section 3 (Testing Strategy) related issue exists
  - Section 2 (Task Independence) related issue exists (but not discovered in Iteration 1)

### Execution (When)

1. Run plan (Iteration 1)
2. Iteration 1 review finds issues only in Section 1, 3
3. Apply Feedback: Fix Section 1, 3 issues
4. Run Iteration 2

### Expected Results (Then)

In Iteration 2 review:

- ✅ Verify Section 1, 3 fixes (CARRYOVER issues resolved)
- ✅ Re-review Section 2 (Task Independence) and discover new issues
- ✅ Also re-review Section 4, 5 (don't assume they were clean before)
- ❌ Do NOT "assume unchecked sections are OK"

### Success Criteria

- Evidence of 3+ checklist sections reviewed in Iteration 2
- Explicit statement "Apply FULL checklist from start"
- [NEW] issue found related to Section 2

---

## Execution Method

### Manual Testing

1. Prepare incomplete sample plan file:
   ```bash
   cp plan/tests/sample_incomplete_plan.md TEST_PLAN.md
   ```

2. Run plan:
   ```bash
   # Run plan skill in Claude Code
   /skill plan
   # Input: TEST_PLAN.md
   ```

3. Analyze review files for each iteration:
   ```bash
   # Iteration 1
   cat TEST_PLAN_REVIEW_v1.md | grep -E "(🔴|🟡)"

   # Iteration 2
   cat TEST_PLAN_REVIEW_v2.md | grep -E "\[(CARRYOVER|NEW)\]"
   ```

4. Verification:
   - [ ] [NEW] tags exist in Iteration 2
   - [ ] New category of issues discovered
   - [ ] Overall checklist section coverage increased

### Automation (Future)

```bash
# Test script to be written
./test_plan_builder_iteration.sh TEST_PLAN.md
```

---

## Verification Checklist

### Iteration 1 Verification

- [ ] Review file created: `*_PLAN_REVIEW_v1.md`
- [ ] Issues found (Required Changes or Suggested Improvements)
- [ ] All issues tagged as [NEW] (no CARRYOVER since N=1)
- [ ] Recommendation: "Needs Iteration"

### Iteration 2 Verification

- [ ] Review file created: `*_PLAN_REVIEW_v2.md`
- [ ] [CARRYOVER] tags exist (previous issue tracking)
- [ ] [NEW] tags exist ⚠️ **CRITICAL** (evidence of new exploration)
- [ ] Issues found in checklist sections not discovered before
- [ ] Recommendation: "Needs Iteration" OR "Approve" (depending on progress)

### Iteration 3+ Verification

- [ ] [CARRYOVER] issue count decreasing trend (feedback application effect)
- [ ] [NEW] issues still discoverable in Iteration N (quality improvement)
- [ ] When ZERO issues achieved: Recommendation: "Approve" + Overall Assessment: "Strong"

---

## Failure Scenarios

### Scenario A: New Exploration Failure

**Symptoms**:
- 0 [NEW] tags in Iteration 2
- Early termination with "Previous issues resolved, Approve"

**Causes**:
- CRITICAL INSTRUCTION ignored
- Over-reliance on previous review context
- FULL checklist not reapplied

**Resolution**:
- Re-verify CRITICAL INSTRUCTION block in SKILL.md Step 3
- Re-verify MANDATORY instructions in review_checklist.md Step 2

### Scenario B: CARRYOVER Tagging Error

**Symptoms**:
- Issues from previous review tagged as [NEW]
- Or new issues tagged as [CARRYOVER]

**Causes**:
- Failed to read previous review in Step 1 (Read Previous Review)
- Comparison logic error in Step 4 (Categorize Findings)

**Resolution**:
- Verify previous review file path
- Review tagging logic

---

## References

- [PLAN_BUILDER_REVIEW_ITERATION_ISSUE_REPORT.md](../../PLAN_BUILDER_REVIEW_ITERATION_ISSUE_REPORT.md) - Analysis Report
- [plan/SKILL.md](../SKILL.md) - Step A Improvements
- [plan/references/review_checklist.md](../references/review_checklist.md) - Enhanced Checklist

---

**Last Updated**: 2025-12-10
**Test Author**: Claude Sonnet 4.5
**Version**: v2.2.0
