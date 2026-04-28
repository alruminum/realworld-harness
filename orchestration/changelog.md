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
| `HARNESS-CHG-20260427-04` | 2026-04-27 | docs | Phase 3 [3.10] quickstart §0 옵션 B (RWHarness repo 직접) + C (~/.claude 폴백) 분리 — `~/.claude/scripts/setup-rwh.sh` 부재 사용자 첫 실패 정정 | — |
| `HARNESS-CHG-20260427-04` | 2026-04-27 | infra | Phase 3 [3.11] setup-rwh.sh `.gitignore` 자동 등록에 `.claude/harness-state/` 추가 — quickstart §1 실측 시 디버그 로그 untracked 발견 | — |
| `HARNESS-CHG-20260427-04` | 2026-04-27 | infra | Phase 3 [3.12] worktree 격리 기본값 활성화 — config.py 기본값/폴백 + setup-rwh.sh 누락 시 자동 추가 | — |
| `HARNESS-CHG-20260427-04` | 2026-04-27 | docs | Phase 3 [3.13] README + CHANGELOG 점검 패치 — Phase 표 갱신 + install 섹션 명확화 + alpha 시작일 명시 | — |
| `HARNESS-CHG-20260427-05` | 2026-04-27 | spec | Phase 4 [4.1] release prep — README/CHANGELOG v0.1.0-alpha release-ready 갱신 | — |
| `HARNESS-CHG-20260427-05` | 2026-04-27 | docs | Phase 4 [4.2] analysis-current-harness.md — historical reference 명시 + §G/§H 결과 갱신 | — |
| `HARNESS-CHG-20260427-05` | 2026-04-27 | docs | Phase 4 [4.3] historical 자료 4개 삭제 — migration-plan / plan-plugin-distribution / proposals / analysis-current-harness | — |
| `HARNESS-CHG-20260427-05` | 2026-04-27 | docs | Phase 4 [4.4] git tag `v0.1.0-alpha` push (메타) | — |
| `HARNESS-CHG-20260427-05` | 2026-04-27 | infra | Phase 4 [4.5] GitHub Release v0.1.0-alpha 생성 (private, 메타) | — |
| `HARNESS-CHG-20260427-05` | 2026-04-27 | infra | Phase 4 [4.6] rename — `setup-project.sh` → `setup-rwh.sh` + `/init-project` → `/init-rwh` (12 파일 일괄 치환) | — |
| `HARNESS-CHG-20260427-05` | 2026-04-27 | infra | Phase 4 [4.7] repo public 전환 — gh repo edit (메타) | — |
| `HARNESS-CHG-20260427-05` | 2026-04-27 | docs | Phase 4 [4.8] Phase 4 ✅ 완료 정리 — README badge + Phase 표 + 설치 섹션 final | — |
| `HARNESS-CHG-20260427-05` | 2026-04-27 | docs | Phase 4 [4.9] README 외부 사용자 진입 정비 — 의존성·첫 사용·트러블슈팅·발견·공유 섹션 | — |
| `HARNESS-CHG-20260427-05` | 2026-04-27 | docs | Phase 4 [4.10] migration-from-source 가이드 — ~/.claude → RWHarness 플러그인 전환 step-by-step | — |
| `HARNESS-CHG-20260427-05` | 2026-04-27 | docs | Phase 4 [4.11] migration-from-source 가이드 정정 — Claude Code 완전 quit 단계 추가 (새 세션도 같은 환경 공유) | — |
| `HARNESS-CHG-20260427-05` | 2026-04-27 | docs | Phase 4 [4.12] migration §5 상세화 — ~/.claude 실측 인벤토리 기반 매핑표·historic·보존·명령어·정리 후 모습 | — |
| `HARNESS-CHG-20260427-05` | 2026-04-27 | infra | Phase 4 [4.13] migrate-step1.sh + migrate-step2.sh 자동화 스크립트 — 사용자 확인·안전 검사·롤백 안내 내장 | — |
| `HARNESS-CHG-20260427-05` | 2026-04-27 | infra | Phase 4 [4.14] marketplace.json/plugin.json 스키마 정정 — Claude Code parser 기준 (top-level name + owner object + repository string) | — |
| `HARNESS-CHG-20260427-06` | 2026-04-27 | infra | v0.2.0 [6.1] setup-rwh.sh 플러그인 모드 분기 — CLAUDE_PLUGIN_ROOT set 시 글로벌 settings.json 훅 등록 skip (Phase 4 잔존 부채 #1 해결) | — |
| `HARNESS-CHG-20260428-01` | 2026-04-28 | infra | [1.1] harness/tracker.py — 추적 ID 백엔드 추상화 (GitHub gh CLI / Local jsonl) + 단위 테스트 16/16 | — |
| `HARNESS-CHG-20260428-01` | 2026-04-28 | spec  | [1.2] LOCAL-1 부트스트랩 + docs/impl/LOCAL-1-tracker-abstraction.md + rationale 4섹션 | — |
| `HARNESS-CHG-20260428-01` | 2026-04-28 | infra | [1.3] hooks/agent-gate.py + harness-router.py 추적 ID 정규식 확장 (#N → #N\|LOCAL-N) | — |
| `HARNESS-CHG-20260428-01` | 2026-04-28 | agent | [1.4] agents/designer.md Phase 0-0 — gh issue create → tracker CLI + commit-gate.py Gate 1 가드 확장 | — |
| `HARNESS-CHG-20260428-01` | 2026-04-28 | agent | [1.5] agents/qa.md MCP 미가용 폴백 — Bash 추가 (tracker CLI 한정) + 폴백 흐름 안내 | — |
| `HARNESS-CHG-20260428-01` | 2026-04-28 | spec  | [1.6] docs/harness-spec.md §3 I-2 추적 ID 일반형 표현 + harness-architecture.md §6 추적 백엔드 신규 섹션 | `Document-Exception: rationale.md 4섹션은 본 Task-ID 의 [1.2] commit 0c9d5f3 에서 일괄 작성됨 — 본 [1.6] 은 그 결정의 spec 적용` |
| `HARNESS-CHG-20260428-02` | 2026-04-28 | infra | [2.1] tracker.py — IssueRef.internal property + format_ref() + normalize_issue_num() + 단위 테스트 33/33 | — |
| `HARNESS-CHG-20260428-02` | 2026-04-28 | infra | [2.2] core.py 의 gh issue view → tracker.get_issue() 위임 + 7파일 f-string `#{issue_num}` → `{format_ref(issue_num)}` + executor 진입 normalize | — |
| `HARNESS-CHG-20260428-02` | 2026-04-28 | infra | [2.3] smoke-test.sh §9 tracker LOCAL-N regression 회로 5건 추가 (parse_ref / format/normalize / LocalBackend 라운드트립 / 강제 폴백 / which CLI) — 56/56 PASS | — |
| `HARNESS-CHG-20260428-03` | 2026-04-28 | infra | [3.1] BATS 잔존 표기 제거 — CHANGELOG 부채 라인 + PR 템플릿 + policies.md §2 `tests/bats/` 표기. 코드/스크립트에 BATS 흔적 0건 확인 (점검 결과) | — |
| `HARNESS-CHG-20260428-04` | 2026-04-28 | infra | [4.1] `~/.claude/harness/executor.py` hardcode 제거 — 6 파일 13 위치 → `${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/marketplaces/realworld-harness}/harness/executor.py` (jajang 실제 사례에서 No such file or directory 발생) | — |
| `HARNESS-CHG-20260428-05` | 2026-04-28 | infra | [5.1] `diagnose_marker_miss()` 헬퍼 + 9 사이트 적용 (impl_router 2 + plan_loop 1 + core 6 validator) — 마커 미감지 시 arch_out 마지막 500자 진단 로그 | — |
| `HARNESS-CHG-20260428-05` | 2026-04-28 | agent | [5.2] architect sub-docs 출력 형식 canonical — light-plan/module-plan/task-decompose `---MARKER:X---` 정형 마커로 통일 + preamble 자가-체크 룰 추가 | — |
| `HARNESS-CHG-20260428-06` | 2026-04-28 | infra | [6.1] AI 패닉 회로 차단 — agent-gate.py + plugin-write-guard.py deny 메시지에 명시적 복구 가이드 (executor 재실행 / 새 세션 / 유저 보고 — 인프라 inspect/edit 금지) | — |
| `HARNESS-CHG-20260428-06` | 2026-04-28 | infra | [6.2] executor.py stale lock 자동 정리 visibility — silent unlink → 명시적 메시지 ("직전 실행 PID=X 죽음, 재진행합니다") | — |
| `HARNESS-CHG-20260428-07` | 2026-04-28 | infra | [7.1] migration audit — `~/.claude/scripts/`, `~/.claude/setup-harness.sh`, `~/.claude/agents/{agent}.md` 잔존 hardcode 5 파일 9 위치 일괄 env-aware 교체 (PR #4 systematic 후속) | `Document-Exception: harness-architecture.md 단일 행 path 정정 — 의사결정 변경 없는 문구 fix 라 rationale 4섹션 불필요. 본 Task-ID 본문 섹션이 동기·범위 명시` |
| `HARNESS-CHG-20260428-08` | 2026-04-28 | agent | [8.1] validator sub-docs canonical 마커 — plan/code/design/bugfix-validation 출력 형식 `---MARKER:X---` 정형화 + preamble 마커명 정확도 절대 룰 추가 (PLAN_LGTM 변형 차단) | — |
| `HARNESS-CHG-20260428-09` | 2026-04-28 | infra | [9.1] parse_marker alias map — LLM 변형(PLAN_LGTM/PLAN_OK/PLAN_APPROVE/APPROVE/REJECT 등) → canonical 흡수. 3차 폴백 + stderr 경고. agent docs 강화로 안 풀린 PLAN_OK/APPROVE 사례(jajang 2026-04-28) defense in depth | — |
| `HARNESS-CHG-20260428-10` | 2026-04-28 | infra | [10.1] migration audit cleanup — notify.py:19 CLI 예시 + plugin-write-guard:83 + settings-watcher:42,54 메시지 + README §C 신규 사용자 혼동 차단 (4건 일괄, MCP graceful 별도 검토) | — |
| `HARNESS-CHG-20260428-11` | 2026-04-28 | infra | [11.1] `--force-retry` 확장 — escalate_history 도 청소 (false failure 누적 후 retry 시 manual JSON 편집 불필요) + auto_spec_gap 메시지에 복구 안내 추가 | — |

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
- `[2.8]` `e8bb7d0` `scripts/setup-rwh.sh` PLUGIN_ROOT 적응 + 거버넌스 pre-commit 자동 설치 (`+46/-44`)
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
- ✓ setup-rwh.sh — HARNESS_ROOT 변수 도입, PLUGIN_ROOT 폴백, BATS rule-audit → 거버넌스 pre-commit 자동 설치
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

## `HARNESS-CHG-20260428-01` — 2026-04-28 — 추적 ID 백엔드 추상화 (gh CLI 강제 결합 해소)

**Type**: spec (인프라 + spec 갱신 포함, 우선순위 spec)

**Issue**: `LOCAL-1` (`orchestration/issues/INDEX.jsonl#1`) — 본 Task-ID 자체가 LocalBackend 의 첫 사용 사례 (자기-호스팅 부트스트랩)

**Branch**: `harness/tracker-abstraction`

**Invariant flag**: `[invariant-shift]` (PR title 에 명시 예정 — `§3 I-2` 의 표현 일반화. 약화 아님)

**Sub-commits**:
- `[1.1]` `4c4d4f0` `harness/tracker.py` 신규 (+273) + `tests/pytest/test_tracker.py` 신규 (+145) + 단위 테스트 16/16
- `[1.2]` (본 commit) `orchestration/issues/INDEX.jsonl` LOCAL-1 부트스트랩 + `docs/impl/LOCAL-1-tracker-abstraction.md` (+108) + `rationale.md` 4섹션 추가
- `[1.3]` `hooks/agent-gate.py:78` + `hooks/harness-router.py:68` 추적 ID 정규식 `#\d+` → `#\d+|LOCAL-\d+`. deny 메시지에 `python3 -m harness.tracker create-issue` 발급 안내 추가
- `[1.4]` `agents/designer.md` Phase 0-0 — `gh issue create` → `python3 -m harness.tracker create-issue` (백엔드 자동 선택). `commit-gate.py` Gate 1 가드 확장: `harness\.tracker\s+(create-issue|comment)` + `harness/tracker\.py\s+(create-issue|comment)` 정규식 추가 — 메인 Claude 우회 차단 보존
- `[1.5]` `agents/qa.md` — `tools:` 라인에 `Bash` 추가 (tracker CLI 폴백 한정 사용). MCP 미가용 폴백 흐름 명시 (mcp__github__create_issue → Bash + tracker CLI → EXTERNAL_TRACKER_NEEDED 마커). 이슈 생성 금지 조건에 `LOCAL-N` 형식 인식 추가
- `[1.6]` `docs/harness-spec.md §3 I-2` 표현 갱신 — `--issue <N>` → `--issue <REF>` (REF = `#N | LOCAL-N`). `harness-architecture.md` 신규 §6 "추적 백엔드 (tracker)" 6.1~6.6 추가 (백엔드 종류 / 선택 우선순위 / 호출 경로 / commit-gate Gate 1 가드 / LocalBackend 저장 형식 / 검증). 기존 §6 "변경 이력 추적" → §7 으로 시프트
- `[1.7]` Phase 종료 commit + PR 생성  *(예정)*

**Linked**:
- 진단 보고: 유저 세션 (2026-04-28) — RWHarness 가 OSS 스택(Husky / lint-staged / GH Actions) 대비 너무 strict 하다는 지적
- `docs/harness-spec.md §0 Core Invariant` — 본 변경은 §0 자체는 보존, §3 의 *구현 표현*만 갱신
- `orchestration/policies.md §2` — `[invariant-shift]` PR token 룰

**Exception**: —

---

## `HARNESS-CHG-20260428-02` — 2026-04-28 — 추적 ID 추상화 follow-up (잔존 흠 + 부수발견 수리)

**Type**: infra (코드 + 테스트, spec 변경 없음)

**Branch**: `harness/tracker-cleanup`

**Issue**: 별도 추적 ID 미발급 — 직전 `HARNESS-CHG-20260428-01` (LOCAL-1) 의 자연 후속. 진단(2026-04-28) 시점에 유저 수리 지시 명시 ("잔존 홀이랑 부수발견 수리" + "1+2 후보도 같이 처리해줘" → smoke-test 통합)

**Sub-commits**:
- `[2.1]` `7a5a64f` `harness/tracker.py` (+50) — `IssueRef.internal` property + `format_ref()` + `normalize_issue_num()` + parse_ref 멱등 확장. `tests/pytest/test_tracker.py` (+60) 16→33 케이스
- `[2.2]` `942cb7d` 7파일 정합 — `core.py` 의 `gh issue view` → `tracker.get_issue()` 위임 + f-string `#{issue_num}` → `{format_ref(issue_num)}` 일괄 교체 + executor 진입 `normalize_issue_num` 적용
- `[2.3]` `0a31611` `scripts/smoke-test.sh` §9 신규 — tracker LOCAL-N regression 회로 5 케이스 (56/56 PASS)
- `[2.4]` (본 commit) `rationale.md` 4섹션 + Task-ID 본문 + PR

**Linked**:
- `HARNESS-CHG-20260428-01` (commit `c18003e`) — 추적 ID 추상화 (이번 정리의 모태)
- 진단 보고: 유저 세션 (2026-04-28) — "잔존 홀이랑 부수발견 수리"
- `[2.2]` 검증: py_compile 8/8 + unittest 33/33 + smoke-test 56/56

**Exception**: —

---

## `HARNESS-CHG-20260428-03` — 2026-04-28 — BATS 잔존 표기 제거 (Phase 4 부채 [6.2] 해소)

**Type**: infra (`.github/` 포함)

**Branch**: `harness/bats-cleanup`

**Issue**: 별도 추적 ID 미발급 — Phase 4 잔존 부채 [6.2] 자체 해소

**점검 결과** (사전 검증):
- `.bats` 파일: 0건
- `tests/bats/` 디렉토리: 미존재 (`tests/pytest/` 만 존재)
- `bats` 명령어 참조 (executable scripts): 0건
- BATS 언급: 문서 placeholder 만 남음 (CHANGELOG, PR 템플릿, policies.md §2)
- 즉, **마이그레이션 작업 자체는 *이미 완료*** 됐고 문서가 갱신 안 된 상태였음

**수정 (3 파일)**:
- `CHANGELOG.md` 알려진 부채 — BATS 라인 strikethrough + 해소 사유 명시 (history 보존)
- `.github/PULL_REQUEST_TEMPLATE.md` — Change-Type test 행에서 `tests/bats/` 제거
- `orchestration/policies.md §2` 표 — 동일

**비변경 (의도)**:
- `scripts/check_doc_sync.py` `TEST_PATTERNS = [re.compile(r"^tests/")]` — prefix 매칭이라 미래 `tests/X/` 추가에도 동작. 손댈 필요 없음
- `orchestration/{changelog,rationale}.md` historical entries — 과거 시점 상태 기록이므로 보존

**Linked**:
- `CHANGELOG.md` v0.2.0 알려진 부채 §[6.2]
- `HARNESS-CHG-20260427-06` rationale.md Follow-Up 의 `[6.2]` 항목

**Exception**: —

---

## `HARNESS-CHG-20260428-04` — 2026-04-28 — executor.py 경로 hardcode 제거 (배포 차단 버그)

**Type**: infra (commands + hooks)

**Branch**: `harness/path-hardcode-fix`

**Issue**: 별도 추적 ID 미발급 — 외부 사용자(jajang 프로젝트) 실측 사고 보고

**증상 보고**: 사용자가 jajang 프로젝트에서 `/qa` 스킬 실행 → AI 가 deny 메시지의 hint 따라 `python3 ~/.claude/harness/executor.py ...` 시도 → `[Errno 2] No such file or directory: '/Users/dc.kim/.claude/harness/executor.py'`

**원인**: Phase 4 [4.13] migrate-step2.sh 가 `~/.claude/harness/` 디렉토리 정리 후, 실제 executor.py 는 `~/.claude/plugins/marketplaces/realworld-harness/harness/executor.py` 에 설치됨. 그러나 다음 위치들의 user-facing 힌트는 *삭제된 경로* 를 그대로 가리킴:

| 파일 | 위치 |
|---|---|
| `commands/quick.md` | line 65 |
| `commands/qa.md` | lines 92, 106 |
| `commands/ux.md` | line 314 |
| `commands/init-rwh.md` | line 106 |
| `commands/product-plan.md` | lines 105, 123, 164, 263 |
| `hooks/agent-gate.py` | lines 101, 102, 117 (deny 메시지 dict + Mode-level deny) |
| **합계** | **6 파일 13 위치** |

**수정**: 모든 위치를 `${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/marketplaces/realworld-harness}/harness/executor.py` 형태로 일괄 교체:
- 플러그인 install + Claude Code 세션: `CLAUDE_PLUGIN_ROOT` env 설정됨 → 그대로 사용
- env 미설정 (수동 shell): 폴백 경로 = 실제 설치 위치
- 기존 `~/.claude/harness/executor.py` 폴백은 *삭제* (post-migration 환경에서 무효)

**검증**:
- `bash scripts/smoke-test.sh` → 56/56 PASS (회귀 없음)
- `python3 -m unittest tests.pytest.test_tracker` → 33/33 OK
- `grep -rn '~/.claude/harness/executor.py' commands/ hooks/` → 0 잔존

**비변경**:
- `harness/executor.py` 자체의 `PLUGIN_ROOT` 폴백 (line 20) — 코드 내부에서 path 해석에 사용. user-facing hint 와 별개. 이번 PR 범위 밖
- `orchestration/upstream/*` historical entries — 보존
- `scripts/setup-rwh.sh:166` — 마이그레이션 정리 로직, user-facing 아님

**Linked**:
- 외부 사용자 보고 (2026-04-28): jajang 프로젝트에서 발생
- Phase 4 [4.13] migrate-step2.sh — 원인이 된 마이그레이션
- 후속: `HARNESS-CHG-20260428-05` (예정) — architect 마커 미감지 → SPEC_GAP_ESCALATE 진단·수정 (별도 Task-ID)

**Exception**: —

---

## `HARNESS-CHG-20260428-05` — 2026-04-28 — marker 진단 가시성 + agent docs canonical

**Type**: infra (코드 + agent docs)

**Branch**: `harness/marker-diagnostics`

**Issue**: jajang 실제 사례 — architect 가 계획 파일은 정상 작성했으나 `parse_marker → UNKNOWN` → `SPEC_GAP_ESCALATE`. 진단 정보 부족으로 현장 디버그 불가능 (`SPEC_GAP_ESCALATE: architect 마커 감지 실패 (UNKNOWN)` 만 출력).

**원인 가설** (3가지):
- (a) 에이전트 출력 도중 끊김 — timeout / 컨텍스트 한계
- (b) 변형 표기 — `LIGHT_PLAN_READY:` 콜론 등 punctuation 으로 word boundary 깨짐
- (c) 마커 누락 — agent docs 내부 *불일치*: preamble 정형 강제 vs sub-doc 평이 단어 예시

**B-1 — 진단 가시성** (`harness/core.py` + `impl_router.py` + `plan_loop.py`):
- 신규 `diagnose_marker_miss(out_file, expected) -> str` 헬퍼 (core.py:497~)
- 9 사이트 적용 — 마커 미감지 시 출력 파일 크기 + 마지막 500자 즉시 출력
  * `impl_router.py:415` (architect SPEC_GAP_ESCALATE)
  * `impl_router.py:432` (architect impl 파일 미생성)
  * `plan_loop.py:334` (ux-architect 마커 미감지)
  * `core.py:2174` (PLAN_VALIDATION UNKNOWN)
  * `core.py:2225` (PLAN_VALIDATION rework UNKNOWN)
  * `core.py:2260` (DESIGN_VALIDATION UNKNOWN)
  * `core.py:2294` (DESIGN_VALIDATION rework UNKNOWN)
  * `core.py:2329` (UX_VALIDATION UNKNOWN)
  * `core.py:2364` (UX_VALIDATION rework UNKNOWN)

**B-2 — agent docs canonical**:
- `agents/architect/light-plan.md` 출력 형식 — 평이 단어 `LIGHT_PLAN_READY` → `---MARKER:LIGHT_PLAN_READY---` 마지막 줄
- `agents/architect/module-plan.md` 출력 형식 — `READY_FOR_IMPL 체크:` 헤딩 → `최종 체크:` (false positive 방지) + `---MARKER:READY_FOR_IMPL---` 마지막 줄
- `agents/architect/task-decompose.md` 출력 형식 — 마커 누락 → `---MARKER:READY_FOR_IMPL---` 추가
- `agents/preamble.md` § "출력 종료 자가-체크" 신규 — 마커 누락이 무진단 실패의 80% 원인임을 명시

**검증**:
- python3 -m py_compile harness/{core,impl_router,plan_loop}.py — OK
- bash scripts/smoke-test.sh — 56/56 PASS (회귀 없음)
- python3 -m unittest tests.pytest.test_tracker — 33/33 OK

**비변경 (의도)**:
- `parse_marker` 자체 — 정형 + word-boundary fallback 보존. 관용도 ↑ 시도는 false positive 위험으로 스킵
- `impl_loop.py` 의 SPEC_GAP_FOUND 흐름 — 마커 *감지 케이스* 라 진단 불필요

**Linked**:
- jajang 사용자 사례 (2026-04-28) — `executor.py` 두 번째 시도 후 SPEC_GAP_ESCALATE
- `HARNESS-CHG-20260428-04` (PR #4) — 같은 사례의 첫 단계 (path hardcode) 해소
- 후속: `HARNESS-CHG-20260428-06` (예정) — 프로세스 hung/crashed 복구 가시성 (B-3)

**Exception**: —

---

## `HARNESS-CHG-20260428-06` — 2026-04-28 — 프로세스 hung/crashed 복구 가시성 (B-3)

**Type**: infra (hooks + executor)

**Branch**: `harness/recovery-visibility`

**Issue**: jajang 사례 — executor 가 validator agent_start 직후 외부 종료(SIGKILL/세션 disconnect 추정). AI 가 *복구 경로 안내 없음* + *stale state silent recovery* 때문에 패닉 → engineer 직접 호출 시도 (HARNESS_ONLY_AGENTS 차단) → 인프라 파일 inspect/edit 시도 (plugin-write-guard 차단) → 유저 좌절 ("니가 인프라를 왜 건들어").

**현 시스템 분석**:
- executor.py 의 lock 파일 PID 검사 + 자동 정리 로직은 *이미 작동* (line 130-144)
- 외부 SIGKILL 후 재진입 시 자동 복구 가능
- 그러나 정리가 *silent* — AI 는 막힌 게 풀린 줄 모름
- HARNESS_ONLY_AGENTS / plugin-write-guard 차단도 *대안 안내 없음* — AI 가 다른 우회 시도

**[6.1] 패닉 회로 차단 (3 deny 메시지)**:
- `hooks/agent-gate.py` HARNESS_ONLY_AGENTS deny — "🚫 패닉 회로" 섹션 추가:
  1. executor.py 재실행 (`--force-retry` 옵션으로 cooldown 우회)
  2. 새 셸/세션 (stale 상태 자동 복구)
  3. 그래도 막히면 유저 보고 — 메인 Claude 영역 아님
- `hooks/plugin-write-guard.py` deny — 동일 패턴 + 정상 경로 안내 (커스텀 스킬은 ~/.claude/commands/, 에이전트 컨텍스트는 .claude/agent-config/, 우회 필요시 `export CLAUDE_ALLOW_PLUGIN_EDIT=1`)

**[6.2] stale lock 가시성**:
- `harness/executor.py:130-144` lock 파일 PID 검사 결과 죽은 PID → 기존: `lock_file.unlink(missing_ok=True)` silent. 신규: `print("[HARNESS] 직전 실행 PID=X 죽음 — stale lock 자동 정리 (마지막 heartbeat N초 전). 재진행합니다.")`
- 손상된 lock 파일도 동일 — silent → 명시 메시지

**비변경 (의도)**:
- `agent_call` watchdog 자체 — 이미 timeout 시 subprocess.terminate + kill. 정상 동작
- atexit + SIGTERM/SIGINT 핸들러 — 이미 cleanup 등록. 정상 동작
- 이슈 lock heartbeat — 이미 존재. 별도 추가 불필요

**검증**:
- python3 -m py_compile harness/executor.py hooks/agent-gate.py hooks/plugin-write-guard.py — OK
- bash scripts/smoke-test.sh — 56/56 PASS (회귀 없음)
- python3 -m unittest tests.pytest.test_tracker — 33/33 OK

**Linked**:
- jajang 사례 (2026-04-28): "니가 인프라를 왜 건들어" 유저 차단
- `HARNESS-CHG-20260428-04` (PR #4): 같은 사례 1단계 (path)
- `HARNESS-CHG-20260428-05` (PR #5): 같은 사례 2단계 (marker)
- 본 PR: 같은 사례 3단계 (process recovery panic)

**Exception**: —

---

## `HARNESS-CHG-20260428-07` — 2026-04-28 — migration systematic audit (PR #4 follow-up)

**Type**: infra (commands + scripts + docs)

**Branch**: `harness/migration-audit`

**Issue**: jajang 사례 — `/harness-review` 스킬 실행 시 `~/.claude/scripts/harness-review.py` No such file. PR #4 가 `~/.claude/harness/executor.py` 만 잡고 같은 systematic drift 의 다른 파일은 놓침.

**원인 — 마이그레이션 부실 입증**:
- 업스트림 `alruminum/ClaudeCodeAgentPrompt` 자체가 `~/.claude/` 임 → 모든 절대경로 reference 가 자기를 가리킴 (정상)
- `migrate-step2.sh:85-100` 가 `~/.claude/{harness,scripts,setup-harness.sh}` *적극 삭제*
- 그러나 파일 내부 *reference* 는 *그대로* — 마이그레이션이 file copy 만 하고 reference rewrite 안 함
- PR #4 가 일부 패턴 잡았지만 systematic 정리 안 했음

**검증**:
```
업스트림 commands/harness-review.md:21 → ~/.claude/scripts/harness-review.py
RWHarness commands/harness-review.md:21 → ~/.claude/scripts/harness-review.py (변경 안 됨)
```

**수정 (5 파일 9 위치)**:
- `commands/harness-review.md` (4 위치) — `~/.claude/scripts/harness-review.py` → env-aware
- `commands/init-rwh.md` (2 위치) — `~/.claude/setup-harness.sh` → `${CLAUDE_PLUGIN_ROOT}/scripts/setup-rwh.sh` (이름도 정정)
- `scripts/classify-miss-report.py` (2 위치, docstring) — usage 라인 env-aware
- `scripts/harness-review.py` (5 위치) — fix recommendation 메시지 + classify-miss-report 호출 안내 → env-aware
- `scripts/setup-rwh.sh` (1 위치, 헤더 주석) — 사용법 안내 정리 (~/.claude/scripts/setup-rwh.sh 폴백 → 소스 클론 직접 사용 폴백)
- `docs/e2e-quickstart.md` (1 위치) — 옵션 C 안내 텍스트 정정
- `docs/harness-architecture.md` (1 위치) — 등록 경로 행 정정

**비변경 (의도)**:
- `docs/migration-from-source.md` — 마이그레이션 가이드 자체. 삭제 명령어 안내는 보존
- `commands/init-rwh.md:68,123` — agents/ 위치 안내 텍스트
- `~/.claude/harness-projects.json`, `~/.claude/harness-memory.md`, `~/.claude/harness-logs/` 등 — 실제 ~/.claude/ 에 존재하는 사용자 자산. 정당
- `orchestration/upstream/*` — historical snapshot

**검증**:
- `python3 -m py_compile scripts/harness-review.py scripts/classify-miss-report.py` — OK
- `bash scripts/smoke-test.sh` — 56/56 PASS
- `python3 -m unittest tests.pytest.test_tracker` — 33/33 OK
- 잔존 `~/.claude/scripts/` 액션 가능한 위치 0건 (의도된 안내 텍스트만 남음)

**Linked**:
- jajang 사례 (2026-04-28) `/harness-review` 발화
- 업스트림 검증: `gh api repos/alruminum/ClaudeCodeAgentPrompt/contents/commands/harness-review.md`
- `HARNESS-CHG-20260428-04` (PR #4) — 같은 systematic drift 의 executor 영역
- 후속: `HARNESS-CHG-20260428-08` — validator sub-docs canonical 마커 (jajang 사례의 *별개* 카테고리)

**Exception**: —

---

## `HARNESS-CHG-20260428-08` — 2026-04-28 — validator sub-docs canonical 마커 + preamble 정확도 절대 룰

**Type**: agent (validator sub-docs + preamble)

**Branch**: `harness/validator-canonical-marker`

**Issue**: jajang 사례 — validator 가 `PLAN_LGTM` 변형 emit → `parse_marker → UNKNOWN` → `PLAN_VALIDATION_ESCALATE`. 마이그레이션 무관, 업스트림에도 동일 fragility 존재 (LLM 이 preamble.md 의 LGTM 예시 + plan-validation 의 PLAN_VALIDATION_* 혼동).

**원인 진단**:
- `parse_marker` 자체는 정상 — `PLAN_LGTM` 이 어느 docs 에도 없으므로 UNKNOWN 반환은 정확
- agent docs *내부* 일관성 부족:
  - `preamble.md` 의 마커 예시(`LGTM`, `PASS`, `FAIL`) 는 다른 에이전트 컨텍스트의 예시
  - `plan-validation.md` 의 출력 형식이 `PLAN_VALIDATION_PASS / PLAN_VALIDATION_FAIL` 평이 단어로 시작
  - LLM 이 두 스타일을 섞어 `PLAN_LGTM` 같은 변형 emit
- PR #5 의 architect canonical 마커 패턴을 validator 에 동일 적용해야 함

**[8.1] validator sub-docs canonical (4 파일)**:
- `agents/validator/plan-validation.md` — 출력 형식 끝에 `---MARKER:PLAN_VALIDATION_PASS---` 정형 마커 + 변형 금지 안내
- `agents/validator/code-validation.md` — `---MARKER:PASS---` / `FAIL` / `SPEC_MISSING` 정형화
- `agents/validator/design-validation.md` — `---MARKER:DESIGN_REVIEW_PASS---` / `FAIL` / `ESCALATE` 3가지 모두 canonical 화
- `agents/validator/bugfix-validation.md` — `---MARKER:BUGFIX_PASS---` / `FAIL` 정형화
- `agents/validator/ux-validation.md` — *변경 없음* (이미 canonical 형식)

**[8.2] preamble 마커명 정확도 절대 룰**:
- `agents/preamble.md` § "마커명 정확도 (절대 룰)" 신규
- 자기 모드의 sub-doc 에 정의된 *정확한 글자만* emit
- 다른 에이전트 컨텍스트의 예시 차용 금지 명시
- Bad: `PLAN_LGTM` / `DESIGN_LGTM` / `BUGFIX_LGTM`
- Good: `PLAN_VALIDATION_PASS` / `DESIGN_REVIEW_PASS` / `BUGFIX_PASS`
- jajang 실측 사례 출처 명시

**비변경 (의도)**:
- `parse_marker` 자체 — 정상 동작. 변경 시 false positive 위험
- `harness/core.py` 의 validator 호출 부분 — 기대 마커는 그대로 (PLAN_VALIDATION_PASS / FAIL)

**검증**:
- `bash scripts/smoke-test.sh` — 56/56 PASS (회귀 없음)
- `python3 -m unittest tests.pytest.test_tracker` — 33/33 OK

**Linked**:
- jajang 사용자 사례 (2026-04-28): validator PLAN_LGTM emit
- 업스트림 검증: `gh api repos/alruminum/ClaudeCodeAgentPrompt` — 업스트림에도 같은 fragility 존재
- `HARNESS-CHG-20260428-05` (PR #5) — architect canonical 마커. 본 PR 은 validator 영역 동일 패턴

**Exception**: —

---

## `HARNESS-CHG-20260428-09` — 2026-04-28 — parse_marker alias map (LLM 변형 흡수)

**Type**: infra (harness/core.py + tests)

**Branch**: `harness/marker-alias-map`

**Issue**: PR #8 의 canonical 마커 + preamble 절대 룰이 *이미 적용된 상태* (jajang 의 plugin cache 가 RWHarness main 으로 symlink — dev 모드, 변경 즉시 live) 에서도 validator 가 `PLAN_OK` / `APPROVE` 변형 emit → `parse_marker → UNKNOWN` → `PLAN_VALIDATION_ESCALATE` 또 발생.

**근본 원인**: agent docs 강화는 *주 방어선* 이지만 LLM 이 룰 따르지 않는 사례 존재. agent docs 만 의지하는 건 fragile — *defense in depth* 필요.

**[9.1] alias map**:
- `harness/core.py:523-580` — `MARKER_ALIASES` dict 신규
  - 변형 키 → canonical 값 (호출자 expected set 안 일 때만 normalize)
  - PLAN_LGTM / PLAN_OK / PLAN_APPROVE / PLAN_APPROVED → PLAN_VALIDATION_PASS
  - PLAN_REJECT / PLAN_REJECTED / PLAN_NOT_APPROVED → PLAN_VALIDATION_FAIL
  - DESIGN_LGTM / DESIGN_OK / DESIGN_APPROVE → DESIGN_REVIEW_PASS
  - DESIGN_REJECT / DESIGN_REJECTED → DESIGN_REVIEW_FAIL
  - BUGFIX_LGTM / BUGFIX_OK / BUGFIX_APPROVE → BUGFIX_PASS
  - UX_LGTM / UX_OK / UX_APPROVE → UX_REVIEW_PASS, UX_REJECT → UX_REVIEW_FAIL
  - CODE_LGTM / CODE_OK / CODE_APPROVE → PASS
  - 일반: APPROVE/APPROVED/OK → PASS, REJECT/REJECTED/NOT_APPROVED → FAIL

- `parse_marker` 3차 폴백 로직 추가:
  1차 `---MARKER:X---` (canonical 정형) → 매치 시 그대로
  2차 `\bX\b` (canonical 워드 바운더리) → 매치 시 그대로
  3차 alias map 의 변형이 ---MARKER 또는 워드 바운더리로 출현 + 그 canonical 이 호출자 expected set 안 → normalize 해서 반환 + stderr 경고

- stderr 경고: "alias hit — 'PLAN_OK' → 'PLAN_VALIDATION_PASS' (agent docs canonical 룰 강화 권장)" — 발생 시 agent docs 보강 시그널

**보존 (false positive 차단)**:
- LGTM 단독 매핑 안 함 — pr-reviewer 의 정식 마커이기도 해서 충돌
- alias 는 호출자가 *해당 canonical 을 expected set 에 포함* 시킬 때만 적용. 다른 컨텍스트의 alias 차용 차단
- canonical 이 같은 파일에 있으면 1차/2차 우선 (alias 는 마지막 폴백)

**검증**:
- `tests/pytest/test_tracker.py` ParseMarkerAliasTests 11 케이스 신규
  - canonical 우선 / alias 정상 normalize / 다른 컨텍스트 거부 / unknown 보존
- 33→44 케이스. 100% 통과.
- bash scripts/smoke-test.sh — 56/56 (회귀 없음)

**Linked**:
- jajang 사례 (2026-04-28) `PLAN_OK / APPROVE` 변형 emit
- `HARNESS-CHG-20260428-08` (PR #8) — agent docs canonical 룰. *주 방어선*. 본 PR 은 *defense in depth* 보완

**Exception**: —

---

## `HARNESS-CHG-20260428-10` — 2026-04-28 — migration audit cleanup (4건)

**Type**: infra (코드 + README)

**Branch**: `harness/audit-cleanup`

**Issue**: 마이그레이션 systematic audit (`HARNESS-CHG-20260428-07` 후속) 잔존 4건 정리.

**[10.1] 4건 일괄**:

1. `harness/notify.py:19` (HIGH — 테스터 차단) — CLI 테스트 예시 `~/.claude/harness/notify.py` 가 마이그레이션으로 삭제된 경로
   → `${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/marketplaces/realworld-harness}/harness/notify.py`

2. `hooks/plugin-write-guard.py:83` (MID — 메시지 정확도) — 우회 안내가 `~/.claude/hooks/*.py` 로 되어 있으나 플러그인 모드에선 `${CLAUDE_PLUGIN_ROOT}/hooks/`
   → "${CLAUDE_PLUGIN_ROOT}/hooks/*.py 또는 자체 플러그인의 hooks"

3. `hooks/harness-settings-watcher.py:42,54` (MID — 메시지 정확도) — 글로벌 hooks 변경 시 안내 메시지가 *삭제된* `~/.claude/setup-harness.sh` 를 가리킴
   → 라인 42: "플러그인의 `hooks/hooks.json` 또는 `scripts/setup-rwh.sh`에도 반영 필요"
   → 라인 54: "플러그인의 `hooks/hooks.json` (자동 로드) 또는 전역 `~/.claude/settings.json` 에서만 관리"

4. `README.md` §C (MID-HIGH — 신규 사용자 혼동) — 옵션 A/B/C 구조에서 §C 가 "기존 사용자 전용" 임이 모호 → 신규가 잘못 진입 가능
   → §C 헤더에 "*기존* 사용자만" 추가 + 명시적 경고 박스 ("**신규 사용자는 §A 사용. §C 는 과거에 ~/.claude 에 직접 hooks/, harness/, agents/ 를 두고 사용하던 사용자 전용 경로**")

**비변경 (의도)**:
- audit 발견 5번 (MCP 도구 hard-fail) — qa.md / designer.md 는 PR #1 에서 Bash + tracker CLI 폴백 이미 추가됨. architect/ux-architect 는 design-only flow 로 한정. critical 아님 → 별도 검토
- audit 발견 9번 (업스트림 후속 변경 갭) — Phase 4 마이그레이션 완료 단계의 기술 부채. 긴급 아님

**검증**:
- `python3 -m py_compile harness/notify.py hooks/plugin-write-guard.py hooks/harness-settings-watcher.py` — OK
- `python3 -m unittest tests.pytest.test_tracker` — 44/44 OK
- `bash scripts/smoke-test.sh` — 56/56 PASS

**Linked**:
- `HARNESS-CHG-20260428-07` (PR #7) — migration systematic audit. 본 PR 은 그 audit 의 잔존 4건 정리
- audit 보고서 (subagent 결과, 2026-04-28)

**Exception**: —

---

## `HARNESS-CHG-20260428-11` — 2026-04-28 — `--force-retry` 확장 (escalate_history 청소)

**Type**: infra (executor + impl_router)

**Branch**: `harness/force-retry-clears-escalate`

**Issue**: jajang 사례 — `parse_marker` alias map (PR #9) 도입 후에도 `_maybe_auto_spec_gap` 가 *과거 false failure* 2건을 보고 architect SPEC_GAP 자동 발동. 사용자가 jajang 의 `escalate_history.json` 을 수동 편집해야 unstuck.

**근본 원인**:
- `record_escalate` 가 모든 ESCALATE 를 history 에 기록 (의도)
- `_maybe_auto_spec_gap` 가 누적 ≥ 2 면 자동 SPEC_GAP 호출 (의도)
- 그러나 *parser bug 가 만든 false failure* 도 동일하게 누적됨 → 파서 fix 후에도 historical count 유지
- 기존 `--force-retry` 는 `merge_cooldown` 만 청소. `escalate_history` 청소 수단 부재

**[11.1] `--force-retry` 확장**:
- `harness/executor.py:102-118` — args.force_retry 분기에서 `clear_escalate_count(state_dir, args.impl_file)` 추가 호출
- 조건: `args.impl_file` 있을 때만 (impl-target 한정 청소, 다른 impl history 보존)
- 메시지: `"[HARNESS] escalate history 청소: <impl_file>"`
- argparse help 텍스트 업데이트 — "stale state 일괄 청소 (merge_cooldown + escalate_history)"

**[11.2] auto_spec_gap 안내 메시지 강화**:
- `harness/impl_router.py:64` 직후 추가 라인:
  ```
  [HARNESS]   ↳ 직전 ESCALATE 가 *false failure* 였다고 판단되면(예: 마커 파서
              mismatch 후 alias map 도입) `--force-retry` 플래그로 재실행하여 history 청소.
  ```

**검증**:
- `python3 -m py_compile harness/executor.py harness/impl_router.py` — OK
- `bash scripts/smoke-test.sh` — 56/56 PASS
- `python3 -m unittest tests.pytest.test_tracker` — 44/44 OK

**비변경 (의도)**:
- `record_escalate` / `_maybe_auto_spec_gap` 자체 — 정상 동작 (legitimate 누적 ESCALATE 시 architect SPEC_GAP 트리거는 가치 있음)
- 자동 청소 로직 추가 안 함 — false vs legitimate 자동 판별 불가능 (파서 fix 시점 비교 같은 휴리스틱은 fragile)

**Linked**:
- jajang 사례 (2026-04-28) `executor impl --impl ...` 후 architect 자동 발동
- `HARNESS-CHG-20260428-09` (PR #9) — alias map 도입 (이번 false failure 의 원인 fix). 본 PR 은 그 fix 후 stale state 청소 수단

**Exception**: —

---

> 새 항목은 위 표 + 본 섹션 양쪽에 추가. Phase 2 자동 게이트가 활성화되면 표는 `scripts/check_doc_sync.py` 가 갱신 검증.
