# Task Plan Template

Use this template when creating `[FEATURE]_PLAN.md` files.

---

# Task Plan: [Feature/Fix Name]

**Date**: [YYYY-MM-DD]
**Type**: Feature / Bug Fix / Refactoring / Research
**Priority**: P[0-3]
**Related**: [JIRA-123], [GitHub Issue #456], [Sentry Issue]
**Based On**: [REPORT_FILE.md] (if from analyze)

## Overview

### Objective
[Clear statement of what needs to be achieved. Be specific and measurable.]

### Context
[Brief background explaining why this is needed. Reference analysis reports, JIRA issues, or user requirements.]

### Success Criteria
1. [Measurable outcome 1]
2. [Measurable outcome 2]
3. [Measurable outcome 3]

### Constraints
- **Timeline**: [Expected completion timeframe]
- **Resources**: [Team members, tools, access required]
- **Technical**: [Technology stack, compatibility requirements]
- **Business**: [Budget, regulatory, compliance considerations]

---

## Task Breakdown

### Task 1: [Task Name] - P[0-3] | [S/M/L]

**Goal**: [Clear, specific outcome for this task]

**Success Criteria**:
- [ ] [Measurable criteria 1]
- [ ] [Measurable criteria 2]
- [ ] [Measurable criteria 3]

**Dependencies**:
- [Task ID or "None"]
- [External dependency if any]

**Tools & Resources**:
- **MCP Servers**: [serena, atlassian, github, etc.]
- **Tools**: [Read, Edit, Bash, etc.]
- **Documentation**: [Links to relevant docs]

**Implementation Approach**:
1. [Step 1]: [What to do]
2. [Step 2]: [What to do]
3. [Step 3]: [What to do]

**Risks & Mitigation**:
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk description] | H/M/L | H/M/L | [How to mitigate] |

**Testing Strategy**: [CRITICAL - Required for every task]
- **Test Type**: Unit / Integration / Manual / E2E
- **Test Cases**:
  1. [Specific test scenario 1]
     - **Given**: [Initial state]
     - **When**: [Action performed]
     - **Then**: [Expected result]
  2. [Specific test scenario 2]
     - **Given**: [Initial state]
     - **When**: [Action performed]
     - **Then**: [Expected result]
  3. [Edge case scenario]
     - **Given**: [Initial state]
     - **When**: [Action performed]
     - **Then**: [Expected result]
- **Acceptance Criteria**:
  - [ ] [Measurable pass condition 1]
  - [ ] [Measurable pass condition 2]
  - [ ] [Code coverage threshold if applicable]
- **Test Commands**:
  ```bash
  # Commands to run the tests
  npm test src/path/to/test.spec.ts
  # or
  pytest tests/test_feature.py -v
  ```

**Expected Duration**: [Time estimate with buffer]

---

### Task 2: [Task Name] - P[0-3] | [S/M/L]

[Repeat same structure as Task 1]

---

[Continue for all tasks...]

---

## Dependencies & Critical Path

### Dependency Diagram

```
[Task 1] ──┐
           ├──> [Task 3] ──> [Task 5]  ← Critical Path
[Task 2] ──┘                ↗
                   [Task 4]
```

### Critical Path Tasks
1. [Task ID]: [Task name] - [Duration]
2. [Task ID]: [Task name] - [Duration]
3. [Task ID]: [Task name] - [Duration]

**Total Critical Path Duration**: [Sum of durations]

### Parallel Opportunities
- [Tasks X and Y] can be executed in parallel
- [Tasks A and B] have no dependencies and can run concurrently

---

## Risk Matrix

| Risk ID | Description | Likelihood | Impact | Priority | Mitigation | Owner |
|---------|-------------|------------|--------|----------|------------|-------|
| R1 | [Risk description] | High/Medium/Low | High/Medium/Low | P0-P3 | [Mitigation strategy] | [Team/Person] |
| R2 | [Risk description] | High/Medium/Low | High/Medium/Low | P0-P3 | [Mitigation strategy] | [Team/Person] |

### Risk Categories

**Technical Risks**:
- [Risk 1]: [Description and mitigation]
- [Risk 2]: [Description and mitigation]

**Resource Risks**:
- [Risk 1]: [Description and mitigation]
- [Risk 2]: [Description and mitigation]

**External Risks**:
- [Risk 1]: [Description and mitigation]
- [Risk 2]: [Description and mitigation]

---

## Testing & Quality Assurance

### Testing Strategy Overview
- **Unit Tests**: [Scope and coverage expectations]
- **Integration Tests**: [What integrations to test]
- **E2E Tests**: [User journeys to verify]
- **Manual Tests**: [What requires manual verification]
- **Performance Tests**: [If applicable]
- **Security Tests**: [If applicable]

### Test Coverage Goals
- **Overall Coverage**: [Target percentage]
- **Critical Paths**: [Higher coverage requirement]
- **New Code**: [Coverage requirement for new code]

### Testing Timeline
1. **Phase 1**: [Which tests when]
2. **Phase 2**: [Which tests when]
3. **Phase 3**: [Which tests when]

---

## Deployment & Rollout

### Deployment Strategy
- **Environment Sequence**: Dev → Staging → Production
- **Deployment Method**: [Blue-green / Rolling / Canary / etc.]
- **Feature Flags**: [If applicable, which flags and strategy]

### Rollout Plan
1. **Phase 1**: [What gets deployed to which users]
2. **Phase 2**: [Gradual expansion]
3. **Phase 3**: [Full rollout]

### Monitoring & Observability
- **Metrics to Track**:
  - [Metric 1]: [What to measure and threshold]
  - [Metric 2]: [What to measure and threshold]
- **Alerts**:
  - [Alert 1]: [Condition and action]
  - [Alert 2]: [Condition and action]
- **Dashboards**: [What to monitor in real-time]

### Rollback Procedure
1. **Trigger Conditions**: [When to rollback]
2. **Rollback Steps**:
   - Step 1: [Action]
   - Step 2: [Action]
   - Step 3: [Action]
3. **Verification**: [How to confirm rollback success]
4. **Communication**: [Who to notify]

---

## Documentation & Communication

### Documentation Updates Required
- [ ] **API Documentation**: [Which APIs/endpoints]
- [ ] **User Documentation**: [What user-facing docs]
- [ ] **Developer Documentation**: [Internal technical docs]
- [ ] **Architecture Decision Records**: [ADRs to create]
- [ ] **Runbooks**: [Operational procedures]

### Communication Plan
- **Stakeholders**: [Who needs to be informed]
- **Updates**: [How often and through which channels]
- **Milestones**: [Which milestones require notification]
- **Completion**: [How to announce completion]

---

## Post-Implementation

### Success Metrics
- **KPI 1**: [Metric name] - Target: [Value]
- **KPI 2**: [Metric name] - Target: [Value]
- **KPI 3**: [Metric name] - Target: [Value]

### Validation Period
- **Duration**: [How long to monitor]
- **Checkpoints**: [When to review metrics]
- **Success Criteria**: [What defines success]

### Lessons Learned
[To be filled after implementation]
- What went well:
- What could be improved:
- Recommendations for future:

---

## Execution Notes

### Before Starting
- [ ] All dependencies are available
- [ ] Required tools and access verified
- [ ] Team members briefed
- [ ] Backup/rollback plan confirmed

### During Execution
- Use `TodoWrite` to track task progress
- Mark tasks as in_progress/completed systematically
- Update JIRA with `mcp__plugin_workflow-skills_atlassian__jira_update_issue`
- Document learnings with `mcp__plugin_workflow-skills_serena__write_memory`

### After Completion
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Stakeholders notified
- [ ] Monitoring in place
- [ ] Post-mortem scheduled (if applicable)

---

## Appendix

### References
- [Link to analysis report]
- [Link to JIRA issue]
- [Link to design docs]
- [Link to relevant ADRs]

### Glossary
- **Term 1**: Definition
- **Term 2**: Definition

---

**Plan Created**: [Timestamp]
**Plan Approved**: [Timestamp after review approval]
**Approved By**: [Review process iteration count]
**Ready for Execution**: [Yes/No]
