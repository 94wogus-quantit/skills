# Plan Review Checklist

Comprehensive checklist for reviewing implementation plans. Use this to ensure thorough evaluation across all critical dimensions.

---

## Review Process

### Step 1: Initial Read-Through
- [ ] Read the entire plan from start to finish
- [ ] Understand the overall objective and context
- [ ] Note initial impressions and concerns

### Step 2: Systematic Evaluation

⚠️ **MANDATORY**: Apply the FULL checklist EVERY TIME, regardless of previous reviews.

**Critical Requirements**:
- [ ] Work through **ALL sections** of this checklist (1-10)
- [ ] Do not skip sections even if previous review was clean
- [ ] Document specific issues with task/section references
- [ ] Look for NEW problems, not just CARRYOVER issues from previous reviews
- [ ] Each iteration should catch different types of issues
- [ ] Categorize findings: Required Changes / Suggested / Optional

**Why this matters**:
- Early iterations catch obvious problems (missing sections, unclear criteria)
- Later iterations catch subtle problems (coupling, edge cases, performance)
- Skipping sections means missing potential issues

### Step 3: Assessment & Recommendation
- [ ] Assign overall assessment (Strong / Good / Needs Improvement / Major Concerns)
- [ ] Make recommendation (Approve / Needs Iteration)
- [ ] List all findings in priority order

---

## 1. Completeness Analysis

### Task Breakdown
- [ ] All necessary tasks are included
- [ ] No obvious steps missing from the workflow
- [ ] Tasks cover the full scope of the objective
- [ ] Both implementation and validation tasks present

### Edge Cases & Error Handling
- [ ] Edge cases identified and addressed
- [ ] Error handling strategy defined
- [ ] Failure scenarios considered
- [ ] Recovery procedures included

### Non-Functional Requirements
- [ ] Performance considerations addressed
- [ ] Security implications reviewed
- [ ] Scalability concerns handled
- [ ] Maintainability considerations included

### Documentation & Communication
- [ ] Documentation updates planned
- [ ] Stakeholder communication strategy defined
- [ ] User-facing changes documented

---

## 2. Task Independence & Boundaries

### Task Independence (CRITICAL)
For each task, verify:

- [ ] **Can be implemented independently**
  - No implicit dependencies on other tasks
  - External dependencies are explicit
  - Shared code is factored out or mocked

- [ ] **Has clear boundaries**
  - Input and output clearly defined
  - Responsibility scope is well-defined
  - No overlap with other tasks

- [ ] **Can be tested in isolation**
  - Tests don't require other tasks to complete
  - Test dependencies can be mocked
  - Success is verifiable independently

- [ ] **Has measurable success criteria**
  - Success can be determined without other tasks
  - Criteria are objective and testable

### Common Independence Issues

**Tight Coupling Red Flags**:
- ❌ Task description says "...and also..."  (doing too much)
- ❌ Task depends on runtime state from another task
- ❌ Tests require executing previous tasks first
- ❌ Success criteria mention other tasks

**How to Fix**:
- Split into smaller, focused tasks
- Define clear interfaces between tasks
- Extract shared logic to separate utility task
- Use dependency injection or mocks for testing

---

## 3. Testing Strategy Quality (CRITICAL)

### For Each Task

- [ ] **Testing Strategy Section Exists**
  - Every task has a "Testing Strategy" section
  - No tasks are missing this critical section

- [ ] **Test Type is Appropriate**
  - Unit tests for isolated logic
  - Integration tests for component interactions
  - E2E tests for user workflows
  - Manual tests only when automation isn't feasible

- [ ] **Test Cases are Specific**
  - Not generic (e.g., "test the feature works")
  - Concrete scenarios with Given/When/Then
  - Edge cases included
  - Error scenarios covered

- [ ] **Acceptance Criteria are Measurable**
  - Clear pass/fail conditions
  - Objective and verifiable
  - Coverage thresholds specified if applicable
  - No vague criteria (e.g., "works well")

- [ ] **Test Commands Provided**
  - Actual runnable commands
  - Correct syntax and parameters
  - Can be executed without additional setup
  - Example: `npm test src/module.test.ts` or `pytest tests/test_feature.py -v`

### Common Testing Strategy Issues

**Insufficient Examples**:
- ❌ "Test that login works"
- ✅ "Test login with valid credentials returns auth token"
- ✅ "Test login with invalid password returns 401 error"
- ✅ "Test login with non-existent user returns 404 error"

**Vague Acceptance Criteria**:
- ❌ "All tests pass"
- ✅ "All 15 unit tests pass with >80% code coverage"
- ✅ "Integration tests verify API returns 200 status"
- ✅ "E2E test completes user registration flow successfully"

**Missing Test Commands**:
- ❌ "Run the tests"
- ✅ "npm test src/auth/login.test.ts"
- ✅ "pytest tests/integration/test_api.py -v -k login"

---

## 4. Feasibility & Technical Viability

### Technical Approach
- [ ] Implementation approach is sound
- [ ] Technologies/frameworks are appropriate
- [ ] No obvious technical blockers
- [ ] Architecture aligns with existing system

### Resource Requirements
- [ ] Time estimates are realistic (not overly optimistic)
- [ ] Required skills are available
- [ ] Necessary tools and access are secured
- [ ] External dependencies are manageable

### Complexity Assessment
- [ ] Tasks are appropriately sized (S/M/L)
- [ ] No tasks are attempting too much
- [ ] Complex tasks are broken down sufficiently
- [ ] Simple tasks aren't over-engineered

---

## 5. Dependencies & Sequencing

### Dependency Clarity
- [ ] All dependencies explicitly stated
- [ ] No hidden or implied dependencies
- [ ] External dependencies identified
- [ ] Circular dependencies avoided

### Critical Path
- [ ] Critical path is identified
- [ ] Critical path duration is reasonable
- [ ] Bottlenecks are addressed
- [ ] Parallel opportunities identified

### Ordering Logic
- [ ] Task sequence is logical
- [ ] Dependencies flow properly
- [ ] No unnecessary sequencing
- [ ] Blocking tasks identified

---

## 6. Risk Management

### Risk Identification
- [ ] Major risks identified and documented
- [ ] Likelihood and impact assessed
- [ ] Risk priorities assigned

### Mitigation Strategies
- [ ] Each high-impact risk has mitigation
- [ ] Mitigations are concrete and actionable
- [ ] Contingency plans for critical risks
- [ ] Early warning indicators defined

### Unaddressed Risks
Look for risks not mentioned:
- [ ] Data loss or corruption risks
- [ ] Security vulnerabilities
- [ ] Performance degradation
- [ ] User experience issues
- [ ] Integration failures
- [ ] Deployment risks

---

## 7. Quality & Best Practices

### Code Quality
- [ ] Code standards will be followed
- [ ] Review process defined
- [ ] Refactoring opportunities identified
- [ ] Technical debt addressed

### Security
- [ ] Security implications reviewed
- [ ] Authentication/authorization considered
- [ ] Data protection addressed
- [ ] Vulnerability prevention planned

### Performance
- [ ] Performance impact assessed
- [ ] Optimization opportunities noted
- [ ] Performance testing planned
- [ ] Scalability considered

### Maintainability
- [ ] Code will be maintainable
- [ ] Documentation strategy defined
- [ ] Knowledge transfer planned
- [ ] Support procedures considered

---

## 8. Deployment & Operations

### Deployment Strategy
- [ ] Deployment approach defined
- [ ] Rollout plan is reasonable
- [ ] Rollback procedure documented
- [ ] Feature flags considered if applicable

### Monitoring & Observability
- [ ] Monitoring strategy defined
- [ ] Metrics to track identified
- [ ] Alerts configured
- [ ] Dashboards planned

### Operational Readiness
- [ ] Runbooks needed are identified
- [ ] On-call procedures considered
- [ ] Incident response planned
- [ ] Support team briefed

---

## 9. GitHub Repository Alignment (if applicable)

When plan references a GitHub repository:

### Code Style & Conventions
- [ ] Plan follows repository conventions
- [ ] Naming patterns match existing code
- [ ] File organization aligns with structure
- [ ] Comment/documentation style consistent

### Architecture Compatibility
- [ ] Changes fit existing architecture
- [ ] No violations of architectural principles
- [ ] Integration points properly identified
- [ ] Component boundaries respected

### Dependency Management
- [ ] No dependency conflicts
- [ ] Version compatibility verified
- [ ] License compatibility checked
- [ ] Dependency additions justified

### Test Coverage
- [ ] Maintains or improves test coverage
- [ ] Test patterns match existing tests
- [ ] CI/CD integration considered
- [ ] Test infrastructure adequate

---

## 10. Documentation & Communication

### Documentation Plan
- [ ] Required documentation identified
- [ ] Documentation scope is adequate
- [ ] Update process defined
- [ ] Review process for docs

### Communication Strategy
- [ ] Stakeholders identified
- [ ] Communication frequency defined
- [ ] Communication channels specified
- [ ] Milestone notifications planned

---

## Review Output Template

```markdown
# Plan Review: [Plan Name]

## Executive Summary
- **Overall Assessment**: [Strong / Good / Needs Improvement / Major Concerns]
- **Confidence Level**: [High / Medium / Low]
- **Recommendation**: [Approve / Needs Iteration]
- **Loop Decision**: [✅ Exit Loop / 🔄 Continue Loop]
- **GitHub Repository Alignment**: [If applicable]

---

## Detailed Findings

### 1. Completeness Analysis
[Score: ✅ Complete / ⚠️ Minor gaps / ❌ Major gaps]

**Missing Components**:
- [List any missing tasks or steps]

**Overlooked Considerations**:
- [List overlooked edge cases, error handling, etc.]

---

### 2. Task Independence Review
[Score: ✅ All independent / ⚠️ Some coupling / ❌ Major coupling]

**Issues Found**:
- **[Task X]**: [Coupling issue description]
  - **Problem**: [What's tightly coupled]
  - **Impact**: [Why it matters]
  - **Fix**: [How to resolve]

---

### 3. Testing Strategy Quality
[Score: ✅ Comprehensive / ⚠️ Adequate / ❌ Insufficient]

**Issues Found**:
- **[Task Y]**: Missing Testing Strategy
- **[Task Z]**: Vague acceptance criteria
  - Current: "Tests pass"
  - Needed: "All 10 unit tests pass with >80% coverage"

---

### 4. Feasibility Assessment
[Score: ✅ Viable / ⚠️ Concerns / ❌ Blocked]

**Technical Concerns**:
- [List technical issues]

**Resource Concerns**:
- [List resource issues]

---

### 5. Dependencies & Sequencing
[Score: ✅ Clear / ⚠️ Some ambiguity / ❌ Unclear]

**Dependency Issues**:
- [List dependency problems]

**Critical Path**:
- [Assess critical path reasonableness]

---

### 6. Risk Management
[Score: ✅ Well managed / ⚠️ Gaps / ❌ Insufficient]

**Unaddressed Risks**:
- [List risks not mentioned]

**Insufficient Mitigation**:
- [List risks needing better mitigation]

---

### 7. Quality & Best Practices
[Score: ✅ Strong / ⚠️ Adequate / ❌ Concerns]

[Assessment of code quality, security, performance, maintainability]

---

### 8. Deployment & Operations
[Score: ✅ Ready / ⚠️ Needs work / ❌ Insufficient]

[Assessment of deployment and operational readiness]

---

## Summary of Findings

### Required Changes (Must Fix) 🔴

#### Testing Strategy Issues (CRITICAL)
1. **[Task A]**: Missing Testing Strategy section entirely
2. **[Task B]**: Test cases too generic - need specific Given/When/Then
3. **[Task C]**: No test commands provided

#### Task Independence Issues (CRITICAL)
1. **[Task D]**: Tightly coupled with Task E - cannot test independently
2. **[Task F]**: Unclear boundaries with Task G

#### Other Critical Issues
1. [Critical issue 1]
2. [Critical issue 2]

### Suggested Improvements (Should Fix) 🟡
1. [Important improvement 1]
2. [Important improvement 2]

### Optional Enhancements (Nice to Have) 🟢
1. [Enhancement 1]
2. [Enhancement 2]

### Questions for Clarification ❓
1. [Question about ambiguous aspect 1]
2. [Question about ambiguous aspect 2]

---

## Recommendation

**Final Recommendation**: [Approve / Needs Iteration]

**Loop Decision**: [✅ Exit Loop (if Approve) / 🔄 Continue Loop (if Needs Iteration)]

**Reasoning**: [Brief explanation of the recommendation]

**Next Steps**:
- If Approve: Exit loop → Proceed to Phase 3 (Finalization)
- If Needs Iteration: Apply feedback → Review again (new iteration)
- If changes needed: Apply feedback and re-review
- If major revision: Re-plan with different approach
```

---

## Review Best Practices

### Be Thorough
- Don't skim - review every task carefully
- Use the checklist systematically
- Document all findings, even minor ones

### Be Specific
- Reference exact tasks and sections
- Provide concrete examples of issues
- Suggest specific fixes, not just "improve this"

### Be Constructive
- Focus on improving the plan
- Explain why something is problematic
- Offer actionable recommendations

### Prioritize
- Distinguish must-fix from nice-to-have
- Start with critical issues (testing, independence)
- Save polish for later iterations

### Be Objective
- Base assessment on criteria, not feelings
- Use evidence from the plan
- Explain your reasoning

---

## Approval Criteria

⚠️ **IMPORTANT**: plan skill uses STRICT binary approval!

This checklist is used within an **iterative loop**.
There is no ambiguous option like "Approve with Changes".
Either the plan is ready (Approve), or another iteration is needed (Needs Iteration).

### ✅ Approve (Ready for Execution)

**Use this ONLY when ALL of the following are true:**
- Overall Assessment: "Strong" (NOT "Good" - Good means needs more work!)
- All critical sections (1-8) score ✅ (green checkmark)
- Required Changes (🔴): **ZERO** (not "minor", not "a few" - ZERO!)
- Suggested Improvements (🟡): **ZERO or only trivial ones** (e.g., minor wording tweaks)
- No open questions remaining (❓ section empty)

**Result**: Exit the review loop → Proceed to Phase 3 (Finalization)

### 🔄 Needs Iteration (Apply Feedback and Review Again)

**Use this when ANY of the following are true:**
- Overall Assessment: "Good", "Needs Improvement", or "Major Concerns"
- Any critical section scores ⚠️ or ❌
- Required Changes (🔴): ANY (even ONE Required Change means Needs Iteration!)
- Suggested Improvements (🟡): ANY significant improvements needed
- Open questions (❓): ANY questions that need clarification

**Result**: Continue loop → Phase 2D (Apply Feedback) → Phase 2A (Review Again)

---

### ⛔ REMOVED: "Approve with Changes"

**This option has been removed.**

**Reason**:
- Ambiguous criteria caused premature termination of feedback loops
- The definition of "minor changes" was unclear, leading to inconsistent application
- If there are changes, they should be applied and reviewed again (prevents loop principle violation)

**Alternative approach**:
- If there are changes → Select "🔄 Needs Iteration"
- After applying changes → Review again (new iteration)
- Repeat until ZERO issues → Then "✅ Approve"

---

### Review Recommendation Format

Use this exact format in your review:

```markdown
## Executive Summary
- **Overall Assessment**: [Strong / Good / Needs Improvement / Major Concerns]
- **Recommendation**: [Approve / Needs Iteration]
- **Loop Decision**: [✅ Exit Loop / 🔄 Continue Loop]

## Summary
[Brief summary of assessment]

**If Needs Iteration:**
- 🔴 Required Changes: [count]
- 🟡 Suggested Improvements: [count]
- Total Issues: [count]
```

---

**Remember**: The goal is to ensure the plan is production-ready, not to rush to approval. The iterative loop exists to systematically eliminate ALL issues before execution.
