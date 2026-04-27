# arkraft-wiki — harness checks summary (for AC L1 derivation)

The wiki repo at `wiki_root` carries 11 hooks across 3 events: 8 PreToolUse (Write/Edit) + 2 PostToolUse (Write/Edit) + 1 Stop. When the Worker writes inside `wiki_root/content/...`, these fire automatically. choo-choo's Phase 3 Acceptance Criteria can use this list as a checklist for L1 (Concrete) — anything the harness blocks on is automatically a pass/fail criterion.

(Note: counts here track the wiki repo's `.claude/settings.json` registration, which can shift as the wiki ecosystem evolves. If the count diverges from the live settings, treat the live settings as source of truth and update this summary in a follow-up PR.)

## PreToolUse(Write|Edit) — fired on every wiki content write

### `validate-content-placement.sh`
- **What it blocks**:
  - Writes into deprecated folders: `content/decisions/`, `content/memo/`, `content/tech/` (top-level)
  - Lifecycle-tracked pages (`content/discussions/{slug}/index.md`, `content/tech/{section}/{component}/{slug}/index.md`) without `<!-- status: VALUE -->` frontmatter
  - Allowed status values: `active | decided | shipped | superseded | archived`
- **L1 candidates**:
  - `rg -l "<!-- status: -->" {written_file}` (placeholder check) → 0 hits
  - target file path is **not** under `content/{decisions,memo,tech}/` (top-level deprecated paths only — `content/tech/agents/...` etc. are still valid since `tech/` was *flattened*, not removed)

### `validate-depth.sh`
- **What it blocks**: ≥ 5 folders deep under `content/`. Allowed: 1–4 deep.
- **L1**: target file path matches `^content/[^/]+(/[^/]+){0,3}/index\.md$`

### `validate-title.sh`
- **What it blocks**:
  - Title (frontmatter `title:` or `# H1`) > 60 chars (CJK counted as 1)
  - Title contains status words (the frontmatter status is the SSOT — title duplication = noise)
- **L1**:
  - Resolved title length ≤ 60 (CJK-aware count)
  - Title doesn't include any of: `active|decided|shipped|superseded|archived|진행중|확정|폐기` (or whichever status-word set the hook script uses — check the script for current list)

### `validate-mermaid.sh`
- **What it blocks**: parser-fatal mermaid syntax (per `scripts/lint-mermaid.py`). The infamous `unquoted-brace` pattern (PR#124, PR#127 incidents) is the canonical example.
- **L1**: `python3 $WIKI_ROOT/scripts/lint-mermaid.py {written_file}` → exit 0
- Scope: `content/**/*.md` only.

### `validate-wiki-refs.sh`
- **What it blocks**: `{{wiki:slug}}` shortcodes pointing to slugs that don't exist on the filesystem. Default behavior of `shortcodes.py` is silent fallback to `/slug/` (dead link); this hook fails fast instead.
- **L1**: every `{{wiki:slug}}` in the new content has a matching `content/**/{slug}/index.md` or equivalent.

### `validate-timeline.sh`
- **What it blocks**: timeline entries (`content/timeline/...`) missing required frontmatter:
  - `date: YYYY-MM-DD`
  - `type: decision|release|sales|milestone|incident` (see hook for current list)
  - `title: ...`
- **L1** (only when section == `timeline`):
  - frontmatter has `date`, `type`, `title` keys
  - filename matches `YYYY-MM-DD-slug.md` (flat) or `YYYY-MM-DD-slug/index.md` (folder)

### `enforce-folder-doc.sh`
- **What it blocks**: any `content/**/*.md` that isn't `index.md` inside a directory. Exception: `content/index.md` itself.
- **L1**: target file path basename == `index.md` (with the one root-level exception)

### `no-site-edit.sh`
- **What it blocks**: writes to `site/**/*` (build artifact directory).
- **L1**: target file path doesn't start with `site/`. (This is hard to violate accidentally during wiki authoring, but the hook is a backstop.)

## PostToolUse(Write|Edit)

### `remind-build.sh`
- **Effect**: emits a `systemMessage` reminding the Worker that `./build.sh` should run before Stop.
- **L1 implication**: not directly a blocker, but Stop will block via `content-checklist.sh` if build is stale.

### `suggest-mermaid.sh` (PostToolUse only — soft suggestion)
- **Effect**: scans the written file for ASCII diagram patterns and suggests Mermaid conversion via `systemMessage`. Registered alongside `remind-build.sh` on PostToolUse(Write|Edit).
- **L1 implication**: none (advisory only).

## Stop

### `content-checklist.sh`
- **What it blocks** (decision: block):
  - `content/` is newer than `site/index.html` → "Build needed: ... Run ./build.sh before finishing."
  - `site/` does not exist → same message.
  - List items missing the required blank line before them (CommonMark `<li>` rendering quirk) — runs `scripts/lint-list-blank-lines.py`.
  - Mermaid syntax violations (last-mile re-check via `scripts/lint-mermaid.py`).
- **What it warns** (systemMessage only): TODO markers, unfilled placeholders.
- **L1**:
  - `[ "$WIKI_ROOT/site/index.html" -nt "$WIKI_ROOT/content" ]` (site fresher than content) — Worker must run `./build.sh` last
  - `python3 $WIKI_ROOT/scripts/lint-list-blank-lines.py --content-dir content` → 0 violations
  - `python3 $WIKI_ROOT/scripts/lint-mermaid.py` → 0 violations (whole content tree)

## Mapping to choo-choo Acceptance Criteria

When choo-choo composes Phase 4's prompt, the wiki authoring task should list these as **L1 (Concrete) candidates**:

```markdown
### Level 1: Concrete
- [ ] file path matches content/{section}/.../index.md (≤4 deep, dir/index pattern)
- [ ] frontmatter status set to one of {active|decided|shipped|superseded|archived} (if lifecycle-tracked)
- [ ] title ≤ 60 chars, no status words
- [ ] all {{wiki:slug}} references resolve to existing files
- [ ] mermaid blocks (if any) pass lint-mermaid.py
- [ ] (timeline only) frontmatter has date/type/title + filename pattern
- [ ] post-write: ./build.sh runs successfully + site/ refreshed
- [ ] lint-list-blank-lines.py: 0 violations
```

**L2 candidates** (Reviewer judges the patterns, not exact-match):
- Section choice matches the doc's intent (start/market/tech/discussions/decisions/timeline) — see `wiki-structure.md` semantics table
- Lifecycle status is correct for the doc's stage (don't write to `decisions/` for unfinished discussions)
- Cross-references use `{{wiki:slug}}` (not raw paths) — so future renames don't break

**L3 candidates** (QA reads as a persona):
- Persona matched to the section (see SKILL.md "Suggested L3 personas" list)
- Outcome: persona can extract the doc's main claim in 5 minutes / can act on the next step / can find related docs via the references
- Verification: QA reads the doc end-to-end with the persona's mindset; flag any place where the persona would stall

## Why this lives here, not as plugin hooks

The wiki repo's hooks are the single source of truth. Copying them into the plugin would create dual-source drift (hook update → plugin must be re-published). Instead, this summary documents *what they enforce* so the choo-choo prompt can derive AC items, and the Worker actually triggers the hooks by writing to `wiki_root/content/`. If the user's wiki repo updates its hooks, this summary needs a corresponding edit (treat it as semi-static documentation, not a runtime mirror).
