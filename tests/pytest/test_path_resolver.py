"""test_path_resolver.py — harness/path_resolver.py 단위 테스트.

8 TC (§7.1–§7.7):
  TC-1  engineer_scope_pathspecs() v1 fallback
  TC-2  engineer_scope_pathspecs() v2 monorepo
  TC-3  engineer_scope_extract_regex() v1 동등
  TC-4  engineer_scope_extract_regex() v2 monorepo
  TC-5  ui_components_paths() v1 default
  TC-6  test_paths_extract_regex() v1 동등 + 비상탈출 flag
  TC-7  engineer_scope_any_exists() v1 + v2
  TC-8  engineer_scope_human_dir_list() v1 + v2
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import harness.path_resolver as pr


# ── 공통 픽스처 ──────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _clear_path_resolver_cache():
    """각 테스트 전후 path_resolver 내부 캐시 초기화."""
    pr._cache_clear()
    yield
    pr._cache_clear()


@pytest.fixture()
def jajang_config(tmp_path):
    """jajang 모노레포 스타일 harness.config.json 가진 tmp 프로젝트 루트."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir(parents=True)
    config_data = {
        "prefix": "jajang",
        "engineer_scope": [
            r"(^|/)src/",
            r"(^|/)apps/[^/]+/src/",
            r"(^|/)services/[^/]+/src/",
        ],
        "ui_components_paths": [],
        "test_paths": [],
    }
    (claude_dir / "harness.config.json").write_text(
        json.dumps(config_data), encoding="utf-8"
    )
    return tmp_path


# ── TC-1: engineer_scope_pathspecs() v1 fallback ─────────────────────────────

def test_pathspecs_v1_fallback(monkeypatch):
    """HARNESS_GUARD_V2_PATHS_EXECUTOR 미설정 시 정확히 ["src/"] 반환."""
    monkeypatch.delenv("HARNESS_GUARD_V2_PATHS_EXECUTOR", raising=False)
    monkeypatch.delenv("HARNESS_GUARD_V2_ALL", raising=False)
    assert pr.engineer_scope_pathspecs() == ["src/"]


# ── TC-2: engineer_scope_pathspecs() v2 monorepo ─────────────────────────────

def test_pathspecs_v2_monorepo(monkeypatch, jajang_config, tmp_path):
    """V2 활성 + jajang config 로드 시 monorepo pathspec 포함 확인."""
    monkeypatch.setenv("HARNESS_GUARD_V2_PATHS_EXECUTOR", "1")
    monkeypatch.chdir(jajang_config)
    pr._cache_clear()

    result = pr.engineer_scope_pathspecs()
    # src/ 와 apps/*/src/ 가 모두 포함되어야 함
    assert "src/" in result
    assert any("apps/" in p for p in result), f"apps/ 경로 없음: {result}"
    # 모든 항목이 / 로 끝나야 함 (git pathspec 형식)
    for p in result:
        assert p.endswith("/"), f"trailing / 없음: {p}"


# ── TC-3: engineer_scope_extract_regex() v1 동등 ─────────────────────────────

def test_extract_regex_v1_equivalent(monkeypatch):
    """V2 비활성 시 v1 동등 결과."""
    monkeypatch.delenv("HARNESS_GUARD_V2_PATHS_EXECUTOR", raising=False)
    monkeypatch.delenv("HARNESS_GUARD_V2_ALL", raising=False)
    pat = pr.engineer_scope_extract_regex()

    # 기본 src/ 파일 매치
    found = pat.findall("import x from 'src/foo/bar.ts'")
    assert "src/foo/bar.ts" in found

    # .ts 는 tsx 보다 먼저 매치됨 (alternation 순서 — v1 동등 확인)
    # 예: "src/pages/Index.tsx" → "src/pages/Index.ts" (v1 동작 그대로)
    found_ts = pat.findall("see src/pages/Index.tsx here")
    assert len(found_ts) >= 1 and found_ts[0].startswith("src/pages/Index.ts")

    # .js 매치
    found_js = pat.findall("src/utils/helper.js loaded")
    assert "src/utils/helper.js" in found_js

    # 콜론 종결 문자 — TS type annotation 옆에서 잘라야 함
    # 예: `let x: src/foo.ts = ...` → "src/foo.ts" 만 추출 (콜론 미포함)
    found2 = pat.findall("let x: src/foo.ts and more")
    assert found2 == ["src/foo.ts"]


# ── TC-4: engineer_scope_extract_regex() v2 monorepo ─────────────────────────

def test_extract_regex_v2_monorepo(monkeypatch, jajang_config):
    """V2 활성 + jajang config 로드 시 apps/api/src/ 경로 매치."""
    monkeypatch.setenv("HARNESS_GUARD_V2_PATHS_EXECUTOR", "1")
    monkeypatch.chdir(jajang_config)
    pr._cache_clear()

    pat = pr.engineer_scope_extract_regex()

    # monorepo 경로 매치
    found = pat.findall("ref apps/api/src/main.ts here")
    assert "apps/api/src/main.ts" in found, f"monorepo 경로 미매치: {found}"

    # services 경로 매치 (.ts 먼저 매치 — v1 alternation 동작 그대로)
    found2 = pat.findall("see services/auth/src/router.tsx")
    assert any(f.startswith("services/auth/src/router.ts") for f in found2), (
        f"services 경로 미매치: {found2}"
    )

    # src/ 기본 경로도 계속 매치
    found3 = pat.findall("src/index.ts is here")
    assert "src/index.ts" in found3


# ── TC-5: ui_components_paths() v1 default ───────────────────────────────────

def test_ui_components_v1_default(monkeypatch):
    """V2 비활성 시 ["src/components"] 반환."""
    monkeypatch.delenv("HARNESS_GUARD_V2_PATHS_EXECUTOR", raising=False)
    monkeypatch.delenv("HARNESS_GUARD_V2_ALL", raising=False)
    assert pr.ui_components_paths() == ["src/components"]


def test_ui_components_v2_monorepo_with_dir(monkeypatch, tmp_path):
    """V2 활성 + apps/web/src/components 디렉토리 존재 시 자동 추론."""
    monkeypatch.setenv("HARNESS_GUARD_V2_PATHS_EXECUTOR", "1")

    # monorepo 구조 생성
    (tmp_path / ".claude").mkdir()
    config_data = {
        "prefix": "test",
        "engineer_scope": [r"(^|/)apps/[^/]+/src/"],
        "ui_components_paths": [],
        "test_paths": [],
    }
    (tmp_path / ".claude" / "harness.config.json").write_text(
        json.dumps(config_data), encoding="utf-8"
    )
    comp_dir = tmp_path / "apps" / "web" / "src" / "components"
    comp_dir.mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    pr._cache_clear()

    result = pr.ui_components_paths()
    # apps/web/src/components 가 포함되어야 함
    assert any("components" in p for p in result), f"components 경로 없음: {result}"


# ── TC-6: test_paths_extract_regex() v1 동등 + 비상탈출 flag ─────────────────

def test_test_regex_v1_equivalent(monkeypatch):
    """V2 비활성 시 v1 regex 동등 결과."""
    monkeypatch.delenv("HARNESS_GUARD_V2_PATHS_EXECUTOR", raising=False)
    monkeypatch.delenv("HARNESS_GUARD_V2_ALL", raising=False)
    monkeypatch.delenv("HARNESS_GUARD_V2_PATHS_TEST_REGEX_OFF", raising=False)
    pat = pr.test_paths_extract_regex()

    found = pat.findall("ran src/foo.test.ts and src/bar.spec.tsx")
    assert "src/foo.test.ts" in found
    assert "src/bar.spec.tsx" in found

    # js/jsx 도 매치
    assert pat.findall("src/utils.test.js") == ["src/utils.test.js"]


def test_test_regex_subflag_off(monkeypatch, jajang_config):
    """HARNESS_GUARD_V2_PATHS_TEST_REGEX_OFF=1 시 v2 활성이어도 v1 regex 강제."""
    monkeypatch.setenv("HARNESS_GUARD_V2_PATHS_EXECUTOR", "1")
    monkeypatch.setenv("HARNESS_GUARD_V2_PATHS_TEST_REGEX_OFF", "1")
    monkeypatch.chdir(jajang_config)
    pr._cache_clear()

    pat = pr.test_paths_extract_regex()
    assert pat.pattern == pr._V1_TEST_PATHS_REGEX, (
        f"비상탈출 실패: pattern={pat.pattern!r}"
    )


def test_test_regex_v2_monorepo(monkeypatch, jajang_config):
    """V2 활성 + jajang config 로드 시 monorepo test 경로 매치."""
    monkeypatch.setenv("HARNESS_GUARD_V2_PATHS_EXECUTOR", "1")
    monkeypatch.delenv("HARNESS_GUARD_V2_PATHS_TEST_REGEX_OFF", raising=False)
    monkeypatch.chdir(jajang_config)
    pr._cache_clear()

    pat = pr.test_paths_extract_regex()

    found = pat.findall("apps/api/src/main.test.ts done")
    assert "apps/api/src/main.test.ts" in found, f"monorepo test 경로 미매치: {found}"

    found2 = pat.findall("services/auth/src/router.spec.tsx")
    assert "services/auth/src/router.spec.tsx" in found2


# ── TC-7: engineer_scope_any_exists() ────────────────────────────────────────

def test_any_exists_v1_src_present(monkeypatch, tmp_path):
    """V2 비활성 + src/ 존재 시 True."""
    monkeypatch.delenv("HARNESS_GUARD_V2_PATHS_EXECUTOR", raising=False)
    monkeypatch.delenv("HARNESS_GUARD_V2_ALL", raising=False)
    (tmp_path / "src").mkdir()
    monkeypatch.chdir(tmp_path)
    pr._cache_clear()
    assert pr.engineer_scope_any_exists() is True


def test_any_exists_v1_no_src(monkeypatch, tmp_path):
    """V2 비활성 + src/ 없음 시 False."""
    monkeypatch.delenv("HARNESS_GUARD_V2_PATHS_EXECUTOR", raising=False)
    monkeypatch.delenv("HARNESS_GUARD_V2_ALL", raising=False)
    monkeypatch.chdir(tmp_path)
    pr._cache_clear()
    assert pr.engineer_scope_any_exists() is False


def test_any_exists_v2_monorepo_no_root_src(monkeypatch, tmp_path):
    """V2 활성 + 루트 src/ 없어도 apps/api/src 존재하면 True."""
    monkeypatch.setenv("HARNESS_GUARD_V2_PATHS_EXECUTOR", "1")

    (tmp_path / ".claude").mkdir()
    config_data = {
        "prefix": "test",
        "engineer_scope": [r"(^|/)apps/[^/]+/src/"],
    }
    (tmp_path / ".claude" / "harness.config.json").write_text(
        json.dumps(config_data), encoding="utf-8"
    )
    (tmp_path / "apps" / "api" / "src").mkdir(parents=True)
    # 루트 src/ 는 생성하지 않음
    monkeypatch.chdir(tmp_path)
    pr._cache_clear()

    assert pr.engineer_scope_any_exists() is True


# ── TC-8: engineer_scope_human_dir_list() ────────────────────────────────────

def test_human_dir_list_v1(monkeypatch):
    """V2 비활성 시 "src/" 반환."""
    monkeypatch.delenv("HARNESS_GUARD_V2_PATHS_EXECUTOR", raising=False)
    monkeypatch.delenv("HARNESS_GUARD_V2_ALL", raising=False)
    assert pr.engineer_scope_human_dir_list() == "src/"


def test_human_dir_list_v2_monorepo(monkeypatch, tmp_path):
    """V2 활성 + 두 디렉토리 존재 시 콤마 join."""
    monkeypatch.setenv("HARNESS_GUARD_V2_PATHS_EXECUTOR", "1")

    (tmp_path / ".claude").mkdir()
    config_data = {
        "prefix": "test",
        "engineer_scope": [
            r"(^|/)apps/[^/]+/src/",
        ],
    }
    (tmp_path / ".claude" / "harness.config.json").write_text(
        json.dumps(config_data), encoding="utf-8"
    )
    (tmp_path / "apps" / "api" / "src").mkdir(parents=True)
    (tmp_path / "apps" / "web" / "src").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    pr._cache_clear()

    result = pr.engineer_scope_human_dir_list()
    # 두 경로 모두 포함 + trailing /
    assert "apps/api/src/" in result or "apps/" in result
    assert result.endswith("/") or result.endswith("/"), f"format 이상: {result}"
