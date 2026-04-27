# Rationale History (WHY log)

> Task-ID 단위 의사결정 근거. **Rationale / Alternatives / Decision / Follow-Up** 4섹션 고정.
>
> WHAT(무엇을 바꿨나)는 [`changelog.md`](changelog.md), 본 문서는 WHY(왜·어떤 대안·후속).

---

## `HARNESS-CHG-20260427-01` — 2026-04-27

### Rationale

`~/.claude/` 의 난개발된(유저 표현) 하네스 시스템을 Claude Code 플러그인 마켓플레이스 배포 가능한 클린 구조로 재구성한다. 작업 인풋:

- `~/.claude/docs/harness-spec.md` — 헌법 (오늘 2026-04-27 작성된 최신본)
- `~/.claude/docs/harness-architecture.md` — 기술 구현 도면 (오늘 작성)
- `docs/plan-plugin-distribution.md` — 정본 설계 문서 (2026-04-21 갱신)
- Explore 에이전트의 시스템 종합 분석 → `docs/analysis-current-harness.md`

핵심 동기는 plan 문서에 명시된 5가지 (다른 머신 설치 불가, 수동 settings.json 편집, 버전 관리 부재 등) 외에, **유저가 직접 명시한 철학 — "에이전트는 진화해도 워크플로우는 불변"** 을 명문화·코드화하기 위함. 이 철학은 plan 문서엔 암묵적이었고, 메모리(`project_realworld_harness.md`)에 별도 보존.

### Alternatives

| # | 옵션 | 설명 | 평가 |
|---|---|---|---|
| 1 | 단방향 마이그레이션 | `~/.claude/` 전체를 RWHarness로 복사 후 정리 | 위험 — 현재 작동 중인 시스템 깨질 가능성. ~/.claude 사용자 = dc.kim 본인이라 작업 중 사이드이펙트 발생 |
| 2 | 빌드 산출물 | `~/.claude/` 그대로 두고 RWHarness는 자동 동기화 스크립트로 생성 | 추적 어려움. 두 시스템이 항상 lockstep 동기화 부담 |
| **3** | **클린 새 구조** | RWHarness에서 새로 짜고 검증되면 ~/.claude deprecate | **선택** |

### Decision

옵션 3을 선택. 이유:

1. `~/.claude/`는 작동 상태로 유지 → 유저 일상 작업에 영향 없음
2. 클린 슬레이트로 시작 → plan 문서의 §4 디렉토리 구조와 §5 경로 추상화를 정확히 따름
3. 검증 충분히 후 deprecate → 롤백 안전성 확보

추가 결정 사항 (모두 `docs/proposals.md` 에 상세):

| 항목 | 결정 |
|---|---|
| 플러그인 정식 이름 | `realworld-harness` (`harness-engineering`은 plan 문서의 가칭이었음, 폐기) |
| 포지셔닝 카피 | "Production-grade Agent Workflow Engine" |
| Core Invariant 명시화 | Phase 2에 `harness-spec.md §0` 추가 (architect 위임 예정) |
| `agent_tiers` 옵션 | `harness.config.json`에 high/mid/low tier 매핑. Phase 2 도입 |
| 거버넌스 시스템 (TDM 패턴) | 통합형 채택 — 별도 `governance.md` 신설 X, `harness-spec.md` + 본 `policies.md` 흡수. Node.js → Python 재작성 |
| Change-Type 분류 | TDM의 6종(api/policy/implementation/build-release/test/docs-only)이 아닌 RWHarness 구조 반영 5종(spec/infra/agent/docs/test) |
| security-reviewer 통합 | 옵트인 (`harness.config.json` 플래그) |
| 워크트리 격리 기본값 | `true` 유지 (HARNESS-CHG-20260427-01 결정 따름) |
| 개인 스타일 가이드 + softcarry/hardcarry | 배포판 완전 배제 (사용자 개인 보관은 별도 사이드 플러그인 또는 fork) |

### Follow-Up

- **Phase 1 (코어 마이그레이션, 2~3일)**: ~/.claude/{hooks, harness, agents, commands} 활성 코드를 RWHarness로 선택적 복사. `Path.home()` → `Path(os.environ.get('CLAUDE_PLUGIN_ROOT', Path.home() / '.claude'))` 추상화. `hooks/hooks.json` 작성 (settings.json 23 엔트리 → 플러그인 hooks.json).
- **Phase 2 (철학 명시화 + 자동 게이트, 1일)**:
  - `harness-spec.md §0` Core Invariant 추가 (architect 위임)
  - README 메인 카피 — "Production-grade Agent Workflow Engine"
  - `agent_tiers` 옵션 도입 (`harness.config.json` 스키마 확장)
  - `scripts/check_doc_sync.py` (Python) 작성
  - `scripts/hooks/pre-commit.sh` (git hook 한 줄 래퍼)
  - `hooks/commit-gate.py` 확장 (CC PreToolUse에서 doc sync 체크)
  - `.github/PULL_REQUEST_TEMPLATE.md` (Document Sync 체크리스트)
- **Phase 3 (검증 + 배포, 2~3일)**: clean install smoke test, 5루프 E2E 검증, v1.0.0 태그, 마켓플레이스 PR.
- 후속 Task-ID 발급 시점에 본 항목의 Follow-Up을 closure ref 추가.

---

---

## `HARNESS-CHG-20260427-02` — 2026-04-27

### Rationale

Phase 0(부트스트랩)이 완료된 시점(`HARNESS-CHG-20260427-01`)에서 Phase 1(코어 마이그레이션)의 *진입 계획*을 명시화한다. ~/.claude의 활성 코드를 한 번에 다 옮기지 않고 sub-section으로 쪼갠 이유는 (1) 이력 추적성 — 매 commit이 단일 책임을 가짐, (2) 회복 가능성 — 중간 단계에서 문제 발생 시 단일 sub-section만 재작업, (3) 유저 명시 요청 — "phase별이나 섹션별로 커밋은 알아서 잘 해주면 좋겠어 나중에 이력파악되게".

### Alternatives

| # | 옵션 | 평가 |
|---|---|---|
| 1 | Phase 1 전체를 단일 거대 commit으로 처리 | 제외 — 이력 추적성 0, 중간 회복 어려움 |
| 2 | sub-section을 Task-ID 분리 (1.2 → CHG-03, 1.3 → CHG-04, …) | 거버넌스 표 비대화. 9개 sub-section이라 부담 |
| **3** | sub-section을 sub-commit으로, Task-ID 1개 공유 | **선택**. 이력 추적 + 거버넌스 단순. 각 commit msg에 sub-section 번호 명시 |

### Decision

옵션 3 채택. `HARNESS-CHG-20260427-02` 산하 sub-commit 형식:

```
HARNESS-CHG-20260427-02 [1.2] hooks/ 마이그레이션 (활성 22개 + 공유 유틸 4개)
HARNESS-CHG-20260427-02 [1.3] harness/ 마이그레이션 (Python 11개 + Shell 8개)
...
```

추가 결정:
- **`orchestration/` 디렉토리 충돌 회피**: ~/.claude/orchestration/policies.md를 RWHarness/orchestration/policies.md로 그대로 복사하면 RWHarness의 거버넌스 policies.md(2026-04-27 신규 작성, Task-ID 룰)와 충돌. → `orchestration/upstream/` 서브디렉토리로 분리 복사.
- **경로 추상화는 Phase 1.7 일괄 적용**: 1.2~1.6에서 *원본 그대로 복사*하고, 1.7에서 일괄 sed/grep으로 `Path.home()` → `Path(os.environ.get('CLAUDE_PLUGIN_ROOT', Path.home() / '.claude'))` 변환. 이유: 코드 정확성 검증을 *복사*와 *변환* 두 단계로 분리.
- **개인용 파일 검증은 Phase 1 종료 시 grep**: 1.2~1.6 진행 중엔 직관적으로 제외. 종료 시점에 `grep -ri "hardcarry|softcarry"` + 개인 스타일 가이드 디렉토리명으로 누락 검증 (`docs/migration-plan.md §6` 체크리스트).

### Follow-Up

- 1.2 ~ 1.9 sub-commit 9개 (각 sub-commit마다 `orchestration/changelog.md` row 갱신은 생략 — Task-ID 단위 묶음 관리. 단, sub-commit msg에 `[1.X]` 표기 필수)
- Phase 1 종료 시점에 `HARNESS-CHG-20260427-02` 의 본 changelog 항목에 sub-commit 결과 요약 추가 — **완료 (commit `bcce3ee` 후 [1.10])**
- 검증 체크리스트(migration-plan.md §6) 모두 ✓ 후 Phase 2 진입 (`HARNESS-CHG-2026MMDD-NN` 신규 발급)

### Phase 1 종료 (2026-04-27)

**달성**:
- ~/.claude 활성 코드 100% 마이그레이션 (Python 34 + .md 73 + JSON/SH 등)
- PLUGIN_ROOT 추상화 도입 — `${CLAUDE_PLUGIN_ROOT}` 환경변수 폴백 ~/.claude
- hooks/hooks.json 작성 — 플러그인 마켓플레이스 install 시 자동 활성화 가능
- 개인용(hardcarry/softcarry/개인 스타일 가이드) 파일 단위 100% 배제

**Phase 2 인계 (다음 Task-ID로)**:
- `harness-spec.md §0` Core Invariant 신규 작성 (proposals.md §3 제안 B)
- README 메인 카피 — "Production-grade Agent Workflow Engine" (proposals.md §3 제안 A)
- `harness.config.json` `agent_tiers` 옵션 도입 (proposals.md §3 제안 C)
- **`hooks/agent-gate.py` + `hooks/agent-boundary.py` 의 hardcarry/softcarry bypass 로직 정리**
  - 옵션 1: 완전 제거 (RWHarness는 특정 개인의 임시 과제 컨셉과 무관)
  - 옵션 2: 일반화 (`HARNESS_BYPASS=1` env 같은 generic flag로 추상화)
  - 결정 필요 — 옵션 2가 더 유연 (외부 사용자가 자기 과제용 bypass 활용 가능)
- `scripts/check_doc_sync.py` (Python 자동 게이트, proposals.md §6 통합형 거버넌스)
- `scripts/hooks/pre-commit.sh` + `hooks/commit-gate.py` 확장
- `.github/PULL_REQUEST_TEMPLATE.md`
- `scripts/setup-rwh.sh` PLUGIN_ROOT 적응 + 플러그인 install 후 hooks/hooks.json 자동 활성화 검증

---

---

## `HARNESS-CHG-20260427-03` — 2026-04-27

### Rationale

Phase 1(코어 마이그레이션) 종료(`HARNESS-CHG-20260427-02`) 후 Phase 2(철학 명시화 + 자동 게이트) 진입. 핵심 의도 3가지:

1. **암묵적 철학을 코드 옆 문서로 끌어내기** — "에이전트는 진화해도 워크플로우는 불변"이라는 유저 명시 철학(`memory/project_realworld_harness.md`)을 `harness-spec.md §0` Core Invariant로 명문화. 향후 PR/제안에서 "이 변경이 워크플로우를 약화시키는가" 판정 기준이 생김.
2. **모델 진화 흡수 매커니즘** — `agent_tiers` 옵션으로 모델 가격 변동·세대 교체 시 워크플로우 코드를 *건드리지 않고* 매핑만 갱신 가능. "에이전트 진화 ↔ 워크플로우 불변"을 코드로 강제하는 가장 깔끔한 표현.
3. **거버넌스 자동 강제** — Phase 0에서 명시한 룰(Task-ID + WHAT/WHY + Document-Exception 스코핑)을 git pre-commit hook + Claude Code commit-gate.py + GitHub PR 템플릿 3중으로 자동 강제. 휴먼 enforce에서 자동 enforce로 승격.

부수 정리: hardcarry/softcarry bypass 로직 — 유저 명시(2026-04-27) "동찬은 제외하고 마이그레이션해 내가 과제할라고 잠깐 넣은 스킬이야" → 옵션 A(완전 제거) 채택.

### Alternatives

| 항목 | 검토 옵션 | 선택 | 근거 |
|---|---|---|---|
| Core Invariant 위치 | (a) 별도 manifesto 파일 / (b) `harness-spec.md §0` / (c) README 첫 문단 | **(b) §0** | spec이 헌법 위치 — 게이트·불변식 모두 §0의 구체화 표현 |
| agent_tiers 매핑 형식 | (a) 에이전트별 직접 매핑 / (b) tier 추상화 high/mid/low / (c) 모델 직접 지정만 | **(b)** | 모델명은 자주 바뀌나 에이전트 역할은 안정. tier 레이어가 둘을 분리 |
| bypass 로직 처리 | (a) 완전 제거 / (b) 일반화 `HARNESS_BYPASS=1` / (c) 그대로 | **(a) 완전 제거** | 유저 결정 — 개인 과제용 임시 스킬, 배포판에 무관 |
| 자동 게이트 구현 언어 | (a) Node.js (TDM 원본) / (b) Python (RWHarness 통일) | **(b) Python** | 기존 인프라 통일. Node 의존성 폭 회피 |
| Phase 2 범위 | (a) 분할 (Phase 2A/B) / (b) 한 Task-ID 산하 sub-commits | **(b)** | Phase 1 패턴 재사용. 9 sub-commit으로 단위 명확화 |

### Decision

위 (b)/(b)/(a)/(b)/(b) 채택. Phase 2 = `HARNESS-CHG-20260427-03` 산하 sub-commit 9개 (2.1~2.9).

### Follow-Up

- 9 sub-commit 진행 후 Phase 3 진입 (clean install smoke test → v1.0.0 → 마켓플레이스 PR) **— 완료 [2.9]**
- `agent_tiers` 의 환경별 분기(개발/배포)는 v1.1 이후 (현재는 단일 매핑)
- `check_doc_sync.py` 의 GitHub Actions 통합은 Phase 3 또는 v1.1
- Core Invariant 자체의 변경은 PR title에 `[invariant-shift]` 토큰 + 별도 거버넌스 (rationale.md 4섹션 강제)

### Phase 2 종료 (2026-04-27)

**달성**:
- 핵심 철학 명문화 (`harness-spec.md §0` Core Invariant 4항목)
- README 메인 카피 — "Production-grade Agent Workflow Engine"
- `agent_tiers` 추상화 — 모델 진화 흡수 메커니즘 (12 에이전트 → 3 tier → 모델 ID)
- 거버넌스 자동 게이트 3중 강제:
  1. `.git/hooks/pre-commit` ← `scripts/hooks/pre-commit.sh`
  2. Claude Code `hooks/commit-gate.py` Gate 4
  3. GitHub PR 템플릿 (휴먼 검토 + 향후 GitHub Actions)
- Phase 1 잔존 TODO 모두 해결 (hardcarry/softcarry 완전 제거, .no-harness 마커는 일반 옵션 보존)

**Phase 3 인계 (다음 Task-ID)**:
- 별도 머신 또는 컨테이너에서 clean install smoke test
  - `/plugin marketplace add alruminum/realworld-harness` → `/plugin install`
  - `${CLAUDE_PLUGIN_ROOT}` 환경변수 자동 set 검증
  - `bash "${CLAUDE_PLUGIN_ROOT}/scripts/setup-rwh.sh"` 신규 프로젝트 적용
- 5루프 E2E 검증 (기획-UX / 설계 / 구현 / 디자인 / 버그픽스)
- BATS → pytest 잔여 마이그레이션 (P1, 차단 요소 X)
- v1.0.0 태그 + `CHANGELOG.md` 정식 릴리즈
- 마켓플레이스 PR — public 전환 결정 (현재 private)
- `setup-rwh.sh` 에 플러그인 모드 분기 추가 (글로벌 settings.json hooks 등록 skip — Phase 2.8 미처리분)
- GitHub Actions workflow — `scripts/check_doc_sync.py base..head` (PR 단계 자동화)

**남은 의식적 부채**:
- `setup-rwh.sh` 가 플러그인 모드에서 사용자 ~/.claude/settings.json 의 hooks 섹션을 *여전히* 수정 — 이는 `if [ -z "$CLAUDE_PLUGIN_ROOT" ]` 분기로 감싸야 하나 큰 변경이라 Phase 3 또는 별도 sub-commit으로 미룸
- `setup-rwh.sh` 의 `gh api` 호출(마일스톤·레이블 자동 생성)은 RWHarness 거버넌스 룰과 직접 연관 없음 — 분리 검토 필요 (v1.1)

---

---

## `HARNESS-CHG-20260427-04` — 2026-04-27

### Rationale

Phase 0~2 완료 시점에서 RWHarness 문서·코드에 *마이그레이션 작업의 흔적*과 *특정 개인의 식별 정보*가 다수 잔존했음을 발견. 외부 사용자(마켓플레이스 install 후 docs/ 둘러보기)가 보면 다음 두 인상이 동시에 남는다:

1. *"이 시스템은 외부의 다른 곳(~/.claude)에서 옮겨진 historical artifact다"* — `에서 마이그레이션됐다`, `원본 source: ~/.claude/...` 같은 헤더가 그 인상의 주범. RWHarness가 자체 정본이라는 신호를 약화시킨다.
2. *"이 시스템은 특정 개인(dongchan)의 개인 도구이거나, 그 사람의 환경 가정이 박혀있다"* — `시니어 엔지니어 dongchan`, `/Users/dc.kim/`, `jajang`, `memoryBattle`, `HardcarryDryRun`, `dongchan-style/`, `dongchan-pack` 같은 식별자. 마켓플레이스 일반 사용자에겐 무관하고 노이즈.

추가로 §0 Core Invariant 와 README 의 한국어 본문에 "분파" 같은 한자어 추상 용어가 등장 — 유저 명시 ("분파가 뭐야? 이런거 현실세계의 언어로 좀 바꿔줘") — 사용자 첫 인상에서 코드 메타용어와 일상어가 섞여 가독성 저하.

### Alternatives

| 대상 | 옵션 (a) | 옵션 (b) | 선택 | 근거 |
|---|---|---|---|---|
| 마이그레이션 헤더 | 그대로 유지 (history 보존 명목) | 헤더 제거, 독립 정본화 | **(b)** | 외부 사용자가 보는 docs/ 는 *현재 정본*이지 *마이그레이션 일지*가 아니다. history는 git log + orchestration/changelog.md 에 충분 |
| dongchan 명시 | 그대로 (작성자 attribution) | 일반화 ("프로젝트 운영자") | **(b)** | 유저 명시 요청. attribution 은 LICENSE + plugin.json author 에 한정 |
| dc.kim 절대 경로 | 그대로 (예시 사실성) | `${HOME}/...`/`<your-name>` 일반화 | **(b)** | 외부 사용자 환경에 직접 적용 가능한 표기가 더 실용적 |
| jajang/memoryBattle 사례 | 코드 주석에 명시적 인용 (실전 출처 명시) | "실측"/"실전 사례"로 추상화 | **(b)** | 외부 사용자에겐 어떤 프로젝트인지 무관. 의미만 살리면 충분 |
| 추상 한자어 ("분파") | 코드 메타용어 그대로 | 일상 한국어로 풀어쓰기 | **(b)** | 유저 명시. spec/README 가독성 우선 |
| upstream/ 디렉토리 dongchan/dc.kim | 일관성 위해 같이 정리 | 원본 그대로 보존 (참조 정본) | **보존** | upstream 은 *~/.claude 원본 스냅샷* 의미. 손대면 정체성 무너짐. 별도 README 로 의도 명시 예정 |
| plan-plugin-distribution.md (유저가 직접 쓴 plan) | 보존 | 단어 수준 일반화 | **단어만** | 큰 의미 변경 없이 식별자만 일반화. 원본 의도 보존 + 외부 노출 우려 해소 |
| LICENSE Copyright | 익명화 | 저작권자 명기 (법적 표준) | **명기 유지** | 저작권 표기는 법적 필수 |

### Decision

(b) 옵션 일관 채택. upstream/ 보존 + LICENSE 보존 만 예외. plugin.json author 는 GitHub username(`alruminum`)으로 일반화 (이메일은 유지 — 컨택 채널).

### Follow-Up

- 본 sub-commit: `HARNESS-CHG-20260427-04` [3.1]
- 후속 sub-commit:
  - **[3.2] (완료)** `orchestration/upstream/README.md` 신규 — 디렉토리 정체성 명시 (commit `30c3dbd`)
  - **[3.3] (완료)** `docs/harness-architecture.md` 본문 잔존 `~/.claude/*` 경로를 `${CLAUDE_PLUGIN_ROOT}/...` 로 적응 — §1 시스템 구성요소 표 (Hooks/Harness Core/Agents/Skills 4행) / §2.1 훅 등록 안내 / §5.3 setup-rwh.sh 호출 / §6 changelog.md 위치 / 마지막 노트 정리
  - **[3.4] (완료)** `.github/workflows/doc-sync.yml` + Change-Type `.github/` infra 분류 (commit `67637af`) — 거버넌스 3중 강제 완성 (git hook + commit-gate + GitHub Actions)
  - **[3.5] (완료)** `scripts/smoke-test.sh` + `docs/smoke-test-guide.md` (commit `9b18cf3`) — 자동 50/50 PASS, Docker/별도 머신/마켓플레이스 install 가이드
  - **[3.6] (완료)** `docs/e2e-test-scenarios.md` — 5루프(기획-UX / 설계 / 구현 / 디자인 / 버그픽스) E2E 시나리오 + 통과 기준 + 통합 체크리스트
- 다음 sub-commit 후보 ([3.7]+, 외부 행위 / 사용자 컨펌 필요):
  - 별도 머신/컨테이너에서 smoke-test + 5루프 E2E 실행 결과 기록
  - v1.0.0 태그 + `CHANGELOG.md` 정식 릴리즈
  - 마켓플레이스 PR + public 전환 (현재 private repo)

---

---

## `HARNESS-CHG-20260427-05` — 2026-04-27

### Rationale

Phase 0~3 완료 (총 27 sub-commits, `HARNESS-CHG-20260427-01` ~ `04`). 코어 + 거버넌스 + 검증 모두 갖춘 시점에서 v0.1.0-alpha 첫 public release. 대상 사용자: `~/.claude` 하네스를 이미 사용 중인 개발자 + Claude Code 플러그인 마켓플레이스 첫 방문자.

릴리즈 시점 결정 근거:
- smoke-test 50/50 PASS (ubuntu-latest 별도 머신 자동)
- E2E quickstart §1 실측 통과 (`/quick` 1 attempt 3m 18s)
- 외부 노출 부적절 식별자 LICENSE/upstream 외 0건 (Explore 점검)
- GitHub Actions 2 workflow 가동 확인

### Alternatives

| 옵션 | 설명 | 평가 |
|---|---|---|
| (a) v1.0.0 직행 | 알파 단계 건너뛰고 정식 v1.0.0 | 거부 — 5루프 전체 E2E 미실측 (구현 루프만 통과, 기획-UX/설계/디자인/큰 구현 미검증) |
| (b) v0.1.0-alpha | 알파 release + 사용자 피드백 + v1.0.0 | **선택** — 검증 충분 + 알파라는 expectation 일치 |
| (c) 더 기다림 | Phase 4 보류, 5루프 전체 E2E 후 release | 거부 — alpha 의 의미는 "early access". 기다릴수록 피드백 사이클 늦어짐 |

### Decision

(b) v0.1.0-alpha. 본 Task-ID 산하 sub-commit 4개:
1. `[4.1]` release prep (README/CHANGELOG release-ready)
2. `[4.2]` git tag + push + GitHub Release (메타 행위, commit 불필요)
3. `[4.3]` public 전환 (`gh repo edit --visibility public`, 메타 행위)
4. `[4.4]` 정리 — 실제 release URL 반영 + Phase 4 ✅ 완료 표기

순서 근거: tag/release 는 private 상태에서 가능 → public 전환을 마지막에 두면 외부 노출 시점 통제 가능.

### Follow-Up

- alpha release 후 사용자 피드백 수집 (GitHub Issues)
- v0.2.0 알려진 부채 정리:
  * setup-rwh.sh 글로벌 hooks 등록의 플러그인 모드 분기
  * Node 20 deprecation env 제거 (액션 Node 24 호환 후)
  * BATS → pytest 잔여 마이그레이션
- v1.0.0 마일스톤: 5루프 전체 E2E 실측 + Anthropic 공식 또는 커뮤니티 큐레이션 (있다면) 등재

### Phase 4 sub-commits 진행 보강 (2026-04-27 추가)

| sub-commit | 결정 | 근거 |
|---|---|---|
| `[4.3]` historical 자료 4개 삭제 (migration-plan / plan-plugin-distribution / proposals / analysis-current-harness) | 외부 사용자(마켓플레이스 install 후) 의 docs/ 둘러보기에 노이즈가 큼. 결과는 모두 정본 문서에 반영됐고 historical 자료의 인풋 가치는 git log + v0.1.0-alpha tag archive 로 충분. | 유저 명시 (2026-04-27): "Migration Plan 이런것도 이제 다 했으니 없애도 될거같고" |
| `[4.4]` git tag `v0.1.0-alpha` push | annotated tag, baseline=`cb5e89d` (4 historical 파일 *포함* 한 시점) — release archive 가 그 시점 historical 사진을 보존. | tag/release 는 private repo 에서도 가능, public 전환을 마지막에 두면 외부 노출 시점 통제 |
| `[4.5]` GitHub Release 생성 (예정) | `gh release create v0.1.0-alpha --notes-from-changelog` — release 페이지 = CHANGELOG 의 v0.1.0-alpha 섹션 | 사용자 install 진입점 명확화 |
| `[4.6]` public 전환 (예정) | `gh repo edit alruminum/realworld-harness --visibility public --accept-visibility-change-consequences` — 외부 노출 시작 | 유저 명시 승인 후 진행 |
| `[4.7]` 정리 commit (예정) | Phase 4 ✅ 완료 표기 + 실제 release URL 반영 | 종료 마커 |

---

---

## `HARNESS-CHG-20260427-06` — 2026-04-27

### Rationale

v0.1.0-alpha release (Phase 4 종료) + 마이그레이션 완료 후, 사용자가 *기존 알려진 부채* (CHANGELOG.md 의 알려진 부채 섹션) 정리 시작. 가장 critical 한 부채:

**`setup-rwh.sh` 의 플러그인 모드 미분기**: 플러그인 install 사용자가 신규 프로젝트에 `bash setup-rwh.sh` 실행하면 *글로벌 ~/.claude/settings.json* 의 hooks 섹션을 *자동 추가* — 플러그인의 `hooks/hooks.json` 와 *중복 등록* 위험. 다행히 "이미 등록됨 — 스킵" 로직이 있어 *중복 실행* 자체는 안 일어나나, 미install 환경 → install 환경 전환 시 잔존 hooks 가 cleanup 안 됨.

근본 원인: setup-rwh.sh 설계 당시 *개발 폴백 모드* (~/.claude 직접 사용) 만 가정. 플러그인 모드는 cache 디렉토리에서 자동 로드되니 글로벌 settings.json 손댈 필요 없음.

### Alternatives

| # | 옵션 | 평가 |
|---|---|---|
| 1 | hooks 등록 영역 완전 제거 (어떤 모드든 안 함) | 거부 — 개발 폴백 사용자(플러그인 install 안 한 환경) 호환성 깨짐 |
| 2 | 분기 추가: `[ -z "$CLAUDE_PLUGIN_ROOT" ]` 일 때만 hooks 등록 | **선택** — 플러그인 모드는 skip + 안내 메시지, 폴백 모드는 기존 동작 유지 |
| 3 | 별도 옵션 플래그 (`--no-global-hooks`) | 거부 — 사용자가 굳이 인자 줘야 — 자동 감지가 자연스러움 |

### Decision

옵션 2 채택. line 234 (영역 시작) ~ line 343 (CLEANUP_PYEOF block 종료 후 fi) 를 `if [ -n "$CLAUDE_PLUGIN_ROOT" ]; then echo "skip"; else ...; fi` 으로 감쌈.

### Follow-Up

- 본 sub-commit `[6.1]`
- 후속 v0.2.0 부채 (CHANGELOG.md 알려진 부채 섹션):
  * `[6.2]` BATS → pytest 잔여 마이그레이션 (차단 X, 정리 가치 있음)
  * `[6.3]` Node 20 deprecation env 제거 (액션 자체 Node 24 호환되면)
  * `[6.4]` 5루프 §2~5 E2E 실측 (현재 §1 quickstart + 코드 검증만 통과)
  * `[6.5]` plugin update 배포 (`/plugin update realworld-harness`로 사용자에 반영)
- Phase 4 종료 commit `4013d09` 이후 첫 새 Task-ID

---

> 새 항목은 위 형식으로 추가. Task-ID 헤더는 H2(`##`), 4섹션은 H3(`###`).
