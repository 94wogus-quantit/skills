# Inline Comment Format Guide

This guide explains how to create inline discussions on GitLab MRs.

## GitLab Discussion API Format

### Using glab CLI

```bash
# Create comment on specific line of specific file
glab mr note create <MR_IID> \
  --message "Comment content" \
  --file "src/path/to/file.ts" \
  --line 123

# Comment spanning multiple lines (line range)
glab mr note create <MR_IID> \
  --message "Comment content" \
  --file "src/path/to/file.ts" \
  --line-start 120 \
  --line-end 125
```

### Using GitLab API Directly

```bash
# POST /projects/:id/merge_requests/:merge_request_iid/discussions
curl --request POST \
  --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
  --header "Content-Type: application/json" \
  --data '{
    "body": "🔴 **Critical**: SQL Injection Risk\n\nUser input is directly connected to the query. Use prepared statements.",
    "position": {
      "base_sha": "'"${BASE_SHA}"'",
      "start_sha": "'"${START_SHA}"'",
      "head_sha": "'"${HEAD_SHA}"'",
      "position_type": "text",
      "new_path": "src/api/user.controller.ts",
      "new_line": 45
    }
  }' \
  "https://gitlab.com/api/v4/projects/${PROJECT_ID}/merge_requests/${MR_IID}/discussions"
```

## Comment Message Format

### Format by Severity

#### 🔴 Critical

```markdown
🔴 **Critical**: [Issue Title]

**Problem**:
[Detailed description]

**Risk**:
[What risks are involved]

**Suggested Fix**:
```typescript
// Recommended code
```

**Reference**: [Related document link]
```

#### 🟡 High Priority

```markdown
🟡 **High**: [Issue Title]

**Description**:
[Issue details]

**Suggested Fix**:
[Recommended approach]
```

#### 🟢 Medium Priority

```markdown
🟢 **Medium**: [Issue Title]

**Suggestion**:
[Improvement direction]
```

## Severity Level Indicators

### Using Emojis

- 🔴 Critical
- 🟡 High
- 🟢 Medium
- ✅ Good (praise)
- 💡 Suggestion (idea)
- ⚠️ Warning (caution)

### Using Text

- `[CRITICAL]`
- `[HIGH]`
- `[MEDIUM]`
- `[INFO]`

## Real Examples

### Example 1: SQL Injection

```markdown
🔴 **Critical**: SQL Injection Vulnerability

**Location**: `src/api/user.controller.ts:45`

**Problem**:
User input `email` is directly connected to SQL query, making it vulnerable to SQL Injection attacks.

**Current Code**:
```typescript
const query = `SELECT * FROM users WHERE email = '${email}'`;
```

**Suggested Fix**:
```typescript
const query = 'SELECT * FROM users WHERE email = ?';
const result = await db.execute(query, [email]);
```

**Reference**: https://owasp.org/www-community/attacks/SQL_Injection
```

### Example 2: Naming Improvement

```markdown
🟢 **Medium**: Variable Naming Improvement Recommended

**Description**:
Variable name `d` is unclear in meaning. Using a more descriptive name improves readability.

**Suggested Fix**:
```typescript
// Before
const d = new Date();

// After
const currentDate = new Date();
```
```

### Example 3: Error Handling

```markdown
🟡 **High**: Missing Error Handling

**Description**:
Async function lacks error handling, which may cause app crash when exceptions occur.

**Suggested Fix**:
```typescript
try {
  const result = await fetchUserData(userId);
  return result;
} catch (error) {
  logger.error('Failed to fetch user data:', error);
  throw new UserDataError('Unable to fetch user data');
}
```
```

## Script Example

### create-inline-comments.sh

```bash
#!/bin/bash
set -e

MR_IID=$1
REVIEW_FILE="MR_${MR_IID}_CODE_REVIEW.md"

# Extract location info from MR_CODE_REVIEW.md and create comments
# Example: Parse locations in format `file_path.ts:123`

while IFS= read -r line; do
  if [[ $line =~ \`([^\`]+):([0-9]+)\` ]]; then
    FILE="${BASH_REMATCH[1]}"
    LINE="${BASH_REMATCH[2]}"

    # Read until next section to use as comment content
    # (Actual implementation may be more complex)

    echo "Creating comment on ${FILE}:${LINE}"

    # Execute glab mr note create
    # glab mr note create ${MR_IID} \
    #   --message "${COMMENT_BODY}" \
    #   --file "${FILE}" \
    #   --line ${LINE}
  fi
done < "${REVIEW_FILE}"
```

## Notes

1. **File Path**: Use relative path from repository root
2. **Line Number**: Comments can only be added to changed lines in MR
3. **SHA Values**: Accurate commit SHA required when using GitLab API
4. **Permissions**: `GITLAB_TOKEN` requires sufficient permissions (api scope)
5. **Rate Limiting**: Consider API call rate limits
