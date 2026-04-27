# Changelog (WHAT log)

> Task-ID 단위 변경 기록. WHAT 중심. WHY는 [`rationale.md`](rationale.md) 참조.

| Task-ID | Date | Type | Title | Exception |
|---|---|---|---|---|
| `HARNESS-CHG-20260427-01` | 2026-04-27 | spec | RealWorld Harness 플러그인 배포 레포 부트스트랩 | — |
| `HARNESS-CHG-20260427-02` | 2026-04-27 | spec | Phase 1 마이그레이션 계획 + ~/.claude 활성 코드 인벤토리 | — |
| `HARNESS-CHG-20260427-03` | 2026-04-27 | spec | Phase 2 — Core Invariant + agent_tiers + 거버넌스 자동 게이트 + bypass 제거 | — |
| `HARNESS-CHG-20260427-04` | 2026-04-27 | spec | Phase 3 [3.1] 독립 정본화 — 마이그레이션 흔적 + 개인 식별자 + 추상어 정리 | — |
| `HARNESS-CHG-20260427-04` | 2026-04-27 | docs | Phase 3 [3.2] orchestration/upstream/README.md 추가 — 참조 스냅샷 정체성 명시 | — |
| `HARNESS-CHG-20260427-04` | 2026-04-27 | spec | Phase 3 [3.3] harness-architecture.md 본문 PLUGIN_ROOT 적응 + 잔존 ~/.claude 정리 | — |
| `HARNESS-CHG-20260427-04` | 2026-04-27 | infra | Phase 3 [3.4] GitHub Actions Document Sync workflow + Change-Type `.github/` 분류 추가 | — |
| `HARNESS-CHG-20260427-04` | 2026-04-27 | infra | Phase 3 [3.5] smoke-test.sh + clean install 검증 가이드 — 50/50 PASS | — |
| `HARNESS-CHG-20260427-04` | 2026-04-27 | docs | Phase 3 [3.6] 5루프 E2E 검증 시나리오 가이드 | — |
| `HARNESS-CHG-20260427-04` | 2026-04-27 | infra | Phase 3 [3.7] GitHub Actions smoke-test.yml — 별도 머신(ubuntu) 자동 검증 (폴백 + 플러그인 모드) | — |
| `HARNESS-CHG-20260427-04` | 2026-04-27 | infra | Phase 3 [3.8] Node 20 deprecation 우회 — workflows env FORCE_JAVASCRIPT_ACTIONS_TO_NODE24 추가 (smoke-test + doc-sync) | — |
| `HARNESS-CHG-20260427-04` | 2026-04-27 | docs | Phase 3 [3.9] E2E quickstart — 30분 검증 경로 (`/quick` 루프 + 거버넌스 게이트 + agent_tiers override) | — |
| `HARNESS-CHG-20260427-04` | 2026-04-27 | docs | Phase 3 [3.10] quickstart §0 옵션 B (RWHarness repo 직접) + C (~/.claude 폴백) 분리 — `~/.claude/scripts/setup-project.sh` 부재 사용자 첫 실패 정정 | — |
| `HARNESS-CHG-20260427-04` | 2026-04-27 | infra | Phase 3 [3.11] setup-project.sh `.gitignore` 자동 등록에 `.claude/harness-state/` 추가 — quickstart §1 실측 시 디버그 로그 untracked 발견 | — |
| `HARNESS-CHG-20260427-04` | 2026-04-27 | infra | Phase 3 [3.12] worktree 격리 기본값 활성화 — config.py 기본값/폴백 + setup-project.sh 누락 시 자동 추가 | — |
| `HARNESS-CHG-20260427-04` | 2026-04-27 | docs | Phase 3 [3.13] README + CHANGELOG 점검 패치 — Phase 표 갱신 + install 섹션 명확화 + alpha 시작일 명시 | — |
| `HARNESS-CHG-20260427-05` | 2026-04-27 | spec | Phase 4 [4.1] release prep — README/CHANGELOG v0.1.0-alpha release-ready 갱신 | — |
| `HARNESS-CHG-20260427-05` | 2026-04-27 | docs | Phase 4 [4.2] analysis-current-harness.md — historical reference 명시 + §G/§H 결과 갱신 | — |
| `HARNESS-CHG-20260427-05` | 2026-04-27 | docs | Phase 4 [4.3] historical 자료 4개 삭제 — migration-plan / plan-plugin-distribution / proposals / analysis-current-harness | — |
| `HARNESS-CHG-20260427-05` | 2026-04-27 | docs | Phase 4 [4.4] git tag `v0.1.0-alpha` push (메타) | — |

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

## `HARNESS-CHG-20260427-03` — 2026-04-27 — Phase 2 (철학 명시화 + 자동 게이트 + 정리)

**Type**: spec

**Sub-commits (완료)**:
- `[2.1]` `c1021a0` Core Invariant `harness-spec.md §0` 신규 (`+88/-2`)
- `[2.2]` `4796a09` README 메인 카피 — "Production-grade Agent Workflow Engine" (`+68/-22`)
- `[2.3]` `10f4171` hardcarry/softcarry bypass 로직 완전 제거 (`+2/-10`)
- `[2.4]` `a554af0` `agent_tiers` 도입 — config.py + docs/agent-tiers.md (`+192`)
- `[2.5]` `26fdf4f` `scripts/check_doc_sync.py` Python 자동 게이트 (`+219`, 단위 테스트 11/11)
- `[2.6]` `394dbf5` `scripts/hooks/pre-commit.sh` + `hooks/commit-gate.py` Gate 4 (`+51`)
- `[2.7]` `d4cdad5` `.github/PULL_REQUEST_TEMPLATE.md` (`+61`)
- `[2.8]` `e8bb7d0` `scripts/setup-project.sh` PLUGIN_ROOT 적응 + 거버넌스 pre-commit 자동 설치 (`+46/-44`)
- `[2.9]` (본 commit) Phase 2 종료 + 셀프 검증

**Phase 2 검증 결과**:
- ✓ Core Invariant — `harness-spec.md §0` 4항목 + `[invariant-shift]` PR 토큰 룰
- ✓ README 카피 강화 — Phase 진행 상태 갱신, 트렌드 비교표 추가
- ✓ bypass 로직 — hooks/agent-gate.py + agent-boundary.py 에 hardcarry/softcarry 잔존 0건 (.no-harness 마커는 일반 옵션으로 보존)
- ✓ agent_tiers — 12 에이전트 → high/mid/low 매핑, 폴백 동작 검증 (architect/engineer/qa/unknown 4 케이스)
- ✓ check_doc_sync.py — Change-Type 5종 분류 단위 테스트 11/11, Document-Exception 스코핑 (사유 ≥ 10자)
- ✓ commit-gate.py Gate 4 — cwd 의 scripts/check_doc_sync.py 자동 호출 (없으면 skip)
- ✓ pre-commit.sh — git hook 진입점, SKIP_DOC_SYNC env 우회
- ✓ PR 템플릿 — Task-ID + Change-Type + Document Sync 체크리스트 + Document-Exception 섹션
- ✓ setup-project.sh — HARNESS_ROOT 변수 도입, PLUGIN_ROOT 폴백, BATS rule-audit → 거버넌스 pre-commit 자동 설치
- ✓ **셀프 게이트 검증** — 본 sub-commit 자체가 spec 변경(changelog + rationale 갱신)이며 .git/hooks/pre-commit 활성화 후 게이트 통과 확인

**Linked**:
- `docs/proposals.md §3` 제안 A/B/C
- `docs/proposals.md §6` 거버넌스 통합 방안
- 유저 결정 (2026-04-27): A·B·D 추천대로, C는 옵션 A(완전 제거)

**Exception**: —

---

## `HARNESS-CHG-20260427-04` — 2026-04-27 — Phase 3 [3.1] 독립 정본화

**Type**: spec

**Summary**: 마이그레이션 흔적·개인 식별자·추상 용어를 정리해 RWHarness 문서를 *외부 배포용 정본*으로 독립화. 외부 사용자가 docs/를 읽을 때 "이 시스템은 ~/.claude 에서 옮겨졌다"는 historical artifact 인상이나 특정 개인 정보 노출 없이 자체 완결되도록.

**Files** (15):
- `docs/harness-spec.md` — 헤더 마이그레이션 표기 제거 / §0 추상어 정리 ("결정론 > 적응성" → "예측 가능성을 자유로운 적응보다 우선", "프로덕션 분파에 정렬" → "실제 서비스 코드를 만드는 데 쓴다") / §1 "시니어 엔지니어 dongchan" → "프로젝트 운영자"
- `docs/harness-architecture.md` — 헤더 마이그레이션 표기 제거 / §2.2 hardcarry/softcarry bypass 행 → `.no-harness` 마커 / §5.1 화이트리스트 예시 일반화
- `README.md` — "데모/연구 분파가 아니라 프로덕션 분파에 정렬" → "데모나 연구용 도구가 아니라, 실제 서비스에 들어가는 코드를 만드는 데 쓴다"
- `.claude-plugin/plugin.json` — author.name "dongchan kim" → "alruminum"
- `docs/proposals.md` — "프로덕션 분파에 정확히 정렬" → "실제 서비스 운영 쪽 흐름에 정확히 맞춰져 있다" / dongchan-style 표현 일반화
- `docs/migration-plan.md` — dongchan-style / dongchan 표현 일반화
- `docs/analysis-current-harness.md` — 화이트리스트 예시 일반화 / dongchan 일반화
- `docs/plan-plugin-distribution.md` — dongchan-style 표현 3곳 일반화
- `commands/ux.md` — `/Users/dc.kim/project/...` → `${HOME}/project/<project-name>/...`
- `hooks/harness-review-trigger.py` — 주석 dc.kim 경로 일반화
- `hooks/agent-boundary.py` — 주석 jajang #99 → 일반화
- `harness/impl_loop.py` — 주석 jajang attempt → 실측
- `harness/impl_router.py` — 주석 jajang 통계 → 실측
- `agents/ux-architect.md` — 주석 jajang 사례 → 일반화
- `agents/engineer.md` — 주석 jajang 로그 → 실측
- `orchestration/{changelog,rationale}.md` — 본 항목 (WHAT/WHY)

**검증**:
- ✓ `dongchan` 잔존 0건 (LICENSE 저작권자 + orchestration/upstream/* 제외)
- ✓ `/Users/dc.kim/` 절대 경로 잔존 0건 (upstream 제외)
- ✓ `jajang|memoryBattle|HardcarryDryRun` 잔존 0건 (upstream 제외)
- ✓ "에서 마이그레이션됐다", "원본 source: ~/" 잔존 0건
- ✓ "분파" 잔존 0건

**보존 (의도적)**:
- `LICENSE` Copyright "dongchan kim" — 저작권 표기, 법적 필수
- `orchestration/upstream/*` — `~/.claude/orchestration/` 원본 보존본 (참조 정본). 본 디렉토리 정체성은 별도 sub-commit으로 README 추가 예정

**Linked**:
- 유저 명시 (2026-04-27): "~/.claude/docs/harness-spec.md 에서 마이그레이션됐다 이런 ~/.claude 관련 내용들은 싹다 빼주고", "내 이름을 명시하는 내용도 검사해서 뺴줘", "분파가 뭐야? 이런거 현실세계의 언어로 좀 바꿔줘"
- `HARNESS-CHG-20260427-02` Phase 1 (마이그레이션 본격) 산출물 정리

**Exception**: —

---

## `HARNESS-CHG-20260427-05` — 2026-04-27 — Phase 4 (alpha release)

**Type**: spec

**Sub-commits 예정**:
- `[4.1]` (본 commit) release prep — README/CHANGELOG release-ready 갱신
- `[4.2]` `git tag -a v0.1.0-alpha` + `git push --tags` + `gh release create v0.1.0-alpha` (메타 행위, 별도 commit 불필요)
- `[4.3]` `gh repo edit alruminum/realworld-harness --visibility public` (메타 행위)
- `[4.4]` 정리 commit — 실제 release URL 반영 + Phase 4 ✅ 완료 표기

**Linked**:
- `docs/proposals.md §4` Phase 4
- 유저 명시 승인 (2026-04-27): "응 진행"

**Exception**: —

---

> 새 항목은 위 표 + 본 섹션 양쪽에 추가. Phase 2 자동 게이트가 활성화되면 표는 `scripts/check_doc_sync.py` 가 갱신 검증.
