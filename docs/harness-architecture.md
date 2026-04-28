# Harness Architecture (TRD 대체)

> `harness-spec.md`의 불변식·게이트를 구현하는 훅·코어·상태·경계 정책 정의.
> 시스템 동작 추적은 본 문서로, 의도·목적은 spec 문서로 분리.

작성: 2026-04-27 / 최근 갱신: §5 가드 정책 일람 + Layered Defense + Staged Rollout (`HARNESS-CHG-20260428-13`)

---

## 1. 시스템 구성요소

| 레이어 | 위치 | 역할 |
|---|---|---|
| **Claude Code** | (외부) | LLM 실행 셸. tool 호출·에이전트 spawn·hook 실행. |
| **Hooks** | `${CLAUDE_PLUGIN_ROOT}/hooks/*.py` | tool 호출 전후 차단·라우팅·경계 강제. 플러그인 내장 `hooks/hooks.json` 자동 로드 (개발 폴백: `~/.claude/settings.json` 의 hooks 섹션). |
| **Harness Core** | `${CLAUDE_PLUGIN_ROOT}/harness/` | executor·plan_loop·impl_loop·core(StateDir/Flag)·notify·providers. |
| **Agents** | `${CLAUDE_PLUGIN_ROOT}/agents/*.md` | 역할별 전문 에이전트 정의 (architect, engineer, designer, validator, …). |
| **Skills** | `${CLAUDE_PLUGIN_ROOT}/commands/*.md` | 사용자 트리거 (qa, ux, quick, ralph, …). |
| **State** | `.claude/harness-state/` | 세션·이슈별 플래그·active agent·escalate history. 프로젝트 루트별. |
| **Whitelist** | `~/.claude/harness-projects.json` | 하네스 활성 프로젝트 목록 (사용자 home 기준). |

---

## 2. 훅 흐름도

훅 등록은 플러그인 내장 `hooks/hooks.json` 이 Claude Code 의 install 시 자동 로드된다. 개발 폴백 모드에선 `~/.claude/settings.json` 의 `hooks` 섹션 사용. 카탈로그는 `scripts/setup-rwh.sh` 코멘트와 본 문서 §2.1 표에 동기화되어 있다.

### 2.1 이벤트별 훅 체인

| 이벤트 | matcher | 훅 체인 (순서) | 차단 능력 |
|---|---|---|---|
| `SessionStart` | — | `harness-session-start.py` | additional context 주입 |
| `UserPromptSubmit` | — | `session-agent-cleanup.py` → `harness-router.py` → `harness-review-inject.py` | additional context 주입 |
| `PreToolUse` | Edit, Write | `plugin-write-guard.py` → `orch-rules-first.py` → `agent-boundary.py` | block + reason |
| `PreToolUse` | Read | `agent-boundary.py` | block (인프라 파일·금지 경로) |
| `PreToolUse` | Bash | `harness-drift-check.py` → `commit-gate.py` | block (UX 드리프트·커밋 룰 위반) |
| `PreToolUse` | Agent | `agent-gate.py` | block (이슈번호 누락·harness_active 누락·HARNESS_ONLY 직접 호출) |
| `PreToolUse` | Skill | `skill-gate.py` | Phase 4: 스킬 호출 제약 |
| `PreToolUse` | `mcp__github__create_issue` / `update_issue` | `issue-gate.py` | block |
| `PostToolUse` | Edit | `harness-settings-watcher.py` | settings.json 변경 감지 → 동기화 알림 |
| `PostToolUse` | Bash | `post-commit-cleanup.py` → `harness-review-trigger.py` | 1회성 플래그 정리 + 리뷰 트리거 |
| `PostToolUse` | Agent | `post-agent-flags.py` | `harness_active` 등 플래그 set/clear |
| `PostToolUse` | Skill | `post-skill-flags.py` | Phase 4 |
| `Stop` | — | `afplay Glass.aiff` → `skill-stop-protect.py` → `ralph-session-stop.py` → `harness-review-stop.py` | 종료 알림 + 리뷰 스냅샷 |

기본 훅 timeout 5초, `harness-router.py`만 30초.

### 2.2 차단 우회 조건

| 조건 | 효과 | 출처 |
|---|---|---|
| `HARNESS_FORCE_ENABLE=1` env | 화이트리스트 무관 활성화 | `harness_common.is_harness_enabled()` |
| 프로젝트가 화이트리스트 미등록 | 모든 훅 조기 종료 (sys.exit(0)) | 동상 |
| `is_infra_project()` True | 인프라 파일 경계 해제 | `agent-boundary.py:29-56` |
| `.no-harness` 마커 파일 (프로젝트 루트) | bypass | `agent-boundary.py` |
| `CLAUDE_ALLOW_PLUGIN_EDIT=1` | 플러그인 디렉토리 Edit 일시 허용 | `plugin-write-guard.py` |

---

## 3. 에이전트 핸드오프 매트릭스

### 3.1 에이전트 호출 권한

`HARNESS_ONLY_AGENTS = ("engineer",)` — 메인이 Agent 도구로 직접 호출 차단. `executor.py impl` 경유 필수.

Mode별 게이트(`agent-gate.py`):

| Agent | Mode | 직접 호출 허용? | 비고 |
|---|---|---|---|
| architect | SYSTEM_DESIGN, TASK_DECOMPOSE, TECH_EPIC, LIGHT_PLAN, DOCS_SYNC | O | 메인 직접 |
| architect | MODULE_PLAN, SPEC_GAP | X | impl_loop / plan_loop 경유 |
| validator | DESIGN_VALIDATION | O | 메인 직접 |
| validator | PLAN_VALIDATION, CODE_VALIDATION, BUGFIX_VALIDATION | X | 루프 경유 |
| 그 외 커스텀 에이전트 | — | O (단, harness_active 플래그 필요한 경우 별도 게이트) | designer, ux-architect, qa, pr-reviewer, design-critic, security-reviewer, product-planner, test-engineer |

### 3.2 Write/Edit 허용 경로 (`agent-boundary.py:80-112`)

| 에이전트 | 허용 경로 |
|---|---|
| engineer | `src/**` |
| architect | `docs/**`, `backlog.md`, `trd.md` |
| designer | `design-variants/**`, `docs/ui-spec*` |
| test-engineer | `src/__tests__/**`, `*.test.*`, `*.spec.*` |
| product-planner | `prd.md`, `stories.md` |
| ux-architect | `docs/ux-flow.md` |
| validator / design-critic / pr-reviewer / qa / security-reviewer | (없음 — 판정 전용) |

### 3.3 Read 금지 경로 (`agent-boundary.py:114-135`)

| 에이전트 | 금지 |
|---|---|
| product-planner | `src/`, `docs/impl/`, `trd.md` |
| designer | `src/` |
| test-engineer | `src/` (impl 외), 도메인 문서 |
| plan-reviewer | `src/`, `docs/impl/`, `trd.md` |

전 에이전트 공통 인프라 패턴 차단:
```python
HARNESS_INFRA_PATTERNS = [
    r'[./]claude/',
    r'hooks/',
    r'harness-(executor|loop|utils)\.sh',
    r'orchestration-rules\.md',
    r'setup-(harness|agents)\.sh',
]
```
인프라 프로젝트(`is_infra_project()` True)에서는 위 패턴 해제.

### 3.4 인프라 프로젝트 판정 (`is_infra_project()` — `agent-boundary.py:29-56`)

4개 신호 OR. 하나라도 True면 인프라.

1. `HARNESS_INFRA=1` 환경변수
2. 마커 파일 `~/.claude/.harness-infra` 존재
3. `CLAUDE_PLUGIN_ROOT` 환경변수 non-empty
4. `cwd.resolve() == Path.home() / ".claude"`

> 워크트리 격리 적용 시 cwd가 `.worktrees/` 내부로 빠지므로 신호 4만으로 부족. 신호 1~3 중 하나가 함께 set되어야 인프라 인식 유지 (이슈 #84).

### 3.5 가드 정책 카탈로그 reference

7개 PreToolUse 가드(`agent-boundary`, `commit-gate`, `agent-gate`, `skill-gate`, `skill-stop-protect`, `issue-gate`, `plugin-write-guard`)의 보호 대상 / 현재 모델 / 환경 가정 / fail mode / 재설계 권장은 단일 카탈로그에 집약된다.

→ **`docs/guard-catalog.md`** (Phase 2 W1 산출물, `HARNESS-CHG-20260428-13`).

본 §3.1~§3.4 의 ALLOW_MATRIX, READ_DENY_MATRIX, HARNESS_INFRA_PATTERNS 표는 catalog 의 실행 표현이다. 가드별 1페이지 상세는 catalog §2, cross-guard silent dependency chain (5번째 위험) 분석은 catalog §3 참조.

---

## 4. 세션 라이프사이클

### 4.1 상태 디렉토리 구조

```
{project_root}/.claude/harness-state/
├── .sessions/{sid}/
│   ├── live.json                  # 활성 agent / skill / issue 단일 소스
│   └── flags/{prefix}_{issue}/
│       ├── {prefix}_harness_active
│       ├── {prefix}_plan_validation_passed
│       ├── {prefix}_test_engineer_passed
│       ├── {prefix}_validator_b_passed
│       ├── {prefix}_pr_reviewer_lgtm
│       ├── {prefix}_designer_ran
│       └── {prefix}_design_critic_passed
├── .global.json                    # 전역 신호 (lenient read)
├── .session-id                     # 현재 세션 ID
├── {prefix}_escalate_history.json  # 누적 ESCALATE
└── {prefix}_last_issue
```

모두 dot-prefix(숨김) — 에이전트 glob/rm 사고 방지.

### 4.2 단계별 전이

| 단계 | 트리거 | 동작 |
|---|---|---|
| **세션 시작** | SessionStart hook | stale `_active` 1시간 초과 제거, 레거시 `.flags/` → `.sessions/{sid}/flags/` 마이그레이션, `_escalate_history.json` 보존 (HARNESS-CHG-20260426-06) |
| **루프 진입** | `executor.py impl` | `harness_active` set, 이슈별 worktree 생성 (isolation=worktree), 플래그 디렉토리 초기화 |
| **에이전트 핸드오프** | 마커 출력 | `_handoffs/{from}_to_{to}_{ts}.md` 생성, 경로만 다음 에이전트에 전달 |
| **ESCALATE 누적** | fail_type 동일 2회 | architect SPEC_GAP 자동 호출 (HARNESS-CHG-20260426-04) |
| **커밋 후** | PostToolUse(Bash) | `pr_reviewer_lgtm`, `test_engineer_passed` 1회성 플래그 삭제, `orch-rules-first` 리셋 |
| **세션 종료** | Stop hook | 알림음 + 리뷰 스냅샷, 6시간 초과 stale 세션 디렉토리 정리 |

### 4.3 핵심 상수

| 항목 | 값 | 출처 |
|---|---|---|
| Hook timeout (기본) | 5s | settings.json |
| harness-router timeout | 30s | settings.json |
| Stale active 플래그 TTL | 1h | harness-session-start.py |
| Stale 세션 디렉토리 TTL | 6h | post-commit-cleanup.py / Stop |
| 이슈 lock heartbeat | 30m | session_state |
| ESCALATE → SPEC_GAP 임계 | 2회 | impl_loop |
| Hook rate limit | 60s 내 5회 | harness_common |

---

## 5. 화이트리스트 / 경계 정책

### 5.1 화이트리스트 저장소

`~/.claude/harness-projects.json`:
```json
{
  "projects": [
    "/Users/<your-name>/project/<example-project-1>",
    "/Users/<your-name>/project/<example-project-2>"
  ]
}
```

각 프로젝트는 절대 경로로 등록. 사용자가 `setup-rwh.sh` 실행 시 자동 추가된다.

### 5.2 활성화 판정 (`harness_common.is_harness_enabled`)

```
HARNESS_FORCE_ENABLE=1 → True
cwd가 화이트리스트 경로 또는 그 서브디렉토리 → True
그 외 → False (모든 훅 조기 종료, 메인 무제약)
```

### 5.3 등록·해제

| 동작 | 방법 |
|---|---|
| 등록 | 프로젝트 루트에서 `bash "${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/marketplaces/realworld-harness}/scripts/setup-rwh.sh"` |
| 일괄 보기 | `harness-list` 스킬 |
| 활성화 | `harness-enable` 스킬 |
| 해제 | `harness-disable` 스킬 |

### 5.4 src/ 경계 강제

- 메인 Claude는 `src/**` Edit/Write 차단 (`agent-boundary.py`).
- engineer만 `src/**` 허용. 다른 에이전트는 자기 권한 영역만.
- 인프라 프로젝트는 위 경계 해제 (메인이 `~/.claude/hooks/`, `~/.claude/harness/` 직접 수정 가능). 단, `MEMORY.md` 정책상 메인 단독 변경은 금지 — qa→architect→engineer 위임 강제.

### 5.5 워크트리 격리

`harness.config.json` 의 `isolation` 필드:

```json
{"prefix": "proj", "isolation": "worktree"}
```

- `setup-harness.sh` (line 60-91)이 신규 프로젝트에 기본 활성화 (HARNESS-CHG-20260427-01 / PR #74).
- 이슈별 worktree 경로: `{project_root}/.worktrees/{prefix}/issue-{N}/`.
- `.gitignore`에 `.worktrees/` 자동 등록.
- `HARNESS_ISSUE_NUM` env로 훅이 이슈별 플래그 디렉토리 참조.
- `harness/core.py:find_main_repo_root()` — Claude Code Bash가 cwd를 worktree 안에 persist시켜도 main repo로 복귀 (L2 방어).

### 5.6 가드 정책 일람 (catalog 매핑)

7개 PreToolUse 가드의 정책·보호 대상·재설계 범위는 `docs/guard-catalog.md` 가 정본이다. 본 섹션은 architecture 차원의 한 줄 요약 + Phase 2 W2 변경 범위만 명시한다.

| 가드 | 보호 대상 | Phase 2 W2 변경 | 출처 |
|---|---|---|---|
| `agent-boundary.py` | 책임 분리 (file ownership) + 일관성 | engineer scope 동적화 (`engineer_scope` config). Read 경계는 보안 모델 유지. | catalog §2.1 |
| `commit-gate.py` | 추적성(Gate 1) + 일관성(Gate 4) + 책임 분리(Gate 5) | staged 패턴을 `engineer_scope` 와 같은 source 에서 파생 + tracker `MUTATING_SUBCOMMANDS` 위임 | catalog §2.2 |
| `agent-gate.py` | 워크플로우 강제 + 추적성 + 책임 분리 | HARNESS_ACTIVE flag age check + GC + 추적 ID `tracker.parse_ref()` 위임 | catalog §2.3 |
| `skill-gate.py` | 일관성 (스킬 컨텍스트 SSOT) | 쓰기 실패 stderr 경고 + 진단 집계. passive recorder 본질 유지. | catalog §2.5 |
| `skill-stop-protect.py` | 워크플로우 강제 (medium/heavy 보호) | 진단 로그 포맷 표준화. TTL/auto_release 모델은 다른 가드의 reference. | catalog §2.6 |
| `issue-gate.py` | 책임 분리 (이슈 생성/수정 권한) | **모델 변경 없음**. W4 진단 가시성만 흡수. | catalog §2.4 |
| `plugin-write-guard.py` | 보안 (CC 플러그인 매니저 영역) | **모델 변경 없음**. allowlist + ENV 우회 = 보안 가드 정답. | catalog §2.7 |

### 5.7 Defense-in-depth ↔ Determinism 정책 (Layered Defense)

가드 정책은 두 레이어로 구분된다. 각 레이어의 책임 분리는 **결정론**(같은 입력 → 같은 deny/allow 결과)을 보장한다.

#### Blocking layer (결정론 — invariant 강제)

**불변식 위반 시 즉시 차단.** 동일 입력에 동일 deny 결과를 보장.

| 가드 | Blocking 트리거 | 출처 |
|---|---|---|
| `agent-boundary.py` | Write/Edit/Read 가 ALLOW_MATRIX / READ_DENY_MATRIX / HARNESS_INFRA_PATTERNS 위반 시 deny | I-1 / I-9 |
| `plugin-write-guard.py` | `~/.claude/plugins/{cache,marketplaces,data}/` Write/Edit 시 deny (ENV 우회 명시 시 통과) | I-8 |
| `commit-gate.py` Gate 1 | 메인 Claude 가 `gh issue create/edit` / tracker mutate 직접 호출 시 deny | policies.md 정책 3 |
| `commit-gate.py` Gate 5 | `engineer_scope` 매치 staged 파일 + main branch + LGTM 플래그 부재 시 deny | I-1 |
| `agent-gate.py` (HARNESS_ONLY) | `engineer` 직접 Agent 호출 + harness_active 플래그 부재 시 deny | I-2 |
| `agent-gate.py` (추적 ID) | architect/engineer 호출 프롬프트에 `tracker.parse_ref` 매치 부재 시 deny | I-2 |
| `issue-gate.py` | `live.json.agent` ∈ ISSUE_CREATORS 외 mcp__github__create_issue/update_issue 시 deny | policies.md 정책 3 |
| `skill-stop-protect.py` | medium/heavy 스킬 active + Stop 발동 + (TTL/max_reinforcements 미도달) 시 차단 | 워크플로우 보호 |

#### Informational layer (진단 — 차단 결정 권한 없음)

**fail 시 stderr 경고만, deny 결정은 변경하지 않음.** 진단 가시성만 추가.

| 가드 / 헬퍼 | Informational 동작 | 출처 |
|---|---|---|
| `skill-gate.py` | `live.json.skill` 쓰기 실패 시 stderr 경고 + `harness-state/.logs/skill-gate.jsonl` 집계. 차단 없음 (passive recorder). | catalog §2.5 |
| `skill-stop-protect.py` | 진단 로그 표준 포맷 출력. 차단 결정은 별도 blocking 레이어. | catalog §2.6 |
| `agent-boundary.py` (W4) | `live.json.agent` 누락 + `HARNESS_AGENT_NAME` env 존재 시 stderr 경고. **deny 결정은 SSOT(live.json) 단독** — env 폴백은 진단용. | impl §2.3 |
| `harness/executor.py` (W4) | 진입 시 live.json round-trip canary 테스트. 실패 시 즉시 ESCALATE — silent dependency cascade 사전 차단. | impl §2.4 |
| 모든 deny 메시지 (W4) | `live.json` 쓰기 진단 + scope source(static/V2) 표기. 사용자가 "왜 막혔는지" 즉시 확인. | impl §1.1 |

**중요 원칙**:
- **결정론 = blocking layer 의 책임**. informational layer 는 invariant 를 완화하거나 차단 결정에 끼어들지 않는다.
- **silent dependency chain 방어** (catalog §3 5번째 위험): live.json 쓰기 실패 → 다른 가드 false-block 의 cascade 를 informational layer 가 stderr/diag log 로 가시화. **단, 차단 결정은 1차 검증 단독.**
- 두 레이어 분리 위반(예: 진단 실패 시 자동 통과 / 차단 결정에 fallback 끼어들기)은 §0 워크플로우 강제 위반 — `[invariant-shift]` PR 토큰 + rationale Alternatives 필수.

### 5.8 Staged Rollout — `HARNESS_GUARD_V2_*` 환경변수

가드 모델 변경(Phase 2 W2)은 환경변수로 점진 활성화하여 **확정성 우선** 정책을 따른다. 미설정 시 v1 fallback (현행 동작 유지).

| 환경변수 | 가드 | 활성 시 동작 |
|---|---|---|
| `HARNESS_GUARD_V2_AGENT_BOUNDARY=1` | `agent-boundary.py` | ALLOW_MATRIX["engineer"] 동적 로드 (config) + deny 메시지 진단 enrichment |
| `HARNESS_GUARD_V2_COMMIT_GATE=1` | `commit-gate.py` | staged 패턴 동적 + tracker.MUTATING_SUBCOMMANDS 위임 |
| `HARNESS_GUARD_V2_AGENT_GATE=1` | `agent-gate.py` | HARNESS_ACTIVE flag age check + tracker.parse_ref 위임 |
| `HARNESS_GUARD_V2_SKILL_GATE=1` | `skill-gate.py` | 쓰기 실패 stderr 경고 + 진단 집계 |
| `HARNESS_GUARD_V2_SKILL_STOP_PROTECT=1` | `skill-stop-protect.py` | 진단 로그 포맷 표준화 |
| `HARNESS_GUARD_V2_ISSUE_GATE=1` | `issue-gate.py` | (W4 한정) deny 메시지 진단 enrichment |
| `HARNESS_GUARD_V2_PLUGIN_WRITE_GUARD=1` | `plugin-write-guard.py` | (W4 한정) deny 메시지 진단 enrichment |

**보조 환경변수**:

| 환경변수 | 기본값 | 설명 |
|---|---|---|
| `HARNESS_GUARD_V2_FLAG_TTL_SEC` | `21600` (6h) | HARNESS_ACTIVE flag age check TTL |
| `HARNESS_GUARD_V2_DIAG_LOG_DIR` | `harness-state/.logs/` | 진단 로그 디렉토리 |
| `HARNESS_GUARD_V2_ALL=1` | (off) | 7개 가드 V2 일괄 활성 (개발 편의) |

**Rollout 단계** (impl §5.3):
- Stage 0 (Iter 2 merge 직후): 모든 V2 flag off — 회귀 0 확인.
- Stage 1 (jajang 재실측): `AGENT_BOUNDARY` + `COMMIT_GATE` 만 on. 모노레포 시나리오 통과.
- Stage 2 (1주): `AGENT_GATE` 추가. stale flag 시나리오 통과.
- Stage 3 (2주): `SKILL_GATE` + `SKILL_STOP_PROTECT` 추가. 진단 가시성 활성.
- Stage 4 (배포): `HARNESS_GUARD_V2_ALL=1` default — `setup-rwh.sh` 자동 export.

**확정성 우선 원칙**: V2 동작이 production-tested 되기 전까지 환경변수 없이는 v1 동작 보장. 회귀 0 == staged rollout 의 선결 조건.

---

## 6. 추적 백엔드 (tracker)

`harness-spec.md §3 I-2` 가 강제하는 *추적 ID* 의 발급 채널을 추상화한 레이어. `harness/tracker.py` 에 정의된다.

### 6.1 백엔드 종류

| 백엔드 | 저장 매체 | ID 형식 | 가용 조건 |
|---|---|---|---|
| `github` | GitHub Issues (gh CLI 경유) | `#N` | `gh` 설치 + `gh repo view` 성공 (repo 연결됨) |
| `local` | `orchestration/issues/INDEX.jsonl` (append-only) + `.next_id` | `LOCAL-N` | 항상 가용 (마지막 폴백) |

### 6.2 선택 우선순위

```
HARNESS_TRACKER env (강제, 미가용이면 RuntimeError)
    └─ prefer 인자 (호출자 지정)
        └─ github (자동)
            └─ local (마지막 폴백, 항상 가용)
```

- 환경에 `gh` 가 없어도 `local` 로 폴백 → 추적성 보존, 환경 의존 차단.
- `HARNESS_TRACKER=local` 강제 시 GitHub repo 가 있어도 로컬에 기록 (테스트·격리 환경용).

### 6.3 호출 경로

| 호출자 | 경로 | 비고 |
|---|---|---|
| `agents/qa.md` | `mcp__github__create_issue` 우선 → 실패 시 `Bash + python3 -m harness.tracker create-issue` 폴백 | qa frontmatter 의 `tools:` 에 Bash 포함 (tracker CLI 한정 사용) |
| `agents/designer.md` Phase 0-0 | `python3 -m harness.tracker create-issue` 직접 | `designer_active` 플래그 set 동안만 `commit-gate.py` Gate 1 통과 |
| `harness/executor.py impl --issue <REF>` | 호출자 (qa/designer/외부) 가 발급한 `<REF>` 를 그대로 사용 | `<REF>` 형식 검증은 agent-gate.py |
| `hooks/agent-gate.py:78` | `r"#\d+|LOCAL-\d+"` 정규식 — architect/engineer 호출 프롬프트 내 추적 ID 존재 강제 | gh 미설치 환경도 LOCAL-N 으로 통과 가능 |

### 6.4 `commit-gate.py` Gate 1 가드

메인 Claude 가 추적 이슈 생성/수정을 직접 호출하는 것을 차단:

```python
# 차단 대상 (cmd 정규식)
gh\s+issue\s+(create|edit)
gh\s+api\s+.*issues.*--method\s+POST
gh\s+api\s+.*issues.*-X\s+(POST|PATCH)
gh\s+api\s+.*issues/\d+.*-X\s+PATCH
harness\.tracker\s+(create-issue|comment)        # ← 추가됨
harness/tracker\.py\s+(create-issue|comment)     # ← 추가됨
```

`ISSUE_CREATORS` (qa, designer, architect, product-planner) 중 하나가 활성일 때만 통과. 조회 명령(`which`, `get`)은 가드 대상 아님.

### 6.5 LocalBackend 저장 형식

`orchestration/issues/INDEX.jsonl` — 1줄 1엔트리 JSON, append-only:

```json
{
  "id": 1,
  "ref": "LOCAL-1",
  "title": "...",
  "body": "...",
  "labels": ["infra", "invariant-shift"],
  "milestone": null,
  "state": "open",
  "created": "2026-04-28T09:59:59",
  "updated": "2026-04-28T09:59:59",
  "comments": [...]
}
```

`.next_id` — ID 시퀀스 카운터(정수). 단일 호출 가정으로 파일 락 없음.

### 6.6 검증

`tests/pytest/test_tracker.py` — stdlib unittest 16 케이스:
- LocalBackend: 시퀀셜 ID, persistence, get/comment/missing, INDEX.jsonl 형식
- ParseRef: github/local/legacy/invalid
- get_tracker: env 강제, 폴백 순서
- GitHubBackend: gh CLI 가용성 디텍션 (subprocess 모킹)

실행: `python3 -m unittest tests.pytest.test_tracker` (pytest 미의존).

---

## 7. 변경 이력 추적

모든 하네스 인프라 변경은 `HARNESS-CHG-YYYYMMDD-NN` 식별자를 가진다.

- `orchestration/changelog.md` — 변경 항목 + 동기 + 검증 (본 RWHarness repo)
- 커밋 메시지 본문에 동일 식별자 포함
- `docs/impl/` — 변경별 impl 계획 (architect 작성)

본 문서(`harness-architecture.md`)와 `harness-spec.md`는 위 변경마다 관련 섹션 갱신 필요. 메모리 `feedback_doc_sync` 원칙 적용.

> 본 문서의 변경은 `orchestration/policies.md` Change-Type `spec` 으로 분류 → `orchestration/changelog.md` + `orchestration/rationale.md` 양쪽 항목 필수. PR title 에 `[invariant-shift]` 토큰이 필요한 변경(§0 Core Invariant 약화)은 자동 게이트 외 추가 휴먼 거버넌스를 거친다.
