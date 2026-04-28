---
depth: simple
identifier: HARNESS-CHG-20260428-19
type: bugfix
scope: light_plan
---

# #19 session_id 글로벌 폴백 — dogfooding 환경 silent malfunction 차단

## 변경 대상

- 파일: `hooks/session_state.py`
- 함수: `current_session_id()` (line 90-97)
- 요약: 프로젝트 pointer 부재 시 `~/.claude/harness-state/.session-id`를 추가 폴백으로 시도하되, **신선도·자기참조 검증**으로 cross-session contamination 방어. RWHarness 같은 dogfooding 환경(화이트리스트 미등록 → SessionStart 훅이 sys.exit(0) → 프로젝트 pointer 미생성)에서 `core.py:980` `update_live(sid, agent=…)` 호출이 빈 sid 때문에 무성공 stub 처리되는 silent malfunction을 차단한다.

## 원인 분석 (architect 검증)

본 RWHarness 환경 측정:
- `HARNESS_SESSION_ID` env: unset (메인 Claude는 자기 env 못 바꿈)
- `/Users/dc.kim/project/RWHarness/.claude/harness-state/.session-id`: **부재** (RWHarness가 화이트리스트에 없어 SessionStart 훅이 일찍 종료)
- `~/.claude/harness-state/.session-id`: **존재** (`~/.claude` 자체가 화이트리스트에 등록되어 있어 home 모드 SessionStart로 작성됨)

```
호출 체인:
  executor.py:85       session_id = ss.current_session_id()       → ""
  → executor.py:87     os.environ["HARNESS_SESSION_ID"] = …        → 안 함
  → core.py:980        _ss.current_session_id()                    → ""
  → core.py:982        if sid: _ss.update_live(...) [skipped]      → live.json.agent 갱신 X
  → hooks(agent-boundary 등) live.json.agent 못 읽음                → 활성 에이전트 판별 실패
  ⇒ 메인 Claude 직접 작업이 agent 작업으로 오인되거나 그 반대로 false-block
```

## 옵션 비교 (architect 검토)

| 옵션 | 변경 범위 | 회귀 리스크 | RWHarness 해결 | 외부 사용자 영향 |
|---|---|---|---|---|
| A: `current_session_id()` 글로벌 폴백 + 가드 | session_state.py 1함수 | 폴백 가드 통과 시만 활성. 정상 환경 영향 0 | ✅ | ✅ (env/프로젝트 pointer 우선순위 보존) |
| B: executor 부팅 시 글로벌→프로젝트 복사 | executor.py | hook 직접 호출 미해결 | ⚠️ 일부 | ⚠️ |
| C: SessionStart hook이 env export | 메인 Claude env 못 바꿈 | dead end | ❌ | ❌ |
| D: RWHarness를 화이트리스트에 추가 | 코드 0 | 1회성 환경 셋업, 배포 불가 | ✅ | dogfooding 인스턴스마다 반복 |
| E: executor `--session-id` CLI arg | 호출자 광범위 수정 | 큼 | ✅ | 큼 |

**선택: 옵션 A + 신선도/자기참조 가드.** 가장 가벼움 + 외부 환경 영향 0 + cross-contamination 방어.

## 수정 내용

`hooks/session_state.py` `current_session_id()` 변경:

```python
# 글로벌 pointer 폴백의 신선도 가드 — leftover sid 오용 방지.
# live.json._meta.written_at 이 이 값보다 오래되면 다른 세션의 leftover로 간주.
_GLOBAL_FALLBACK_FRESHNESS_SEC = 6 * 60 * 60  # 6h = DEFAULT_SESSION_TTL_SEC와 일관

def current_session_id(project_root: Optional[Path] = None) -> str:
    """현재 세션 ID 우선순위:
      1) HARNESS_SESSION_ID env (executor 부팅 시 set; 가장 권위 있음)
      2) 프로젝트 .session-id 파일 (SessionStart 훅이 작성)
      3) 글로벌 ~/.claude/harness-state/.session-id (폴백) — 단, 다음 가드 모두 통과해야 채택:
         a) sid 형식 유효
         b) ~/.claude/harness-state/.sessions/{sid}/live.json 존재
         c) live.json._meta.sessionId == sid (자기참조 — 다른 세션 덮어쓰기 거부)
         d) live.json._meta.written_at 이 6h 이내 (stale leftover 거부)
      가드 실패 시 빈 문자열 — v1 동작 유지(회귀 0).
    """
    sid = os.environ.get("HARNESS_SESSION_ID", "")
    if valid_session_id(sid):
        return sid
    sid = read_session_pointer(project_root)
    if sid:
        return sid
    # 글로벌 폴백
    return _read_global_session_pointer_safely()


def _read_global_session_pointer_safely() -> str:
    """글로벌 ~/.claude pointer 폴백 — 모든 가드 통과 시에만 sid 반환."""
    try:
        home_root = Path.home() / ".claude" / "harness-state"
        pointer = home_root / ".session-id"
        if not pointer.exists():
            return ""
        sid = pointer.read_text(encoding="utf-8").strip()
        if not valid_session_id(sid):
            return ""
        live = home_root / ".sessions" / sid / "live.json"
        if not live.exists():
            return ""
        data = read_json(live)
        if not isinstance(data, dict):
            return ""
        meta = data.get("_meta") if isinstance(data.get("_meta"), dict) else {}
        if meta.get("sessionId") != sid:
            return ""  # 자기참조 실패 — 다른 세션 leftover
        written_at = int(meta.get("written_at", 0) or 0)
        if not written_at or (time.time() - written_at) > _GLOBAL_FALLBACK_FRESHNESS_SEC:
            return ""  # stale leftover
        return sid
    except (OSError, ValueError):
        return ""
```

추가 위치:
- `_GLOBAL_FALLBACK_FRESHNESS_SEC` 상수 — line 49(`STDIN_TIMEOUT_SEC` 아래)에 추가.
- `_read_global_session_pointer_safely()` — `current_session_id()` 바로 뒤(line 98)에 추가.
- `current_session_id()` body 교체 — line 90-97.

## 회귀 위험 격리

1. **env 우선순위 보존**: `HARNESS_SESSION_ID` env 있으면 즉시 반환 (변경 없음).
2. **프로젝트 pointer 우선순위 보존**: 두 번째 분기 `read_session_pointer()` 그대로 (변경 없음).
3. **폴백 실패 시 빈 문자열**: 모든 가드(파일 존재/형식/자기참조/신선도) 실패 시 v1과 동일하게 `""` 반환 → 호출자(`core.py:980`)가 `if sid:` 분기로 안전하게 skip.
4. **모든 try/except**: `OSError`/`ValueError`/JSON 파싱 실패는 `""`로 흡수.

## 보안 분석 — cross-session contamination

| 시나리오 | 결과 |
|---|---|
| RWHarness dogfooding (현재) — 글로벌 pointer = 현재 세션 sid, live.json 신선 | ✅ 폴백 활성, 정상 동작 |
| 다른 사용자 일반 환경 (jajang 등) — 프로젝트 pointer 존재 | ✅ 폴백 미발동 (2번 분기에서 종결) |
| 한 머신에 두 Claude Code 인스턴스 동시 실행 — 글로벌 pointer가 최근 세션의 것 | ⚠️ 자기참조 가드 통과 + 6h 이내 → 잘못된 sid 채택 가능. **단 이 경우 두 세션 sid가 모두 신선하므로 후순위 인스턴스도 SessionStart로 자기 글로벌 pointer 덮어쓰기 → race window 짧음.** |
| 어제 세션의 leftover pointer | ✅ written_at 6h 초과 → 거부 |
| 다른 세션이 같은 글로벌 sid 슬롯에 덮어쓰기 (이론) | ✅ 자기참조 검증 (`_meta.sessionId == sid`) 통과 못 함 → 거부 |

> 다중 인스턴스 race는 **현재 v1도 동일 문제** (`~/.claude/harness-state/.session-id`가 단일 슬롯). 본 fix는 race window를 추가로 만들지 않는다.

## staged rollout 판단

**Immediate fix.** 이유:
- 변경 범위 1함수 + 1헬퍼.
- 회귀 리스크 0 (모든 폴백 가드는 enrichment, 기존 경로 보존).
- staged rollout 인프라는 동작 변경(behavior change)이 외부 환경에 영향 줄 때 의미 있음. 본 fix는 외부 환경에서 폴백이 발동하지 않으므로 staged 의미 없음.

## 수용 기준

| 요구사항 ID | 내용 | 검증 방법 | 통과 조건 |
|---|---|---|---|
| REQ-001 | RWHarness dogfooding cwd에서 `current_session_id()`가 신선한 글로벌 sid 반환 | (TEST) `pytest tests/test_session_state_fallback.py::test_global_fallback_fresh_pointer` | live.json `_meta.written_at` = now, `_meta.sessionId == sid` 일 때 sid 반환 |
| REQ-002 | stale 글로벌 pointer (written_at 6h 초과) 거부 | (TEST) `pytest tests/test_session_state_fallback.py::test_global_fallback_stale_rejected` | 빈 문자열 반환 |
| REQ-003 | 자기참조 실패(`_meta.sessionId != sid`) 거부 | (TEST) `pytest tests/test_session_state_fallback.py::test_global_fallback_meta_mismatch_rejected` | 빈 문자열 반환 |
| REQ-004 | 환경 우선순위 (env > project > global) 보존 | (TEST) `pytest tests/test_session_state_fallback.py::test_priority_order_preserved` | env set 시 env 값, env unset+project pointer 시 project 값 |
| REQ-005 | 글로벌 pointer 부재 시 `""` 반환 (회귀 0) | (TEST) `pytest tests/test_session_state_fallback.py::test_no_pointer_returns_empty` | 빈 문자열 반환 |

## 관련 테스트 파일

- 신규: `tests/test_session_state_fallback.py` (없으면 생성).
- **변경 동작을 assert하는 기존 테스트 없음** — `current_session_id()` 단위 테스트가 미존재. engineer는 위 5개 케이스를 신규 작성 + scope에 포함.

## 수정 파일 목록 (engineer 강제 scope)

- `hooks/session_state.py` — 본문 변경
- `tests/test_session_state_fallback.py` — 신규 (5 TC)
- `orchestration/changelog.md` — `HARNESS-CHG-20260428-19` 항목 추가

## 다음 단계 (engineer 위임 컨텍스트)

1. engineer 호출 시 위 "수정 파일 목록" 그대로 scope.
2. `tests/test_session_state_fallback.py`는 monkeypatch + `tmp_path`로 `~/.claude` 격리 (`monkeypatch.setattr(Path, "home", lambda: tmp_path)`).
3. validator 통과 후 PR 본문에 본 impl 파일 링크 + RWHarness dogfooding 측정값(env/pointer 상태) 포함.
4. PR squash merge 후 RWHarness 세션 재시작 시 `core.py:980` 로그가 `[HARNESS] live.json.agent ← {agent}` 출력되는지 1회 dogfooding 검증.

<!-- Document-Exception: impl 계획 파일 단독 추가 — 동일 unit(HARNESS-CHG-20260428-19)의 코드와 changelog는 commit 109b076에 이미 포함됨. 중복 changelog 갱신 불필요. -->
