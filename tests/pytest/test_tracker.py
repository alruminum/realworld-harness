"""Unit tests for harness.tracker.

stdlib unittest 사용 (외부 의존 없음).

실행:
  python3 -m unittest tests.pytest.test_tracker
  또는: python3 tests/pytest/test_tracker.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# 프로젝트 루트를 sys.path 에 추가 (RWHarness 자체에서 직접 실행 가능)
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from harness import tracker as tr  # noqa: E402


class LocalBackendTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.b = tr.LocalBackend(root=self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_create_assigns_sequential_ids(self):
        r1 = self.b.create_issue("first", "body", ["bug"])
        r2 = self.b.create_issue("second", "body")
        self.assertEqual(r1.raw, "LOCAL-1")
        self.assertEqual(r2.raw, "LOCAL-2")
        self.assertEqual(r1.backend, "local")

    def test_persistence_across_instances(self):
        self.b.create_issue("x")
        b2 = tr.LocalBackend(root=self.root)
        r2 = b2.create_issue("y")
        self.assertEqual(r2.number, 2)

    def test_get_returns_entry(self):
        ref = self.b.create_issue("title", "body content",
                                  ["a", "b"], milestone="m1")
        entry = self.b.get_issue(ref)
        self.assertEqual(entry["title"], "title")
        self.assertEqual(entry["body"], "body content")
        self.assertEqual(entry["labels"], ["a", "b"])
        self.assertEqual(entry["milestone"], "m1")
        self.assertEqual(entry["state"], "open")

    def test_get_missing_raises(self):
        with self.assertRaises(KeyError):
            self.b.get_issue(tr.IssueRef("local", 999, "LOCAL-999"))

    def test_add_comment_appends(self):
        ref = self.b.create_issue("t", "b")
        self.b.add_comment(ref, "first")
        self.b.add_comment(ref, "second")
        entry = self.b.get_issue(ref)
        self.assertEqual(len(entry["comments"]), 2)
        self.assertEqual(entry["comments"][0]["body"], "first")

    def test_index_is_jsonl(self):
        self.b.create_issue("hello", "world")
        index = self.root / "INDEX.jsonl"
        lines = index.read_text().strip().splitlines()
        self.assertEqual(len(lines), 1)
        self.assertEqual(json.loads(lines[0])["ref"], "LOCAL-1")

    def test_is_available_always_true(self):
        self.assertTrue(self.b.is_available())


class ParseRefTests(unittest.TestCase):
    def test_github_hash(self):
        r = tr.parse_ref("#42")
        self.assertEqual((r.backend, r.number, r.raw), ("github", 42, "#42"))

    def test_local(self):
        r = tr.parse_ref("LOCAL-7")
        self.assertEqual((r.backend, r.number, r.raw), ("local", 7, "LOCAL-7"))

    def test_bare_number_assumes_github(self):
        r = tr.parse_ref("42")
        self.assertEqual(r.backend, "github")
        self.assertEqual(r.raw, "#42")

    def test_invalid_raises(self):
        with self.assertRaises(ValueError):
            tr.parse_ref("xyz")

    def test_invalid_local_format(self):
        with self.assertRaises(ValueError):
            tr.parse_ref("LOCAL-")


class GetTrackerTests(unittest.TestCase):
    def setUp(self):
        self._saved = os.environ.pop("HARNESS_TRACKER", None)

    def tearDown(self):
        if self._saved is not None:
            os.environ["HARNESS_TRACKER"] = self._saved
        else:
            os.environ.pop("HARNESS_TRACKER", None)

    def test_force_local_via_env(self):
        os.environ["HARNESS_TRACKER"] = "local"
        b = tr.get_tracker()
        self.assertEqual(b.name, "local")

    def test_invalid_force_raises(self):
        os.environ["HARNESS_TRACKER"] = "nonexistent"
        with self.assertRaises(ValueError):
            tr.get_tracker()

    def test_local_always_falls_back(self):
        # github 미가용일 때도 local로 폴백
        if "HARNESS_TRACKER" in os.environ:
            del os.environ["HARNESS_TRACKER"]
        b = tr.get_tracker(prefer="local")
        self.assertEqual(b.name, "local")


class GitHubBackendDetectionTests(unittest.TestCase):
    """gh CLI 가용성 판정만 검증 (실제 API 호출 없음)."""

    def test_unavailable_when_gh_missing(self):
        import shutil as _sh
        original = _sh.which
        try:
            _sh.which = lambda x: None
            b = tr.GitHubBackend()
            self.assertFalse(b.is_available())
        finally:
            _sh.which = original


if __name__ == "__main__":
    unittest.main()
