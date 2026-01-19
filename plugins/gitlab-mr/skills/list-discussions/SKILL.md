---
name: list-discussions
description: List unresolved discussions on a GitLab MR. Automatically detects MR from current branch or accepts explicit MR number. Supports auto-pagination for MRs with many discussions. Korean triggers: discussion 목록, 디스커션 보기, MR 코멘트, 리뷰 코멘트, unresolved 보기, 미해결 코멘트.
user-invocable: true
---

# List Discussions

## Overview

Retrieves and displays **unresolved discussions** from a GitLab MR in an organized format.

**Key Features**:
- **Auto MR Detection**: Finds MR from current branch automatically
- **Auto-pagination**: Fetches all discussions even for large MRs (100+ discussions)
- **Filtered View**: Shows only unresolved (actionable) discussions
- **Rich Metadata**: File path, line number, author, timestamp, code snippet

---

## When to Use

**Use this skill when:**
- Checking review comments on an MR
- Identifying which discussions need to be addressed
- Before running `fix-discussion` to see the list

**Do NOT use when:**
- Working on a branch without an MR
- All discussions are already resolved

---

## Workflow

### Phase 1: MR Identification

**1-1. Check User Input**

Determine if user provided MR number:
- Provided: Use that MR number
- Not provided: Auto-detect from current branch

**1-2. Auto-detect MR from Current Branch**

```bash
# Get current branch name
CURRENT_BRANCH=$(git branch --show-current)

# Find MR for this branch
glab mr list --source-branch="$CURRENT_BRANCH" --state=opened --json iid,title,web_url
```

**1-3. Handle No MR Found**

```
No open MR found for branch '$CURRENT_BRANCH'.

Options:
1. Specify MR number: "Show discussions for MR !123"
2. Create MR first: `glab mr create`
```

---

### Phase 2: Fetch Discussions with Pagination

**2-1. Fetch All Discussions (Auto-pagination)**

GitLab API returns max 100 items per page. For MRs with many discussions, iterate through all pages:

```bash
#!/bin/bash
# Fetch all discussions with auto-pagination

MR_IID="123"
PAGE=1
PER_PAGE=100
ALL_DISCUSSIONS="[]"

while true; do
  # Fetch current page
  RESPONSE=$(glab api "projects/:fullpath/merge_requests/${MR_IID}/discussions?per_page=${PER_PAGE}&page=${PAGE}" 2>/dev/null)

  # Check if empty or error
  if [[ -z "$RESPONSE" || "$RESPONSE" == "[]" ]]; then
    break
  fi

  # Merge results
  ALL_DISCUSSIONS=$(echo "$ALL_DISCUSSIONS $RESPONSE" | jq -s 'add')

  # Check if we got fewer items than requested (last page)
  COUNT=$(echo "$RESPONSE" | jq 'length')
  if [[ "$COUNT" -lt "$PER_PAGE" ]]; then
    break
  fi

  ((PAGE++))

  # Safety limit: max 10 pages (1000 discussions)
  if [[ "$PAGE" -gt 10 ]]; then
    echo "Warning: Reached pagination limit (1000 discussions)"
    break
  fi
done

echo "$ALL_DISCUSSIONS"
```

**2-2. Filter Unresolved Discussions**

```bash
# Filter only unresolved discussions
echo "$ALL_DISCUSSIONS" | jq '[
  .[] | select(.notes[0].resolvable == true and .notes[0].resolved == false)
]'
```

**2-3. Extract Required Fields**

For each discussion, extract:
- `id`: Discussion ID (needed for resolve)
- `notes[0].body`: Comment content
- `notes[0].author.name`: Author name
- `notes[0].created_at`: Creation timestamp
- `notes[0].position.new_path`: File path
- `notes[0].position.new_line`: Line number

---

### Phase 3: Display Results

**3-1. Summary Table**

```markdown
## Unresolved Discussions (N total)

| # | File | Line | Summary | Author |
|---|------|------|---------|--------|
| 1 | src/api/user.ts | 45 | SQL Injection risk | reviewer1 |
| 2 | src/services/auth.ts | 78 | Missing error handling | reviewer2 |
| 3 | src/utils/validation.ts | 12 | Naming improvement needed | reviewer1 |
```

**3-2. Detailed View**

For each discussion:

```markdown
### Discussion #1: SQL Injection Risk

- **File**: `src/api/user.ts:45`
- **Author**: reviewer1
- **Created**: 2025-01-05 10:30
- **Discussion ID**: `abc123def456`

**Comment**:
> This query is vulnerable to SQL injection. User input is directly concatenated...

**Code Context**:
```typescript
const query = `SELECT * FROM users WHERE id = ${userId}`;
```

---
```

**3-3. Pagination Info**

If multiple pages were fetched:

```markdown
## Pagination Info
- **Total Discussions**: 150
- **Pages Fetched**: 2
- **Unresolved**: 12
```

**3-4. Next Steps**

```markdown
## Next Steps

To fix a specific discussion:
```
Run fix-discussion skill for Discussion #1
```

To fix all discussions:
```
Run fix-discussion skill for all discussions
```
```

---

## Output Format

### Success (with discussions)

```markdown
# MR !456 - Unresolved Discussions

**MR Title**: Implement user authentication
**Branch**: feature/user-auth → main
**Total Discussions**: 5 (unresolved: 3)

## Summary Table

[table]

## Details

[detailed view for each discussion]

## Next Steps
...
```

### Success (no unresolved discussions)

```markdown
# MR !456 - All Discussions Resolved

**MR Title**: Implement user authentication
**Branch**: feature/user-auth → main

All discussions have been resolved.
This MR is ready to merge.
```

---

## glab CLI Reference

### Essential Commands

```bash
# List MRs
glab mr list --source-branch="branch-name" --state=opened

# MR details
glab mr view <MR_IID> --json

# Fetch discussions (with pagination)
glab api "projects/:fullpath/merge_requests/<MR_IID>/discussions?per_page=100&page=1"

# Fetch specific discussion
glab api "projects/:fullpath/merge_requests/<MR_IID>/discussions/<DISCUSSION_ID>"
```

### Useful jq Filters

```bash
# Filter unresolved only
jq '[.[] | select(.notes[0].resolvable == true and .notes[0].resolved == false)]'

# Group by file
jq 'group_by(.notes[0].position.new_path)'

# Extract key fields
jq '[.[] | {
  id: .id,
  file: .notes[0].position.new_path,
  line: .notes[0].position.new_line,
  body: .notes[0].body,
  author: .notes[0].author.name
}]'

# Count by author
jq 'group_by(.notes[0].author.name) | map({author: .[0].notes[0].author.name, count: length})'
```

---

## Error Handling

### glab Authentication Failure

```
GitLab authentication failed.

Check glab auth status:
$ glab auth status

If not authenticated:
$ glab auth login
```

### API Access Denied

```
Cannot access MR !456.

Possible causes:
1. MR does not exist
2. No access to this project
3. MR is already merged/closed

Verify:
$ glab mr view 456
```

### Pagination Timeout

```
Pagination took too long (exceeded 10 pages / 1000 discussions).

This MR has an unusually large number of discussions.
Consider filtering by file or reviewing in GitLab UI.
```

---

## Integration with fix-discussion

This skill's output feeds into the `fix-discussion` skill.

**Workflow**:
1. `list-discussions` → Review discussion list
2. User selects discussions to fix
3. `fix-discussion` → Code fix, reply, resolve

**Data Passed**:
- Discussion ID
- File path
- Line number
- Comment content (fix guidance)
