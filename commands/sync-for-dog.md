---
name: sync-for-dog
description: RWHarness dogfooding 환경에서 source(`~/project/RWHarness`) → marketplace clone → plugin cache 양방향 동기화. RWHarness 작업 후 jajang 등 다른 프로젝트에서 즉시 반영하려면 이 스킬을 실행한다. 유저가 "동기화", "sync", "도그푸딩 반영", "/sync-for-dog" 등을 말할 때 사용.
---

# /sync-for-dog

RWHarness 자체를 개발하면서 jajang 등에 즉시 반영해야 할 때 (dogfooding) 의 동기화 진입점. 플러그인 매니저가 symlink 를 자동 정리하는 호환 문제 때문에 cache 와 marketplace 를 *real directory* 로 유지하면서, 본 스킬이 source → marketplace → cache 로 일괄 mirror 한다.

## 언제 쓰나

- RWHarness 에 commit 직후, 다른 프로젝트(jajang 등) 의 다음 세션에서 *즉시* 반영하고 싶을 때
- `Plugin directory does not exist` 에러나 stale 한 동작 (예전 prompt 사용) 보고 받았을 때
- HARNESS-CHG-37 의 SessionStart auto-pull 만으론 cache 까지는 동기화 안 되므로 수동 step 으로 보강

## 동작

1. RWHarness 가 검색 가능한 위치에 있는지 확인 (`~/project/RWHarness`)
2. RWHarness 의 commit 상태 확인 — uncommitted 면 경고만 띄우고 진행 (working tree 가 marketplace/cache 로 그대로 복사됨)
3. marketplace 클론 → RWHarness 동기화 (`git pull --ff-only`)
4. cache 디렉토리 → marketplace 와 동일하게 mirror (rsync)
5. 검증 — 핵심 파일 (`hooks/session_state.py`, `agents/product-planner.md`) 의 cache 본이 RWHarness 본과 동일

## 실행

Bash 도구로 아래 스크립트 실행.

```bash
bash << 'BASH'
set -e

SOURCE="$HOME/project/RWHarness"
MARKET="$HOME/.claude/plugins/marketplaces/realworld-harness"
CACHE_PARENT="$HOME/.claude/plugins/cache/realworld-harness/realworld-harness"
CACHE="$CACHE_PARENT/0.1.0-alpha"

# 1. source 존재 확인
if [ ! -d "$SOURCE/.git" ]; then
  echo "[sync-for-dog] ERROR: $SOURCE 가 git repo 아님 — 경로 수정 필요" >&2
  exit 1
fi

# 2. uncommitted 경고
cd "$SOURCE"
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "[sync-for-dog] ⚠️  RWHarness 에 uncommitted 변경 있음 — working tree 그대로 mirror 됨" >&2
fi

# 3. marketplace 동기화
if [ -d "$MARKET/.git" ]; then
  echo "[sync-for-dog] marketplace pull..."
  git -C "$MARKET" pull --ff-only --quiet 2>&1 | grep -v "Already up to date" || true
else
  echo "[sync-for-dog] ERROR: marketplace clone 부재 ($MARKET) — `/plugin reinstall` 필요" >&2
  exit 1
fi

# 4. cache mirror (real dir 유지)
mkdir -p "$CACHE_PARENT"
if [ ! -d "$CACHE" ]; then
  echo "[sync-for-dog] cache 부재 — 새로 생성"
  cp -R "$MARKET" "$CACHE"
else
  echo "[sync-for-dog] cache mirror..."
  rsync -a --delete --exclude='.git' "$MARKET/" "$CACHE/"
fi

# 5. 검증
echo ""
echo "[sync-for-dog] 검증:"
for f in hooks/session_state.py agents/product-planner.md harness/core.py; do
  if diff -q "$SOURCE/$f" "$CACHE/$f" > /dev/null 2>&1; then
    echo "  ✅ $f"
  else
    echo "  ❌ $f — drift 잔존" >&2
  fi
done

# 6. 요약
SOURCE_HEAD=$(git -C "$SOURCE" rev-parse --short HEAD 2>/dev/null || echo "?")
MARKET_HEAD=$(git -C "$MARKET" rev-parse --short HEAD 2>/dev/null || echo "?")
echo ""
echo "[sync-for-dog] HEAD: source=$SOURCE_HEAD market=$MARKET_HEAD cache=mirror"
echo "[sync-for-dog] 완료. 다른 프로젝트(jajang 등)에서 새 세션 시작 시 fix 반영됨."
BASH
```

## 주의사항

- **cache 는 real directory** 로 유지 (symlink 시 Claude Code 플러그인 매니저가 자동 삭제 사고 발생 — 2026-04-28 사고). 본 스킬은 그 호환을 지키면서도 동기화 자동화.
- 본 스킬은 **수동 트리거** — SessionStart auto-pull (HARNESS-CHG-37) 는 marketplace 까지만 동기화. cache 는 본 스킬을 명시적으로 호출해야 갱신.
- RWHarness uncommitted 변경도 mirror 됨 (working tree 기준 rsync). 즉 commit 안 하고도 dogfooding 가능. 단 push 안 된 변경은 jajang 의 SessionStart auto-pull 다음 세션엔 사라짐 → 본격 dogfooding 시 commit + push 후 본 스킬 호출 권장.
- bak 디렉토리 (`*.cache.bak`, `*.clone.bak`) 가 cache_parent 에 있으면 rsync 가 영향 없음 (별도 path).

## 트러블슈팅

- **`Plugin directory does not exist` 에러 지속**: cache 가 또 사라졌다는 뜻. 본 스킬 재실행하면 복원.
- **drift 가 검증 단계에서 잔존**: marketplace 가 origin 과 안 맞을 가능성. `git -C marketplace pull` 직접 실행 후 재시도.
- **rsync 미설치 환경**: `cp -R` fallback 으로 변경 가능 (현재 macOS 기본 rsync 가정).
