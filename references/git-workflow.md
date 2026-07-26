# Vault Git 워크플로우 (공통 절차)

sr-labs vault 노트 작업의 표준 Issue→Branch→PR 절차.
각 스킬은 이 절차에 스킬별 제목·브랜치 패턴만 대입한다.

## 규칙

- 1 Issue = 1 Branch = 1 PR. 커밋 메시지에 `(#N)` 필수 — 없으면 훅이 차단.
- 브랜치는 반드시 **main 최신에서** 분기. worktree 금지(머지 전까지 Obsidian에서 파일이 안 보임), feature 브랜치 체인 금지.
- PR body에 `Closes #N` 필수 — 머지 시 이슈 자동 종료(self-issue open 누수 차단).
- 같은 목적의 오픈 이슈가 이미 있으면 **재사용**하고 신규 생성하지 않는다.

## 절차

```bash
# 1. 이슈 재사용 조회 → 없으면 생성
ISSUE=$(gh issue list --repo SeokRae/knowledge-labs --state open \
  --search "{제목 키워드} in:title" --json number --jq '.[0].number' 2>/dev/null)
[ -z "$ISSUE" ] && ISSUE=$(gh issue create --repo SeokRae/knowledge-labs \
  --title "{prefix}: {제목}" --body "{요약}" | grep -oE '[0-9]+$')

# 2. main에서 브랜치
git checkout main && git pull origin main
git checkout -b feature/${ISSUE}-{slug}

# 3. 노트 작성 후 커밋·Push·PR
git add {파일}
git commit -m "{prefix}: {제목} (#${ISSUE})"
git push -u origin HEAD
gh pr create --repo SeokRae/knowledge-labs \
  --title "{prefix}: {제목}" --body "Closes #${ISSUE}"

# 4. 스킬이 머지까지 담당할 때만
gh pr merge --merge --delete-branch
git checkout main && git pull origin main
```

커밋 prefix: `docs:`(노트 추가·수정) · `chore:`(구조 변경·이동) · `fix:`(오류 수정)
