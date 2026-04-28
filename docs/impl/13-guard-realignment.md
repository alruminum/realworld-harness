# Impl 계획 — Issue #13 Guard Model Realignment

> Status: SPEC_READY (W1 완료 게이트 통과 후 W2 진입)
> Origin: Phase 2 — `~/.claude/harness-state/.sessions/c86ce041-.../ralph/plan.md`
> Catalog: `docs/guard-catalog.md` (W1 1차 산출물)
> Branch: `harness/guard-realignment-iter1` (Iter 1 = W1+W3) → `harness/guard-realignment-iter2` (Iter 2 = W2+W4) → `harness/guard-realignment-iter3` (Iter 3 = W5)
> PR title: `[invariant-shift] HARNESS-CHG-2026MMDD-NN guard model realignment — <iter>`

---

## 0. 전체 변경 파일 목록 (단계별)

### Iter 1 (W1 + W3)

| 파일 | 작업 | 단계 |
|---|---|---|
| `docs/guard-catalog.md` | **신규** | W1 |
| `docs/impl/13-guard-realignment.md` | **신규** (이 파일) | W1 |
| `docs/harness-spec.md` | §3 I-1, I-2, I-9 표현 갱신 (allowlist→보호 대상 명시), §0 `[invariant-shift]` PR title 토큰 명시 | W3 |
| `docs/harness-architecture.md` | §3 (핸드오프 매트릭스) → catalog reference, §5 (경계 정책) 모델 정책 분기 추가 | W3 |
| `orchestration/rationale.md` | 4섹션 (Context / Decision / Alternatives / Consequences) 추가 — Phase 2 W1 결정 기록 | W3 |

### Iter 2 (W2 + W4)

| 파일 | 작업 | 단계 |
|---|---|---|
| `harness/config.py` | `engineer_scope` 필드 추가 (list[str], default=현 7패턴) | W2 |
| `hooks/agent-boundary.py` | ALLOW_MATRIX["engineer"] 동적 로드 (config.engineer_scope) + default fallback | W2 |
| `hooks/commit-gate.py` | staged 파일 패턴을 `engineer_scope` 에서 파생 + tracker.MUTATING_SUBCOMMANDS 위임 | W2 |
| `hooks/agent-gate.py` | HARNESS_ACTIVE flag age check + auto GC + 추적 ID `tracker.parse_ref()` 위임 | W2 |
| `hooks/skill-gate.py` | live.json 쓰기 실패 stderr 경고 + 진단 집계 | W2 (W4 시너지) |
| `hooks/skill-stop-protect.py` | 진단 로그 포맷 표준화 (다른 가드와 통일) | W2 (W4 시너지) |
| `harness/tracker.py` | `parse_ref()` 노출 + `MUTATING_SUBCOMMANDS` 상수 신설 | W2 |
| `hooks/harness_common.py` | `flag_age_seconds()` 헬퍼 + `auto_gc_stale_flag()` 헬퍼 추가 | W2 |
| `harness/executor.py` | 시작 시 live.json round-trip 테스트 — 실패 시 즉시 ESCALATE | W4 |

### Iter 3 (W5)

| 파일 | 작업 | 단계 |
|---|---|---|
| `tests/pytest/test_guards.py` | **신규** — 7 가드별 보호 대상 unit test | W5 |
| `tests/pytest/fixtures/jajang_monorepo/` | **신규** — apps/api, apps/web 모노레포 fixture | W5 |
| `tests/pytest/fixtures/llm_marker_variants/` | **신규** — 마커 변형 corpus | W5 |
| `scripts/smoke-test.sh` | §10 시나리오 추가 (monorepo / env 미설정 / LLM 변형 3건) | W5 |
| `orchestration/changelog.md` | `HARNESS-CHG-2026MMDD-13.[1-5]` 항목 일괄 추가 | 각 단계 종료 시 |

**제외 가드 (W1 게이트 결정)**: `hooks/issue-gate.py`, `hooks/plugin-write-guard.py` — 모델 변경 없음. W4 진단 가시성 표준만 자동 흡수.

---

## 1. 인터페이스 변경 명세 (가드별)

### 1.1 `agent-boundary.py`

**function signature 변경**: 없음 (내부 구현만).

**새 동작**:
```python
def _load_engineer_scope() -> list[str]:
    """harness.config.json 에서 engineer_scope 로드. 누락 시 default 7 패턴.
    HARNESS_GUARD_V2_AGENT_BOUNDARY 미설정 시 정적 ALLOW_MATRIX 유지 (회귀 방어).
    """
    if os.environ.get("HARNESS_GUARD_V2_AGENT_BOUNDARY") != "1":
        return _STATIC_ENGINEER_SCOPE  # 현재 ALLOW_MATRIX["engineer"]
    try:
        from harness.config import load_config
        cfg = load_config()
        return cfg.engineer_scope or _STATIC_ENGINEER_SCOPE
    except Exception as e:
        sys.stderr.write(f"[agent-boundary] WARN: engineer_scope load failed ({e}), fallback to static\n")
        return _STATIC_ENGINEER_SCOPE
```

**HARNESS_INFRA_PATTERNS / READ_DENY_MATRIX**: **변경 없음** — 보안 가드 (allowlist 유지).

**deny 메시지 enrichment** (W4):
```
❌ [hooks/agent-boundary.py] engineer는 services/api/foo.ts 수정 불가.
허용 경로: ^src/, ^apps/.../src/, ...
진단: live.json 쓰기 상태 OK | engineer_scope source: harness.config.json (V2)
```

---

### 1.2 `commit-gate.py`

**function signature 변경**: 없음.

**Gate 1 (tracker mutate)**:
```python
# 현재: regex 다발
# 변경: tracker 모듈에서 위임
from harness.tracker import MUTATING_SUBCOMMANDS  # 신설 ("create-issue", "comment", ...)
_IS_GH_ISSUE_MUTATE = (
    re.search(r"gh\s+issue\s+(create|edit)", cmd)
    or re.search(r"gh\s+api\s+.*issues.*--method\s+POST", cmd)
    or re.search(r"gh\s+api\s+.*issues.*-X\s+(POST|PATCH)", cmd)
    or _matches_tracker_mutate(cmd)  # MUTATING_SUBCOMMANDS 동적 매치
)
```

**Gate 5 (staged src LGTM)**:
```python
# 현재: re.search(r"^src/", staged, re.MULTILINE)
# 변경: engineer_scope 동적
def _has_engineer_change(staged: str) -> bool:
    if os.environ.get("HARNESS_GUARD_V2_COMMIT_GATE") != "1":
        return bool(re.search(r"^src/", staged, re.MULTILINE))
    patterns = _load_engineer_scope()  # agent-boundary 와 공유
    if not patterns:
        sys.stderr.write("[commit-gate] WARN: engineer_scope empty, fallback to ^src/\n")
        return bool(re.search(r"^src/", staged, re.MULTILINE))
    combined = "(" + "|".join(patterns) + ")"
    return bool(re.search(combined, staged, re.MULTILINE))
```

**`_load_engineer_scope`**: agent-boundary 와 동일 헬퍼 → `harness_common.py` 로 이전.

---

### 1.3 `agent-gate.py`

**HARNESS_ACTIVE flag age check 신규**:
```python
def _is_active_flag_fresh() -> bool:
    """HARNESS_ACTIVE flag mtime + TTL > now → fresh.
    skill-stop-protect.py 의 started_at + ttl_sec 패턴 일반화.
    """
    if os.environ.get("HARNESS_GUARD_V2_AGENT_GATE") != "1":
        return flag(FLAGS.HARNESS_ACTIVE)  # 현행
    flag_p = flag_path(PREFIX, FLAGS.HARNESS_ACTIVE)
    if not flag_p.exists():
        return False
    age = time.time() - flag_p.stat().st_mtime
    ttl = int(os.environ.get("HARNESS_GUARD_V2_FLAG_TTL_SEC", "21600"))  # 6h default
    if age > ttl:
        try:
            flag_p.unlink()
            sys.stderr.write(f"[agent-gate] auto-GC stale HARNESS_ACTIVE flag (age={int(age)}s > ttl={ttl}s)\n")
        except OSError:
            pass
        return False
    return True
```

**추적 ID 검증을 tracker.parse_ref 위임**:
```python
# 현재: re.search(r"#\d+|LOCAL-\d+", prompt)
# 변경:
from harness.tracker import parse_ref  # 신설 (또는 export)
def _has_tracking_id(prompt: str) -> bool:
    if os.environ.get("HARNESS_GUARD_V2_AGENT_GATE") != "1":
        return bool(re.search(r"#\d+|LOCAL-\d+", prompt))
    try:
        return parse_ref(prompt) is not None
    except Exception:
        return bool(re.search(r"#\d+|LOCAL-\d+", prompt))  # 폴백
```

**heartbeat (executor 측)**:
- `harness/executor.py` 가 매 attempt 종료 시 `flag_p.touch()` 로 mtime 갱신 → 장시간 engineer 실행 도중 false-GC 방지.

---

### 1.4 `skill-gate.py`

**기록 실패 진단 추가**:
```python
try:
    ss.set_active_skill(sid, name, level)
except Exception as e:
    if os.environ.get("HARNESS_GUARD_V2_SKILL_GATE") == "1":
        sys.stderr.write(f"[skill-gate] WARN: set_active_skill failed: {e}\n")
        _log_diag({"event": "set_skill_fail", "sid": sid, "skill": name, "err": str(e)})
    # 차단은 하지 않음 (passive recorder 유지)
```

**`_log_diag` 헬퍼**: `harness-state/.logs/skill-gate.jsonl` 에 success/fail 집계.

---

### 1.5 `skill-stop-protect.py`

**변경 최소** — 진단 로그 포맷 표준화:
- 기존 `_log_event` 의 dict 키를 다른 가드와 통일 (`ts`, `event`, `sid`, `guard`, `result`).
- `_log_event({"guard": "skill-stop-protect", ...})` 표준화.

**SELF_MANAGED_LIFECYCLE 모델은 reference**:
- agent-gate 의 stale flag GC, agent-boundary 의 stale live.json.agent GC 가 같은 패턴 사용 — qa 결정 E.
- 코드 공유는 `harness_common.py` 의 `auto_gc_stale_flag(path, ttl, label)` 헬퍼로 1회 중복 제거.

---

### 1.6 `issue-gate.py`, `plugin-write-guard.py` — 변경 없음

W4 진단 가시성 표준만 자동 흡수 (deny 메시지에 진단 정보 추가). 모델 변경 없음.

---

### 1.7 신규 config 키 — `harness.config.json`

```json
{
  "engineer_scope": [
    "(^|/)src/",
    "(^|/)apps/[^/]+/src/",
    "(^|/)apps/[^/]+/app/",
    "(^|/)apps/[^/]+/alembic/",
    "(^|/)packages/[^/]+/src/",
    "(^|/)apps/[^/]+/[^/]+\\.toml$",
    "(^|/)apps/[^/]+/[^/]+\\.cfg$"
  ]
}
```

**default 동작**: 키 누락 시 위 7 패턴 (현 정적 매트릭스 그대로). 회귀 0.

**검증**: `harness/config.py` 의 `HarnessConfig.engineer_scope` 필드 추가 + 단위 테스트 (None / [] / 사용자 override).

---

### 1.8 신규 헬퍼 — `harness/tracker.py`

```python
# 신설 export
MUTATING_SUBCOMMANDS = frozenset({"create-issue", "comment", "create-comment"})

def parse_ref(text: str) -> Optional[IssueRef]:
    """텍스트에서 추적 ID 추출. 백엔드 무관 (#N, LOCAL-N).
    agent-gate, harness-router 가 단일 구현 위임.
    """
    # 기존 normalize_issue_num + format_ref 합성
    ...
```

기존 `parse_ref` 가 이미 일부 코드에 있으면 재export, 없으면 신설.

---

## 2. 핵심 로직 의사코드

### 2.1 ALLOW_MATRIX 동적 로딩 (agent-boundary)

```python
# 모듈 로드 시 1회만 (per-process cache)
_ENGINEER_SCOPE = None

def _engineer_scope() -> list[str]:
    global _ENGINEER_SCOPE
    if _ENGINEER_SCOPE is not None:
        return _ENGINEER_SCOPE
    if os.environ.get("HARNESS_GUARD_V2_AGENT_BOUNDARY") != "1":
        _ENGINEER_SCOPE = _STATIC_ENGINEER_SCOPE
        return _ENGINEER_SCOPE
    try:
        from harness.config import load_config
        cfg = load_config()
        scope = cfg.engineer_scope or _STATIC_ENGINEER_SCOPE
    except Exception as e:
        sys.stderr.write(f"[agent-boundary] WARN: config load failed ({e}); fallback static\n")
        scope = _STATIC_ENGINEER_SCOPE
    _ENGINEER_SCOPE = scope
    return _ENGINEER_SCOPE

# main() 안에서:
ALLOW_MATRIX = dict(_STATIC_ALLOW_MATRIX)  # 다른 키는 정적 유지
ALLOW_MATRIX["engineer"] = _engineer_scope()
```

### 2.2 Flag age check + GC (agent-gate / 일반화 헬퍼)

```python
# harness_common.py 신설
def auto_gc_stale_flag(flag_p: Path, ttl_sec: int, label: str) -> bool:
    """flag mtime 기준 age > ttl 이면 unlink + 진단. 반환: fresh 여부.
    skill-stop-protect 의 auto_release 패턴 일반화.
    """
    if not flag_p.exists():
        return False
    try:
        age = time.time() - flag_p.stat().st_mtime
    except OSError:
        return False
    if age > ttl_sec:
        try:
            flag_p.unlink()
            sys.stderr.write(f"[{label}] auto-GC stale flag (age={int(age)}s > ttl={ttl_sec}s)\n")
            _log_event({"guard": label, "event": "auto_gc", "age": int(age), "ttl": ttl_sec})
        except OSError:
            pass
        return False
    return True
```

agent-gate.py 호출:
```python
HARNESS_ACTIVE_TTL = int(os.environ.get("HARNESS_GUARD_V2_FLAG_TTL_SEC", "21600"))
fresh = auto_gc_stale_flag(flag_path(PREFIX, FLAGS.HARNESS_ACTIVE), HARNESS_ACTIVE_TTL, "agent-gate")
```

### 2.3 Layered defense 전파 (W4)

**원칙 (defense-in-depth ↔ determinism 정책)**:
- **차단 결정 = 결정론** — 1차 검증 (live.json.agent) 만이 deny 권한.
- **fallback layer = informational** — env var, stale flag GC 후 재검사 등은 진단 가시성만 추가, deny 결정은 재변경하지 않음.

```python
def resolve_active_agent(stdin_data) -> Optional[str]:
    """1차: live.json.agent (SSOT — 결정 권한).
    2차: env HARNESS_AGENT_NAME (informational only — 진단 로그에만 비교).
    """
    primary = ss.active_agent(stdin_data=stdin_data)
    fallback = os.environ.get("HARNESS_AGENT_NAME") or None
    if primary is None and fallback:
        sys.stderr.write(
            f"[agent-boundary] WARN: live.json.agent missing but HARNESS_AGENT_NAME={fallback} "
            "(informational — not used for decisions; check skill-gate/agent-gate write health)\n"
        )
    elif primary and fallback and primary != fallback:
        sys.stderr.write(
            f"[agent-boundary] WARN: SSOT mismatch live.json={primary} env={fallback} "
            "(informational — using SSOT)\n"
        )
    return primary
```

### 2.4 Executor live.json round-trip 테스트 (W4)

```python
# harness/executor.py 진입부
def _verify_live_json_writable(session_id: str) -> None:
    """live.json 쓰기 가능 여부 사전 검증. 실패 시 즉시 ESCALATE.
    silent dependency cascade (5번째 위험) 사전 차단.
    """
    try:
        ss.update_live(session_id, _harness_canary=int(time.time()))
        ss.clear_live_field(session_id, "_harness_canary")
    except Exception as e:
        emit_marker("ESCALATE", reason=f"live.json write failed: {e}; downstream guards will silent-cascade")
        sys.exit(1)
```

---

## 3. 결정 근거 (qa 권장안 A~E 반영)

| qa 결정 | 본 계획 반영 위치 | 검토한 대안 | 채택 이유 |
|---|---|---|---|
| **A**: agent-boundary engineer scope 동적화, Read 경계 allowlist 유지 | §1.1 + §1.7 | (1) 전체 ALLOW_MATRIX 동적화 (2) blocklist 전환 | (1) 거부 — designer/architect 등 다른 키도 동적화하면 보안 가드 약화. engineer 키만 monorepo 동기. (2) 거부 — blocklist 는 신규 위협 발생 시 기본 통과 (false-pass) → src 보호 약화. |
| **B**: agent-gate flag age check + 추적 ID tracker.parse_ref 위임 | §1.3 + §2.2 | (1) flag 청소를 SessionEnd 훅에서만 (2) tracker regex 확장 | (1) 거부 — SessionEnd 가 누락되면 (외부 종료) 잔존. age check 는 self-healing. (2) 거부 — 백엔드 추가마다 정규식 분기 → drift. tracker 단일 책임이 정답. |
| **C**: commit-gate staged 패턴이 ALLOW_MATRIX 와 같은 소스 | §1.2 + §1.7 | (1) commit-gate 가 직접 agent-boundary import (2) 두 가드가 각자 config 로드 | (1) 거부 — 훅 간 import 의존 = 로드 순서 결합. (2) 채택 — 각자 config 로드, 같은 source key 공유 (SSOT in config, not in code). |
| **D**: silent dependency 진단 가시성 (live.json 쓰기 실패 stderr 표준화) | §1.4 + §2.3 + §2.4 | (1) deny 결정 변경 (silent 시 fallback to env) (2) 진단만 | (1) 거부 — 차단 결정 비결정론 → spec §0 워크플로우 강제 위반. (2) 채택 — fallback 은 informational, 차단은 1차 단독. |
| **E**: skill-stop-protect 의 auto_release/TTL 패턴을 stale flag/live.json.agent 에 일반화 | §1.5 + §2.2 (`auto_gc_stale_flag` 헬퍼) | (1) 가드별 자체 GC 로직 (2) 외부 cleanup 데몬 | (1) 거부 — 코드 중복 + drift. (2) 거부 — 데몬 의존 = install 복잡성 증가. 헬퍼 1개로 단일화. |

---

## 4. 주의사항 — 다른 모듈과의 경계 / 회귀 위험

### 4.1 ALLOW_MATRIX default fallback 누락 — engineer 전 차단 위험

**시나리오**: `harness.config.json` 신규 사용자가 `engineer_scope: []` 으로 설정 (의도치 않은 빈 리스트).

**방어**:
```python
scope = cfg.engineer_scope or _STATIC_ENGINEER_SCOPE  # falsy → static
if not scope:
    sys.stderr.write("[agent-boundary] WARN: engineer_scope empty; fallback static\n")
    scope = _STATIC_ENGINEER_SCOPE
```

테스트: `tests/pytest/test_guards.py` 에 `test_engineer_scope_empty_falls_back_to_static`.

### 4.2 commit-gate Gate 5 regex 컴파일 실패 → silent-bypass 위험

**시나리오**: 사용자 config 의 `engineer_scope` regex 가 invalid (e.g. unbalanced paren).

**방어**:
```python
try:
    combined_re = re.compile("(" + "|".join(patterns) + ")", re.MULTILINE)
except re.error as e:
    sys.stderr.write(f"[commit-gate] WARN: engineer_scope regex invalid ({e}); fallback ^src/\n")
    combined_re = re.compile(r"^src/", re.MULTILINE)
```

**중요**: except 에서 `pass` 만 하면 silent-bypass — 명시적 fallback 필수.

### 4.3 flag GC TTL 너무 짧음 → 장시간 engineer 중도 차단

**시나리오**: 8시간 짜리 대규모 마이그레이션 → 6h TTL 도달 → flag GC → 다음 attempt agent-gate 통과 못 함.

**방어**:
- default TTL = 6h (보수적).
- `harness/executor.py` 가 매 attempt 종료 시 flag mtime touch (heartbeat).
- 사용자 override: `HARNESS_GUARD_V2_FLAG_TTL_SEC=43200` (12h 등).

### 4.4 tracker.parse_ref 변경이 다른 호출처 회귀

**시나리오**: harness-router.py, core.py 등이 이미 `re.search(r"#\d+|LOCAL-\d+", ...)` 사용 중.

**방어**:
- `parse_ref` 는 신규 노출이지 기존 호출 변경 아님.
- 본 계획 W2 에서는 agent-gate.py 한 곳만 위임 — 다른 호출처는 별 issue 로 점진 마이그레이션.

### 4.5 staged rollout flag 누락 → 실수로 V2 동작 활성화

**시나리오**: 개발 중 환경변수 export 후 unset 누락.

**방어**:
- 테스트 환경 격리 (`subprocess.run(env={"HARNESS_GUARD_V2_*": ""})`).
- smoke-test.sh 가 V2 on/off 양쪽 시나리오 검증.

### 4.6 W3 spec 변경 누락 → 코드/spec drift

**시나리오**: W2 코드 변경했는데 W3 spec §3 I-1 표현 갱신 안 함.

**방어**:
- Iter 1 = W1+W3 (코드 전 spec 먼저). Iter 2 = W2+W4 (spec 정렬 확인 후 코드).
- `[invariant-shift]` PR title 토큰 — spec 변경 동반 필수 신호 (§0 룰).
- `scripts/check_doc_sync.py` 가 catalog reference 누락 검출.

---

## 5. Staged Rollout 계획

### 5.1 Feature Flag 일람 (7개)

| 환경변수 | 가드 | 활성 시 동작 |
|---|---|---|
| `HARNESS_GUARD_V2_AGENT_BOUNDARY=1` | `agent-boundary.py` | ALLOW_MATRIX["engineer"] 동적 로드 (config) + deny 메시지 진단 enrichment |
| `HARNESS_GUARD_V2_COMMIT_GATE=1` | `commit-gate.py` | staged 패턴 동적 + tracker.MUTATING_SUBCOMMANDS 위임 |
| `HARNESS_GUARD_V2_AGENT_GATE=1` | `agent-gate.py` | HARNESS_ACTIVE flag age check + tracker.parse_ref 위임 |
| `HARNESS_GUARD_V2_SKILL_GATE=1` | `skill-gate.py` | 쓰기 실패 stderr 경고 + 진단 집계 |
| `HARNESS_GUARD_V2_SKILL_STOP_PROTECT=1` | `skill-stop-protect.py` | 진단 로그 포맷 표준화 |
| `HARNESS_GUARD_V2_ISSUE_GATE=1` | `issue-gate.py` | (W4 한정) deny 메시지 진단 enrichment 만 |
| `HARNESS_GUARD_V2_PLUGIN_WRITE_GUARD=1` | `plugin-write-guard.py` | (W4 한정) deny 메시지 진단 enrichment 만 |

### 5.2 보조 환경변수

| 환경변수 | 기본값 | 설명 |
|---|---|---|
| `HARNESS_GUARD_V2_FLAG_TTL_SEC` | `21600` (6h) | HARNESS_ACTIVE flag age check TTL |
| `HARNESS_GUARD_V2_DIAG_LOG_DIR` | `harness-state/.logs/` | 진단 로그 디렉토리 |
| `HARNESS_GUARD_V2_ALL=1` | (off) | 7개 가드 V2 일괄 활성 (개발 편의) |

### 5.3 Rollout 단계

**Stage 0** (Iter 2 merge 직후): 모든 V2 flag off — 회귀 0 확인.

**Stage 1** (jajang 재실측): `HARNESS_GUARD_V2_AGENT_BOUNDARY=1` + `HARNESS_GUARD_V2_COMMIT_GATE=1` 만 on. 모노레포 시나리오 통과 확인.

**Stage 2** (1주 후): `HARNESS_GUARD_V2_AGENT_GATE=1` 추가. stale flag 시나리오 통과 확인.

**Stage 3** (2주 후): `HARNESS_GUARD_V2_SKILL_GATE=1` + `HARNESS_GUARD_V2_SKILL_STOP_PROTECT=1` 추가. 진단 가시성 활성.

**Stage 4** (배포): `HARNESS_GUARD_V2_ALL=1` default — setup-rwh.sh 가 자동 export.

각 stage 마다 `orchestration/changelog.md` 에 `HARNESS-CHG-2026MMDD-13.X` 추가.

---

## 6. W1 게이트 결정 (재차 명시)

본 계획의 **W2 코드 변경 범위**:

- **포함**: `agent-boundary.py`, `commit-gate.py`, `agent-gate.py`, `skill-gate.py`, `skill-stop-protect.py` (5개)
- **제외**: `issue-gate.py`, `plugin-write-guard.py` (2개) — W4 진단 가시성만 흡수

근거: catalog §0 표 + qa 권장안.

---

## 7. PR Title / Branch 전략

- Iter 1 PR (W1+W3): `[invariant-shift] HARNESS-CHG-2026MMDD-13.1 guard catalog + spec realignment` — branch `harness/guard-realignment-iter1`
- Iter 2 PR (W2+W4): `[invariant-shift] HARNESS-CHG-2026MMDD-13.2 guard model redesign (5 guards) + layered defense` — branch `harness/guard-realignment-iter2`
- Iter 3 PR (W5): `[invariant-shift] HARNESS-CHG-2026MMDD-13.3 guard regression tests + jajang fixtures` — branch `harness/guard-realignment-iter3`

`[invariant-shift]` 토큰: spec §3 invariant 표현 변경 동반 PR 의 정식 마커. spec §0 에 룰 명시 (W3).

---

## 8. 다음 단계 안내

1. **W1 (이 단계 완료)** — catalog + 본 impl 계획 작성.
2. **W3 (다음 architect 호출)** — `docs/harness-spec.md` §3 + `docs/harness-architecture.md` §3/§5 + `orchestration/rationale.md` 4섹션 갱신. **본 메시지에서는 미작성** (별도 회차).
3. **W2 (engineer 호출)** — Iter 2 코드 변경 (5개 가드).
4. **W4 (engineer 호출)** — executor.py round-trip + deny 메시지 enrichment.
5. **W5 (test-engineer 호출)** — 회귀 검증 + jajang fixture.

---

## 9. Acceptance Criteria (impl 계획 자체 게이트)

- [x] 7 가드 모두 catalog 에 1페이지 + 표 등재
- [x] qa 권장안 A~E 5개 모두 본 impl 계획에 반영 (§3 표)
- [x] staged rollout `HARNESS_GUARD_V2_*` 7개 가드 환경변수 + 2개 보조 + 1개 ALL 명세
- [x] W1 게이트 결정 (issue-gate / plugin-write-guard 제외) 명시 (§0 + §6)
- [x] PR title `[invariant-shift]` 토큰 사용 명시 (§7)
- [x] branch 네이밍 (`harness/guard-realignment-iter{1,2,3}`) 명시 (§7)
- [x] Cross-guard silent dependency chain (5번째 위험) 별도 처리 (catalog §3 + 본 §1.4 / §2.3 / §2.4)
- [x] 회귀 위험 6항목 분석 (§4)
