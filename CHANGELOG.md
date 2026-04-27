# Changelog

All notable changes to RealWorld Harness will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

각 항목은 Task-ID(`HARNESS-CHG-YYYYMMDD-NN`)와 연결된다. 세부 변경 기록은 [`orchestration/changelog.md`](orchestration/changelog.md)(WHAT), 의사결정 근거는 [`orchestration/rationale.md`](orchestration/rationale.md)(WHY) 참조.

---

## [Unreleased]

### Added (Phase 0 — bootstrap)
- `HARNESS-CHG-20260427-01` (2026-04-27) — 플러그인 배포 레포 골격
  - 디렉토리 구조: `.claude-plugin/`, `hooks/`, `agents/`, `harness/`, `commands/`, `orchestration/`, `templates/`, `scripts/`, `tests/`
  - LICENSE (MIT), `.gitignore`, README (영문 + 한글 골격)
  - `.claude-plugin/{plugin,marketplace}.json` 메타데이터
  - 가벼운 거버넌스 시스템: Task-ID + Change-Type 5종 + Document-Exception 스코핑 + WHAT/WHY 분리 로그
  - `~/.claude/docs/harness-{spec,architecture}.md` 마이그레이션 (헤더만 RWHarness 컨텍스트로 변경, 본문 보존)
  - `docs/{analysis-current-harness,proposals,plan-plugin-distribution}.md` 인풋 자료

---

## [0.1.0-alpha] — TBD

플러그인 배포판 첫 알파. `~/.claude/` 시스템을 클린 구조로 마이그레이션 + 거버넌스 자동 게이트 활성화.
