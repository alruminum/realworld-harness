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

    def test_int_input(self):
        r = tr.parse_ref(42)
        self.assertEqual(r.backend, "github")
        self.assertEqual(r.raw, "#42")

    def test_idempotent_on_issue_ref(self):
        r1 = tr.parse_ref("LOCAL-7")
        r2 = tr.parse_ref(r1)
        self.assertIs(r1, r2)

    def test_invalid_raises(self):
        with self.assertRaises(ValueError):
            tr.parse_ref("xyz")

    def test_invalid_local_format(self):
        with self.assertRaises(ValueError):
            tr.parse_ref("LOCAL-")


class IssueRefInternalTests(unittest.TestCase):
    """IssueRef.internal — 디렉토리·flag·branch·env 안전한 내부 표현."""

    def test_github_internal_is_bare_number(self):
        r = tr.parse_ref("#42")
        self.assertEqual(r.internal, "42")

    def test_local_internal_preserves_form(self):
        r = tr.parse_ref("LOCAL-7")
        self.assertEqual(r.internal, "LOCAL-7")

    def test_github_legacy_internal(self):
        r = tr.parse_ref("42")
        self.assertEqual(r.internal, "42")


class FormatRefTests(unittest.TestCase):
    """format_ref — display form (commit msg, PR title)."""

    def test_bare_number_to_hash(self):
        self.assertEqual(tr.format_ref("42"), "#42")

    def test_hash_idempotent(self):
        self.assertEqual(tr.format_ref("#42"), "#42")

    def test_local_unchanged(self):
        self.assertEqual(tr.format_ref("LOCAL-7"), "LOCAL-7")

    def test_int_input(self):
        self.assertEqual(tr.format_ref(42), "#42")

    def test_issue_ref_input(self):
        ref = tr.IssueRef("local", 1, "LOCAL-1")
        self.assertEqual(tr.format_ref(ref), "LOCAL-1")

    def test_empty_is_empty(self):
        self.assertEqual(tr.format_ref(""), "")
        self.assertEqual(tr.format_ref(None), "")


class NormalizeIssueNumTests(unittest.TestCase):
    """normalize_issue_num — internal form (디렉토리·flag·branch)."""

    def test_bare_number_unchanged(self):
        self.assertEqual(tr.normalize_issue_num("42"), "42")

    def test_strips_leading_hash(self):
        # 부수발견 수리: "#42" → "42" — 디렉토리/branch 안전
        self.assertEqual(tr.normalize_issue_num("#42"), "42")

    def test_local_preserved(self):
        self.assertEqual(tr.normalize_issue_num("LOCAL-7"), "LOCAL-7")

    def test_int_input(self):
        self.assertEqual(tr.normalize_issue_num(42), "42")

    def test_issue_ref_input(self):
        ref = tr.IssueRef("local", 1, "LOCAL-1")
        self.assertEqual(tr.normalize_issue_num(ref), "LOCAL-1")

    def test_empty_is_empty(self):
        # executor 의 issue 미지정 케이스 — 빈 문자열 그대로
        self.assertEqual(tr.normalize_issue_num(""), "")
        self.assertEqual(tr.normalize_issue_num(None), "")


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


class ParseMarkerAliasTests(unittest.TestCase):
    """parse_marker alias map — LLM 변형 흡수 (defense in depth)."""

    def setUp(self):
        from harness import core as _core  # noqa: E402
        self.core = _core
        self.tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        )

    def tearDown(self):
        import os as _os
        try:
            _os.unlink(self.tmp.name)
        except OSError:
            pass

    def _write(self, content: str):
        self.tmp.write(content)
        self.tmp.flush()
        self.tmp.close()

    def test_canonical_marker_still_works(self):
        self._write("preamble\n---MARKER:PLAN_VALIDATION_PASS---\n")
        r = self.core.parse_marker(self.tmp.name,
                                   "PLAN_VALIDATION_PASS|PLAN_VALIDATION_FAIL")
        self.assertEqual(r, "PLAN_VALIDATION_PASS")

    def test_alias_plan_lgtm_to_canonical(self):
        # jajang 2026-04-28 실측 사례
        self._write("validator output...\nPLAN_LGTM\n")
        r = self.core.parse_marker(self.tmp.name,
                                   "PLAN_VALIDATION_PASS|PLAN_VALIDATION_FAIL|PASS|FAIL")
        self.assertEqual(r, "PLAN_VALIDATION_PASS")

    def test_alias_plan_ok_to_canonical(self):
        self._write("validator output...\nPLAN_OK\n")
        r = self.core.parse_marker(self.tmp.name,
                                   "PLAN_VALIDATION_PASS|PLAN_VALIDATION_FAIL|PASS|FAIL")
        self.assertEqual(r, "PLAN_VALIDATION_PASS")

    def test_alias_plan_approve_to_canonical(self):
        self._write("validator output...\nPLAN_APPROVE\n")
        r = self.core.parse_marker(self.tmp.name,
                                   "PLAN_VALIDATION_PASS|PLAN_VALIDATION_FAIL|PASS|FAIL")
        self.assertEqual(r, "PLAN_VALIDATION_PASS")

    def test_alias_design_lgtm(self):
        self._write("output\nDESIGN_LGTM\n")
        r = self.core.parse_marker(self.tmp.name,
                                   "DESIGN_REVIEW_PASS|DESIGN_REVIEW_FAIL")
        self.assertEqual(r, "DESIGN_REVIEW_PASS")

    def test_alias_in_marker_block(self):
        # ---MARKER:PLAN_OK--- 정형 안에 alias 들어와도 잡혀야
        self._write("output\n---MARKER:PLAN_OK---\n")
        r = self.core.parse_marker(self.tmp.name,
                                   "PLAN_VALIDATION_PASS|PLAN_VALIDATION_FAIL|PASS|FAIL")
        self.assertEqual(r, "PLAN_VALIDATION_PASS")

    def test_alias_only_when_canonical_in_expected(self):
        # 호출자가 PLAN_VALIDATION_* 기대 안 하면 alias 도 적용 안 됨
        # (DESIGN 컨텍스트에서 PLAN_LGTM 입력 → UNKNOWN)
        self._write("output\nPLAN_LGTM\n")
        r = self.core.parse_marker(self.tmp.name,
                                   "DESIGN_REVIEW_PASS|DESIGN_REVIEW_FAIL")
        self.assertEqual(r, "UNKNOWN")

    def test_unknown_when_no_canonical_no_alias(self):
        self._write("output without any marker\n")
        r = self.core.parse_marker(self.tmp.name,
                                   "PLAN_VALIDATION_PASS|PLAN_VALIDATION_FAIL")
        self.assertEqual(r, "UNKNOWN")

    def test_canonical_takes_precedence_over_alias(self):
        # 같은 파일에 canonical + alias 모두 있으면 canonical 우선
        self._write("PLAN_LGTM\n---MARKER:PLAN_VALIDATION_PASS---\n")
        r = self.core.parse_marker(self.tmp.name,
                                   "PLAN_VALIDATION_PASS|PLAN_VALIDATION_FAIL|PASS|FAIL")
        self.assertEqual(r, "PLAN_VALIDATION_PASS")  # 같은 결과지만 1차 매치 경로

    def test_general_approve_to_pass(self):
        self._write("output\nAPPROVE\n")
        r = self.core.parse_marker(self.tmp.name, "PASS|FAIL|SPEC_MISSING")
        self.assertEqual(r, "PASS")

    def test_reject_to_fail(self):
        self._write("output\nREJECT\n")
        r = self.core.parse_marker(self.tmp.name, "PASS|FAIL")
        self.assertEqual(r, "FAIL")

    # ── PLAN_REVIEW alias (jajang #133, 2026-04-29 사고) ─────────

    def test_plan_review_lgtm_to_pass(self):
        # jajang #133 — bare LGTM 은 의도적 미alias 지만 PLAN_REVIEW_LGTM 변형은 흡수
        self._write("reviewer output\n---MARKER:PLAN_REVIEW_LGTM---\n")
        r = self.core.parse_marker(self.tmp.name,
                                   "PLAN_REVIEW_PASS|PLAN_REVIEW_CHANGES_REQUESTED")
        self.assertEqual(r, "PLAN_REVIEW_PASS")

    def test_plan_review_ok_to_pass(self):
        self._write("reviewer output\nPLAN_REVIEW_OK\n")
        r = self.core.parse_marker(self.tmp.name,
                                   "PLAN_REVIEW_PASS|PLAN_REVIEW_CHANGES_REQUESTED")
        self.assertEqual(r, "PLAN_REVIEW_PASS")

    def test_plan_review_approve_to_pass(self):
        self._write("reviewer output\nPLAN_REVIEW_APPROVE\n")
        r = self.core.parse_marker(self.tmp.name,
                                   "PLAN_REVIEW_PASS|PLAN_REVIEW_CHANGES_REQUESTED")
        self.assertEqual(r, "PLAN_REVIEW_PASS")

    def test_plan_review_reject_to_changes_requested(self):
        self._write("reviewer output\n---MARKER:PLAN_REVIEW_REJECT---\n")
        r = self.core.parse_marker(self.tmp.name,
                                   "PLAN_REVIEW_PASS|PLAN_REVIEW_CHANGES_REQUESTED")
        self.assertEqual(r, "PLAN_REVIEW_CHANGES_REQUESTED")

    def test_bare_lgtm_aliased_in_plan_review_context(self):
        # jajang 2026-04-29 실측: plan-reviewer 가 bare ---MARKER:LGTM--- emit
        # parse_marker 1차(canonical) 가 alias 보다 우선이라 pr-reviewer 호출
        # (expected_set 에 LGTM) 에선 1차 매치 → alias 우회. plan-reviewer 호출
        # (expected_set 에 LGTM 없음) 에선 1차/2차 fail → alias → PLAN_REVIEW_PASS.
        self._write("reviewer output\n---MARKER:LGTM---\n")
        r = self.core.parse_marker(self.tmp.name,
                                   "PLAN_REVIEW_PASS|PLAN_REVIEW_CHANGES_REQUESTED")
        self.assertEqual(r, "PLAN_REVIEW_PASS")

    def test_bare_lgtm_canonical_in_pr_reviewer_context(self):
        # pr-reviewer 호출은 expected_set 에 LGTM 포함 → 1차 canonical 매치
        # → alias 까지 안 가고 LGTM 그대로 반환 (충돌 없음)
        self._write("pr-reviewer output\n---MARKER:LGTM---\n")
        r = self.core.parse_marker(self.tmp.name, "LGTM|CHANGES_REQUESTED")
        self.assertEqual(r, "LGTM")  # canonical 1차 매치, alias 우회


if __name__ == "__main__":
    unittest.main()
