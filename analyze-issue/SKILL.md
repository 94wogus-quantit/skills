---
name: analyze-issue
description: Systematically analyze the root cause of bugs and issues using multi-perspective investigation. Use this skill when analyzing JIRA issues, Sentry errors, or investigating bug reports to identify root causes and provide actionable remediation recommendations. Generates detailed analysis reports with code locations, reproduction steps, and fix recommendations.
---

# Analyze Issue Root Cause

## ⚠️ CRITICAL LANGUAGE POLICY

**DEFAULT LANGUAGE: KOREAN (한국어)**

ALL outputs, documentation, reports, and communications MUST be in **KOREAN** unless explicitly requested otherwise by the user.

- ✅ **Report files**: Write in Korean
- ✅ **Analysis**: Perform in Korean
- ✅ **Comments**: Write in Korean
- ✅ **Explanations**: Provide in Korean
- ✅ **User communication**: Respond in Korean

**Exception**: If the user writes in another language, match that language for responses.

**This is a MANDATORY requirement. Do NOT default to English.**

---

## Overview

Systematically analyze bugs and issues to identify root causes using a structured, multi-perspective approach. This skill combines JIRA/Atlassian integration, Sentry error tracking, codebase investigation with Serena, and sequential thinking to produce comprehensive analysis reports.

**Output**: `[ISSUE_ID]_REPORT.md` file containing root cause analysis, affected code locations, reproduction steps, and remediation recommendations.

## When to Use This Skill

Use this skill when:
- Analyzing JIRA issues or bug reports
- Investigating Sentry errors or production incidents
- User requests "analyze this issue", "what's causing this bug", "investigate [ISSUE-ID]"
- Need systematic root cause analysis before planning a fix
- Debugging complex problems requiring multi-source investigation

## Analysis Workflow

### Phase 1: Context Gathering

Gather comprehensive context from all available sources:

**1. JIRA Issue Analysis** (if JIRA link/ID provided)
- Use `mcp__atlassian__getJiraIssue` to fetch issue details
- Extract:
  - Issue summary and description
  - Reproduction steps
  - Expected vs actual behavior
  - Environment details
  - Attachments and linked resources
  - Comments and discussion threads
- Check for linked issues or sub-tasks

**2. Sentry Error Investigation** (if mentioned)
- Use `mcp__sentry__search_issues` to find related errors
- Use `mcp__sentry__get_issue_details` for specific issue IDs
- Extract:
  - Stack traces and error messages
  - Breadcrumbs and context
  - Affected users and frequency
  - Error patterns and trends

**3. Additional Context**
- Read any file paths or code references provided
- Analyze error logs or screenshots
- Check Confluence documentation if referenced

### Phase 2: Hypothesis Generation

Use `mcp__sequential-thinking__sequentialthinking` to systematically explore multiple perspectives:

**Generate Initial Hypotheses**

Consider various possible root causes:
- Code logic errors (off-by-one, null checks, type mismatches)
- Race conditions or concurrency issues
- Resource leaks or memory problems
- Configuration issues
- Dependency version conflicts
- Environmental differences
- Data quality or edge cases
- Integration issues with external services

**Multi-Perspective Analysis**

For each hypothesis, evaluate:
- **Likelihood**: How probable given the symptoms?
- **Evidence**: What observations support or contradict this?
- **Impact**: How severe would this issue be?
- **Complexity**: How difficult to fix?

**Systematic Elimination**

Use logical reasoning to eliminate unlikely causes:
- Cross-reference with stack traces
- Check timing of deployments vs issue occurrence
- Verify affected components
- Consider scope (all users vs specific conditions)

### Phase 3: Codebase Investigation

Use Serena tools efficiently for targeted code exploration:

**1. Targeted Code Exploration**
- `mcp__serena__get_symbols_overview` - Understand file structure
- `mcp__serena__find_symbol` - Locate specific functions/classes
- `mcp__serena__find_referencing_symbols` - Trace execution flow
- `mcp__serena__search_for_pattern` - Find error messages or patterns

**2. Execution Flow Tracing**
- Map the path from user action to error
- Identify all components in the flow
- Look for conditional branches
- Check error handling and validation logic

**3. Recent Changes Analysis** (if applicable)
- Use GitHub MCP to find recent changes
- Correlate timing with issue occurrence
- Review related code modifications

### Phase 4: Root Cause Determination

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

### Phase 5: Recommendations

Provide actionable recommendations:

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

## Report Generation

Create a comprehensive markdown report using the template in `references/report_template.md`:

### Report Structure

```markdown
# Issue Analysis: [Issue Title/ID]

## Summary
[One-paragraph executive summary]

## Context
- JIRA: [link and key details]
- Sentry: [error details if applicable]
- Additional files: [user-provided context]

## Investigation Process
[Summary of hypotheses considered and eliminated]

## Root Cause
**Location**: [file.ts:123](file.ts#L123)
**Explanation**: [Why this happens]
**Trigger**: [What causes it]

## Recommendations

### Immediate Fix
[Specific code changes or workarounds]

### Long-term Solution
[Architectural or design improvements]

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
/analyze-issue [JIRA]
  → Creates: [ISSUE_ID]_REPORT.md
  → Next: /plan [REPORT]
  → Next: /execute-plan [PLAN]
  → Next: /document
```

The generated report becomes input for the `/plan` command to create an implementation plan.

## Resources

### references/

This skill includes reference materials to support the analysis process:

- `report_template.md` - Detailed template for analysis reports
- `common_bug_patterns.md` - Catalog of frequently encountered bug patterns and their characteristics

These references can be loaded into context when needed for comprehensive analysis.
