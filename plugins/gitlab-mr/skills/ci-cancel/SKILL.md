---
name: ci-cancel
description: Cancel running GitLab CI/CD pipelines or specific jobs. Supports single job cancel or entire pipeline cancellation. Korean triggers: CI 중지, 파이프라인 취소, job 취소, CI 멈춰, 파이프라인 중지, 빌드 취소, CI 취소.
user-invocable: true
---

# CI Cancel

## Overview

Cancels running CI/CD pipelines or specific jobs.

**Key Features**:
- **Single Job Cancel**: Stop specific running job
- **Pipeline Cancel**: Cancel entire pipeline
- **Batch Cancel**: Stop all running jobs
- **Confirmation**: Verify before canceling

---

## When to Use

**Use this skill when:**
- Wrong code was pushed and pipeline should stop
- Need to free up CI runners
- Pipeline is stuck or hanging
- Want to cancel before retrying with fixes

**Do NOT use when:**
- Pipeline already completed (nothing to cancel)
- Job is manual and not started (use `ci-trigger` to start)
- Want to check status only (use `ci-status`)

---

## Workflow

### Phase 0: Identify Running Jobs

**0-1. Check Pipeline Status**

```bash
# Get current pipeline status
glab ci status
```

**0-2. List Running Jobs**

```bash
# Find running jobs
glab ci get --output json | jq '.jobs[] | select(.status == "running" or .status == "pending") | {id, name, stage, status}'
```

Output example:
```json
{"id": 789, "name": "unit-tests", "stage": "test", "status": "running"}
{"id": 790, "name": "lint", "stage": "build", "status": "pending"}
```

---

### Phase 1: Cancel Execution

**Option A: Cancel Specific Job**

```bash
# Cancel specific job
glab ci cancel job <job-id>
```

**Option B: Cancel Entire Pipeline**

```bash
# Cancel current pipeline
glab ci cancel pipeline
```

**Option C: Cancel via API (more control)**

```bash
# Get pipeline ID
PIPELINE_ID=$(glab ci get --output json | jq -r '.id')

# Cancel pipeline via API
glab api --method POST "projects/:fullpath/pipelines/$PIPELINE_ID/cancel"
```

**Option D: Cancel Specific Job via API**

```bash
# Cancel job via API
glab api --method POST "projects/:fullpath/jobs/<job-id>/cancel"
```

---

### Phase 2: Verify Cancellation

**2-1. Check Status**

```bash
# Verify cancellation
glab ci status
```

**2-2. Confirm Job Status**

```bash
# Check job is now canceled
glab ci get --output json | jq '.jobs[] | select(.id == <job-id>) | {name, status}'
```

---

### Phase 3: Report Results

**3-1. Single Job Cancel Result**

```markdown
## CI Job Canceled

**Job**: unit-tests (ID: 789)
**Previous Status**: running
**Current Status**: canceled

### Result

Job successfully canceled.

### Next Steps

1. Fix the issue in your code
2. Push changes: `git push`
3. Or retry: use `ci-retry`
```

**3-2. Pipeline Cancel Result**

```markdown
## Pipeline Canceled

**Pipeline ID**: #12345
**Branch**: feature/my-feature
**Previous Status**: running

### Canceled Jobs

| Job ID | Name | Stage | Was |
|--------|------|-------|-----|
| 789 | unit-tests | test | running |
| 790 | lint | build | pending |
| 791 | e2e-tests | test | pending |

**Total**: 3 jobs canceled

### Next Steps

1. Fix the issue
2. Push changes or trigger new pipeline
3. Use `ci-trigger` to start fresh pipeline
```

---

## glab CLI Reference

### Cancel Job

```bash
# Cancel specific job
glab ci cancel job <job-id>

# Via API
glab api --method POST "projects/:fullpath/jobs/<job-id>/cancel"
```

### Cancel Pipeline

```bash
# Cancel current pipeline
glab ci cancel pipeline

# Via API
PIPELINE_ID=$(glab ci get --output json | jq -r '.id')
glab api --method POST "projects/:fullpath/pipelines/$PIPELINE_ID/cancel"
```

### List Running Jobs

```bash
# Find jobs to cancel
glab ci get --output json | jq '.jobs[] | select(.status == "running" or .status == "pending")'
```

---

## Error Handling

### No Running Pipeline

```markdown
No running pipeline to cancel.

**Current Status**: success (completed)

Nothing to cancel.
```

### Job Already Finished

```markdown
Cannot cancel: job already finished.

**Job**: unit-tests
**Status**: success
**Finished**: 5 minutes ago

Job completed before cancel request.
```

### Permission Denied

```markdown
Permission denied to cancel this pipeline.

**Pipeline ID**: #12345
**Required Permission**: Developer or higher

**Troubleshooting**:
1. Check your project role
2. Contact project maintainer
3. Request Developer access
```

### Pipeline Already Canceled

```markdown
Pipeline already canceled.

**Pipeline ID**: #12345
**Status**: canceled
**Canceled At**: 2024-01-05 10:25:00

No action needed.
```

---

## Best Practices

### When to Cancel

1. **Wrong Code Pushed**: Realized mistake after push
2. **Unnecessary Run**: Pipeline triggered by accident
3. **Resource Conflict**: Need runners for higher priority job
4. **Hanging Jobs**: Job stuck without progress

### Before Canceling

1. **Confirm Intent**: Make sure you want to stop
2. **Check Dependencies**: Other jobs may depend on this
3. **Notify Team**: Let team know if shared pipeline

### After Canceling

1. **Fix Issues**: Address the root cause
2. **Push Fixes**: If code changes needed
3. **Retry/Trigger**: Start new pipeline when ready

---

## Integration

### Cancel and Retry Workflow

```
1. ci-status     → Check running jobs
2. ci-cancel     → Cancel problematic pipeline
3. Fix code      → Make necessary changes
4. git push      → Push fixes
5. ci-status     → Verify new pipeline started
```

### Related Skills

- **ci-status**: Check pipeline and job status
- **ci-retry**: Retry after cancel and fix
- **ci-trigger**: Start new pipeline after cancel
