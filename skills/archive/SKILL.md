---
name: archive
description: >
  10-projects/ISS-*/ 를 스캔하여 완료 조건(hub status: closed + 모든 step status: done)을
  충족하는 ISS를 찾아 40-archives/ 로 일괄 이동. ISS 아카이브 작업 시작 시 사용.
  Do NOT use for open/in-progress ISS — only closed hub + all steps done.
  Keywords: archive, 아카이브, ISS 완료, 이슈 정리, iss archive, 완료 이동
allowed-tools: Read, Write, Bash, Grep, Glob
---

# sr-obsidian:archive — 완료 ISS 일괄 아카이브

## Phase 1: 스캔

`10-projects/` 하위 모든 `ISS-*/` 디렉토리를 탐색한다.

```bash
# hub status 확인
grep -r "^status:" 10-projects/ISS-*/ISS-*.md 2>/dev/null

# step status 확인
grep -r "^status:" 10-projects/ISS-*/steps/*.md 2>/dev/null
```

**완료 기준** (둘 다 충족해야 아카이브 대상):
1. hub 파일 `status: closed`
2. `steps/` 하위 모든 파일 `status: done`

steps/ 가 없는 ISS는 hub `status: closed` 단독으로 판단.

## Phase 2: 결과 보고

스캔 후 다음 형식으로 출력:

```
아카이브 대상 (N건)
  ✅ ISS-051 — paypro PSP ITSM step 의존성 교정
  ✅ ISS-0XX — ...

보류 (미완료 step 있음)
  ⏳ ISS-0YY — ... (step-03 in-progress)
  ⏳ ISS-0ZZ — ... (hub: open)
```

대상이 0건이면 "아카이브할 ISS 없음" 출력 후 종료.

## Phase 3: 사용자 확인

목록 출력 후 사용자 확인을 받는다.

> "위 N건을 40-archives/로 이동합니다. 진행할까요?"

## Phase 4: 실행 (확인 후)

sr-harness 워크플로우 준수.

### 4-1. GH Issue 생성
```bash
gh issue create \
  --title "chore: 완료 ISS 일괄 아카이브 (N건)" \
  --body "완료 ISS를 10-projects/ → 40-archives/ 이동.\n\n대상:\n- ISS-0XX ...\n- ISS-0YY ..."
```

### 4-2. Feature 브랜치 생성

> **worktree 사용 금지** (vault 전용 규칙) — worktree 안 파일은 머지 전까지 Obsidian vault 루트에서 보이지 않아 PR 리뷰 단계에서 노트 확인이 불가능하다. 반드시 main에서 feature 브랜치를 직접 체크아웃한다.

```bash
git checkout main && git pull origin main
git checkout -b feature/{ISSUE_NUM}-archive-iss-batch
```

### 4-3. git mv (대상 ISS 각각)
```bash
git mv "10-projects/ISS-{NNN}-{slug}" "40-archives/ISS-{NNN}-{slug}"
```

### 4-4. Commit → Push → PR → Merge
```bash
git commit -m "chore: 완료 ISS 일괄 아카이브 (#{ISSUE_NUM})"
git push origin feature/{ISSUE_NUM}-archive-iss-batch
gh pr create --title "chore: 완료 ISS 일괄 아카이브" --body "Closes #{ISSUE_NUM}" \
  --head feature/{ISSUE_NUM}-archive-iss-batch
gh pr merge {PR_NUM} --merge --delete-branch
git checkout main && git pull origin main
```

## 판단 기준

| 상황 | 처리 |
|------|------|
| steps/ 일부만 done | 보류 — 모든 step이 done이어야 이동 가능 |
| hub closed이나 step in-progress/ready 있음 | 보류 — step 완료 후 재실행 |
| steps/ 없는 ISS | hub `status: closed` 단독으로 아카이브 가능 |
| 아카이브 대상 0건 | "아카이브할 ISS 없음" 출력 후 종료 |
| 이동 후 내부 링크 깨짐 | 이 스킬 범위 밖 — 수동 수정 또는 sr-obsidian:migrate 사용 |
