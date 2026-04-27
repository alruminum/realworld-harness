# Harness Architecture (TRD 대체) — RealWorld Harness

> `harness-spec.md`의 불변식·게이트를 구현하는 훅·코어·상태·경계 정책 정의.
> 시스템 동작 추적은 본 문서로, 의도·목적은 spec 문서로 분리.
>
> **본 문서는 `~/.claude/docs/harness-architecture.md` 에서 마이그레이션됐다.** 본문은 source 그대로 보존하고, RWHarness 컨텍스트(플러그인 배포)에 맞춰 점진적으로 갱신될 예정이다. **Phase 1에 경로 추상화(`Path.home()` → `${CLAUDE_PLUGIN_ROOT}`) 반영 예정** (architect/engineer 위임).

마이그레이션: 2026-04-27
원본 source: `~/.claude/docs/harness-architecture.md` @ main `2c231c3`
다음 갱신: Phase 1 — 경로 추상화 + `hooks/hooks.json` (settings.json 훅 → 플러그인 내장)

---

## 1. 시스템 구성요소

| 레이어 | 위치 | 역할 |
|---|---|---|
| **Claude Code** | (외부) | LLM 실행 셸. tool 호출·에이전트 spawn·hook 실행. |
| **Hooks** | `~/.claude/hooks/*.py` | tool 호출 전후 차단·라우팅·경계 강제. 전역(`~/.claude/settings.json`)에서만 등록. |
| **Harness Core** | `~/.claude/harness/` | executor·plan_loop·impl_loop·core(StateDir/Flag)·notify·providers. |
| **Agents** | `~/.claude/agents/*.md` | 역할별 전문 에이전트 정의 (architect, engineer, designer, validator, …). |
| **Skills** | `~/.claude/commands/*.md` | 사용자 트리거 (qa, ux, quick, ralph, …). |
| **State** | `.claude/harness-state/` | 세션·이슈별 플래그·active agent·escalate history. 프로젝트 루트별. |
| **Whitelist** | `~/.claude/harness-projects.json` | 하네스 활성 프로젝트 목록. |

---

## 2. 훅 흐름도

전역 훅 목록은 `~/.claude/settings.json` 의 `hooks` 섹션에 등록되며, `setup-harness.sh` 코멘트 블록(line 6-27)에 카탈로그가 동기화되어 있다.

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
| `.no-harness` 마커 / `softcarry` 프로젝트명 / `HardcarryDryRun` | bypass | `agent-boundary.py`, `agent-gate.py` |
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
    "/Users/dc.kim/.claude",
    "/Users/dc.kim/project/jajang",
    "/Users/dc.kim/project/memoryBattle"
  ]
}
```

### 5.2 활성화 판정 (`harness_common.is_harness_enabled`)

```
HARNESS_FORCE_ENABLE=1 → True
cwd가 화이트리스트 경로 또는 그 서브디렉토리 → True
그 외 → False (모든 훅 조기 종료, 메인 무제약)
```

### 5.3 등록·해제

| 동작 | 방법 |
|---|---|
| 등록 | 프로젝트 루트에서 `bash ~/.claude/setup-harness.sh` |
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

---

## 6. 변경 이력 추적

모든 하네스 인프라 변경은 `HARNESS-CHG-YYYYMMDD-NN` 식별자를 가진다.

- `~/.claude/orchestration/changelog.md` — 변경 항목 + 동기 + 검증
- 커밋 메시지 본문에 동일 식별자 포함
- `docs/impl/` — 변경별 impl 계획 (architect 작성)

본 문서(`harness-architecture.md`)와 `harness-spec.md`는 위 변경마다 관련 섹션 갱신 필요. 메모리 `feedback_doc_sync` 원칙 적용.

> RWHarness 컨텍스트: 본 문서는 플러그인 배포판으로 마이그레이션 중이다. Phase 1에서 §1 (`~/.claude/...` 경로) → `${CLAUDE_PLUGIN_ROOT}/...` 추상화, §2.1 (settings.json hooks) → `hooks/hooks.json` 내장형으로 갱신 예정. 본 문서 자체의 변경은 RWHarness `orchestration/policies.md` Change-Type `spec` 으로 분류 → `orchestration/changelog.md` + `orchestration/rationale.md` 양쪽 항목 필수.
