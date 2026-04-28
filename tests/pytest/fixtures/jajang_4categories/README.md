# jajang 4 카테고리 재현 케이스

Issue #13 jajang 실측에서 발견된 4가지 결함 카테고리.

## path 카테고리
- apps/api/src/ 경로가 engineer_scope 에 없어 engineer 차단 (false-deny)
- monorepo 루트 경로 패턴 누락

## marker 카테고리
- PLAN_LGTM 마커가 PLAN_VALIDATION_PASS 로 인식 안 됨 (alias map 없음)
- validator 출력 마커 변형 흡수 실패

## state 카테고리
- live.json.skill silent 쓰기 실패 → downstream false-block cascade
- HARNESS_ACTIVE flag stale 잔존 → engineer 작업 차단

## scope 카테고리
- agent-boundary 와 commit-gate Gate 5 가 서로 다른 engineer_scope source 사용
- partial V2 활성 시 cross-flag 호환성 깨짐 (§4.8)
