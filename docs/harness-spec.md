# Harness Spec (PRD 대체)

> RealWorld Harness 플러그인의 목적·불변식·게이트·비목표 정의.
> 일반 제품 PRD가 아닌, 메타 시스템(코딩 에이전트 오케스트레이션)의 운영 헌법.

작성: 2026-04-27 / 최근 갱신: §0 Core Invariant 추가 (`HARNESS-CHG-20260427-03`)

---

## 0. Core Invariant — 워크플로우 불변

본 시스템은 **LLM 에이전트의 능력이 시간에 따라 향상된다**고 가정한다.
**워크플로우는 그렇지 않다.** Process layer는 시스템의 영속적 자산이다.

따라서:

1. **워크플로우 변경에는 명시적 거버넌스가 필요하다** — `orch-rules-first` 훅 + Task-ID(`HARNESS-CHG-YYYYMMDD-NN`) + WHAT/WHY 분리 로그 (`orchestration/changelog.md` + `rationale.md`).
2. **에이전트 능력 향상은 *고정된 게이트 안에서만* 작동한다** — 모델이 Opus 4.7 → 5.0 → 6.0 으로 진화하더라도, `architect → engineer → validator → pr-reviewer` 핸드오프 경로는 변하지 않는다. `agent_tiers` (harness.config.json)는 이 분리를 코드로 강제한다.
3. **실제 서비스 코드 경로에서는 예측 가능성을 자유로운 적응보다 우선한다** — 자율 에이전트가 *알아서* 복구하는 패턴 대신, 명시적 ESCALATE → 유저 게이트 → 재계약(SPEC_GAP) 흐름을 강제. 같은 입력에 같은 결과(재현성)와 누가 무엇을 결정했는지 추적 가능성이 자유로운 적응보다 중요하다.
4. **자율 에이전트보다 역할별 분업이 더 잘 맞는 영역** — 신뢰성, 재현성, B2B 적합성, 6개월 이상 유지보수가 필요한 코드. 본 시스템은 데모나 연구용이 아니라, *실제 서비스에 들어가는 코드를 만드는 데 쓰는 것*을 목표로 한다.

### 적용 범위

본 §0은 RealWorld Harness의 **철학적 헌법**이다. §1~6의 모든 게이트·불변식·비목표는 본 §0의 구체화 표현이다.

- 본 §0을 약화시키는 변경(예: 게이트 우회, 에이전트 자율성 확대, 예측 가능성 완화)은 PR title에 `[invariant-shift]` 토큰을 명시한다.
- 해당 PR은 `orchestration/rationale.md` 의 4섹션(Rationale / Alternatives / Decision / Follow-Up) 중 **Alternatives**에 *왜 이 워크플로우 불변식이 깨져야 하는가*를 명시 필수.
- 자동 게이트(`scripts/check_doc_sync.py`, Phase 2.5+)는 `[invariant-shift]` PR 제목에 `Document-Exception:` 라인이 동반되지 않으면 머지 차단.

> *현실 세계의 프로덕트 조직(기획·UX·아키·엔지·QA·리뷰)이 그러하듯, 개별 구성원이 똑똑해진다고 회사의 의사결정 절차가 사라지지는 않는다. RealWorld Harness의 가치는 그 절차에 있다.*

---

## 1. 개요

`~/.claude` 하네스는 Claude Code 위에서 동작하는 **에이전트 오케스트레이션 인프라**다.
사용자가 단일 LLM에게 "구현해줘"를 던지는 대신, 역할별 전문 에이전트(architect / designer / engineer / validator / pr-reviewer 등)가 **명시적 게이트와 핸드오프**를 거쳐 작업을 진행하도록 강제한다.

핵심 사용자는 두 부류:
- **메인 Claude (오케스트레이터)** — 루프 게이트 통과 여부를 확인하고 다음 단계 에이전트를 호출.
- **프로젝트 운영자 (시니어 엔지니어 / 리드)** — 에이전트 산출물을 검수하고 게이트 승인을 내림. 코드는 직접 거의 쓰지 않음.

---

## 2. 풀려는 문제

하네스가 해결하는 4가지 failure mode. 모두 실제 incident에서 발견된 패턴이며 출처는 commit message body / `orchestration/changelog.md`.

### 2.1 메인 Claude의 src/ 직접 수정으로 인한 체인 붕괴
- **증상**: 메인이 직접 코드를 쓰면 architect 계획·designer 토큰·validator 검증이 모두 우회되어, 누구도 추적할 수 없는 변경이 누적됨.
- **방어**: `src/**` 메인 Edit/Write 차단 (agent-boundary.py). 모든 구현은 `executor.py impl` 경유.

### 2.2 핸드오프 페이로드 인라인 전달로 인한 토큰 폭주
- **증상**: validator 피드백 본문을 다음 에이전트 프롬프트에 인라인 → 수만 토큰 → 에이전트가 파일 재작성 루프에 빠지고 Stream idle timeout(900초/11분).
- **방어**: 하네스가 `_handoffs/` 파일을 만들고 **경로만** 다음 에이전트에 전달. 전문 인라인 금지.

### 2.3 동일 impl 반복 ESCALATE
- **증상**: 같은 impl이 attempt 0–3을 N회 풀세트로 반복하며 동일 fail_type만 반복.
- **방어**: `_escalate_history.json`에 누적 카운트 → 2회 이상 동일 fail_type이면 architect SPEC_GAP 자동 호출 (HARNESS-CHG-20260426-04).

### 2.4 디자인 토큰 우선 미적용으로 인한 컴포넌트 갈아엎기
- **증상**: ux-flow.md만 있고 design-handoff.md가 없는 상태로 구현 시작 → 시안 도착 시 색·폰트·간격 전부 재작업.
- **방어**: 첫 impl을 `01-theme-tokens.md`로 강제하고, 모든 색/폰트/간격은 토큰 경유 (HARNESS-CHG-20260426-02).

추가 사례:
- **AI smell 무한 색 금지**: 다크 네이비+골드 = Claude/AI 클리셰. 색 swap만으로 우회 가능했음 → ux-architect가 5개 구조 패턴(단색 배경, 단일 엑센트, outline 카드, 플랫 글리프, Spotify 인상) 자가 점검 후 3개 이상이면 자동 reject (HARNESS-CHG-20260426-05).

---

## 3. 불변식 (Invariant)

깨지면 즉시 escalate. 어느 에이전트·스킬도 우회 불가.

### I-1. 메인 Claude는 `src/**`를 직접 수정하지 않는다
- 강제 지점: `hooks/agent-boundary.py` PreToolUse(Edit/Write).
- 예외: 인프라 프로젝트 (`is_infra_project()` True인 경우) — `~/.claude` 자체.
- 출처: `orchestration-rules.md:29-35`, `CLAUDE.md:113-125`.

### I-2. 모든 구현은 하네스 루프를 거친다
- 강제 지점: `harness/executor.py impl --impl <path> --issue <REF>`.
- `<REF>` 는 추적 ID 일반형 — `#N` (GitHub Issue) 또는 `LOCAL-N` (LocalBackend, `orchestration/issues/INDEX.jsonl`).
- 백엔드는 `harness/tracker.py` 가 환경에 따라 자동 선택 (`gh` CLI 가용성 + repo 연결 + `HARNESS_TRACKER` env). gh 미설치 환경에서도 `LOCAL-N` 폴백으로 추적성 보존.
- 추적 ID 강제 자체는 보존 — agent-gate.py:78 이 `r"#\d+|LOCAL-\d+"` 정규식으로 검증.
- depth=simple으로 경량화 가능하지만 우회는 없다.

### I-3. 유저 게이트에서 자동 진행 금지
- `READY_FOR_IMPL`, `UX_FLOW_READY`, `PLAN_REVIEW_PASS` 등 마커 도달 시 메인은 유저 승인 없이 다음 단계로 진입할 수 없다.
- "마커 없으면 진행 금지" — 텍스트에서 추출한 경로로 다음 단계 진입 방지.

### I-4. ESCALATE 자동 복구 금지
- `IMPLEMENTATION_ESCALATE`, `UX_FLOW_ESCALATE`, `SCOPE_ESCALATE` 수신 시 메인은 즉시 사용자 보고 후 대기. 자동 재시도/우회 금지.

### I-5. 워크플로우 변경은 문서 먼저, 코드는 그 다음
- `orchestration-rules.md` / `harness-spec.md` / `harness-architecture.md` 갱신 → 그 다음 훅·executor 코드.

### I-6. 핸드오프는 경로 전달, 본문 인라인 금지
- 하네스가 `_handoffs/{from}_to_{to}_{ts}.md` 파일 생성 → 경로만 다음 에이전트에 전달.
- 위반 시 토큰 폭주 → 11분 timeout.

### I-7. 활성 에이전트 판정은 단일 소스
- `session_state.active_agent()` 하나만 사용. 별도 폴백/TTL 추가 금지.

### I-8. 플러그인 디렉토리(`~/.claude/plugins/{cache,marketplaces,data}/`) 직접 수정 금지
- 재설치 시 증발하거나 drift 발생.
- 우회가 필요하면 `~/.claude/hooks/`에 선행 훅 추가.

### I-9. 하네스 인프라 변경(`hooks/`, `harness/`, `scripts/`, `agents/`)은 메인 단독 Edit/commit 금지
- qa → architect → engineer 위임 강제 (`MEMORY.md` 참조).

---

## 4. 루프 게이트

`hooks/harness-router.py`가 매 UserPromptSubmit마다 출력하는 7개 플래그가 진행 상태를 표현한다.

### 4.1 플래그 표

| 플래그 | 의미 | Set 조건 | Clear 조건 |
|---|---|---|---|
| `harness_active` | executor 루프 점유 중 | `executor.py impl` 진입 | PostToolUse(Agent) — `post-agent-flags.py` |
| `plan_validation_passed` | impl 계획이 validator(Plan) 통과 | validator PASS 마커 출력 | 다음 impl 진입 시 |
| `designer_ran` | designer 에이전트가 1회 이상 실행 | designer 호출 직후 | 새 이슈 진입 시 |
| `design_critic_passed` | THREE_WAY 모드에서 design-critic이 1개 이상 PASS 판정 | critic VARIANTS_APPROVED | 새 이슈 진입 시 |
| `test_engineer_passed` | TDD 테스트 선작성 완료 | test-engineer attempt 0 종료 | post-commit-cleanup |
| `validator_b_passed` | 코드 검증 PASS | validator(Code) PASS | 다음 impl 진입 시 |
| `pr_reviewer_lgtm` | pr-reviewer LGTM | pr-reviewer 통과 | post-commit-cleanup |

### 4.2 게이트 시퀀스 (최소 패스)

```
[plan]   architect Module Plan → validator(Plan) → plan_validation_passed
   ↓
[test]   test-engineer (attempt 0) → test_engineer_passed
   ↓
[impl]   engineer (attempt 0..3) → validator(Code) → validator_b_passed
   ↓
[review] pr-reviewer → pr_reviewer_lgtm
   ↓
[merge]  유저 승인 → squash merge → post-commit-cleanup
```

UI 작업이 포함되면 `[design]` 단계가 `[plan]`과 `[test]` 사이에 삽입되어 `designer_ran` + (THREE_WAY일 때) `design_critic_passed`를 함께 요구한다.

### 4.3 진입 경로별 루프

| 상황 | 진입 |
|---|---|
| 신규 기능 / PRD 변경 | 기획-UX 루프 → 설계 루프 → 구현 루프 |
| UI만 변경 | `ux` 스킬 → designer (하네스 루프 없음) |
| 화면 리디자인 | `ux` 스킬 (REFINE 감지) → ux-architect(UX_REFINE) → 유저 승인 → designer SCREEN |
| 일반 구현 | `executor.py impl --impl <path> --issue <N>` |
| 작은 버그 | `quick` 스킬 → qa → architect LIGHT_PLAN → executor (depth=simple) |
| 버그 보고 | `qa` 스킬 → QA 에이전트 분류 → LIGHT_PLAN / DESIGN_HANDOFF / SCOPE_ESCALATE |

---

## 5. 비목표 (Out-of-Scope)

하네스가 의도적으로 **하지 않는** 것. 단일 책임과 토큰 효율을 위해 제외됨.

### 5.1 단일 에이전트의 다중 책임 금지
- engineer는 아키텍처 결정·요구사항 정의·디자인 심사 안 함 → 즉시 escalate.
- designer는 src/ 수정 안 함 → 코드는 engineer 담당.
- validator / design-critic / pr-reviewer / qa / security-reviewer는 **파일을 수정하지 않는다** (판정만).

### 5.2 product-planner는 코드 결정 금지
- src/, docs/impl/, trd.md 읽기 차단.
- 파일명·함수명·Props명·import 경로 언어 사용 금지.
- 허용: 유저 행동, 시스템 반응, 비즈니스 규칙, 화면 단위.

### 5.3 plan-reviewer는 architect 내부 결정 역오염 금지
- src/, docs/impl/, trd.md 읽기 차단. PRD 레벨 현실성만 판정.

### 5.4 test-engineer는 구현 코드 없이 테스트 작성
- attempt 0에서만 호출. attempt 1+는 테스트 이미 존재.
- 도메인 문서 / src/ 읽기 차단 — impl 인터페이스만 보고 작성.

### 5.5 UX_REFINE는 src/ 코드 안 본다
- Pencil MCP 4개 도구(get_editor_state, batch_get, get_screenshot, get_variables) 각 1회만 허용.
- 추가 조회 필요 시 `UX_FLOW_ESCALATE` (Stream idle timeout 11분 방지).

### 5.6 자동 PR/이슈 생성·코멘트
- 메인은 사용자 명시 요청 시에만 PR 생성·머지. `mcp__github__*` 호출은 issue-gate.py가 검증.

### 5.7 main 브랜치 직접 push
- 모든 변경은 branch → PR → squash merge. main 직접 commit/push 금지.

---

## 6. 참고 문서

| 파일 | 역할 |
|---|---|
| `~/.claude/orchestration-rules.md` | 루프 진입 기준·마커 규약·에이전트 권한 매트릭스 (운영 룰) |
| `~/.claude/CLAUDE.md` | 메인 Claude 작업 헌법 (절대 원칙·커밋 절차·에이전트 위임) |
| `~/.claude/orchestration/changelog.md` | HARNESS-CHG-* 변경 이력 (incident → 패치 추적) |
| `docs/harness-architecture.md` | 본 spec의 기술 구현 (훅·핸드오프·세션·화이트리스트) |
| `~/.claude/MEMORY.md` | 사용자별 feedback / project memory 인덱스 |
| `orchestration/policies.md` | (RWHarness) Task-ID + Change-Type + Document-Exception 룰 |
