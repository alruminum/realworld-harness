---
issue: 32
type: feature
depth: simple
identifier_candidate: HARNESS-CHG-20260428-27.A2
parent_epic: 30
related: HARNESS-CHG-20260428-14 (commits 14.1~14.5 — tests 0개 회귀 사례)
---

# Impl 계획 — Issue #32 PR-time harness/** ↔ tests/** 동반 게이트 (Stage A2 of epic #30)

> Status: **LIGHT_PLAN_READY** (depth=simple — 기존 `check_doc_sync.py` 패턴 직접 이식, 새 설계 결정 없음)
> Branch (제안): `harness/test-sync-gate`
> PR title (제안): `HARNESS-CHG-20260428-27.A2 PR-time test-sync gate (Tests-Exception 패턴)`

## 변경 대상

| 파일 | 작업 | 비고 |
|---|---|---|
| `scripts/check_test_sync.py` | **신규** | `check_doc_sync.py` 와 동일 골격, 트리거 경로/예외 마커만 교체 |
| `.github/workflows/test-sync.yml` | **신규** | `doc-sync.yml` 의 거의 1:1 복사. 별도 workflow 로 분리 (검증 결정 — §"CI workflow 통합 방식" 참조) |
| `orchestration/policies.md` | **수정** | §8 `test-sync` 섹션 신규 (§2~3 Document-Exception 와 평행 구조) |
| `tests/pytest/test_check_test_sync.py` | **신규** | REQ-001~REQ-005 5케이스 + 마커 사유 길이 검증 |

## 배경 (요약)

- 최근 [14.1]~[14.5] 5개 연속 commit 이 `tests/**` 변경 0개. commit msg 의 "검증: 임시 git repo 시나리오" 는 **manual smoke** 이며 영구 회귀 가드 아님.
- [14.2] reuse hole (issue #26) 이 정확히 이 sticky 회귀 카테고리에서 발현: [14.1] 이 fresh path 만 추가하고 reuse path 를 빠뜨린 hole 을 후속 사람이 발견.
- `scripts/check_doc_sync.py` 는 이미 동작하는 PR-time 분류·게이트 인프라. 동일 골격 + 트리거 경로 교체 + 예외 마커 이름 변경만으로 본 게이트 성립.

## 수정 내용

### 1. `scripts/check_test_sync.py` 신규 — 인터페이스 명세

**시그니처 / 사용법** (check_doc_sync.py:8-18 와 동일 패턴):

```bash
# 로컬 (staged):
python3 scripts/check_test_sync.py
# CI (base..head):
python3 scripts/check_test_sync.py <base_sha> <head_sha>
```

**종료 코드**:
- `0` — PASS (트리거 변경 없음 / tests 동반 / Tests-Exception 유효)
- `1` — FAIL (harness/** or hooks/** 변경 + tests/** 변경 0 + Tests-Exception 없음)
- `2` — ERROR (git 호출 실패 등 — `check_doc_sync.py:94` 패턴 동일)

**트리거 정규식**:

```python
# orchestration/policies.md §8 정의의 코드 표현
TRIGGER_PATTERNS = [
    re.compile(r"^harness/"),
    re.compile(r"^hooks/"),
]

TEST_PATH_PATTERNS = [
    re.compile(r"^tests/"),
]
```

**비트리거 경로 (게이트 미적용)** — 이슈 본문 §3, REQ-004 와 일치:
- `docs/**`, `agents/**`, `scripts/**` 자체, `.github/**`, `templates/**`, `README.md`, `orchestration/**`, `prd.md`, `trd.md` — 어느 하나만 변경되어도 본 게이트는 PASS 반환 (다른 게이트 영역).
- 단, harness/** 또는 hooks/** 변경이 **하나라도** 있으면 게이트 트리거.

**예외 마커 정규식** (Document-Exception 와 형식 통일):

```python
EXCEPTION_PATTERN = re.compile(r"Tests-Exception:\s*(.+)")
MIN_REASON_LEN = 10
```

마커 검색 소스 (check_doc_sync.py:194-196 와 동일):
1. 현재 diff 의 추가 라인 (`+` 시작, `+++` 헤더 제외)
2. `.git/COMMIT_EDITMSG` (pre-commit / 로컬 컨텍스트)

> **재사용 hole 차단**: 과거 commit body 에 있던 `Tests-Exception:` 라인은 무효 — diff 추가 라인 또는 현재 commit msg 에만 있어야 함 (check_doc_sync.py:46-47 §3 룰 동일 적용).

**main() 흐름** (check_doc_sync.py:164-216 와 동일 골격):

```
1. base/head argv 파싱
2. get_changed_files() → 변경 파일 목록
3. 빈 목록이면 skip → return 0
4. 트리거 분류:
   - has_trigger = 변경 파일 중 TRIGGER_PATTERNS 매칭 ≥ 1
   - has_tests   = 변경 파일 중 TEST_PATH_PATTERNS 매칭 ≥ 1
5. has_trigger == False                       → return 0 ("게이트 대상 아님")
6. has_trigger and has_tests                  → return 0 ("동반 충족")
7. has_trigger and not has_tests:
   - find_tests_exception(diff_added, commit_msg) 호출
   - found=True 이고 사유 ≥ 10자                → return 0
   - 그 외                                    → return 1 (FAIL 메시지 + 해결 방법 출력)
```

> **함수 재사용**: `get_changed_files`, `get_diff_added_lines`, `get_commit_message_subject_and_body` 3개는 check_doc_sync.py 와 시그니처/동작 동일 — 파일 단위 직접 복제 (import 의존 신설 회피, 두 게이트는 독립 진화 가능). 본 의사결정은 epic #30 Stage A2 비목표 ("두 게이트 통합") 와 정합.

**Failure 메시지 (예시)**:

```
[check_test_sync] ✗ FAIL — harness/hooks 변경에 tests/** 동반 누락
  변경 트리거 파일:
    [trigger] harness/executor.py
    [trigger] hooks/agent-boundary.py

해결 방법:
  1. tests/pytest/ 또는 tests/** 아래 회귀 테스트 추가 후 같은 PR 에 포함
  2. 또는 commit msg / PR body 에 'Tests-Exception: <10자 이상 사유>' 명시
       (예: 'Tests-Exception: docstring-only refactor — 행동 불변')

룰: orchestration/policies.md §8
```

### 2. `.github/workflows/test-sync.yml` 신규

**검증된 결정: 별도 workflow 로 분리** (doc-sync.yml 와 합치지 않음).

근거:
- 두 게이트는 트리거 경로 / 예외 마커 / 실패 시 가이드 문구가 모두 다르다. 합치면 한 workflow 안에 두 step 이 생기고 step 하나 실패 시 다른 step PASS 결과가 PR check UI 에서 한 줄로 묶여 가독성↓.
- doc-sync.yml 는 이미 PR `pull_request` 트리거 + base/head sha 전달 패턴을 확립. 동일 yml 1:1 복사 + step 이름·스크립트 경로만 교체하는 비용 < 통합 비용.
- 향후 한쪽 게이트만 disable 해야 할 운영 상황 (예: 인프라 hotfix) 에 workflow 단위 토글 가능.

**파일 내용 (요지)** — doc-sync.yml 와 9-38 라인 동일 골격, 차이는 다음 4지점:

| 라인 | doc-sync.yml | test-sync.yml |
|---|---|---|
| 1 | `name: Document Sync Gate` | `name: Test Sync Gate` |
| 19 | `doc-sync:` (job id) | `test-sync:` |
| 20 | `name: check_doc_sync.py base..head` | `name: check_test_sync.py base..head` |
| 36 | `python3 scripts/check_doc_sync.py ...` | `python3 scripts/check_test_sync.py ...` |

env (FORCE_JAVASCRIPT_ACTIONS_TO_NODE24), checkout fetch-depth=0, setup-python 3.11 모두 동일.

### 3. `orchestration/policies.md` §8 신규 섹션

**위치**: 현재 §7 ("본 문서 갱신 룰") **앞**에 §8 추가하지 않고, **§7 앞에 §8 삽입 후 기존 §7 → §9 로 번호 이동**. (§7 은 메타 문서 갱신 룰이라 마지막에 배치 유지)

> 위 결정 이유: §2~3 (Change-Type / Document-Exception) → §6 (자동 게이트 §6.1~6.3) → §7~ 메타 순서 유지가 자연. 신규 §8 은 §6 의 *동일 패턴* 두 번째 사례라 §6 직후 (§7 → §9 재번호) 또는 §6 안 §6.4 로 가능. 검토 후 **§8 신규 + 기존 §7 을 §9 로 이동** 채택 (자동 게이트 두 종류를 §6 / §8 로 병렬 배치하면 §3 Document-Exception 과 §8 Tests-Exception 도 평행 — 학습성↑).

**§8 본문 (계획)**:

```markdown
## 8. test-sync 게이트 (PR-time)

> 같은 패턴: §3 Document-Exception (`scripts/check_doc_sync.py`) 와 골격 공유. 본 §8 은 코드 변경에 대한 회귀 테스트 동반 강제만 다룬다.

### 8.1 트리거 경로

| 토큰 | 감시 경로 | 동반 필수 |
|---|---|---|
| `code` | `harness/`, `hooks/` | `tests/**` 아래 1개 이상 변경 |

비트리거: `docs/`, `agents/`, `scripts/` 자체, `.github/`, `prd.md`, `trd.md`, `templates/`, `orchestration/` — 본 게이트 미적용 (§2~3 doc-sync 게이트는 별도).

### 8.2 Tests-Exception 스코핑

동반 테스트 추가가 어려운 경우 (docstring/comment-only refactor, mass-rename 등) 커밋 메시지 또는 PR 본문에 명시:

\`\`\`
Tests-Exception: <10자 이상 사유>
\`\`\`

판정 룰 (§3 Document-Exception 와 동일):
- 유효: 현재 diff 의 *추가 라인* 또는 현재 commit msg 에 마커 + 사유 ≥ 10자
- 무효: 과거 commit / 과거 changelog 엔트리 재사용 불가
- 사유 길이: 최소 10자 (단순 "skip" 거부)

### 8.3 통합 지점

- CI: GitHub Actions `pull_request` → `scripts/check_test_sync.py $BASE $HEAD` (.github/workflows/test-sync.yml)
- 로컬 (선택): `git commit` 시 pre-commit 훅 — Stage A2 범위 외 (epic #30 후속 단계)

### 8.4 본 게이트가 있었으면 차단됐을 사례

[14.1]~[14.5] 5건 연속 commit. 모두 harness/ or hooks/ 코드 변경 + tests 0 + Tests-Exception 미명시. retroactive 시뮬레이션 결과는 회귀 테스트 보고서에 첨부 (수용 기준 §5 참조).
```

> 위 §8 텍스트 자체는 architect 가 별도로 채울 영역. 본 plan 은 골격·결정만 명시.

### 4. 회귀 테스트 — `tests/pytest/test_check_test_sync.py` 신규

**테스트 패턴**: stdlib `unittest` (test_tracker.py:8-9 컨벤션). pytest 도 자동 인식.

**테스트 격리 방식**: 각 케이스마다 `tempfile.TemporaryDirectory` + `git init` 후 fixture 파일 생성·commit → `subprocess.run(["python3", str(SCRIPT), base, head])` 호출 → exit code + stdout 검증.

**5케이스 명세** (이슈 본문 §회귀 테스트):

| ID | 시나리오 | 변경 파일 | Tests-Exception | 기대 |
|---|---|---|---|---|
| REQ-001 | harness/ 만 변경 + tests 0 | `harness/foo.py` | 없음 | exit 1 + "tests/** 동반 누락" |
| REQ-002 | harness/ + tests 동반 | `harness/foo.py`, `tests/pytest/test_foo.py` | 없음 | exit 0 |
| REQ-003 | hooks/ 만 변경 + tests 0 | `hooks/bar.py` | 없음 | exit 1 |
| REQ-004 | docs/ 만 변경 (코드 X) | `docs/baz.md` | 없음 | exit 0 ("게이트 대상 아님") |
| REQ-005 | Tests-Exception 마커 명시 | `harness/foo.py` | `Tests-Exception: docstring-only refactor` (commit msg 에) | exit 0 |

**REQ-005 보조 케이스** (사유 길이 검증):

- REQ-005a: `Tests-Exception: ok` (사유 2자) → exit 1 + "사유 너무 짧음" 메시지
- REQ-005b: `Tests-Exception: ` (빈 사유) → exit 1
- REQ-005c: 과거 commit body 에 `Tests-Exception: ...` (현재 diff 에는 없음) → exit 1 (재사용 hole 차단)

**fixture 헬퍼** (test_tracker.py 와 동일 컨벤션):

```python
def _init_git_repo(tmp: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp, check=True)
    subprocess.run(["git", "config", "user.email", "test@test"], cwd=tmp, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=tmp, check=True)

def _commit_files(tmp: Path, files: dict[str, str], msg: str) -> str:
    for rel, content in files.items():
        path = tmp / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    subprocess.run(["git", "add", "-A"], cwd=tmp, check=True)
    subprocess.run(["git", "commit", "-q", "-m", msg], cwd=tmp, check=True)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp,
                          capture_output=True, text=True).stdout.strip()
```

스크립트는 `REPO_ROOT = Path(__file__).resolve().parent.parent` 로 자기 위치를 잡으므로, fixture tmp 디렉토리에서 직접 호출하려면 `cwd=tmp` 로 subprocess 실행. (check_doc_sync.py:27 와 동일 패턴 → 호출 디렉토리가 git root 가정).

## 비목표 (이슈 본문 명시)

- [14.x] retroactive 차단 — 본 PR 머지 *이후* commit 부터 적용
- 동반 테스트 "양" 검증 (코드 100라인 / 테스트 1라인) — 본 게이트는 형식만 체크 (≥1개). 품질·커버리지는 pr-reviewer 영역
- pre-commit 훅 통합 — Stage A2 범위 외, epic #30 후속

## 결정 근거 (검토 대안)

### CI workflow 통합 vs 분리 → 분리 선택

| 항목 | 통합 (한 workflow 두 step) | 분리 (별도 workflow) ✓ |
|---|---|---|
| 신규 파일 수 | 0 (기존 doc-sync.yml 수정) | 1 (test-sync.yml 신규) |
| PR check UI 가독성 | 두 게이트 결과가 한 line | 두 줄 (각 게이트 명확) |
| 운영 토글 | step skip 조건 분기 필요 | workflow 단위 disable |
| 의도 분리 | doc-sync.yml 가 두 책임 보유 | 1 workflow 1 책임 |
| 비용 | yml diff 작음 / step name 충돌 | yml 거의 1:1 복사 |

→ 운영 토글 + 가독성 우선, 비용 차이 미미 → **분리**.

### Tests-Exception 마커 이름 → `Tests-Exception:` 채택

- 후보: `Tests-Exception:`, `NoTests:`, `Skip-Tests:`
- `Tests-Exception:` 채택: `Document-Exception:` (§3) 와 형식 통일 → 학습성·grep용이성↑. `NoTests:` / `Skip-Tests:` 는 명령형이라 "왜 skip 하는가" 압박 약함.

### 함수 import vs 코드 복제 → 복제 채택

- check_doc_sync.py 의 `get_changed_files`, `get_diff_added_lines`, `get_commit_message_subject_and_body` 를 module 화하여 import vs 직접 복제.
- 선택: **복제**. 두 스크립트는 독립 진화 가능 (§8 트리거 룰 변경이 §2~3 에 영향 X). 공통 모듈 도입은 게이트 3개 이상으로 늘 때 정당화 — 현 시점 YAGNI.

## 수용 기준

| 요구사항 ID | 내용 | 검증 방법 | 통과 조건 |
|---|---|---|---|
| REQ-001 | `scripts/check_test_sync.py` 작성 + py_compile OK | `python3 -m py_compile scripts/check_test_sync.py` | 종료 코드 0, 경고 0 |
| REQ-002 | CI workflow `test-sync.yml` 추가 + base..head 트리거 동작 | 본 PR 자체에서 GitHub Actions `Test Sync Gate` job 실행 | job conclusion = success (PR 자체엔 tests 포함되므로) |
| REQ-003 | `orchestration/policies.md` §8 `test-sync` 섹션 추가 + 기존 §7 → §9 재번호 | grep `^## 8\. test-sync` policies.md && grep `^## 9\. 본 문서 갱신` policies.md | 두 grep 모두 hit |
| REQ-004 | 회귀 테스트 5/5 PASS (REQ-005 보조 3건 포함 시 8/8) | `python3 -m pytest tests/pytest/test_check_test_sync.py -v` | 모든 케이스 PASS |
| REQ-005 | [14.1]~[14.5] retroactive 시뮬레이션 보고 | 5개 commit sha (585a500, 4eb20b3, fc837e8, c8b1e2a, c9e84fb) 각각에 대해 `python3 scripts/check_test_sync.py <commit~1> <commit>` 실행 결과를 PR body 에 첨부 | 모두 exit 1 (또는 [14.4] 처럼 tests 가 우연히 들어간 케이스 명시적 분류) |

## 자가 체크 (LIGHT_PLAN_READY 4항목)

- [x] 변경 대상 파일·컴포넌트 특정 완료 (4파일: 신규 3 + 수정 1)
- [x] 수정 내용 명시 (시그니처·정규식·main 흐름·CI 통합 결정 근거 모두 본 plan 에 포함)
- [x] 변경 동작을 assert 하는 테스트 파일이 수정 범위에 포함됨 (`tests/pytest/test_check_test_sync.py` 신규 — REQ-001~005 + 보조 3건)
- [x] 수용 기준 섹션 존재 + 태그 (REQ-001~REQ-005)
