---
name: archive
description: >
  10-projects/ISS-*/ 를 스캔하여 완료 조건(hub status: closed + 모든 step status: done)을
  충족하는 ISS를 찾아 40-archives/ 로 일괄 이동. ISS 아카이브 작업 시작 시 사용.
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

### 4-2. Worktree 생성
```bash
git worktree add -b feature/{ISSUE_NUM}-archive-iss-batch \
  .claude/worktrees/archive-iss-batch main
```

### 4-3. git mv (대상 ISS 각각)
```bash
git mv "10-projects/ISS-{NNN}-{slug}" "40-archives/ISS-{NNN}-{slug}"
```

### 4-4. Commit → Push → PR → Merge
```bash
git commit -m "chore: 완료 ISS 일괄 아카이브 #{ISSUE_NUM}"
git push origin feature/{ISSUE_NUM}-archive-iss-batch
gh pr create --title "chore: 완료 ISS 일괄 아카이브" --body "Closes #{ISSUE_NUM}" \
  --head feature/{ISSUE_NUM}-archive-iss-batch
gh pr merge {PR_NUM} --squash
git pull origin main
git worktree remove .claude/worktrees/archive-iss-batch --force
```

## 주의사항

- steps/ 가 일부만 done인 ISS는 절대 이동하지 않는다
- hub status가 closed여도 step이 하나라도 in-progress/ready면 보류
- 이동 후 기존 내부 링크 수정은 이 스킬 범위 밖 (수동 또는 별도 작업)
