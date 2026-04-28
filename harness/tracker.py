"""harness/tracker.py — 추적 ID 백엔드 추상화.

I-2 (모든 구현은 하네스 루프 + 추적 ID) 보존을 위한 추상화 레이어.
gh CLI / 로컬 jsonl 중 가용 백엔드를 자동 선택한다.

ID 포맷:
  - GitHub:  "#42"
  - Local:   "LOCAL-7"

CLI:
  python3 -m harness.tracker create-issue --title "..." --body "..." [--label X --milestone N]
  python3 -m harness.tracker get <ref>
  python3 -m harness.tracker comment <ref> --body "..."
  python3 -m harness.tracker which

Env:
  HARNESS_TRACKER=github|local   강제 백엔드 선택
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Protocol


# ── ID 파싱/표현 ──

@dataclass(frozen=True)
class IssueRef:
    backend: str       # "github" | "local"
    number: int
    raw: str           # "#42" | "LOCAL-7"

    def __str__(self) -> str:
        return self.raw


def parse_ref(s: str) -> IssueRef:
    """추적 ID 문자열 파싱.

    수용 형식: "#42", "LOCAL-7", "42" (legacy GitHub)
    """
    s = s.strip()
    if s.startswith("#") and s[1:].isdigit():
        return IssueRef("github", int(s[1:]), s)
    if s.startswith("LOCAL-") and s[6:].isdigit():
        return IssueRef("local", int(s[6:]), s)
    if s.isdigit():
        n = int(s)
        return IssueRef("github", n, f"#{n}")
    raise ValueError(f"Unknown issue ref: {s!r}")


# ── Backend Protocol ──

class TrackingBackend(Protocol):
    name: str

    def is_available(self) -> bool: ...
    def create_issue(
        self, title: str, body: str,
        labels: Optional[list] = None, milestone: Optional[str] = None,
    ) -> IssueRef: ...
    def get_issue(self, ref: IssueRef) -> dict: ...
    def add_comment(self, ref: IssueRef, body: str) -> None: ...


# ── GitHub backend (gh CLI) ──

class GitHubBackend:
    name = "github"

    def __init__(self, repo: Optional[str] = None):
        self._repo_cached = repo

    @property
    def repo(self) -> Optional[str]:
        if self._repo_cached is None:
            self._repo_cached = self._detect_repo() or ""
        return self._repo_cached or None

    @staticmethod
    def _detect_repo() -> Optional[str]:
        if not shutil.which("gh"):
            return None
        try:
            r = subprocess.run(
                ["gh", "repo", "view", "--json", "nameWithOwner",
                 "--jq", ".nameWithOwner"],
                capture_output=True, text=True, timeout=5,
            )
        except Exception:
            return None
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
        return None

    def is_available(self) -> bool:
        return bool(shutil.which("gh") and self.repo)

    def create_issue(self, title, body="", labels=None, milestone=None) -> IssueRef:
        cmd = ["gh", "issue", "create", "--repo", self.repo,
               "--title", title, "--body", body or ""]
        for label in (labels or []):
            cmd += ["--label", label]
        if milestone:
            cmd += ["--milestone", str(milestone)]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            raise RuntimeError(f"gh issue create 실패: {r.stderr.strip()}")
        url = r.stdout.strip().splitlines()[-1]
        n = int(url.rstrip("/").rsplit("/", 1)[-1])
        return IssueRef("github", n, f"#{n}")

    def get_issue(self, ref: IssueRef) -> dict:
        r = subprocess.run(
            ["gh", "issue", "view", str(ref.number), "--repo", self.repo,
             "--json", "number,title,body,state,labels,milestone"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode != 0:
            raise RuntimeError(f"gh issue view 실패: {r.stderr.strip()}")
        return json.loads(r.stdout)

    def add_comment(self, ref: IssueRef, body: str) -> None:
        r = subprocess.run(
            ["gh", "issue", "comment", str(ref.number),
             "--repo", self.repo, "--body", body],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode != 0:
            raise RuntimeError(f"gh issue comment 실패: {r.stderr.strip()}")


# ── Local backend (orchestration/issues/INDEX.jsonl) ──

def _project_root() -> Path:
    cwd = Path.cwd().resolve()
    for parent in [cwd, *cwd.parents]:
        if (parent / "orchestration").is_dir() and (parent / ".git").is_dir():
            return parent
        if (parent / ".claude").is_dir():
            return parent
    return cwd


class LocalBackend:
    name = "local"

    def __init__(self, root: Optional[Path] = None):
        base = Path(root) if root else (_project_root() / "orchestration" / "issues")
        self.root = base

    def is_available(self) -> bool:
        return True

    def _index(self) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        return self.root / "INDEX.jsonl"

    def _next_id_file(self) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        return self.root / ".next_id"

    def _next_id(self) -> int:
        f = self._next_id_file()
        n = (int(f.read_text().strip() or "0") + 1) if f.exists() else 1
        f.write_text(str(n))
        return n

    def _read_all(self) -> list:
        f = self._index()
        if not f.exists():
            return []
        return [json.loads(line) for line in f.read_text().splitlines() if line.strip()]

    def _write_all(self, entries: list) -> None:
        f = self._index()
        f.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in entries))

    def create_issue(self, title, body="", labels=None, milestone=None) -> IssueRef:
        n = self._next_id()
        now = datetime.now().isoformat(timespec="seconds")
        entry = {
            "id": n,
            "ref": f"LOCAL-{n}",
            "title": title,
            "body": body or "",
            "labels": list(labels or []),
            "milestone": milestone,
            "state": "open",
            "created": now,
            "updated": now,
            "comments": [],
        }
        with open(self._index(), "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return IssueRef("local", n, f"LOCAL-{n}")

    def get_issue(self, ref: IssueRef) -> dict:
        for entry in self._read_all():
            if entry["id"] == ref.number:
                return entry
        raise KeyError(f"LOCAL-{ref.number} not found")

    def add_comment(self, ref: IssueRef, body: str) -> None:
        entries = self._read_all()
        for entry in entries:
            if entry["id"] == ref.number:
                entry["comments"].append({
                    "body": body,
                    "created": datetime.now().isoformat(timespec="seconds"),
                })
                entry["updated"] = datetime.now().isoformat(timespec="seconds")
                self._write_all(entries)
                return
        raise KeyError(f"LOCAL-{ref.number} not found")


# ── Backend selection ──

_BACKENDS = {"github": GitHubBackend, "local": LocalBackend}


def get_tracker(prefer: Optional[str] = None) -> TrackingBackend:
    """가용 백엔드 자동 선택.

    우선순위:
      1. HARNESS_TRACKER env (강제, 미가용이면 RuntimeError)
      2. prefer 인자
      3. github → local
    """
    forced = os.environ.get("HARNESS_TRACKER")
    if forced:
        cls = _BACKENDS.get(forced)
        if cls is None:
            raise ValueError(f"Unknown HARNESS_TRACKER: {forced}")
        b = cls()
        if not b.is_available():
            raise RuntimeError(f"HARNESS_TRACKER={forced} but backend unavailable")
        return b
    order = []
    if prefer and prefer in _BACKENDS:
        order.append(prefer)
    for name in ("github", "local"):
        if name not in order:
            order.append(name)
    for name in order:
        b = _BACKENDS[name]()
        if b.is_available():
            return b
    raise RuntimeError("No tracker backend available")


def get_tracker_for(ref: IssueRef) -> TrackingBackend:
    cls = _BACKENDS.get(ref.backend)
    if cls is None:
        raise ValueError(f"Unknown backend in ref: {ref}")
    b = cls()
    if not b.is_available():
        raise RuntimeError(f"Backend {ref.backend} unavailable for {ref}")
    return b


# ── CLI ──

def _cli_create(args):
    backend = get_tracker(prefer=args.backend)
    ref = backend.create_issue(
        title=args.title, body=args.body or "",
        labels=args.label or [], milestone=args.milestone,
    )
    print(ref.raw)
    if args.verbose:
        print(f"backend={backend.name}", file=sys.stderr)


def _cli_get(args):
    ref = parse_ref(args.ref)
    print(json.dumps(get_tracker_for(ref).get_issue(ref),
                     ensure_ascii=False, indent=2))


def _cli_comment(args):
    ref = parse_ref(args.ref)
    get_tracker_for(ref).add_comment(ref, args.body)
    print(f"commented on {ref}")


def _cli_which(args):
    forced = os.environ.get("HARNESS_TRACKER")
    selected = get_tracker().name
    msg = f"selected: {selected}"
    if forced:
        msg += " (forced via HARNESS_TRACKER)"
    print(msg)
    for name, cls in _BACKENDS.items():
        ok = cls().is_available()
        print(f"  {name}: {'available' if ok else 'unavailable'}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="python -m harness.tracker")
    p.add_argument("--backend", choices=list(_BACKENDS),
                   help="강제 백엔드 (auto-select 우회)")
    p.add_argument("--verbose", "-v", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create-issue")
    c.add_argument("--title", required=True)
    c.add_argument("--body", default="")
    c.add_argument("--label", action="append", default=[])
    c.add_argument("--milestone")
    c.set_defaults(func=_cli_create)

    g = sub.add_parser("get")
    g.add_argument("ref")
    g.set_defaults(func=_cli_get)

    cm = sub.add_parser("comment")
    cm.add_argument("ref")
    cm.add_argument("--body", required=True)
    cm.set_defaults(func=_cli_comment)

    w = sub.add_parser("which")
    w.set_defaults(func=_cli_which)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
