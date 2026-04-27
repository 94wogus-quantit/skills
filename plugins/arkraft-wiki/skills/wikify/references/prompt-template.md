# choo-choo args template

The exact string the wikify skill passes to `Skill(skill: "run-ralph:choo-choo", args: ...)`. Worker substitutes the placeholders below before invoking.

## Template

```text
Wiki authoring task — arkraft-wiki에 지식 문서 생성/업데이트.

[USER_TASK]
<one or two-sentence verbatim copy of what the user said when they invoked /wikify>

[WIKI_ROOT]
<absolute path resolved from .claude/arkraft-wiki.local.md settings, e.g. /Users/me/Project/arkraft/arkraft-wiki>

[REPOS_TO_SCAN]
<bullet list of absolute repo paths from settings, OR the literal note "default 9 arkraft repos under <parent_of_wiki_root>/" if settings didn't override>

[SECTION_TAXONOMY]
- start/        — vision, philosophy, glossary, system-overview, contributing
- market/       — sales, customer, competition, pipeline, partnerships
- tech/agents/  — AI agent별 (alpha, insight, portfolio, report, data, …)
- tech/quant/   — 퀀트 / 금융 도메인 지식
- tech/engineering/ — CI/CD, infra, ops runbooks
- discussions/  — 분석 / RFC / 제안 (status: active)
- decisions/    — 결정 ADR (status: decided, immutable)
- timeline/     — events (decision/release/sales/milestone/incident)

Lifecycle: open question → discussions/ → decisions/ (status frontmatter tracked)

[STRUCTURE_RULES]
- Folder pattern: content/{section}/.../index.md (≤ 4 folders deep)
- Lifecycle-tracked pages require <!-- status: VALUE --> frontmatter
- Title ≤ 60 chars (CJK = 1), no status words
- Cross-refs use {{wiki:slug}} (must resolve)
- Mermaid blocks pass lint-mermaid.py
- Deprecated paths blocked: content/{decisions,memo,tech}/ at top-level (note: tech/ subdirs like tech/agents/ are valid — only the literal top-level "tech/" is deprecated as flat path)

[HARNESS_HOOKS_THAT_WILL_FIRE]
PreToolUse(Write|Edit):
  - validate-content-placement (placement + status frontmatter)
  - validate-depth (≤ 4 folders)
  - validate-title (length + no-status-words)
  - validate-mermaid (parser-fatal syntax)
  - validate-wiki-refs ({{wiki:slug}} resolves)
  - validate-timeline (timeline/ frontmatter)
  - enforce-folder-doc (dir/index.md pattern)
  - no-site-edit (site/ protected)
PostToolUse(Write|Edit):
  - remind-build (systemMessage only)
  - suggest-mermaid (systemMessage only)
Stop:
  - content-checklist (build-needed / list-blank-lines / mermaid lint — BLOCK)

These are guaranteed to fire on every Write into [WIKI_ROOT]/content/. Use them as L1 acceptance criteria.

[SUGGESTED_AC_TEMPLATE]
L1 (Concrete) — bind to harness checks:
  - [ ] file path: content/{section}/.../index.md, ≤ 4 deep
  - [ ] frontmatter <!-- status: VALUE --> if lifecycle-tracked
  - [ ] title ≤ 60 chars, no status words
  - [ ] all {{wiki:slug}} resolve
  - [ ] mermaid lint passes (if any)
  - [ ] (timeline only) date/type/title frontmatter + filename YYYY-MM-DD-slug
  - [ ] ./build.sh ran successfully + site/ refreshed
  - [ ] lint-list-blank-lines.py: 0 violations

L2 (Structural) — Reviewer judges patterns:
  - [ ] section choice matches doc intent (Phase 1 Clarify confirmed)
  - [ ] lifecycle status correct for stage
  - [ ] cross-refs use {{wiki:slug}}, not raw paths
  - [ ] (when relevant) supersedes/superseded-by chain noted in frontmatter

L3 (Holistic) — Reader-Persona:
  - Persona matched to section's audience (see [PERSONA_HINTS] below)
  - Outcome: persona forms the intended mental model in 5 min

[PERSONA_HINTS]
section → suggested persona:
  - start         → "처음 합류한 신규 멤버"
  - market        → "외부와 의사결정하는 비기술 인원"
  - tech/agents   → "이 agent를 처음 다루는 백엔드 개발자"
  - tech/quant    → "퀀트 도메인 입문자 / 인접 도메인의 새로 합류한 리서처"
  - tech/engineering → "온콜로 들어와 처음 운영 보는 개발자"
  - discussions   → "1주일 후 후속 논의를 이어갈 의사결정자"
  - decisions     → "6개월 후 이 결정을 다시 보는 신규 메인테이너"
  - timeline      → "분기말 회고에서 이 이벤트를 인용하는 PM"

[CONSTRAINTS]
- Write only inside [WIKI_ROOT]/content/
- Section/depth/title decisions confirmed via Phase 1 Clarify (AskUserQuestion)
- Never write to decisions/ if the underlying call hasn't been made — start in discussions/
- Build (./build.sh) is the Worker's responsibility; Stop hook blocks if site/ is stale
- Mermaid block 만들 때는 lint 통과 보장. ASCII 다이어그램은 suggest-mermaid가 권유.

[NOTES_FOR_RALPH]
- Phase 1.5 dispatch: this is doc-only work + may touch multiple wiki pages (cross-refs).
  trivial threshold likely met (no JIRA, no new abstraction, internal-only). Default to TRIVIAL flow unless the user signals otherwise — wf 5-skill chain has no test loop suited to wiki content.
- Phase 6 record decision: wiki commits land in WIKI_ROOT's repo (separate from the Claude session's repo). The plugin's record-gate inspects the *current* repo's branch, not WIKI_ROOT's branch — wiki commits won't trip it. The wiki repo's own Stop content-checklist hook handles wiki-side build/doc verification.
- Build step: every iteration where wiki content actually changed should end with `cd "$WIKI_ROOT" && ./build.sh` (or whatever the user's settings.build_command says) before promise emission.
```

## Substitution rules (for the wikify skill body)

When wikify constructs the args string:

1. Replace `[USER_TASK]`, `[WIKI_ROOT]`, `[REPOS_TO_SCAN]` (section bodies and inline references) with the resolved values.
2. Keep all other sections **verbatim** — they're guidance for choo-choo's planning, not data the wikify skill should rewrite per-call.
3. The full args string is shell-safe by virtue of being passed via the Skill tool (not Bash). No need to escape backticks / `$` / `!` — Skill args are not word-split.

## Anti-patterns

- **Don't** prefill section choice in the args. Let choo-choo's Phase 1 Clarify ask the user. The taxonomy is provided as context, not a decision.
- **Don't** prefill the L1 checklist as final criteria — the Suggested AC Template is exactly that, suggested. choo-choo's Phase 3 may add/remove items based on the actual task.
- **Don't** include git scan results in the args. The repos_to_scan list is enough — choo-choo can run the scan itself in Phase 1, and pre-running here would waste a turn.
