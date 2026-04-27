# orchestration/upstream/ — 원본 운영 룰 참조 스냅샷

> 본 디렉토리는 **참조 전용 스냅샷**이다. RWHarness 의 *실제 운영 룰* 이 아니다.

## 정체성

이 디렉토리는 `~/.claude/orchestration/` (RealWorld Harness 가 마이그레이션해온 source 환경의 운영 룰)의 **원본 보존본**이다. RWHarness 가 ~/.claude 의 작동 중인 시스템을 플러그인으로 클린 재구성할 때, 마스터 룰(`policies.md`, 단계별 운영 룰, 권한 매트릭스 등)을 *원본 그대로* 옮겨두어 향후 비교·검증·문서 추적에 사용할 수 있도록 했다.

## 본 디렉토리의 파일은 RWHarness 의 활성 운영 룰이 아니다

| 활성 정본 (RWHarness) | 참조 스냅샷 (본 디렉토리) |
|---|---|
| [`../policies.md`](../policies.md) | [`policies.md`](policies.md) |
| [`../changelog.md`](../changelog.md) | [`changelog.md`](changelog.md), [`update-record.md`](update-record.md) |
| [`../rationale.md`](../rationale.md) | [`rationale-history.md`](rationale-history.md) |

RWHarness 안에서 운영 룰을 따를 때는 **반드시 상위 `orchestration/{policies,changelog,rationale}.md` 를 참조**한다. 본 디렉토리의 파일은 다음 두 경우에만 참조한다:

1. **historical compare** — RWHarness 의 정본 룰이 source 환경에서 어떻게 진화했는지 추적할 때
2. **incident archaeology** — 과거 incident-driven 변경(`HARNESS-CHG-2026MMDD-NN` 식별자)의 원래 컨텍스트를 확인할 때

## 본 디렉토리에 변경을 가하지 않는 원칙

- **수정 금지** — 원본 보존이 목적. 단어 일반화·추상어 정리 등 RWHarness 의 다른 docs/ 와 일관된 정리 작업에서 의도적으로 *제외*한다.
- **확장 금지** — 새 파일 추가도 하지 않는다. 새 운영 룰은 상위 `orchestration/` 에 추가.
- **삭제 금지** — 본 스냅샷은 v1.0.0 release 이후에도 보존. 단, archive 디렉토리로 이동 가능 (Phase 3+ 검토).

## 문서 안의 식별자 (개인 이름·프로젝트명) 보존 사유

본 디렉토리의 파일들에는 RWHarness 의 다른 docs/ 와 달리 다음 식별자가 그대로 남아있을 수 있다:

- 특정 사용자 이름 (예: `dongchan`)
- 특정 프로젝트명 (예: `jajang`, `memoryBattle`)
- 특정 절대 경로 (예: `/Users/dc.kim/...`)
- `HardcarryDryRun` 같은 임시 과제 식별자

이들은 **incident archaeology 의 정확성**을 위해 보존한다. 외부 사용자(마켓플레이스 install 후 본 디렉토리를 우연히 본 경우)에게 노이즈일 수 있으나, 본 디렉토리의 정체성("source 환경의 *실제* 운영 기록")을 살리기 위함이다. RWHarness 의 *현재* 운영에는 영향 없음.

## Reference

- 본 디렉토리 마이그레이션 sub-commit: `HARNESS-CHG-20260427-02` [1.6] (commit `147b33b`)
- 본 README 추가 sub-commit: `HARNESS-CHG-20260427-04` [3.2]
- 정체성 결정 근거: [`../rationale.md`](../rationale.md) 의 `HARNESS-CHG-20260427-04` 4섹션
