# LOCAL-1 — 추적 ID 백엔드 추상화

| 항목 | 값 |
|---|---|
| Issue ref | `LOCAL-1` (orchestration/issues/INDEX.jsonl#1) |
| Task-ID | `HARNESS-CHG-20260428-01` |
| Branch | `harness/tracker-abstraction` |
| Type | infra (+ spec 갱신은 [1.6]) |
| Invariant flag | `[invariant-shift]` (일반화, 약화 아님) |

---

## 1. 동기

`docs/harness-spec.md §3 I-2` 는 "모든 구현은 하네스 루프 + 추적 ID 강제" 를 명시한다. 그러나 현행 코드는 **추적 ID = GitHub Issue 번호 (`#N`)** 라는 단일 표현에 종속되어 있다:

| 위치 | 의존 | 깨졌을 때 |
|---|---|---|
| `hooks/agent-gate.py:73-79` | `r"#\d+"` 정규식 | architect/engineer 호출 차단 |
| `agents/qa.md` 이슈 생성 | `mcp__github__create_issue` | QA 가 이슈 발급 못 함 |
| `agents/designer.md:84-99` | `gh issue create` Bash 직호출 | 디자인 루프 진입 불가 |
| `harness/executor.py` | `--issue <N>` 인자 | 상태 격리 불가 |

→ 환경 의존(`gh` CLI / GitHub repo / 네트워크) 이 프로세스 강제(추적성) 와 결합돼, 도구 한 점이 빠지면 워크플로우가 정지한다.

본 변경은 **추적성은 보존**하면서 **백엔드 의존을 추상화**한다. 추적 ID는 여전히 강제되지만, 발급 채널은 `github`(gh CLI) / `local`(jsonl) 중 가용한 백엔드를 자동 선택한다.

---

## 2. 산출물

### 신규
- `harness/tracker.py` — Backend Protocol + 두 구현 + auto-select + CLI **(완료, [1.1])**
- `tests/pytest/test_tracker.py` — stdlib unittest 16 케이스 **(완료, [1.1])**
- `orchestration/issues/INDEX.jsonl` — LocalBackend 저장소 (이번 [1.2] 부트스트랩)
- `docs/impl/LOCAL-1-tracker-abstraction.md` — 본 파일 (이번 [1.2])

### 수정
- `hooks/agent-gate.py` — 추적 ID 정규식 확장 ([1.3])
- `agents/designer.md` — Phase 0-0 의 직접 gh 호출 → tracker CLI 위임 ([1.4])
- `agents/qa.md` — MCP 미가용 폴백 안내 ([1.5])
- `docs/harness-spec.md` `§3 I-2` — `#N` → 추적 ID 일반형 ([1.6])
- `docs/harness-architecture.md` — tracker 섹션 추가 ([1.6])
- `orchestration/changelog.md` + `rationale.md` — 본 Task-ID 항목 ([1.2] 초안 / [1.7] 확정)

---

## 3. API 설계

### IssueRef
```python
@dataclass(frozen=True)
class IssueRef:
    backend: str       # "github" | "local"
    number: int
    raw: str           # "#42" | "LOCAL-7"
```

### TrackingBackend (Protocol)
```python
class TrackingBackend(Protocol):
    name: str
    def is_available(self) -> bool: ...
    def create_issue(self, title, body, labels=None, milestone=None) -> IssueRef: ...
    def get_issue(self, ref: IssueRef) -> dict: ...
    def add_comment(self, ref: IssueRef, body: str) -> None: ...
```

### 백엔드 선택
- `HARNESS_TRACKER` env (`github` | `local`) — 강제, 미가용이면 RuntimeError
- 기본값 — `github` 가용하면 github, 아니면 `local` 폴백

### CLI
```
python3 -m harness.tracker create-issue --title T --body B [--label X --milestone N]
python3 -m harness.tracker get <ref>
python3 -m harness.tracker comment <ref> --body B
python3 -m harness.tracker which
```
출력: `create-issue` 는 stdout 에 `#42` 또는 `LOCAL-7` 만 출력 (스크립트 파싱 용이).

### Local 저장 형식 (`orchestration/issues/INDEX.jsonl`)
```json
{"id": 1, "ref": "LOCAL-1", "title": "...", "body": "...",
 "labels": [...], "milestone": null, "state": "open",
 "created": "2026-04-28T...", "updated": "...", "comments": []}
```
append-only. ID 시퀀스는 `.next_id` 파일로 관리 (race 안 — 단일 호출 가정).

---

## 4. Wire-in 전략

### 4.1 agent-gate.py — 정규식 확장 ([1.3])

```python
# Before
if not is_exempt and not re.search(r"#\d+", prompt):
    deny(...)

# After
ISSUE_REF_RE = re.compile(r"(?:#\d+|LOCAL-\d+)")
if not is_exempt and not ISSUE_REF_RE.search(prompt):
    deny(...)
```

같은 패턴 다른 훅에 있는지 grep 확인:
- `hooks/harness-router.py:68-69` — `#NNN` 마커 분류 (IMPLEMENTATION). 동일 패턴 적용.

### 4.2 agents/designer.md — gh CLI → tracker CLI ([1.4])

기존 (Phase 0-0):
```bash
gh issue create --repo {owner}/{repo} --title "..." --label "design-fix" --milestone N --body "..."
```

신규:
```bash
python3 -m harness.tracker create-issue \
  --title "[design] ..." --label "design-fix" --milestone N --body "..."
# stdout: "#42" 또는 "LOCAL-7"
```

`designer_active` 플래그 흐름은 보존 — `commit-gate.py` 가 검사하는 건 `gh` 호출이 아니라 `mcp__github__create_issue`/`mcp__github__update_issue` 이므로 영향 없음. 단, 만약 commit-gate가 `gh issue create` 직접 차단하는 로직이 있다면 [1.4] 진입 시 검토.

### 4.3 agents/qa.md — 폴백 안내 ([1.5])

qa 에이전트는 `tools:` 라인에 `Bash` 미허용 → tracker CLI 직접 호출 불가. 따라서:
- `mcp__github__create_issue` 우선 사용 (기존 그대로)
- 미가용 시: 메인 Claude 가 qa 결과 받아 tracker CLI 로 사후 등록 (메인 호출 경로 추가)
- qa.md 본문에 "MCP 차단 환경이면 출력 마커에 `EXTERNAL_TRACKER_NEEDED` 포함" 안내

### 4.4 spec 문서 갱신 ([1.6])

`docs/harness-spec.md §3 I-2`:
```diff
- 강제 지점: harness/executor.py impl --impl <path> --issue <N>.
+ 강제 지점: harness/executor.py impl --impl <path> --issue <REF>.
+ REF 는 추적 ID 일반형 (#N | LOCAL-N). 백엔드는 `harness/tracker.py` 가 환경에 따라 자동 선택.
```

`§0 Core Invariant` 자체는 변경 없음 — 본 변경은 §3 의 *구현 표현*만 갱신.

`docs/harness-architecture.md` 에 신규 §X "추적 백엔드 (tracker)" 섹션 추가 — 백엔드 선택 트리, LocalBackend 저장 형식, env override.

---

## 5. 의사 결정 기록

| 결정 | 채택 | 기각 |
|---|---|---|
| ID 표현 | `#N` / `LOCAL-N` 분리 표기 | `T-N` 통합 표기 — 기존 코드 호환성 ↓ |
| Local 저장 | jsonl (append-only) | sqlite — stdlib only 원칙 + grep 가능성 |
| race 처리 | 단일 호출 가정, 파일 락 미도입 | flock — 단일 사용자 + 단일 호출 가정에서 과한 복잡성 |
| ID 시퀀스 | `.next_id` 별도 파일 | jsonl 끝에서 max 계산 — 비용 차이 미미하나 명시성 우선 |
| MCP 백엔드 추가 | 보류 | qa/designer 가 이미 MCP 도구를 직접 호출하므로 추상화 불요 — 도구 호출 자체가 추상화 |
| 폴백 자동화 | env + 자동 | 항상 사용자 prompt — 워크플로우 진입 친화성 ↓ |

---

## 6. 검증 계획

| 시나리오 | 기대 |
|---|---|
| `gh` 가용 + repo 연결 | `python3 -m harness.tracker which` → selected: github |
| `gh` 미설치 (모킹) | selected: local 자동 폴백 |
| `HARNESS_TRACKER=local` | github 가용해도 local 강제 |
| `HARNESS_TRACKER=invalid` | ValueError |
| LocalBackend create×3 | LOCAL-1, LOCAL-2, LOCAL-3 시퀀스 |
| agent-gate 프롬프트 `LOCAL-7 처리` | 통과 (이전엔 차단됐을 케이스) |
| agent-gate 프롬프트 `이슈 처리` (ref 없음) | deny (기존 강제 보존) |

[1.1] 시점 16/16 unittest 통과. [1.3] 이후 agent-gate 통합 테스트 추가 ([1.7]에서 정리).

---

## 7. 후속 (이번 Task-ID 외)

- harness/executor.py 의 `--issue` 인자 처리 — 현재 정수 강제일 가능성. `IssueRef` 통과시키도록 개선 (별도 Task-ID 권장)
- HARNESS_ISSUE_NUM env 가 worktree 격리에서 사용됨 — `LOCAL-N` 도 디렉토리 안전한지 확인
- GitHub Actions/CI 환경 — gh 인증 필요 시 LocalBackend 폴백이 더 안정적일 수 있음 (별도 평가)
