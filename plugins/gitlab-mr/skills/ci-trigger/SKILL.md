---
name: ci-trigger
description: Trigger GitLab CI/CD manual jobs or start new pipelines. Supports manual job execution and pipeline creation on current branch. Korean triggers: CI 실행, 파이프라인 실행, job 트리거, 수동 실행, 파이프라인 시작, CI 돌려, 배포 실행.
user-invocable: true
---

# CI Trigger

## Overview

Triggers manual CI/CD jobs or starts new pipelines on the current branch.

**Key Features**:
- **Manual Job Trigger**: Execute manual/blocked jobs
- **New Pipeline**: Start fresh pipeline on current branch
- **Job Selection**: Choose specific manual jobs to run
- **Status Tracking**: Monitor triggered job progress

---

## When to Use

**Use this skill when:**
- Need to trigger a manual deployment job
- Want to start a new pipeline without pushing
- Have manual approval/gate jobs to execute
- Need to run a specific stage manually

**Do NOT use when:**
- Jobs are already running (use `ci-status` to check)
- Need to retry failed jobs (use `ci-retry`)
- Want to cancel running jobs (use `ci-cancel`)

---

## Workflow

### Phase 0: Identify Manual Jobs

**0-1. Get Current Pipeline**

```bash
# Check current pipeline
glab ci status
```

**0-2. List Manual Jobs**

```bash
# Find manual jobs
glab ci get --output json | jq '.jobs[] | select(.status == "manual") | {id, name, stage}'
```

Output example:
```json
{"id": 456, "name": "deploy-staging", "stage": "deploy"}
{"id": 457, "name": "deploy-production", "stage": "deploy"}
```

---

### Phase 1: Trigger Execution

**Option A: Trigger Manual Job**

```bash
# Trigger specific manual job
glab ci trigger <job-id>
```

**Option B: Start New Pipeline**

```bash
# Run new pipeline on current branch
glab ci run
```

**Option C: Run Pipeline on Specific Branch**

```bash
# Run pipeline on specific branch/tag
glab ci run --branch <branch-name>
```

---

### Phase 2: Monitor Progress

**2-1. Check Trigger Status**

```bash
# View pipeline status
glab ci status

# Or detailed view
glab ci view
```

**2-2. Trace Job Log (optional)**

```bash
# Watch job execution in real-time
glab ci trace <job-id>
```

---

### Phase 3: Report Results

**3-1. Manual Job Trigger Result**

```markdown
## Manual Job Triggered

**Job**: deploy-staging (ID: 456)
**Stage**: deploy
**Previous Status**: manual

### Execution

Job triggered successfully.

**Current Status**: running
**Started At**: 2024-01-05 10:30:00

### Monitoring

Track progress:
```bash
glab ci trace 456
```

Or view in browser:
https://gitlab.example.com/.../jobs/456
```

**3-2. New Pipeline Result**

```markdown
## New Pipeline Started

**Branch**: feature/my-feature
**Pipeline ID**: #12346
**Status**: pending

### Pipeline Info

| Field | Value |
|-------|-------|
| Created | 2024-01-05 10:30:00 |
| Source | manual trigger |
| Stages | build, test, deploy |

### Monitoring

Check status:
```bash
glab ci status
```

View in browser:
https://gitlab.example.com/.../pipelines/12346
```

---

## glab CLI Reference

### Trigger Manual Job

```bash
# Trigger by job ID
glab ci trigger <job-id>

# Find manual job IDs
glab ci get --output json | jq '.jobs[] | select(.status == "manual")'
```

### Run New Pipeline

```bash
# Run on current branch
glab ci run

# Run on specific branch
glab ci run --branch main

# Run on tag
glab ci run --branch v1.0.0
```

### View Pipeline/Job

```bash
# View pipeline
glab ci view

# View specific job
glab ci view <job-id>
```

---

## Error Handling

### No Manual Jobs Available

```markdown
No manual jobs found in current pipeline.

**Current Pipeline Status**: success

**Possible Actions**:
1. Check if pipeline has manual jobs: review `.gitlab-ci.yml`
2. Start new pipeline: `glab ci run`
```

### Job Already Running

```markdown
Cannot trigger: job is already running.

**Job**: deploy-staging
**Status**: running
**Started**: 5 minutes ago

**Options**:
1. Wait for completion
2. Cancel with `ci-cancel` if needed
```

### No Pipeline Exists

```markdown
No pipeline found for current branch.

**Branch**: feature/new-feature

**Action**: Starting new pipeline...
```bash
glab ci run
```
```

### Permission Denied

```markdown
Permission denied to trigger this job.

**Job**: deploy-production
**Required Role**: Maintainer or higher

**Troubleshooting**:
1. Check your project role
2. Contact project maintainer
3. Request elevated permissions
```

---

## Manual Job Types

### Common Manual Jobs

| Job Type | Purpose | Typical Stage |
|----------|---------|---------------|
| deploy-staging | Deploy to staging env | deploy |
| deploy-production | Deploy to prod | deploy |
| manual-approval | Gate/approval step | deploy |
| cleanup | Resource cleanup | cleanup |
| rollback | Rollback deployment | deploy |

### Identifying Manual Jobs

In `.gitlab-ci.yml`:
```yaml
deploy-production:
  stage: deploy
  script:
    - ./deploy.sh production
  when: manual  # This makes it a manual job
  only:
    - main
```

---

## Best Practices

### Before Triggering

1. **Check Prerequisites**: Ensure previous stages passed
2. **Verify Environment**: Confirm target environment is ready
3. **Review Changes**: Know what will be deployed

### For Production Deployments

1. **Verify Branch**: Confirm you're on the correct branch
2. **Check Tests**: All tests should pass
3. **Notify Team**: Inform team before production deploy
4. **Monitor**: Watch the deployment logs

---

## Integration

### Deployment Workflow

```
1. ci-status     → Verify all tests passed
2. ci-trigger    → Trigger deploy-staging
3. ci-status     → Verify staging success
4. Manual QA     → Test on staging
5. ci-trigger    → Trigger deploy-production
6. ci-status     → Verify production success
```

### Related Skills

- **ci-status**: Check pipeline and job status
- **ci-retry**: Retry failed jobs
- **ci-cancel**: Cancel running jobs
