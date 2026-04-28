"""path_resolver.py — engineer_scope / ui_components_paths / test_paths SSOT 변환기.

Phase 2 W2 (#13) 의 hooks/_load_engineer_scope() 와 동등 의미를 executor 측에서 노출.
회귀 0 보장: HARNESS_GUARD_V2_PATHS_EXECUTOR (또는 _ALL) 미설정 시 v1 정적 fallback.

헬퍼 목록:
- engineer_scope_pathspecs()      — git diff/log 의 -- pathspec 인자 (S1)
- engineer_scope_extract_regex()  — impl/error trace 에서 src 파일 추출 regex (S2/S3)
- engineer_scope_grep_paths()     — grep -rl 의 path 인자 (S5)
- engineer_scope_any_exists()     — Path.exists() OR (S7)
- engineer_scope_human_dir_list() — 사람/LLM 용 콤마 join (S9)
- ui_components_paths()           — design loop 컴포넌트 디렉토리 (S4)
- test_paths_extract_regex()      — test-engineer 산출 추출 regex (S6)
"""
from __future__ import annotations

import glob as _glob_mod
import os
import re
import sys
from pathlib import Path
from typing import List

# v1 정적 fallback (회귀 검증 reference — 변경 금지)
_V1_ENGINEER_SCOPE_PATHSPECS: List[str] = ["src/"]
_V1_ENGINEER_SCOPE_EXTRACT_REGEX = r"src/[^ `\"':()]+\.(?:ts|tsx|js|jsx)"
_V1_UI_COMPONENTS_PATHS: List[str] = ["src/components"]
# V1 fallback test regex 보강 (G4 — pytest + jest/vitest 디렉토리 패턴 추가).
# 기존 `src/...\.test\.[jt]sx?` 를 첫 번째 OR 절로 유지하여 기존 호출자 호환.
# 이 regex 를 helpers._is_test_file() 이 재사용 (SSOT, G4 결정).
_V1_TEST_PATHS_REGEX = (
    r"src/[^ ]+\.(?:test|spec)\.[jt]sx?"          # 기존 (src/ 고정 — 호환성 유지)
    r"|(?:^|/)(?:tests|__tests__)/[^ ]+"           # /tests/ 또는 /__tests__/ 디렉토리
    r"|(?:^|/)test_[^/ ]+\.py"                     # test_*.py (pytest 표준)
    r"|[^ /]+_test\.py"                            # *_test.py (pytest 표준)
)

_CACHE: dict = {}  # per-process 캐시 — config 재로드 회피


def _cache_clear() -> None:
    """테스트 격리용 캐시 초기화."""
    _CACHE.clear()


def _v2_active() -> bool:
    """HARNESS_GUARD_V2_PATHS_EXECUTOR=1 또는 HARNESS_GUARD_V2_ALL=1 이면 V2 활성."""
    return (
        os.environ.get("HARNESS_GUARD_V2_PATHS_EXECUTOR") == "1"
        or os.environ.get("HARNESS_GUARD_V2_ALL") == "1"
    )


def _load_cfg():
    """harness.config 동적 로드 (실패 시 None — caller 가 fallback)."""
    cache_key = "_cfg"
    if cache_key in _CACHE:
        return _CACHE[cache_key]
    try:
        try:
            from .config import load_config  # type: ignore[import]
        except ImportError:
            from config import load_config  # type: ignore[import]
        cfg = load_config()
    except Exception as e:
        sys.stderr.write(f"[path_resolver] WARN: config load fail ({e}); v1 fallback\n")
        cfg = None
    _CACHE[cache_key] = cfg
    return cfg


def _engineer_scope_dirs() -> List[str]:
    """engineer_scope regex 패턴들에서 디렉토리 prefix 리스트 추출.

    예: ["(^|/)src/", "(^|/)apps/[^/]+/src/"] -> ["src", "apps/*/src"]
    grep/git pathspec 용. 정적 fallback: ["src"].
    """
    if not _v2_active():
        return ["src"]
    cfg = _load_cfg()
    if not cfg or not cfg.engineer_scope:
        return ["src"]
    dirs: List[str] = []
    for pat in cfg.engineer_scope:
        # regex (^|/) 와 $ 제거 후 디렉토리만 추출 — 단순 휴리스틱
        m = re.match(r"\(\^\|/\)([\w\-/\[\]^*+.]+?)/", pat)
        if m:
            d = m.group(1).replace("[^/]+", "*")  # apps/[^/]+/src -> apps/*/src
            dirs.append(d)
    return dirs or ["src"]


def engineer_scope_pathspecs() -> List[str]:
    """git diff/log 의 -- pathspec 인자로 쓸 형태 (S1 helpers.py:295).

    git pathspec 은 `apps/*/src/` 형태 직접 지원 (glob).
    v1 fallback: ["src/"]
    """
    if not _v2_active():
        return list(_V1_ENGINEER_SCOPE_PATHSPECS)
    return [d.rstrip("/") + "/" for d in _engineer_scope_dirs()]


def engineer_scope_extract_regex() -> "re.Pattern[str]":
    """impl 본문/error trace 에서 src 파일을 뽑는 regex (S2/S3 core.py:1818/1824).

    S2 vs S3 차이 (v1): S2 는 [^ `\"'] 종결, S3 는 [^ :()] 종결.
    합집합 [^ `\"':()] 로 통일 — TS import 경로에 콜론은 없으므로 안전.
    동적 dirs 를 OR 합성. v1 fallback: 단일 "src/..." 패턴.
    """
    if not _v2_active():
        return re.compile(_V1_ENGINEER_SCOPE_EXTRACT_REGEX)
    dirs = _engineer_scope_dirs()
    # 각 dir 에 대해 "<dir>/[^ `\"':()]+\.(?:ts|tsx|js|jsx)" 합성
    parts = [re.escape(d).replace(r"\*", "[^/]+") for d in dirs]
    body = "(?:" + "|".join(parts) + r")/[^ `\"':()]+\.(?:ts|tsx|js|jsx)"
    try:
        return re.compile(body)
    except re.error:
        sys.stderr.write(
            f"[path_resolver] WARN: extract_regex compile fail; v1 fallback\n"
        )
        return re.compile(_V1_ENGINEER_SCOPE_EXTRACT_REGEX)


def engineer_scope_grep_paths() -> List[str]:
    """grep -rl 의 path 인자 (S5 impl_router.py:320).

    grep 은 단순 디렉토리 path 를 인자로 받으므로, `apps/*/src` 형태는 shell glob 확장.
    v1 fallback: src/ 가 존재하면 ["src/"], 없으면 [].
    """
    if not _v2_active():
        return ["src/"] if Path("src").is_dir() else []
    dirs = _engineer_scope_dirs()
    paths: List[str] = []
    for d in dirs:
        if "*" in d:
            expanded = _glob_mod.glob(d)
            paths.extend(e for e in expanded if Path(e).is_dir())
        else:
            if Path(d).is_dir():
                paths.append(d)
    # 빈 리스트 방어 — v1 fallback
    if not paths and Path("src").is_dir():
        return ["src/"]
    return paths


def engineer_scope_any_exists() -> bool:
    """engineer_scope 디렉토리가 하나라도 존재하는지 (S7 plan_loop.py:286).

    v1 fallback: Path("src").exists().
    """
    if not _v2_active():
        return Path("src").exists()
    return bool(engineer_scope_grep_paths())


def engineer_scope_human_dir_list() -> str:
    """사람/LLM 이 읽는 디렉토리 콤마 join (S9 plan_loop.py:298 `src_dir:`).

    v1 fallback: "src/".
    """
    if not _v2_active():
        return "src/"
    paths = engineer_scope_grep_paths()
    if not paths:
        return "src/"
    return ", ".join(p.rstrip("/") + "/" for p in paths)


def ui_components_paths() -> List[str]:
    """design loop 컴포넌트 디렉토리 (S4 core.py:1906).

    cfg.ui_components_paths 명시 우선.
    미설정 + monorepo: engineer_scope dirs 각각의 `<root>/components` 자동 추론.
    v1 fallback: ["src/components"].
    """
    if not _v2_active():
        return list(_V1_UI_COMPONENTS_PATHS)
    cfg = _load_cfg()
    if cfg and cfg.ui_components_paths:
        return list(cfg.ui_components_paths)
    # 폴백: engineer_scope dirs 의 `<dir>/components` 합성 (monorepo 자동 추론)
    dirs = _engineer_scope_dirs()
    if dirs == ["src"]:
        return list(_V1_UI_COMPONENTS_PATHS)
    candidates: List[str] = []
    for d in dirs:
        if "*" in d:
            candidates.extend(
                e for e in _glob_mod.glob(d + "/components") if Path(e).is_dir()
            )
        else:
            cand = d + "/components"
            if Path(cand).is_dir():
                candidates.append(cand)
    return candidates or list(_V1_UI_COMPONENTS_PATHS)


def test_paths_extract_regex() -> "re.Pattern[str]":
    """test-engineer 산출 추출 regex (S6 impl_loop.py:993).

    우선순위:
    1. HARNESS_GUARD_V2_PATHS_TEST_REGEX_OFF=1 → v1 강제 (비상탈출)
    2. V2 비활성 → v1 fallback
    3. cfg.test_paths 명시 → 사용자 지정 OR 합성
    4. engineer_scope dirs 기반 자동 합성
    """
    # 비상탈출 flag (S6 false-positive 방어)
    if os.environ.get("HARNESS_GUARD_V2_PATHS_TEST_REGEX_OFF") == "1":
        return re.compile(_V1_TEST_PATHS_REGEX)
    if not _v2_active():
        return re.compile(_V1_TEST_PATHS_REGEX)
    cfg = _load_cfg()
    if cfg and cfg.test_paths:
        # 사용자 명시 regex 들의 OR
        try:
            return re.compile("(?:" + "|".join(cfg.test_paths) + ")")
        except re.error:
            sys.stderr.write(
                "[path_resolver] WARN: test_paths regex compile fail; auto-synthesize\n"
            )
    dirs = _engineer_scope_dirs()
    parts = [re.escape(d).replace(r"\*", "[^/]+") for d in dirs]
    # V2 자동 합성: engineer_scope 기반 디렉토리 패턴
    scope_body = "(?:" + "|".join(parts) + r")/[^ ]+\.(?:test|spec)\.[jt]sx?"
    # V1 보강 패턴(pytest/jest 디렉토리)을 OR 로 합산 — scope 밖 tests/ 도 매칭
    body = scope_body + "|" + _V1_TEST_PATHS_REGEX
    try:
        return re.compile(body)
    except re.error:
        sys.stderr.write(
            "[path_resolver] WARN: test_paths_extract_regex compile fail; v1 fallback\n"
        )
        return re.compile(_V1_TEST_PATHS_REGEX)
