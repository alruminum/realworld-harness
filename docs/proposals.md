# RealWorld Harness 방향성 제안

> 작성: 2026-04-27
> 목적: 유저 철학("워크플로우 불변, 에이전트만 진화") vs 현재 AI 트렌드 정합성 검증 + 배포판 방향 제안.

---

## 1. 유저 철학 재정의

> **현실 세계 프로덕트 조직(기획·UX·아키·엔지·QA·리뷰)을 에이전트로 시뮬레이션. 에이전트는 진화해도 워크플로우는 불변. 절차가 시스템의 가드레일.**

핵심 키워드 3개:
1. **현실 시뮬레이션** — 가공된 AI workflow가 아니라, 실제 조직의 분업 구조 모사
2. **워크플로우 불변** — 모델·에이전트가 똑똑해져도 게이트·핸드오프 경로는 바꾸지 않음
3. **절차 = 가드레일** — 자율성보다 결정론적 협업 절차를 우선

---

## 2. 현재 AI 트렌드와의 정합성 검증

### 2-1. 일치하는 부분 (이 철학이 트렌드의 *우위*에 있는 지점)

| 트렌드 | 정합성 |
|---|---|
| **Multi-agent orchestration** (AutoGen, CrewAI, LangGraph 등) | ✓ 일치. 역할별 분업이 단일 거대 에이전트보다 multi-step 정확도가 높다는 게 2025~2026 SOTA 합의. |
| **Anthropic Claude Code의 sub-agent 모델** | ✓ 일치. 메인 + 전문 sub-agent + 명시적 핸드오프 = 실제 Claude Code 권장 패턴. |
| **"Process is the moat"** | ✓ 강한 일치. 모델은 6개월마다 갈아엎히지만, 워크플로우 레이어는 자산이 됨. |
| **Constitutional AI / deliberative checks** | ✓ 일치. 게이트(validator/pr-reviewer)가 hallucination·overreach를 잡는 게 입증된 패턴. |
| **TDD + structured output** | ✓ 일치. test-engineer attempt 0 + validator는 LLM 코딩 정확도 끌어올리는 표준 기법. |

### 2-2. 트렌드와 *충돌*하는 부분 (의식적으로 거스르는 지점)

| 트렌드 | 충돌 지점 | 평가 |
|---|---|---|
| **Agent autonomy 극대화** (1개 거대 에이전트가 모든 걸 함) | 유저 철학은 의도적으로 자율성을 제약. 게이트마다 유저 승인 강제. | **유저 철학이 옳다 (프로덕션 기준)**. 자율성은 데모에선 화려하나, 6h+ 작업·B2B 납품에서는 신뢰성이 떨어진다. |
| **Self-correcting loops** (에이전트가 자기 실수 감지 → 자동 복구) | 유저는 ESCALATE 시 자동 복구를 명시적으로 금지. | **상황 의존**. 작은 버그는 자동 복구가 더 빠르나, 큰 영향은 유저 게이트가 옳다. 현재의 `/quick` depth=simple이 이 균형을 잡고 있음. |
| **Tool-using monolith** (Computer Use, Operator 등) | 유저는 명시적 다중 에이전트 + 권한 분리. | **유저 철학이 더 안전**. monolith는 권한 경계가 흐릿해서 sandbox escape 위험이 높다. |
| **"Memory가 알아서 진화"** | 워크플로우 자체는 변하지 않게 함. memory는 보조. | **유저 철학이 옳다**. 워크플로우가 memory 학습 곡선에 휘둘리면 재현성이 깨진다. |

### 2-3. 결론

**유저의 "워크플로우 불변" 철학은 트렌드와 동떨어진 게 아니라, 현재 SOTA의 *프로덕션* 분파에 정확히 정렬돼 있다.** 데모/연구 트렌드는 자율성 극대화로 가지만, 실제 프로덕트에 들어가는 코드 작성 — 특히 B2B/엔터프라이즈 — 는 게이트·검증·재현성이 필수다. 유저 철학은 이쪽이다.

다만 "워크플로우 절대 불변"으로 보일 수 있는 표현은 약간 조정이 필요하다 — 워크플로우는 진화하되, 진화 비용을 의도적으로 비싸게 만든다(orch-rules-first 훅 + 문서 먼저 코드 나중). 이게 더 정확한 표현.

---

## 3. 배포판 방향 제안 (3가지)

### 제안 A: 포지셔닝 — "Production-grade Agent Workflow Engine"

현재 plan-plugin-distribution.md는 도구 중심으로 기술돼있음. 마켓플레이스 노출/네트워킹용으로는 약함. 다음 표현으로 재포지셔닝:

> *"AI가 똑똑해질수록 시스템이 풀리는 게 아니라, 워크플로우가 그 똑똑함을 받아안는다."*

타겟: 1인 개발자 + 소규모 팀 + B2B 외주 개발자 (실제 유저가 그 자리에 있음).
차별점: AutoGen·CrewAI 등은 프레임워크지만, RealWorld Harness는 **결정론적 게이트 시스템 + 5루프 표준 절차**. 패턴이 이미 정의돼있고 즉시 동작.

### 제안 B: 코어 불변식을 spec.md에 명시화

현재 harness-spec.md는 게이트와 비목표는 적혀있으나, 핵심 철학("워크플로우 불변")이 *암묵적*. 다음을 명시:

```
§0. Core Invariant
RealWorld Harness assumes agent capability will improve over time.
The workflow does not. Process layer is the system's persistent value.

Therefore:
- Workflow changes require explicit governance (orch-rules-first)
- Agent improvements operate within fixed gates
- Determinism > adaptability for production code paths
```

이게 명시되면 향후 PR/제안에서 "이 변경이 워크플로우를 약화시키는가" 판정 기준이 생긴다.

### 제안 C: "Agent Capability Tier" 개념 도입 (신규)

현재는 모든 에이전트가 동일 모델로 가정됨. 실제로는:
- engineer는 sonnet/haiku로 충분 (반복 attempt)
- architect는 opus 같은 high-tier 추천
- validator는 cost 최적화 가능

**제안**: `harness.config.json`에 `agent_tiers`를 추가하고, 모델 가격 변동에 따라 tier 매핑만 바꾸면 워크플로우 코드는 안 건드림. 이게 "에이전트 진화 vs 워크플로우 불변"을 코드로 강제하는 가장 깔끔한 표현.

```json
{
  "agent_tiers": {
    "high": "claude-opus-4-7",     // architect, plan-reviewer
    "mid":  "claude-sonnet-4-6",   // engineer, validator, pr-reviewer
    "low":  "claude-haiku-4-5"     // qa, design-critic
  }
}
```

---

## 4. 실행 순서 제안

분석에서 확인된 P0 정리 + 위 제안을 합쳐 다음 순서:

### Phase 0 — 클린업 + 거버넌스 골격 (1~1.5일)
1. `.bak` 11개 + `dongchan-style/` + 개인 커맨드 배제 (RWHarness에는 처음부터 미포함)
2. LICENSE (MIT) + CHANGELOG.md(v1.0.0 골격) + README 골격
3. RWHarness 디렉토리 구조 셋업: `.claude-plugin/`, `hooks/`, `agents/`, `harness/`, `commands/`, `orchestration/`, `templates/`, `scripts/`, `tests/`
4. **거버넌스 가벼운 버전** (§6 통합 방안):
   - `orchestration/changelog.md` 헤더에 Task-ID 컬럼 명시화 (HARNESS-CHG-YYYYMMDD-NN)
   - `orchestration/rationale.md` 신규 (Rationale/Alternatives/Decision/Follow-Up 4섹션 템플릿)
   - `orchestration/policies.md` 내 Change-Type 5종 분류표 + Document-Exception 스코핑 룰 추가

### Phase 1 — 코어 마이그레이션 (2~3일)
4. `~/.claude/`에서 RWHarness로 *선택적* 복사 (engineer 위임)
   - 활성 코드만, `.bak`/personal/legacy 제외
5. 경로 추상화: `Path.home()` → `Path(os.environ.get('CLAUDE_PLUGIN_ROOT', Path.home() / '.claude'))`
6. `hooks/hooks.json` 작성 (settings.json 23 엔트리 → 플러그인 hooks.json)

### Phase 2 — 철학 명시화 + 거버넌스 자동 게이트 (1일)
7. `docs/harness-spec.md` §0에 Core Invariant 추가 (제안 B)
8. README 메인 카피 — "Production-grade Agent Workflow Engine" (제안 A)
9. `agent_tiers` 옵션 도입 (제안 C, harness.config.json 스키마 확장)
10. **거버넌스 자동 게이트** (§6 Phase 2):
    - `scripts/check_doc_sync.py` (Python, git diff → Change-Type 자동 분류 → 동반 산출물 검사)
    - `scripts/hooks/pre-commit.sh` (git hook용 한 줄 래퍼)
    - `hooks/commit-gate.py` 확장 (CC PreToolUse에서 doc sync 체크)
    - `.github/PULL_REQUEST_TEMPLATE.md` (Document Sync 체크리스트)

### Phase 3 — 검증 + 배포 (2~3일)
10. clean install smoke test (별도 머신 또는 컨테이너)
11. 5루프 E2E 검증 (기획-UX / 설계 / 구현 / 디자인 / 버그픽스)
12. v1.0.0 태그 + 마켓플레이스 PR

총 4~7일.

---

## 5. 의사결정 필요 항목

| 항목 | 옵션 | 추천 |
|---|---|---|
| 마켓플레이스 플러그인 ID | `realworld-harness` / `rw-harness` / `harness-engineering` | **`realworld-harness`** (실제 이름 그대로) |
| security-reviewer 통합 | 통합 / 옵트인 / 배제 | **옵트인** (`harness.config.json` 플래그) — 5루프에 추가하면 비용↑ |
| `agent_tiers` 도입 시점 | Phase 1 / Phase 2 / 별도 에픽 | **Phase 2** (제안 C, 큰 코드 변경 없음) |
| dongchan-style + softcarry/hardcarry | 완전 배제 / 별도 fork 보관 / 옵션 패키지 | **완전 배제** (배포판) + 별도 `dongchan-pack` 사이드 플러그인 (개인 보관) |
| BATS → pytest 잔여 migration | 배포 전 / 후 | **배포 후** (현재 parity 34/34, 배포 차단 요소 아님) |
| 워크트리 격리 기본값 | true (현재) / false / 옵션 | **true 유지** (HARNESS-CHG-20260427-01 결정 따름) |
| 거버넌스 시스템 도입 | 그대로 채택 / 통합형 / 미채택 | **통합형** (§6 참조) |

---

## 6. 거버넌스 시스템 (TDM 패턴) 평가 + 통합 방안

> 외부 프로젝트(TDM)의 문서 거버넌스 시스템을 RealWorld Harness에 적용할지 검토. 2026-04-27 추가.

### 6-1. 평가: A− (좋은 패턴, 우리 환경에 맞춤 필요)

**TDM 거버넌스 핵심 5요소**:
1. `governance.md` = SSOT (모든 규칙 단일 출처)
2. Task-ID(`TDM-CHG-YYYYMMDD-NN`) 하나로 WHAT 로그(`document_update_record.md`)와 WHY 로그(`change_rationale_history.md`) 연결
3. Change-Type 6종 분류 (api/policy/implementation/build-release/test/docs-only)
4. `check_document_sync.mjs` — git diff 기반 CI 게이트 (Node.js)
5. 3중 pre-commit 강제 (git hook + CC hook + 에이전트 지침)

### 6-2. 강점 (배워야 할 것)

| 강점 | 우리 시스템에 부족한가 |
|---|---|
| WHAT/WHY 분리 로그 | ✓ 부족. orchestration/changelog.md는 WHAT 중심, WHY는 커밋 메시지에 분산 |
| Task-ID 단일 식별자로 양 로그 연결 | ⚠️ 일부. HARNESS-CHG-YYYYMMDD-NN은 있으나 WHY 로그 분리 안 됨 |
| 머지 차단 자동 게이트 | ✗ 없음. orch-rules-first.py는 *경고*만, 차단 안 함 |
| Document-Exception 스코핑 (현재 diff만 유효) | ✓ 매우 깔끔. 과거 누적 엔트리가 면죄부 안 됨 |
| 3중 강제 (git + CC + agent) | ⚠️ 부분. CC hook은 있고 git hook은 없음 |

### 6-3. 우리 환경 부적합 지점 (그대로 채택 안 함)

1. **무게 vs 규모 불균형**: TDM은 다국적/대규모 추정. RealWorld Harness는 1인 + 소규모. 6종 Change-Type을 그대로 들이면 오버엔지니어링.
2. **에이전트 워크플로우와 중복**: 이미 architect→engineer→validator→pr-reviewer 5게이트 체인이 인적/자동 강제 중. 거기에 별도 거버넌스를 *겹치면* 룰 충돌 위험.
3. **Node.js 의존성**: `check_document_sync.mjs` 신규 의존성. RWHarness는 Python 중심. **Python으로 재작성 필수** (`scripts/check_doc_sync.py`).
4. **별도 governance.md 추가는 SSOT 분산**: 우리는 이미 `harness-spec.md`(헌법) + `orchestration/policies.md`(운영 룰) 2층 구조. 여기에 governance.md를 *추가*하지 말고, 기존 두 문서에 *흡수*.
5. **CI 게이트 ROI는 자체 개발 흐름 한정**: RWHarness는 플러그인 배포 레포라 외부 PR 빈도 낮음. 게이트의 가치는 우리 내부 워크플로우 보호에 한정됨 (유효).

### 6-4. 통합 방안 (TDM 패턴 ↔ 우리 자산 매핑)

| TDM 산출물 | 우리 통합 위치 | 비고 |
|---|---|---|
| `governance.md` (SSOT) | `harness-spec.md` §0 Core Invariant + `orchestration/policies.md` 흡수 | 신규 파일 만들지 않음 |
| `document_update_record.md` (WHAT) | `orchestration/changelog.md` 확장 (이미 존재) | 컬럼 명시화: Task-ID, Date, Files, Exception |
| `change_rationale_history.md` (WHY) | `orchestration/rationale.md` **신규** | Rationale + Alternatives + Decision + Follow-Up 4섹션 |
| `document_impact_matrix.md` | `orchestration/policies.md` 내 표 추가 | 별도 파일 안 만듦 |
| `check_document_sync.mjs` (Node) | `scripts/check_doc_sync.py` **신규 (Python)** | Python 재작성, hooks/harness_common.py 유틸 활용 |
| `pre-commit` hook | `scripts/hooks/pre-commit.sh` **신규** | 한 줄로 `python3 scripts/check_doc_sync.py` |
| `.claude/settings.json` PreToolUse | `hooks/commit-gate.py` 확장 | 이미 존재. doc sync 체크 추가 |
| `cc-pre-commit.sh` (stdin JSON 파싱) | `hooks/commit-gate.py`에 통합 | Python 통일 |
| `PULL_REQUEST_TEMPLATE.md` | `.github/PULL_REQUEST_TEMPLATE.md` 신규 | 한국어 + 영문 |
| `AGENTS.md` 규칙 명시 | `agents/preamble.md` + `MEMORY.md` 정책 | 이미 있음, 문구 보강 |

### 6-5. Change-Type 우리 버전 (5종, RWHarness 구조 반영)

```yaml
spec:           # harness-spec.md, harness-architecture.md, prd.md, trd.md (헌법급)
infra:          # hooks/, harness/, scripts/, .claude-plugin/ (핵심 인프라)
agent:          # agents/*.md, agents/*/* (에이전트 정의)
docs:           # docs/, orchestration/, README, CHANGELOG (문서만)
test:           # tests/pytest/, tests/bats/ (테스트만)
```

각 타입별 동반 필수 산출물:
- `spec` → orchestration/changelog.md + orchestration/rationale.md (양쪽 필수)
- `infra` / `agent` → orchestration/changelog.md + 영향 받는 spec 문서 검토 표시
- `docs` → orchestration/changelog.md
- `test` → 산출물 추가 없음 (테스트 단독)

### 6-6. 적용 시점

- **Phase 0** (클린업 단계): Task-ID 명시화 + `orchestration/rationale.md` 골격 + Document-Exception 스코핑 룰만 도입 (가벼운 버전).
- **Phase 2** (철학 명시화 단계): `scripts/check_doc_sync.py` + git pre-commit hook + Change-Type 자동 분류 + 머지 차단 게이트 활성화 (전체).

이유: Phase 0~1에선 코드가 대대적으로 마이그레이션되는 중이라 게이트를 켜면 자기 발에 걸림. Phase 2부터 안정화 후 강제.

### 6-7. 결정 (메모리 보존용)

- **채택**: Task-ID 단일 식별자, WHAT/WHY 분리 로그, Document-Exception 스코핑, git pre-commit 추가 강제, Change-Type 분류
- **거부**: 별도 `governance.md` 신설 (SSOT 분산), Node.js 의존성, 6종 분류 그대로 이식
- **시점**: Phase 0에서 가벼운 버전(로그 분리 + Task-ID), Phase 2에서 자동 게이트 활성화
