# sr-obsidian

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> Claude Code 플러그인 — Obsidian 프로젝트 문서 자동화 스킬 모음

## 구조

```
.claude-plugin/
  plugin.json       # 스킬 목록, 버전 (설치 시 사용)
  marketplace.json  # 마켓플레이스 메타데이터 + 버전
skills/
  {skill-name}/
    SKILL.md        # 스킬 정의 (frontmatter + 실행 절차)
    references/     # (선택) 템플릿, 형식처럼 SKILL.md에서 링크해 읽는 문서
    scripts/        # (선택) 판정, 치환처럼 결정적으로 돌려야 하는 Python 스크립트 (예: archive/scripts/scan.py, migrate/scripts/relink.py)
agents/             # 스킬이 띄우는 서브에이전트 정의 (예: handover-collector.md)
references/         # 여러 스킬이 같이 쓰는 공통 문서 (git-workflow.md 등)
```

`skills/*/scripts/`의 스크립트는 설치 캐시 경로에서 실행됩니다. SKILL.md는 `CLAUDE_PLUGIN_ROOT`를 먼저 보고, 없으면 설치 캐시에서 스크립트 파일을 찾아 플러그인 루트를 정해요(archive, migrate SKILL.md의 `ROOT=` 루트 해석 스니펫 참고). 스크립트를 추가하거나 옮기면 배포(버전 bump, 태그, marketplace pull, plugin update)까지 끝나야 설치본에서 보입니다. 실행하면 생기는 `__pycache__/`는 `.gitignore`로 제외합니다.

## 스킬 추가 체크리스트

새 스킬을 추가할 때 **반드시** 같은 PR에 포함:

- [ ] `skills/{name}/SKILL.md` 생성
- [ ] `plugin.json` → `skills` 배열에 `"./skills/{name}"` 추가
- [ ] `plugin.json` → `version` MINOR 올리기
- [ ] `marketplace.json` → `metadata.version` + `plugins[0].version` 동일하게 올리기
- [ ] `README.md` / `README.ko.md` 스킬 표에 추가

버전 bump 누락 시 설치본과 소스가 불일치한다 — 버전 bump는 별도 PR 금지.

## 버전 규칙 (semver)

| 변경 | 올릴 자리 |
|------|----------|
| 스킬 추가 / 기능 확장 | MINOR |
| 버그 픽스 / 문서 수정 | PATCH |
| 스킬 제거 / 인터페이스 변경 | MAJOR |

## 릴리즈 절차 (PR 머지 후)

```bash
git checkout main && git pull origin main
git tag -a v{version} -m "v{version}: {한 줄 요약}"
git push origin v{version}
gh release create v{version} --title "v{version}" --generate-notes
```

## 작업 흐름

```
gh issue create → git checkout -b feature/{N}-{desc} → 구현 + 버전 bump
→ git commit -m "... (#N)" → gh pr create (Closes #N) → gh pr merge → 릴리즈 태그
```

커밋 prefix: `feat:` (스킬 추가), `fix:` (버그), `chore:` (설정·버전 bump), `docs:` (문서)
