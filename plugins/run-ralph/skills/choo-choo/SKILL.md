---
name: choo-choo
description: This skill should be used when the user asks to "run ralph", "랄프 실행", "랄프 돌려", "ralph loop 실행", "ralph로 해줘", "랄프로 돌려", "run-ralph", "choo choo", "랄프 출발", or wants to execute ANY iterative work — code changes, design documents, skill/workflow integrations, architectural decisions, documentation, or refactoring — through a multi-agent team. Choo-choo is a general iterative framework, not a code-only tool: anything expressible as "work + acceptance criteria + per-iteration verification" fits. Transforms the request into a Ralph Loop prompt with a multi-agent team (mandatory Reviewer + QA), 3-level acceptance criteria, and an iteration workflow that gates completion-promise emission on independent verdicts. Anchors all sentinel/prompt files to the project root so a Worker that `cd`s into a sub-directory mid-loop does not break the gate. Then invokes /ralph-loop.
user-invocable: true
---

# Choo-Choo (Run Ralph)

Transforms a natural-language request into a structured Ralph Loop prompt that runs with a multi-agent team. Reviewer and QA are mandatory on every task — without independent verdicts the Worker self-approves and emits the completion promise prematurely.

## Scope — what choo-choo is for (read this first)

Choo-choo is a **general iterative framework**, not a code-changes-only tool. The Ralph Loop value is "Worker can't self-approve + stepwise verifiable progress" — that mechanism applies to any work where iterations can be defined.

**In scope (treat all of these as first-class):**

| Category | Example requests | What an "iteration" looks like |
|----------|------------------|-------------------------------|
| **Code changes** | refactor, bug fix, feature add, infra (terraform/k8s), test writing | edit code → diff → tests/verifications |
| **Meta / Design** | ADR 작성, 두 스킬 통합 설계, 워크플로우 재설계, 아키텍처 결정 문서 | draft/refine a design artifact → reviewer judges structure → QA judges reader perception |
| **Integration / Migration** | 두 모듈/플러그인을 하나로 합치기, 기존 → 새 시스템으로의 단계적 마이그레이션 설계 | each iteration advances one section/module of the integration |
| **Documentation** | README, runbook, onboarding 문서, ADR 모음 | write/revise → reviewer checks structure → QA reads as the target persona |

**Out of scope (rare exceptions):**
- One-shot trivial tasks the user could do themselves in one message — ask once at Phase 1 whether choo-choo is overkill; if user says proceed, proceed.
- Live debugging of choo-choo itself (running the skill on the skill while it's running creates a meta-loop).

**Do not refuse a request as "not a code change" or "not a Ralph Loop task."** If you can name an iteration unit and acceptance criteria, you can run it through choo-choo — translate the request, don't reject it. The previous narrowing-to-code-only behavior was a framing bug, not a design intent.

## Authoring conventions (applies to every prompt this skill generates)

- **Instructions / rules / rationale are written in English.** This includes the Iteration Workflow block, acceptance-criteria level definitions, constraints, step labels, and any explanation of *why* something must happen.
- **Examples, sample phrasing, confirmation UI, and user-facing Korean prose stay in Korean.** This includes clarification questions, the Phase 5 confirmation block, the pointer prompt passed to `/ralph-loop`, and illustrative task names.
- When adding new content to this skill or to references, keep the two registers separated — do not translate rules into Korean or examples into English.

## Path discipline (MANDATORY — read this before Phase 5)

Every sentinel, prompt file, and `.ralph/*.md` artifact MUST be referenced as an **absolute path anchored to the project root**, not as a CWD-relative path.

**Why:** Ralph Loop iterations frequently `cd` into sub-directories (e.g. monorepo packages like `arkraft-wiki/`, `arkraft-web/`). If sentinels are touched at CWD, the next iteration's CWD or the project-level Stop hook will look in the wrong place — Reviewer/QA spawns read stale files, the report gate misfires, and the loop silently breaks.

**Anchor capture** — at the start of Phase 5 (before any file write or sentinel touch):

```bash
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
```

Use `"$PROJECT_ROOT/.ralph/<slug>/prompt.md"`, `"$PROJECT_ROOT/.ralph/<slug>/review-{N}.md"`, `"$PROJECT_ROOT/.ralph/<slug>/qa-{N}.md"`, `"$PROJECT_ROOT/.ralph/<slug>/<custom-role>-{N}.md"` everywhere — including inside the composed prompt body, so Reviewer/QA spawns receive absolute paths too.

The single exception is the **session-level sentinel** at `"$PROJECT_ROOT/.ralph/.report-pending"`, which stays at the top level of `.ralph/`. The Stop hook checks one fixed path; promoting the sentinel into a slug subdirectory would force the hook to scan all subdirs every Stop event. A Claude session only runs one choo-choo at a time, so a single top-level sentinel is sufficient.

### Why per-slug subdirectories (not flat files)

Earlier versions wrote `prompt`, `review-{N}`, `qa-{N}` directly under `.ralph/`. When users ran multiple Ralph Loop tasks in the same repo over time, the iteration logs from different runs collided — `review-1.md` from yesterday's auth refactor was overwritten by today's docs rewrite, and after a few runs it became impossible to tell which file belonged to which task. Per-slug subdirectories (`<slug>/prompt.md`, `<slug>/review-1.md`, …) keep every run's artifacts isolated and inspectable indefinitely.

The Stop hook (`hooks/run-ralph-report-gate.sh`) uses `${CLAUDE_PROJECT_DIR}` for the same CWD-robustness reason — both ends agree on the project root regardless of CWD drift.

---

## Phase overview

1. **Clarify** — Resolve ambiguity through 1–3 targeted questions.
1.5. **Auto-dispatch classification** — Score the task on trivial vs full-pipeline signals. trivial → ralph direct. full → run `wf:analyze → plan → execute → qa → record` first, then return to Phase 2 with the wf artifacts as context.
2. **Team Composition** — Pick the default team for the task type, add custom roles when triggered.
3. **Acceptance Criteria** — Define 3 levels (Concrete / Structural / Holistic) with conditional enforcement.
4. **Compose** — Generate the prompt with team workflow embedded.
5. **Execute** — Capture project root, write the prompt file, touch the sentinel, then invoke `/ralph-loop`.
6. **Report** — After `/ralph-loop` returns, summarize what actually happened so the user doesn't have to reconstruct it from `.ralph/` and `git diff`.

---

## Phase 1: Clarify

Ask via AskUserQuestion only when input is insufficient. Skip if already specific.

| Element | Insufficient example | Question example |
|---------|---------------------|------------------|
| **Scope (code)** | "리팩토링해줘" | "어떤 파일/모듈 범위인가요?" |
| **Problem definition** | "auth 고쳐줘" | "어떤 증상/에러가 발생하나요?" |
| **Success criteria** | "성능 개선해줘" | "어떤 지표가 개선되면 완료인가요?" |
| **Expected result** | "테스트 추가해줘" | "어떤 종류의 테스트? 어떤 모듈 대상?" |
| **Scope (design/meta)** | "두 스킬 통합해줘" | "어떤 두 스킬? 통합 결과물은 새 스킬 / 기존 하나로 흡수 / 디스패처 중 무엇? 완료 기준은?" |
| **Design artifact target** | "아키텍처 결정해줘" | "결정해야 할 선택지가 무엇무엇인가요? 결과를 ADR 문서로 남기나요, 코드 반영까지 가나요?" |

Principles:
- Maximum 1–3 questions at a time.
- Resolve the most critical ambiguity first.
- Explore the repo briefly before asking — reflect what you found in the question.

Detailed task-type guides: see `references/prompt-template.md` ("Clarification questions by task type").

---

## Phase 1.5: Auto-dispatch classification

After Phase 1, before Phase 2, classify the task to decide whether to run the new `wf` plugin's full pipeline (`wf:analyze → plan → execute → qa → record`) before composing the Ralph Loop prompt, or skip wf entirely and go straight into Phase 2.

**Why this exists**: simple, contained tasks (typo fix, single-line tweak) don't need a 5-skill external review pipeline — the overhead would dwarf the work. But anything with cross-file impact, schema/API changes, or formal issue tracking benefits from going through wf first because wf produces analyzed REPORT, externally-reviewed PLAN, executed code, independently-QA'd verification, and documented record — all of which then feed into Ralph's Phase 4 prompt as concrete acceptance criteria.

### Classification heuristic (single section — do not scatter the logic)

Compute two scores from the user's request + a brief initial repo grep.

```
# trivial threshold = 3: 5개 신호 중 과반(50% 초과) 충족 시 trivial 분류 — 명확한 다수결
# full 신호 가중치 ×2: 구조적 변경(schema/API/cross-file)은 단순 패턴 신호보다 정책 영향이 크므로 가중
# full threshold = 4: 가중치 +2 신호 2개만으로도 도달 — 단 하나의 강한 구조적 신호도 full 강제 가능
# diff < 50 lines: 단일 함수/변수 수정 수준 (한 화면 내 검토 가능) — 경험적 기준

trivial 신호 (각 +1; 누적 ≥ 3 → trivial):
  - 단일 파일 수정 의도 (사용자 발언에 1 file path만 있고 cross-file 언급 없음)
  - diff 예상 < 50 lines (typo, color value, 임계값 1개 등)
  - JIRA-ID 미언급 (PROJ-NNN 형태 없음)
  - 새 추상화 (class / function / file) 도입 안 함
  - 외부 인터페이스 / 스키마 영향 없음 (purely internal detail)

full-pipeline 신호 (각 +2; 누적 ≥ 4 → full):
  - cross-file refactor 또는 ≥3 file 변경 의도
  - JIRA-ID 명시 (PROJ-NNN 형태)
  - 사용자 발언에 "기능 추가 / feat / 새로 / refactor / migrate / 통합 / merge" 류 키워드
  - schema / API / migration / DB / 인프라 변경 신호
  - 새 파일 생성 또는 의존성 추가
  - 메타 / 설계 / 문서 작업 (ADR, integration design 등 — Design/Meta 카테고리)
```

### Decision logic

```
if trivial_score >= 3 AND full_score < 4:
    mode = "TRIVIAL"        # → skip wf, go straight to Phase 2
elif full_score >= 4:
    mode = "FULL"           # → run wf:analyze → plan → execute → qa → record, then Phase 2
else:
    # ambiguous (둘 다 약하거나 둘 다 강함)
    mode = ASK_USER         # one-shot AskUserQuestion override
    # default-on-uncertainty = "FULL" (안전 쪽 — 시간 약간 더 들지만 품질 보장)
```

### TRIVIAL flow

No wf skills are invoked. Proceed to Phase 2 with no wf artifacts. The Ralph Loop's own Reviewer + QA + Acceptance Criteria are sufficient for trivial work.

### FULL flow

Run the wf pipeline before composing the Ralph prompt. Each wf skill is invoked as a Skill (not as a sub-agent — wf skills are user-invocable):

```
1. Skill(wf:analyze)   → produces [ISSUE_ID]_REPORT.md
                          (wf-review-gate.sh hook auto-spawns wf:wf-review-analyze; iterate until LGTM)

2. Skill(wf:plan)      → produces [FEATURE]_PLAN.md
                          (hook auto-spawns wf:wf-review-plan; iterate until LGTM)

3. Skill(wf:execute)   → produces code changes + AC Achievement Report
                          (Phase 7.5 internally spawns wf:qa; resumes only when wf:qa returns PASS)

4. Skill(wf:record)    → produces README / CHANGELOG / ARCHITECTURE updates
                          (hook auto-spawns wf:wf-review-record on CHANGELOG.md write)
```

After `wf:record` exits cleanly, return to Phase 2 with the following artifacts available as Phase 4 prompt context:

- `[ISSUE_ID]_REPORT.md` — root cause + reproduction (informs Constraints + Steps)
- `[FEATURE]_PLAN.md` — task breakdown + success criteria (informs Acceptance Criteria L1)
- `[ISSUE_ID]_QA.md` — independently-verified PASS verdict (becomes a Phase 4 reference, not a re-test)
- The actual git diff from execute (informs scope of L2 Reviewer review)

The Ralph Loop's own Phase 2-5 still runs after this — it's not redundant. wf produces the *first-pass* implementation; Ralph's iteration is for whatever residual cycles are needed (additional acceptance criteria, persona checks, follow-up tweaks).

### Ambiguous → AskUserQuestion

When neither score dominates, ask once:

```
"이 작업이 새 wf 풀 파이프라인을 거쳐야 할지 모호합니다. 어떻게 진행할까요?
  - FULL: wf 5단계 (analyze → plan → execute → qa → record) 후 ralph
  - TRIVIAL: ralph 직행
  - 자세히: 점수 계산 결과를 보여줘"
```

If the user picks "자세히", show the trivial_score / full_score breakdown with which signals fired, then ask again.

### Edge case: graceful degradation

If `wf` plugin is not installed (Skill resolution fails for `wf:analyze`), output:

```
⚠️ wf plugin not available — falling back to TRIVIAL flow. Install the wf plugin
   for automatic full-pipeline dispatch on complex tasks.
```

…and proceed to Phase 2 directly. Do not block the Ralph Loop on missing wf.

### Anti-pattern: scattered dispatch logic

Do **not** sprinkle if-then dispatch checks throughout other phases. The classification + decision must live entirely in this single section so future Workers can find and tune it in one place.

---

## Phase 2: Team Composition

Detect task type from clarified input + initial repo grep. Pick the default team from the matrix below.

**Mandatory in every task** (never skip):
- **Worker** — main Ralph Loop session
- **Reviewer** — `ralph-reviewer` agent (Level 2 verdict)
- **QA** — `ralph-qa` agent (Level 1 + Level 3 verdicts)

The Reviewer/QA gating is the entire mechanism that prevents the Worker from self-approving completion. They are non-negotiable.

### Default teams by task type

| Task type | Default team | Common custom additions (when triggered) |
|-----------|-------------|----------------------------------------|
| Refactoring | Worker, Reviewer, QA | Architecture-Reviewer (large structural moves) |
| Bug Fix | Worker, Reviewer, QA | Reproducer (complex env reproduction) |
| Feature Addition | Worker, Reviewer, QA | API-Designer, Test-Writer |
| Infra | Worker, Reviewer, QA | Cost-Auditor, Security-Reviewer |
| Documentation | Worker, Reviewer, QA | Reader-Persona |
| Test Writing | Worker, Reviewer, QA | — |
| **Design / Meta** (ADR, integration design, workflow redesign) | Worker, Reviewer, QA | Domain-Expert, Reader-Persona |
| **Integration / Migration** (merging modules/skills, staged migration plans) | Worker, Reviewer, QA | Domain-Expert (when multiple domain rules collide) |

### Custom role triggers

- Infra + cost-sensitive resource (RDS, ElastiCache, NAT) → **Cost-Auditor**
- Infra + IAM / SG / public endpoint change → **Security-Reviewer**
- Docs with named target reader → **Reader-Persona**
- Design/meta work where deep domain rules drive correctness (e.g., multiple existing skills' contracts must be preserved) → **Domain-Expert**
- Anything user-specified that isn't covered

### Workflow

1. Show proposed team to user with rationale (why these custom roles, if any).
2. User confirms or edits.
3. The confirmed team is embedded into Phase 4's Iteration Workflow section.

Detailed templates and custom-role definition syntax: see `references/team-composition.md`.

---

## Phase 3: Acceptance Criteria

Define criteria across 3 levels. Conditional enforcement prevents fake criteria.

### Level definitions

| Level | Name | Judge | Method |
|-------|------|-------|--------|
| **L1** | Concrete | `ralph-qa` | Run command, compare exit code/output (binary) |
| **L2** | Structural | `ralph-reviewer` | Read code/diff, judge patterns |
| **L3** | Holistic | `ralph-qa` | Read artifact as a human, judge perception |

### Activation rules (conditional)

```
L1: ALWAYS — at least one criterion required

L2:
  files_changed == 1 AND no_new_abstraction AND no_design_artifact
    → SKIP
  else
    → REQUIRED

  (Design/meta work almost always introduces a "structural surface" — sections, decisions,
   alternatives, dependency relationships — even when only 1 file changes. That counts as
   design_artifact and keeps L2 active.)

L3:
  any artifact in the change has a human reader?
    docs / README / wiki / ADR / design docs      → REQUIRED
    UI copy, error messages, API response text    → REQUIRED
    public API signatures / naming                → REQUIRED
    pure internal implementation detail only      → SKIP
```

### Workflow

1. Compute activation per the rules above.
2. Draft criteria for each active level (use the authoring guides in `references/acceptance-criteria.md`).
3. Show activated levels and criteria to user for confirmation.
4. **Trust the SKIP outcomes** — an empty level is far safer than a fake criterion. Do not invent L2/L3 criteria for trivial fixes just to fill the section.

Anti-patterns and exhaustive ✅/❌ examples per level: `references/acceptance-criteria.md`.

---

## Phase 4: Compose

Generate the prompt using the template in `references/prompt-template.md`. Required sections:

1. **Context** — current state, why the work is needed
2. **Objective** — measurable goal
3. **Team Roster** — all agents from Phase 2 with spawn syntax
4. **Acceptance Criteria** — all active levels from Phase 3 (mark SKIPped levels as `N/A` with reason)
5. **Constraints** — scope limits, untouchable areas
6. **Steps** — ordered actions per iteration
7. **Iteration Workflow** — mandatory Reviewer/QA spawn + verdict gate (the section that prevents self-approval)
8. **Completion** — single gated promise emission

### Storage convention (MANDATORY — absolute paths + per-slug subdirectory)

Every file produced by a single Ralph Loop run is stored under a dedicated subdirectory:

```
<PROJECT_ROOT>/.ralph/<slug>/
├── prompt.md                  # the composed prompt (Worker re-reads this each iteration)
├── review-{N}.md              # Reviewer agent output, one per iteration
├── qa-{N}.md                  # QA agent output, one per iteration
└── <custom-role>-{N}.md       # any custom-role outputs (cost-{N}.md, domain-{N}.md, …)
```

The session-level sentinel `<PROJECT_ROOT>/.ralph/.report-pending` stays at the top level — it represents "this Claude session owes a Phase 6 report", not "this run".

**Why a file (not inline `$ARGUMENTS`) for the prompt:**

- `/ralph-loop`'s setup script receives the prompt via `$ARGUMENTS`, which goes through shell word-splitting. Multi-line prompts or prompts with backticks / quotes / `$` / `!` break parsing and fail the command entirely.
- A file pointer is single-line, shell-safe, and makes the full prompt re-readable every iteration.
- An **absolute path** (anchored to the captured `PROJECT_ROOT`) survives any `cd` the Worker performs during the loop. CWD-relative paths break as soon as Ralph dives into a sub-directory.

**Why a per-slug subdirectory (not flat files at `.ralph/`):**

- Multiple Ralph Loop runs over the lifetime of a repo would otherwise overwrite each other's `review-1.md`, `qa-1.md`, etc. After a few runs nobody can tell which file belongs to which task.
- Subdirectory isolation keeps every run's logs inspectable indefinitely (useful for "wait, what did the auth refactor's iteration 4 reviewer actually say?").
- `.ralph/` is gitignored, so subdir count growth is harmless.

**Slug rules:**
- Derive from task: kebab-case, ≤ 40 chars, no spaces/special chars, no trailing `-prompt` (the slug is now a directory name, not a filename).
- Examples: `alembic-chain-repair`, `auth-middleware-rewrite`, `ARK-1337`, `skill-A-B-merge-adr`.
- If the task has a JIRA ID (PROJ-XXX), prefer that as the slug.
- If unsure, ask the user or pick a 2–4 word summary of the objective.
- The directory `.ralph/<slug>/` is created in Phase 5 step 1 (`mkdir -p`) before any file is written.

Phase 5 captures `PROJECT_ROOT`, creates `.ralph/<slug>/`, writes `prompt.md` inside it, then invokes `/ralph-loop` with only the pointer + options. The chosen absolute path is embedded into the Iteration Workflow block so Reviewer/QA read the same file regardless of their spawn CWD.

### Iteration Workflow block (always include verbatim — substitute `{PROMPT_PATH}`, `{RUN_DIR}`, `{PROJECT_ROOT}` with the concrete absolute paths)

```markdown
## Iteration Workflow (Mandatory)
각 iteration 끝에 다음을 순서대로 수행:

1. Worker가 `{PROMPT_PATH}` (절대경로)를 읽고 위 Steps를 진행, git diff에 변경 반영
2. Spawn Reviewer:
   Agent(subagent_type: "ralph-reviewer", prompt: "iteration={N}, prompt_path='{PROMPT_PATH}', output_path='{RUN_DIR}/review-{N}.md', diff_command='git diff', previous_review_path='{RUN_DIR}/review-{N-1}.md'")
   → 결과를 {RUN_DIR}/review-{N}.md로 저장
3. Spawn QA:
   Agent(subagent_type: "ralph-qa", prompt: "iteration={N}, prompt_path='{PROMPT_PATH}', output_path='{RUN_DIR}/qa-{N}.md', level1_checks=<L1 명령어 목록>, level3_targets=<L3 페르소나/대상>, previous_qa_path='{RUN_DIR}/qa-{N-1}.md'")
   → 결과를 {RUN_DIR}/qa-{N}.md로 저장
4. {커스텀 agent 호출 — 있을 경우, output_path='{RUN_DIR}/<custom-role>-{N}.md'}
5. 판정 게이트:
   - Reviewer == LGTM AND QA == PASS {AND 커스텀 verdict 모두 통과} AND 모든 Acceptance Criteria 충족
     → 이 iteration의 **같은 메시지 안에** 순서대로:
       a. Phase 6 보고서(`## Ralph Loop 실행 결과` 블록) 작성
       b. `rm "{PROJECT_ROOT}/.ralph/.report-pending"` 실행 (report-gate hook sentinel 제거 — sentinel은 top-level 유지)
       c. `<promise>{COMPLETION_PROMISE}</promise>` emit
     셋 중 하나라도 빠지면 run-ralph 플러그인의 Stop hook이 Stop을 block하고 재주입함.
   - 그 외 → 다음 iteration에서 수정. promise emit 절대 금지.
6. 최신 review/qa 파일이 없거나 outdated면 promise emit 금지 (강제력).
```

`{PROMPT_PATH}` (예: `<PROJECT_ROOT>/.ralph/<slug>/prompt.md`), `{RUN_DIR}` (예: `<PROJECT_ROOT>/.ralph/<slug>`), `{PROJECT_ROOT}` 세 placeholder 모두 Phase 5에서 캡처한 구체 절대경로로 치환 후 파일에 기록한다. 저장된 프롬프트에 literal placeholder가 남아있으면 안 된다.

### Repo-specific constraints (template)

Reflect repo characteristics in the Constraints section. Each repo's full architecture rules already live in project rules (e.g. `.claude/rules/architecture.md`); only include rules that matter during repeated execution. Examples of what to capture:

- **Layer/import direction rules** that the Worker must respect every iteration (e.g. `domain → application → infrastructure → presentation`).
- **Required end-of-iteration commands** (e.g. `make fmt && make validate`, `pnpm build`, alembic chain check).
- **Forbidden actions** (e.g. direct `terraform apply`, editing tfstate, modifying agent system prompts in `workspace/CLAUDE.md`).
- **Convention-specific bans** the codebase already enforces (e.g. "no `useMemo`/`useCallback` because React Compiler is on", "no direct `process.env`, use `@infra/config/env`").
- **Scope-of-ownership boundaries** in monorepos (e.g. service-specific chart owners — stop if work crosses owned domain).
- **Design/meta-work constraints** (when the artifact is a design document, ADR, or integration plan): required ADR template sections, terminology that must align with an existing glossary, mandatory references to prior decisions, "do not write code in this iteration — design only".

Lift only the rules whose violation would cost the Worker an iteration to undo. Static documentation belongs in `architecture.md`, not in this prompt.

### Auto-determined options

| Option | Decision rule |
|--------|--------------|
| `--max-iterations` | Simple fix: 5–10, Feature: 10–20, Complex: 20–40 |
| `--completion-promise` | Phrase emitted when all criteria + verdicts pass (always set) |

---

## Phase 5: Execute

### Confirmation

Show the generated prompt + summary to user (absolute prompt path included):

```
📋 생성된 Ralph Loop 프롬프트
- 이번 run의 작업 디렉토리: <PROJECT_ROOT>/.ralph/<slug>/
- 저장될 파일들:
  - prompt.md           (이 프롬프트)
  - review-{N}.md       (각 iteration의 Reviewer 출력)
  - qa-{N}.md           (각 iteration의 QA 출력)
  - <custom-role>-{N}.md (있을 경우)

---
[프롬프트 전문]
---

👥 팀:
- Worker (이 세션)
- Reviewer: ralph-reviewer
- QA: ralph-qa
- {커스텀 역할 — 있을 경우}

✅ 활성 Acceptance Levels:
- L1: {N}개 기준
- L2: {활성 / SKIP — 사유}
- L3: {활성 / SKIP — 사유}

⚙️ 옵션:
- max-iterations: {N}
- completion-promise: "{PROMISE}"

이대로 실행할까요? 수정할 부분이 있으면 말씀해주세요.
```

### Invocation

After user approval, run these **four steps in order** (step 0 captures the project root so all subsequent paths are absolute and CWD-robust):

0. **Capture project root and define the run directory** so every subsequent path is absolute and survives any `cd` during the loop:

   ```
   Bash: PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"; echo "$PROJECT_ROOT"
   ```

   Read the printed path. Compute `RUN_DIR="$PROJECT_ROOT/.ralph/<slug>"` (slug derived per Phase 4 rules). Substitute `{PROJECT_ROOT}`, `{RUN_DIR}`, and `{PROMPT_PATH}="$RUN_DIR/prompt.md"` into the composed prompt (Iteration Workflow block, completion step, every review/qa/custom path). After substitution, no literal placeholders should remain inside the prompt body.

1. **Create the run directory and write the prompt file at the absolute path** (full multi-line content, shell-safe because Write never touches a shell):

   ```
   Bash: mkdir -p "$PROJECT_ROOT/.ralph/<slug>"
   Write(file_path: "<PROJECT_ROOT>/.ralph/<slug>/prompt.md", content: "<full composed prompt>")
   ```

2. **Touch the session-level Stop-gate sentinels at the top of `.ralph/`** so the run-ralph hooks know this session owes a Phase 6 report and (potentially) a record/CHANGELOG update. Both sentinels stay at `.ralph/` top level (NOT inside the slug subdirectory) — the hooks check fixed paths:

   ```
   Bash: touch "$PROJECT_ROOT/.ralph/.report-pending" "$PROJECT_ROOT/.ralph/.record-pending"
   ```

   Two sentinels, two gates:
   - **`.report-pending`** — `run-ralph-report-gate.sh` blocks Stop until Phase 6 report is written + sentinel removed.
   - **`.record-pending`** — `run-ralph-record-gate.sh` blocks Stop when the branch has code commits ahead of `origin/{base}` but no CHANGELOG.md / changelogs/v*.md change. The hook does its own `git diff` check, so doc-only / experiment-only runs pass silently. `wf:record` skill (recommended) or a manual CHANGELOG edit clears it; if record is genuinely not applicable, `rm` the sentinel.

3. **`cd` to PROJECT_ROOT, then invoke `/ralph-loop` with a short pointer prompt** (single-line, no backticks / `$` / newlines). The pointer text itself is Korean per the authoring conventions:

   ```
   Bash: cd "$PROJECT_ROOT"
   Skill(
     skill: "ralph-loop:ralph-loop",
     args: "<PROJECT_ROOT>/.ralph/<slug>/prompt.md 파일을 읽고 그 안의 Ralph Loop 작업을 수행하세요. Iteration Workflow를 그대로 따르고, 모든 게이트가 통과했을 때만 completion promise를 emit 하세요. --max-iterations {N} --completion-promise '{PROMISE}'"
   )
   ```

**Why this split:** `/ralph-loop`'s setup script passes `$ARGUMENTS` through shell word-splitting. Embedding the full multi-line prompt inline causes `Shell command failed for pattern` errors. Writing the prompt to a file first and passing only a pointer sidesteps this entirely — the pointer is the string re-fed each iteration, and the Worker reads the real content from the file. The sentinel is a separate concern — it exists so the run-ralph plugin's Stop hook can distinguish "run-ralph session owes a report" from "regular session, nothing to enforce." `cd "$PROJECT_ROOT"` immediately before `/ralph-loop` normalizes the launch CWD so `/ralph-loop`'s own state file (`.claude/ralph-loop.local.md`) lands at the project root where our hook expects it.

**Pointer prompt rules:**
- Must name the **absolute** file path (the same `<PROJECT_ROOT>/.ralph/<slug>/prompt.md` written in step 1).
- No special shell characters: no backticks, no `$`, no `!`, no newlines, no unescaped quotes.
- Keep it to one sentence — it's what Ralph re-injects on every iteration, so shorter = cleaner.

---

## Phase 6: Report

**Mandatory.** Before emitting `<promise>…</promise>`, **within the SAME final iteration message**, the Worker must write a Phase 6 report. Do NOT end the session with a terse completion-promise echo. The user ran a multi-iteration loop in the background and needs to know what actually landed without having to diff the repo themselves.

**Timing is the subtle part:** `/ralph-loop`'s stop-hook gates the session. When the Worker emits the completion promise, the hook detects it, deletes the state file, and allows Stop — the session ends. There is no "post-loop turn." So the report must be placed *above* the `<promise>…</promise>` tag in the same final message, not written afterwards.

**Order within the final message:**
1. Write the `## Ralph Loop 실행 결과` report block (format below).
2. **Decide on record (documentation):**
   - If the run produced code or config changes (anything outside `*.md` / `changelogs/` / `.ralph/` / `docs/`), invoke `Skill(skill: "wf:record")` BEFORE proceeding. `wf:record` updates README/CHANGELOG/ARCHITECTURE/CLAUDE.md as a single coherent commit and removes `.ralph/.record-pending` itself on success.
   - If the run is doc-only or genuinely doesn't need a record (experiment, .ralph cleanup, hotfix that will be amended), explicitly remove `.ralph/.record-pending` with a one-line justification noted in the Phase 6 report so the audit trail is honest.
3. `rm "$PROJECT_ROOT/.ralph/.report-pending"` to clear the report sentinel so `run-ralph-report-gate.sh` exits cleanly. Use the absolute path — Worker may have `cd`d during the loop.
4. Emit `<promise>{COMPLETION_PROMISE}</promise>`.

> **Why both gates:** `run-ralph-report-gate.sh` enforces the human-readable "what just happened" report (so the user is never left to reconstruct it from `git diff`). `run-ralph-record-gate.sh` enforces the project-level documentation sync (CHANGELOG / README / ARCHITECTURE consistent with the code). Without the second gate, the most common failure mode is "code shipped, CHANGELOG forgotten" — silent doc drift that compounds across runs.

If any of these is skipped, the run-ralph plugin's Stop hook will block Stop and re-inject a reminder.

### Collect evidence first

Before writing the report, gather the ground truth — don't rely on what Ralph "said" it did:

1. **Outcome** — Did the loop emit the completion promise, or hit `--max-iterations`? Check the last iteration's output.
2. **Iteration count** — Read the highest `N` in `$PROJECT_ROOT/.ralph/<slug>/review-{N}.md` / `$PROJECT_ROOT/.ralph/<slug>/qa-{N}.md`.
3. **Final verdicts** — Read the last `$PROJECT_ROOT/.ralph/<slug>/review-{N}.md` and `$PROJECT_ROOT/.ralph/<slug>/qa-{N}.md`. If QA FAILed or Reviewer said REVISE on the last iteration, the loop exited without passing — say so explicitly.
4. **Actual changes** — `git status` + `git diff --stat` (and `git log` if new commits were made). Do not list files from memory.
5. **Acceptance criteria status** — For each active L1/L2/L3 criterion, map it to what the final QA/Reviewer actually checked. Mark any that were skipped / deferred / fudged.

### Report structure (Korean, user-facing)

```markdown
## Ralph Loop 실행 결과

**결과**: {완료 / max-iterations 도달 / 중단} — {한 줄 근거}
**Iteration**: 총 {N}회
**최종 판정**: Reviewer={LGTM/REVISE}, QA={PASS/FAIL}{, 커스텀 역할 있으면 같이}

### 무엇을 했나
- {실제로 변경된 파일/모듈을 bullet로. git diff --stat 기반, 추측 금지}
- {주요 로직 변경 한 줄 요약 — "왜" 바꿨는지 포함}

### Acceptance Criteria 충족 여부
- L1: {충족 항목 / 미충족 항목 — 각 기준별 O/X}
- L2: {판정 근거 한 줄. SKIP이었으면 SKIP 사유 재확인}
- L3: {판정 근거 한 줄. SKIP이었으면 SKIP 사유 재확인}

### 남은 작업 / 주의사항
- {max-iterations로 끝났거나 미해결 이슈가 있으면 여기. 없으면 "없음"}
- {사용자가 직접 확인해야 할 부분 — 예: 수동 테스트 필요, 배포 전 리뷰 필요}

### 산출물 위치
- 이번 run의 작업 디렉토리: `<PROJECT_ROOT>/.ralph/<slug>/`
- 변경: `git diff` / 커밋 {있으면 해시}
- Reviewer 로그: `<PROJECT_ROOT>/.ralph/<slug>/review-{N}.md` (N=1..최종)
- QA 로그: `<PROJECT_ROOT>/.ralph/<slug>/qa-{N}.md`
- 커스텀 역할 로그: `<PROJECT_ROOT>/.ralph/<slug>/<role>-{N}.md` (있을 경우)
- 원본 프롬프트: `<PROJECT_ROOT>/.ralph/<slug>/prompt.md`
```

### Rules

- **No fabrication.** Every bullet under "무엇을 했나" must be backed by `git diff` / `git log` output you actually read this turn. If you can't show it, don't claim it.
- **Acknowledge failure honestly.** If the loop hit max-iterations without passing, lead with that — don't bury it. The user needs to decide whether to re-run, adjust criteria, or abandon.
- **Don't re-paste the full diff.** Summarize. The user can read `git diff` themselves; your job is to tell them *what changed and why* so they know whether it's worth reading.
- **Keep it scoped to this run.** Don't re-explain the original task or team composition — the user was there for Phase 1–5. This phase is purely "what happened after I handed off to `/ralph-loop`."

### Stop hook safety nets (report + record)

The Phase 6 instructions above are the primary path. Two Stop hooks act as mechanical safety nets if a step is skipped:

#### (1) `run-ralph-report-gate.sh`

The Phase 6 instruction above is the primary path. The plugin's Stop hook is the secondary, mechanical safety net.

- **Script**: `${CLAUDE_PLUGIN_ROOT}/hooks/run-ralph-report-gate.sh` (bundled with this plugin).
- **Registered in**: `${CLAUDE_PLUGIN_ROOT}/hooks/hooks.json` — Stop event, matcher `*`. Auto-loads when the `run-ralph` plugin is installed; no per-project `.claude/settings.json` edit needed.
- **What it does** (all checks use `${CLAUDE_PROJECT_DIR}` — CWD-independent):
  - `${CLAUDE_PROJECT_DIR}/.claude/ralph-loop.local.md` **exists** → `/ralph-loop` is still iterating. Hook exits 0; ralph-loop plugin's own Stop hook handles continuation.
  - `${CLAUDE_PROJECT_DIR}/.ralph/.report-pending` **absent** → not a run-ralph session (or Phase 6 already cleaned up). Hook exits 0.
  - **otherwise** → ralph ended AND report sentinel still present → hook blocks Stop and injects a Korean prompt telling the Worker to write the Phase 6 report and `rm "$PROJECT_ROOT/.ralph/.report-pending"`.
- **Why the sentinel lives at `.ralph/.report-pending` (not inside `.ralph/<slug>/`)**: a single Claude session only runs one choo-choo at a time, so a session-level sentinel is sufficient. Keeping it at a fixed top-level path means the Stop hook checks one file (cheap, no glob), regardless of which slug is currently running. Per-run artifacts (prompt, review, qa) are isolated under `.ralph/<slug>/` for inspection longevity; the sentinel is orthogonal to that.
- **Sentinel lifecycle** (don't touch it from anywhere else):
  - Created by Phase 5 step 2 (`touch "$PROJECT_ROOT/.ralph/.report-pending"`).
  - Removed by Phase 6 step 2 (`rm "$PROJECT_ROOT/.ralph/.report-pending"`) within the final iteration message.
- **Disabling** (if it's ever in the way): disable the `run-ralph` plugin (`/plugin` → uninstall or toggle off). The Phase 6 instruction remains as a weaker fallback.
- **Orphan sentinel recovery**: if a prior run-ralph session crashed and left `.ralph/.report-pending` behind, the next Phase 5 `touch` is idempotent (no-op on existing file) — the new session will clean it up at its own Phase 6. If you want to run anything *other than* run-ralph first and not be bothered, `rm "$(git rev-parse --show-toplevel)/.ralph/.report-pending"` manually.
- **`/cancel-ralph` behavior**: cancelling removes `.claude/ralph-loop.local.md` but not the sentinel. Next Stop → hook fires → Worker must still write a Phase 6 report (a short one explaining the cancellation is acceptable) and remove the sentinel. This is intentional: cancellation is still an "end of run" the user should be told about.

#### (2) `run-ralph-record-gate.sh` (v1.2 신규)

The second Stop hook catches the most common harness-failure: **code shipped without the matching record/CHANGELOG update.**

- **Script**: `${CLAUDE_PLUGIN_ROOT}/hooks/run-ralph-record-gate.sh` (bundled; auto-loaded with the plugin).
- **Sentinel**: `${CLAUDE_PROJECT_DIR}/.ralph/.record-pending` (top level, alongside `.report-pending`).
- **Decision logic** (the gate does its own `git diff` check, so it's *much* quieter than report-gate):
  1. `/ralph-loop` still iterating → defer (exit 0).
  2. `.record-pending` absent → no obligation (exit 0).
  3. Branch has 0 commits ahead of `origin/{base}` → nothing to record yet (exit 0).
  4. Ahead-commits touch only `*.md` / `changelogs/` / `.ralph/` / `docs/` → doc-only run, no obligation (exit 0).
  5. Ahead-commits include `CHANGELOG.md` or `changelogs/v*.md` change → docs already done (exit 0).
  6. Otherwise → real code shipped, CHANGELOG missing → **block Stop** with a Korean instruction to spawn `wf:record` (or `rm` the sentinel + justify in the Phase 6 report).
- **Why both gates?** `report-gate` handles "did the user get told what just happened?" `record-gate` handles "did the project's documentation stay in sync with the code?" They're orthogonal failure modes and both cost only milliseconds per Stop.
- **Sentinel lifecycle**:
  - Created by Phase 5 step 2 (`touch ".../.record-pending"`).
  - Removed by `wf:record` skill on success, or by Phase 6 step 2 if record is genuinely not needed (with justification logged in the report).
- **Disabling**: toggle the `run-ralph` plugin off (`/plugin`). The Phase 6 record-spawn instruction in this SKILL.md remains as a weaker fallback.

---

## Reference files

- **`references/prompt-template.md`** — Full template structure, quality checklist, anti-patterns, clarification questions per task type
- **`references/team-composition.md`** — Team templates by task type, custom role triggers, ad-hoc role definition syntax
- **`references/acceptance-criteria.md`** — 3-level definitions, conditional activation rules, exhaustive ✅/❌ examples per level
- **`references/example-transformation.md`** — Worked examples: vague request → composed prompt for refactor / infra / trivial-fix / **design-ADR (meta work, no code change)** cases

## Reusable agents (bundled with this plugin)

- **`ralph-reviewer`** — Level 2 (Structural) judge. Returns LGTM / REVISE.
- **`ralph-qa`** — Level 1 (Concrete) runner + Level 3 (Holistic) judge. Returns PASS / FAIL.

## Dependency

This skill terminates Phase 5 by invoking `/ralph-loop` (`ralph-loop:ralph-loop`). The `ralph-loop` plugin must be installed and enabled — install it from the `claude-plugins-official` marketplace if it isn't already.
