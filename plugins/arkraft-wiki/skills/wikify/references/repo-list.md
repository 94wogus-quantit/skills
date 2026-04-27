# Repo scan list

This reference lists the arkraft repo set that wikify's Phase 2 bundles into the choo-choo args string (the `[REPOS_TO_SCAN]` slot defined in `prompt-template.md`). It also documents the settings-override rule so the Worker knows when to use the user-supplied list instead of the defaults.

When the user asks for a wiki page about "what we just did", choo-choo's Phase 1 Clarify often needs to scan recent git activity to anchor the writeup in real changes. The repos below are what gets scanned.

## Default arkraft repo set (9 repos)

Stored in the original wikify (arkraft-side) skill as a hardcoded list:

```
arkraft-api
arkraft-web
arkraft-agent-alpha
arkraft-agent-insight
arkraft-agent-portfolio
arkraft-agent-report
arkraft-agent-data
arkraft-deploy
arkraft-sdk
```

Resolved as `${parent_of_wiki_root}/{repo_name}` — assumes all arkraft repos sit as siblings of `arkraft-wiki/` under one parent directory (typical layout: `~/Project/arkraft/{repo}` for every repo).

## Settings override

The user can override the list in `.claude/arkraft-wiki.local.md` frontmatter:

```yaml
repos:
  - /Users/me/Project/arkraft/arkraft-api
  - /Users/me/Project/arkraft/arkraft-web
  - /Users/me/Project/arkraft/some-other-repo   # absolute paths, not bare names
```

When `repos:` is present in settings:
- Use **only** the listed paths (do not merge with defaults)
- Each entry is an absolute path; verify with `test -d "$path/.git"` before scanning

When `repos:` is **absent** from settings:
- Fall back to the 9-repo default list above
- Resolve as `${parent_of_wiki_root}/{repo_name}` (e.g., if `wiki_root=/Users/me/Project/arkraft/arkraft-wiki`, parent is `/Users/me/Project/arkraft`, so `arkraft-api` → `/Users/me/Project/arkraft/arkraft-api`)

## Scan command (for reference — Worker uses this in Ralph iterations)

```bash
for repo in "${REPOS[@]}"; do
  [ -d "$repo/.git" ] || continue
  echo "=== $(basename "$repo") ==="
  git -C "$repo" log --oneline -5 2>/dev/null
done
```

Limit to `-5` (last 5 commits) per repo by default. Increase only if the user explicitly says "지난 1주일", "지난 N일" etc.

## What this is *not*

- Not a list of repos the wiki "owns" — wiki is independent of code repos.
- Not a permission list — the user can still scan any repo by passing it inline to choo-choo.
- Not exhaustive — new arkraft repos that appear later need to be added either here (PR to wogus-plugin) or in user's local settings.

## When to suggest adding a repo

If during git scan the Worker notices a repo path mentioned in the user's message that isn't on the list, ask once via AskUserQuestion whether to scan it for this run + whether to persist it in settings for future runs.
