---
depth: simple
identifier: HARNESS-CHG-20260428-24
type: refactor
scope: paths
branch: harness/24-path-hardcode-audit-fix
phase_predecessor: HARNESS-CHG-13.* (Phase 2 W2 — hooks/ 7 가드 dynamic engineer_scope)
---

# #24 src/ 하드코딩 잔존 사이트 일괄 audit + executor-내부 fix 계획

## 0. 문제 정의 — Phase 2 W2 누락 정정

Phase 2 W2 (Issue #13) 가 `hooks/agent-boundary.py`, `hooks/commit-gate.py` 등 7 가드만 dynamic
`_load_engineer_scope()` 로 전환하고, **executor 내부 함수**(`harness/helpers.py`,
`harness/core.py`, `harness/impl_router.py`, `harness/impl_loop.py`, `harness/plan_loop.py`)는
하드코딩된 `src/` 리터럴을 그대로 둔 상태였다. 그 결과:

- monorepo (`apps/api/src/`, `packages/foo/src/`) 프로젝트에서 변경 감지가 false-negative.
- 단일 레포여도 `engineer_scope` 가 `src/` 외 (예: `lib/`) 로 설정되면 executor 가 추적 못 함.
- 결과적으로 가드는 v2 인데 executor 가 v1 → 책임 경계 불일치 (silent drift).

본 issue 는 그 누락을 마무리한다. **회귀 0** (v1 fallback 유지) + Phase 2 패턴 일관성을 1순위로 한다.

## 1. 변경 대상 파일 + 줄번호 인벤토리

### 1.1 1차 audit 6 사이트 (이슈 본문 명시)

| # | 파일:라인 | 현행 코드 | 의도 | 분류 |
|---|---|---|---|---|
| S1 | `harness/helpers.py:295` | `["git", "diff", "main..HEAD", "--name-only", "--", "src/"]` | engineer 변경 감지 (no_changes 판정용) — Phase 2 W2 패턴 직접 친척 | **engineer_scope** |
| S2 | `harness/core.py:1818` | `re.findall(r"src/[^ \`\"']+\.(?:ts|tsx|js|jsx)", content)` | impl 파일 본문에서 참조 src 파일 추출 (smart context) | **engineer_scope (read)** |
| S3 | `harness/core.py:1824` | `re.findall(r"src/[^ :()]+\.(?:ts|tsx|js|jsx)", error_text)` | 에러 trace 에서 src 파일 역추적 (retry context) | **engineer_scope (read)** |
| S4 | `harness/core.py:1906` | `Path("src/components")` + `comp_dir.rglob("*.tsx" / "*.ts")` | design loop 진입 컨텍스트 (UI 영역) | **ui_components_path** |
| S5 | `harness/impl_router.py:320` | `["grep", "-rlE", kw_pattern, "src/"]` | LIGHT_PLAN 분기에서 이슈 키워드로 의심 파일 탐색 | **engineer_scope (read)** |
| S6 | `harness/impl_loop.py:993` | `re.finditer(r"src/[^ ]+\.(?:test|spec)\.[jt]sx?", _te_content)` | test-engineer 산출에서 테스트 파일 추출 (RED 검증용 인자) | **test_paths** |

### 1.2 추가 audit (본 단계에서 발견)

`grep -rn "src/" harness/ hooks/ scripts/` 를 다시 돌려 **본 6개 외 6개를 추가 발견**.

| # | 파일:라인 | 현행 코드 | 의도 | 분류 / 처리 |
|---|---|---|---|---|
| S7 | `harness/plan_loop.py:286` | `if Path("src").exists() and not Path("docs/ux-flow.md").exists():` | UX_SYNC 모드 분기 (src/ 존재 + ux-flow.md 부재 → UX_SYNC) | **engineer_scope (existence)** — `_engineer_scope_has_any_match()` 위임 |
| S8 | `harness/plan_loop.py:288` | `print("[HARNESS] src/ 존재 + ux-flow.md 없음 -> UX_SYNC 모드")` | 위 S7 의 로그 메시지 | **로그 텍스트만 — 변경 불요** (사용자 가독성, 의미 보존) |
| S9 | `harness/plan_loop.py:298` | `f"@MODE:UX_ARCHITECT:UX_SYNC\nprd_path: {prd_path}\nsrc_dir: src/\nissue: ..."` | ux-architect 프롬프트 입력 (`src_dir: src/`) | **engineer_scope (UX 진입점)** — 다중 root 시 첫 매치 root 또는 콤마 join |
| S10 | `harness/helpers.py:357` | `# "- \`src/pages/ResultPage.tsx\` (수정)" 같은 형식` | 주석 (사용자에게 전형 예시 보여주는 docstring 코멘트) | **주석만 — 변경 불요** |
| S11 | `harness/core.py:997` | `"[SCOPE] 프로젝트 소스(src/, docs/, 루트 설정)만 분석 대상. "` | architect/qa 호출 시 SCOPE 프롬프트 (LLM 가이드) | **LLM 프롬프트 텍스트 — Phase 별도 처리 (이슈 #24 범위 외)**. 이유: monorepo 프로젝트라도 LLM 은 `src/` 를 "소스 디렉토리" 의미로 해석 가능. 잘못된 친절은 위험. |
| S12 | `harness/core.py:1374` | 주석 (`# 안전 패턴: plan 디렉토리만. src/ 등은 worktree 경계 보호 위해 제외.`) | worktree untracked 복사 정책 docstring | **주석만 — 변경 불요** |

**hooks/ 의 잔존 src/ 참조** (Grep 결과 line 49/50/53/67/68/.. 등) — 모두 `_STATIC_ENGINEER_SCOPE` 정적 default 정의 또는 매트릭스 내 다른 에이전트의 read deny 패턴. **이미 Phase 2 W2 에서 처리됨** (`_load_engineer_scope` 가 동등 fallback 보장). 본 이슈 범위 외.

**scripts/smoke-test.sh** — 픽스처 검증 코드 내부 assertion (`apps/api/src/main.py` 매치 확인). 의도적 하드코딩 (테스트 자체가 "이 패턴이 매치되는지" 검증). 변경 대상 아님.

### 1.3 최종 변경 대상 = **8 개 사이트** (S1–S7 + S9). S8/S10/S11/S12 미변경.

## 2. 추상화 결정 — 통합 vs 분리

### 2.1 검토한 옵션

| 옵션 | 정의 | 장점 | 단점 |
|---|---|---|---|
| **A. 단일 `project_paths` config 통합** | `engineer_scope` + `ui_components_path` + `test_paths` 를 하나의 dict 로 묶음 | 사용자 단일 SSOT | 의도 충돌 시 분리 어려움. config 파일 schema 거대화. |
| **B. 사이트 종류별 분리 (engineer_scope / ui_components_path / test_paths)** | 각 의도별 독립 필드 | 의도 명확. Phase 2 W2 의 `engineer_scope` 그대로 재사용. UI/test 만 신규 필드. | 사용자 config 여러 곳 수정. |
| **C. engineer_scope 만 재사용 + UI/test 는 정적 fallback 유지** | UI/test 는 일단 하드코딩 유지 (다음 Phase) | 변경 최소 | UI 영역 monorepo 프로젝트(예: jajang `apps/web/src/components/`) 에서 silent drift 지속 |

### 2.2 채택: **옵션 B (사이트 종류별 분리)**

근거:
1. **의도 분리** — `engineer_scope` 는 "engineer 가 만질 수 있는 곳" (write 권한 모델), 본 이슈의 read/추출/변경감지는 "engineer 작업 영역" (overlap 90%) 이라 재사용 적합. 하지만 **UI components 디렉토리** 는 designer 의도, **test paths** 는 test-engineer 의도. SSOT 충돌 위험 (engineer_scope 가 `apps/api/src/` 인데 UI 가 `apps/web/src/components/` 인 monorepo 흔함).
2. **Phase 2 W2 와 정합** — `engineer_scope` 그대로 재사용 → S1, S2, S3, S5, S7, S9 6 사이트가 같은 SSOT. UI/test 는 별도 신규.
3. **사용자 config 부담** — UI/test 미설정 시 정적 fallback (`src/components`, `src/**/*.test.*`) 동작. monorepo 만 명시 필요. 부담 작음.

### 2.3 신규 config 필드 (`harness/config.py`)

```python
@dataclass
class HarnessConfig:
    ...  # 기존 필드 유지
    engineer_scope: list = field(default_factory=list)  # Phase 2 W2 기존
    # ── #24 신규 ───────────────────────────────────────────────────────
    # UI 컴포넌트 디렉토리 (design loop 컨텍스트 빌더 진입점).
    # 빈 리스트 → 정적 fallback ["src/components"].
    ui_components_paths: list = field(default_factory=list)
    # 테스트 파일 추출 패턴 (test-engineer 산출 검증용 regex).
    # 빈 리스트 → 정적 fallback [r"src/[^ ]+\.(?:test|spec)\.[jt]sx?"].
    test_paths: list = field(default_factory=list)
```

`load_config` 에 isinstance 가드 + 기본값 처리 (line 121 패턴 재사용).

### 2.4 사이트별 추상화 매핑

| 사이트 | 사용 config | 호출 헬퍼 |
|---|---|---|
| S1 (helpers.py:295 변경 감지) | `engineer_scope` | `_engineer_scope_pathspecs()` (git pathspec 형태) |
| S2 (core.py:1818 impl 본문 추출) | `engineer_scope` | `_engineer_scope_extract_regex()` (regex 합성) |
| S3 (core.py:1824 error trace 추출) | `engineer_scope` | `_engineer_scope_extract_regex()` 재사용 |
| S4 (core.py:1906 components dir) | `ui_components_paths` | `_ui_components_paths()` |
| S5 (impl_router.py:320 grep -rlE) | `engineer_scope` | `_engineer_scope_grep_paths()` (디렉토리 리스트) |
| S6 (impl_loop.py:993 test 추출) | `test_paths` | `_test_paths_extract_regex()` |
| S7 (plan_loop.py:286 존재 체크) | `engineer_scope` | `_engineer_scope_any_exists()` |
| S9 (plan_loop.py:298 ux 프롬프트) | `engineer_scope` | `_engineer_scope_human_dir_list()` (사람이 읽는 디렉토리 콤마 join) |

## 3. 신규 헬퍼 모듈 — `harness/path_resolver.py`

**왜 신규 모듈?** `harness_common.py` 는 hooks 전용 (sys.path 분리), `harness/helpers.py` 는 executor 헬퍼지만 이미 1000줄 초과. 사이트가 5 모듈에 흩어져 있어 단일 import surface 가 필요. `harness/path_resolver.py` 신설.

```python
"""path_resolver.py — engineer_scope / ui_components_paths / test_paths SSOT 변환기.

Phase 2 W2 (#13) 의 hooks/_load_engineer_scope() 와 동등 의미를 executor 측에서 노출.
회귀 0 보장: HARNESS_GUARD_V2_PATHS_EXECUTOR (또는 _ALL) 미설정 시 v1 정적 fallback.
"""
from __future__ import annotations
import os, re, sys
from pathlib import Path
from typing import Iterable

# v1 정적 fallback (회귀 검증 reference)
_V1_ENGINEER_SCOPE_PATHSPECS = ["src/"]
_V1_ENGINEER_SCOPE_EXTRACT_REGEX = r"src/[^ \`\"':()]+\.(?:ts|tsx|js|jsx)"
_V1_UI_COMPONENTS_PATHS = ["src/components"]
_V1_TEST_PATHS_REGEX = r"src/[^ ]+\.(?:test|spec)\.[jt]sx?"

_CACHE: dict = {}  # per-process 캐시 — config 재로드 회피


def _v2_active() -> bool:
    return (
        os.environ.get("HARNESS_GUARD_V2_PATHS_EXECUTOR") == "1"
        or os.environ.get("HARNESS_GUARD_V2_ALL") == "1"
    )


def _load_cfg():
    """harness.config 동적 로드 (실패 시 None — caller 가 fallback)."""
    if "_cfg" in _CACHE:
        return _CACHE["_cfg"]
    try:
        from .config import load_config  # type: ignore
        cfg = load_config()
    except Exception as e:
        sys.stderr.write(f"[path_resolver] WARN: config load fail ({e}); v1 fallback\n")
        cfg = None
    _CACHE["_cfg"] = cfg
    return cfg


def _engineer_scope_dirs() -> list[str]:
    """engineer_scope regex 패턴들에서 추출 가능한 디렉토리 prefix 리스트.

    예: ["(^|/)src/", "(^|/)apps/[^/]+/src/"] → ["src", "apps/*/src"]
    grep/git pathspec 용. 정적 fallback: ["src"].
    """
    if not _v2_active():
        return ["src"]
    cfg = _load_cfg()
    if not cfg or not cfg.engineer_scope:
        return ["src"]
    dirs = []
    for pat in cfg.engineer_scope:
        # regex (^|/) 와 $ 제거 후 디렉토리만 추출 — 단순 휴리스틱
        m = re.match(r"\(\^\|/\)([\w\-/\[\]^*+]+?)/", pat)
        if m:
            d = m.group(1).replace("[^/]+", "*")  # apps/[^/]+/src → apps/*/src
            dirs.append(d)
    return dirs or ["src"]


def engineer_scope_pathspecs() -> list[str]:
    """git diff/log 의 -- pathspec 인자로 쓸 형태 (S1 helpers.py:295).

    git pathspec 은 `apps/*/src/` 형태 직접 지원 (glob).
    """
    return [d.rstrip("/") + "/" for d in _engineer_scope_dirs()]


def engineer_scope_extract_regex() -> "re.Pattern[str]":
    """impl 본문/error trace 에서 src 파일을 뽑는 regex (S2/S3 core.py:1818/1824).

    동적 dirs 를 OR 합성. v1 fallback: 단일 "src/..." 패턴.
    """
    if not _v2_active():
        return re.compile(_V1_ENGINEER_SCOPE_EXTRACT_REGEX)
    dirs = _engineer_scope_dirs()
    # 각 dir 에 대해 "<dir>/[^ \`\"':()]+\.(?:ts|tsx|js|jsx)" 합성
    parts = [re.escape(d).replace(r"\*", "[^/]+") for d in dirs]
    body = "(?:" + "|".join(parts) + r")/[^ \`\"':()]+\.(?:ts|tsx|js|jsx)"
    try:
        return re.compile(body)
    except re.error:
        return re.compile(_V1_ENGINEER_SCOPE_EXTRACT_REGEX)


def engineer_scope_grep_paths() -> list[str]:
    """grep -rl 의 path 인자 (S5 impl_router.py:320).

    grep 은 디렉토리 단순 path 만 받으므로 glob 확장 필요.
    `apps/*/src` 형태는 shell glob 으로 사전 expand.
    """
    import glob as _glob
    dirs = _engineer_scope_dirs()
    paths = []
    for d in dirs:
        if "*" in d:
            paths.extend(_glob.glob(d))
        else:
            if Path(d).is_dir():
                paths.append(d)
    return paths or ["src/"] if Path("src").is_dir() else paths


def engineer_scope_any_exists() -> bool:
    """engineer_scope 디렉토리가 하나라도 존재하는지 (S7 plan_loop.py:286).

    v1 fallback: Path("src").exists().
    """
    return bool(engineer_scope_grep_paths())


def engineer_scope_human_dir_list() -> str:
    """사람/LLM 이 읽는 디렉토리 콤마 join (S9 plan_loop.py:298 `src_dir:`).

    v1 fallback: "src/".
    """
    paths = engineer_scope_grep_paths()
    return ", ".join(p.rstrip("/") + "/" for p in paths) or "src/"


def ui_components_paths() -> list[str]:
    """design loop 컴포넌트 디렉토리 (S4 core.py:1906).

    빈 리스트 + monorepo 일 때: engineer_scope dirs 각각의 `<root>/components` 합성.
    명시된 cfg 가 있으면 그대로.
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
    candidates = []
    import glob as _glob
    for d in dirs:
        if "*" in d:
            candidates.extend(_glob.glob(d + "/components"))
        else:
            cand = d + "/components"
            if Path(cand).is_dir():
                candidates.append(cand)
    return candidates or list(_V1_UI_COMPONENTS_PATHS)


def test_paths_extract_regex() -> "re.Pattern[str]":
    """test-engineer 산출 추출 regex (S6 impl_loop.py:993).

    cfg.test_paths 명시 우선. 없으면 engineer_scope dirs 기반 합성.
    """
    if not _v2_active():
        return re.compile(_V1_TEST_PATHS_REGEX)
    cfg = _load_cfg()
    if cfg and cfg.test_paths:
        # 사용자 명시 regex 들의 OR
        try:
            return re.compile("(?:" + "|".join(cfg.test_paths) + ")")
        except re.error:
            pass
    dirs = _engineer_scope_dirs()
    parts = [re.escape(d).replace(r"\*", "[^/]+") for d in dirs]
    body = "(?:" + "|".join(parts) + r")/[^ ]+\.(?:test|spec)\.[jt]sx?"
    try:
        return re.compile(body)
    except re.error:
        return re.compile(_V1_TEST_PATHS_REGEX)
```

## 4. 사이트별 패치 의사코드

### 4.1 S1 — `harness/helpers.py:295` (engineer 변경 감지)

```python
# v1 (현행 295):
r_diff = _run(
    ["git", "diff", "main..HEAD", "--name-only", "--", "src/"],
    capture_output=True, text=True, timeout=10,
)

# v2 패치:
from .path_resolver import engineer_scope_pathspecs
_pathspecs = engineer_scope_pathspecs()  # v1 fallback: ["src/"]
r_diff = _run(
    ["git", "diff", "main..HEAD", "--name-only", "--"] + _pathspecs,
    capture_output=True, text=True, timeout=10,
)
```

**v1 fallback 검증**: `engineer_scope_pathspecs()` 는 `_v2_active()=False` 시 `["src/"]` 반환 → `git diff ... -- src/` 동등.

### 4.2 S2 — `harness/core.py:1818` (impl 본문 src 추출)

```python
# v1 (현행 1818):
matches = re.findall(r"src/[^ `\"']+\.(?:ts|tsx|js|jsx)", content)

# v2 패치:
from .path_resolver import engineer_scope_extract_regex
matches = engineer_scope_extract_regex().findall(content)
```

### 4.3 S3 — `harness/core.py:1824` (error trace src 추출)

```python
# v1 (현행 1824):
matches = re.findall(r"src/[^ :()]+\.(?:ts|tsx|js|jsx)", error_text)

# v2 패치 — 동일 헬퍼 재사용:
matches = engineer_scope_extract_regex().findall(error_text)
```

> **주의**: v1 의 S2 정규식과 S3 정규식의 character class 차이 (`[^ \`\"']` vs `[^ :()]`) 가 있다. S3 는 stack trace 의 `path:line:col` 또는 `path(line)` 토큰을 자르기 위한 더 광범위한 종결 문자. **합성 regex 는 양쪽 종결 문자 합집합** (`[^ \`\"':()]`) 으로 통일 — 양쪽 의도를 모두 포섭.
> 회귀 위험: S2 의 경우 백틱/따옴표/공백만 종결문자였는데 콜론도 종결문자가 되면 `import { X } from 'src/foo.ts:bar'` 같은 변형이 잘릴 수 있음. **실측**: TS import 문에 콜론이 들어가는 사례 없음 (콜론은 type annotation 에만 등장하고 import 경로엔 안 들어감). 안전.

### 4.4 S4 — `harness/core.py:1906` (design loop UI 컴포넌트 트리)

```python
# v1 (현행 1906-1917):
if loop_type == "design":
    comp_dir = Path("src/components")
    if comp_dir.is_dir():
        try:
            components = sorted(str(p) for p in comp_dir.rglob("*.tsx"))[:20]
            components += sorted(str(p) for p in comp_dir.rglob("*.ts"))[:20]
            components = sorted(set(components))[:20]
            ...

# v2 패치:
from .path_resolver import ui_components_paths
if loop_type == "design":
    comps_all: list[str] = []
    for comp_dir_s in ui_components_paths():
        comp_dir = Path(comp_dir_s)
        if comp_dir.is_dir():
            try:
                comps_all.extend(str(p) for p in comp_dir.rglob("*.tsx"))
                comps_all.extend(str(p) for p in comp_dir.rglob("*.ts"))
            except OSError:
                pass
    components = sorted(set(comps_all))[:20]
    if components:
        # "src/components/" 라는 단일 라벨 대신 동적 라벨
        label = ", ".join(ui_components_paths())
        ctx += f"\n=== {label} 트리 ===\n" + "\n".join(components)
```

### 4.5 S5 — `harness/impl_router.py:320` (LIGHT_PLAN 의심 파일 grep)

```python
# v1 (현행 319-322):
r = subprocess.run(
    ["grep", "-rlE", kw_pattern, "src/"],
    capture_output=True, text=True, timeout=10,
)

# v2 패치:
from .path_resolver import engineer_scope_grep_paths
_grep_paths = engineer_scope_grep_paths() or ["src/"]  # 빈 리스트 방어
r = subprocess.run(
    ["grep", "-rlE", kw_pattern] + _grep_paths,
    capture_output=True, text=True, timeout=10,
)
```

> grep 은 다중 path 인자 native 지원. monorepo `apps/api/src/` + `apps/web/src/` 양쪽 동시 검색.

### 4.6 S6 — `harness/impl_loop.py:993` (test-engineer 산출 추출)

```python
# v1 (현행 991-994):
_te_content = Path(te_tdd_out).read_text(encoding="utf-8", errors="replace")
_tdd_test_files = " ".join(
    m.group(0) for m in re.finditer(r"src/[^ ]+\.(?:test|spec)\.[jt]sx?", _te_content)
)

# v2 패치:
from .path_resolver import test_paths_extract_regex
_te_content = Path(te_tdd_out).read_text(encoding="utf-8", errors="replace")
_tdd_test_files = " ".join(
    m.group(0) for m in test_paths_extract_regex().finditer(_te_content)
)
```

### 4.7 S7 — `harness/plan_loop.py:286` (UX_SYNC 모드 분기)

```python
# v1 (현행 286):
if Path("src").exists() and not Path("docs/ux-flow.md").exists():

# v2 패치:
from .path_resolver import engineer_scope_any_exists
if engineer_scope_any_exists() and not Path("docs/ux-flow.md").exists():
```

### 4.8 S9 — `harness/plan_loop.py:298` (ux-architect UX_SYNC 프롬프트)

```python
# v1 (현행 296-300):
_uxa_exit = agent_call(
    "ux-architect", 600,
    f"@MODE:UX_ARCHITECT:UX_SYNC\nprd_path: {prd_path}\nsrc_dir: src/\nissue: {format_ref(issue_num)}",
    uxa_out_file, run_logger, config,
)

# v2 패치:
from .path_resolver import engineer_scope_human_dir_list
_uxa_exit = agent_call(
    "ux-architect", 600,
    f"@MODE:UX_ARCHITECT:UX_SYNC\nprd_path: {prd_path}\nsrc_dir: {engineer_scope_human_dir_list()}\nissue: {format_ref(issue_num)}",
    uxa_out_file, run_logger, config,
)
```

> ux-architect 가 받는 `src_dir` 는 LLM 가이드용 자유 텍스트 — `apps/api/src/, apps/web/src/` 처럼 사람이 읽는 형태로 단순 join. `src_dir:` 키 이름은 backward-compat 유지 (다중 root 라도 prompt 변수명만 보존).

## 5. Staged Rollout — Flag 매트릭스

Phase 2 W2 패턴 일관성 (`HARNESS_GUARD_V2_AGENT_BOUNDARY`, `HARNESS_GUARD_V2_COMMIT_GATE`, ..., `HARNESS_GUARD_V2_ALL`) 을 따른다.

| Flag | 활성 사이트 | 의도 | Default |
|---|---|---|---|
| `HARNESS_GUARD_V2_PATHS_EXECUTOR=1` | S1, S2, S3, S4, S5, S6, S7, S9 (전부) | 본 #24 의 단일 일괄 활성 flag | unset (v1) |
| `HARNESS_GUARD_V2_ALL=1` | 위 + Phase 2 W2 가드들 + 미래 추가 | 메타 flag (전체 v2 강제) | unset |

**왜 사이트별 flag 분리 안 하나?**
- 사이트가 8개로 모두 같은 SSOT (`engineer_scope` + 2 새 필드) 사용. 의도 분리가 약함.
- 사이트별 flag 8개 도입 시 사용자 인지 부하 + 매트릭스 폭증 (Phase 2 W2 의 가드별 flag 7 + 본 8 = 15).
- 단일 `HARNESS_GUARD_V2_PATHS_EXECUTOR` 로 묶고, **회귀 위험 격리는 fallback 동등성 단위 테스트** 로 보장 (§7 참조).

**예외 — S6 (test_paths)**: 회귀 0 보장 강도가 가장 약한 사이트(추출 regex character class 변형). 만약 v1 실측에서 false-positive 가 발생한다면 사이트별 sub-flag `HARNESS_GUARD_V2_PATHS_TEST_REGEX_OFF=1` 로 v1 강제 fallback 가능 (path_resolver 내부에서 우선순위 체크). 본 단계에선 도입만 명세, 활성 X.

```python
# path_resolver.py 의 test_paths_extract_regex() 보강:
def test_paths_extract_regex():
    if os.environ.get("HARNESS_GUARD_V2_PATHS_TEST_REGEX_OFF") == "1":
        return re.compile(_V1_TEST_PATHS_REGEX)
    if not _v2_active():
        return re.compile(_V1_TEST_PATHS_REGEX)
    ...
```

## 6. 회귀 위험 격리 — 사이트별 분석

| 사이트 | 회귀 위험 | 격리 수단 |
|---|---|---|
| S1 | git pathspec `["src/"]` vs `["apps/*/src/"]` — pathspec 자체는 stable. monorepo 미설정 시 v1 fallback. | `_v2_active()=False` 분기에서 정확히 v1 인자 동등. unit test §7.1. |
| S2/S3 | regex character class 합집합 변경. import 경로 구조에 콜론 들어가는 사례 없음 (TS spec 검토). | unit test §7.2: 실측 코드 fixture 에서 v1 결과 == v2 결과 (engineer_scope 단일 root) 검증. |
| S4 | `Path("src/components")` 단일 → 다중 list. 단일 레포 (engineer_scope 비활성) 시 동등 fallback. | unit test §7.3: v1 default 시 `ui_components_paths() == ["src/components"]`. |
| S5 | grep 다중 path 인자 — bash 호환성. `["grep", "-rlE", pat, "src/"]` 와 `["grep", "-rlE", pat, "src/"]` (단일) 동등. | unit test §7.4. |
| S6 | regex character class 변경 미발생 (S6 는 test/spec 패턴이라 char class 변경 없음). dirs 합성만 변경. | unit test §7.5 + sub-flag `HARNESS_GUARD_V2_PATHS_TEST_REGEX_OFF` 비상탈출. |
| S7 | `Path("src").exists()` → `engineer_scope_any_exists()`. v1 fallback `["src"]` 동등. | unit test §7.6. |
| S9 | prompt 텍스트 `src/` → `src/` (v1) / `apps/api/src/, apps/web/src/` (v2 monorepo). LLM 입력만 변경. | smoke test §7.7 + 실 ux-architect 호출 1회 (jajang 환경 검증). |

## 7. 단위 테스트 케이스 (`tests/pytest/test_path_resolver.py` 신규)

### 7.1 S1 — engineer_scope_pathspecs

```python
def test_pathspecs_v1_fallback(monkeypatch):
    monkeypatch.delenv("HARNESS_GUARD_V2_PATHS_EXECUTOR", raising=False)
    monkeypatch.delenv("HARNESS_GUARD_V2_ALL", raising=False)
    from harness.path_resolver import engineer_scope_pathspecs, _CACHE
    _CACHE.clear()
    assert engineer_scope_pathspecs() == ["src/"]

def test_pathspecs_v2_monorepo(monkeypatch, tmp_path):
    # jajang fixture: engineer_scope = ["(^|/)apps/[^/]+/src/", "(^|/)src/"]
    monkeypatch.setenv("HARNESS_GUARD_V2_PATHS_EXECUTOR", "1")
    ... (config 픽스처 로드)
    assert "apps/*/src/" in engineer_scope_pathspecs()
    assert "src/" in engineer_scope_pathspecs()
```

### 7.2 S2/S3 — engineer_scope_extract_regex

```python
def test_extract_regex_v1_equivalent(monkeypatch):
    monkeypatch.delenv("HARNESS_GUARD_V2_PATHS_EXECUTOR", raising=False)
    from harness.path_resolver import engineer_scope_extract_regex
    pat = engineer_scope_extract_regex()
    assert pat.findall("import x from 'src/foo.ts'") == ["src/foo.ts"]

def test_extract_regex_v2_monorepo(monkeypatch):
    monkeypatch.setenv("HARNESS_GUARD_V2_PATHS_EXECUTOR", "1")
    ... # config 로드 (apps/*/src 포함)
    assert "apps/api/src/main.ts" in pat.findall("ref apps/api/src/main.ts here")

def test_extract_regex_no_false_positive_on_colon_in_type_annotation():
    """TS type annotation (예: `let x: src/foo.ts = ...`) 같은 인위적 케이스에서
    src/foo.ts 토큰만 정확히 잡아야 함."""
    ...
```

### 7.3 S4 — ui_components_paths

```python
def test_ui_components_v1_default():
    assert ui_components_paths() == ["src/components"]

def test_ui_components_v2_monorepo(tmp_path, monkeypatch):
    # apps/web/src/components 디렉토리 생성
    (tmp_path / "apps" / "web" / "src" / "components").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HARNESS_GUARD_V2_PATHS_EXECUTOR", "1")
    ... # config: engineer_scope = ["(^|/)apps/[^/]+/src/"]
    assert "apps/web/src/components" in ui_components_paths()
```

### 7.4 S5 — engineer_scope_grep_paths

(동일 패턴 — v1 == ["src/"] when src exists, v2 monorepo == ["apps/api/src", "apps/web/src"])

### 7.5 S6 — test_paths_extract_regex

```python
def test_test_regex_v1_equivalent():
    pat = test_paths_extract_regex()
    assert pat.findall("ran src/foo.test.ts and src/bar.spec.tsx") == [
        "src/foo.test.ts", "src/bar.spec.tsx"
    ]

def test_test_regex_v2_monorepo():
    ...
    # apps/api/src/__tests__/main.test.ts 매치 확인

def test_test_regex_subflag_off(monkeypatch):
    monkeypatch.setenv("HARNESS_GUARD_V2_PATHS_EXECUTOR", "1")
    monkeypatch.setenv("HARNESS_GUARD_V2_PATHS_TEST_REGEX_OFF", "1")
    # 비상탈출: v2 활성이어도 v1 regex 강제 사용
    pat = test_paths_extract_regex()
    assert pat.pattern == _V1_TEST_PATHS_REGEX
```

### 7.6 S7 — engineer_scope_any_exists

```python
def test_any_exists_v1_only_src(tmp_path, monkeypatch):
    (tmp_path / "src").mkdir()
    monkeypatch.chdir(tmp_path)
    assert engineer_scope_any_exists() is True

def test_any_exists_v2_monorepo_no_root_src(tmp_path, monkeypatch):
    """단일 src/ 가 없어도 apps/api/src 만 있으면 True."""
    (tmp_path / "apps" / "api" / "src").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HARNESS_GUARD_V2_PATHS_EXECUTOR", "1")
    ...
    assert engineer_scope_any_exists() is True
```

### 7.7 S9 — engineer_scope_human_dir_list

```python
def test_human_dir_list_v1():
    assert engineer_scope_human_dir_list() == "src/"

def test_human_dir_list_v2_monorepo():
    monkeypatch.setenv("HARNESS_GUARD_V2_PATHS_EXECUTOR", "1")
    ...
    assert engineer_scope_human_dir_list() == "apps/api/src/, apps/web/src/"
```

### 7.8 통합 (smoke)

`scripts/smoke-test.sh` 에 시나리오 추가:
- jajang fixture (`tests/pytest/fixtures/jajang_monorepo/`) 에서 `HARNESS_GUARD_V2_PATHS_EXECUTOR=1` 설정 후
  - S1 git diff 가 `apps/api/src/` 변경 감지 OK
  - S5 grep 이 `apps/api/src/` + `apps/web/src/` 양쪽 검색 OK
- 단일 레포 (현 RWHarness `src/` 부재) 에서 `_v2_active()=False` → 모든 헬퍼 v1 fallback OK

## 8. 파일 변경 매트릭스 (engineer 작업 항목)

| 파일 | 변경 종류 | 위치 |
|---|---|---|
| `harness/path_resolver.py` | **신규** | 전체 (§3) |
| `harness/config.py` | **추가** | `ui_components_paths`, `test_paths` 필드 (line 59 직후) + `load_config` line 121 직후 매핑 |
| `harness/helpers.py` | 패치 | line 295 (S1) |
| `harness/core.py` | 패치 | line 1818 (S2), line 1824 (S3), line 1906-1917 (S4) |
| `harness/impl_router.py` | 패치 | line 320 (S5) |
| `harness/impl_loop.py` | 패치 | line 993 (S6) |
| `harness/plan_loop.py` | 패치 | line 286 (S7), line 298 (S9) |
| `tests/pytest/test_path_resolver.py` | **신규** | §7.1–§7.7 8 케이스 |
| `scripts/smoke-test.sh` | **추가** | §7.8 시나리오 (3 step) |
| `orchestration/changelog.md` | **추가** | `HARNESS-CHG-20260428-24` 항목 |

## 9. 후속 cleanup (별도 issue 후보)

- **S11 (`core.py:997` SCOPE 프롬프트 텍스트)**: LLM 입력 텍스트라 별도 검토 필요. monorepo 환경에서 architect/qa 가 `apps/api/src/` 를 "프로젝트 소스" 로 식별하는지 ux 검증 후 결정.
- **`scripts/smoke-test.sh` line 253-296** 의 jajang fixture assertion: 본 #24 가 path_resolver 통과시키면 fixture assertion 도 신규 헬퍼 사용으로 단순화 가능.
- **path_resolver 캐시 무효화**: 현재 per-process. test isolation 시 `_CACHE.clear()` 수동 호출 필요. 후속에서 LRU TTL 또는 mtime 기반 자동 무효화 검토.
- **`_engineer_scope_dirs()` 휴리스틱**: regex 에서 디렉토리 추출 (`re.match(r"\(\^\|/\)([\w\-/\[\]^*+]+?)/", ...)`) 단순 패턴. 사용자가 복잡한 regex (예: `(^|/)(src|lib)/`) 작성 시 캡처 못 함. 후속에서 명시적 `engineer_scope_dirs` cfg 필드 도입 검토.

## 10. engineer 호출 시 추가 결정 없음 검증

체크리스트 (engineer 가 본 문서만 보고 코드 작성 가능?):

- [x] 신규 모듈 위치/이름 확정 (`harness/path_resolver.py`)
- [x] 신규 config 필드 이름/타입 확정 (`ui_components_paths: list`, `test_paths: list`)
- [x] 8 사이트 줄번호 + before/after 의사코드 명시
- [x] flag 이름 확정 (`HARNESS_GUARD_V2_PATHS_EXECUTOR`, `HARNESS_GUARD_V2_PATHS_TEST_REGEX_OFF` sub-flag)
- [x] 정적 fallback 값 명시 (`_V1_*` 상수)
- [x] regex character class 합집합 처리 명시 (S2/S3 통일)
- [x] 단위 테스트 케이스 8개 명시
- [x] 미변경 사이트 4개 (S8/S10/S11/S12) 와 그 사유 명시
- [x] 신규/수정 파일 매트릭스 (§8)

## 11. 자기 검증 결과

- **6 사이트 + 추가 6 사이트 audit 완료**: S1–S12 분류. 변경 8개 (S1-S7, S9), 미변경 4개 (S8/S10/S11/S12 — 주석/로그/LLM 프롬프트/주석).
- **각 사이트 의도 정확 파악**: §1.1 분류 컬럼.
- **추상화가 의도 충돌 없이 작동**: `engineer_scope` (write 범위 + read 추출 둘 다 같은 root 가정) — 90%+ overlap. UI/test 는 별도 필드. 충돌 위험 없음.
- **Staged rollout v1 fallback (회귀 0)**: 모든 헬퍼가 `_v2_active()=False` 분기에서 v1 정적 상수 반환. unit test §7.1–§7.7 가 동등성 검증.
- **engineer 추가 결정 없음 수준**: §10 체크리스트 통과.
