# Changelog (WHAT log)

> Task-ID 단위 변경 기록. WHAT 중심. WHY는 [`rationale.md`](rationale.md) 참조.

| Task-ID | Date | Type | Title | Exception |
|---|---|---|---|---|
| `HARNESS-CHG-20260427-01` | 2026-04-27 | spec | RealWorld Harness 플러그인 배포 레포 부트스트랩 | — |
| `HARNESS-CHG-20260427-02` | 2026-04-27 | spec | Phase 1 마이그레이션 계획 + ~/.claude 활성 코드 인벤토리 | — |

---

## `HARNESS-CHG-20260427-01` — 2026-04-27 — RealWorld Harness 플러그인 배포 레포 부트스트랩

**Type**: spec

**Files**:
- `LICENSE` (MIT)
- `.gitignore`
- `README.md`
- `CHANGELOG.md`
- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `docs/harness-spec.md` (마이그레이션 from `~/.claude/docs/harness-spec.md`)
- `docs/harness-architecture.md` (마이그레이션 from `~/.claude/docs/harness-architecture.md`)
- `docs/analysis-current-harness.md` (신규 — 분석 보고서)
- `docs/proposals.md` (신규 — 배포 방향 제안 + 거버넌스 통합 방안)
- `docs/plan-plugin-distribution.md` (이동 from repo root, 정본 설계 문서)
- `orchestration/policies.md` (신규 — Task-ID + Change-Type 5종 + Document-Exception 룰)
- `orchestration/changelog.md` (신규 — 본 파일)
- `orchestration/rationale.md` (신규 — WHY 로그)
- 디렉토리 골격: `.claude-plugin/`, `hooks/`, `agents/`, `harness/`, `commands/`, `templates/`, `scripts/hooks/`, `tests/pytest/`

**Summary**: 빈 디렉토리에 RealWorld Harness 플러그인 배포 레포의 부트스트랩 골격을 구축. ~/.claude의 작동 중인 하네스 시스템을 클린 플러그인 구조로 마이그레이션하기 위한 출발점. Phase 0 가벼운 거버넌스(Task-ID + WHAT/WHY 분리 로그) 동시 도입.

**Linked**:
- `docs/proposals.md §4` — 4-Phase 실행 순서
- `docs/proposals.md §6` — TDM 거버넌스 통합 방안
- 메모리: `project_kickoff_decisions.md`

**Exception**: —

---

## `HARNESS-CHG-20260427-02` — 2026-04-27 — Phase 1 마이그레이션 계획 + ~/.claude 활성 코드 인벤토리

**Type**: spec

**Files**:
- `docs/migration-plan.md` (신규)

**Summary**: Phase 1(코어 마이그레이션)의 sub-section 9개 분할 + ~/.claude 활성 코드 카탈로그 + 경로 추상화 패턴 + 검증 체크리스트 정의. 본 Task-ID 산하의 sub-commit으로 1.2~1.9 진행 예정.

**Sub-commits (완료)**:
- `[1.1]` 마이그레이션 계획 (commit `348d7b5`)
- `[1.2]` hooks/ Python 23개 (commit `ad62ac7`, +4024 lines)
- `[1.3]` harness/ Python 11개 (commit `97a860e`, +6773 lines — impl_loop 85KB 포함)
- `[1.4]` agents/ .md 26개 (commit `c97fa3b`, +4642 lines)
- `[1.5]` commands/ .md 16개 (commit `8986e0d`, +1855 lines, hardcarry/softcarry 제외)
- `[1.6]` orchestration/upstream/ .md 15개 (commit `147b33b`, +1924 lines)
- `[1.7]` 경로 추상화 PLUGIN_ROOT 도입 5 파일 9곳 (commit `e8c4cee`)
- `[1.8]` hooks/hooks.json 25 엔트리 (commit `7ca05f5`)
- `[1.9]` templates/, scripts/ 4 파일 (commit `bcce3ee`)
- `[1.10]` Phase 1 종료 정리 (본 commit)

**Phase 1 검증 결과** (migration-plan.md §6):
- ✓ hooks/ 23 / harness/ 11 / agents/ 26 / commands/ 16 / orchestration/upstream/ 15 / templates/ 1 / scripts/ 3
- ✓ hooks/hooks.json 존재 + 25 엔트리 + json 파싱 통과
- ✓ PLUGIN_ROOT 정의 5 파일 (harness: core, executor, review_agent / hooks: harness-router, harness-review-trigger)
- ✓ Path.home() / ".claude" / {hooks,agents,harness,scripts} 잔존 0건
- ✓ python3 -m py_compile 5 파일 통과
- ✓ .bak / .bak-* 잔존 0건
- ⚠️ hooks/agent-gate.py + hooks/agent-boundary.py 에 hardcarry/softcarry bypass 주석·로직 잔존 → **Phase 2 정리 대상** (코드 자체에 텍스트로 박혀있어 단순 grep으론 제거 불가, 일반화 또는 제거 결정 필요)

**Linked**:
- `docs/proposals.md §4` Phase 1
- `docs/plan-plugin-distribution.md §5` (경로 추상화 + hooks.json 변환)
- `docs/analysis-current-harness.md` (인벤토리 인풋)

**Exception**: —

---

> 새 항목은 위 표 + 본 섹션 양쪽에 추가. Phase 2 자동 게이트가 활성화되면 표는 `scripts/check_doc_sync.py` 가 갱신 검증.
