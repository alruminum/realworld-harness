# Bugfix Validation

`@MODE:VALIDATOR:BUGFIX_VALIDATION` → `BUGFIX_PASS` / `BUGFIX_FAIL`

```
@PARAMS: { "impl_path": "bugfix impl 경로", "src_files": "수정된 소스 파일 경로", "vitest_result?": "vitest 실행 결과" }
@OUTPUT: { "marker": "BUGFIX_PASS / BUGFIX_FAIL", "fail_items?": "문제 목록 (FAIL 시)" }
```

**목표**: 경량 버그 수정이 원인을 해결했고 회귀를 발생시키지 않았는지 검증한다.
Code Validation의 경량 버전. 전체 스펙 일치 대신 수정 범위만 검증.

### 작업 순서

1. bugfix impl 파일 읽기 (`docs/bugfix/#N-slug.md`)
2. 수정된 소스 파일 읽기
3. vitest 결과 확인 (전달받은 경우)
4. 아래 체크리스트 수행

### Bugfix Validation 체크리스트

#### A. 원인 해결 — 미충족 시 FAIL

| 항목 | 확인 기준 |
|---|---|
| 수정 위치 일치 | impl에 명시된 파일·함수가 실제로 수정되었는가 |
| 원인 해소 | impl에 기술된 원인이 수정으로 해결되는가 (로직 추적) |
| 범위 초과 금지 | impl에 명시되지 않은 파일이 수정되지 않았는가 |

#### B. 회귀 안전 — 미충족 시 FAIL

| 항목 | 확인 기준 |
|---|---|
| vitest 통과 | vitest run 결과가 전체 통과인가 |
| 기존 로직 보존 | 수정 주변의 기존 로직이 의도치 않게 변경되지 않았는가 |
| 타입 안전성 | `as any`, `@ts-ignore` 등 타입 우회가 새로 추가되지 않았는가 |

### Code Validation과의 차이

| 항목 | Code Validation | Bugfix Validation |
|---|---|---|
| 스펙 일치 검증 | 전체 (생성 파일, Props, 함수 시그니처, 핵심 로직) | **수정 위치·원인 해소만** |
| 의존성 규칙 | 래퍼 사용, 외부 패키지, 모듈 경계, DB 스키마 | **범위 초과 금지만** |
| 코드 품질 심층 | 12항목 시니어 관점 검토 | **타입 안전성만** |
| 체크리스트 항목 수 | ~25개 | **6개** |

### 판정 기준

- **BUGFIX_PASS**: A/B 모두 통과
- **BUGFIX_FAIL**: A 또는 B에서 하나라도 미충족

### 출력 형식

마커는 **출력 마지막 줄에 정형(`---MARKER:BUGFIX_PASS---` 또는 `---MARKER:BUGFIX_FAIL---`)** 으로 둔다. `LGTM` / `BUGFIX_LGTM` / `PASS` 변형 금지 — preamble.md 의 다른 에이전트 예시와 혼동하지 말 것. 정확한 글자만 사용해야 `parse_marker` 가 인식한다.

```
### A. 원인 해결
| 항목 | 결과 | 비고 |
|---|---|---|
| 수정 위치 일치 | PASS/FAIL | ... |
| 원인 해소 | PASS/FAIL | ... |
| 범위 초과 금지 | PASS/FAIL | ... |

### B. 회귀 안전
| 항목 | 결과 | 비고 |
|---|---|---|
| vitest 통과 | PASS/FAIL | ... |
| 기존 로직 보존 | PASS/FAIL | ... |
| 타입 안전성 | PASS/FAIL | ... |

### FAIL 원인 요약 (FAIL 시만)
1. [구체적 문제 + 수정 요청]

---MARKER:BUGFIX_PASS---
```

> PASS 일 땐 `---MARKER:BUGFIX_PASS---`, FAIL 일 땐 `---MARKER:BUGFIX_FAIL---`. *둘 중 하나만* 마지막 줄에.
