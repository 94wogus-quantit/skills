# Loop Verification Test Cases

This document defines test cases for verifying the feedback loop behavior of the plan skill.

---

## Test Case 1: Minimum Iterations

**Goal**: Verify that plan iterates at least 2-3 times

**Given**:
- A scenario creating a new plan
- First review is intentionally strict

**Expected**:
- No "Approve" result in Iteration 1
- At least 2 review-revision cycles occur
- Each iteration creates a `[FEATURE]_PLAN_REVIEW_v[N].md` file
- Finally repeats until ZERO issues are found

**Fail Condition**:
- Immediate "Approve" in Iteration 1
- Review file created without version number
- Skips loop and moves to Phase 3

**Test Commands**:
```bash
# Check number of generated review files (should be at least 2)
ls -la *_PLAN_REVIEW_v*.md | wc -l

# Check iteration number in each review file
grep -h "Iteration" *_PLAN_REVIEW_v*.md
```

---

## Test Case 2: Issue Counting

**Goal**: Verify that issue counting is performed accurately in Step B

**Given**:
- Issues explicitly marked in review file:
  - 🔴 Required Changes: 3
  - 🟡 Suggested Improvements: 2

**Expected**:
- Accurate count in Step B:
  - required_changes_count = 3
  - suggested_improvements_count = 2
  - total_issues = 5
- Accurate numbers output in Iteration Status Report
- Loop continues in Step C since total_issues > 0

**Fail Condition**:
- Inaccurate issue count
- Cannot distinguish between 🔴 and 🟡
- total_issues calculation error

**Test Commands**:
```bash
# Count Required Changes in review file
grep -c "🔴" [FEATURE]_PLAN_REVIEW_v1.md

# Count Suggested Improvements
grep -c "🟡" [FEATURE]_PLAN_REVIEW_v1.md

# Check numbers in Iteration Status Report
grep "Required Changes:" [FEATURE]_PLAN_REVIEW_v1.md
grep "Suggested Improvements:" [FEATURE]_PLAN_REVIEW_v1.md
grep "Total Issues:" [FEATURE]_PLAN_REVIEW_v1.md
```

---

## Test Case 3: Loop Continuation

**Goal**: Verify that loop continues when issues exist

**Given**:
- total_issues = 5 in Step B (not ZERO)
- Overall Assessment = "Good" (NOT "Strong")
- Recommendation = "Needs Iteration"

**Expected**:
- Decision in Step C: "❌ NOT READY - Proceeding to Step D"
- Proceed to Step D to apply feedback
- N = N + 1 (iteration counter increment)
- **MANDATORY**: Return to Step A (start new iteration)
- Output Iteration Transition Message

**Fail Condition**:
- Moves to Phase 3 despite having issues
- Does not return to Step A after Step D execution
- Iteration counter does not increment

**Test Commands**:
```bash
# Check Iteration Transition Message
grep "Iteration Transition" [execution log or output]

# Verify Step A re-execution after Step D (new iteration start)
grep "Iteration #2" [execution log]
```

---

## Test Case 4: Proper Exit

**Goal**: Verify that loop terminates only when issues are ZERO

**Given**:
- total_issues = 0 in Step B
- Overall Assessment = "Strong"
- Recommendation = "Approve"
- required_changes_count = 0
- suggested_improvements_count = 0

**Expected**:
- Decision in Step C: "✅ READY - ZERO issues found, exiting loop to Phase 3"
- All Loop Exit Condition requirements met
- Proceed to Phase 3 (Finalization)
- Output message "Plan approved after [N] iterations - ZERO remaining issues!"

**Fail Condition**:
- Loop continues despite ZERO issues
- Approve with "Good" Assessment (should be "Strong")
- Approve while Suggested Improvements remain

**Test Commands**:
```bash
# Check issue counts in final review file (all should be 0)
grep "Required Changes: 0" [FEATURE]_PLAN_REVIEW_v[N].md
grep "Suggested Improvements: 0" [FEATURE]_PLAN_REVIEW_v[N].md

# Verify Overall Assessment is "Strong"
grep "Overall Assessment: Strong" [FEATURE]_PLAN_REVIEW_v[N].md

# Check Phase 3 entry message
grep "Phase 3: Finalization\|Plan approved after" [execution log]
```

---

## Test Case 5: Version Tracking

**Goal**: Verify that review files are preserved with version numbers

**Given**:
- 3 iterations performed
- Review file generated for each iteration

**Expected**:
- After Iteration 1: `[FEATURE]_PLAN_REVIEW_v1.md` exists
- After Iteration 2: Both `[FEATURE]_PLAN_REVIEW_v1.md` and `v2.md` exist
- After Iteration 3: `v1.md`, `v2.md`, `v3.md` all exist
- **Intermediate review files are not deleted** (during Phase 2)
- Cleanup only in Phase 3 (archive or delete)

**Fail Condition**:
- Previous iteration review files are immediately deleted
- Overwritten without version number
- Inconsistent version number format (v1, v2 vs REVIEW_1, REVIEW_2)

**Test Commands**:
```bash
# Verify both v1, v2 files exist at Iteration 2
ls -la [FEATURE]_PLAN_REVIEW_v1.md [FEATURE]_PLAN_REVIEW_v2.md

# Check version number format consistency
ls [FEATURE]_PLAN_REVIEW_v*.md

# Verify only FINAL file remains after Phase 3 cleanup
ls [FEATURE]_PLAN_REVIEW_FINAL.md
ls .archive/[FEATURE]_PLAN_REVIEW_v*.md  # If archive option selected
```

---

## Comprehensive Verification Checklist

Verify the following after actual plan skill execution:

- [ ] **Minimum Iterations**: At least 2 iterations performed
- [ ] **Issue Counting**: Issue counts are accurate
- [ ] **Loop Continuation**: Loop continues when issues exist
- [ ] **Proper Exit**: Terminates only when issues are ZERO
- [ ] **Version Tracking**: Review files preserved with version numbers
- [ ] **Iteration Status Report**: Output for each iteration
- [ ] **Iteration Transition Message**: Output after Step D
- [ ] **Phase 3 Cleanup**: Final review file cleanup completed

---

## Notes

These test cases define behaviors that should automatically execute **when the plan skill itself runs**.

Actual verification method:
1. Create a new plan with the plan skill
2. Check execution logs and generated files
3. Verify that all 5 test case conditions above are met

Expected success scenario:
- ✅ Iteration 1: 9 issues found → Step D (apply feedback)
- ✅ Iteration 2: 2 issues found → Step D (apply feedback)
- ✅ Iteration 3: ZERO issues → Exit to Phase 3 ✅
