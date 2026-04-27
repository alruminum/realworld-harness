# 현재 ~/.claude 하네스 시스템 분석 (배포 인풋)

> 분석 시점: 2026-04-27
> 기준: ~/.claude main @ 2c231c3 (harness-spec/architecture 최종 검증 시점)
> 목적: RealWorld Harness 플러그인 배포판 정제를 위한 현황 도면.

---

## A. 시스템 1줄 요약

**34개 Python 훅 + 14개 역할별 에이전트 + 18개 자연어 스킬**로 5단계 워크플로우(기획-UX · 설계 · 구현 · 디자인 · 리뷰-커밋)를 강제하는 메타 오케스트레이션 인프라. 절차가 불변식 — 에이전트 성능과 무관하게 게이트·핸드오프·에스컬레이션 경로는 변하지 않는다.

---

## B. 워크플로우 도면 (5루프)

```
[기획-UX 루프]   product-planner → plan-reviewer → UI check → ux-architect
                 → validator(UX) → 유저 승인① → ux-flow.md (+ design-handoff.md)

[설계 루프]      architect (System Design / Module Plan) → trd.md / impl 계획

[구현 루프]      test-engineer(attempt 0) → engineer(0..3) → validator(Code)
                 ↳ 동일 fail_type 2회 → architect(SPEC_GAP) [동결 카운트]
                 ↳ attempt 3 + spec_gap 2 도달 → IMPLEMENTATION_ESCALATE

[디자인 루프]    designer (ONE_WAY/THREE_WAY) → (THREE_WAY) design-critic
                 → 유저 승인②

[PR 리뷰 루프]   pr-reviewer → LGTM → 유저 승인③ → squash merge
                 → post-commit-cleanup
```

### 게이트 마커
- `READY_FOR_IMPL` / `PLAN_VALIDATION_PASS` / `HARNESS_DONE` (정상 흐름)
- `HARNESS_ESCALATE` / `SPEC_GAP_FOUND` / `UX_FLOW_ESCALATE` / `SCOPE_ESCALATE` (자동 복구 금지, 유저 보고 후 대기)

### 진입 경로별 분기
| 입력 | 진입 스킬 | 라우팅 |
|---|---|---|
| 신규 기능 | `/product-plan` | 기획-UX 루프 |
| UI만 변경 | `/ux` | designer (루프 생략, Pencil만) |
| 화면 리디자인 | `/ux` (REFINE 감지) | ux-architect(UX_REFINE) → designer |
| 일반 구현 | (직접) | `executor.py impl --impl <path> --issue <N>` |
| 버그/이슈 | `/qa` | qa 분류 → LIGHT_PLAN / DESIGN_HANDOFF / SCOPE_ESCALATE |
| 작은 버그 | `/quick` | qa → architect(LIGHT_PLAN) → executor(depth=simple) |

---

## C. 구성 요소 인벤토리 (실측)

### 훅 34개 — 카테고리별

| 카테고리 | 개수 | 핵심 |
|---|---|---|
| 게이트 / 경계 | 8 | agent-boundary, agent-gate, commit-gate, issue-gate, plugin-write-guard, orch-rules-first, skill-gate |
| 라우팅 / 상태 | 9 | harness-router (UserPromptSubmit), session-state, session-agent-cleanup, post-agent-flags, post-skill-flags |
| UX 드리프트 | 3 | harness-drift-check, harness-settings-watcher, harness-session-start |
| 리뷰 / 로깅 | 5 | harness-review-inject / -trigger / -stop, ralph-session-stop |
| 유틸 / 공유 | 9 | harness_common, helpers, notify, core, config, impl_router, review_agent, providers |

훅 등록 위치: `~/.claude/settings.json` 의 hooks 섹션 (전역). 프로젝트별 훅 미지원.

### 에이전트 14개

| 에이전트 | 역할 1줄 | 직접 호출 |
|---|---|---|
| architect | 시스템 설계, 모듈 계획, SPEC_GAP 처리 | Mode 종속 |
| engineer | src/** 구현 (attempt 0..3) | 불가 (executor 경유) |
| test-engineer | TDD 테스트 선작성 (attempt 0만) | 불가 |
| validator | Plan/Code/UX 3역 검증 | Mode 종속 |
| designer | Pencil 캔버스 시안 (ONE_WAY/THREE_WAY) | 가능 |
| ux-architect | UX Flow + 레이아웃 설계 | 가능 |
| pr-reviewer | LGTM 판정 (merge gate) | 불가 |
| design-critic | 디자인 4기준 점수화 | executor 경유 |
| product-planner | PRD 작성 | 가능 |
| plan-reviewer | PRD 6차원 현실성 검증 | 자동 (executor) |
| qa | 버그 분류, 라우팅 추천 | 가능 |
| security-reviewer | 보안 감시 (예약 — 미통합) | 미정 |
| preamble.md | 공통 규칙 자동 주입 | — |
| README.md | index | — |

### 스킬 18개 (자연어 진입로)
`/qa /ux /quick /product-plan /ralph /harness /deliver /doc-garden /softcarry /hardcarry /init-project /ux-sync /init /review /simplify /fewer-permission-prompts /security-review` 등.

> **배포 제외**: `/softcarry`, `/hardcarry`, `dongchan-style/` (개인 dongchan 시니어 보조 모드)

### 하네스 코어 11개 모듈 (~/.claude/harness/*.py)

| 모듈 | 책임 |
|---|---|
| executor.py | 진입점. impl/design/plan/tech-epic 라우팅 |
| **impl_loop.py (85KB)** | 구현 루프 완전 로직 — attempt 0..3, ESCALATE 누적, SPEC_GAP 동결, 마커 파싱, 핸드오프 생성 |
| plan_loop.py (19KB) | 기획-UX 루프 |
| core.py | StateDir, Flag, LogDir |
| config.py | harness.config.json 파싱 |
| helpers.py | harness-memory.md, escalate_history |
| notify.py | osascript / terminal-notifier 알림 |
| providers.py | LLM 초기화 |
| impl_router.py | depth 분기 (simple/std/deep) |
| review_agent.py | 리뷰 호출 래퍼 |

쉘 보조: `executor.sh / impl{,_simple,_std,_deep}.sh / design.sh / plan.sh / utils.sh`

### 상태 저장 (프로젝트별)

```
{project}/.claude/harness-state/
├── .sessions/{session_id}/live.json  # 활성 agent/skill/issue 단일 소스
├── .sessions/.../flags/{prefix}_{issue}/*  # plan_validation, test_engineer, validator_b, pr_reviewer_lgtm 등
├── .global.json
├── {prefix}_escalate_history.json
└── .worktrees/{prefix}/issue-{N}/    # 이슈별 워크트리 (isolation=worktree, 2026-04-27 기본)
```

화이트리스트 등록: `~/.claude`, `~/project/jajang`, `~/project/memoryBattle`.

---

## D. 불변식 (워크플로우 가드레일 9개)

| # | 불변식 | 강제 지점 |
|---|---|---|
| I-1 | 메인 Claude는 src/** 직접 수정 금지 (인프라 프로젝트 예외) | agent-boundary.py |
| I-2 | 모든 구현은 executor.py impl 경유 | agent-gate.py |
| I-3 | 유저 게이트(READY_FOR_IMPL 등)에서 자동 진행 금지 | harness-router.py |
| I-4 | ESCALATE 자동 복구 금지 (유저 보고 후 대기) | impl_loop.py + harness-router |
| I-5 | 워크플로우 변경은 문서 먼저, 코드 나중 | orch-rules-first.py |
| I-6 | 핸드오프는 경로 전달, 본문 인라인 금지 (Stream idle 11분 회피) | core.py.write_handoff |
| I-7 | 활성 에이전트 판정 단일 소스 (session_state.active_agent) | session-state.py |
| I-8 | 플러그인 디렉토리(~/.claude/plugins/{cache,marketplaces,data}) 직접 수정 금지 | plugin-write-guard.py |
| I-9 | 하네스 인프라 변경은 메인 단독 Edit/commit 금지 (qa→architect→engineer 위임) | MEMORY.md + 운영 룰 |

---

## E. 현실 워크플로우 시뮬레이션 매핑

| 현실 직군 | 에이전트 | 활성 단계 |
|---|---|---|
| Product Manager | product-planner | 기획-UX 시작 (PRD 작성) |
| PM 검토 | plan-reviewer | 6차원 현실성 검증 (2026-04-25 순서 변경) |
| UX Designer | ux-architect | UX Flow + 구조 검증 (anti-AI-smell 강화) |
| UI Designer | designer | Pencil 시안 (ONE/THREE_WAY) |
| QA | test-engineer + validator | TDD + 회귀 |
| Senior Engineer | architect | 시스템·모듈·SPEC_GAP |
| Mid Engineer | engineer | attempt 0..3 |
| Code Reviewer | pr-reviewer | LGTM |

**완성도**: 5단계 정직군 커버 ✓ / SPEC_GAP 재계약 루프(architect↔engineer) ✓
**구멍**:
1. security-reviewer 미통합 (예약 역할만)
2. 시니어 최종 승인 매커니즘 모호 (위임 강제는 있으나 누가 최종 권한자인지 미명시)
3. cross-team 피드백 루프 약함 — ux-architect → product-planner 역방향 사이클 없음 (순차만)
4. architect의 UI 컴포넌트 구조 검증 약함 (designer 단독 가드)

---

## F. 문서-코드 드리프트

| 항목 | 상태 |
|---|---|
| 훅/에이전트/스킬 카운트 | ✓ 일치 (34/14/18) |
| HARNESS_ONLY_AGENTS, attempt max, SPEC_GAP 임계 | ✓ 일치 |
| 워크트리 격리 기본값 | ✓ 일치 (HARNESS-CHG-20260427-01) |
| 플래그 7개 set/clear 지점 (spec.md §4.1) | ⚠️ 미검증 — impl_loop.py 85KB 산재 |
| security-reviewer 호출 경로 | ⚠️ 코드/문서 모두 미명시 |

---

## G. 배포 전 정리 체크리스트

### 필수
- [ ] `.bak` 11개 삭제 (`harness/*.sh.bak`)
- [ ] 개인용 제거: `dongchan-style/`, `commands/{hardcarry,softcarry}.md`, `projects/-Users-...-HardcarryDryRun/`
- [ ] 하드코딩 경로(`Path.home()`) → `${CLAUDE_PLUGIN_ROOT}` 추상화 (~58곳, 활성 코드 ~15곳)
- [ ] LICENSE 추가 (MIT)
- [ ] CHANGELOG v1.0.0 초기화
- [ ] README 영문+한글 (현재 드리프트 심함)

### 검증 필요
- [ ] 플래그 set/clear 지점 완전 매핑 (impl_loop.py 추적)
- [ ] security-reviewer 통합 경로 결정 (배제 / 통합 / 옵트인)
- [ ] 핸드오프 파일 방식의 토큰 효율 실측 (이론만 있음)
- [ ] BATS → pytest 잔여 migration (현재 parity 34/34)

---

## H. 추가 조사 필요

1. **플래그 상태 머신** — impl_loop.py 85KB 내 set/clear 지점 다이어그램화
2. **fail_type 분류체계** — 동일 fail_type 2회 판정 로직 정확한 위치
3. **security-reviewer 통합 계획** — 통합 vs 옵트인 vs 배제
4. **핸드오프 토큰 효율 실측** — Stream idle timeout 11분 회피 검증 (session log 기반)
