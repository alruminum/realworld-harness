"""
harness_common.py — 훅 공유 유틸리티
PREFIX 결정, deny 헬퍼, 플래그 상수, 마커 파싱 등 훅 간 공통 로직.
"""
import json
import os
import re
import sys


# ── 마커 포맷 (Single Source of Truth) ──
# 에이전트 출력 마커: ---MARKER:<NAME>---
MARKER_RE = re.compile(r'---MARKER:([A-Z_]+)---')


def parse_marker_text(text, allowed=None):
    """텍스트에서 구조화된 마커를 추출.
    allowed: 허용 마커 집합 (None이면 모든 마커 허용).
    반환: 첫 번째 매칭 마커 또는 None.
    """
    for m in MARKER_RE.finditer(text):
        name = m.group(1)
        if allowed is None or name in allowed:
            return name
    return None


# ── 플래그 이름 상수 ──
class FLAGS:
    HARNESS_ACTIVE = "harness_active"
    HARNESS_KILL = "harness_kill"
    PLAN_VALIDATION_PASSED = "plan_validation_passed"
    TEST_ENGINEER_PASSED = "test_engineer_passed"
    VALIDATOR_B_PASSED = "validator_b_passed"
    PR_REVIEWER_LGTM = "pr_reviewer_lgtm"
    SECURITY_REVIEW_PASSED = "security_review_passed"
    BUGFIX_VALIDATION_PASSED = "bugfix_validation_passed"
    LIGHT_PLAN_READY = "light_plan_ready"
    DESIGNER_RAN = "designer_ran"
    DESIGN_CRITIC_PASSED = "design_critic_passed"


# ── 에이전트 분류 상수 (Single Source of Truth) ──
# 훅에서 에이전트별 권한/제약을 판단할 때 이 상수만 참조한다.
# 변경 시 이 파일만 수정 → 모든 훅에 즉시 반영.

# 하네스(executor.sh) 경유 필수 에이전트 — 직접 Agent 호출 금지
HARNESS_ONLY_AGENTS = ("engineer",)

# Mode-level 게이트 — architect/validator는 Mode별로 직접 호출 허용 여부가 갈린다.
# 아래 집합의 Mode는 harness/executor.py 경유 필수 (impl_loop / plan_loop 내부에서 자동 호출).
# 나머지는 product-plan 스킬 6단계처럼 메인 Claude가 Agent 도구로 직접 호출 가능.
ARCHITECT_HARNESS_ONLY_MODES = frozenset({
    "MODULE_PLAN",   # impl 경로, plan_loop가 호출
    "SPEC_GAP",      # impl loop attempt 내부 복구
})
VALIDATOR_HARNESS_ONLY_MODES = frozenset({
    "PLAN_VALIDATION",     # plan_loop 내부
    "CODE_VALIDATION",     # impl_loop attempt 내부
    "BUGFIX_VALIDATION",   # bugfix/quick 경로
})

def detect_architect_mode(prompt):
    """architect 프롬프트에서 Mode 식별. 의미적 키워드만 인식.

    Why: 과거엔 `Mode A-G` 알파벳 표기도 인식했으나 알파벳은 의미 전달이 약하고
    신규 모드가 추가될 때마다 알파벳 재할당이 필요해 deprecate. 호출자는
    항상 SYSTEM_DESIGN / MODULE_PLAN / SPEC_GAP / TASK_DECOMPOSE / TECH_EPIC /
    LIGHT_PLAN / DOCS_SYNC 중 하나를 프롬프트에 명시해야 한다.
    """
    for m in ("SYSTEM_DESIGN", "MODULE_PLAN", "SPEC_GAP",
              "TASK_DECOMPOSE", "TECH_EPIC", "LIGHT_PLAN", "DOCS_SYNC"):
        if re.search(rf"\b{m}\b", prompt):
            return m
    return None


def detect_validator_mode(prompt):
    """validator 프롬프트에서 Mode 식별. 키워드 + 자연어 표현 모두 매치."""
    for m in ("DESIGN_VALIDATION", "PLAN_VALIDATION",
              "CODE_VALIDATION", "BUGFIX_VALIDATION"):
        if re.search(rf"\b{m}\b", prompt):
            return m
    for pat, mode in (
        (r"[Pp]lan[\s_-]*[Vv]alidation", "PLAN_VALIDATION"),
        (r"[Dd]esign[\s_-]*[Vv]alidation", "DESIGN_VALIDATION"),
        (r"[Cc]ode[\s_-]*[Vv]alidation", "CODE_VALIDATION"),
        (r"[Bb]ugfix[\s_-]*[Vv]alidation", "BUGFIX_VALIDATION"),
    ):
        if re.search(pat, prompt):
            return mode
    return None

# 이슈 생성 가능 에이전트 — issue-gate.py에서 harness_active 없이도 허용
ISSUE_CREATORS = ("qa", "designer", "architect", "product-planner")

# 이슈 번호 필수 에이전트 — 프롬프트에 #NNN 없으면 차단
ISSUE_REQUIRED_AGENTS = ("architect", "engineer")

# 하네스가 소유하는 커스텀 에이전트 화이트리스트 (Single Source of Truth).
# Claude Code 내장 서브에이전트(Explore, Plan, general-purpose, claude-code-guide,
# statusline-setup 등)는 이 집합 밖이며, 훅은 이들에 관여하지 않는다.
# - agent-gate.py: 이 집합 밖의 에이전트에는 {prefix}_{agent}_active 플래그를 만들지 않음.
# - agent-boundary.py: 이 집합 밖이면 active_agent로 인정하지 않고 메인 Claude와 동일 경로로 통과.
CUSTOM_AGENTS = frozenset({
    "architect",
    "engineer",
    "designer",
    "ux-architect",
    "validator",
    "pr-reviewer",
    "qa",
    "test-engineer",
    "security-reviewer",
    "design-critic",
    "product-planner",
})


_WHITELIST_PATH = os.path.expanduser("~/.claude/harness-projects.json")


def _load_whitelist():
    """`~/.claude/harness-projects.json`의 `projects` 경로 목록을 resolve된 형태로 반환."""
    try:
        with open(_WHITELIST_PATH) as f:
            data = json.load(f)
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return []
    projects = data.get("projects", [])
    out = []
    for p in projects:
        try:
            out.append(os.path.realpath(os.path.expanduser(p)))
        except Exception:
            continue
    return out


def is_harness_enabled(cwd=None):
    """현재 프로젝트(또는 주어진 cwd)가 하네스 화이트리스트에 등록됐는지 판정.

    Why: 하네스 훅은 전역(`~/.claude/hooks/*.py`)이라 모든 Claude Code 세션에서
    호출된다. 일반 프로젝트에서 훅이 오작동(Mode 경고·file-ownership 차단 등)하지
    않도록, `~/.claude/harness-projects.json`에 명시된 경로에서만 동작.

    - 기본값은 disabled — 화이트리스트 없거나 cwd가 목록 밖이면 False
    - 화이트리스트 경로의 서브디렉토리(worktree 포함)도 True로 판정
    - `HARNESS_FORCE_ENABLE=1` env var로 임시 활성 (디버깅용)
    """
    if os.environ.get("HARNESS_FORCE_ENABLE") == "1":
        return True
    try:
        here = os.path.realpath(cwd) if cwd else os.path.realpath(os.getcwd())
    except OSError:
        return False
    for root in _load_whitelist():
        if here == root or here.startswith(root + os.sep):
            return True
    return False


def get_prefix():
    """프로젝트별 prefix를 env → harness.config.json (상위 순환) → 디렉토리명 → "proj" 폴백으로 유도."""
    # 훅 서브프로세스에서는 HARNESS_PREFIX env var가 전파되지 않을 수 있음.
    # HARNESS_PREFIX 환경변수가 있으면 최우선 사용.
    env_prefix = os.environ.get('HARNESS_PREFIX')
    if env_prefix:
        return env_prefix
    # CWD가 프로젝트 하위 디렉토리이거나 ~./claude 등 엉뚱한 위치일 수 있으므로
    # 현재 디렉토리부터 루트까지 순환하며 .claude/harness.config.json 탐색.
    cwd = os.path.abspath(os.getcwd())
    while True:
        config_path = os.path.join(cwd, ".claude", "harness.config.json")
        if os.path.exists(config_path):
            try:
                prefix = json.load(open(config_path)).get("prefix")
                if prefix:
                    return prefix
            except Exception:
                pass
        parent = os.path.dirname(cwd)
        if parent == cwd:   # 파일시스템 루트 도달
            break
        cwd = parent
    raw = os.path.basename(os.getcwd()).lower()
    return re.sub(r'[^a-z0-9]', '', raw)[:8] or "proj"


def deny(reason):
    """PreToolUse 훅에서 도구 실행을 거부한다."""
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason
        }
    }))
    sys.exit(0)


def get_state_dir():
    """하네스 상태 디렉토리 반환. 프로젝트 .claude/harness-state/ 우선, 없으면 /tmp 폴백."""
    cwd = os.path.abspath(os.getcwd())
    while True:
        state_dir = os.path.join(cwd, ".claude", "harness-state")
        if os.path.isdir(state_dir):
            return state_dir
        # .claude 디렉토리만 있어도 harness-state 생성 가능한 프로젝트 루트
        claude_dir = os.path.join(cwd, ".claude")
        if os.path.isdir(claude_dir):
            os.makedirs(state_dir, exist_ok=True)
            return state_dir
        parent = os.path.dirname(cwd)
        if parent == cwd:
            break
        cwd = parent
    return "/tmp"


def get_flags_dir(issue_num=""):
    """플래그 전용 숨김 디렉토리 반환.
    Phase 3: 세션 스코프 `.sessions/{sid}/flags/{prefix}_{issue}/` 사용.
    session_id 없으면 레거시 `.flags/` 폴백 (전역 모드).
    HARNESS_ISSUE_NUM env var도 참조.
    """
    state_dir = get_state_dir()
    if not issue_num:
        issue_num = os.environ.get("HARNESS_ISSUE_NUM", "")
    prefix = get_prefix()
    # Phase 3: session_state 모듈이 있으면 세션 스코프 사용
    try:
        from session_state import session_flags_dir, current_session_id  # type: ignore
        sid = current_session_id()
        if sid:
            return str(session_flags_dir(sid, prefix, issue_num))
    except ImportError:
        pass
    # 폴백: 전역 .flags/
    if issue_num:
        flags_dir = os.path.join(state_dir, ".flags", f"{prefix}_{issue_num}")
    else:
        flags_dir = os.path.join(state_dir, ".flags")
    os.makedirs(flags_dir, exist_ok=True)
    return flags_dir


def get_active_agent(stdin_data=None):
    """현재 세션의 활성 에이전트 판별 (Phase 3: live.json 단일 소스).
    stdin_data가 있으면 훅 stdin session_id 기반.
    하위호환: session_state 모듈 없으면 HARNESS_AGENT_NAME env 폴백.
    """
    try:
        from session_state import active_agent  # type: ignore
        return active_agent(stdin_data=stdin_data)
    except ImportError:
        return os.environ.get("HARNESS_AGENT_NAME") or None


def flag_path(prefix, name):
    """플래그 파일 경로 반환."""
    return os.path.join(get_flags_dir(), f"{prefix}_{name}")


def flag_exists(prefix, name):
    """플래그 파일 존재 여부."""
    return os.path.exists(flag_path(prefix, name))


# ══════════════════════════════════════════════════════════════════════════════
# Phase 2 W2/W4 헬퍼 (HARNESS-CHG Issue #13 — Guard Model Realignment)
# ══════════════════════════════════════════════════════════════════════════════

# ── engineer_scope 로더 (agent-boundary + commit-gate 공유) ──────────────────
_ENGINEER_SCOPE_CACHE: "list[str] | None" = None  # per-process 캐시

# 정적 default — agent-boundary.ALLOW_MATRIX["engineer"] 와 동등.
# v1 동작 회귀 검증을 위해 본 리스트만으로 기존 매트릭스가 재현 가능해야 함.
_STATIC_ENGINEER_SCOPE: "list[str]" = [
    r'(^|/)src/',
    r'(^|/)apps/[^/]+/src/',
    r'(^|/)apps/[^/]+/app/',
    r'(^|/)apps/[^/]+/alembic/',
    r'(^|/)packages/[^/]+/src/',
    r'(^|/)apps/[^/]+/[^/]+\.toml$',
    r'(^|/)apps/[^/]+/[^/]+\.cfg$',
]


def _load_engineer_scope() -> "list[str]":
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
        if plugin_root and plugin_root not in sys.path:
            sys.path.insert(0, plugin_root)
        from harness.config import load_config  # type: ignore
        cfg = load_config()
        scope = list(cfg.engineer_scope) if cfg.engineer_scope else []
    except Exception as e:
        sys.stderr.write(
            f"[harness_common] WARN: engineer_scope config load failed ({e}); fallback static\n"
        )
        scope = []
    if not scope:
        scope = list(_STATIC_ENGINEER_SCOPE)
    _ENGINEER_SCOPE_CACHE = scope
    return _ENGINEER_SCOPE_CACHE


# ── auto_gc_stale_flag — skill-stop-protect 패턴 일반화 ─────────────────────
def auto_gc_stale_flag(flag_p: object, ttl_sec: int, label: str) -> bool:
    """flag mtime 기반 age check + auto-GC.

    Args:
      flag_p: pathlib.Path — flag 파일 경로
      ttl_sec: int — TTL (초). default 6h (21600).
      label: str — stderr/log 진단용 가드 이름 (e.g. "agent-gate")

    Returns: fresh 여부 (False 면 stale 또는 부재).
    skill-stop-protect 의 auto_release 패턴 일반화.
    """
    import time as _time
    from pathlib import Path as _Path
    flag_p = _Path(flag_p)
    if not flag_p.exists():
        return False
    try:
        age = _time.time() - flag_p.stat().st_mtime
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
                import session_state as _ss  # type: ignore
                log_dir = _ss.state_root() / ".logs"
                log_dir.mkdir(exist_ok=True)
                log_path = log_dir / f"{label}.jsonl"
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps({
                        "ts": int(_time.time()),
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


# ── live.json round-trip canary (executor.py 진입 시 호출) ──────────────────
def _verify_live_json_writable(session_id: str) -> "tuple[bool, str]":
    """live.json 쓰기 가능 여부 사전 검증. Returns (ok, error_msg).
    ok=False 면 caller 가 ESCALATE 결정. silent dependency cascade 사전 차단.
    """
    try:
        import time as _time
        import session_state as _ss  # type: ignore
        canary = int(_time.time())
        _ss.update_live(session_id, _harness_canary=canary)
        # readback 검증 — atomic_write_json 후 directory fsync 까지 검증
        live = _ss.get_live(session_id)
        if live.get("_harness_canary") != canary:
            return (False, f"canary mismatch: wrote {canary}, read {live.get('_harness_canary')}")
        _ss.clear_live_field(session_id, "_harness_canary")
        return (True, "")
    except Exception as e:
        return (False, f"{type(e).__name__}: {e}")
