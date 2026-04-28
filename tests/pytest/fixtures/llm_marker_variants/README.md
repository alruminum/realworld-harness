# LLM 마커 변형 corpus

parse_marker alias map 검증용 fixture.
alias map 에 등록된 변형 마커가 canonical 마커로 올바르게 흡수되는지 확인.

## 변형 종류

| 변형 마커 | canonical 대상 |
|---|---|
| PLAN_LGTM | PLAN_VALIDATION_PASS |
| PLAN_OK | PLAN_VALIDATION_PASS |
| PLAN_APPROVE | PLAN_VALIDATION_PASS |
| DESIGN_LGTM | DESIGN_REVIEW_PASS |
| APPROVE | PASS |
| REJECT | FAIL |
