"""test_autocheck_no_changes.py — Issue #34 회귀 테스트.

run_automated_checks 의 no_changes 분기에서 직전 커밋이 test-only 인 경우 PASS 처리 +
mixed/empty 인 경우 hard reset 으로 stranded 방지.

컨벤션: tests/pytest/test_worktree.py — 임시 git repo + 실제 subprocess.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness.helpers import (  # noqa: E402
    _classify_last_commit_files,
    rollback_attempt,
    run_automated_checks,
)
from harness.core import StateDir  # noqa: E402


# ── 공통 헬퍼 ──────────────────────────────────────────────────────────

def _init_repo(repo: Path) -> None:
    """임시 git repo 초기화 + 첫 커밋 (main branch)."""
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "t"], check=True)
    (repo / "README.md").write_text("seed\n")
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "seed"], check=True)


def _commit(repo: Path, files: dict, msg: str) -> str:
    """파일 dict 를 worktree 에 쓰고 커밋. 반환: HEAD sha."""
    for rel, content in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", msg], check=True)
    r = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    return r.stdout.strip()


def _make_state_dir(tmp_path: Path) -> StateDir:
    sd_path = tmp_path / "state"
    sd_path.mkdir()
    return StateDir(sd_path, prefix="test")


def _impl_file_with_scope(tmp_path: Path, allowed: list) -> Path:
    f = tmp_path / "impl.md"
    body = "## 수정 파일\n" + "\n".join(f"- `{a}`" for a in allowed) + "\n"
    f.write_text(body)
    return f


def _head_sha(repo: Path) -> str:
    r = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    return r.stdout.strip()


# ══════════════════════════════════════════════════════════════════════
# REQ-006~008: _classify_last_commit_files() 분류 헬퍼 단위 테스트
# ══════════════════════════════════════════════════════════════════════

class TestREQ006Classification:
    """직전 커밋 파일 목록의 5가지 분류 정확성 검증 (REQ-006, REQ-007, REQ-008)."""

    def test_classify_empty(self):
        """파일 없음 → empty."""
        assert _classify_last_commit_files([]) == "empty"

    def test_classify_test_only_jest(self):
        """jest/vitest *.test.tsx → test_only."""
        assert _classify_last_commit_files(
            ["src/components/__tests__/Button.test.tsx"]
        ) == "test_only"

    def test_classify_test_only_pytest(self):
        """pytest tests/ 디렉토리 → test_only (REQ-006 monorepo 패턴)."""
        assert _classify_last_commit_files(
            ["apps/api/tests/test_recordings.py"]
        ) == "test_only"

    def test_classify_plan_only(self):
        """docs/impl/ + docs/bugfix/ → plan_only (REQ-007)."""
        assert _classify_last_commit_files(
            ["docs/impl/34-foo.md", "docs/bugfix/bar.md"]
        ) == "plan_only"

    def test_classify_test_and_plan(self):
        """test + plan 혼합 → test_and_plan (모두 PASS 대상)."""
        assert _classify_last_commit_files(
            ["apps/api/tests/test_x.py", "docs/impl/34-foo.md"]
        ) == "test_and_plan"

    def test_classify_mixed(self):
        """test + 일반 src → mixed (REQ-008 — escalate 대상)."""
        assert _classify_last_commit_files(
            ["apps/api/tests/test_x.py", "apps/api/app/main.py"]
        ) == "mixed"

    def test_classify_underscore_test_py(self):
        """*_test.py 형식 → test_only (pytest 표준 naming)."""
        assert _classify_last_commit_files(
            ["apps/api/recordings_test.py"]
        ) == "test_only"


# ══════════════════════════════════════════════════════════════════════
# REQ-001/002: test-only / plan-only commit → run_automated_checks PASS
# ══════════════════════════════════════════════════════════════════════

class TestREQ002TestOnlyCommitPass:
    """직전 커밋이 test-only / plan-only 이면 run_automated_checks 가 PASS 반환 (REQ-002)."""

    def test_test_only_commit_returns_pass(self, tmp_path, monkeypatch):
        """apps/api/tests/test_x.py 만 커밋 → engineer_scope 미변경이지만 PASS."""
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        monkeypatch.chdir(repo)

        subprocess.run(
            ["git", "-C", str(repo), "checkout", "-q", "-b", "feat/x"], check=True
        )
        _commit(
            repo,
            {"apps/api/tests/test_x.py": "def test_a(): pass\n"},
            "test(api): regression",
        )

        impl = _impl_file_with_scope(tmp_path, ["apps/api/tests/test_x.py"])
        sd = _make_state_dir(tmp_path)
        cfg = SimpleNamespace(lint_command="", build_command="", test_command="")

        ok, err = run_automated_checks(
            str(impl), cfg, sd, "test", cwd=str(repo), run_tests=False,
        )
        assert ok, f"test-only commit 은 PASS 여야 함. err={err!r}"

    def test_plan_only_commit_returns_pass(self, tmp_path, monkeypatch):
        """docs/impl/ 만 커밋 → PASS."""
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        monkeypatch.chdir(repo)

        subprocess.run(
            ["git", "-C", str(repo), "checkout", "-q", "-b", "feat/p"], check=True
        )
        _commit(
            repo,
            {"docs/impl/34-plan.md": "# plan\n"},
            "docs: add impl plan",
        )

        impl = _impl_file_with_scope(tmp_path, ["docs/impl/34-plan.md"])
        sd = _make_state_dir(tmp_path)
        cfg = SimpleNamespace(lint_command="", build_command="", test_command="")

        ok, err = run_automated_checks(
            str(impl), cfg, sd, "test", cwd=str(repo), run_tests=False,
        )
        assert ok, f"plan-only commit 은 PASS 여야 함. err={err!r}"

    def test_test_and_plan_commit_returns_pass(self, tmp_path, monkeypatch):
        """tests/ + docs/impl/ 함께 커밋 → PASS."""
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        monkeypatch.chdir(repo)

        subprocess.run(
            ["git", "-C", str(repo), "checkout", "-q", "-b", "feat/tp"], check=True
        )
        _commit(
            repo,
            {
                "apps/api/tests/test_x.py": "def test_a(): pass\n",
                "docs/impl/34-plan.md": "# plan\n",
            },
            "test+docs: regression + plan",
        )

        impl = _impl_file_with_scope(
            tmp_path, ["apps/api/tests/test_x.py", "docs/impl/34-plan.md"]
        )
        sd = _make_state_dir(tmp_path)
        cfg = SimpleNamespace(lint_command="", build_command="", test_command="")

        ok, err = run_automated_checks(
            str(impl), cfg, sd, "test", cwd=str(repo), run_tests=False,
        )
        assert ok, f"test+plan commit 은 PASS 여야 함. err={err!r}"


# ══════════════════════════════════════════════════════════════════════
# REQ-001: git log -1 --name-only HEAD 가 호출되는지 (결과로 검증)
# ══════════════════════════════════════════════════════════════════════

class TestREQ001LastCommitInspection:
    """no_changes 분기 진입 시 직전 커밋 파일 목록을 실제로 검사하는지 결과로 검증."""

    def test_inspects_last_commit_on_no_changes(self, tmp_path, monkeypatch):
        """test-only commit 후 no_changes 분기 → PASS = 직전 커밋 검사가 이뤄진 증거."""
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        monkeypatch.chdir(repo)

        subprocess.run(
            ["git", "-C", str(repo), "checkout", "-q", "-b", "feat/inspect"], check=True
        )
        _commit(
            repo,
            {"tests/test_something.py": "def test_ok(): pass\n"},
            "test: add regression",
        )

        impl = _impl_file_with_scope(tmp_path, ["tests/test_something.py"])
        sd = _make_state_dir(tmp_path)
        cfg = SimpleNamespace(lint_command="", build_command="", test_command="")

        ok, err = run_automated_checks(
            str(impl), cfg, sd, "test", cwd=str(repo), run_tests=False,
        )
        # PASS 는 내부에서 git log -1 --name-only HEAD 를 호출하고
        # 파일을 test_only 로 분류한 결과임 — 직접 subprocess mock 없이 결과로 검증
        assert ok, f"직전 커밋 검사 후 PASS 여야 함. err={err!r}"


# ══════════════════════════════════════════════════════════════════════
# REQ-003: mixed/empty → rollback_attempt(hard_reset=True) 시 git reset
# ══════════════════════════════════════════════════════════════════════

class TestREQ003RollbackOnInvalidScope:
    """mixed/empty 커밋 후 rollback_attempt(hard_reset=True) 가 HEAD 를 되돌리는지 검증."""

    def test_mixed_commit_resets_hard(self, tmp_path, monkeypatch):
        """mixed scope commit → hard_reset=True 시 HEAD~1 fallback."""
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        monkeypatch.chdir(repo)

        subprocess.run(
            ["git", "-C", str(repo), "checkout", "-q", "-b", "feat/y"], check=True
        )
        before_sha = _commit(repo, {"foo.txt": "1\n"}, "first")
        _commit(repo, {"random.txt": "2\n"}, "bad mixed commit")

        # caller 모방: rollback_attempt(hard_reset=True)
        rollback_attempt(
            1, run_logger=None,
            hard_reset=True, feature_branch="feat/y", cwd=str(repo),
        )

        after_sha = _head_sha(repo)
        # origin 없으므로 HEAD~1 fallback → before_sha 로 reset
        assert after_sha == before_sha, (
            f"HEAD~1 fallback 로 reset 되어야 함. before={before_sha}, after={after_sha}"
        )

    def test_empty_commit_resets_hard(self, tmp_path, monkeypatch):
        """git commit --allow-empty 후 hard reset."""
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        monkeypatch.chdir(repo)

        subprocess.run(
            ["git", "-C", str(repo), "checkout", "-q", "-b", "feat/empty"], check=True
        )
        before_sha = _head_sha(repo)
        subprocess.run(
            ["git", "-C", str(repo), "commit", "-q", "--allow-empty", "-m", "empty"],
            check=True,
        )
        after_commit_sha = _head_sha(repo)
        assert after_commit_sha != before_sha  # 커밋 만들어졌음 확인

        rollback_attempt(
            1, run_logger=None,
            hard_reset=True, feature_branch="feat/empty", cwd=str(repo),
        )

        reset_sha = _head_sha(repo)
        assert reset_sha == before_sha, (
            f"empty commit 후 hard reset → seed commit 으로 돌아가야 함. "
            f"before={before_sha}, reset={reset_sha}"
        )

    def test_no_origin_falls_back_to_head_minus_one(self, tmp_path, monkeypatch):
        """origin remote 자체 없을 때 HEAD~1 폴백 명시적 검증."""
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        monkeypatch.chdir(repo)

        subprocess.run(
            ["git", "-C", str(repo), "checkout", "-q", "-b", "feat/noorigin"], check=True
        )
        before_sha = _commit(repo, {"a.txt": "1\n"}, "base")
        _commit(repo, {"b.txt": "2\n"}, "bad")

        # origin remote 가 없는 상태에서 호출
        rollback_attempt(
            1, run_logger=None,
            hard_reset=True, feature_branch="feat/noorigin", cwd=str(repo),
        )

        reset_sha = _head_sha(repo)
        assert reset_sha == before_sha, (
            f"origin 없을 때 HEAD~1 fallback 적용 기대. before={before_sha}, actual={reset_sha}"
        )


# ══════════════════════════════════════════════════════════════════════
# 기존 keep-on-branch 호출 호환 (REQ-004 회귀 보호)
# ══════════════════════════════════════════════════════════════════════

class TestRollbackBackwardCompat:
    """hard_reset 미지정 시 기존 keep-on-branch 동작 유지 (backward compat)."""

    def test_default_call_no_reset(self, tmp_path, monkeypatch):
        """hard_reset 미지정 → HEAD 변경 없음."""
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        monkeypatch.chdir(repo)

        before_sha = _commit(repo, {"a.txt": "1\n"}, "x")

        # 기존 호출 패턴 (위치인자만)
        rollback_attempt(1, run_logger=None)

        after_sha = _head_sha(repo)
        assert after_sha == before_sha, (
            "hard_reset 미지정 시 HEAD 변경되지 않아야 함"
        )


# ══════════════════════════════════════════════════════════════════════
# G5: hard_reset target 별 JSONL 분류 검증
# ══════════════════════════════════════════════════════════════════════

class TestRollbackJSONLClassification:
    """rollback_attempt(hard_reset=True) 의 JSONL 이벤트가 method/target 을 정확히 기록."""

    def _make_logger(self, tmp_path: Path):
        """간이 RunLogger stub — log_event 호출 내용을 리스트로 수집."""
        events = []

        class _Logger:
            def log_event(self, ev):
                events.append(ev)

        return _Logger(), events

    def test_head_minus_one_target_logged_when_no_origin(self, tmp_path, monkeypatch):
        """origin remote 없는 케이스 — rollback_hard_reset event target=='HEAD~1'."""
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        monkeypatch.chdir(repo)

        subprocess.run(
            ["git", "-C", str(repo), "checkout", "-q", "-b", "feat/log"], check=True
        )
        _commit(repo, {"a.txt": "1\n"}, "base")
        _commit(repo, {"b.txt": "2\n"}, "bad")

        logger, events = self._make_logger(tmp_path)

        rollback_attempt(
            1, run_logger=logger,
            hard_reset=True, feature_branch="feat/log", cwd=str(repo),
        )

        reset_events = [e for e in events if e.get("event") == "rollback_hard_reset"]
        assert reset_events, "rollback_hard_reset 이벤트가 기록되어야 함"
        assert reset_events[0]["target"] == "HEAD~1", (
            f"target 은 'HEAD~1' 이어야 함. actual={reset_events[0]['target']!r}"
        )

        rollback_events = [e for e in events if e.get("event") == "rollback"]
        assert rollback_events, "rollback 이벤트가 기록되어야 함"
        assert rollback_events[0]["method"] == "hard-reset:HEAD~1", (
            f"method 는 'hard-reset:HEAD~1' 이어야 함. actual={rollback_events[0]['method']!r}"
        )

    def test_skipped_target_logged_when_first_commit(self, tmp_path, monkeypatch):
        """HEAD~1 없음 (첫 커밋 직후) → target=='skipped', HEAD 변경 없음."""
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        monkeypatch.chdir(repo)

        # main 의 seed commit 이 유일 → HEAD~1 없음
        before_sha = _head_sha(repo)

        logger, events = self._make_logger(tmp_path)

        rollback_attempt(
            1, run_logger=logger,
            hard_reset=True, feature_branch="nonexistent", cwd=str(repo),
        )

        reset_events = [e for e in events if e.get("event") == "rollback_hard_reset"]
        assert reset_events, "rollback_hard_reset 이벤트 기록 기대"
        assert reset_events[0]["target"] == "skipped", (
            f"HEAD~1 없을 때 target='skipped' 기대. actual={reset_events[0]['target']!r}"
        )

        after_sha = _head_sha(repo)
        assert after_sha == before_sha, "skipped 케이스에서 HEAD 변경 없어야 함"

    def test_origin_target_logged_when_origin_exists(self, tmp_path, monkeypatch):
        """origin/<branch> 가 존재할 때 target=='origin/<branch>'."""
        # bare remote 생성 + clone + push
        bare = tmp_path / "bare.git"
        subprocess.run(["git", "init", "--bare", "-q", str(bare)], check=True)

        repo = tmp_path / "repo"
        subprocess.run(["git", "clone", "-q", str(bare), str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@t"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.name", "t"], check=True)

        # 초기 커밋 + push → origin/main 생성
        (repo / "README.md").write_text("seed\n")
        subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "seed"], check=True)
        subprocess.run(["git", "-C", str(repo), "push", "-q", "-u", "origin", "main"], check=True)

        # feature branch 생성 + push
        subprocess.run(
            ["git", "-C", str(repo), "checkout", "-q", "-b", "feat/origin-test"],
            check=True,
        )
        before_sha = _commit(repo, {"a.txt": "1\n"}, "base")
        subprocess.run(
            ["git", "-C", str(repo), "push", "-q", "-u", "origin", "feat/origin-test"],
            check=True,
        )

        # mixed commit (pushed 이후 추가 커밋)
        _commit(repo, {"bad.txt": "2\n"}, "bad")

        monkeypatch.chdir(repo)
        logger, events = self._make_logger(tmp_path)

        rollback_attempt(
            1, run_logger=logger,
            hard_reset=True, feature_branch="feat/origin-test", cwd=str(repo),
        )

        reset_events = [e for e in events if e.get("event") == "rollback_hard_reset"]
        assert reset_events, "rollback_hard_reset 이벤트 기록 기대"
        assert reset_events[0]["target"] == "origin/feat/origin-test", (
            f"origin push 후 target='origin/<br>' 기대. actual={reset_events[0]['target']!r}"
        )

        after_sha = _head_sha(repo)
        assert after_sha == before_sha, (
            f"origin reset 후 HEAD = push 직전 SHA 기대. before={before_sha}, after={after_sha}"
        )


# ══════════════════════════════════════════════════════════════════════
# G5: passthrough 후 build_command fail 케이스
# ══════════════════════════════════════════════════════════════════════

class TestREQ002BuildFailAfterPassthrough:
    """test-only commit PASS → build_command 실행 → build 실패 → escalate (G3 passthrough)."""

    def test_test_only_commit_then_build_fail_returns_fail(self, tmp_path, monkeypatch):
        """build_command 가 항상 fail 하는 경우, test-only commit 이어도 FAIL 반환."""
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        monkeypatch.chdir(repo)

        subprocess.run(
            ["git", "-C", str(repo), "checkout", "-q", "-b", "feat/build"], check=True
        )
        _commit(
            repo,
            {"apps/api/tests/test_x.py": "def test_a(): pass\n"},
            "test(api): regression",
        )

        impl = _impl_file_with_scope(tmp_path, ["apps/api/tests/test_x.py"])
        sd = _make_state_dir(tmp_path)
        # build_command 가 항상 fail
        cfg = SimpleNamespace(
            lint_command="",
            build_command="exit 1",
            test_command="",
        )

        ok, err = run_automated_checks(
            str(impl), cfg, sd, "test", cwd=str(repo), run_tests=False,
        )
        assert not ok, "build 실패 시 PASS 가 아니어야 함"
        assert "build_fail" in err, f"err 에 'build_fail' 포함 기대. actual={err!r}"
