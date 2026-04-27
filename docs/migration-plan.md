# Migration Plan — ~/.claude → realworld-harness 플러그인

> Task-ID: `HARNESS-CHG-20260427-02` (Phase 1)
> 작성: 2026-04-27
> 인풋: `docs/analysis-current-harness.md` (Explore 분석) + `docs/plan-plugin-distribution.md` §4~5

---

## 1. 마이그레이션 원칙

1. **~/.claude는 작동 상태 유지** — RWHarness로 *복사*만 하고 ~/.claude는 건드리지 않는다.
2. **선택적 복사** — `.bak` / 개인용(`softcarry`, `hardcarry`, `dongchan-style`) 제외.
3. **경로 추상화** — `Path.home()` → `Path(os.environ.get('CLAUDE_PLUGIN_ROOT', Path.home() / '.claude'))` 폴백.
4. **`settings.json` hooks → `hooks/hooks.json`** — 플러그인 내장형 전환.
5. **본문 보존, 헤더만 갱신** — 에이전트/오케스트레이션 .md 본문은 그대로. 헤더에 RWHarness 컨텍스트 명시.

---

## 2. Phase 1 sub-section 진행 순서

각 sub-section = 1 commit (메인 직접, Task-ID `HARNESS-CHG-20260427-02` 공유, sub-commit으로 이력 보존).

| # | 단위 | 산출물 |
|---|---|---|
| 1.1 | 인벤토리 + 계획 | 본 문서 |
| 1.2 | `hooks/` 마이그레이션 | Python 훅 활성 22개 + 공유 유틸 4개 |
| 1.3 | `harness/` 마이그레이션 | Python 코어 11개 + 쉘 보조 8개 |
| 1.4 | `agents/` 마이그레이션 | .md 13개 + architect 하위 6개 (개인용 제외) |
| 1.5 | `commands/` 마이그레이션 | 14개 (`hardcarry`/`softcarry` 제외) |
| 1.6 | `orchestration/` 마이그레이션 | 마스터 룰 + 보조 문서 13개 |
| 1.7 | 경로 추상화 일괄 적용 | Python ~25곳 + Shell ~5곳 |
| 1.8 | `hooks/hooks.json` 작성 | settings.json 23 엔트리 → 내장형 |
| 1.9 | `templates/`, `scripts/` 마이그레이션 | CLAUDE-base.md + setup-project.sh (PLUGIN_ROOT 기반) |

---

## 3. 인벤토리 (~/.claude 활성 코드)

### 3.1 hooks/ — 활성 22개 + 공유 유틸 4개

**라우팅 / 상태 (UserPromptSubmit, SessionStart, Stop)**:
- `harness-router.py` (UserPromptSubmit, 30s timeout)
- `session-agent-cleanup.py` (UserPromptSubmit)
- `harness-review-inject.py` (UserPromptSubmit)
- `harness-session-start.py` (SessionStart)
- `skill-stop-protect.py` (Stop)
- `ralph-session-stop.py` (Stop)
- `harness-review-stop.py` (Stop)

**게이트 / 경계 (PreToolUse)**:
- `plugin-write-guard.py` (Edit/Write)
- `orch-rules-first.py` (Edit/Write — 경고형)
- `agent-boundary.py` (Edit/Write/Read)
- `harness-drift-check.py` (Bash)
- `commit-gate.py` (Bash)
- `agent-gate.py` (Agent)
- `skill-gate.py` (Skill)
- `issue-gate.py` (mcp__github__create_issue / update_issue)

**플래그 / 사후 정리 (PostToolUse)**:
- `harness-settings-watcher.py` (Edit)
- `post-agent-flags.py` (Agent)
- `post-skill-flags.py` (Skill)
- `post-commit-cleanup.py` (Bash)
- `harness-review-trigger.py` (Bash)

**공유 유틸 (직접 등록 X)**:
- `harness_common.py` (is_harness_enabled, path rules, rate limit)
- `session_state.py` (Phase 3 세션 격리 상태 API)
- `skill_protection.py` (Phase 4 스킬 컨텍스트 보호 공유 유틸)
- `helpers.py`

**제외**: `*.bak-hardcarry` 2개, 기타 `.bak`

### 3.2 harness/ — Python 코어 11개 + 쉘 8개

**Python**: `__init__.py`, `config.py`, `core.py`, `executor.py`, `helpers.py`, `impl_loop.py` (85KB), `impl_router.py`, `notify.py`, `plan_loop.py` (19KB), `providers.py`, `review_agent.py`

**Shell 보조**: `executor.sh`, `impl.sh`, `impl_simple.sh`, `impl_std.sh`, `impl_deep.sh`, `design.sh`, `plan.sh`, `utils.sh`

**제외**: `harness/*.sh.bak` 11개

### 3.3 agents/ — .md 14개 (개인용 0개, 모두 배포 대상)

`architect.md`, `architect/{light-plan,module-plan,spec-gap,system-design,task-decompose,tech-epic}.md`, `engineer.md`, `test-engineer.md`, `validator.md`, `validator/plan-validation.md`, `pr-reviewer.md`, `security-reviewer.md`, `qa.md`, `designer.md`, `design-critic.md`, `ux-architect.md`, `product-planner.md`, `plan-reviewer.md`, `preamble.md`, `README.md`

### 3.4 commands/ — 14개 (hardcarry/softcarry 제외)

`init-project.md`, `quick.md`, `qa.md`, `ux.md`, `ux-sync.md`, `product-plan.md`, `ralph.md`, `deliver.md`, `doc-garden.md`, `harness-test.md`, `harness-review.md`, `harness-status.md`, `harness-monitor.md`, `harness-kill.md`

**제외**: `hardcarry.md`, `softcarry.md` (개인용 dongchan 보조 모드)

### 3.5 orchestration/

**마스터**: `policies.md` (229줄, 2026-04-19 정제)

**보조 (12개)**: `agent-boundaries.md`, `branch-strategy.md`, `changelog.md`, `issue-convention.md`, `design.md`, `impl.md`, `impl_simple.md`, `impl_std.md`, `impl_deep.md`, `plan.md`, `system-design.md`, `tech-epic.md`

> RWHarness 자체의 거버넌스(`orchestration/policies.md`, `changelog.md`, `rationale.md`)와 **혼동 주의**. ~/.claude 마스터를 RWHarness로 가져올 때 별도 디렉토리(예: `orchestration/upstream/`) 또는 파일명 충돌 회피 필요. **결정**: `orchestration/upstream/` 으로 분리 (Phase 1.6).

### 3.6 templates/, scripts/

- `templates/CLAUDE-base.md` (프로젝트 CLAUDE.md 템플릿)
- `scripts/setup-project.sh` (`setup-harness.sh` 를 PLUGIN_ROOT 기반으로 재작성)

### 3.7 settings 골격

- `settings.json` (배포본): hooks 섹션 제거된 빈 골격 + 기본 permissions/env
- `harness-projects.json` (배포본): 빈 템플릿 (사용자가 자기 프로젝트 등록)

---

## 4. 경로 추상화 패턴 (Phase 1.7)

### Python (harness/, hooks/)
```python
# Before
from pathlib import Path
HARNESS_ROOT = Path.home() / ".claude"

# After
import os
from pathlib import Path
HARNESS_ROOT = Path(os.environ.get('CLAUDE_PLUGIN_ROOT', Path.home() / '.claude'))
```

### Shell (harness/*.sh, scripts/*.sh)
```bash
# Before
HARNESS_ROOT="${HOME}/.claude"

# After
HARNESS_ROOT="${CLAUDE_PLUGIN_ROOT:-${HOME}/.claude}"
```

### 영향 범위 (예상)
- `harness/*.py`: ~15곳
- `hooks/*.py`: ~10곳
- 쉘 스크립트: ~5곳
- `agents/*.md`, `commands/*.md`: 문서 내 절대 경로 ~20곳 (선택적 — `${CLAUDE_PLUGIN_ROOT}` 표기)

---

## 5. hooks/hooks.json 변환 (Phase 1.8)

`~/.claude/settings.json`의 hooks 섹션 23 엔트리를 `hooks/hooks.json`으로 이전.

명령어 패턴: `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/<hook>.py"`

상세 매핑은 `docs/plan-plugin-distribution.md §5.2` 참조 — 본 작업 시 그 표를 그대로 사용.

**예외**: macOS 전용 `Stop` 훅의 첫 엔트리 `afplay Glass.aiff`는 플러그인에서 제외. README에 옵션 스니펫 안내.

---

## 6. 검증 체크리스트 (Phase 1 종료 시점)

- [ ] hooks/ 활성 22개 + 공유 유틸 4개 모두 복사
- [ ] harness/ Python 11개 + Shell 8개 모두 복사 (`.bak` 0개 검증: `find harness -name '*.bak'` 결과 empty)
- [ ] agents/ 13개 + architect 하위 6개 모두 복사
- [ ] commands/ 14개 복사 (`grep -r "hardcarry\|softcarry" commands/` 결과 0)
- [ ] orchestration/upstream/ 13개 복사
- [ ] CLAUDE_PLUGIN_ROOT 미설정 환경에서 폴백 동작 확인 (`unset CLAUDE_PLUGIN_ROOT && python3 -c "from harness.core import HARNESS_ROOT; print(HARNESS_ROOT)"`)
- [ ] `hooks/hooks.json` 23 엔트리 — settings.json과 1:1 대응 검증
- [ ] `dongchan-style/`, `hardcarry`, `softcarry` 흔적 0건 (`grep -ri "hardcarry\|softcarry\|dongchan" --exclude-dir=.git --exclude-dir=docs --exclude-dir=.claude/projects`)
- [ ] `orchestration/changelog.md` Phase 1 sub-commit 9개 모두 기록

---

## 7. Phase 2 인계 (참고)

Phase 1 완료 후 Phase 2에서 다룰 항목 (proposals.md §4):
- `harness-spec.md §0` Core Invariant 신규 작성
- README 메인 카피 — "Production-grade Agent Workflow Engine"
- `harness.config.json` `agent_tiers` 옵션 도입
- `scripts/check_doc_sync.py` (Python) — 자동 게이트
- `scripts/hooks/pre-commit.sh` + `hooks/commit-gate.py` 확장
- `.github/PULL_REQUEST_TEMPLATE.md`
