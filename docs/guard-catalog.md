# Guard Catalog — Phase 2 W1

> Status: W1 (catalog gate before redesign). Origin: 2026-04-28 jajang dogfooding 회고 (12 reactive PR / 4 카테고리).
> Scope: 7 hooks under `hooks/`. 정책 재설계 결정의 1차 산출물 — W2 코드 변경의 게이트.

---

## 0. W1 게이트 결정 (재설계 범위)

| Guard | Phase 2 W2 포함? | 근거 |
|---|---|---|
| `agent-boundary.py` | **포함** (HIGH) | jajang scope strict 사고의 진앙. ALLOW_MATRIX 정적 → 모노레포마다 편집 강요. |
| `commit-gate.py` | **포함** (HIGH) | staged 파일 `^src/` regex 가 ALLOW_MATRIX 와 별개 소스 — drift 위험. Gate 1/3/4 책임 비대. |
| `agent-gate.py` | **포함** (HIGH) | stale `HARNESS_ACTIVE` flag silent-pass. 추적 ID regex 단일 방어선. |
| `skill-gate.py` | **포함** (MEDIUM) | live.json.skill 기록 silent 실패 = downstream agent-boundary false-block 체인 진앙 (5번째 위험). |
| `skill-stop-protect.py` | **부분 포함** (MEDIUM) | auto_release/TTL/max_reinforcements 패턴이 가장 robust. **이 모델을 다른 가드로 일반화**하는 reference. 자체 코드는 layered defense 진단 가시성 최소 변경만. |
| `issue-gate.py` | **제외** (LOW) | 30 LOC 단순. 동작 모델 ("ISSUE_CREATORS 활성 외 deny") 가 이미 결정론적. fail mode 가 항상 false-block (보안적으로 안전). 단일 fail mode 라 layered 불필요. |
| `plugin-write-guard.py` | **제외** (LOW) | 보안 가드. allowlist (사실상 blocklist + ENV 우회) 모델 유지가 정답. 모노레포 동기 없음. drift 무관. |

**제외 가드의 W4 layered defense 참여 정책**:
- `issue-gate.py` 와 `plugin-write-guard.py` 도 W4 의 진단 가시성 표준 ("silent 실패 = stderr 경고") 만 흡수.
- 모델 변경은 없다.

---

## 1. 7-Guard 요약 표

| 가드 | 보호 대상 | 현재 모델 | 환경 가정 | Fail mode | 재설계 권장 |
|---|---|---|---|---|---|
| `agent-boundary.py` | 책임 분리 (file ownership) + 일관성 | 정적 ALLOW_MATRIX (regex 화이트리스트) + READ_DENY_MATRIX + HARNESS_INFRA_PATTERNS | 단일 레포 + `src/`, `apps/<x>/src/`, `packages/<x>/src/` 셋만 monorepo. agent 추가 시 코드 편집. | engineer **false-block** — 모노레포 신규 디렉토리 (`services/`, `libs/`) 차단. 가정 깨질 때 reactive 패치 발생. | **workspace-aware allowlist**: `harness.config.json` `engineer_scope` 동적 로드 + 합리적 default fallback. Read 경계 = 보안 가드, allowlist 유지. |
| `commit-gate.py` | 추적성 (Gate 1) + 일관성 (Gate 4 doc-sync) + 책임 분리 (Gate 5 LGTM) | regex 다발 (gh/tracker mutate, executor.sh, `^src/` staged) + flag 파일 존재 확인 | staged 파일이 `^src/` 로 시작 (단일 레포). doc_sync 스크립트 위치 고정. | **Gate 5 silent-pass** — staged 가 `apps/<x>/src/` 면 `^src/` 미매치 → LGTM 우회. **Gate 1 false-block** — main branch 외 시나리오 보존이 수동. | **single source 의 staged 파일 패턴** — agent-boundary `engineer_scope` 와 같은 config 키에서 파생. Gate 별 책임 분리 (mutate / interview / commit) 명시. |
| `agent-gate.py` | 워크플로우 강제 + 추적성 + 책임 분리 | flag 존재 (HARNESS_ACTIVE) + 추적 ID regex `#\d+\|LOCAL-\d+` + branch check + Mode regex | flag 청소가 PostToolUse 또는 정상 종료 경로에서만. tracker 백엔드 항상 활성. | **silent-pass** — stale `HARNESS_ACTIVE` flag 시 메인 Claude 의 engineer 직접 호출이 통과 (PR #11 가 retry escalate_history 청소만 처리. flag 자체는 미보호). 추적 ID regex 1회 실패 시 deny — alias/normalize 부재. | flag **age check + GC** (skill-stop-protect 의 TTL/auto_release 패턴 일반화). 추적 ID 검증을 `tracker.parse_ref()` 위임 (백엔드 단일 책임). |
| `issue-gate.py` | 책임 분리 (이슈 생성/수정 = qa/designer/architect/product-planner 만) | live.json.agent ∈ ISSUE_CREATORS 이외 deny | live.json 기록 정상 작동 가정 (= skill-gate/agent-gate 의존). | **false-block** (안전한 방향). live.json silent 쓰기 실패 시 ISSUE_CREATORS 활성도 차단됨. | **유지**. 단일 fail mode = 보안적 정답. silent 의존 체인은 W4 진단 가시성으로 해결. |
| `skill-gate.py` | 일관성 (스킬 맥락 → 다른 가드의 false-block 방지) | live.json.skill 갱신만 (deny 없음) — passive recorder | live.json 디렉토리 쓰기 가능 + atomic_write_json 정상. | **silent 실패** — 쓰기 실패 시 다른 가드 (agent-boundary) 가 스킬 컨텍스트 못 읽어 정당한 작업 false-block. **5번째 위험 패턴의 진앙**. | 쓰기 실패 stderr 경고 + 진단 hook (live.json 쓰기 결과 코드 집계). 모델 자체는 유지. |
| `skill-stop-protect.py` | 워크플로우 강제 (medium/heavy 스킬 조기 종료 방지) | TTL 기반 auto_release + max_reinforcements + SELF_MANAGED_LIFECYCLE 예외 + harness_kill 신호 우선 | live.json.skill 가 정직하게 기록. 시간 측정 가능. | **선의의 차단**. TTL 도달 시 auto_release 로 graceful. 최악 시 max_reinforcements 도달 → 통과. **현존 가드 중 가장 robust**. | **변경 최소화** — 이 모델을 agent-gate 의 stale flag, agent-boundary 의 stale live.json.agent 에 일반화하는 reference. 자체는 진단 로그 표준만. |
| `plugin-write-guard.py` | 보안 (CC 플러그인 매니저 영역 보호) | `~/.claude/plugins/{cache,marketplaces,data}/` 경로 prefix 차단 + `CLAUDE_ALLOW_PLUGIN_EDIT=1` 우회 | Plugin 매니저가 위 3개 디렉토리를 관리. ENV 우회는 개발 세션 한정. | **false-block** (안전한 방향). Bash 실행은 차단하지 않음 — 정상 동작. | **유지**. Allowlist 유지. 모노레포 가정 영향 없음. 보안 가드의 정답 모델. |

---

## 2. 가드별 상세 (1페이지 × 7)

### 2.1 `agent-boundary.py`

**보호 대상**: 책임 분리 (각 에이전트가 자기 역할 범위 안 파일만 수정) + 일관성 (HARNESS_INFRA_PATTERNS 차단으로 인프라/프로젝트 분리) + 일부 보안 (Read deny matrix 로 plan-reviewer 가 src/ 못 읽음 등 역방향 오염 차단).

**현재 모델**: 정적 dict ALLOW_MATRIX (engineer/architect/designer/test-engineer/product-planner/ux-architect 별 regex 리스트). HARNESS_INFRA_PATTERNS 는 모든 에이전트 공통. READ_DENY_MATRIX 는 별도. `live.json.agent` 단일 소스로 활성 에이전트 판정 (Phase 3 단일화).

**현재 환경 가정**:
- 워크스페이스 구조가 `src/`, `apps/<name>/src/`, `apps/<name>/app/`, `apps/<name>/alembic/`, `packages/<name>/src/`, `apps/<name>/*.toml`, `apps/<name>/*.cfg` 7개 패턴으로 충분.
- 새 monorepo 도입 시 코드 편집 + 배포.
- 핸드오프 디렉토리는 `*_handoffs/` regex 한 줄로 매칭.

**가정 깨질 때 fail mode**: **false-block**. jajang dogfooding 에서 `services/api/`, `libs/sdk/` 등의 경로 추가 시 engineer 가 매번 차단. 메인 Claude 가 agent-boundary 직접 패치를 시도하면 I-9 (인프라 메인 단독 변경 금지) 위반 → 위임 → 카탈로그/계획 → 코드 → PR 의 전체 사이클 반복.

**재설계 권장 (qa 결정 A 반영)**:
- ALLOW_MATRIX engineer 키만 동적화 — `harness.config.json` 의 `engineer_scope` (list[regex]) 키 신규.
- 누락 시 **default fallback** = 현재 7 패턴 (회귀 방어).
- Read 경계 (READ_DENY_MATRIX, HARNESS_INFRA_PATTERNS) 는 **보안 가드** — 정적 allowlist 유지. 보호 대상 다름.
- staged rollout: `HARNESS_GUARD_V2_AGENT_BOUNDARY=1` 일 때만 동적 로드 활성. off 시 현재 정적 매트릭스 유지.

**jajang 연관 PR**: PR #4, #7, #10 (path hardcode 잔존 카테고리 — 본 가드의 ALLOW_MATRIX 도 같은 환경 가정 위에 표현되어 있음).

---

### 2.2 `commit-gate.py`

**보호 대상**: 추적성 (Gate 1 = gh issue/tracker mutate 메인 Claude 직접 호출 차단) + 워크플로우 강제 (Gate 3 = 인터뷰 진행 중 executor 호출 차단) + 일관성 (Gate 4 = check_doc_sync.py 실행) + 책임 분리 (Gate 5 = src/ commit 전 pr-reviewer LGTM 필요).

**현재 모델**: regex 다발. `gh issue (create|edit)`, `gh api ... issues ... POST/PATCH`, `harness.tracker (create-issue|comment)` → ISSUE_CREATORS 활성 아니면 deny. staged 파일 `^src/` 매치 + main branch → flag 파일 (`{prefix}_pr_reviewer_lgtm`) 존재 확인.

**현재 환경 가정**:
- staged 파일 패턴이 `^src/` 만으로 충분 (단일 레포).
- ISSUE_CREATORS 판정은 live.json.agent 정상 기록 가정.
- `scripts/check_doc_sync.py` 는 프로젝트 루트 cwd 기준 — 다른 cwd 에서 호출 시 silent skip.
- main/master 외 branch = LGTM 우회 (정책 결정).

**가정 깨질 때 fail mode**:
- **Gate 5 silent-pass**: staged 가 `apps/<x>/src/foo.ts` 면 `^src/` 미매치 → has_src=False → LGTM 검사 skip. 모노레포에서 책임 분리 실종. `agent-boundary.ALLOW_MATRIX` 와 같은 monorepo 패턴을 인지하지만 정의가 별도 소스에 있음 → drift.
- **Gate 1 false-block**: tracker CLI 가 신규 변형 (e.g. `harness.tracker create-comment` 신규 sub) 도입 시 regex 미매치 → 메인 Claude 통과.
- **Gate 4 silent-skip**: cwd 가 프로젝트 루트 아니면 doc_sync skip.

**재설계 권장 (qa 결정 C 반영)**:
- staged 파일 패턴을 **agent-boundary 와 같은 source** (= `engineer_scope` config) 에서 파생. 단일 수정점.
- 의사코드:
  ```python
  scope_patterns = load_engineer_scope()  # agent-boundary.py 와 공유
  staged_re = compile_or(scope_patterns)  # ^src/, ^apps/.../src/, ...
  has_engineer_change = bool(staged_re.search(staged))
  ```
- Gate 1 의 mutate 패턴은 `tracker` 모듈이 노출하는 `MUTATING_SUBCOMMANDS` 상수로 위임 (확장 시 단일 수정).
- staged rollout: `HARNESS_GUARD_V2_COMMIT_GATE=1` 일 때 동적 패턴 활성. off 시 현행 `^src/`.
- **회귀 위험**: regex 컴파일 실패 시 except pass 가 silent-bypass 를 만든다 — 명시적 fallback (`patterns or ["^src/"]`) + stderr 경고 표준화.

**jajang 연관 PR**: PR #1 (tracker 추상화 — Gate 1 가드 확장에 직접 영향), PR #10 (audit cleanup) — Gate 4 doc_sync 스크립트 정합성.

---

### 2.3 `agent-gate.py`

**보호 대상**: 워크플로우 강제 (engineer 등 HARNESS_ONLY_AGENTS 는 executor.py 경유 필수) + 추적성 (ISSUE_REQUIRED_AGENTS 호출 시 추적 ID 필수) + 책임 분리 (architect/validator Mode-level 게이트 + engineer feature branch 강제 + background 금지).

**현재 모델**:
- `HARNESS_ACTIVE` flag 존재 → executor 경유로 판단 (메인 직접 호출 deny 회피).
- 추적 ID 검증 = `re.search(r"#\d+|LOCAL-\d+", prompt)` 단일 regex. SYSTEM_DESIGN/TECH_EPIC 등은 exempt.
- Mode 검증 = architect/validator prompt 내 키워드 정규식.
- engineer 활성 시 feature branch 검사 (subprocess git rev-parse).
- live.json.agent 기록 = `ss.update_live(session_id, agent=agent)`.

**현재 환경 가정**:
- `HARNESS_ACTIVE` flag 가 정상 lifecycle 종료 시 청소됨 (post-agent-flags.py 가 책임).
- 추적 ID 형식이 `#N` 또는 `LOCAL-N` 만. 다른 백엔드 (예: Linear `LIN-123`, GitLab `!42`) 도입 시 regex 확장 필요.
- session_id 가 stdin 에서 파싱 가능 (Phase 3 SSOT).

**가정 깨질 때 fail mode**:
- **silent-pass**: PR 또는 외부 종료로 stale `HARNESS_ACTIVE` flag 잔존 시 메인 Claude 의 engineer 호출이 통과. PR #11 의 `--force-retry` escalate_history 청소는 retry 경로만 처리, flag 자체는 미보호.
- **false-block**: 추적 ID regex 1회 실패 (예: `#  123` 공백, `Local-1` 대소문자) → 즉시 deny. alias/normalize 부재.
- **false-block**: engineer 가 worktree 격리 모드에서 `HEAD` resolve 실패 시 try/except 통과 — 그러나 격리 깨졌을 때 main 작업이 silent-pass.

**재설계 권장 (qa 결정 B 반영)**:
- `HARNESS_ACTIVE` flag **age check** — 파일 mtime 기준 TTL (default 6h) 초과 시 자동 GC + 진단 로그.
  - skill-stop-protect 의 `started_at + ttl_sec` 패턴 일반화 (qa 결정 E).
- 추적 ID 검증을 `tracker.parse_ref(prompt)` 위임 — 백엔드별 형식 (GitHub `#N`, Local `LOCAL-N`, 향후 Linear/GitLab) 단일 책임.
- staged rollout: `HARNESS_GUARD_V2_AGENT_GATE=1` 일 때 age check + tracker.parse_ref 위임. off 시 현행.
- **회귀 위험**: TTL 너무 짧으면 장시간 engineer 중도 차단 — default 6h 보수적 + heartbeat (`harness/executor.py` 가 매 attempt mtime touch).

**jajang 연관 PR**: PR #5/#8/#9 (marker fragility — 추적 ID 검증도 같은 단일 regex 패턴 결함), PR #6/#11 (state persistence stuck — flag 잔존 사례).

---

### 2.4 `issue-gate.py`

**보호 대상**: 책임 분리 (이슈 생성/수정 = qa/designer/architect/product-planner 만, 메인 Claude 직접 호출 금지 — orchestration/policies.md 정책 3).

**현재 모델**: live.json.agent ∈ ISSUE_CREATORS 인지만 검사. 그 외 모두 deny. 30 LOC.

**현재 환경 가정**: live.json 기록이 정상 작동 (skill-gate / agent-gate 가 SSOT 갱신). MCP `create_issue/update_issue` 만 차단 대상.

**가정 깨질 때 fail mode**: **false-block** (안전한 방향). live.json 쓰기 silent 실패 시 ISSUE_CREATORS 활성도 차단 — 보안적으로 정답이지만 사용자 confusion 유발 (5번째 위험 = silent dependency chain).

**재설계 권장**: **W2 범위 외**. 모델 단순 + 단일 fail mode = 보안 가드의 정답. 다만 W4 의 layered defense 진단 가시성 (live.json 쓰기 실패 stderr 경고 표준화) 은 모든 가드 공통이므로 자동 흡수.

**jajang 연관 PR**: 없음 (이 가드가 야기한 사고 0건).

---

### 2.5 `skill-gate.py`

**보호 대상**: 일관성 (스킬 맥락을 live.json.skill 에 기록 → 다른 훅이 정당한 작업을 false-block 하지 않음). passive recorder. deny 없음.

**현재 모델**: PreToolUse(Skill) 트리거 → tool_input 의 skill/skillName/name 에서 추출 → `ss.set_active_skill(sid, name, level)` 호출. 실패 시 except pass.

**현재 환경 가정**:
- live.json 디렉토리 쓰기 가능.
- atomic_write_json 정상 동작.
- session_id stdin 파싱 또는 current_session_id() 폴백 가능.

**가정 깨질 때 fail mode**: **silent 실패 — 5번째 위험 패턴의 진앙**. 쓰기 실패 시:
1. live.json.skill 미갱신.
2. agent-boundary.py 가 활성 스킬 못 읽음.
3. 메인 Claude 의 정당한 docs/src 읽기 (예: /qa 의 src 분석) 가 false-block.
4. 사용자에게 "왜 막혔는지" 진단 부재 — confusing UX.

**재설계 권장 (qa 결정 D 반영)**:
- 쓰기 실패 시 **stderr 경고** 표준화 — `[skill-gate] WARN: live.json.skill write failed: <err>`. 차단은 하지 않음 (passive recorder 본질 유지).
- 진단 카운터 — `harness-state/.logs/skill-gate.jsonl` 에 success/fail 집계.
- staged rollout: `HARNESS_GUARD_V2_SKILL_GATE=1` 일 때 진단 출력 활성. off 시 현행 silent except pass.
- **회귀 위험**: stderr 가 항상 출력되면 정상 흐름에 노이즈. 실패 케이스만 출력하도록 except 분기 명확화.

**jajang 연관 PR**: 없음 (잠재 위험 — qa 진단에서 발견).

---

### 2.6 `skill-stop-protect.py`

**보호 대상**: 워크플로우 강제 (medium/heavy 스킬 도중 Stop 발동 시 조기 종료 방지 — 사용자 실수로 ralph-loop 이 끊기는 사고 차단).

**현재 모델**:
- `harness_kill` 신호 → 즉시 청소 + 통과.
- `should_block_stop(name, level)` → SELF_MANAGED_LIFECYCLE (ralph-loop 등) 제외 + level ∈ {medium, heavy} 이면 보호.
- `started_at + ttl_sec` 또는 `reinforcements >= max_reinforcements` 도달 → auto_release + 통과.
- 그 외 → reinforcements +1, Stop 차단 (continue 메시지 주입).

**현재 환경 가정**:
- live.json.skill 정직한 기록 (skill-gate 의존).
- 시간 측정 가능 (time.time()).
- skill_protection.py 의 LEVEL_POLICIES 가 reasonable.

**가정 깨질 때 fail mode**: **선의의 차단**. TTL 도달 시 auto_release 로 graceful. 최악 시 max_reinforcements 도달 → 통과. 사용자가 진짜로 멈추고 싶으면 `/harness-kill` 신호로 즉시 청소. **현존 가드 중 가장 robust**.

**재설계 권장**: **변경 최소화**. 이 모델 (TTL + max_reinforcements + auto_release + kill signal + SELF_MANAGED_LIFECYCLE) 을 agent-gate 의 stale `HARNESS_ACTIVE` flag, agent-boundary 의 stale live.json.agent GC 에 **일반화** — qa 결정 E.
- 자체 코드 변경: 진단 로그 포맷 표준화 (skill-gate / agent-gate / agent-boundary 모두 같은 `harness-state/.logs/*.jsonl` 형식).
- staged rollout: `HARNESS_GUARD_V2_SKILL_STOP_PROTECT=1` 일 때 표준 로그 활성. off 시 현행 (이미 robust).

**jajang 연관 PR**: 없음 (이 가드는 jajang 사고 미유발 — 다만 reference 모델로 다른 가드 재설계에 활용).

---

### 2.7 `plugin-write-guard.py`

**보호 대상**: 보안 (CC 플러그인 매니저 영역 — `~/.claude/plugins/{cache,marketplaces,data}/` 직접 수정 차단. 재설치 drift / 추적 불가능 오염 방지).

**현재 모델**: PreToolUse(Write/Edit) 만. 경로 prefix 매칭 (`_is_under`) → deny. `CLAUDE_ALLOW_PLUGIN_EDIT=1` 환경변수 우회. Bash 실행은 차단하지 않음 (스크립트 실행 = 정상).

**현재 환경 가정**: plugin 매니저가 위 3개 디렉토리만 관리. 사용자 경로 정규화 (`Path.expanduser().resolve()`) 가능.

**가정 깨질 때 fail mode**: **false-block** (안전한 방향). symlink resolution 실패 시 abspath fallback — 보수적. ENV 우회 잘못 활성 시 silent-pass 가능 — 그러나 명시적 사용자 결정.

**재설계 권장**: **유지 (W2 제외)**. 보안 가드의 정답 모델 (allowlist + 명시적 ENV 우회). 모노레포 가정 영향 없음. drift 무관. W4 진단 가시성만 흡수.

**jajang 연관 PR**: 없음 (이 가드가 야기한 사고 0건).

---

## 3. Cross-Guard Silent Dependency Chain (5번째 위험 패턴)

plan.md 의 4 카테고리 (path / marker / state / scope) 외에 qa 진단에서 추가 발견된 패턴.

### 3.1 의존 그래프

```
                ┌─────────────────────────────────────────────┐
                │           live.json (SSOT)                  │
                │  { agent, skill, session_id, ... }          │
                └─────────────────────────────────────────────┘
                       ▲                          │
                       │ writes                   │ reads
                       │                          ▼
   ┌────────────────────┐                   ┌─────────────────────┐
   │ skill-gate.py      │                   │ agent-boundary.py   │
   │ (PreToolUse Skill) │                   │ (PreToolUse W/E/R)  │
   │ — passive recorder │                   │ — read skill ctx,   │
   │   set_active_skill │                   │   active_agent      │
   └────────────────────┘                   └─────────────────────┘
                                                      ▲
   ┌────────────────────┐                             │
   │ agent-gate.py      │  writes agent ──────────────┤
   │ (PreToolUse Agent) │                             │
   │ — update_live      │                             │
   │   agent=agent      │                             │
   └────────────────────┘                             │
                                                      │
   ┌────────────────────┐                             │
   │ issue-gate.py      │  reads agent ───────────────┤
   │ (PreToolUse MCP)   │                             │
   └────────────────────┘                             │
                                                      │
   ┌────────────────────┐                             │
   │ commit-gate.py     │  reads agent (Gate 1) ──────┘
   │ (PreToolUse Bash)  │
   └────────────────────┘
```

### 3.2 Failure Cascade

**Scenario A — skill-gate 쓰기 실패**:
1. `skill-gate.py` 가 `live.json.skill` 갱신 실패 (디스크 풀, 권한 변경, atomic_write 충돌).
2. `agent-boundary.py` 가 활성 스킬 없음으로 판단.
3. 메인 Claude 의 정당한 작업 (예: `/qa` 가 src/ 읽기) 이 file-ownership 룰로 false-block.
4. 사용자: "왜 막혔는지" 진단 부재. agent-boundary 의 deny 메시지에 skill-gate 실패 흔적 없음.

**Scenario B — agent-gate 쓰기 실패**:
1. `agent-gate.py` 가 `live.json.agent` 갱신 실패.
2. `issue-gate.py` 가 ISSUE_CREATORS 활성 아님으로 판단 → qa/designer 활성 호출도 deny.
3. `commit-gate.py` Gate 1 도 같은 판단 → tracker mutate 차단.
4. 사용자: "qa 가 활성인데 왜 차단?" — 5번째 위험 패턴.

### 3.3 W4 layered defense 명세 요구사항

W4 단계에서 다음을 통합 처리:

1. **진단 가시성 표준** — 모든 live.json 쓰기 실패 시 stderr 경고 + `harness-state/.logs/<guard>.jsonl` 집계.
2. **Layered fallback 정책** — 1차 (live.json) 실패 → 2차 (env var HARNESS_AGENT_NAME) → 3차 (deny with diagnostic). 단, **deny 결정은 1차 단독** (defense-in-depth ↔ determinism 정책 — 차단은 결정론, fallback 은 informational).
3. **End-to-end 진단** — `harness/executor.py` 시작 시 live.json 쓰기 round-trip 테스트 → 실패 시 즉시 ESCALATE (downstream silent cascade 사전 차단).
4. **deny 메시지 enrichment** — agent-boundary/issue-gate/commit-gate 의 deny 메시지에 "live.json 쓰기 진단" 링크 추가 (사용자가 "왜 막혔는지" 즉시 확인).

이 4개 항목은 W2/W4 코드 작업의 일부로 처리하되, 현재 W1 단계에서는 catalog 의 요구사항으로만 고정한다.

---

## 4. W2 후속 작업 인덱스

각 가드의 **재설계 권장** 섹션은 다음 impl 계획 파일과 1:1 대응:

- 통합 impl 계획: `docs/impl/13-guard-realignment.md` (W1~W5 단계별 변경 명세)
- 가드별 sub-task: 위 impl 의 W2 섹션에서 sub-commit 단위로 분리

W3 (spec/architecture 갱신) 은 별도 architect 호출에서 처리 — 본 카탈로그가 게이트.
