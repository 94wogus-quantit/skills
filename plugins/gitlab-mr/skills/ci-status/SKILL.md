---
name: ci-status
description: Check GitLab CI/CD pipeline status for current branch. Shows pipeline list, job status, and analyzes error logs with root cause analysis using sequential-thinking. Korean triggers: CI 상태, 파이프라인 상태, CI 확인, 파이프라인 에러, job 실패, CI 로그, 파이프라인 확인, 빌드 상태.
user-invocable: true
---

# CI Status

## Overview

Provides comprehensive CI/CD pipeline status for the current branch with **error log analysis**.

**Key Features**:
- **Pipeline Status**: View current/recent pipeline status
- **Job Details**: List all jobs with their status
- **Error Log Retrieval**: Fetch failed job logs
- **Root Cause Analysis**: Analyze errors using sequential-thinking

---

## When to Use

**Use this skill when:**
- Checking if CI is passing on current branch
- Investigating why a pipeline failed
- Viewing job logs for debugging
- Understanding error patterns

**Do NOT use when:**
- Need to retry/rerun jobs (use `ci-retry`)
- Need to trigger manual jobs (use `ci-trigger`)
- Need to cancel running jobs (use `ci-cancel`)

---

## Workflow

### Phase 0: Detect Current Branch

**0-1. Get Current Branch**

```bash
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"
```

**0-2. Verify GitLab Remote**

```bash
# Check if glab is configured
glab auth status
```

---

### Phase 1: Pipeline Overview

**1-1. Get Pipeline Status**

```bash
# Quick status check
glab ci status
```

**1-2. List Recent Pipelines**

```bash
# List recent pipelines (default: current branch)
glab ci list

# With more details
glab ci list --per-page 5
```

**1-3. Get Pipeline JSON (for detailed info)**

```bash
# Get current pipeline as JSON
glab ci get --output json
```

Extract from JSON:
- `id`: Pipeline ID
- `status`: running, success, failed, canceled, pending
- `created_at`: When pipeline started
- `web_url`: Link to GitLab UI

---

### Phase 2: Job Status Analysis

**2-1. View Pipeline with Jobs**

```bash
# Interactive view with all jobs
glab ci view
```

**2-2. Parse Job Status**

From `glab ci get --output json`, extract jobs:
- Job name
- Stage
- Status (success, failed, running, pending, manual, skipped)
- Duration

**2-3. Identify Failed Jobs**

```bash
# Get pipeline JSON and filter failed jobs
glab ci get --output json | jq '.jobs[] | select(.status == "failed") | {id, name, stage, status}'
```

---

### Phase 3: Error Log Analysis

**3-1. Fetch Failed Job Logs**

```bash
# Trace job log (replace <job-id> with actual ID)
glab ci trace <job-id>
```

**3-2. Analyze Error with Sequential Thinking**

```typescript
mcp__plugin_sequential-thinking_sequential-thinking__sequentialthinking({
  thought: "Analyzing CI failure: What is the error message? What type of failure is this (build, test, lint, deploy)?",
  thoughtNumber: 1,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

Continue analysis:

```typescript
mcp__plugin_sequential-thinking_sequential-thinking__sequentialthinking({
  thought: "Root cause identification: Based on the error log, what is the underlying cause? Is it a code issue, dependency issue, or infrastructure issue?",
  thoughtNumber: 2,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

```typescript
mcp__plugin_sequential-thinking_sequential-thinking__sequentialthinking({
  thought: "Solution recommendation: What are the possible fixes? Which fix is most likely to resolve the issue?",
  thoughtNumber: 3,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

---

### Phase 4: Report Results

**4-1. Status Summary**

```markdown
## CI/CD Pipeline Status

**Branch**: feature/my-feature
**Pipeline ID**: #12345
**Status**: failed
**URL**: https://gitlab.example.com/group/project/-/pipelines/12345

### Jobs Overview

| Stage | Job | Status | Duration |
|-------|-----|--------|----------|
| build | compile | success | 2m 15s |
| test | unit-tests | failed | 1m 30s |
| test | integration | skipped | - |
| deploy | staging | skipped | - |

### Failed Job: unit-tests

**Error Summary**:
```
FAILED: src/api/user.test.ts
  - UserService.create should validate email
    Expected: valid@email.com
    Received: undefined
```

### Root Cause Analysis

1. **Error Type**: Test failure
2. **Root Cause**: `UserService.create` returns undefined instead of user object
3. **Affected File**: `src/services/user.service.ts`
4. **Suggested Fix**: Check return statement in create method

### Next Steps

1. Fix the failing test in `src/services/user.service.ts`
2. Run `ci-retry` to rerun the pipeline
```

**4-2. Quick Status (when all passing)**

```markdown
## CI/CD Pipeline Status

**Branch**: feature/my-feature
**Pipeline ID**: #12345
**Status**: success

All 5 jobs passed successfully.

| Stage | Jobs | Status |
|-------|------|--------|
| build | 1/1 | passed |
| test | 2/2 | passed |
| deploy | 2/2 | passed |
```

---

## glab CLI Reference

### Pipeline Status

```bash
# Quick status
glab ci status

# Detailed view
glab ci view

# JSON output
glab ci get --output json
```

### Pipeline List

```bash
# List pipelines
glab ci list

# Filter by status
glab ci list --status failed
glab ci list --status running
```

### Job Logs

```bash
# Trace job log
glab ci trace <job-id>

# View specific job
glab ci view <job-id>
```

---

## Error Handling

### No Pipeline Found

```markdown
No pipeline found for current branch.

**Possible Causes**:
1. No commits pushed yet
2. CI not configured for this branch
3. Pipeline not triggered

**Next Steps**:
1. Push commits: `git push`
2. Check `.gitlab-ci.yml` configuration
3. Manually trigger: use `ci-trigger`
```

### glab Auth Error

```markdown
GitLab authentication failed.

**Troubleshooting**:
1. Check auth status: `glab auth status`
2. Re-authenticate: `glab auth login`
3. Verify remote URL: `git remote -v`
```

---

## Integration

### Workflow with Other Skills

```
1. ci-status     → Check pipeline status
2. (If failed)   → Analyze error logs
3. Fix code      → Based on analysis
4. ci-retry      → Rerun failed jobs
5. ci-status     → Verify fix
```

### Related Skills

- **ci-retry**: Retry failed jobs
- **ci-trigger**: Trigger manual jobs or new pipeline
- **ci-cancel**: Cancel running pipeline
