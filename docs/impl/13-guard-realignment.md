# Impl 계획 — Issue #13 Guard Model Realignment

> Status: **Iter 2 SPEC_READY** (W1+W3 merged in PR #14. W2+W4 engineer-ready)
> Origin: Phase 2 — `~/.claude/harness-state/.sessions/c86ce041-.../ralph/plan.md`
> Catalog: `docs/guard-catalog.md` (W1 1차 산출물)
> Branch: `harness/guard-realignment-iter1` (Iter 1 = W1+W3, PR #14 merged) → `harness/guard-realignment-iter2` (Iter 2 = W2+W4) → `harness/guard-realignment-iter3` (Iter 3 = W5)
> PR title: `[invariant-shift] HARNESS-CHG-2026MMDD-NN guard model realignment — <iter>`

### Iter 2 정밀화 (2026-04-28) — engineer 호출 직전 통화 가능 수준

§1.x §2.x §4.x §5.x 를 함수 시그니처 + 의사코드 + v1 fallback 분기 위치까지 **engineer 가 추가 결정 없이 코드 작성 가능**한 수준으로 정밀화. `__file__` 줄번호는 본 정밀화 시점(2026-04-28) 기준 — engineer 작업 시 `git log` 로 최신 버전 확인 필수.

**§1.9 + §2.5 + §4.7 + §5.4 신규 추가**: 본 ralph-loop 자체에서 발현된 5번째 위험 실측 케이스 (live.json.skill silent missing → ralph-session-stop placeholder false-pending) 의 영구 fix 를 W4 layered defense 에 신규 항목으로 편입 — 가드는 아니지만 동일 silent dependency cascade 의 보강이라 W4 정합.

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

### Iter 2 (W2 + W4) — 정밀화 후

| 파일 | 작업 | 단계 |
|---|---|---|
| `harness/config.py` | `engineer_scope: list = field(default_factory=list)` 필드 추가 + load_config 매핑 (line 42-117) | W2 |
| `harness/tracker.py` | `MUTATING_SUBCOMMANDS: frozenset` 상수 신설 (`parse_ref` 는 이미 존재 — 재export 불필요) | W2 |
| `hooks/harness_common.py` | `_STATIC_ENGINEER_SCOPE` + `_load_engineer_scope()` + `auto_gc_stale_flag()` + `_verify_live_json_writable()` 4개 헬퍼 신설 | W2+W4 |
| `hooks/agent-boundary.py` | `_load_engineer_scope()` 위임 (line 218 패치) + V2 deny 메시지 enrichment (line 246) | W2+W4 |
| `hooks/commit-gate.py` | `_matches_tracker_mutate()` + `_has_engineer_change()` 헬퍼 + Gate 1 line 50-57 / Gate 5 line 115 패치 + V2 deny enrichment | W2+W4 |
| `hooks/agent-gate.py` | `flag()` 헬퍼 v2 분기 + `_is_active_flag_fresh()` + `_has_tracking_id()` + V2 deny enrichment | W2+W4 |
| `hooks/skill-gate.py` | `_log_diag()` 헬퍼 + line 65-68 except 진단 + line 41-49 키 변형 silent 진단 | W2+W4 |
| `hooks/skill-stop-protect.py` | `_log_event` schema 표준화 (`guard`/`result` setdefault, line 55-66) — backward-compat | W2 |
| `hooks/ralph-session-stop.py` | **신규** `_is_ralph_initiator` 3-layer fallback (line 109-114 변경 + 보조 helpers) | W4 |
| `harness/executor.py` | line 88-93 직후 `_verify_live_json_writable` 호출 + 실패 시 ESCALATE + `write_lease()` 에 HARNESS_ACTIVE flag mtime touch (line 179-188) | W4 |

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

**수정 대상 파일·줄번호**:
- `hooks/agent-boundary.py:47-90` — 정적 `ALLOW_MATRIX` dict (engineer 키만 동적화 대상)
- `hooks/agent-boundary.py:218` — `allowed_patterns = ALLOW_MATRIX.get(active_agent, [])` 호출 지점
- `hooks/agent-boundary.py:232-247` — deny 메시지 출력 (W4 enrichment 대상)

**function signature 변경**: 없음 (외부 인터페이스 유지). 내부 모듈 변수만 변경.

**v1↔v2 분기 위치 (단일 헬퍼)**:
```python
# hooks/agent-boundary.py 모듈 상단 (line 47 직전) — _STATIC_ENGINEER_SCOPE 명시 정의
_STATIC_ENGINEER_SCOPE: list[str] = [
    r'(^|/)src/',
    r'(^|/)apps/[^/]+/src/',
    r'(^|/)apps/[^/]+/app/',
    r'(^|/)apps/[^/]+/alembic/',
    r'(^|/)packages/[^/]+/src/',
    r'(^|/)apps/[^/]+/[^/]+\.toml$',
    r'(^|/)apps/[^/]+/[^/]+\.cfg$',
]

# ALLOW_MATRIX["engineer"] 는 빌드 시 _STATIC_ENGINEER_SCOPE 참조로 변경
ALLOW_MATRIX = {
    "engineer": _STATIC_ENGINEER_SCOPE,  # 기본값 (v1 fallback 동등)
    "architect": [...],  # 기존 유지
    ...
}
```

**핵심 헬퍼 (`harness_common.py` 신설 — §1.8 참조)**:
- `_load_engineer_scope()` — agent-boundary 와 commit-gate 가 공유.
- 호출 지점: `main()` 진입부 또는 `ALLOW_MATRIX.get(active_agent, [])` 호출 직전.

**main() 호출 시 패치 (line 218 변경)**:
```python
# v1 (현행): allowed_patterns = ALLOW_MATRIX.get(active_agent, [])
# v2 패치:
if active_agent == "engineer":
    from harness_common import _load_engineer_scope  # 신규 헬퍼 (§1.8)
    allowed_patterns = _load_engineer_scope()
else:
    allowed_patterns = ALLOW_MATRIX.get(active_agent, [])
```

**v1 fallback 보장 검증**:
- `HARNESS_GUARD_V2_AGENT_BOUNDARY` 미설정 시 `_load_engineer_scope()` 내부에서 `_STATIC_ENGINEER_SCOPE` 반환 → ALLOW_MATRIX["engineer"] 그대로.
- 빈 리스트 (`engineer_scope: []`) 시 `or _STATIC_ENGINEER_SCOPE` 폴백 (§4.1 참조).
- 회귀 검증 테스트: `HARNESS_GUARD_V2_AGENT_BOUNDARY` unset / `=0` / `=1` 3 케이스 모두 `^src/foo.ts` 매치 확인.

**HARNESS_INFRA_PATTERNS / READ_DENY_MATRIX**: **변경 없음** — 보안 가드 (allowlist 유지). I-1 모델 변경 정책 §2 (보안 가드 예외) 명시.

**deny 메시지 enrichment (W4 — line 246-247 변경)**:
```python
# v2 enrichment (HARNESS_GUARD_V2_AGENT_BOUNDARY=1 전용)
if os.environ.get("HARNESS_GUARD_V2_AGENT_BOUNDARY") == "1":
    scope_source = "harness.config.json" if cfg_loaded else "static fallback"
    live_health = "OK" if active_agent else "MISSING (cross-guard cascade?)"
    deny(f"❌ [hooks/agent-boundary.py] {active_agent}는 {os.path.basename(fp)} 수정 불가. "
         f"허용 경로: {allowed_desc}\n"
         f"진단: live.json={live_health} | engineer_scope source: {scope_source} (V2)")
else:
    # v1 메시지 그대로
    deny(f"❌ [hooks/agent-boundary.py] {active_agent}는 {os.path.basename(fp)} 수정 불가. "
         f"허용 경로: {allowed_desc}")
```

---

### 1.2 `commit-gate.py`

**수정 대상 파일·줄번호**:
- `hooks/commit-gate.py:50-57` — Gate 1 mutate 패턴 regex 다발 (`_IS_GH_ISSUE_MUTATE`)
- `hooks/commit-gate.py:115` — Gate 5 staged 매칭 `re.search(r"^src/", staged, re.MULTILINE)`

**function signature 변경**: 없음 (모듈 함수만).

**Gate 1 신규 헬퍼 (`harness/tracker.py` 의 `MUTATING_SUBCOMMANDS` 위임)**:
```python
# hooks/commit-gate.py 신규 헬퍼 (line 22 부근)
def _matches_tracker_mutate(cmd: str) -> bool:
    """harness.tracker MUTATING_SUBCOMMANDS 의 동적 매칭.
    v1 fallback: 정적 (create-issue|comment) regex.
    """
    if os.environ.get("HARNESS_GUARD_V2_COMMIT_GATE") != "1":
        # v1 동작 (line 55-56 그대로)
        return bool(
            re.search(r"harness\.tracker\s+(create-issue|comment)", cmd)
            or re.search(r"harness/tracker\.py\s+(create-issue|comment)", cmd)
        )
    try:
        from harness.tracker import MUTATING_SUBCOMMANDS  # §1.8 신설
    except ImportError:
        sys.stderr.write("[commit-gate] WARN: tracker.MUTATING_SUBCOMMANDS import failed; v1 fallback\n")
        return bool(re.search(r"harness\.tracker\s+(create-issue|comment)", cmd))
    if not MUTATING_SUBCOMMANDS:
        sys.stderr.write("[commit-gate] WARN: MUTATING_SUBCOMMANDS empty; v1 fallback\n")
        return bool(re.search(r"harness\.tracker\s+(create-issue|comment)", cmd))
    sub_pat = "|".join(re.escape(s) for s in MUTATING_SUBCOMMANDS)
    return bool(
        re.search(rf"harness\.tracker\s+({sub_pat})", cmd)
        or re.search(rf"harness/tracker\.py\s+({sub_pat})", cmd)
    )

# Gate 1 패치 (line 50-57 변경)
_IS_GH_ISSUE_MUTATE = (
    re.search(r"gh\s+issue\s+(create|edit)", cmd)
    or re.search(r"gh\s+api\s+.*issues.*--method\s+POST", cmd)
    or re.search(r"gh\s+api\s+.*issues.*-X\s+(POST|PATCH)", cmd)
    or re.search(r"gh\s+api\s+.*issues/\d+.*-X\s+PATCH", cmd)
    or _matches_tracker_mutate(cmd)  # ← v1/v2 모두 통과
)
```

**Gate 5 staged 패턴 동적 (line 115 변경)**:
```python
# hooks/commit-gate.py 신규 헬퍼
def _has_engineer_change(staged: str) -> bool:
    """staged 파일이 engineer_scope 패턴 중 하나라도 매치하는지.
    v1: 정적 ^src/. v2: harness_common._load_engineer_scope() 위임.
    """
    if os.environ.get("HARNESS_GUARD_V2_COMMIT_GATE") != "1":
        return bool(re.search(r"^src/", staged, re.MULTILINE))
    try:
        from harness_common import _load_engineer_scope  # §1.8
        patterns = _load_engineer_scope()
    except Exception as e:
        sys.stderr.write(f"[commit-gate] WARN: engineer_scope load failed ({e}); v1 fallback\n")
        return bool(re.search(r"^src/", staged, re.MULTILINE))
    if not patterns:
        sys.stderr.write("[commit-gate] WARN: engineer_scope empty; v1 fallback ^src/\n")
        return bool(re.search(r"^src/", staged, re.MULTILINE))
    # regex 컴파일 실패 방어 (§4.2)
    try:
        combined_re = re.compile("(" + "|".join(patterns) + ")", re.MULTILINE)
    except re.error as e:
        sys.stderr.write(f"[commit-gate] WARN: engineer_scope regex invalid ({e}); v1 fallback ^src/\n")
        combined_re = re.compile(r"^src/", re.MULTILINE)
    return bool(combined_re.search(staged))

# main() line 115 패치
has_src = _has_engineer_change(staged)
```

**v1 fallback 보장 검증**:
- `HARNESS_GUARD_V2_COMMIT_GATE` unset → 두 헬퍼 모두 1줄째 v1 분기 → 기존 regex 그대로.
- tracker import 실패 / MUTATING_SUBCOMMANDS 빈 리스트 / engineer_scope 빈 리스트 / regex invalid 4 케이스 모두 stderr 경고 후 v1 동작.
- 회귀 검증 테스트: `git commit` with `src/foo.ts` staged 가 `HARNESS_GUARD_V2_COMMIT_GATE` 미설정 시 LGTM 검사 동작 확인.

**deny 메시지 enrichment (W4)**:
- Gate 1 deny 메시지 (line 60-65) 에 `진단: cmd matched MUTATING_SUBCOMMANDS={listed} | tracker source: V2` 추가 (V2 활성 시).
- Gate 5 deny 메시지 (line 134) 에 `진단: engineer_scope source: harness.config.json (V2) | matched_pattern: <pattern>` 추가 (V2 활성 시).

---

### 1.3 `agent-gate.py`

**수정 대상 파일·줄번호**:
- `hooks/agent-gate.py:42-43` — `flag()` 헬퍼 (HARNESS_ACTIVE 존재 검사)
- `hooks/agent-gate.py:81` — `re.search(r"#\d+|LOCAL-\d+", prompt)` 추적 ID 단일 regex
- `hooks/agent-gate.py:99` — `not flag(FLAGS.HARNESS_ACTIVE)` Gate 3 호출 지점
- `hooks/agent-gate.py:120` — `not flag(FLAGS.HARNESS_ACTIVE)` Mode-level 호출 지점
- `hooks/agent-gate.py:136` — `flag(FLAGS.HARNESS_ACTIVE)` engineer branch 검사 호출 지점
- `hooks/agent-gate.py:156` — `flag(FLAGS.HARNESS_ACTIVE)` 호출 로그 caller 분기

**function signature 변경**: 없음 (`flag()` 호출자는 모두 boolean 반환만 기대).

**핵심 변경 1: `flag()` 헬퍼를 v2 분기 인지로 확장 (line 42-43 변경)**:
```python
def flag(name: str) -> bool:
    """v1: 단순 존재. v2: age check + auto-GC (HARNESS_ACTIVE 한정)."""
    if (
        name == FLAGS.HARNESS_ACTIVE
        and os.environ.get("HARNESS_GUARD_V2_AGENT_GATE") == "1"
    ):
        return _is_active_flag_fresh()
    return flag_exists(PREFIX, name)
```

**핵심 변경 2: 신규 헬퍼 `_is_active_flag_fresh()` (line 43 직후 추가)**:
```python
def _is_active_flag_fresh() -> bool:
    """HARNESS_ACTIVE flag mtime + TTL > now → fresh.
    skill-stop-protect.py started_at+ttl 패턴을 harness_common.auto_gc_stale_flag 로 일반화.
    """
    from harness_common import auto_gc_stale_flag  # §1.8 신설
    flag_p = Path(flag_path(PREFIX, FLAGS.HARNESS_ACTIVE))
    ttl = int(os.environ.get("HARNESS_GUARD_V2_FLAG_TTL_SEC", "21600"))  # 6h default
    return auto_gc_stale_flag(flag_p, ttl, "agent-gate")
```

**핵심 변경 3: 추적 ID 검증을 `tracker.parse_ref` 위임 (line 81 변경)**:
```python
# 신규 헬퍼 (line 39 부근)
def _has_tracking_id(prompt: str) -> bool:
    """v1: 단일 regex. v2: tracker.parse_ref 위임 (백엔드 단일 책임)."""
    if os.environ.get("HARNESS_GUARD_V2_AGENT_GATE") != "1":
        return bool(re.search(r"#\d+|LOCAL-\d+", prompt))
    try:
        from harness.tracker import parse_ref
    except ImportError:
        return bool(re.search(r"#\d+|LOCAL-\d+", prompt))  # v1 폴백
    # 프롬프트에서 추적 ID 후보 찾기 (모든 백엔드 지원)
    for token in re.findall(r"#\d+|LOCAL-\d+|\b\d+\b", prompt):
        try:
            parse_ref(token)
            return True
        except (ValueError, Exception):
            continue
    return False

# main() line 81 패치
if not is_exempt and not _has_tracking_id(prompt):
    deny(...)
```

**핵심 변경 4: heartbeat — `harness/executor.py` 의 `write_lease()` 가 매 15초 lock_file 쓰기 (이미 line 195-205)**.

W2 추가 작업: `executor.py write_lease()` 에 `flag_p = state_dir.flag_path(FLAGS.HARNESS_ACTIVE); flag_p.touch(exist_ok=True)` 추가 — TTL false-GC 방지. (`StateDir.flag_path` 가 없으면 `state_dir.path / f"{prefix}_{FLAGS.HARNESS_ACTIVE}"` 직접 사용).

**v1 fallback 보장 검증**:
- `HARNESS_GUARD_V2_AGENT_GATE` unset → `flag()` 는 `flag_exists()` 직접 호출 (현행 동작 100% 동등).
- `_has_tracking_id` 도 v1 regex 그대로.
- tracker import 실패 시 v1 regex 폴백 (회귀 0).
- 회귀 검증 테스트: 4 변형 프롬프트 (`#42`, `LOCAL-7`, `42`, `Issue 42`) v1/v2 결과 비교.

**deny 메시지 enrichment (W4)**:
- line 82-85 `❌ {agent} 호출 전 추적 ID 등록 필요...` 메시지에 `진단: tracker.parse_ref 검증 (V2) | 시도된 백엔드: github,local` 추가.
- line 104-115 HARNESS_ACTIVE 차단 메시지에 `진단: flag fresh? {True|False auto-GC at age={N}s}` 추가.

---

### 1.4 `skill-gate.py`

**수정 대상 파일·줄번호**:
- `hooks/skill-gate.py:65-68` — `try: ss.set_active_skill(...) except Exception: pass` (silent 실패 = 5번째 위험 진앙)

**function signature 변경**: 없음 (`main()` 만 갱신).

**핵심 변경: silent except → diagnostic except (line 65-68 변경)**:
```python
# 신규 헬퍼 (line 30 부근, _read_stdin 다음에 추가)
def _log_diag(event: dict) -> None:
    """진단 집계 — harness-state/.logs/skill-gate.jsonl"""
    try:
        log_dir = ss.state_root() / ".logs"
        log_dir.mkdir(exist_ok=True)
        log_path = log_dir / "skill-gate.jsonl"
        event["ts"] = int(time.time())
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except OSError:
        pass

# main() line 65-68 패치
import time as _time  # 모듈 상단으로 이동 권장
v2_on = os.environ.get("HARNESS_GUARD_V2_SKILL_GATE") == "1"
try:
    ss.set_active_skill(sid, name, level)
    # v2 success 진단 — 5번째 위험 (silent missing) 사전 가시화
    if v2_on:
        _log_diag({"event": "set_skill_ok", "sid": sid, "skill": name, "level": level})
except Exception as e:
    # v1: silent pass (regression 0).
    # v2: stderr 경고 + diag log. passive recorder 본질 유지 (차단 없음).
    if v2_on:
        sys.stderr.write(
            f"[skill-gate] WARN: set_active_skill failed (sid={sid[:8]}…, skill={name}): {e}\n"
            f"  → downstream guards (agent-boundary/issue-gate/commit-gate) may false-block.\n"
            f"  → check live.json writability: ls -la .claude/harness-state/.sessions/{sid}/live.json\n"
        )
        _log_diag({"event": "set_skill_fail", "sid": sid, "skill": name, "err": str(e)})
    # silent pass 자체는 v1/v2 동일 — 본 가드는 deny 권한 없음
    pass
```

**키 변형 silent 실패 — `_skill_name` 도 진단 추가 (line 41-49 변경)**:
```python
def _skill_name(d: dict) -> str:
    """Skill 툴 입력에서 스킬 이름 추출. 가능한 키 변형 모두 시도."""
    inp = d.get("tool_input") or {}
    for key in ("skill", "skillName", "name"):
        v = inp.get(key)
        if v:
            return v
    # v2: 이름 없음을 진단 — 메인 Claude Skill 호출 형식 변경 시 silent missing 차단
    if os.environ.get("HARNESS_GUARD_V2_SKILL_GATE") == "1":
        sys.stderr.write(
            f"[skill-gate] WARN: Skill tool_input missing skill name. keys={list(inp.keys())}\n"
        )
        _log_diag({"event": "skill_name_missing", "tool_input_keys": list(inp.keys())})
    return ""
```

**v1 fallback 보장 검증**:
- `HARNESS_GUARD_V2_SKILL_GATE` unset → except 본문 `if v2_on:` 분기 모두 skip → 완전한 silent pass (현행 동작).
- 회귀 검증 테스트: live.json 디렉토리 권한 0o000 만든 상태에서 Skill 호출 → v1 silent / v2 stderr 경고 출력 비교.

**진단 로그 형식 (`harness-state/.logs/skill-gate.jsonl`)**:
```json
{"ts": 1714298400, "event": "set_skill_ok", "sid": "c86e...", "skill": "ralph-loop:ralph-loop", "level": "heavy"}
{"ts": 1714298401, "event": "set_skill_fail", "sid": "c86e...", "skill": "ralph-loop:ralph-loop", "err": "OSError: [Errno 13] Permission denied: ..."}
{"ts": 1714298402, "event": "skill_name_missing", "tool_input_keys": ["foo"]}
```

**중요**: 본 가드는 deny 결정 권한이 **여전히 없다** — passive recorder 본질 유지. v2 변경은 진단 가시성만 추가.

---

### 1.5 `skill-stop-protect.py`

**수정 대상 파일·줄번호**:
- `hooks/skill-stop-protect.py:55-66` — `_log_event` 헬퍼 (key 표준화 대상)
- `hooks/skill-stop-protect.py:82, 109-114, 127-131` — `_log_event` 호출 지점 3곳

**function signature 변경**: 없음 (`_log_event` 시그니처 유지, 내부 key 추가만).

**핵심 변경 — `_log_event` key 표준화 (line 55-66 변경)**:
```python
def _log_event(event: dict) -> None:
    """진단 로그 — harness-state/.logs/skill-protect.jsonl
    v2: guard, result 키 표준화 (다른 가드와 동일 schema).
    """
    try:
        root = ss.state_root()
        log_dir = root / ".logs"
        log_dir.mkdir(exist_ok=True)
        log_path = log_dir / "skill-protect.jsonl"
        # v2 표준 schema 강제 — 누락된 key 자동 채움
        event.setdefault("ts", int(time.time()))
        event.setdefault("guard", "skill-stop-protect")
        # event 안에 result 가 없으면 event 종류로 유도 (kill_clear/auto_release/block_stop)
        if "result" not in event:
            evt = event.get("event", "")
            event["result"] = {
                "kill_clear": "released",
                "auto_release": "released",
                "block_stop": "blocked",
            }.get(evt, "unknown")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except OSError:
        pass
```

**v2 분기**: 없음 — key 추가는 backward-compat (기존 reader 도 새 key 무시 가능). 모델 변경 정책 §1.5 (가장 robust 한 가드) 따라 분기 없이 표준화만.

**v1 fallback 보장 검증**:
- 기존 `_log_event` 호출자 (line 82, 109-114, 127-131) 의 인자 dict 변경 없음 — `setdefault` 가 기존 key 보존.
- jsonl reader 가 `guard`/`result` 새 key 모름 → 무시 → 회귀 0.

**SELF_MANAGED_LIFECYCLE 모델은 reference**: §1.8 `auto_gc_stale_flag` 헬퍼가 본 가드의 `started_at + ttl_sec` 패턴 (line 102-114) 을 일반화 — agent-gate.HARNESS_ACTIVE flag GC 가 동일 헬퍼 사용.

**코드 공유 — 별도 변경 없음**: 본 가드 자체는 `auto_gc_stale_flag` 를 호출하지 않는다 (skill-protect 는 live.json.skill 의 dict 안 `started_at` 필드 기반이지 flag mtime 기반이 아니므로 직접 적용 불가). 단, 동일한 *개념* (TTL + max_reinforcements + auto_release) 이 새 헬퍼에 일반화되어 agent-gate 가 채택. 본 가드는 reference 이자 변경 최소.

---

### 1.6 `issue-gate.py`, `plugin-write-guard.py` — 변경 없음

W4 진단 가시성 표준만 자동 흡수 (deny 메시지에 진단 정보 추가). 모델 변경 없음.

---

### 1.7 신규 config 키 — `harness.config.json`

**수정 대상 파일·줄번호**:
- `harness/config.py:42-55` — `HarnessConfig` dataclass (필드 추가)
- `harness/config.py:105-117` — `load_config()` 의 dict→dataclass 변환 (필드 매핑 추가)

**`HarnessConfig.engineer_scope` 필드 추가 (line 55 직후 추가)**:
```python
@dataclass
class HarnessConfig:
    # ... 기존 필드 유지 ...
    agent_tier_assignment: dict = field(default_factory=lambda: dict(DEFAULT_AGENT_TIER_ASSIGNMENT))
    # 신규 (Phase 2 W2 — engineer scope 동적화)
    engineer_scope: list = field(default_factory=list)  # 빈 리스트 default — agent-boundary._STATIC_ENGINEER_SCOPE 폴백
```

**`load_config()` 매핑 추가 (line 105-117 패치)**:
```python
return HarnessConfig(
    prefix=data.get("prefix", "proj"),
    # ... 기존 필드 유지 ...
    agent_tier_assignment=merged_assignment,
    engineer_scope=data.get("engineer_scope", []) if isinstance(data.get("engineer_scope", []), list) else [],
)
```

**선택적 사용자 config (`harness.config.json`)**:
```json
{
  "prefix": "myproj",
  "engineer_scope": [
    "(^|/)src/",
    "(^|/)apps/[^/]+/src/",
    "(^|/)apps/[^/]+/app/",
    "(^|/)apps/[^/]+/alembic/",
    "(^|/)packages/[^/]+/src/",
    "(^|/)apps/[^/]+/[^/]+\\.toml$",
    "(^|/)apps/[^/]+/[^/]+\\.cfg$",
    "(^|/)services/[^/]+/src/",
    "(^|/)libs/[^/]+/src/"
  ]
}
```

**default 동작**: 키 누락 → 빈 리스트 → `_load_engineer_scope()` 의 `or _STATIC_ENGINEER_SCOPE` 폴백 → 회귀 0.

**검증**: `tests/pytest/test_guards.py` (W5) 에 `test_engineer_scope_load_*` 4 케이스 (None / [] / 사용자 override / regex invalid).

---

### 1.8 신규 헬퍼 — `harness/tracker.py` + `hooks/harness_common.py`

#### 1.8.1 `harness/tracker.py` — `MUTATING_SUBCOMMANDS` 상수 신설

**수정 대상**: `harness/tracker.py:32` 부근 (parse_ref 함수 정의 전).

`parse_ref` 는 이미 line 59-80 에 존재 — 신규 작업은 **상수 추가만**:
```python
# harness/tracker.py 모듈 상단 추가 (line 32 부근)
# Mutating subcommands — commit-gate.py 가 Gate 1 차단 패턴에 위임.
# 새 subcommand 추가 시 본 frozenset 만 갱신하면 hooks/commit-gate.py 자동 흡수.
MUTATING_SUBCOMMANDS: frozenset = frozenset({
    "create-issue",
    "comment",
})
```

**추후 확장**: `update-issue`, `close-issue` 등 추가 시 본 상수만 update — commit-gate Gate 1 자동 흡수 (drift 0).

#### 1.8.2 `hooks/harness_common.py` — `_load_engineer_scope` + `auto_gc_stale_flag` + `_verify_live_json_writable`

**수정 대상**: `hooks/harness_common.py` 파일 끝 (line 268 이후) 헬퍼 추가.

```python
# hooks/harness_common.py 끝에 추가

# ── engineer_scope 로더 (agent-boundary + commit-gate 공유) ──
_ENGINEER_SCOPE_CACHE: list[str] | None = None  # per-process 캐시

# 정적 default — agent-boundary.ALLOW_MATRIX["engineer"] 와 동등.
# v1 동작 회귀 검증을 위해 본 리스트만으로 기존 매트릭스가 재현 가능해야 함.
_STATIC_ENGINEER_SCOPE: list[str] = [
    r'(^|/)src/',
    r'(^|/)apps/[^/]+/src/',
    r'(^|/)apps/[^/]+/app/',
    r'(^|/)apps/[^/]+/alembic/',
    r'(^|/)packages/[^/]+/src/',
    r'(^|/)apps/[^/]+/[^/]+\.toml$',
    r'(^|/)apps/[^/]+/[^/]+\.cfg$',
]

def _load_engineer_scope() -> list[str]:
    """engineer 활성 시 ALLOW_MATRIX["engineer"] 가 사용할 패턴 리스트.
    agent-boundary 와 commit-gate 가 같은 source 에서 파생.
    HARNESS_GUARD_V2_AGENT_BOUNDARY 또는 HARNESS_GUARD_V2_COMMIT_GATE 중 하나라도
    활성이면 config 로드 시도. 둘 다 미설정이면 정적 fallback (per-process 캐시).
    """
    global _ENGINEER_SCOPE_CACHE
    if _ENGINEER_SCOPE_CACHE is not None:
        return _ENGINEER_SCOPE_CACHE
    v2_any = (
        os.environ.get("HARNESS_GUARD_V2_AGENT_BOUNDARY") == "1"
        or os.environ.get("HARNESS_GUARD_V2_COMMIT_GATE") == "1"
        or os.environ.get("HARNESS_GUARD_V2_ALL") == "1"
    )
    if not v2_any:
        _ENGINEER_SCOPE_CACHE = list(_STATIC_ENGINEER_SCOPE)
        return _ENGINEER_SCOPE_CACHE
    try:
        # PLUGIN_ROOT 의 harness/config.py 동적 로드
        plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
        if plugin_root:
            sys.path.insert(0, plugin_root)
        from harness.config import load_config
        cfg = load_config()
        scope = list(cfg.engineer_scope) if cfg.engineer_scope else []
    except Exception as e:
        sys.stderr.write(f"[harness_common] WARN: engineer_scope config load failed ({e}); fallback static\n")
        scope = []
    if not scope:
        scope = list(_STATIC_ENGINEER_SCOPE)
    _ENGINEER_SCOPE_CACHE = scope
    return _ENGINEER_SCOPE_CACHE


# ── auto_gc_stale_flag — skill-stop-protect 패턴 일반화 ──
def auto_gc_stale_flag(flag_p, ttl_sec: int, label: str) -> bool:
    """flag mtime 기반 age check + auto-GC.
    Args:
      flag_p: pathlib.Path — flag 파일 경로
      ttl_sec: int — TTL (초). default 6h (21600).
      label: str — stderr/log 진단용 가드 이름 (e.g. "agent-gate")
    Returns: fresh 여부 (False 면 stale 또는 부재).
    """
    import time
    if not flag_p.exists():
        return False
    try:
        age = time.time() - flag_p.stat().st_mtime
    except OSError:
        return False
    if age > ttl_sec:
        try:
            flag_p.unlink()
            sys.stderr.write(
                f"[{label}] auto-GC stale flag {flag_p.name} "
                f"(age={int(age)}s > ttl={ttl_sec}s)\n"
            )
            # 진단 jsonl
            try:
                from session_state import state_root
                log_dir = state_root() / ".logs"
                log_dir.mkdir(exist_ok=True)
                log_path = log_dir / f"{label}.jsonl"
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps({
                        "ts": int(time.time()),
                        "guard": label,
                        "event": "auto_gc",
                        "flag": flag_p.name,
                        "age": int(age),
                        "ttl": ttl_sec,
                    }, ensure_ascii=False) + "\n")
            except Exception:
                pass
        except OSError:
            pass
        return False
    return True


# ── live.json round-trip canary (executor.py 진입 시 호출) ──
def _verify_live_json_writable(session_id: str) -> tuple[bool, str]:
    """live.json 쓰기 가능 여부 사전 검증. Returns (ok, error_msg).
    ok=False 면 caller 가 ESCALATE 결정. silent dependency cascade 사전 차단.
    """
    try:
        from session_state import update_live, clear_live_field
        import time
        canary = int(time.time())
        update_live(session_id, _harness_canary=canary)
        # readback 검증 — atomic_write_json 후 directory fsync 까지 검증
        from session_state import get_live
        live = get_live(session_id)
        if live.get("_harness_canary") != canary:
            return (False, f"canary mismatch: wrote {canary}, read {live.get('_harness_canary')}")
        clear_live_field(session_id, "_harness_canary")
        return (True, "")
    except Exception as e:
        return (False, f"{type(e).__name__}: {e}")
```

**v1 fallback 보장 검증**:
- `_load_engineer_scope`: `v2_any` 미활성 시 무조건 `_STATIC_ENGINEER_SCOPE` (config 로드 시도조차 안 함 → 빠른 path).
- `auto_gc_stale_flag`: caller 가 v2 분기에서만 호출 — v1 호출자는 `flag_exists` 그대로 사용.
- `_verify_live_json_writable`: caller 가 `HARNESS_GUARD_V2_*` 어떤 것도 검사하지 않음 — executor.py W4 진입 검증 (always-on).

---

### 1.9 W4 신규 — `hooks/ralph-session-stop.py` Layered Fallback

**5번째 위험 실측 케이스 (2026-04-28 본 ralph-loop 환경에서 발현)**:
- 본 세션 sid `c86ce041-e4d3-4d05-83d8-d9717e7029dc` 의 `live.json` 에 `skill` 필드 자체가 없음.
- `ralph-session-stop.py:109` `_is_ralph_initiator(sid)` → `ss.get_active_skill(sid)` → None → False.
- 결과: 본 세션이 진짜 ralph 시작자임에도 placeholder `__pending_<short>__` 박힘 → ralph-loop stop hook 발동 안 해서 Iter 1→2 transition 멈춤.
- 진단: skill-gate.py 의 `live.json.skill` 쓰기가 silent 실패한 cascade — 카탈로그 §3 의 정확한 시나리오 발현.

**수정 대상 파일·줄번호**:
- `hooks/ralph-session-stop.py:109-114` — `_is_ralph_initiator()` 함수 (1차 폴백만 존재)

**function signature 변경**: 없음 (`_is_ralph_initiator(sid: str) -> bool` 유지).

**핵심 변경 — 3-layer fallback (line 109-114 변경)**:
```python
def _is_ralph_initiator(sid: str) -> bool:
    """현재 세션이 ralph-loop의 시작자인지 — 3-layer fallback.

    Staged rollout: HARNESS_GUARD_V2_RALPH_FALLBACK=1 일 때만 2~3차 활성.
    미설정 시 v1 동작 (live.json.skill 단일 검사) 유지 — regression 0.

    1차 (always): live.json.skill.name ∈ RALPH_SKILL_NAMES
    2차 (V2): live.json._meta.skill_started_at 존재 (skill-gate 가 partial 기록 흔적)
    3차 (V2): RALPH_SESSION_INITIATOR env var == sid 또는 ralph-cross-session.jsonl
              에 본 sid 의 claim_self 이벤트가 있는지
    """
    # 1차 — v1 경로 (변경 없음)
    skill = ss.get_active_skill(sid)
    if skill and skill.get("name", "") in RALPH_SKILL_NAMES:
        return True

    # V2 staged rollout — 미설정 시 v1 결과 (False) 반환
    if os.environ.get("HARNESS_GUARD_V2_RALPH_FALLBACK") != "1":
        return False

    # 2차 — _meta 흔적 (skill-gate 가 _meta 만 쓰고 skill 갱신 실패한 partial 케이스)
    try:
        live_p = ss.live_path(sid)
        if live_p.exists():
            data = json.loads(live_p.read_text(encoding="utf-8"))
            meta = data.get("_meta") or {}
            # skill-gate 가 partial 흔적을 _meta 에 남기는 경우 (W4 보강과 함께 도입)
            if meta.get("skill_started_at") and meta.get("skill_name", "") in RALPH_SKILL_NAMES:
                _log_event({
                    "event": "fallback_meta_match",
                    "sid": sid,
                    "skill_name": meta.get("skill_name"),
                })
                return True
    except (json.JSONDecodeError, OSError):
        pass

    # 3차 — env var + jsonl 이벤트 검색
    env_initiator = os.environ.get("RALPH_SESSION_INITIATOR", "")
    if env_initiator and env_initiator == sid:
        _log_event({"event": "fallback_env_match", "sid": sid})
        return True

    try:
        log_p = ss.state_root() / ".logs" / "ralph-cross-session.jsonl"
        if log_p.exists():
            # 본 sid 의 claim_self 이벤트가 있으면 시작자 (과거 기록)
            for line in log_p.read_text(encoding="utf-8").splitlines():
                try:
                    evt = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if evt.get("event") == "claim_self" and evt.get("sid") == sid:
                    _log_event({"event": "fallback_jsonl_match", "sid": sid})
                    return True
    except OSError:
        pass

    # 모든 폴백 실패 — placeholder 박는 v1 동작 유지 (regression 0)
    _log_event({"event": "fallback_all_missed", "sid": sid})
    return False
```

**보조 — skill-gate 의 `_meta.skill_started_at` 기록 (선택, V2 보강 시)**:
- W4 staged rollout 단계 4 (skill-gate.V2 활성) 시 skill-gate.py 가 set_active_skill 실패해도 `_meta.skill_started_at` + `_meta.skill_name` 만이라도 partial 기록 시도 — ralph-session-stop 2차 폴백 활용.
- 본 정밀화에서 skill-gate.py 의 변경은 §1.4 의 진단 추가만으로 한정 (partial 기록은 별 issue 로 분리). 즉 2차 폴백은 *향후 활성* — 현재는 항상 miss.

**v1 fallback 보장 검증**:
- `HARNESS_GUARD_V2_RALPH_FALLBACK` unset → 1차 검사 후 즉시 return False (현행 동작 100% 동등).
- 모든 폴백 실패 시 placeholder 박는 기존 main() 경로 (line 164-175) 진입 — 회귀 0.
- 회귀 검증 테스트:
  - 정상 ralph 세션: 1차 매치 → True (v1/v2 동일).
  - 비-ralph 세션: 1차 miss + V2 off → False (v1 동등).
  - 5번째 위험 발현 케이스 (live.json.skill 없음 + env var 설정): V2 on → 3차 매치 → True (영구 fix).
  - 비-ralph 세션 + V2 on + env var 없음 + jsonl 없음: 모든 폴백 miss → False (v1 동등).

**staged rollout flag 결정 (architect 결정)**:
- 신규 환경변수 `HARNESS_GUARD_V2_RALPH_FALLBACK` 도입 결정. 가드 이름이 아닌 보강 항목이지만, V2 패밀리의 staged rollout 패턴 일관성 위해 동일 prefix 사용.
- default off — Stage 4 (배포) 시점에 `HARNESS_GUARD_V2_ALL=1` 에 포함 (§5.4 참조).
- 임시 fix (사용자 sed) 는 deprecate — 영구 fix 가 본 V2 분기 뒤에 들어감.

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

**구현 위치**: `harness/executor.py:88` (sys.path.insert + session_state import 직후, line 88-93 의 `if session_id` 분기 안)

```python
# harness/executor.py 의 line 84-87 직후 추가
if ss is not None:
    session_id = ss.current_session_id()
    if session_id:
        os.environ["HARNESS_SESSION_ID"] = session_id
        # W4 신규 — round-trip canary
        try:
            from hooks.harness_common import _verify_live_json_writable
        except ImportError:
            sys.path.insert(0, str(PLUGIN_ROOT / "hooks"))
            from harness_common import _verify_live_json_writable
        ok, err = _verify_live_json_writable(session_id)
        if not ok:
            print(
                f"[HARNESS] ❌ ESCALATE — live.json round-trip 실패: {err}\n"
                f"  downstream guards (agent-boundary/issue-gate/commit-gate/ralph-session-stop) 가\n"
                f"  silent-cascade 합니다. 진단:\n"
                f"  ls -la .claude/harness-state/.sessions/{session_id}/\n"
                f"  df -h .claude/harness-state/  # 디스크 풀 확인\n",
                file=sys.stderr,
            )
            sys.exit(1)
```

**이 검증은 staged rollout flag 뒤에 두지 않는다** — silent cascade 자체가 spec §3 I-7 SSOT 무효화이므로 always-on. 단, exit 코드 1 이 이전 정상 동작을 깨는 경우(예: 디스크 권한 일시 문제) 가 있을 수 있어 W4 도입 후 1주간 모니터링 — 잔존 사고 시 `HARNESS_GUARD_V2_LIVE_JSON_CANARY=0` env var 로 임시 우회 가능하게 추가 검토.

### 2.5 Ralph-session-stop layered fallback (W4 신규)

§1.9 의 `_is_ralph_initiator` 3-layer fallback 의 의사코드 흐름:

```
sid 입력
  ↓
[1차] live.json.skill.name ∈ RALPH_SKILL_NAMES
  ├─ True → return True (v1 경로 = ralph 초기자 정상 인식)
  └─ False ↓
       [V2 flag 검사: HARNESS_GUARD_V2_RALPH_FALLBACK=1?]
         ├─ Off → return False (v1 동등 — placeholder 박는 main() 경로 진입)
         └─ On ↓
              [2차] live.json._meta.skill_started_at + .skill_name in RALPH_SKILL_NAMES
                ├─ Match → return True (skill-gate partial 기록 활용 — 향후 활성)
                └─ Miss ↓
                     [3차] env RALPH_SESSION_INITIATOR == sid
                       ├─ Match → return True
                       └─ Miss ↓
                            [3차-b] ralph-cross-session.jsonl 에 본 sid 의 claim_self 이벤트?
                              ├─ Match → return True
                              └─ Miss → return False (모든 폴백 fail — v1 동등)
```

**진단 가시성**:
- 각 폴백 결과 _log_event 로 `harness-state/.logs/ralph-cross-session.jsonl` 에 추가 기록.
- 메인 Claude 가 `cat .claude/harness-state/.logs/ralph-cross-session.jsonl | grep fallback_` 으로 즉시 진단.

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

### 4.7 ralph-session-stop layered fallback false-positive (W4 신규)

**시나리오**: 비-ralph 세션이 우연히 `RALPH_SESSION_INITIATOR` env var 가 자기 sid 와 같게 export 된 상태로 들어옴 → 3차 폴백 잘못 매치 → 다른 ralph 세션의 state 파일 claim → cross-session 오염.

**방어**:
- env var 매치 시 즉시 return True 하지 않고 **2차 보강 검증**: `live.json.skill` 가 None 이라도 최근 30분 내 본 sid 의 PreToolUse(Skill) 호출 흔적이 `skill-gate.jsonl` 에 있는지 확인.
- 의사코드:
  ```python
  if env_initiator == sid:
      # 보강: skill-gate.jsonl 에 최근 30분 내 본 sid 의 ralph 호출 흔적
      try:
          log_p = ss.state_root() / ".logs" / "skill-gate.jsonl"
          if log_p.exists():
              recent_threshold = int(time.time()) - 1800  # 30 min
              for line in log_p.read_text().splitlines()[-200:]:  # tail 200
                  evt = json.loads(line)
                  if (
                      evt.get("sid") == sid
                      and evt.get("event") == "set_skill_ok"
                      and evt.get("skill") in RALPH_SKILL_NAMES
                      and evt.get("ts", 0) >= recent_threshold
                  ):
                      _log_event({"event": "fallback_env_match_corroborated", "sid": sid})
                      return True
              # env match 했지만 corroboration 실패 — false-positive 의심
              _log_event({"event": "fallback_env_match_uncorroborated", "sid": sid})
              return False
      except (json.JSONDecodeError, OSError):
          pass
      # log 자체 없음 → env 만 신뢰 (조기 도입 시 fallback)
      return True
  ```
- 회귀 검증: env var 임의 export + 비-ralph 세션 → corroboration 실패 → False (cross-session 오염 차단).

### 4.8 staged rollout flag 누적 호환성 (W4 신규)

**시나리오**: 사용자가 `HARNESS_GUARD_V2_AGENT_BOUNDARY=1` 만 활성, `HARNESS_GUARD_V2_COMMIT_GATE=0` → agent-boundary 는 config 의 engineer_scope 사용, commit-gate 는 정적 `^src/` 사용 → 모노레포에서 commit-gate Gate 5 가 src 변경 인식 못 해 LGTM 우회.

**방어**:
- `_load_engineer_scope` 헬퍼 내부에서 두 flag 중 하나라도 활성이면 config 로드 (이미 §1.8.2 에 반영). 즉, agent-boundary V2 단독 활성 시에도 commit-gate 는 별도 V2 flag 없이도 같은 source 사용.
- 단, commit-gate.py 의 main() 진입점에서 `HARNESS_GUARD_V2_COMMIT_GATE=1` 이 아니면 `_has_engineer_change` 첫 줄 `^src/` v1 분기로 직행 — *위 보강이 무의미*.
- 결정: §1.2 `_has_engineer_change` 의 v1 분기 조건을 `HARNESS_GUARD_V2_COMMIT_GATE != "1" and HARNESS_GUARD_V2_AGENT_BOUNDARY != "1"` 로 변경 — 두 flag 중 하나라도 활성이면 V2 동작 (Stage 1 jajang 실측 가능).
- 대안 거부 (`HARNESS_GUARD_V2_ENGINEER_SCOPE=1` 통합 flag 신설) — staged rollout 일관성 깨짐. 대신 `HARNESS_GUARD_V2_ALL=1` 이 두 flag 일괄 활성으로 충분.

---

## 5. Staged Rollout 계획

### 5.1 Feature Flag 일람 (7개 가드 + W4 보강 1개)

| 환경변수 | 가드/보강 | 활성 시 동작 |
|---|---|---|
| `HARNESS_GUARD_V2_AGENT_BOUNDARY=1` | `agent-boundary.py` | ALLOW_MATRIX["engineer"] 동적 로드 (config) + deny 메시지 진단 enrichment |
| `HARNESS_GUARD_V2_COMMIT_GATE=1` | `commit-gate.py` | staged 패턴 동적 + tracker.MUTATING_SUBCOMMANDS 위임 + deny enrichment |
| `HARNESS_GUARD_V2_AGENT_GATE=1` | `agent-gate.py` | HARNESS_ACTIVE flag age check + tracker.parse_ref 위임 + deny enrichment |
| `HARNESS_GUARD_V2_SKILL_GATE=1` | `skill-gate.py` | 쓰기 실패 stderr 경고 + 진단 집계 (passive recorder 본질 유지) |
| `HARNESS_GUARD_V2_SKILL_STOP_PROTECT=1` | `skill-stop-protect.py` | _log_event schema 표준화 (backward-compat) |
| `HARNESS_GUARD_V2_ISSUE_GATE=1` | `issue-gate.py` | (W4 한정) deny 메시지 진단 enrichment 만 |
| `HARNESS_GUARD_V2_PLUGIN_WRITE_GUARD=1` | `plugin-write-guard.py` | (W4 한정) deny 메시지 진단 enrichment 만 |
| `HARNESS_GUARD_V2_RALPH_FALLBACK=1` | **(W4 신규)** `ralph-session-stop.py` | `_is_ralph_initiator` 3-layer fallback 활성. 5번째 위험 실측 케이스 영구 fix. default off — env corroboration 검증 (§4.7) 포함. |

### 5.2 보조 환경변수

| 환경변수 | 기본값 | 설명 |
|---|---|---|
| `HARNESS_GUARD_V2_FLAG_TTL_SEC` | `21600` (6h) | HARNESS_ACTIVE flag age check TTL |
| `HARNESS_GUARD_V2_DIAG_LOG_DIR` | `harness-state/.logs/` | 진단 로그 디렉토리 |
| `HARNESS_GUARD_V2_ALL=1` | (off) | 7개 가드 V2 일괄 활성 (개발 편의) |

### 5.3 Rollout 단계

**Stage 0** (Iter 2 merge 직후): 모든 V2 flag off — 회귀 0 확인. executor.py round-trip canary 만 always-on (§2.4).

**Stage 1** (jajang 재실측): `HARNESS_GUARD_V2_AGENT_BOUNDARY=1` + `HARNESS_GUARD_V2_COMMIT_GATE=1` 만 on. 모노레포 시나리오 통과 확인.

**Stage 2** (1주 후): `HARNESS_GUARD_V2_AGENT_GATE=1` 추가. stale flag 시나리오 통과 확인.

**Stage 3** (2주 후): `HARNESS_GUARD_V2_SKILL_GATE=1` + `HARNESS_GUARD_V2_SKILL_STOP_PROTECT=1` + `HARNESS_GUARD_V2_RALPH_FALLBACK=1` 추가. 진단 가시성 + ralph 5번째 위험 영구 fix 활성.

**Stage 4** (배포): `HARNESS_GUARD_V2_ALL=1` default — setup-rwh.sh 가 자동 export. 본 flag 가 8개 V2 환경변수 (가드 7개 + ralph fallback 1개) 일괄 활성.

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
- [x] staged rollout `HARNESS_GUARD_V2_*` 7개 가드 환경변수 + 2개 보조 + 1개 ALL + W4 신규 1개 (`RALPH_FALLBACK`) 명세
- [x] W1 게이트 결정 (issue-gate / plugin-write-guard 제외) 명시 (§0 + §6)
- [x] PR title `[invariant-shift]` 토큰 사용 명시 (§7)
- [x] branch 네이밍 (`harness/guard-realignment-iter{1,2,3}`) 명시 (§7)
- [x] Cross-guard silent dependency chain (5번째 위험) 별도 처리 (catalog §3 + 본 §1.4 / §2.3 / §2.4)
- [x] 회귀 위험 8항목 분석 (§4 — 6 + 신규 §4.7 §4.8)
- [x] **Iter 2 정밀화 — 5개 가드 각각 함수 시그니처 + 의사코드 + 분기 위치 + v1 fallback 검증 명시** (§1.1~§1.5)
- [x] **W4 5+1 항목 구현 위치 + 의사코드 명시** (§2.1~§2.5)
- [x] **ralph-session-stop layered fallback 이 staged rollout flag 뒤에 있음** — `HARNESS_GUARD_V2_RALPH_FALLBACK` default off (§1.9)
- [x] **engineer 호출 시 추가 결정 없이 바로 코드 작성 가능 수준** — 줄번호 + 함수 시그니처 + import 경로 모두 명시

---

## 10. 수용 기준 (engineer 작업 검증용)

| 요구사항 ID | 내용 | 검증 방법 | 통과 조건 |
|---|---|---|---|
| REQ-001 | `harness/config.py` 에 `engineer_scope: list` 필드 추가 + load_config 매핑 | (TEST) | `tests/pytest/test_guards.py::test_config_engineer_scope_default_empty` 통과 |
| REQ-002 | `harness/tracker.py` 에 `MUTATING_SUBCOMMANDS` frozenset 상수 신설 | (TEST) | `from harness.tracker import MUTATING_SUBCOMMANDS; assert "create-issue" in MUTATING_SUBCOMMANDS` |
| REQ-003 | `hooks/harness_common.py` 에 `_load_engineer_scope` / `auto_gc_stale_flag` / `_verify_live_json_writable` 헬퍼 신설 + `_STATIC_ENGINEER_SCOPE` 상수 | (TEST) | 4 케이스 unit test: V2 off → static / V2 on + config 7 패턴 / V2 on + 빈 리스트 → static / V2 on + config invalid → static |
| REQ-004 | `hooks/agent-boundary.py` engineer 활성 시 `_load_engineer_scope()` 위임 | (TEST) | `HARNESS_GUARD_V2_AGENT_BOUNDARY=1` + config `services/api/src/` 추가 → `services/api/src/foo.ts` 통과 |
| REQ-005 | agent-boundary v1 회귀 0 — `HARNESS_GUARD_V2_AGENT_BOUNDARY` unset 시 ALLOW_MATRIX 정적 동등 | (TEST) | unset 상태 7 패턴 매치 결과가 PR #14 이전과 동일 |
| REQ-006 | `hooks/commit-gate.py` `_matches_tracker_mutate` 가 `MUTATING_SUBCOMMANDS` 위임 | (TEST) | `MUTATING_SUBCOMMANDS = {"create-issue", "comment", "update-issue"}` 강제 후 `harness.tracker update-issue` 매치 확인 |
| REQ-007 | commit-gate Gate 5 `_has_engineer_change` 가 engineer_scope 동적 + regex invalid 시 `^src/` fallback | (TEST) | invalid regex `(unbalanced` 주입 → stderr 경고 + `src/foo.ts` 매치 정상 |
| REQ-008 | `hooks/agent-gate.py` `flag()` 가 HARNESS_ACTIVE + V2 활성 시 age check 적용 | (TEST) | flag mtime 7h 전 → V2 on 시 auto-GC + False 반환, V2 off 시 True 반환 (회귀 0) |
| REQ-009 | agent-gate `_has_tracking_id` 가 `parse_ref` 위임 + ImportError 시 v1 regex fallback | (TEST) | `#42`, `LOCAL-7`, `42`, `Issue 42 description` 4 변형 모두 v2 통과 |
| REQ-010 | `hooks/skill-gate.py` set_active_skill 실패 시 V2 활성 stderr 경고 + jsonl 로그 + silent pass 유지 | (TEST) | live.json 디렉토리 권한 0o000 → V2 on stderr 경고 출력 / V2 off silent / 어느 경우든 sys.exit(0) |
| REQ-011 | `hooks/skill-stop-protect.py` `_log_event` 가 `guard`/`result` setdefault 추가 (backward-compat) | (TEST) | 기존 호출자 dict 변경 없이 jsonl 출력에 새 key 포함 확인 |
| REQ-012 | `hooks/ralph-session-stop.py` `_is_ralph_initiator` 3-layer fallback — V2 off 시 1차만 / V2 on 시 1→2→3차 / 모든 폴백 fail 시 False | (TEST) | 5 시나리오: 정상 ralph / 비-ralph V2 off / 5번째 위험 발현 + env match / 5번째 위험 + jsonl claim_self / 모든 fail |
| REQ-013 | ralph fallback false-positive 차단 — env match 시 skill-gate.jsonl corroboration 검증 | (TEST) | env 임의 export + 비-ralph 세션 + skill-gate log 부재 → `fallback_env_match_uncorroborated` 기록 + False 반환 |
| REQ-014 | `harness/executor.py` 진입 시 live.json round-trip canary 검증 — 실패 시 ESCALATE + sys.exit(1) | (TEST) | 디렉토리 권한 0o000 mock → executor.py 진입 즉시 ESCALATE 출력 + exit 1 |
| REQ-015 | `harness/executor.py` `write_lease()` 가 HARNESS_ACTIVE flag mtime touch (heartbeat) | (TEST) | 15초 wait 후 flag mtime 갱신 확인 — 6h TTL false-GC 방지 |
| REQ-016 | 통합 회귀 — 모든 V2 flag unset 상태에서 본 ralph-loop 환경 (5번째 위험 발현) 정상 차단 동작 (placeholder 박는 v1 경로) | (TEST) | live.json.skill 없음 + V2 off → placeholder 박힘 (현행 동작 100% 동등) |
| REQ-017 | jajang 모노레포 fixture 통과 — `apps/api/src/foo.py` engineer 통과 + commit Gate 5 LGTM 검사 발동 | (BROWSER:DOM) | (Iter 3 W5) jajang fixture 에서 V2 on 시 monorepo 시나리오 정상 |
| REQ-018 | 신규 V2 환경변수 8개 (`HARNESS_GUARD_V2_*`) 모두 setup-rwh.sh 에 export 분기 존재 | (MANUAL) | setup-rwh.sh 검토 — Stage 4 default ALL=1 시점 확정. 자동화 불가 이유: 사용자 환경 export shell 스크립트 검증은 외부 셸 컨텍스트 의존. |
