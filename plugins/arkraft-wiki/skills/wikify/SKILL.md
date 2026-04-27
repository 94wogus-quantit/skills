---
name: wikify
description: arkraft-wiki repo에 지식 문서를 생성/업데이트하는 thin wrapper skill. "지식화하자", "지식화", "wiki에 추가해줘", "wiki 문서로 남겨줘", "wikify", "wiki 정리", "wiki에 정리" 같은 요청에 사용. 사용자가 wiki_root를 settings로 지정하면 그 경로로 작업. 컨텍스트 수집 + 섹션 결정 + Acceptance Criteria 도출은 직접 처리하지 않고 run-ralph:choo-choo에 위임 — 이 skill은 wiki-specific 컨텍스트(섹션 구조, lifecycle, harness 검사 항목, scan 대상 repo 목록)를 묶어 choo-choo에 깨끗한 task 명세로 전달하는 것이 전부.
user-invocable: true
---

# Wikify (thin wrapper for arkraft-wiki authoring)

This skill **does not author wiki content directly**. It packages wiki-specific context and delegates the actual iterative authoring to `run-ralph:choo-choo`. The resulting Ralph Loop iterates on the draft, the wiki repo's own PreToolUse hooks enforce structure, and Reviewer/QA validate quality.

## Where the section decision happens (read this if you wonder "어디에 넣을지 고민하는 단계는?")

A wiki authoring task has one decision that has to be made before drafting: **which section under `content/` does this belong to?** (start / market / tech/agents / tech/quant / tech/engineering / discussions / decisions / timeline). The lifecycle (open question → discussions → decisions), the title rules, the persona, and the L1 acceptance checks all branch off that one choice.

In this plugin **wikify does NOT make that decision and does NOT ask the user about it directly**. Instead:

1. **wikify (Phase 2 below)** packages the section taxonomy + lifecycle + each section's semantics into the choo-choo args string. The relevant pieces live in `references/wiki-structure.md` (full taxonomy + section semantics table) and `references/prompt-template.md` (the `[SECTION_TAXONOMY]` block of the args).
2. **choo-choo (its own Phase 1 Clarify)** is the agent that actually asks the user "어느 섹션에 넣을까요? (start/market/tech/agents/tech/quant/...)" via AskUserQuestion, using the taxonomy wikify provided. choo-choo also asks about title and "new doc vs update existing" at the same step.
3. **choo-choo (its own Phase 3 Acceptance Criteria)** then derives concrete L1/L2/L3 criteria from that section choice — e.g., for `discussions/` the L1 includes `<!-- status: -->` frontmatter, for `timeline/` it includes the `YYYY-MM-DD-slug` filename pattern, for `tech/agents/{name}/` the L3 persona is "이 agent를 처음 다루는 백엔드 개발자".

The reason the decision lives in choo-choo, not wikify: choo-choo already has a tested Clarify phase + AskUserQuestion + multi-turn iteration, and duplicating that machinery inside wikify would defeat the thin-wrapper principle. wikify's job is to **make sure choo-choo has the right context to ask a good question** — the taxonomy must be in front of choo-choo before it asks the user, otherwise choo-choo guesses.

If `references/wiki-structure.md` ever gets out of sync with the wiki repo's actual section structure, choo-choo will ask outdated section names — that's the single failure mode this design is sensitive to. Keep wiki-structure.md updated whenever the wiki repo's `content/` taxonomy changes.

## Why thin wrapper, not direct authoring

Wiki authoring is naturally iterative — first draft → reviewer flags placement / depth / title / mermaid issues → revise → reviewer re-checks → ship. That is exactly what `run-ralph:choo-choo` is designed for. Building a parallel iterative engine inside this skill would duplicate work the user already trusts.

The wrapper's job is to:
1. Read user-specific settings (wiki_root path, repo scan list, etc.)
2. Bundle wiki-specific knowledge (section semantics, lifecycle rules, harness checks) as references for choo-choo's prompt
3. Hand off — `Skill(skill: "run-ralph:choo-choo", args: "<wiki authoring task + bundled context>")`

After hand-off, choo-choo's Phase 1 (Clarify) handles user questions about section/title/scope, Phase 3 (Acceptance Criteria) derives concrete L1 checks from the harness summary, and the Ralph Loop iterates against the wiki repo's hooks.

---

## Phase 0: Read settings

The plugin reads a settings file at `${CLAUDE_PROJECT_DIR}/.claude/arkraft-wiki.local.md` (or, if absent, falls back to user-global `~/.claude/arkraft-wiki.local.md`). The file is YAML frontmatter + (optional) markdown body, following the `plugin-dev:plugin-settings` convention:

```markdown
---
wiki_root: /Users/me/Project/arkraft/arkraft-wiki
repos:
  - /Users/me/Project/arkraft/arkraft-api
  - /Users/me/Project/arkraft/arkraft-web
  - /Users/me/Project/arkraft/arkraft-agent-alpha
  - /Users/me/Project/arkraft/arkraft-agent-insight
  - /Users/me/Project/arkraft/arkraft-agent-portfolio
  - /Users/me/Project/arkraft/arkraft-agent-report
  - /Users/me/Project/arkraft/arkraft-agent-data
  - /Users/me/Project/arkraft/arkraft-deploy
  - /Users/me/Project/arkraft/arkraft-sdk
build_command: ./build.sh   # optional — Stop hook reminder uses this
---

# arkraft-wiki settings
(optional notes)
```

If the settings file is missing, the skill prints an actionable message:

```
⚠️ arkraft-wiki settings not found.

Create one of:
  - {project}/.claude/arkraft-wiki.local.md   (per-project)
  - ~/.claude/arkraft-wiki.local.md           (user-global)

Minimum frontmatter:
  ---
  wiki_root: /absolute/path/to/arkraft-wiki
  ---

See plugins/arkraft-wiki/README.md for the full template.
```

…and stops without invoking choo-choo. Do **not** guess a default path.

When the file exists but `wiki_root` is missing or empty, treat it as not configured and emit the same message.

## Phase 1: Confirm wiki_root + collect cheap context

1. Verify `test -d "$WIKI_ROOT"` succeeds. If not, error out with the missing-settings message + the path that was attempted.
2. Confirm the wiki repo looks like the expected ecosystem: `test -f "$WIKI_ROOT/INDEX.md" && test -d "$WIKI_ROOT/content" && test -f "$WIKI_ROOT/build.sh"`. If any check fails, surface a one-line warning ("$WIKI_ROOT exists but doesn't look like the arkraft-wiki ecosystem — INDEX.md / content/ / build.sh missing"). The user might be pointing at a different wiki; ask once before proceeding.
3. Capture the 1-2 sentence task description from the user's input as `USER_TASK` (verbatim — choo-choo's Clarify phase will sharpen it).

Do **not** scan all repos here, do **not** decide a section, do **not** compose criteria. Those are choo-choo's job.

## Phase 2: Bundle wiki-specific context

Read these reference files (bundled with this plugin — they describe arkraft-wiki's invariants):

- `references/wiki-structure.md` — section taxonomy + lifecycle (open question → discussions → decisions, etc.) + canonical 2-deep / 4-deep depth rules
- `references/repo-list.md` — default git-scan repo list + how settings overrides work
- `references/harness-summary.md` — the 11 hooks (8 PreToolUse + 2 PostToolUse + 1 Stop) the wiki repo enforces (placement, depth, title, mermaid, timeline, refs, build-needed). These map 1:1 to L1 acceptance criteria choo-choo can include.
- `references/prompt-template.md` — exact format for the args string handed to choo-choo

Build the choo-choo task description by filling the template:

```
[wiki-authoring task]

User intent: [USER_TASK]

wiki_root: [WIKI_ROOT]   # substituted to the absolute path resolved in Phase 1 (e.g. /Users/me/Project/arkraft/arkraft-wiki)
repos to scan for context: <list from settings, or note "default 9 arkraft repos">

Section structure & lifecycle (from references/wiki-structure.md):
  - start / market / tech / discussions / decisions / timeline
  - open question → discussions → decisions (lifecycle progression)
  - 4-deep limit, content/{section}/.../index.md folder pattern

Harness checks the wiki repo will enforce on every Write/Edit (use as L1 candidates):
  - validate-content-placement (status frontmatter, deprecated folder block)
  - validate-depth (≤ 4 folders under content/)
  - validate-title (≤ 60 chars, no status words)
  - validate-mermaid (parser-fatal syntax block)
  - validate-wiki-refs ({{wiki:slug}} resolves)
  - validate-timeline (frontmatter date/type/title for timeline entries)
  - enforce-folder-doc (dir/index.md pattern)
  - no-site-edit (site/ build artifact protected)
  - Stop: content-checklist (build needed / placeholder / mermaid / list-blank-lines)

Suggested L3 personas (from wiki section semantics):
  - For start/market: "처음 합류한 신규 멤버 / 외부 파트너"
  - For tech/agents|quant|engineering: "이 컴포넌트 처음 다루는 백엔드/리서치 개발자"
  - For discussions: "1주일 후 후속 논의를 이어갈 의사결정자"
  - For decisions (ADR): "6개월 후 이 결정을 다시 보는 신규 메인테이너"
  - For timeline: "분기말에 history 훑어보는 PM"

Constraints:
  - Write only inside [WIKI_ROOT]/content/ (substituted to absolute path before send)
  - Section/depth/title decisions must be confirmed via Phase 1 Clarify (AskUserQuestion)
  - Lifecycle: never write directly to decisions/ if the underlying call hasn't been made — start in discussions/
  - Build is the Worker's responsibility — Stop hook (content-checklist) blocks if site/ is stale
```

The exact wording of the args string lives in `references/prompt-template.md`. The above is the structural skeleton.

## Phase 3: Hand off to choo-choo

Invoke:

```
Skill(
  skill: "run-ralph:choo-choo",
  args: "<the bundled task description from Phase 2>"
)
```

That's it. Stop here — choo-choo takes over.

## What happens after the hand-off (informational, not part of this skill's job)

1. choo-choo Phase 1 Clarify — asks the user (via AskUserQuestion) which section, what title, new doc vs update.
2. choo-choo Phase 1.5 Auto-dispatch — wiki authoring is doc-only with cross-file references, so it usually classifies as TRIVIAL or borderline. Either path is fine. The wf 5-skill chain rarely fits wiki authoring (no test loop), so trivial → ralph direct is the natural outcome.
3. choo-choo Phase 2 Team — Documentation default, plus Reader-Persona (matched to the section's audience).
4. choo-choo Phase 3 AC — L1 derived from harness-summary; L2 from section invariants; L3 from the persona list above.
5. Ralph Loop iterations — Worker drafts at `<wiki_root>/content/...`; the wiki repo's PreToolUse hooks fire on every Write (placement / depth / title / mermaid validation); Reviewer/QA gate completion.
6. choo-choo Phase 6 — report + record decision. record-gate looks at `origin/{base}` of the *current* repo (not wiki_root), so wiki commits land in the wiki repo's branch and don't trip wogus-plugin's record-gate. The wiki repo's own Stop content-checklist hook handles the wiki-side build/doc-sync.

## Output convention

This skill produces no artifacts of its own. The choo-choo invocation is the side effect; everything else is choo-choo's output.

## Settings template

A starter settings file is provided at `references/arkraft-wiki.local.md.template`. Users copy it to `{project}/.claude/arkraft-wiki.local.md` (or `~/.claude/`) and edit `wiki_root` to their machine's path.

## Dependencies

- `run-ralph` plugin must be installed and enabled (this skill terminates by invoking `run-ralph:choo-choo`). If not installed, output: `⚠️ run-ralph plugin not available — install it before using wikify.`
- The arkraft-wiki repo itself must exist at the configured `wiki_root` and contain the canonical hooks/skills (PreToolUse harness). This skill does **not** ship copies of those hooks — the wiki repo is the source of truth.
