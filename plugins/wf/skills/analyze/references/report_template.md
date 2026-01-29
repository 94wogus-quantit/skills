# Issue Analysis Report Template

Use this template when creating `[ISSUE_ID]_REPORT.md` files.

---

# Issue Analysis: [Issue Title/ID]

**Date**: [YYYY-MM-DD]
**Analyzer**: Claude Code
**Issue ID**: [JIRA-123 or descriptive name]
**Severity**: [Critical / High / Medium / Low]

## Summary

[One-paragraph executive summary explaining:
- What the issue is
- What causes it
- What the impact is
- High-level solution approach]

---

## Context

### JIRA Issue
- **Link**: [Issue URL]
- **Reporter**: [Name]
- **Affected Version**: [Version]
- **Environment**: [Production / Staging / Development]
- **Key Details**: [Important information from description]

### Sentry Error (if applicable)
- **Error Link**: [Sentry URL]
- **First Seen**: [Date/Time]
- **Last Seen**: [Date/Time]
- **Frequency**: [Count / Rate]
- **Affected Users**: [Count or percentage]
- **Error Message**:
  ```
  [Actual error message]
  ```

### Additional Context
- **User Reports**: [Summary of user-reported symptoms]
- **Reproduction Steps**: [If available]
- **Related Files**: [Any files user provided]
- **Screenshots/Logs**: [References to attachments]

---

## Investigation Process

### Hypotheses Considered

**Hypothesis 1: [Description]**
- **Likelihood**: High / Medium / Low
- **Evidence For**: [Supporting observations]
- **Evidence Against**: [Contradicting observations]
- **Conclusion**: ✅ Confirmed / ❌ Eliminated / ⚠️ Partial

**Hypothesis 2: [Description]**
- **Likelihood**: High / Medium / Low
- **Evidence For**: [Supporting observations]
- **Evidence Against**: [Contradicting observations]
- **Conclusion**: ✅ Confirmed / ❌ Eliminated / ⚠️ Partial

[Continue for each hypothesis...]

### Investigation Steps Taken

1. **Step 1**: [What was investigated]
   - Tool used: [Serena / Sentry / JIRA / etc.]
   - Findings: [What was discovered]

2. **Step 2**: [What was investigated]
   - Tool used: [Tool name]
   - Findings: [What was discovered]

[Continue for each step...]

---

## Root Cause

### Primary Root Cause

**Location**: [`file_path.ts:123`](path/to/file.ts#L123)

**Code Snippet**:
```typescript
// Problematic code
function problematicFunction() {
  // Line 123: Issue occurs here
  const result = nullableValue.property; // No null check
  return result;
}
```

**Explanation**:

[Detailed technical explanation of WHY the issue occurs. Include:
- The specific code pattern causing the problem
- Why this pattern is problematic
- What happens at runtime when the issue manifests
- Any relevant language/framework behavior]

**Trigger Conditions**:

The issue occurs when:
1. [Specific condition 1]
2. [Specific condition 2]
3. [Specific condition 3]

Example scenario:
```
User action: [What the user does]
↓
Component: [Component A processes]
↓
Component: [Component B receives null]  ← Issue occurs here
↓
Result: [Error is thrown]
```

### Contributing Factors

**Factor 1: [Description]**
- **Location**: [`file.ts:45`](path/to/file.ts#L45)
- **Impact**: [How this exacerbates the problem]
- **Recommendation**: [How to address]

**Factor 2: [Description]**
- **Location**: [`file.ts:89`](path/to/file.ts#L89)
- **Impact**: [How this exacerbates the problem]
- **Recommendation**: [How to address]

### Impact Assessment

**Affected Scope**:
- **Users**: [All users / Specific cohort / Percentage]
- **Frequency**: [Every time / Sometimes / Rarely]
- **Reproducibility**: [Always / Often / Occasionally / Hard to reproduce]

**Business Impact**:
- **User Experience**: [Degraded / Broken / Unusable]
- **Data Integrity**: [At risk / Safe]
- **Performance**: [Degraded / Normal]
- **Security**: [Vulnerable / Secure]

**Risk Level**: [Critical / High / Medium / Low]

---

## Recommendations

### Immediate Actions (Hotfix)

**Priority**: P0 (Deploy within 24-48 hours)

```typescript
// Quick fix to mitigate the issue
function problematicFunction() {
  // Add null check
  if (!nullableValue) {
    return defaultValue; // Safe fallback
  }
  const result = nullableValue.property;
  return result;
}
```

**Deployment Strategy**:
1. [Step to deploy hotfix]
2. [Verification step]
3. [Rollback plan if needed]

**Monitoring**:
- Add Sentry alert for [specific error]
- Monitor [specific metric] for [time period]

### Long-term Solution

**Priority**: P1 (Implement in next sprint)

**Approach**: [High-level description of proper fix]

**Implementation Details**:

1. **Refactor Component A** ([`file_a.ts`](path/to/file_a.ts))
   ```typescript
   // Proper validation at source
   function getValueSafely(): ValueType | null {
     if (!isValid(source)) {
       logger.warn('Invalid source detected');
       return null;
     }
     return source.value;
   }
   ```

2. **Update Component B** ([`file_b.ts`](path/to/file_b.ts))
   ```typescript
   // Handle null case gracefully
   function processValue(value: ValueType | null) {
     if (!value) {
       return handleMissingValue();
     }
     // Process valid value
   }
   ```

3. **Add Type Safety** ([`types.ts`](path/to/types.ts))
   ```typescript
   // Make nullability explicit in types
   type ProcessResult = {
     value: ValueType | null;
     error?: Error;
   }
   ```

**Edge Cases to Handle**:
- [ ] Case 1: [Description and how to handle]
- [ ] Case 2: [Description and how to handle]
- [ ] Case 3: [Description and how to handle]

### Testing Strategy

**Unit Tests**:
```typescript
// test/unit/problematic-function.test.ts
describe('problematicFunction', () => {
  it('should handle null values gracefully', () => {
    const result = problematicFunction(null);
    expect(result).toBe(defaultValue);
  });

  it('should process valid values correctly', () => {
    const result = problematicFunction(validValue);
    expect(result).toBe(expectedResult);
  });

  it('should throw on invalid input', () => {
    expect(() => problematicFunction(invalidValue))
      .toThrow(ValidationError);
  });
});
```

**Integration Tests**:
```typescript
// test/integration/user-flow.test.ts
describe('User Flow', () => {
  it('should complete flow when data is missing', async () => {
    // Simulate scenario that triggers the issue
    const response = await triggerProblemScenario();
    expect(response.status).toBe(200);
    expect(response.error).toBeNull();
  });
});
```

**Manual Testing Checklist**:
- [ ] Test with missing data
- [ ] Test with invalid data
- [ ] Test with edge case values
- [ ] Test error handling and recovery
- [ ] Verify logging and monitoring

### Prevention

**Code Review Checklist**:
- [ ] Add to `.github/PULL_REQUEST_TEMPLATE.md`:
  - "Does this code handle null/undefined values?"
  - "Are there appropriate guards for edge cases?"

**Linting Rules**:
```json
// .eslintrc.json
{
  "rules": {
    "@typescript-strict-null-checks": "error",
    "no-unsafe-optional-chaining": "error"
  }
}
```

**Documentation Updates**:
- [ ] Update API documentation for affected functions
- [ ] Add architecture decision record (ADR) for null handling pattern
- [ ] Update developer guide with null safety best practices

**Monitoring**:
- [ ] Add Sentry alert for similar error patterns
- [ ] Set up dashboard for tracking null-related errors
- [ ] Create runbook for investigating similar issues

### Related Areas to Review

**Similar Patterns**:
1. [`file1.ts:45`](path/to/file1.ts#L45) - Similar null handling pattern
   - **Risk**: Medium
   - **Action**: Refactor to use safe access pattern
   - **Priority**: P2

2. [`file2.ts:89`](path/to/file2.ts#L89) - Shared utility function
   - **Risk**: High
   - **Action**: Add null checks and update all callers
   - **Priority**: P1

**Upstream Dependencies**:
- [`data-provider.ts`](path/to/data-provider.ts) - Should guarantee non-null or document nullability
- [`api-client.ts`](path/to/api-client.ts) - Review error handling for failed requests

**Downstream Dependencies**:
- [`consumer-a.ts`](path/to/consumer-a.ts) - May have same vulnerability
- [`consumer-b.ts`](path/to/consumer-b.ts) - Already has proper null checks ✅

---

## Appendix

### Stack Trace
```
[Full stack trace from Sentry if applicable]
```

### Related Issues
- [ISSUE-456] - Similar null pointer issue in different component
- [ISSUE-789] - Related data validation problem

### References
- [Link to relevant documentation]
- [Link to similar resolved issues]
- [Link to architectural decisions]

---

**Report Generated**: [Timestamp]
**Tools Used**: Serena, Sentry, JIRA, Sequential Thinking
**Next Steps**: Create implementation plan with `plan` skill using this report
