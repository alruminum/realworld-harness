"""
test_check_test_sync.py — scripts/check_test_sync.py 회귀 테스트

REQ-001: harness/ 만 변경 + tests 0 → exit 1
REQ-002: harness/ + tests 동반 → exit 0
REQ-003: hooks/ 만 변경 + tests 0 → exit 1
REQ-004: docs/ 만 변경 (코드 X) → exit 0
REQ-005: Tests-Exception 마커 명시 → exit 0
REQ-005a: Tests-Exception 사유 너무 짧음 → exit 1
REQ-005b: Tests-Exception 빈 사유 → exit 1
REQ-005c: 과거 commit body 에 Tests-Exception (현재 diff 에는 없음) → exit 1
"""
from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent.parent / "scripts" / "check_test_sync.py"


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
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp,
        capture_output=True,
        text=True,
    ).stdout.strip()


class TestCheckTestSync(unittest.TestCase):

    def _run_script(self, tmp: Path, base: str, head: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["python3", str(SCRIPT), base, head],
            capture_output=True,
            text=True,
            cwd=tmp,
        )

    def test_req_001_harness_only_no_tests_exit1(self):
        """REQ-001: harness/ 만 변경 + tests 0 → exit 1 + "tests/** 동반 누락" 메시지."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            _init_git_repo(tmp)
            base = _commit_files(tmp, {"README.md": "init"}, "init")
            head = _commit_files(tmp, {"harness/foo.py": "# harness code"}, "add harness")

            result = self._run_script(tmp, base, head)

            self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
            self.assertIn("FAIL", result.stdout)
            self.assertIn("tests/**", result.stdout)

    def test_req_002_harness_with_tests_exit0(self):
        """REQ-002: harness/ + tests 동반 → exit 0."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            _init_git_repo(tmp)
            base = _commit_files(tmp, {"README.md": "init"}, "init")
            head = _commit_files(
                tmp,
                {
                    "harness/foo.py": "# harness code",
                    "tests/pytest/test_foo.py": "# test",
                },
                "add harness + test",
            )

            result = self._run_script(tmp, base, head)

            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

    def test_req_003_hooks_only_no_tests_exit1(self):
        """REQ-003: hooks/ 만 변경 + tests 0 → exit 1."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            _init_git_repo(tmp)
            base = _commit_files(tmp, {"README.md": "init"}, "init")
            head = _commit_files(tmp, {"hooks/bar.py": "# hook code"}, "add hook")

            result = self._run_script(tmp, base, head)

            self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
            self.assertIn("FAIL", result.stdout)

    def test_req_004_docs_only_exit0(self):
        """REQ-004: docs/ 만 변경 (코드 X) → exit 0 ("게이트 대상 아님")."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            _init_git_repo(tmp)
            base = _commit_files(tmp, {"README.md": "init"}, "init")
            head = _commit_files(tmp, {"docs/baz.md": "# docs"}, "add docs")

            result = self._run_script(tmp, base, head)

            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

    def test_req_005_tests_exception_in_commit_msg_exit0(self):
        """REQ-005: Tests-Exception 마커를 commit msg 에 명시 → exit 0."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            _init_git_repo(tmp)
            base = _commit_files(tmp, {"README.md": "init"}, "init")
            head = _commit_files(
                tmp,
                {"harness/foo.py": "# harness code"},
                "refactor harness\n\nTests-Exception: docstring-only refactor",
            )

            result = self._run_script(tmp, base, head)

            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

    def test_req_005a_tests_exception_short_reason_exit1(self):
        """REQ-005a: Tests-Exception 사유 2자 → exit 1 + 사유 너무 짧음 메시지."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            _init_git_repo(tmp)
            base = _commit_files(tmp, {"README.md": "init"}, "init")
            head = _commit_files(
                tmp,
                {"harness/foo.py": "# harness code"},
                "refactor\n\nTests-Exception: ok",
            )

            result = self._run_script(tmp, base, head)

            self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
            self.assertIn("짧음", result.stdout)

    def test_req_005b_tests_exception_empty_reason_exit1(self):
        """REQ-005b: Tests-Exception 빈 사유 → exit 1."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            _init_git_repo(tmp)
            base = _commit_files(tmp, {"README.md": "init"}, "init")
            head = _commit_files(
                tmp,
                {"harness/foo.py": "# harness code"},
                "refactor\n\nTests-Exception: ",
            )

            result = self._run_script(tmp, base, head)

            self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)

    def test_req_005c_tests_exception_in_old_commit_exit1(self):
        """REQ-005c: 과거 commit body 에 Tests-Exception (현재 diff 에는 없음) → exit 1 (재사용 hole 차단)."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            _init_git_repo(tmp)
            # 과거 commit 에 Tests-Exception 포함
            _commit_files(
                tmp,
                {"README.md": "init"},
                "old commit\n\nTests-Exception: docstring-only refactor — 행동 불변",
            )
            base = _commit_files(tmp, {"docs/note.md": "note"}, "mid commit — no exception")
            # 현재 diff: harness/ 변경 + Tests-Exception 없음
            head = _commit_files(
                tmp,
                {"harness/foo.py": "# new harness code"},
                "add harness code",
            )

            result = self._run_script(tmp, base, head)

            self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
            self.assertIn("FAIL", result.stdout)


if __name__ == "__main__":
    unittest.main()
