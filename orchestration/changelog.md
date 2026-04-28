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
| `HARNESS-CHG-20260428-12` | 2026-04-28 | infra | [12.1] PLUGIN_ROOT `__file__` self-detect — env 미설정 시 `~/.claude` 폴백(post-migration 무효) 대신 `${plugin}/harness/core.py` 위치에서 root 추론. session_state import 안정화 (jajang 사례 — bash `${VAR:-...}` path 확장은 env export 아님) | — |
| `HARNESS-CHG-20260428-13.1` | 2026-04-28 | docs | Phase 2 Iter 1 (W1+W3) — 가드 카탈로그 7개 (5개 W2 포함 / 2개 제외: issue-gate, plugin-write-guard) + spec §0 [invariant-shift] PR 토큰 정식 도입 + §3 I-1/I-2/I-7/I-9 보호 대상↔모델 분리 + architecture §5.6/§5.7 Layered Defense + §5.8 Staged Rollout + rationale 4섹션 + 5번째 위험 패턴 (Cross-guard Silent Dependency Chain) | — |
| `HARNESS-CHG-20260428-13.2` | 2026-04-28 | infra | Phase 2 Iter 2 (W2+W4) — 5 가드 + 1 ralph fallback + Layered Defense 보강. config.py engineer_scope 필드 + tracker.MUTATING_SUBCOMMANDS SSOT + harness_common 4개 헬퍼(_load_engineer_scope/auto_gc_stale_flag/_verify_live_json_writable/_STATIC_ENGINEER_SCOPE) + session_state.update_live 쓰기 실패 stderr 표준화 + executor.py round-trip canary(always-on) + HARNESS_ACTIVE flag heartbeat + agent-boundary/commit-gate/agent-gate/skill-gate/skill-stop-protect V2 분기 + ralph-session-stop 3-layer fallback(HARNESS_GUARD_V2_RALPH_FALLBACK, default off). 모든 V2 env unset 시 v1 동작 100% 회귀 0. py_compile + smoke-test 57/57 PASS. | — |
| `HARNESS-CHG-20260428-13.3` | 2026-04-28 | test  | Phase 2 Iter 3 (W5) — 회귀 테스트 + jajang fixtures + smoke-test 시나리오. `tests/pytest/test_guards.py` 신규 (101 케이스, 18 REQ 전수 / V2 on·off 양쪽 검증) + `tests/pytest/conftest.py` 신규 + 4 fixture 디렉토리(jajang_monorepo / llm_marker_variants / jajang_4categories / cross_guard_silent_dependency A·B) + `scripts/smoke-test.sh` 시나리오 10~14 추가(monorepo / env unset / LLM 변형 / cross-flag / silent dependency 가시화). pytest 101/101 + smoke-test 70/70 PASS. 코드 결함 0건(test 기술만 정정). 5번째 위험(Cross-guard Silent Dependency Chain) 본 ralph-loop Iter 2→3 transition 에서 production 재발 — 영구 fix가 default off라 v1 동작 그대로, 시나리오 A/B 자동 회귀 테스트화. invariant 변경 없음 → `[invariant-shift]` 토큰 미사용. | — |
| `HARNESS-CHG-20260428-14.1` | 2026-04-28 | infra | MARKER_ALIASES 12개 변형 추가 — PLAN_VALIDATION(PLAN_VALIDATED/PLAN_VERIFIED/PLAN_PASS/PLAN_INVALID) + LIGHT_PLAN_READY(LIGHT_PLAN_DONE/LIGHT_PLAN_COMPLETE/LIGHT_PLAN_WRITTEN/BUGFIX_PLAN_READY) + READY_FOR_IMPL(MODULE_PLAN_READY/MODULE_PLAN_DONE/IMPL_PLAN_READY/IMPL_READY/PLAN_DONE/PLAN_WRITTEN/PLAN_COMPLETE). validator/architect 가 canonical 대신 자유 텍스트 변형 emit 시 SPEC_GAP_ESCALATE / PLAN_VALIDATION_ESCALATE 로 attempt 무위 소진되던 사례 차단. defense in depth 2nd layer 두꺼워짐. | — |
| `HARNESS-CHG-20260428-14.2` | 2026-04-28 | infra | WorktreeManager.create_or_reuse 에 untracked plan 파일 자동 복사 추가 — `git worktree add` 직후 main repo `ls-files --others --exclude-standard` 결과 중 `docs/bugfix/`, `docs/impl/`, `docs/milestones/` prefix 파일을 worktree 같은 상대경로로 cp. architect 가 main repo 에 LIGHT_PLAN 작성 후 commit 전 worktree 진입하면 engineer 가 'impl 파일 없음' no_changes 로 attempt 0 무위 소진되던 사고 차단. 안전 패턴: plan 디렉토리만 — src/ 등은 worktree 경계 보호 위해 제외. | — |
| `HARNESS-CHG-20260428-14.3` | 2026-04-28 | infra | TDD 순서 강제 — impl_loop.py:928 `_tdd_active` 조건에서 `bool(config.test_command)` 의존성 제거. 1209 의 옛 폴백(engineer→test-engineer, OLD 순서) elif 블록 제거. test_command 부재가 TDD 자체를 끄지 않도록 — 테스트 작성은 회귀 방어 + impl 명세 검증 목적도 있고, RED/GREEN 실측 게이트만 test_command 가드 유지. jajang 류 std/deep 프로젝트에서 engineer 가 test-engineer 보다 먼저 실행되던 룰 위반 차단. | — |
| `HARNESS-CHG-20260428-14.4` | 2026-04-28 | docs  | pr-reviewer.md 에 에이전트 스코프 매트릭스 섹션 추가 — `hooks/agent-boundary.py` `ALLOW_MATRIX` 명시 + 스코프 밖 파일(docs/bugfix/**, docs/impl/**, package.json 등) 발견 시 NICE TO HAVE 강등 + 라우팅 권고 명시. MUST FIX 는 engineer/test-engineer 스코프 안 파일에만 발행. pr-reviewer 가 boundary 모르고 모든 영역에 MUST FIX 발행 → engineer boundary 차단 → no_changes 사이클 차단. | — |
| `HARNESS-CHG-20260428-14.5` | 2026-04-28 | infra | impl_loop.py automated_checks 분기에 `no_changes` 별도 fail_type 추가 — `check_err.startswith("no_changes:")` 시 즉시 `IMPLEMENTATION_ESCALATE` (run_simple/_run_std_deep 양쪽). 옛 동작: 모든 autocheck 실패가 `autocheck_fail` 로 단일 분류 → circuit breaker 가 2회 누적 후에야 fire → boundary block 시 attempt 2회 무위 ($1.5+) 소진. 새 동작: no_changes 1회만에 escalate (boundary block / missing impl / 컨텍스트 손실 등 retry 무의미한 카테고리). | — |
| `HARNESS-CHG-20260428-19` | 2026-04-28 | infra | [19.1] `current_session_id()` 글로벌 폴백 + 4중 가드 — RWHarness dogfooding 환경(화이트리스트 미등록 → 프로젝트 pointer 미생성)에서 live.json.agent silent skip 버그 차단. `~/.claude/harness-state/.session-id` 폴백 + 파일존재/sid형식/자기참조/6h신선도 가드. 회귀 0 (env > project > global 우선순위 보존, 폴백 실패 시 빈 문자열). 단위 테스트 9TC 신규. py_compile OK / pytest 9/9 / 회귀 101/101 / smoke 70/70 / dogfooding 실측 c86ce041-... 반환 확인. | — |
| `HARNESS-CHG-20260428-24` | 2026-04-28 | infra | [24.1] src/ 하드코딩 잔존 8 사이트 일괄 fix — `harness/path_resolver.py` 신규 (7 헬퍼 SSOT) + `harness/config.py` ui_components_paths/test_paths 필드 추가 + 5 executor 파일 패치 (S1-S7,S9). `HARNESS_GUARD_V2_PATHS_EXECUTOR=1` staged flag (default off, v1 fallback 보장). `HARNESS_GUARD_V2_PATHS_TEST_REGEX_OFF=1` 비상탈출. 회귀 0: py_compile ALL OK / pytest 14/14 신규 + 110/110 회귀 / smoke 74/74 PASS. | — |
| `HARNESS-CHG-20260428-25` | 2026-04-28 | hotfix | [25.1] PR #25 회귀 hotfix — 인라인 `from .path_resolver import X` 9 사이트에 `try/except ImportError` 추가. `python3 harness/core.py` 직접 실행(no parent package) 시 `ImportError: attempted relative import with no known parent package` 크래시 수정. `tests/pytest/test_executor_direct_imports.py` 신규 9 TC — subprocess 직접 실행 시뮬레이션 회귀 테스트. 회귀 0: py_compile ALL OK / pytest 9/9 신규 + 168/168 회귀 (총 177). | — |
| `HARNESS-CHG-20260428-26` | 2026-04-28 | infra | [26.1] worktree 재사용 시 untracked plan 파일 자동 복사 — `create_or_reuse` reuse 분기(`wt_path.exists()` 즉시 return)가 `_copy_untracked_plan_files` 를 건너뛰던 hole 수정. `reused` 플래그 도입, 재사용 worktree 에 이미 존재하는 파일은 덮어쓰기 금지(dst.exists 가드). `tests/pytest/test_worktree.py` 신규 3TC (REQ-001 reuse 복사 / REQ-002 기존 보존 / REQ-003 fresh 회귀 0). pytest 3/3 + 전체 171/171 PASS. Closes #26. | — |
| `HARNESS-CHG-20260428-26` | 2026-04-28 | infra | [26.2] PR review 반영 — `_copy_untracked_plan_files` 내 `import shutil` 중복 제거 (최상단 이미 존재) + `_git("ls-files", ...)` 에 `cwd=str(self.project_root)` 명시 (worktree cwd 에서 호출 시 main repo 스캔 보장). REQ-005 cwd 독립성 회귀 테스트 추가. pytest 5/5 + 전체 173/173 PASS. | — |
| `HARNESS-CHG-20260428-26` | 2026-04-28 | infra | [26.3] LIGHT_PLAN 산출물 동봉 — `docs/impl/26-worktree-reuse-plan-copy.md` 추가 ([24.1] [19.1] 등 기존 패턴과 일관). | — |
| `HARNESS-CHG-20260428-27` | 2026-04-28 | infra | [27.A1] light-plan template 분기 enumeration 섹션 강제 — `agents/architect/light-plan.md` 템플릿에 `## 분기 enumeration` 섹션 + LIGHT_PLAN_READY 자가 체크 5항목(+1행) 추가. `agents/validator/plan-validation.md` §A 체크리스트에 분기 enumeration 행 추가 + 출력 표 동기화. `tests/pytest/test_plan_template.py` 신규 6 TC (합성 픽스처 5 + self-apply 1). [14.2] hole (#26) 재발 차단 — reuse 분기 누락 → 단일행 enumeration → PLAN_VALIDATION_FAIL 게이트 강제. pytest 6/6 신규 + 188/188 전체 PASS. Closes #31. | — |
| `HARNESS-CHG-20260428-27` | 2026-04-28 | infra | [27.A1.plan] LIGHT_PLAN 산출물 동봉 — `docs/impl/31-light-plan-branch-enumeration.md` 추가 ([24.1] [19.1] [26.3] 패턴과 일관). | — |
| `HARNESS-CHG-20260428-27` | 2026-04-28 | infra | [27.A2] PR-time harness/** ↔ tests/** 동반 게이트 (Tests-Exception 패턴) — `scripts/check_test_sync.py` 신규 (check_doc_sync.py 골격 이식, TRIGGER_PATTERNS harness/+hooks/, Tests-Exception 마커). `.github/workflows/test-sync.yml` 신규 (doc-sync.yml 1:1 복사 + step 이름·경로 교체). `orchestration/policies.md` §8 신규 (test-sync 게이트 + Tests-Exception 스코핑 + 통합 지점) + 기존 §7 → §9 재번호. `tests/pytest/test_check_test_sync.py` 신규 8 TC (REQ-001~005 + 보조 3건 — 사유 짧음/빈 사유/과거 commit 재사용 hole 차단). pytest 8/8 신규 + 196/196 전체 PASS. Closes #32. | — |
| `HARNESS-CHG-20260428-27` | 2026-04-28 | infra | [27.A2.plan] LIGHT_PLAN 산출물 동봉 — `docs/impl/32-pr-time-test-sync-gate.md` 추가 ([26.3] [27.A1.plan] 패턴과 일관). | — |
| `HARNESS-CHG-20260428-27` | 2026-04-28 | infra | [27.A2.fixup] PR review 반영 — `check_test_sync.py` REPO_ROOT 상수 추가 + `CHECK_TEST_SYNC_ROOT` env 오버라이드로 silent wrong-repo 방지. docstring 오타 "무효 사유 사유" → "무효 사유 메시지". `test_check_test_sync.py` import tempfile 상단 통합 + env 주입 격리. `orchestration/policies.md` "갱신 예정" 문구 → §6 §8 현 상태 반영. pytest 8/8 + 196/196 PASS. | — |
| `HARNESS-CHG-20260428-34` | 2026-04-28 | infra | [34.1] autocheck no_changes 오판 — test-only commit PASS + stranded 방지. `helpers.py` no_changes 분기에 `git log -1 --name-only HEAD` 직전 커밋 검사 추가 + `_classify_last_commit_files()` (5개 카테고리: empty/test_only/plan_only/test_and_plan/mixed) 신설. test_only/plan_only/test_and_plan → PASS 처리(후속 lint/build/test 체크 fall-through). mixed/empty → escalate 유지 + `rollback_attempt(hard_reset=True)` 로 stranded 방지. `path_resolver._V1_TEST_PATHS_REGEX` pytest/jest 디렉토리 패턴 보강 (G4 SSOT). `core._PLAN_PREFIXES` 클래스 속성 → 모듈 레벨 승격 (G1 SSOT, helpers 가 import 가능). `rollback_attempt` keyword-only `hard_reset/feature_branch/cwd` 옵션 추가 (16개 기존 caller 호환). impl_loop.py no_changes 2곳 hard_reset=True 업그레이드. `tests/pytest/test_autocheck_no_changes.py` 신규 (7클래스 19TC — REQ-001~003, REQ-006~008, G5). 회귀 0. | — |
| `HARNESS-CHG-20260428-36` | 2026-04-28 | infra | [36.1] SessionStart stale worktree sweep — 외부(수동 `gh pr merge`) 머지된 worktree 자동 정리. `hooks/worktree_sweep.py` 신규 (`sweep()`/`format_report()`) — `git worktree list --porcelain` × `git branch -r --merged origin/<default>` 교차로 후보 추출, 3중 안전장치(working tree clean + unpushed commit 0 + 머지 확인) 통과 시 `git worktree remove --force` + `git branch -D`. unpushed commit 있으면 stderr 경고만 (jajang `611fbb8` 류 stranded 보호). `harness-session-start.py` 에서 호출, 결과를 stderr 1줄 요약. `tests/pytest/test_worktree_sweep.py` 신규 (7클래스 10TC — REQ-001~007: 머지+clean+pushed 제거 / 미머지 skip / unpushed 경고 / dirty 경고 / main 보호 / idempotent / report 포맷). pytest 10/10 신규 + 225/225 전체 PASS. Closes #36. | — |
| `HARNESS-CHG-20260428-35` | 2026-04-28 | infra | [35.1] SessionStart orphaned untracked sweep — main repo 의 untracked plan 사본이 worktree PR 머지 후 origin 의 tracked 사본과 path 충돌해 `git pull` fast-forward 실패하는 hole 차단. `hooks/worktree_sweep.py` 에 `sweep_orphaned_untracked()`/`format_orphaned_report()` 추가 — `git fetch` 후 untracked × `git diff --diff-filter=A HEAD..origin/<default>` 교차로 후보 추출, content 동일 시 자동 삭제 (origin tracked 가 정본). content 다르면 stderr 경고만 (사용자 수정 보호). `harness-session-start.py` 에서 worktree sweep 직후 호출. `tests/pytest/test_orphaned_untracked_sweep.py` 신규 (6클래스 8TC — 동일 content 삭제 / 다른 content 경고 / 무관 untracked 보존 / idempotent / origin 없음 silent / report 포맷). pytest 8/8 신규 + 233/233 전체 PASS. Closes #35. | — |
| `HARNESS-CHG-20260428-37` | 2026-04-28 | infra | [37.1] SessionStart 마켓플레이스 클론 auto-pull — bash 가 `${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/marketplaces/realworld-harness}/...` 폴백으로 진입할 때 stale 클론(c094154 정체 케이스)이 옛 core.py 실행 → `import session_state` 실패 → 후속 fix(12.1/19.1/26.1/34/35/36) 무력화되던 hole 차단. `harness-session-start.py` 의 stale 세션 정리 직후 `git -C ~/.claude/plugins/marketplaces/realworld-harness pull --ff-only --quiet` 실행 (실패 silent, timeout 10s). `tests/pytest/test_marketplace_auto_pull.py` 신규 (5클래스 5TC — stale 동기화 / 이미 동기 noop / .git 없음 skip / dirty 보존 / non-ff 보존). pytest 5/5 신규 + 238/238 전체 PASS. jajang issue #22 silent skip 직접 원인 영구 차단. | — |
| `HARNESS-CHG-20260428-38` | 2026-04-28 | infra | [38.1] product-planner 정체성 선언 강화 — jajang 5회 연속 self-recognition 실패(자기를 메인 Claude 로 착각, "product-planner 에게 위임 권고" 류 출력) 차단. `agents/product-planner.md` 최상단에 🔴 정체성 섹션 + 5개 금지 패턴 명시 (case 1~5 회귀 사례 박제). 기존 "메인 Claude와 architect" 표현을 "당신을 호출한 메인 Claude" 로 명료화. `tests/pytest/test_planner_identity.py` 신규 (4클래스 8TC — 정체성 섹션 / 명시적 자기선언 / 금지 패턴 4종 / 마커 요구 / 모드 마커 처리 / 출력 마커 보존). pytest 8/8 신규 + 246/246 전체 PASS. | — |
| `HARNESS-CHG-20260428-39` | 2026-04-28 | infra | [39.1] `/sync-for-dog` 스킬 신설 — RWHarness dogfooding 시 source → marketplace → cache 일괄 동기화. plugin 매니저 호환을 위해 cache 는 real directory 유지하면서 rsync mirror 로 dogfooding 즉시 반영. SessionStart auto-pull (HARNESS-CHG-37) 가 marketplace 까지만 갱신하던 갭 보강 — cache 까지 명시적 mirror 가 필요한 케이스의 단일 진입점. 검증 단계로 hooks/session_state.py, agents/product-planner.md, harness/core.py 의 source vs cache diff 검사. uncommitted 변경도 working tree 기준 mirror 가능 (commit 전 dogfooding 지원). 2026-04-28 cache symlink 가 plugin 매니저에 자동 삭제되던 사고 후 real-dir 패턴 정착. | — |
| `HARNESS-CHG-20260428-40` | 2026-04-28 | infra | [40.1] ux-architect 정체성 선언 강화 — jajang #133 plan 루프에서 ux-architect 가 동일 self-recognition 실패("메인 Claude 세션이라 서브에이전트로 진입하지 않습니다... /ux-sync 또는 명시적인 요청 주세요") 발생. HARNESS-CHG-38 (#42) 에서 product-planner 에 적용한 동일 패턴을 ux-architect 에도 적용. `agents/ux-architect.md` 최상단에 🔴 정체성 섹션 + 6개 금지 패턴 박제 (jajang 실 케이스 포함). 4개 출력 마커 명시(UX_FLOW_READY / UX_FLOW_PATCHED / UX_REFINE_READY / UX_FLOW_ESCALATE) — 모드별 정확한 마커 요구. `tests/pytest/test_ux_architect_identity.py` 신규 (4클래스 10TC). pytest 10/10 신규 + 256/256 전체 PASS. | — |
| `HARNESS-CHG-20260428-41` | 2026-04-28 | infra | [41.1] plan_loop checkpoint 부분 저장 hole 차단 — jajang #133 시나리오에서 plan-reviewer PASS 후 ux-architect 실패 시 `{prefix}_plan_metadata.json` 미저장 → 재실행 시 PRD 체크포인트 손실 → planner 처음부터 재실행되던 버그. metadata 저장 로직을 `save_plan_checkpoint(state_dir, prefix, prd_path, issue_num, ux_flow_doc?)` helper 로 추출 + plan-reviewer PASS 직후 partial 저장 호출 추가 (ux_flow_doc 키 생략). 기존 PLAN_REVIEW_CHANGES_REQUESTED 분기와 ux-validation 완료 후 full 저장 분기는 helper 사용으로 통합 (drift 방지). `tests/pytest/test_plan_checkpoint.py` 신규 (6클래스 7TC — partial / full / upgrade / prefix 격리 / int issue_num / jajang #133 회귀 시나리오). pytest 7/7 신규 + 263/263 전체 PASS. | — |

---

## `HARNESS-CHG-20260428-24` — 2026-04-28 — src/ 하드코딩 8 사이트 일괄 fix (executor 내부 dynamic SSOT 전환)

**Type**: infra

**Files**:
- `harness/path_resolver.py` — 신규. 7 헬퍼 함수 (engineer_scope_pathspecs / extract_regex / grep_paths / any_exists / human_dir_list / ui_components_paths / test_paths_extract_regex). V2 flag 기반 staged rollout + v1 fallback 보장.
- `harness/config.py` — `ui_components_paths: list`, `test_paths: list` 필드 추가 + load_config 매핑
- `harness/helpers.py` — S1 (line 295): git diff pathspec → `engineer_scope_pathspecs()`
- `harness/core.py` — S2 (line 1818): impl 추출 regex, S3 (line 1824): error trace 추출 regex → `engineer_scope_extract_regex()`. S4 (line 1906): design loop UI 컴포넌트 → `ui_components_paths()`
- `harness/impl_router.py` — S5 (line 320): LIGHT_PLAN grep → `engineer_scope_grep_paths()`
- `harness/impl_loop.py` — S6 (line 993): test-engineer 산출 추출 → `test_paths_extract_regex()`
- `harness/plan_loop.py` — S7 (line 286): UX_SYNC 분기 → `engineer_scope_any_exists()`. S9 (line 298): ux-architect src_dir → `engineer_scope_human_dir_list()`
- `tests/pytest/test_path_resolver.py` — 신규 14 TC (impl §7.1–§7.7 8 케이스 + v1/v2 양면 분리)
- `scripts/smoke-test.sh` — [15] path_resolver V2 활성/비활성 회귀 3 step 추가
- `orchestration/changelog.md` — 본 항목

**미변경 (spec 준수)**: S8 (plan_loop.py 로그 텍스트), S10 (helpers.py 주석), S11 (core.py LLM 프롬프트), S12 (core.py 주석)

**Staged rollout**:
- `HARNESS_GUARD_V2_PATHS_EXECUTOR=1` → 8 사이트 전체 V2 활성
- `HARNESS_GUARD_V2_ALL=1` → 위 포함 전체 V2 활성 (메타 flag)
- `HARNESS_GUARD_V2_PATHS_TEST_REGEX_OFF=1` → S6 비상탈출 (v1 강제)
- default: unset → v1 fallback 100% 보장

**검증**: py_compile ALL OK / pytest 14/14 신규 + 110/110 회귀 / smoke 74/74 PASS

---

## `HARNESS-CHG-20260428-19` — 2026-04-28 — `current_session_id()` 글로벌 폴백 (dogfooding silent malfunction 차단)

**Type**: infra

**Files**:
- `hooks/session_state.py` — `current_session_id()` 3단계 글로벌 폴백 + `_read_global_session_pointer_safely()` 헬퍼 + `_GLOBAL_FALLBACK_FRESHNESS_SEC` 상수
- `tests/pytest/test_session_state_fallback.py` — 신규 9TC
- `orchestration/changelog.md` — 본 항목

**변경 요약**:
RWHarness dogfooding 환경(화이트리스트 미등록 → SessionStart 훅 조기 종료 → 프로젝트 `.session-id` 미생성)에서 `current_session_id()` 가 빈 문자열을 반환해 `core.py:980` `update_live(sid, agent=…)` 가 silent skip 되는 버그 차단.

`~/.claude/harness-state/.session-id` 를 3번째 폴백으로 추가. 4중 가드(파일존재/sid형식/자기참조/6h신선도) 모두 통과 시에만 채택. 가드 실패 시 빈 문자열 — v1 동작 유지(회귀 0).

**검증**:
- `py_compile hooks/*.py harness/*.py`: ALL OK
- `pytest tests/pytest/test_session_state_fallback.py`: 9/9 PASS
- `pytest tests/pytest/test_guards.py`: 101/101 PASS (회귀 0)
- `bash scripts/smoke-test.sh`: 70/70 PASS
- dogfooding 실측: `current_session_id()` → `'c86ce041-e4d3-4d05-83d8-d9717e7029dc'` (빈 문자열 → 실제 sid)

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

## `HARNESS-CHG-20260428-12` — 2026-04-28 — PLUGIN_ROOT __file__ self-detect

**Type**: infra (harness/core.py + executor.py + smoke-test.sh)

**Branch**: `harness/plugin-root-self-detect`

**Issue**: jajang 실측 — agent_call 호출 시 `[HARNESS] session_state 로드 실패: No module named 'session_state'` 반복. functional 영향: live.json.agent 미기록 → ISSUE_CREATORS 활성 체크 실패 → designer 등 일부 흐름 stuck 가능.

**근본 원인**:
- `PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT") or str(Path.home() / ".claude"))`
- 사용자가 bash 에서 `${CLAUDE_PLUGIN_ROOT:-...}/harness/executor.py` 형태 호출 시
- bash 의 `${VAR:-default}` 는 *path 확장만* 함, env export 아님
- → Python 이 env 미설정 봄 → 폴백 `~/.claude/hooks/` 시도 → 마이그레이션이 삭제한 경로 → import fail

**[12.1] 자기-감지 폴백** (`harness/core.py` + `executor.py`):
```python
def _resolve_plugin_root() -> Path:
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env:
        return Path(env)
    # __file__ = ${PLUGIN_ROOT}/harness/core.py — 위치에서 root 추론
    here = Path(__file__).resolve()
    if here.parent.name == "harness":
        return here.parent.parent
    return Path.home() / ".claude"  # legacy fallback
```

**[12.2] smoke-test.sh §3 갱신**:
- 폴백 검증 expected: `~/.claude` → `__file__` 기반 (실제 RWHarness root)
- session_state import 통합 테스트 추가 — env 미설정 + 폴백 시 hooks/session_state 로드 가능 확인

**검증**:
- `python3 -c "..."` env 미설정 + 명시 둘 다 정확
- `bash scripts/smoke-test.sh` — 56→57 PASS (신규 session_state 테스트 추가)
- `python3 -m unittest tests.pytest.test_tracker` — 44/44 OK

**비변경 (의도)**:
- `CLAUDE_PLUGIN_ROOT` env 우선순위 보존 — Claude Code 가 플러그인 hooks/agents 호출 시 자동 set 하는 정상 흐름 유지
- legacy `~/.claude` 폴백 보존 — 매우 예외적 케이스 (script 가 비표준 위치) 대비

**Linked**:
- jajang 사례 (2026-04-28) — agent_call session_state 로드 실패
- migration audit (PR #7) 의 *코드 내부* path 후속 — audit 가 user-facing path 만 잡고 코드 내부 PLUGIN_ROOT 폴백은 놓쳤었음

**Exception**: —

---

## `HARNESS-CHG-20260428-13.1` — 2026-04-28 — 가드 카탈로그 + spec/architecture invariant-shift (W1+W3)

**Type**: docs (guard-catalog + harness-spec §0/§3 + harness-architecture §5.6/§5.7/§5.8 + rationale.md)

**Branch**: `harness/guard-realignment-iter1`

**Issue**: #13 — Phase 2 Guard Model Realignment. W1 (catalog 게이트) + W3 (spec/architecture 정렬) Iter 1 범위. W2 (5 가드 코드 변경) / W4 (deny 메시지 enrichment + executor round-trip) / W5 (회귀 테스트 + jajang fixtures) 는 후속 Iter 2/3.

**범위**: Iter 1 = 분석·문서·계획. 코드 변경 0건. 후속 Iter 2 (W2+W4) 와 Iter 3 (W5) 는 별도 PR.

**[13.1.W1] 가드 카탈로그 작성** — `docs/guard-catalog.md` (신규):
- 활성 7개 PreToolUse 가드 전수 조사 — 보호 대상(보안 / 책임 분리 / 일관성 / 추적성 / 워크플로우 강제), 현재 모델, 환경 가정, fail mode, 재설계 권장을 가드별 1페이지로 정리.
- W2 코드 변경 포함 5개 식별:
  - `agent-boundary.py` (HIGH) — scope strict 진앙. ALLOW_MATRIX["engineer"] 동적화 (`engineer_scope` config) + Read 경계는 보안 모델 유지.
  - `commit-gate.py` (HIGH) — Gate 1/3/4/5 책임 비대 + staged regex drift. agent-boundary 와 같은 source 에서 staged 패턴 파생 + tracker `MUTATING_SUBCOMMANDS` 위임.
  - `agent-gate.py` (HIGH) — stale `HARNESS_ACTIVE` flag silent-pass + 추적 ID 단일 regex. flag age check + GC + `tracker.parse_ref()` 위임.
  - `skill-gate.py` (MEDIUM) — `live.json.skill` 쓰기 silent 실패 = downstream cascade 진앙. 쓰기 실패 stderr 경고 + 진단 집계 (passive recorder 본질 유지).
  - `skill-stop-protect.py` (MEDIUM, 부분 포함) — TTL/auto_release/max_reinforcements 모델이 가장 robust. **이 모델을 다른 가드에 일반화** 하는 reference. 자체는 진단 로그 표준만.
- W2 제외 2개 + 제외 사유:
  - `issue-gate.py` — 30 LOC 단순. 단일 fail mode (false-block, 보안적 정답). W4 진단 가시성만 흡수, 모델 변경 없음.
  - `plugin-write-guard.py` — 보안 가드 (allowlist + ENV 우회 = 정답 모델). 모노레포 가정 영향 없음. W4 진단 가시성만 흡수, 모델 변경 없음.

**[13.1.X] 위험 패턴 5번째** — guard-catalog.md §3 (Cross-guard Silent Dependency Chain):
- 4 카테고리(path hardcode / marker fragility / state persistence stuck / scope strict) 외 qa 진단에서 추가 발견.
- 시나리오 A: `skill-gate.py` 의 `live.json.skill` 쓰기 silent 실패 → `agent-boundary.py` 가 활성 스킬 못 읽음 → 메인 Claude 의 정당한 작업 false-block + 사용자에게 진단 부재.
- 시나리오 B: `agent-gate.py` 의 `live.json.agent` 쓰기 실패 → `issue-gate.py`/`commit-gate.py` Gate 1 이 ISSUE_CREATORS 활성도 차단.
- 해결: blocking layer 결정은 1차 검증 단독 + informational layer 로 silent cascade 가시화 (W4 항목 4개 — stderr 경고 표준화 / `harness-state/.logs/<guard>.jsonl` 집계 / executor round-trip canary / deny 메시지 enrichment).

**[13.1.W3] spec/architecture invariant-shift**:

`docs/harness-spec.md`:
- **§0 `[invariant-shift]` PR title 토큰 정식 룰** 신규 — §0 약화뿐 아니라 §3 invariant(I-1 ~ I-N) 의 *표현(wording) / 모델(model) / 효과 범위(scope)* 변경 PR 모두 토큰 의무화. 사용 기준(표현·모델·범위 변경) / 미사용 기준(typo·진단 로그·내부 정리) / 식별자 동반 의무(commit body `HARNESS-CHG-YYYYMMDD-NN`) 명시. pr-reviewer 가 누락 PR 자동 reject.
- **§3 I-1** — 보호 대상(책임 분리: 메인 단독 수정 차단) ↔ 현재 모델(`agent-boundary.py` ALLOW_MATRIX 동적 화이트리스트 — `engineer_scope` config + default 7 패턴 fallback) 분리. 모델 진화 시 효과 동등성 입증 의무. 보안 가드 예외(Read 경계 + plugin-write-guard 는 allowlist 모델 자체가 invariant) 명시.
- **§3 I-2** — 보호 대상(추적성: 모든 구현이 추적 ID 와 결합) ↔ 모델(`tracker.parse_ref()` 위임 — `#N` / `LOCAL-N` 형식 흡수) 분리. 향후 백엔드 추가 시 invariant 표현 유지, tracker 가 변형 흡수.
- **§3 I-7** — 활성 에이전트 판정 SSOT 는 `live.json.agent`. `HARNESS_ACTIVE` flag (executor 점유 신호) 의 age check + GC 는 본 invariant 와 무관 — 다른 상태 객체 + informational layer 폴백(`HARNESS_AGENT_NAME` env stderr 경고)도 진단용으로 deny 결정 영향 없음 명확화.
- **§3 I-9** — 보호 대상(책임 분리 + 추적성: 인프라 변경 메인 단독 차단) ↔ 모델(`HARNESS_INFRA_PATTERNS` + `is_infra_project()` 신호 1~3 OR + 위임 룰) 분리.

`docs/harness-architecture.md`:
- **§5.6 가드 정책 일람** 신규 — 7개 가드별 보호 대상 / Phase 2 W2 변경 범위 / catalog 출처 한 줄 요약 표. 정본은 `docs/guard-catalog.md`, 본 섹션은 architecture 차원 매핑.
- **§5.7 Defense-in-depth ↔ Determinism 정책 (Layered Defense)** 신규 — 두 레이어 분리:
  - **Blocking layer (결정론)**: invariant 위반 시 즉시 deny. 동일 입력 → 동일 결과 보장. 8개 항목(agent-boundary / plugin-write-guard / commit-gate Gate 1·5 / agent-gate HARNESS_ONLY·추적 ID / issue-gate / skill-stop-protect).
  - **Informational layer (진단)**: fail 시 stderr 경고 + diag log, **차단 결정 권한 없음**. 5개 항목(skill-gate 쓰기 실패 / skill-stop-protect 표준 로그 / agent-boundary live.json 폴백 / executor round-trip canary / deny 메시지 enrichment).
  - 결정론 = blocking layer 의 책임. silent dependency cascade 는 informational layer 가 가시화하되 invariant 완화하지 않음. 위반 시 §0 워크플로우 강제 위반 → `[invariant-shift]` 토큰 + rationale Alternatives 필수.
- **§5.8 Staged Rollout — `HARNESS_GUARD_V2_*` 환경변수** 신규 — 가드 모델 변경(Phase 2 W2)을 env var 로 점진 활성화. 미설정 시 v1 fallback (회귀 0):
  - 가드별 7개: `HARNESS_GUARD_V2_{AGENT_BOUNDARY,COMMIT_GATE,AGENT_GATE,SKILL_GATE,SKILL_STOP_PROTECT,ISSUE_GATE,PLUGIN_WRITE_GUARD}=1`.
  - 보조 3개: `HARNESS_GUARD_V2_FLAG_TTL_SEC=21600` (6h default), `HARNESS_GUARD_V2_DIAG_LOG_DIR=harness-state/.logs/`, `HARNESS_GUARD_V2_ALL=1` (일괄 활성, 개발 편의).
  - Stage 0~4: Iter 2 merge 직후 모두 off → jajang 재실측(AGENT_BOUNDARY+COMMIT_GATE) → 1주(AGENT_GATE) → 2주(SKILL_GATE+SKILL_STOP_PROTECT) → 배포(`HARNESS_GUARD_V2_ALL=1` default via `setup-rwh.sh`).

`orchestration/rationale.md`:
- **HARNESS-CHG-20260428-13** 항목 — 4섹션 (Context / Decision / Alternatives considered / Consequences):
  - Context: jajang 12 reactive PR 의 4 카테고리 + 5번째 cross-guard silent dependency. 7 가드 단일 모델 통일이 cascade 진앙.
  - Decision: 5+2 게이트 결정 (5 재설계 / 2 제외) + Layered Defense 명문화 + Staged Rollout + `[invariant-shift]` 토큰 정식화 + invariant 보호 대상 ↔ 모델 분리 (I-1/I-2/I-9).
  - Alternatives considered (5개): (1) 일괄 blocklist 전환 거부 / (2) validator 사후 탐지 거부 / (3) **가드별 정책 분기 + Layered + Staged 채택** / (4) skill-stop-protect TTL 모델 일괄 도입 부분 채택 (헬퍼만 일반화) / (5) issue-gate / plugin-write-guard W2 포함 거부.
  - Consequences: 4+1 카테고리 재발 구조적 차단 / 확정성 우선 (V2 코드 작성되나 env var 없이는 비활성) / 결정론 보존 (blocking ↔ informational 분리) / 회귀 위험 4개 격리 방어 (regex 컴파일 실패 / TTL 너무 짧음 / silent dependency 진단 false-positive / staged rollout flag 누락).

**검증** (Iter 1 = 문서 only, 코드 변경 X):
- `python3 -m py_compile harness/*.py hooks/*.py` — OK (변경 없음 확인).
- `bash scripts/smoke-test.sh` — 회귀 0 (Iter 1 코드 변경 없음).
- 문서 cross-link 점검 — `guard-catalog.md` ↔ `harness-spec.md` §0/§3 ↔ `harness-architecture.md` §5.6/§5.7/§5.8 ↔ `rationale.md` HARNESS-CHG-20260428-13 일치.

**비변경 (의도)**:
- 가드 코드 5개 (`agent-boundary.py`, `commit-gate.py`, `agent-gate.py`, `skill-gate.py`, `skill-stop-protect.py`) — Iter 2 (W2+W4) 에서 적용.
- `harness/config.py` `engineer_scope` 필드 / `harness/tracker.py` `parse_ref` + `MUTATING_SUBCOMMANDS` / `hooks/harness_common.py` `auto_gc_stale_flag` 헬퍼 — Iter 2.
- `harness/executor.py` live.json round-trip canary — Iter 2 (W4).
- 회귀 테스트 + jajang monorepo fixtures + LLM marker variants corpus — Iter 3 (W5).
- `issue-gate.py` / `plugin-write-guard.py` — W2 영구 제외 (rationale.md Alternatives 5번째). W4 진단 가시성만 흡수.

**Linked**:
- Issue #13 — Phase 2 Guard Model Realignment 메인 트래킹.
- `docs/guard-catalog.md` — W1 1차 산출물 (신규).
- `docs/impl/13-guard-realignment.md` — impl 계획 (Iter 2/3 작업 분해, qa 결정 A~E 반영).
- `orchestration/rationale.md` HARNESS-CHG-20260428-13 — 4섹션 결정 근거.
- 후속 PR (Iter 2): W2 5 가드 모델 변경 + W4 진단 enrichment + executor round-trip canary.
- 후속 PR (Iter 3): W5 회귀 테스트 + jajang fixtures.

**Exception**: —

---

## `HARNESS-CHG-20260428-13.2` — 2026-04-28 — Phase 2 Iter 2 (W2+W4) 가드 V2 + ralph fallback

**Type**: infra (5 가드 V2 분기 + Layered Defense 보강 + ralph-session-stop fallback)

**Branch**: `harness/guard-realignment-iter2`

**Issue**: #13 — Phase 2 Guard Model Realignment. W2 (5 가드 코드 변경) + W4 (deny 메시지 enrichment + executor round-trip canary) Iter 2 범위.

**범위 요약**: 13.1 에서 정의한 V2 모델을 코드에 반영. `HARNESS_GUARD_V2_*` env unset 시 v1 동작 100% 보존(회귀 0). 5 가드 + ralph-session-stop 3-layer fallback + 4개 헬퍼 + executor canary.

- PR review 후속 fix (LGTM 이전 단계):
  - `hooks/agent-gate.py`: `flag_path` import 누락 추가 — V2 활성 시 `auto_gc_stale_flag()` 호출 직전 NameError 방지 (MUST FIX 1).
  - `hooks/agent-boundary.py` + `hooks/commit-gate.py`: unused `_les` import + dead branch 제거 — V2 분기 정리 과정에서 남은 죽은 코드 (MUST FIX 2).
  - `hooks/skill-stop-protect.py:121`: `clear_active_skill()` try/except 래핑 — `update_live` raise 변경에 따라 예외 전파로 `_log_event` 도달 못 하는 회귀 차단(권고).
- impl 계획 정밀화: `docs/impl/13-guard-realignment.md` 를 architect (module-plan)이 줄번호 + 함수 시그니처 + 의사코드 수준으로 정밀화 (503 → 1099 line). 5번째 위험 실측 케이스 (Cross-guard Silent Dependency Chain) 를 W4 에 `ralph-session-stop` 3-layer fallback (`HARNESS_GUARD_V2_RALPH_FALLBACK`, default off) 으로 영구 fix 명시.

**Exception**: —

---

## `HARNESS-CHG-20260428-13.3` — 2026-04-28 — Phase 2 Iter 3 (W5) 회귀 테스트 + jajang fixtures + smoke-test 시나리오

**Type**: test (`tests/pytest/test_guards.py` 101 케이스 + 4 fixture 디렉토리 + `scripts/smoke-test.sh` 시나리오 10~14)

**Branch**: `harness/guard-realignment-iter3`

**Issue**: #13 — Phase 2 Guard Model Realignment. W5 (회귀 테스트 + jajang fixtures + smoke-test 시나리오) Iter 3 범위. W1+W3 (Iter 1, PR #14) / W2+W4 (Iter 2, PR #15) 후속.

**범위 요약**: Iter 1/2 산출물의 회귀 테스트 자동화. 코드 결함 0건 — test 기술만 정정. 13.1 의 18 요구사항(REQ-001~018) 전수 커버. `HARNESS_GUARD_V2_*` env on/off 양쪽에서 invariant 보존 검증. invariant 변경 없음 → spec §0 룰에 따라 `[invariant-shift]` PR 토큰 미사용.

**[13.3.W5] pytest 회귀 테스트 corpus** — `tests/pytest/test_guards.py` (신규, 101 케이스):
- 가드별 단위 테스트: agent-boundary / commit-gate / agent-gate / skill-gate / skill-stop-protect / issue-gate / plugin-write-guard 7개.
- V2 분기 양면 검증: `HARNESS_GUARD_V2_*` 미설정(v1 폴백) ↔ 설정(V2) 동일 invariant 결과 보장 — staged rollout 회귀 0 입증.
- Layered Defense 분리 검증: blocking layer (deny 결정) ↔ informational layer (stderr/diag log) 분리. silent dependency 가시화 케이스 — `live.json.skill` 쓰기 실패 시 `agent-boundary` 동작 + stderr 경고 동시 발생 확인.
- 18 REQ 전수 매핑: 각 테스트 케이스에 `# REQ-NNN` 주석으로 추적성 확보.
- `tests/pytest/conftest.py` (신규) — fixture 공통 셋업 + tmp working dir + env reset.

**[13.3.W5] jajang monorepo fixtures**:
- `tests/pytest/fixtures/jajang_monorepo/` (신규) — agent-boundary `engineer_scope` 동적 화이트리스트 검증용. 멀티 패키지 구조에서 default 7 패턴 외 추가 경로 허용 입증.
- `tests/pytest/fixtures/llm_marker_variants/` (신규) — parse_marker alias map 회귀 테스트 corpus. PLAN_LGTM / PLAN_OK / PLAN_APPROVE / APPROVE / REJECT 등 LLM 변형 → canonical 흡수 검증.
- `tests/pytest/fixtures/jajang_4categories/` (신규) — 4 카테고리(path hardcode / marker fragility / state persistence stuck / scope strict) 재발 차단 자동화. 13.1 위험 패턴 카탈로그와 1:1.
- `tests/pytest/fixtures/cross_guard_silent_dependency/` (신규 — 5번째 위험 시나리오 A/B):
  - 시나리오 A: `skill-gate.py` `live.json.skill` 쓰기 silent 실패 → `agent-boundary.py` 가 활성 스킬 못 읽음 → false-block + 진단 부재.
  - 시나리오 B: `agent-gate.py` `live.json.agent` 쓰기 실패 → `issue-gate.py`/`commit-gate.py` Gate 1 이 ISSUE_CREATORS 활성도 차단.
  - 두 시나리오 모두 informational layer (stderr 경고 + diag log) 가 차단 결정 영향 없이 가시화하는지 검증.

**[13.3.W5] smoke-test.sh 시나리오 10~14 추가**:
- `scripts/smoke-test.sh` 5 시나리오 추가 — monorepo / env unset (V2 미활성 회귀) / LLM 변형 / cross-flag (V2 부분 활성) / silent dependency 가시화.
- 기존 57/57 → 70/70 PASS (회귀 0).

**[13.3.X] 5번째 위험 production 재발 + 본 회귀 테스트화**:
- 본 ralph-loop이 Iter 2 → Iter 3 transition 에서도 stop-hook 미발동으로 멈춤 — `HARNESS_GUARD_V2_RALPH_FALLBACK` 영구 fix가 default off 이므로 v1 동작 그대로 유지.
- 동일 시나리오를 `cross_guard_silent_dependency/` fixture A/B 로 자동 회귀 테스트화 — 영구 fix env on 시 fallback 동작 + off 시 v1 동작 양면 검증.

**검증** (Iter 3 = test-only):
- `python3 -m pytest tests/pytest/test_guards.py -v` — 101/101 PASS (V2 on/off 양쪽).
- `bash scripts/smoke-test.sh` — 70/70 PASS (시나리오 10~14 신규 포함).
- `python3 -m py_compile harness/*.py hooks/*.py` — OK (Iter 3 코드 변경 없음).
- 코드 결함 0건 — Iter 1/2 구현 정확. test 기술 일부 정정만.

**비변경 (의도)**:
- 가드 코드 (`hooks/*.py`) — Iter 2 에서 완료. Iter 3 는 test-only.
- `harness/*.py` — Iter 1/2 에서 완료. Iter 3 변경 없음.
- spec/architecture/rationale 문서 — Iter 1 에서 완료. invariant 변경 없음.
- `[invariant-shift]` PR 토큰 — spec §0 미사용 기준(test-only, invariant wording/model/scope 변경 없음)에 해당.

**Linked**:
- Issue #13 — Phase 2 Guard Model Realignment 마지막 Iter.
- PR #14 (Iter 1, 13.1) — W1+W3.
- PR #15 (Iter 2, 13.2) — W2+W4.
- `tests/pytest/test_guards.py` — W5 1차 산출물.
- `docs/guard-catalog.md` (13.1) ↔ test 케이스 18 REQ 매핑.
- `docs/impl/13-guard-realignment.md` — W5 작업 분해 완료.

**Exception**: —

---

## `HARNESS-CHG-20260428-14.1` — 2026-04-28 — MARKER_ALIASES 12개 변형 추가

**Type**: infra (LLM 변형 흡수 — defense in depth 2nd layer)

**Branch**: `harness/marker-aliases-expand`

**Issue**: validator 가 PLAN_VALIDATION_PASS 대신 PLAN_VALIDATED / PLAN_PASS 같은 변형, architect (LIGHT_PLAN/MODULE_PLAN) 가 LIGHT_PLAN_READY / READY_FOR_IMPL 대신 LIGHT_PLAN_DONE / PLAN_DONE / MODULE_PLAN_READY 같은 변형 emit 시 `parse_marker` UNKNOWN → SPEC_GAP_ESCALATE / PLAN_VALIDATION_ESCALATE 로 attempt 통째로 무위 소진. 9.1 alias map 의 다음 layer.

**범위 요약**:
- `harness/core.py` `MARKER_ALIASES` 에 12개 variant → canonical 매핑 추가.
  - PLAN_VALIDATION (4): `PLAN_VALIDATED` / `PLAN_VERIFIED` / `PLAN_PASS` → `PLAN_VALIDATION_PASS`, `PLAN_INVALID` → `PLAN_VALIDATION_FAIL`.
  - LIGHT_PLAN_READY (4): `LIGHT_PLAN_DONE` / `LIGHT_PLAN_COMPLETE` / `LIGHT_PLAN_WRITTEN` / `BUGFIX_PLAN_READY`.
  - READY_FOR_IMPL (7): `MODULE_PLAN_READY` / `MODULE_PLAN_DONE` / `IMPL_PLAN_READY` / `IMPL_READY` / `PLAN_DONE` / `PLAN_WRITTEN` / `PLAN_COMPLETE` (LIGHT_PLAN/MODULE_PLAN 두 모드 expected_set 모두에 READY_FOR_IMPL 포함되어 단일 매핑으로 양쪽 커버).

**검증**:
- `python3 -m py_compile harness/core.py` — OK.
- alias smoke test 6/6 신규 변형 정상 매핑 (`PLAN_VALIDATED→PLAN_VALIDATION_PASS`, `LIGHT_PLAN_DONE→LIGHT_PLAN_READY`, `PLAN_DONE→READY_FOR_IMPL`, `MODULE_PLAN_READY→READY_FOR_IMPL`, `PLAN_INVALID→PLAN_VALIDATION_FAIL`, `PLAN_PASS→PLAN_VALIDATION_PASS`).

**비변경 (의도)**:
- agent docs (`agents/validator.md`, `agents/architect/light-plan.md`) — canonical 마커 명세는 1차 방어선으로 유지. alias map 은 fallback.
- LGTM 단독 alias 미추가 (pr-reviewer 정식 마커이기도 해서 충돌).

**Linked**:
- 선행 `HARNESS-CHG-20260428-09.1` — alias map 1차 도입.
- 후속 (이번 6건 묶음): C2 worktree untracked plan / C3 TDD 순서 / C4 pr-reviewer scope / C5 no_changes 분리.

**Exception**: —

---

## `HARNESS-CHG-20260428-14.2` — 2026-04-28 — worktree untracked plan 파일 자동 포함

**Type**: infra (worktree 격리 모드 첫 attempt 회수)

**Branch**: `harness/worktree-include-untracked`

**Issue**: `WorktreeManager.create_or_reuse` 가 `git worktree add` 만 호출 — tracked HEAD 만 가져옴. architect 가 main repo 에 작성한 `docs/bugfix/#NNN.md` / `docs/impl/*.md` 가 미커밋 상태로 worktree 진입 시 누락 → engineer attempt 0 에서 "impl 파일 존재하지 않음" no_changes 로 무위 종료. 매 신규 이슈마다 attempt 0 한 번을 통째로 태움.

**범위 요약**:
- `harness/core.py` `WorktreeManager._copy_untracked_plan_files(wt_path)` 추가 — worktree 진입 직후 main repo `git ls-files --others --exclude-standard` 결과 필터링 후 worktree 같은 상대경로로 `shutil.copy2`.
- 안전 패턴: `docs/bugfix/`, `docs/impl/`, `docs/milestones/` 3개 prefix 만. `src/` 등 코드 영역은 worktree 경계 보호 위해 명시적 제외.
- 복사 건수 stdout 가시화 (`worktree 진입: untracked plan 파일 N개 복사`).

**검증**:
- `python3 -m py_compile harness/core.py` — OK.
- 임시 git repo + untracked `docs/bugfix/#42-test.md` + `docs/impl/99-something.md` + 비-plan `random.md` 시나리오 — bugfix/impl 복사 ✓, random 복사 안 함 ✓, 내용 정확 ✓.

**비변경 (의도)**:
- tracked plan 파일 — 이미 worktree add 가 가져옴. 중복 cp 안 함 (ls-files --others 결과에 없음).
- src/ untracked — worktree 경계 보호. engineer 가 worktree 안에서 직접 작성해야 함.
- 자동 commit — 미커밋 상태로 cp 만. main repo 의 untracked 도 그대로 보존.

**Linked**:
- 선행 `HARNESS-CHG-20260428-14.1` — 같은 묶음의 1번째 fix.
- 후속 (이번 6건 묶음): C3 TDD 순서 / C4 pr-reviewer scope / C5 no_changes 분리.

**Exception**: —

---

## `HARNESS-CHG-20260428-14.3` — 2026-04-28 — TDD 순서 강제 (test_command 의존성 제거)

**Type**: infra (워크플로우 룰 무결성)

**Branch**: `harness/tdd-order-strict`

**Issue**: `impl_loop.py:928` `_tdd_active = (attempt == 0 and bool(config.test_command) and depth in ("std", "deep"))` 조건이 `test_command` 미설정 프로젝트(예: jajang `harness.config.json` `"test_command": ""`)에선 `_tdd_active=False` → 1209 의 옛 폴백(engineer→test-engineer) 분기로 빠짐 → engineer 가 test-engineer 보다 먼저 실행 → TDD 룰("test 먼저, code 뒤") 정반대.

**범위 요약**:
- `harness/impl_loop.py:928` `_tdd_active` 조건에서 `bool(config.test_command) and ` 제거.
  - 결과: `_tdd_active = (attempt == 0 and depth in ("std", "deep"))`. test_command 유무와 무관하게 std/deep attempt 0 이면 test-engineer 선행.
- `harness/impl_loop.py:1209` `elif not config.test_command:` 폴백 블록 (~70 line) 제거.
  - 옛 의도: test_command 가 없으면 TDD 의미가 없다고 판단해 engineer 먼저, test-engineer 나중. 그러나 테스트 작성 자체는 회귀 방어 + impl 명세 검증 목적도 있어 TDD 룰을 끄면 안 됨.
- RED/GREEN 실측 게이트(`if _tdd_test_files and config.test_command:` 974, `if config.test_command:` 1283 부근)는 그대로 유지 — test_command 없으면 실행 게이트만 자연 스킵, 테스트 작성은 항상 함.
- `_tdd_active or (attempt > 0 and depth in ("std", "deep"))` 분기는 `_run_std_deep` 가 항상 std/deep 으로만 호출되므로 결과적으로 항상 True — 단순 로그로 정리.

**검증**:
- `python3 -m py_compile harness/impl_loop.py` — OK.
- AST 점검 — `_tdd_active` 라인 932: `attempt == 0 and depth in ('std', 'deep')` ✓ (test_command 의존 없음).

**비변경 (의도)**:
- simple depth — `run_simple` 가 별도 함수, test-engineer 자체가 스킵 (line 731-735). 변경 없음.
- agent docs `agents/test-engineer.md` — TDD 모드 명세는 그대로. 호출 조건만 정정.

**Linked**:
- 선행 `HARNESS-CHG-20260428-14.1`/`14.2` — 같은 묶음.
- 후속: C4 pr-reviewer scope / C5 no_changes 분리.

**Exception**: —

---

## `HARNESS-CHG-20260428-14.4` — 2026-04-28 — pr-reviewer 에이전트 스코프 매트릭스 인지

**Type**: docs (agent docs 강화 — boundary 사이클 차단)

**Branch**: `harness/pr-reviewer-scope-aware`

**Issue**: pr-reviewer 가 `hooks/agent-boundary.py` `ALLOW_MATRIX` 를 모르고 `docs/bugfix/**`, `package.json`, `docs/impl/**` 등 engineer 스코프 밖 파일에 MUST FIX 발행 → engineer 가 boundary 차단으로 처리 불가 → no_changes → harness retry → 같은 boundary 또 차단 → MAX(3) 소진까지 의미 없는 attempt 가 비용($1.5+) 태움.

**범위 요약**:
- `agents/pr-reviewer.md` 에 "에이전트 스코프 매트릭스 (반드시 인지)" 섹션 추가:
  - engineer 가 수정 가능한 영역 (src/**, apps/<name>/src/, apps/<name>/app/, apps/<name>/alembic/, packages/<name>/src/, *.toml/cfg) 명시.
  - test-engineer 가 수정 가능한 영역 (테스트 파일 한정) 명시.
  - 스코프 밖 파일별 소유 에이전트 매트릭스 (architect/designer/ux-architect/product-planner/사용자 직접/인프라).
  - 규칙 3개: MUST FIX 는 스코프 안만 / 스코프 밖은 NICE TO HAVE + 라우팅 권고 / 인프라는 언급 금지.
  - Why: boundary 사이클로 attempt 비용 폭주 막기 위함.

**검증**:
- agents/pr-reviewer.md grep — "에이전트 스코프 매트릭스" 섹션 존재 ✓.
- `agents/pr-reviewer.md:184` 기존 "인프라 파일 읽기 금지" 룰과 충돌 없음 (보강 관계).

**비변경 (의도)**:
- `hooks/agent-boundary.py` ALLOW_MATRIX — 실제 강제는 그대로. 본 변경은 agent docs 만.
- pr-reviewer 의 MUST FIX/NICE TO HAVE 분류 체크리스트 — 그대로 (A~G). 스코프 매트릭스는 그 위에 적용되는 라우팅 룰.

**Linked**:
- 선행 `HARNESS-CHG-20260428-14.1~14.3` — 같은 묶음.
- 후속: C5 no_changes 별도 fail_type 분리 (boundary 사이클의 회로 단계).

**Exception**: —

---

## `HARNESS-CHG-20260428-14.5` — 2026-04-28 — no_changes 별도 fail_type 분리 + 즉시 escalate

**Type**: infra (retry 비용 회로)

**Branch**: `harness/no-changes-fail-type-split`

**Issue**: `helpers.py:301` 에서 engineer 가 아무 파일도 수정 안 했을 때 `no_changes:` 메시지 emit, impl_loop 양쪽 분기는 모두 `fail_type = "autocheck_fail"` 로 단일 분류. circuit breaker 는 같은 fail_type 2회 누적 후에야 fire 하므로 boundary block 시 attempt 0+1 모두 같은 차단을 반복하다가 attempt 2 시작 시점에서야 escalate. 비용 $1.5+ 무의미 소진.

**범위 요약**:
- `harness/impl_loop.py` `run_simple` autocheck 실패 분기에 `if check_err.startswith("no_changes:"):` 분기 추가 — fail_type = `"no_changes"` 로 분리, 1회만에 즉시 `IMPLEMENTATION_ESCALATE`. record_escalate / write_run_end / Flag.PLAN_VALIDATION_PASSED rm 처리.
- `harness/impl_loop.py` `_run_std_deep` autocheck 실패 분기에 동일 패턴 추가 (run_simple 과 같은 사유).
- 기존 `autocheck_fail` 분기는 그대로 — 다른 autocheck 실패(new_deps / file_unchanged / impl scope guard 등) 는 retry 가능성이 있어 기존 circuit breaker 흐름 유지.

**검증**:
- `python3 -m py_compile harness/impl_loop.py` — OK.
- regex 점검 — `check_err.startswith("no_changes:")` 분기 2회 (run_simple + _run_std_deep), `IMPLEMENTATION_ESCALATE (no_changes)` 출력 2회 ✓.

**비변경 (의도)**:
- `helpers.py` `run_automated_checks` 시그니처 / 반환 — 그대로. 호출 측에서 `check_err` prefix 로 분기.
- circuit breaker 윈도우/임계값 — 그대로. no_changes 만 단일 회로로 분리, 다른 fail_type 은 영향 없음.
- agent-boundary 강제 — 그대로. boundary 자체는 손대지 않고 그 결과(no_changes) 를 빠르게 escalate.

**Linked**:
- 선행 `HARNESS-CHG-20260428-14.1~14.4` — 6건 묶음 마지막.
- 보완 관계: `14.4` (pr-reviewer scope) 가 boundary 충돌 빈도 자체를 줄이고, `14.5` 는 충돌 발생 후 회로 차단.

**Exception**: —

---

> 새 항목은 위 표 + 본 섹션 양쪽에 추가. Phase 2 자동 게이트가 활성화되면 표는 `scripts/check_doc_sync.py` 가 갱신 검증.
