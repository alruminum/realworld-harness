# cross-guard silent dependency fixture

5번째 위험 시나리오 자동화 재현 케이스.

## 시나리오 A — skill-gate live.json 쓰기 silent 실패 → agent-boundary false-block

1. skill-gate.py 가 set_active_skill 호출
2. live.json 디렉토리 권한 문제로 쓰기 실패 (silent pass)
3. live.json.skill = None 상태
4. agent-boundary 가 active_agent = None 으로 engineer 인식 실패
5. 결과: engineer 정상 작업인데 통과 불가 (false-block)

## 시나리오 B — agent-gate live.json 쓰기 실패 → issue-gate/commit-gate false-pass

1. agent-gate 가 HARNESS_ACTIVE flag 생성
2. live.json 쓰기 실패로 agent 정보 미기록
3. commit-gate Gate 5 / issue-gate 가 live.json.agent 없음 → harness 비활성으로 오인
4. 결과: 권한 없는 커밋/이슈 작업이 통과 (false-pass)
