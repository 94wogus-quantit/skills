# Acceptance Criteria — 3 Levels

Ralph Loop's completion gate. A single dimension of criteria produces partial-success failures: tests pass but the artifact reads badly, or humans approve but a regression slipped in. Three layered levels prevent both.

## Level definitions

| Level | Name | Judge | How | Example |
|-------|------|-------|-----|---------|
| **L1** | Concrete | `ralph-qa` | Run command, compare exit code / output | `pytest` 통과, `grep` 0 hit, 파일 존재 |
| **L2** | Structural | `ralph-reviewer` | Read code/diff, judge patterns | 레이어 위반 없음, 패턴 일관성, 추상화 정합성 |
| **L3** | Holistic | `ralph-qa` | Read artifact as a human, judge perception | "5분 내 이해 가능", "에러 메시지가 다음 행동을 알려줌" |

## Conditional enforcement (when each level is required)

| Level | Required when | Reasoning |
|-------|---------------|-----------|
| **L1** | **Always — at least one criterion** | Without binary checks there is no automated completion gate at all. |
| **L2** | **Conditionally — files changed ≥2 OR new abstraction/module/API introduced** | A one-line single-file edit has no structural surface; forcing L2 spawns fake criteria. |
| **L3** | **Conditionally — the artifact has a human reader (docs, UI copy, error messages, public API names, code intended for review)** | When the work is purely machine-verifiable, perception criteria become rubber-stamps. |

### Auto-decision tree

```
L1: ALWAYS REQUIRED

L2:
  files_changed == 1 AND no_new_abstraction
    → SKIP
  else
    → REQUIRED

L3:
  any artifact in the change has a human reader?
    docs (.md, README, CHANGELOG, wiki)         → YES → REQUIRED
    UI copy, error messages, API response text  → YES → REQUIRED
    public API signatures / naming              → YES → REQUIRED (other devs read these)
    pure internal implementation detail         → NO  → SKIP
```

The activated levels are shown to the user during Phase 2 (Compose) for confirmation.

---

## Level 1: Concrete — authoring guide

**Principle**: A single shell command must determine PASS/FAIL.

### ✅ Good examples

```bash
# Test execution
pytest tests/auth/ -v                          # exit 0
pnpm test --filter "auth/*"                    # exit 0
make test                                       # exit 0

# Negative grep (something must be gone)
rg "verify_jwt" src/presentation/routes/        # 0 hits
rg "TODO\(deprecated\)" src/                    # 0 hits

# Positive grep (something must exist)
rg "class AuthMiddleware" src/                  # exactly 1
rg "X-Internal-Secret" src/ | wc -l             # 0 (legacy fully removed)

# Build / typecheck
pnpm build                                      # exit 0, no warnings
make validate                                   # exit 0
mypy src/                                       # exit 0

# File state
test -f alembic/versions/abc123_*.py
test ! -f src/legacy/old_auth.py

# DB state (after migration)
docker exec api psql -c "\d auth_session" | grep -q "session_token"
```

### ❌ Bad examples

```text
"인증 로직이 깔끔해진다"               # 주관적, 자동 검증 불가
"성능이 개선된다"                       # 수치 없음
"middleware로 통합됨"                   # 검증 명령어 없음 — 무엇을 어떻게 확인?
"테스트가 대부분 통과"                  # 모호 — 몇 개 중 몇 개?
"기존보다 좋아짐"                       # 비교 기준 없음
```

### L1 authoring checklist

- [ ] Each item carries an exact shell command and an exact expected result.
- [ ] Only binary comparisons are used: "0 hits", "exit 0", "exactly N".
- [ ] QA can run the command in an environment that never saw the Worker's reasoning.
- [ ] Each command finishes in ≤30 seconds (long-running checks need separate handling).

---

## Level 2: Structural — authoring guide

**Principle**: Pattern-level consistency and integrity. Reviewer reads the diff and judges.

### ✅ Good examples

```text
- 모든 protected route가 `Depends(get_current_user)` 패턴 사용 (믹스 없음)
- AuthMiddleware는 SRP 준수: 토큰 검증만 수행, 권한 체크는 별도 dependency
- 신규 도입한 `BaseHandler` 추상화가 모든 신규 핸들러에 적용됨 (일부만 적용된 부분 없음)
- `domain/` 레이어에 외부 의존성 import 0건 (architecture rule 준수)
- 제거된 legacy auth 함수가 import / 호출 / 주석 어디에도 흔적 없음
- 새 도메인 모델 `AuthSession`이 application/, infrastructure/에서 일관된 매핑 패턴으로 사용됨
```

### ❌ Bad examples

```text
"코드가 깔끔하다"                  # 모호 — Reviewer가 PASS/REVISE 판정 불가
"좋은 설계다"                       # 동일
"패턴을 잘 따른다"                  # 어떤 패턴인지 정의 없음
"pytest가 통과한다"                 # L1 영역 침범 — L1으로 이동
"grep 결과 0개"                     # L1 영역 침범 — L1으로 이동
"이해하기 쉽다"                     # L3 영역 침범 — L3으로 이동
```

### L2 authoring checklist

- [ ] Each item names a pattern/structural property that is directly observable in the diff.
- [ ] When the form is "follows X pattern", X is defined in the prompt or in `architecture.md`.
- [ ] Reviewer can read the diff and emit PASS/REVISE — no human judgment beyond pattern matching.
- [ ] Anything verifiable by a single command was moved to L1.

---

## Level 3: Holistic — authoring guide

**Principle**: A human reads the artifact and forms a perception judgment. QA judges.

This level is the most dangerous — vague criteria become rubber-stamps. Every L3 criterion MUST specify:

1. **Persona** — who reads it
2. **Outcome** — what that person can do/think after reading
3. **Verification** — how QA simulates the persona

### ✅ Good examples

```text
- Persona: 이 코드베이스를 처음 보는 백엔드 개발자
  Outcome: README.md를 읽고 5분 내에 "auth는 middleware에서 단방향으로 처리된다"는 mental model 형성
  Verification: QA가 해당 페르소나로 readme를 처음부터 끝까지 읽고 self-report

- Persona: API 호출 후 401을 받은 사용자(개발자)
  Outcome: 에러 메시지를 본 직후 "토큰을 다시 발급받아야 한다"는 다음 행동을 인지
  Verification: 에러 메시지 텍스트만 단독으로 보고도 다음 행동을 자연어로 기술 가능한가

- Persona: 1년 후 이 PR을 다시 보는 작성자
  Outcome: 함수명/주석만으로 "왜 이렇게 했는가"의 핵심 의도를 떠올릴 수 있음
  Verification: 함수 시그니처와 주석만 발췌해 읽었을 때 의도가 self-evident
```

### ❌ Bad examples

```text
"코드가 명확하다"                                  # 누가 평가하는가 (persona 없음)
"문서가 잘 쓰여있다"                                # 동일
"가독성이 좋다"                                     # outcome 없음
"자연스러운 흐름"                                   # 동일
"우아하다", "깔끔하다", "직관적이다"                # 추상명사 — 검증 불가능
"사용자가 layout shift를 인지하지 못한다"
  (skeleton 높이 148px 픽스 작업에)               # 작업 목적과 무관 — L1(스크린샷 비교)에서 처리할 일
```

### L3 authoring checklist

- [ ] Persona is concrete ("처음 합류한 백엔드 개발자" — not "개발자").
- [ ] Outcome is described as an action or thought (not a feeling).
- [ ] QA can plausibly simulate the persona.
- [ ] The criterion only appears when the work's purpose actually involves perception (no padding).

---

## Iteration workflow (how the levels combine)

```
[Iteration N start]
   ↓
Worker: advance one unmet criterion (edit code)
   ↓
Spawn Reviewer (sub-agent, fresh context)
   → reads diff, evaluates L2 → .ralph/review-N.md → LGTM or REVISE
   ↓
Spawn QA (sub-agent, fresh context)
   → runs L1 commands + judges L3 personas → .ralph/qa-N.md → PASS or FAIL
   ↓
Reviewer == LGTM AND QA == PASS?
   YES → all criteria met across all active levels? → if YES emit <promise>, else next iteration
   NO  → read REVISE/FAIL feedback, address in next iteration
```

**Single completion gate**: emit the promise only when every criterion of every active level is PASS/LGTM AND the latest Reviewer + QA verdicts are LGTM/PASS. No partial-credit completion.

---

## Anti-pattern: enforcing all levels by reflex

Bad — applying all three levels to a trivial single-line fix:

```markdown
## L1
- skeleton 높이가 148px

## L2
- 컴포넌트 패턴 일관성    ← 1줄 수정에 무의미

## L3
- 사용자가 layout shift를 인지하지 못한다    ← rubber-stamp 확정
```

Result: L2/L3 become fake criteria. Reviewer/QA give formal PASS without real evaluation → self-approval problem returns.

Correct:

```markdown
## L1 (always)
- skeleton 높이 148px
- pnpm build 통과

## L2 (skip — single-file edit, no new abstraction)
N/A

## L3 (skip — internal visual detail, no human-read artifact)
N/A
```

Trust the conditional rules. **An empty level is far safer than a fake criterion.**
