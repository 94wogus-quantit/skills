# Personal Claude Code Plugins

Claude Code의 확장 기능(Plugins)을 모아둔 저장소입니다. Skills를 중심으로 체계적인 개발 워크플로우를 지원합니다.

## 🔌 Plugin이란?

**Plugin**은 Claude Code를 확장하는 모든 기능의 총칭입니다:

- **🤖 Skills**: AI 기반 워크플로우 오케스트레이터 (분석, 계획, 실행, 문서화 등)
- **🔧 Agents**: AC (Acceptance Criteria) 추적 자동화 (requirement-validator)
- **🔗 MCP Servers**: 외부 도구/서비스 통합 (seq-think, terraform, amplitude, slack, atlassian, github)

이 저장소는 **Skills + Agents + MCP Servers**를 제공합니다.

> 변경 이력은 [CHANGELOG.md](CHANGELOG.md) 참조.

## 🌐 언어 정책

**모든 스킬은 기본적으로 한국어로 작동합니다.**

- ✅ 모든 문서, 리포트, 계획서는 **한국어**로 생성
- ✅ 사용자 응답과 설명은 **한국어**로 제공
- ✅ 코드 주석과 문서화는 **한국어**로 작성
- 🔄 예외: 사용자가 다른 언어로 작성하면 해당 언어로 응답

이는 모든 스킬에 강제 적용되는 **필수 정책**입니다.

## 🔒 브랜치 보호 정책

workflow-skills는 보호된 브랜치(main, master, staging)에서 직접 작업하는 것을 방지합니다.

### 보호 동작

| Skill | 보호된 브랜치 감지 시 |
|-------|---------------------|
| **analyze** | 새 feature 브랜치 자동 생성 |
| **plan** | 경고 + 권장 워크플로우 안내 |
| **execute** | 경고 (코드 수정 위험 강조) |
| **record** | 경고 (문서 커밋 위험) |

### 권장 워크플로우

```bash
# 1. Feature 브랜치 생성 후 작업
git checkout -b feature/JIRA-123

# 2. 워크플로우 실행 (Skills 사용)
analyze JIRA-123
plan JIRA-123_REPORT.md
execute JIRA-123_PLAN.md
record

# 3. MR 생성 및 리뷰
glab mr create --title "feat: JIRA-123 구현"
```

## 🚀 Getting Started

### 마켓플레이스로 설치 (권장)

1. Claude Code에서 marketplace 추가:
   ```bash
   /marketplace add git@github.com:94wogus-quantit/wogus-plugin.git
   ```

2. 원하는 플러그인 설치:
   ```bash
   # 워크플로우 전체 (5 skills + agent + seq-think)
   /plugin install wogus-plugins:wf

   # 또는 개별 MCP만
   /plugin install wogus-plugins:terraform
   /plugin install wogus-plugins:amplitude
   /plugin install wogus-plugins:slack
   /plugin install wogus-plugins:atlassian
   /plugin install wogus-plugins:github
   ```

3. 설치 확인:
   ```bash
   /plugin list
   ```

4. **MCP 서버 설정** (선택사항):

   일부 MCP 서버는 환경 변수 설정이 필요합니다. **프로젝트 루트**에 `.claude/settings.json` 파일을 생성하세요:

   ```jsonc
   {
     "env": {
       // Context7 - 라이브러리 문서 조회
       "CONTEXT7_API_KEY": "your-api-key-here",

       // Sentry - 에러 트래킹
       "SENTRY_ACCESS_TOKEN": "your-sentry-token-here",
       "SENTRY_HOST": "your-org.sentry.io",
       "OPENAI_API_KEY": "your-openai-api-key-here",  // Sentry AI 분석용

       // Atlassian - JIRA/Confluence 연동
       "ATLASSIAN_URL": "https://your-company.atlassian.net",
       "ATLASSIAN_USERNAME": "your.email@company.com",
       "ATLASSIAN_API_TOKEN": "your-api-token-here",

       // Amplitude - 사용자 행동 분석
       "AMPLITUDE_API_KEY": "your-amplitude-api-key-here",

       // Slack - 메시지 검색/히스토리
       "SLACK_BOT_TOKEN": "xoxb-your-bot-token-here",

       // GitHub - 저장소/이슈/PR 관리
       "GITHUB_TOKEN": "ghp_your-personal-access-token-here"
     }
   }
   ```

   > **참고**: 실제 사용 시 주석(`//`)을 제거하세요. 위 예시는 가독성을 위한 JSONC 형식입니다.

   **주의**: `.claude/settings.json`은 `.gitignore`에 추가하여 민감한 정보가 커밋되지 않도록 하세요.

   - **seq-think**: 별도 설정 없이 자동 동작
   - **context7**: [Context7](https://context7.com)에서 API 키 발급 필요
   - **serena**: 코드 심볼 분석 및 검색 (별도 설정 불필요, uvx 자동 설치)
   - **sentry**: [Sentry](https://sentry.io)에서 액세스 토큰 발급 필요 (+ OpenAI API 키)
   - **atlassian**: uvx 기반 API 토큰 인증 (mcp-atlassian by sooperset)
     - [Atlassian API 토큰 생성](https://id.atlassian.com/manage-profile/security/api-tokens)에서 토큰 발급
     - 3개 환경변수로 간단 설정: `ATLASSIAN_URL`, `ATLASSIAN_USERNAME`, `ATLASSIAN_API_TOKEN`
   - **terraform**: HashiCorp Terraform IaC 자동화 (별도 설정 불필요, Docker 필요)
   - **amplitude**: [Amplitude](https://amplitude.com)에서 API 키 발급 필요
   - **slack**: [Slack API](https://api.slack.com/apps)에서 Bot 토큰 발급 필요
   - **github**: [GitHub Settings](https://github.com/settings/tokens)에서 Personal Access Token 발급 필요

5. **MCP 서버 비활성화** (선택사항):

   특정 MCP 서버를 사용하지 않으려면 Claude Code 내에서 `/mcp` 명령어를 실행하고 원하는 서버를 선택하여 disable할 수 있습니다.

### 로컬 패키징으로 설치

1. 스킬을 패키징하여 `.zip` 파일 생성:
   ```bash
   python3 ~/.claude/plugins/marketplaces/anthropic-agent-skills/skill-creator/scripts/package_skill.py analyze
   ```

2. Claude Code에서 설치:
   ```bash
   /plugin install analyze.zip
   ```

## 💡 Recommended Plugins

**wf:plan** 스킬의 성능을 극대화하려면 Claude 공식 플러그인을 활성화하세요:

### ralph-loop (계획서 자동 반복 검토)

**기능**: 계획서 품질을 자동으로 반복 개선합니다.

**활성화 방법**:

`~/.claude/settings.json`에 추가:
```json
{
  "ralph-loop@claude-plugins-official": true
}
```

**효과**:
- ✅ **ralph-loop 활성화**: wf:plan이 자동으로 반복 검토 루프를 실행하여 계획서 품질을 향상시킵니다
- ⚠️ **ralph-loop 미활성화**: 수동 피드백 적용 방식으로 fallback (여전히 작동하지만 덜 자동화됨)

**권장 대상**: 고품질 계획서가 필요한 복잡한 프로젝트

## 📦 Available Skills

### analyze

버그와 이슈의 근본 원인을 체계적으로 분석하는 스킬입니다.

**주요 기능:**
- JIRA 이슈 및 Sentry 에러 조사
- 다각도 가설 수립 및 검증 (First Principles + 일론 머스크 사고법)
- 코드베이스 탐색을 통한 문제 지점 파악
- 상세한 분석 리포트 자동 생성 (`*_REPORT.md`)
- 브랜치 보호 (main/master/staging 감지 시 feature 브랜치 자동 생성)

**사용 시점:**
- JIRA 이슈나 버그 리포트 분석 시
- Sentry 에러나 프로덕션 인시던트 조사 시
- 복잡한 문제의 근본 원인 분석이 필요할 때

**설치:**
```bash
# Claude Code에 스킬 설치
/plugin install analyze.zip
```

### mr-review

GitLab MR의 코드 변경사항을 분석하여 맥락 기반 종합 리뷰를 수행하는 스킬입니다.

**주요 기능:**
- **7가지 종합 검증**: 아키텍처, 비즈니스 로직, 컨벤션, 이슈 패턴, JIRA 요구사항, 보안, 테스트
- **2개 파일 출력**: `INLINE_DISCUSSION.json` (GitLab 자동화용) + `SUMMARY_COMMENT.md` (요약)
- **범용 보안 스캔**: Trivy로 모든 언어 지원 (JS, Python, Go, Java, Rust 등)
- **Phase별 중간 산출물**: `.mr-review/` 디렉토리에 각 Phase 결과 저장 (Context 손실 방지)
- **MCP 기반 심화 분석**: Sequential Thinking + Serena Context7 + Atlassian 적극 활용

**사용 시점:**
- GitLab MR 코드 리뷰가 필요할 때
- 맥락 기반 종합 리뷰가 필요한 중요한 MR (아키텍처 변경, 신규 기능)
- 프로젝트 문서와 JIRA 요구사항을 종합 검증해야 할 때
- 보안, 품질, 테스트 커버리지를 체계적으로 검증하고 싶을 때

**사용 방법:**
```bash
# 로컬에서 직접 실행
claude-code exec "Use mr-review skill to review this MR. Branch: feature/user-auth"

# 또는 대화형으로
# "mr-review skill로 이 MR 리뷰해줘"
```

**설치:**
```bash
# Claude Code에 스킬 설치
/plugin install mr-review.zip
```

### plan

일론머스크 5단계 알고리즘 기반 사고 방법론과 자동 반복 검토를 통해 고품질 구현 계획을 생성하는 스킬입니다.

**주요 기능:**
- **5단계 알고리즘 기반 계획 수립**: 요구사항 질의 → 삭제 → 단순화 → 가속 → 자동화 순서로 사고
- **Idiot Index**: 계획 비대화 자동 감지 (전체 노력 / 핵심 기능 노력 비율)
- **Zero-Context Plan Writing**: 코드베이스 사전 지식 없이도 실행 가능한 계획 작성
- **반복 리뷰 루프**: 계획 생성 → 검토 → 피드백 반영 (ZERO 이슈까지 자동 반복)
- **11-point 리뷰 체크리스트**: Efficiency & Necessity 항목 포함
- **CARRYOVER/NEW 태깅**: 이전 이슈 추적 + 새로 발견한 이슈 구분
- 모든 태스크에 테스팅 전략 필수 포함
- 태스크 독립성 검증
- 브랜치 보호 (feature 브랜치 확인)

**사용 시점:**
- `*_REPORT.md`에서 구현 계획 생성 시
- 복잡한 기능이나 아키텍처 변경 계획 시
- 실행 전 고신뢰도 계획이 필요할 때
- 품질과 완성도가 속도보다 중요할 때

**설치:**
```bash
# Claude Code에 스킬 설치
/plugin install plan.zip
```

### execute

승인된 구현 계획을 체계적으로 실행하는 스킬입니다.

**주요 기능:**
- TaskList 자동 생성 및 진행 추적
- 9단계 체계적 실행 프로세스
- 자동 테스트 실행 및 검증
- 브랜치 보호 (보호된 브랜치 경고)
- **순수 구현에만 집중** (문서 정리는 record 스킬에서 처리)

**사용 시점:**
- 승인된 `*_PLAN.md` 파일 실행 시
- 체계적인 진행 추적이 필요할 때
- 모든 성공 기준 검증이 필요할 때
- 코드 구현에만 집중하고 싶을 때

**Note**: 문서 업데이트와 파일 정리는 `record` 스킬에서 처리합니다.

**설치:**
```bash
# Claude Code에 스킬 설치
/plugin install execute.zip
```

## 🔧 Available Agents

Agent는 Skills에서 실제로 활용되는 것만 유지합니다.

### requirement-validator (유일하게 유지)

JIRA Acceptance Criteria와 코드를 자동 매핑하여 요구사항 달성 여부를 검증합니다.

**주요 기능:**
- AC ↔ 코드 자동 매핑
- 4가지 실행 모드 (Reverse, Pre, Post, Final)
- 미구현 AC 자동 탐지
- 전체 워크플로우 AC traceability

**사용 시나리오:**
```bash
# 1. 자동 호출 (Skills 통합)
# - analyze에서 자동 호출 (AC 역추적)
# - plan에서 자동 호출 (AC coverage 체크)
# - execute에서 자동 호출 (AC 달성 보고)
# - mr-review에서 자동 호출 (AC 최종 게이트)

# 2. 수동 호출 (Agent 직접 실행)
# Mode 1: 특정 코드가 어떤 AC와 관련되었는지 역추적
"requirement-validator agent로 UserService.ts의 login 함수가 어떤 AC와 관련있는지 찾아줘"

# Mode 2: 계획이 모든 AC를 커버하는지 사전 검증
"requirement-validator agent Mode 2로 FEATURE_PLAN.md의 AC coverage 체크해줘"

# Mode 3: 현재 구현이 AC를 얼마나 충족하는지 확인
"requirement-validator agent Mode 3로 현재 git diff 기준 AC 달성률 보고해줘"

# Mode 4: MR이 AC를 충족하는지 최종 검증
"requirement-validator agent Mode 4로 이 MR이 JIRA-123 AC를 모두 달성했는지 확인해줘"
```

**통합 Skills**: analyze, plan, execute, mr-review

---

### record

워크플로우 아티팩트를 수집하여 프로젝트 문서를 종합적으로 업데이트하는 스킬입니다.

**주요 기능:**
- README, CHANGELOG, CLAUDE 문서 자동 업데이트
- **ARCHITECTURE.md 자동 생성/업데이트** (matklad 패턴: 조감도, 코드맵, 불변성, 횡단 관심사)
- JIRA 이슈에 구현 완료 사항 정리 및 코멘트
- Serena 메모리에 기술 인사이트 저장
- 워크플로우 아티팩트 아카이브/정리
- Git 커밋/푸시
- 브랜치 보호

**사용 시점:**
- **`execute` 완료 후 반드시 실행** (README/CHANGELOG 업데이트)
- 프로젝트 문서화가 필요한 경우
- 아키텍처 결정사항 문서화 시
- 마이그레이션 가이드 생성 시
- git commit 전 최종 문서화

**설치:**
```bash
# Claude Code에 스킬 설치
/plugin install record.zip
```

**워크플로우 통합:**
```
analyze
  → *_REPORT.md 생성
  → plan (자동 반복 검토)
    └─> *_PLAN.md (승인된 계획)
  → execute (코드 구현 및 테스트)
    └─> 구현 완료, 코드 문서화, 파일 정리
  → record (필수: 프로젝트 문서화)
    └─> README, CHANGELOG, CLAUDE 문서, Serena 메모리
```

## 📋 권장 워크플로우

### 표준 워크플로우

```
1. analyze [JIRA/버그 리포트]
   └─> *_REPORT.md 생성
   └─> [Phase 3D] 복잡도 분석 및 리팩토링 가이드 직접 제공 (조건부 필수)
   └─> [Phase 3E] requirement-validator (AC 역추적)

2. plan [REPORT 참조]
   └─> 자동 반복 검토 (계획 → 검토 → 개선 → 재검토...)
   └─> [Step C-2] requirement-validator (AC coverage 검증)
   └─> *_PLAN.md (승인된 고품질 계획)

3. execute [PLAN]
   └─> TaskList 생성 및 실행
   └─> [Phase 4] 코드 구현
   └─> [Phase 4C] DB Migration 검증 (마이그레이션 작업 시)
   └─> [Phase 5] 테스트 직접 생성 - AAA 패턴 (조건부 필수)
   └─> [Phase 6] requirement-validator (AC 달성 보고)
   └─> [Phase 7] 테스트 실행 및 검증

4. record (필수)
   └─> README 업데이트 (기능, API, 설정 등)
   └─> ARCHITECTURE.md 생성/업데이트 (matklad 패턴)
   └─> CHANGELOG 업데이트 (변경 이력)
   └─> CLAUDE 문서 업데이트 (아키텍처 결정사항)
   └─> Serena 메모리 저장 (기술 인사이트)
   └─> JIRA 이슈 업데이트
   └─> 워크플로우 아티팩트 정리 (*_PLAN.md, *_REPORT.md)
```

**중요**:
- `plan`는 자동으로 피드백 루프를 반복하여 고품질 계획을 보장합니다
- `execute`은 코드 구현에, `record`는 문서화에 집중하도록 역할이 분리되어 있습니다

### MR 리뷰 워크플로우

```
mr-review [Branch/MR URL]
├─> Phase 1: 맥락 수집 → .mr-review/1_CONTEXT.md
├─> Phase 2: 코드 분석 → .mr-review/2_CODE_ANALYSIS.md
├─> Phase 3: 보안 분석 (Trivy) → .mr-review/3_SECURITY_ANALYSIS.md
└─> Phase 4: 리포트 생성
    ├─> INLINE_DISCUSSION.json (GitLab Inline Discussion용)
    └─> SUMMARY_COMMENT.md (요약 리포트)

7가지 종합 검증:
1. 아키텍처 일관성
2. 비즈니스 로직 정확성 (JIRA 목표 대비)
3. 컨벤션 준수
4. 과거 이슈 패턴 재발 방지
5. JIRA 요구사항 검증
6. 보안 검토
7. 테스트 커버리지
```


## 📦 설치

Git URL로 직접 설치합니다:

```bash
/plugin install git@github.com:94wogus-quantit/wogus-plugin.git
```

## 📁 Repository Structure

```
wogus-plugin/
├── .claude-plugin/
│   └── marketplace.json       # 카탈로그 (8 plugins)
│
├── plugins/                   # 모든 플러그인
│   ├── wf/                    # 메인 워크플로우 플러그인
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/            # 자동 인식
│   │   │   ├── analyze/
│   │   │   ├── plan/
│   │   │   ├── execute/
│   │   │   └── record/
│   │   └── agents/
│   │       └── requirement-validator.md
│   ├── seq-think/             # Sequential Thinking MCP
│   ├── glmr/                  # GitLab MR 관리 (7 skills)
│   ├── terraform/
│   ├── amplitude/
│   ├── slack/
│   ├── atlassian/
│   └── github/                # GitHub MCP
│
├── changelogs/              # 버전별 변경 이력
├── CHANGELOG.md             # 버전 카탈로그
├── CLAUDE.md                # Claude Code 가이드
└── README.md                # 이 파일
```

## 🛠 Development

### 새로운 스킬 만들기

```bash
# 1. skill-creator로 템플릿 생성
python3 ~/.claude/plugins/marketplaces/anthropic-agent-skills/skill-creator/scripts/init_skill.py <skill-name> --path .

# 2. 스킬 커스터마이징 (SKILL.md, references 등 편집)

# 3. 패키징 (배포용 .zip 생성)
python3 ~/.claude/plugins/marketplaces/anthropic-agent-skills/skill-creator/scripts/package_skill.py <skill-folder>
```

### 스킬 구조

```
skill-name/
├── SKILL.md (required)      # 메타데이터 + 사용 가이드
├── scripts/ (optional)      # 실행 가능한 스크립트
├── references/ (optional)   # 참조 문서
└── assets/ (optional)       # 템플릿, 에셋
```

### Git 워크플로우

**버전 관리 대상:**
- ✅ 스킬 소스 디렉토리 (`analyze/`, `plan/` 등)
- ✅ 문서 파일 (`CLAUDE.md`, `README.md`)
- ✅ `.gitignore`

**제외 항목** (`.gitignore`로 관리):
- ❌ `.zip` 파일 (빌드 결과물)
- ❌ `.claude/` (개인 설정)
- ❌ IDE 설정, 로그, 캐시 등

**워크플로우:**
```bash
# 소스만 커밋
git add analyze/ plan/
git commit -m "feat: add new skill"

# 배포는 로컬에서 패키징
python3 ~/.claude/.../package_skill.py analyze
/plugin install analyze.zip
```

## 📝 License

개인 사용을 위한 저장소입니다.
