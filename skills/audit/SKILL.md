---
name: audit
description: >
  프로젝트 문서 구조 검증(읽기 전용): 표준 docs 폴더 세트 준수, 핵심 파일 존재, HTML/MD 혼재, 링크 무결성. "구조 확인", "docs 점검", "audit" 요청 시 사용.
  Do NOT use for 파일 이동·수정 → sr-obsidian:migrate.
  Do NOT use for wiki/permanent 노트 품질 검사 → sr-obsidian:lint-wiki.
  Keywords: audit, 구조 검증, 폴더 점검, 링크 확인, HTML 혼재
allowed-tools: Read, Bash
---

# sr-obsidian:audit — 프로젝트 구조 검증

프로젝트 폴더가 표준 구조를 충족하는지 체크리스트로 검증한다.

## 표준 기준

기준은 vault 선언을 그대로 따르고, 이 스킬에서 새 규칙을 만들지 않습니다. 예전 체크리스트는 vault docs 표준보다 앞선 폴더 세트(runbook 등)를 기준으로 해서 서비스 7곳 모두 오탐이 났어요(#8609).

| 기준 | 출처 (vault 루트 기준) |
|------|------|
| `docs/` 하위 폴더 세트 | `CLAUDE.md` 폴더 구조의 `docs/` 선언, `.claude/rules/wbs-docs-design.md` |
| `docs/` 루트에 파일 금지, 프로젝트에 없는 유형의 폴더는 만들지 않음 | `.claude/rules/wbs-docs-design.md`, `30-resources/methodology/dev-workflow/프로젝트 문서화 구조 표준.md` §2 |
| 다이어그램 HTML + 페어드 MD | `20-areas/CLAUDE.md` 다이어그램 파일 패턴 |

표준 `docs/` 폴더 세트 (12개):

`overview` `kickoff` `constraints` `session-design` `architecture` `operations` `specs` `config` `reports` `adr` `components` `_archive`

- `components/` 는 멀티모듈 서비스에만 둡니다.
- `kickoff/` 에는 착수 보고 HTML 슬라이드가 허용돼요. 그래서 HTML 혼재 검사(D-2)에서 뺍니다.
- 예전 세트의 `runbook/` 은 표준에 없습니다. 운영 문서는 `operations/` 에 둬요.
- 20-areas 구조 정본(#8607 D10)이 미결이라 WBS 파일명 두 형식을 모두 인정하고, 표준 세트 밖 폴더는 ❌ 가 아니라 ⚠️ 로 표시합니다.

## 실행 절차

### Step 1. 대상 프로젝트 확인

명령은 vault 루트에서 실행합니다. 입력은 `20-areas/` 아래 경로예요(예: `payment/psp`).

```bash
PROJECT_PATH="20-areas/{입력 경로}"   # 예: 20-areas/payment/psp
ls "$PROJECT_PATH"
```

### Step 2. 체크리스트 실행

각 항목을 순서대로 확인하고 결과를 `✅ / ❌ / ⚠️` 로 표기.

#### A. 핵심 파일

```bash
# 허브 노트
find "$PROJECT_PATH" -maxdepth 1 -type f -name "*프로젝트 현황.md"

# WBS: "{service} WBS.md" 와 소문자 "wbs.md" 모두 인정 (대소문자 무시, #8609)
find "$PROJECT_PATH" -maxdepth 1 -type f -iname "*wbs.md"
```

| # | 항목 | 결과 |
|---|------|------|
| A-1 | 허브 노트 (`{project-id} 프로젝트 현황.md`) 존재 | |
| A-2 | WBS (`{service} WBS.md` 또는 `wbs.md`) 존재 | |

WBS 는 `grep "WBS"` 로 찾으면 소문자 `wbs.md` 를 쓰는 서비스(FIE, paypro, untact-qa)가 없는 것으로 잡힙니다. `wbs-docs-design.md` 규칙도 `**/WBS.md` 와 `**/wbs.md` 를 함께 받으니 대소문자를 무시해서 찾아요.

#### B. docs/ 하위 폴더

```bash
STD=" overview kickoff constraints session-design architecture operations specs config reports adr components _archive "
# glob 반복(docs/*/)은 docs/ 가 없거나 하위 폴더가 없으면 zsh 에서 'no matches found' 로 멈춘다. D-1 처럼 find 로 돈다
find "$PROJECT_PATH/docs" -mindepth 1 -maxdepth 1 -type d ! -name '.*' 2>/dev/null | sort | while IFS= read -r d; do
  name=$(basename "$d")
  case "$STD" in
    *" $name "*) echo "✅ $name" ;;
    *) [ "$name" = runbook ] && echo "⚠️ 표준 세트 밖: runbook (operations/ 로 이관 대상)" \
                             || echo "⚠️ 표준 세트 밖: $name" ;;
  esac
done
```

| # | 항목 | 결과 |
|---|------|------|
| B-1 | `docs/` 하위 폴더가 모두 표준 세트 안에 있음 (밖이면 ⚠️) | |
| B-2 | (정보) 있는 표준 폴더 목록 | |

표준 폴더가 없다는 이유로는 실패 처리하지 않습니다. 구조 표준이 "프로젝트에 없는 유형의 폴더는 만들지 않는다"고 정하고 있어서, 폴더마다 존재를 요구하면 모든 서비스가 걸려요. 표준 세트 밖 폴더를 어디로 옮길지는 migrate 계획에서 사용자와 정합니다.

#### C. docs/ 직하 파일 혼재 검출

```bash
# docs/ 루트에는 파일을 두지 않는다 (wbs-docs-design.md). 숨김 파일만 제외
find "$PROJECT_PATH/docs" -maxdepth 1 -type f ! -name ".*"
```

| # | 항목 | 결과 |
|---|------|------|
| C-1 | `docs/` 직하에 파일 없음 | |

#### D. diagrams/ 무결성

```bash
# diagrams/ 의 HTML 마다 페어드 MD 확인. diagrams/ 나 HTML 이 없으면 아무것도 출력하지 않는다
find "$PROJECT_PATH/diagrams" -type f -name "*.html" 2>/dev/null | while IFS= read -r html; do
  [ -f "${html%.html}.md" ] && echo "✅ ${html#"$PROJECT_PATH"/}" || echo "❌ missing MD: ${html#"$PROJECT_PATH"/}"
done

# docs/ 안의 HTML. kickoff/ 는 HTML 슬라이드가 허용되는 폴더라 뺀다
find "$PROJECT_PATH/docs" -type f -name "*.html" -not -path "*/docs/kickoff/*" 2>/dev/null
```

| # | 항목 | 결과 |
|---|------|------|
| D-1 | `diagrams/` 내 HTML마다 페어드 MD 존재 | |
| D-2 | `docs/` 에 HTML 파일 없음 (`docs/kickoff/` 제외) | |

예전 `for html in diagrams/*.html` 반복은 HTML 이 하나도 없으면 패턴 문자열 자체를 파일로 보고 ❌ 를 냈습니다. `find` 로 바꿔서 diagrams/ 가 없는 서비스도 오탐 없이 지나가요. B 검사도 같은 이유로 glob 대신 `find` 를 씁니다. 이 환경의 Bash 도구는 zsh 로 돌고, zsh 는 매치 없는 glob 에서 명령 전체를 멈추기 때문이에요.

#### E. 히스토리

```bash
ls "$PROJECT_PATH/docs/adr/" 2>/dev/null | wc -l
ls "$PROJECT_PATH/meetings/" 2>/dev/null | wc -l
```

| # | 항목 | 결과 |
|---|------|------|
| E-1 | `docs/adr/` 에 ADR 파일 존재 (없으면 ⚠️) | |
| E-2 | `meetings/` 존재 (없으면 ⚠️) | |

### Step 3. 결과 요약

```
✅ 통과: {N}개
❌ 실패: {N}개
⚠️ 경고: {N}개 → 선택적 보완

실패, 경고 항목:
  - {항목}: {조치 방법}
```

| 항목 | 조치 방법 |
|------|-----------|
| B-1 표준 세트 밖 폴더, C-1 `docs/` 직하 파일, D-2 `docs/` 안 HTML | `sr-obsidian:migrate` 로 이관 |
| A-1 허브 없음 | `sr-obsidian:hub` (신규 서비스면 `sr-obsidian:scaffold`) |
| A-2 WBS 없음 | `sr-obsidian:wbs` |
| D-1 페어드 MD 없음 | `20-areas/CLAUDE.md` 다이어그램 파일 패턴대로 MD 작성 |

B-1, C-1, D-2 가 걸리면 `sr-obsidian:migrate` 실행을 제안합니다. A 와 D-1 은 파일 이동으로 풀리지 않으니 표의 조치로 안내해요.
