---
name: ci-retry
description: Retry failed GitLab CI/CD jobs or entire pipeline. Supports single job retry or batch retry of all failed jobs. Korean triggers: CI 재실행, 파이프라인 재시도, job 재실행, 다시 돌려, 재시도, 파이프라인 다시, 실패한 job 재실행.
---

# CI Retry

## Overview

Retries failed CI/CD jobs or pipelines with **single or batch processing** support.

**Key Features**:
- **Single Job Retry**: Retry specific failed job
- **Batch Retry**: Retry all failed jobs at once
- **Status Monitoring**: Track retry progress
- **Result Reporting**: Summary of retry outcomes

---

## When to Use

**Use this skill when:**
- A job failed due to transient issues (network, timing)
- After fixing code that caused CI failure
- Need to rerun flaky tests
- Want to retry all failed jobs in one command

**Do NOT use when:**
- Pipeline is still running (use `ci-cancel` first)
- Need to trigger manual jobs (use `ci-trigger`)
- Want to check status only (use `ci-status`)

---

## Workflow

### Phase 0: Identify Failed Jobs

**0-1. Get Current Pipeline**

```bash
# Get pipeline status
glab ci status
```

**0-2. List Failed Jobs**

```bash
# Get pipeline JSON and extract failed jobs
glab ci get --output json | jq '.jobs[] | select(.status == "failed") | {id, name, stage}'
```

Output example:
```json
{"id": 123, "name": "unit-tests", "stage": "test"}
{"id": 124, "name": "lint", "stage": "build"}
```

---

### Phase 1: Retry Execution

**Option A: Single Job Retry**

```bash
# Retry specific job by ID
glab ci retry <job-id>
```

**Option B: Retry All Failed Jobs**

```bash
# Get all failed job IDs and retry each
FAILED_JOBS=$(glab ci get --output json | jq -r '.jobs[] | select(.status == "failed") | .id')

for job_id in $FAILED_JOBS; do
  echo "Retrying job: $job_id"
  glab ci retry $job_id
done
```

**Option C: Retry Entire Pipeline**

```bash
# Get pipeline ID
PIPELINE_ID=$(glab ci get --output json | jq -r '.id')

# Retry pipeline via API
glab api --method POST "projects/:fullpath/pipelines/$PIPELINE_ID/retry"
```

---

### Phase 2: Monitor Progress

**2-1. Check Retry Status**

```bash
# Watch pipeline status
glab ci status

# Or view in real-time
glab ci view
```

**2-2. Trace Running Job (optional)**

```bash
# Trace job log in real-time
glab ci trace <job-id>
```

---

### Phase 3: Report Results

**3-1. Single Job Retry Result**

```markdown
## CI Job Retry Result

**Job**: unit-tests (ID: 123)
**Previous Status**: failed
**Action**: Retried

### Status

Retry initiated successfully. Monitoring...

**Current Status**: running
**Pipeline URL**: https://gitlab.example.com/.../pipelines/12345

Use `ci-status` to check the result.
```

**3-2. Batch Retry Result**

```markdown
## CI Batch Retry Result

**Pipeline ID**: #12345
**Branch**: feature/my-feature

### Retried Jobs

| Job ID | Name | Stage | Retry Status |
|--------|------|-------|--------------|
| 123 | unit-tests | test | retried |
| 124 | lint | build | retried |
| 125 | e2e-tests | test | retried |

**Total**: 3 jobs retried

### Monitoring

Pipeline is now running. Check status with:
```bash
glab ci status
```

Or view in browser:
https://gitlab.example.com/.../pipelines/12345
```

---

## glab CLI Reference

### Retry Job

```bash
# Retry by job ID
glab ci retry <job-id>

# Get job ID from pipeline
glab ci get --output json | jq '.jobs[] | {id, name, status}'
```

### Retry Pipeline (via API)

```bash
# Get pipeline ID
PIPELINE_ID=$(glab ci get --output json | jq -r '.id')

# Retry entire pipeline
glab api --method POST "projects/:fullpath/pipelines/$PIPELINE_ID/retry"
```

### Check Status After Retry

```bash
# Quick status
glab ci status

# Detailed view
glab ci view
```

---

## Error Handling

### Job Already Running

```markdown
Cannot retry job: already running.

**Current Status**: running
**Started**: 2 minutes ago

**Options**:
1. Wait for completion
2. Cancel with `ci-cancel` then retry
```

### Job Not Found

```markdown
Job ID not found.

**Troubleshooting**:
1. List available jobs: `glab ci get --output json | jq '.jobs[]'`
2. Check pipeline ID is correct
3. Verify you have access to this project
```

### No Failed Jobs

```markdown
No failed jobs to retry.

**Current Pipeline Status**: success

All jobs passed. No retry needed.
```

---

## Best Practices

### When to Retry

1. **Transient Failures**: Network timeouts, service unavailability
2. **Flaky Tests**: Known intermittent test failures
3. **After Fixes**: Code pushed to fix the issue
4. **Resource Issues**: Runner capacity, memory limits

### When NOT to Retry

1. **Consistent Failures**: Same error every time (fix code first)
2. **Config Issues**: `.gitlab-ci.yml` problems
3. **Dependency Issues**: Missing packages (fix lockfile)

---

## Integration

### Typical Workflow

```
1. ci-status     → Identify failure
2. Analyze logs  → Understand root cause
3. (Optional)    → Fix code and push
4. ci-retry      → Retry failed jobs
5. ci-status     → Verify success
```

### Related Skills

- **ci-status**: Check pipeline and job status
- **ci-trigger**: Trigger new pipeline or manual jobs
- **ci-cancel**: Cancel running jobs before retry
