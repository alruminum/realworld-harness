# 5루프 E2E 검증 시나리오

> Phase 3 [3.6] 산출물. 마켓플레이스 install 후 또는 개발 폴백 모드에서 5개 루프(기획-UX / 설계 / 구현 / 디자인 / 버그픽스)가 끝까지 동작하는지 사용자 시나리오로 검증.

작성: 2026-04-27 / Task-ID: `HARNESS-CHG-20260427-04` [3.6]

---

## 0. 사전 준비

### 0.1 환경 셋업

```bash
# 옵션 A: 마켓플레이스 install
/plugin marketplace add alruminum/realworld-harness
/plugin install realworld-harness
# Claude Code 재시작

# 옵션 B: 개발 폴백 모드 (~/.claude 기존 사용자)
git clone https://github.com/alruminum/realworld-harness.git ~/realworld-harness
# 또는 기존 ~/.claude 그대로 사용 (PLUGIN_ROOT 미설정)
```

### 0.2 테스트 프로젝트 생성

```bash
mkdir -p /tmp/rw-e2e-test && cd /tmp/rw-e2e-test
git init
git remote add origin https://github.com/<your>/<test-repo>.git  # 테스트 repo
bash "${CLAUDE_PLUGIN_ROOT:-${HOME}/.claude}/scripts/setup-project.sh"
```

검증:
- [ ] `.claude/harness.config.json` 생성됨 (`prefix`, `isolation: worktree`)
- [ ] `.claude/settings.json` 생성됨 (env + allowedTools 만)
- [ ] `.git/hooks/pre-commit` 자동 설치 (또는 없으면 수동 `ln -sf`)
- [ ] 프로젝트 루트가 화이트리스트에 등록됨 (`harness-list` 스킬로 확인)

---

## 1. 기획-UX 루프 검증

**시나리오**: "할일 추적 앱에 알림 기능 추가" 신규 기능 PRD 작성.

### 1.1 진입

```
유저 프롬프트: "기획자야 할일 추적 앱에 알림 기능을 추가하고 싶어"
```

→ `/product-plan` 스킬 자동 호출 (또는 명시 호출).

### 1.2 흐름

```
product-planner (PRD 작성)
  → plan-reviewer (6차원 현실성 검증)
  → 통과 → UI check (UI 변경 여부 판정)
  → ux-architect (UX_FLOW 작성)
  → validator(UX) (PASS/FAIL)
  → 유저 승인 ① → ux-flow.md + design-handoff.md(선택)
```

### 1.3 통과 기준

- [ ] `prd.md` 생성됨 (product-planner 산출)
- [ ] `plan-reviewer` 가 6차원(현실성/MVP/제약/숨은 가정/경쟁/과금/기술 실현성) 분석 출력
- [ ] `PLAN_REVIEW_PASS` 마커 출력 (또는 `PLAN_REVIEW_CHANGES_REQUESTED` 후 재작업)
- [ ] `docs/ux-flow.md` 생성됨 (ux-architect 산출)
- [ ] `validator` UX 검증 PASS (또는 `UX_FLOW_ESCALATE` 시 유저 보고)
- [ ] `READY_FOR_IMPL` 마커 도달 시 메인이 자동 진행하지 않고 *유저 승인 대기* (불변식 I-3)

### 1.4 실패 시나리오 검증

- **ESCALATE 발생 시**: `UX_FLOW_ESCALATE` 또는 `PLAN_REVIEW_CHANGES_REQUESTED` 시 메인이 *자동 복구하지 않음* + 유저에게 보고
- **CLARITY_INSUFFICIENT (5차원 모호성)**: product-planner 가 추가 질문 → 인터뷰 모드 진입

예상 시간: 5~15분.

---

## 2. 설계 루프 검증

**시나리오**: 위 PRD 기반으로 시스템 설계 + impl 계획.

### 2.1 진입

```
유저 프롬프트: "설계해줘 (또는 architect 직접 호출)"
```

### 2.2 흐름

```
architect SYSTEM_DESIGN → trd.md
architect TASK_DECOMPOSE → backlog.md + 에픽
architect MODULE_PLAN → docs/milestones/vNN/epics/.../impl/NN-*.md
  (executor.py impl 진입 시 자동 호출)
```

### 2.3 통과 기준

- [ ] `trd.md` 생성됨 (SYSTEM_DESIGN 산출)
- [ ] `backlog.md` + `stories.md` 작성됨
- [ ] impl 계획 파일 생성 (`docs/milestones/vNN/epics/<epic>/impl/NN-*.md`)
- [ ] design-handoff.md 작성됨 (UI 변경 포함 시) — 첫 impl이 `01-theme-tokens.md` 인지 확인 (불변식 — HARNESS-CHG-20260426-02)
- [ ] `READY_FOR_IMPL` 마커 + 유저 승인 대기

### 2.4 실패 시나리오

- architect 가 `MODULE_PLAN` 모드를 직접 호출하려 하면 차단 (impl_loop 경유 필수)
- `validator(Plan) FAIL` 시 architect 재호출 + 누적 카운트

예상 시간: 5~15분.

---

## 3. 구현 루프 검증 (가장 핵심)

**시나리오**: impl 계획 1개 (예: `01-theme-tokens.md`) 구현.

### 3.1 진입

```
python3 "${CLAUDE_PLUGIN_ROOT}/harness/executor.py" impl \
  --impl docs/milestones/v01/epics/epic-01-notification/impl/01-theme-tokens.md \
  --issue 1 \
  --prefix rwe2e
```

### 3.2 흐름 (attempt 0..3 + SPEC_GAP)

```
test-engineer (attempt 0 only) → test 파일 작성 → test_engineer_passed
  ↓
engineer (attempt 0) → src/** 구현
  ↓
validator(Code) → PASS / FAIL
  ↓ FAIL
engineer (attempt 1, 출력 토큰 최소화)
  ↓ … attempt 3
  ↓ FAIL 동일 fail_type 2회 → architect SPEC_GAP 자동 호출
  ↓ SPEC_GAP 처리 후 attempt 카운터 동결, 새 attempt 0 시작
  ↓ attempt 3 + spec_gap 2 도달 → IMPLEMENTATION_ESCALATE
```

### 3.3 통과 기준

- [ ] `harness_active` 플래그 set (`executor.py impl` 진입)
- [ ] `.worktrees/<prefix>/issue-1/` 워크트리 생성 (isolation=worktree)
- [ ] `test-engineer` attempt 0 실행 + `test_engineer_passed` 플래그 set
- [ ] `engineer` 가 `src/**` 만 수정 (다른 경로 시도 시 `agent-boundary.py` 차단)
- [ ] `validator(Code)` PASS 시 `validator_b_passed` 플래그 set
- [ ] `pr-reviewer` LGTM 시 `pr_reviewer_lgtm` 플래그 set
- [ ] `HARNESS_DONE` 마커 + 유저 승인 대기 → squash merge → `post-commit-cleanup` 1회성 플래그 정리

### 3.4 실패 시나리오 (반드시 검증)

- **메인 Claude 가 src/ 직접 수정 시도** → `agent-boundary.py` 차단 + 이유 메시지
- **engineer 직접 Agent 도구 호출** → `agent-gate.py` 차단 (HARNESS_ONLY_AGENTS)
- **동일 fail_type 2회** → architect SPEC_GAP 자동 호출 (HARNESS-CHG-20260426-04)
- **attempt 3 + spec_gap 2 초과** → `IMPLEMENTATION_ESCALATE` + 자동 복구 금지 (불변식 I-4)
- **핸드오프 페이로드 인라인** → 차단 또는 11분 timeout 회피 (불변식 I-6)

### 3.5 거버넌스 게이트 동작 검증 (Phase 2.5+ 추가)

- [ ] git commit 시 `.git/hooks/pre-commit` → `check_doc_sync.py` 호출
- [ ] spec 변경 + changelog/rationale 누락 시 commit 차단
- [ ] `Document-Exception: <사유>` commit msg 시 통과
- [ ] Claude Code 가 `Bash(git commit ...)` 호출 시 `commit-gate.py` Gate 4 동일 검증

예상 시간: 30분 ~ 2시간 (impl 복잡도 따라).

---

## 4. 디자인 루프 검증

**시나리오**: UI 컴포넌트 시안 생성.

### 4.1 진입

```
유저 프롬프트: "디자인해줘" 또는 "/ux"
```

### 4.2 흐름 (ONE_WAY)

```
ux 스킬 → designer (Pencil 캔버스 시안 1개)
  → 유저 확인 → 채택 → DESIGN_HANDOFF 패키지 출력
```

### 4.3 흐름 (THREE_WAY)

```
ux 스킬 → designer (3 variants 동시 생성)
  → design-critic (4기준 점수화 + PASS/REJECT)
  → VARIANTS_APPROVED (1개 이상 PASS) 또는 VARIANTS_ALL_REJECTED
  → 유저 PICK → 채택 → DESIGN_HANDOFF
```

### 4.4 통과 기준

- [ ] Pencil MCP 연결 정상 (`mcp__pencil__get_editor_state` 호출 가능)
- [ ] designer 가 `design-variants/**` 또는 `docs/ui-spec*` 만 수정
- [ ] `designer_ran` 플래그 set
- [ ] THREE_WAY 모드 시 `design_critic_passed` 플래그 set (1개 이상 PASS)
- [ ] AI smell 5개 구조 패턴 자가 점검 — 3개 이상 매칭 시 자동 reject (HARNESS-CHG-20260426-05)
- [ ] DESIGN_HANDOFF 패키지가 `01-theme-tokens.md` 작성을 강제

예상 시간: 10~30분 (Pencil 응답 + 검토 시간).

---

## 5. 버그픽스 루프 검증

**시나리오**: 사용자가 "버그가 있어" 보고.

### 5.1 진입 (작은 버그)

```
유저 프롬프트: "/quick" 또는 "간단히 고쳐줘"
```

### 5.2 흐름

```
qa (이슈 분류) → architect LIGHT_PLAN → executor.py impl --depth simple
  → engineer attempt 0..3 (단순 fix)
  → validator(Code) → pr-reviewer
  → HARNESS_DONE
```

### 5.3 진입 (큰 버그 / 디자인 영향)

```
유저 프롬프트: "/qa 버그 보고: ..."
```

→ qa 에이전트 분류:

```
LIGHT_PLAN → 위와 동일
DESIGN_HANDOFF → 디자인 루프 진입
SCOPE_ESCALATE → 자동 복구 금지 + 유저 보고
```

### 5.4 통과 기준

- [ ] qa 에이전트가 issue 생성 (`mcp__github__create_issue`) — `issue-gate.py` 검증 통과
- [ ] LIGHT_PLAN architect 호출 가능 (직접 호출 허용 mode)
- [ ] `quick` 스킬 → depth=simple → simple/std/deep 분기 정상 (impl_router)
- [ ] `SCOPE_ESCALATE` 시 자동 복구 금지

예상 시간: 5~30분.

---

## 6. 통합 검증 체크리스트

### 6.1 권한 경계 (불변식 I-1, I-2)

- [ ] 메인 Claude 가 `src/**` Edit/Write 시도 → 차단 (`agent-boundary.py`)
- [ ] 메인 Claude 가 `engineer` Agent 직접 호출 → 차단 (`agent-gate.py`)
- [ ] engineer 가 `docs/**` 수정 시도 → 차단

### 6.2 게이트 (불변식 I-3, I-4)

- [ ] `READY_FOR_IMPL` 마커 시 자동 진행 X (유저 승인 대기)
- [ ] `IMPLEMENTATION_ESCALATE` 시 자동 복구 X (유저 보고 + 옵션 제시)

### 6.3 핸드오프 (불변식 I-6)

- [ ] `_handoffs/` 파일 경로만 다음 에이전트에 전달 (본문 인라인 X)
- [ ] Stream idle timeout 11분 회피 (실측 시간 30초 이내)

### 6.4 거버넌스 (Phase 2)

- [ ] git commit 시 doc-sync 게이트 발동 (3중 강제 중 하나라도)
- [ ] Document-Exception 스코핑 — 현재 diff 만 유효 (과거 누적 무효)
- [ ] PR 머지 시 GitHub Actions doc-sync workflow 통과

### 6.5 agent_tiers (Phase 2)

- [ ] `harness.config.json` 의 `agent_tiers` override 시 모델 매핑 변경 적용
- [ ] 워크플로우 코드 무수정으로 모델 교체 가능

---

## 7. 결과 기록

각 루프별 통과 결과를 본 문서 끝에 추가하거나 별도 `docs/e2e-results-YYYY-MM-DD.md` 로 기록 권장.

```
| 루프 | 통과 | 시간 | 비고 |
|---|---|---|---|
| 1. 기획-UX | ✅/❌ | __ min | |
| 2. 설계 | ✅/❌ | __ min | |
| 3. 구현 | ✅/❌ | __ min | |
| 4. 디자인 | ✅/❌ | __ min | |
| 5. 버그픽스 | ✅/❌ | __ min | |
```

---

## 8. 참고

- `docs/harness-spec.md §4` — 루프 게이트 정의
- `docs/harness-architecture.md §2~5` — 훅 흐름 / 핸드오프 / 세션
- `docs/smoke-test-guide.md` — 코어 자동 검증 (E2E 전 사전 단계)
- `orchestration/policies.md §6` — 자동 게이트 동작
- `agents/*.md` — 각 에이전트 책임/권한
