"""
Issue #27 회귀 테스트: PR #25 path_resolver inline import 9 사이트
direct-execution 컨텍스트(no parent package)에서 ImportError 없이 통과하는지 검증.

검증 방식:
  subprocess로 `python3 -c "import sys; sys.path.insert(0, 'harness'); ..."` 실행
  → package 없이 절대 import 경로로 모듈을 로드하는 상황을 재현.
"""
import subprocess
import sys
import os
from pathlib import Path

# harness/ 디렉토리를 포함하는 프로젝트 루트
REPO_ROOT = Path(__file__).parent.parent.parent


def _run_direct(code: str) -> subprocess.CompletedProcess:
    """harness/ 를 sys.path에 삽입하고 코드를 직접 실행."""
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env={**os.environ, "PYTHONPATH": ""},  # 기존 PYTHONPATH 격리
    )


class TestDirectImportNoError:
    """각 사이트 함수를 직접 실행 컨텍스트에서 호출 — ImportError 0 기대."""

    def test_engineer_scope_extract_regex_in_extract_src_refs(self):
        """core.py:1818/1825 — extract_src_refs / extract_files_from_error"""
        code = (
            "import sys; sys.path.insert(0, 'harness'); "
            "import core; "
            "result = core.extract_src_refs('/etc/hosts'); "
            "print(repr(result))"
        )
        r = _run_direct(code)
        assert r.returncode == 0, f"ImportError 발생:\n{r.stderr}"
        assert "ImportError" not in r.stderr

    def test_engineer_scope_extract_regex_in_extract_files_from_error(self):
        """core.py:1825 — extract_files_from_error"""
        code = (
            "import sys; sys.path.insert(0, 'harness'); "
            "import core; "
            "result = core.extract_files_from_error('some error trace'); "
            "print(repr(result))"
        )
        r = _run_direct(code)
        assert r.returncode == 0, f"ImportError 발생:\n{r.stderr}"
        assert "ImportError" not in r.stderr

    def test_path_resolver_config_import(self):
        """path_resolver.py:52 — from .config import load_config"""
        code = (
            "import sys; sys.path.insert(0, 'harness'); "
            "import path_resolver; "
            "result = path_resolver.engineer_scope_pathspecs(); "
            "print(repr(result))"
        )
        r = _run_direct(code)
        assert r.returncode == 0, f"ImportError 발생:\n{r.stderr}"
        assert "ImportError" not in r.stderr

    def test_engineer_scope_grep_paths(self):
        """impl_router.py:319 — engineer_scope_grep_paths"""
        code = (
            "import sys; sys.path.insert(0, 'harness'); "
            "import path_resolver; "
            "result = path_resolver.engineer_scope_grep_paths(); "
            "print(repr(result))"
        )
        r = _run_direct(code)
        assert r.returncode == 0, f"ImportError 발생:\n{r.stderr}"
        assert "ImportError" not in r.stderr

    def test_engineer_scope_any_exists(self):
        """plan_loop.py:286 — engineer_scope_any_exists"""
        code = (
            "import sys; sys.path.insert(0, 'harness'); "
            "import path_resolver; "
            "result = path_resolver.engineer_scope_any_exists(); "
            "print(repr(result))"
        )
        r = _run_direct(code)
        assert r.returncode == 0, f"ImportError 발생:\n{r.stderr}"
        assert "ImportError" not in r.stderr

    def test_engineer_scope_human_dir_list(self):
        """plan_loop.py:297 — engineer_scope_human_dir_list"""
        code = (
            "import sys; sys.path.insert(0, 'harness'); "
            "import path_resolver; "
            "result = path_resolver.engineer_scope_human_dir_list(); "
            "print(repr(result))"
        )
        r = _run_direct(code)
        assert r.returncode == 0, f"ImportError 발생:\n{r.stderr}"
        assert "ImportError" not in r.stderr

    def test_ui_components_paths(self):
        """core.py:1908 — ui_components_paths"""
        code = (
            "import sys; sys.path.insert(0, 'harness'); "
            "import path_resolver; "
            "result = path_resolver.ui_components_paths(); "
            "print(repr(result))"
        )
        r = _run_direct(code)
        assert r.returncode == 0, f"ImportError 발생:\n{r.stderr}"
        assert "ImportError" not in r.stderr

    def test_test_paths_extract_regex(self):
        """impl_loop.py:992 — test_paths_extract_regex"""
        code = (
            "import sys; sys.path.insert(0, 'harness'); "
            "import path_resolver; "
            "result = path_resolver.test_paths_extract_regex(); "
            "print(repr(result))"
        )
        r = _run_direct(code)
        assert r.returncode == 0, f"ImportError 발생:\n{r.stderr}"
        assert "ImportError" not in r.stderr

    def test_full_simulation(self):
        """Issue #27 직접 재현 시뮬레이션 — 9개 함수 한꺼번에 호출."""
        code = (
            "import sys\n"
            "sys.path.insert(0, 'harness')\n"
            "import core, path_resolver\n"
            "print(core.extract_src_refs('/etc/hosts'))\n"
            "print(core.extract_files_from_error('test error trace'))\n"
            "print(path_resolver.engineer_scope_pathspecs())\n"
            "print(path_resolver.engineer_scope_extract_regex())\n"
            "print(path_resolver.engineer_scope_grep_paths())\n"
            "print(path_resolver.engineer_scope_any_exists())\n"
            "print(path_resolver.engineer_scope_human_dir_list())\n"
            "print(path_resolver.ui_components_paths())\n"
            "print(path_resolver.test_paths_extract_regex())\n"
        )
        r = _run_direct(code)
        assert r.returncode == 0, (
            f"직접 실행 시뮬레이션 실패 (returncode={r.returncode}):\n"
            f"--- stdout ---\n{r.stdout}\n"
            f"--- stderr ---\n{r.stderr}"
        )
        assert "ImportError" not in r.stderr, (
            f"stderr에 ImportError 흔적:\n{r.stderr}"
        )
