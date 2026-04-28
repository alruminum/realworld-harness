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

## [0.1.0-alpha] — 2026-04-27

**RealWorld Harness 첫 알파 release.** Claude Code 플러그인 마켓플레이스 배포 가능.

### 핵심 기능

- **34 Python 훅** — 에이전트 권한 경계, 결정론적 게이트, 상태 관리
- **14 역할별 에이전트** — product-planner, plan-reviewer, ux-architect, architect, engineer, test-engineer, validator, designer, design-critic, pr-reviewer, qa, security-reviewer
- **5단계 워크플로우** — 기획-UX → 설계 → 구현(attempt 0..3 + SPEC_GAP 동결) → 디자인 → 리뷰-커밋
- **Core Invariant** — `harness-spec.md §0` 워크플로우 불변 명문화 + `[invariant-shift]` PR 토큰
- **agent_tiers** — high/mid/low tier 매핑으로 모델 진화 흡수 (워크플로우 코드 무수정)
- **Task-ID 거버넌스** — WHAT(`changelog.md`) / WHY(`rationale.md`) 분리 로그 + Document-Exception 스코핑
- **3중 자동 게이트** — git pre-commit hook + Claude Code commit-gate + GitHub Actions PR
- **PLUGIN_ROOT 추상화** — `${CLAUDE_PLUGIN_ROOT}` 환경변수 폴백 `~/.claude`

### 마이그레이션 결과 (Phase 1)
- ~/.claude 활성 코드 100% 이전: hooks 23 / harness 11 / agents 26 / commands 16 / orchestration 15 / templates 1 / scripts 3 / hooks.json 25 엔트리

### 검증 (Phase 3)
- smoke-test 50/50 PASS (ubuntu-latest 별도 머신 자동)
- E2E quickstart §1 (`/quick` 루프) 1 attempt 3m 18s 통과 (실측)
- GitHub Actions doc-sync workflow 가동 (PR 단계 자동 게이트)

### 알려진 부채 (v0.2.0 이후 정리 대상)
- `setup-rwh.sh` 의 글로벌 settings.json hooks 등록 영역에 플러그인 모드 분기 미적용 (잠재 중복 등록 가능성, 다만 "이미 등록됨" 스킵 로직으로 안전)
- ~~BATS → pytest 잔여 마이그레이션~~ (해소됨 — `HARNESS-CHG-20260428-03`. 코드/스크립트에 BATS 흔적 0건 확인, 문서 placeholder 만 남아있던 것을 정리)
- Node.js 20 deprecation (액션 자체 Node 24 호환되면 env 제거)

### Phase
- Phase 0 ✅ 부트스트랩
- Phase 1 ✅ 코어 마이그레이션
- Phase 2 ✅ 철학 명시화 + 자동 게이트
- Phase 3 ✅ 독립 정본화 + 검증
- Phase 4 (현재) — alpha release
