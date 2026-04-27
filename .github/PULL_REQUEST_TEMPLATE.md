<!--
PR 작성자: 본 템플릿을 그대로 두고 ✅ 체크 또는 빈 항목을 채워주세요.
거버넌스 룰 정본: orchestration/policies.md §2~6
-->

## Task-ID

`HARNESS-CHG-YYYYMMDD-NN`

<!-- 새 Task-ID인 경우 orchestration/changelog.md 마지막 번호 + 1.
     같은 Task-ID 산하 sub-commit이면 PR title 에 [N.M] 표기. -->

## Change-Type

<!-- 가장 강한 1개 선택. 우선순위: spec > infra > agent > docs > test -->

- [ ] **spec** — `docs/harness-spec.md`, `harness-architecture.md`, `proposals.md`, `prd.md`, `trd.md`
- [ ] **infra** — `hooks/`, `harness/`, `scripts/`, `.claude-plugin/`
- [ ] **agent** — `agents/*.md`, `agents/**/*.md`
- [ ] **docs** — `README.md`, `CHANGELOG.md`, `docs/`(spec 제외), `templates/`
- [ ] **test** — `tests/pytest/`, `tests/bats/`

## Summary

<!-- 1~3 bullet — 무엇을, 왜 -->

-

## Document Sync 체크리스트

> 자동 게이트(`scripts/check_doc_sync.py`)가 검증. 누락 시 머지 차단.

- [ ] `orchestration/changelog.md` — 본 Task-ID 항목 추가/갱신 (WHAT)
- [ ] `orchestration/rationale.md` — 본 Task-ID 4섹션 (Rationale / Alternatives / Decision / Follow-Up) 추가/갱신 (WHY) **— spec 변경 시 필수**
- [ ] 관련 문서 갱신 — 영향 받는 spec 파일 (예: harness-spec, harness-architecture, agent-tiers) 검토 표시
- [ ] `[invariant-shift]` PR title 토큰 — Core Invariant 약화 변경인 경우 (`harness-spec.md §0` 참조)

## Document-Exception

<!-- 동반 산출물을 갖추기 어려운 경우만 작성. 사유 ≥ 10자. 무관하면 삭제. -->

<!--
Document-Exception: <10자 이상 사유>
-->

## Test Plan

<!-- 검증 방법. infra/agent 변경은 필수, docs 만은 선택. -->

- [ ]
- [ ]

## Linked

<!-- 관련 issue, 이전 Task-ID, 영향 받는 문서 등 -->

-

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
