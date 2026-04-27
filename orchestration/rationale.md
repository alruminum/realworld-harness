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
| dongchan-style + softcarry/hardcarry | 배포판 완전 배제 (별도 `dongchan-pack` 사이드 플러그인으로 보관 옵션) |

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
- **개인용 파일 검증은 Phase 1 종료 시 grep**: 1.2~1.6 진행 중엔 직관적으로 제외. 종료 시점에 `grep -ri "hardcarry|softcarry|dongchan"` 으로 누락 검증 (`docs/migration-plan.md §6` 체크리스트).

### Follow-Up

- 1.2 ~ 1.9 sub-commit 9개 (각 sub-commit마다 `orchestration/changelog.md` row 갱신은 생략 — Task-ID 단위 묶음 관리. 단, sub-commit msg에 `[1.X]` 표기 필수)
- Phase 1 종료 시점에 `HARNESS-CHG-20260427-02` 의 본 changelog 항목에 sub-commit 결과 요약 추가
- 검증 체크리스트(migration-plan.md §6) 모두 ✓ 후 Phase 2 진입 (`HARNESS-CHG-2026MMDD-NN` 신규 발급)

---

> 새 항목은 위 형식으로 추가. Task-ID 헤더는 H2(`##`), 4섹션은 H3(`###`).
