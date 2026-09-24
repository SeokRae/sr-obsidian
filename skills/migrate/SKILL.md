---
name: migrate
description: >
  비표준 프로젝트 구조를 표준으로 이관: docs/ 직하 파일과 표준 세트 밖 폴더 → 유형 폴더, HTML → diagrams/ 이동, vault 전체 링크 갱신. "구조 정리", "파일 이동", "migrate", "docs 재구성" 요청 시 사용.
  Do NOT use for 읽기 전용 구조 검증 → sr-obsidian:audit.
  Do NOT use for 완료 ISS의 40-archives/ 이동 → sr-obsidian:archive.
  Keywords: migrate, 이관, 파일 이동, 구조 정리, 재구성
allowed-tools: Read, Write, Bash, Edit
---

# sr-obsidian:migrate — 구조 이관

`sr-obsidian:audit` 결과를 기반으로 비표준 파일·폴더를 표준 위치로 이동한다.

## 표준 기준

`sr-obsidian:audit` 의 "표준 기준" 절과 같은 기준을 씁니다. 표준 `docs/` 폴더 세트는 vault `CLAUDE.md` 선언을 따른 12개예요.

`overview` `kickoff` `constraints` `session-design` `architecture` `operations` `specs` `config` `reports` `adr` `components` `_archive`

| audit 항목 | 이관 방법 |
|------------|-----------|
| C-1 `docs/` 직하 파일 | 내용에 맞는 표준 유형 폴더 `docs/{type}/` 로 |
| B-1 표준 세트 밖 폴더 | 대응하는 표준 유형 폴더로. `runbook/` 은 `operations/` 로 |
| D-2 `docs/` 안 HTML | `diagrams/` 로. `docs/kickoff/` 의 HTML 슬라이드는 옮기지 않음 |

어느 유형 폴더로 보낼지 기계적으로 정해지지 않는 파일은 계획표에 후보와 근거를 적고 사용자가 고르게 합니다. 20-areas 구조 정본(#8607 D10)이 미결이라 `docs/` 바로 아래에는 표준 세트 밖의 새 폴더를 만들지 않아요. 유형 폴더 안의 하위 폴더(예: `specs/{module}/`)는 기존 구성을 따릅니다.

## 실행 절차

### Step 1. audit 결과 확인

`sr-obsidian:audit` 를 먼저 실행하거나 현재 구조를 스캔:

```bash
PROJECT_PATH="20-areas/{입력 경로}"   # 예: 20-areas/payment/psp (vault 루트 기준)
find "$PROJECT_PATH" -maxdepth 3 | sort
```

### Step 2. 이관 계획 생성

파일별로 이동 계획을 테이블로 제시:

| 현재 위치 | 이동 위치 | 사유 |
|-----------|-----------|------|
| `docs/01-component.md` | `docs/specs/01-component.md` | specs/ 분류 |
| `docs/analysis.md` | `docs/architecture/analysis.md` | architecture/ 분류 |
| `docs/runbook/` | `docs/operations/` | runbook 은 표준 세트 밖, 운영 문서는 operations/ |
| `docs/report.html` | `diagrams/report.html` | HTML → diagrams/ |
| `docs/kickoff/*.html` | (이동 안 함) | kickoff/ 는 HTML 슬라이드 허용 |
| `docs/itsm/` | (보류) | 보류(미커밋): 폴더 안에 미커밋 변경 |

**이동 대상의 미커밋 변경 검사.** 세션들이 워킹트리를 공유해서, 옮길 파일에 다른 세션이 고치던 내용이나 아직 커밋하지 않은 새 파일이 있을 수 있어요. 그대로 옮기면 남의 미커밋 작업이 migrate 커밋에 실립니다. 계획표의 현재 위치를 모두 넣어 검사하고, 폴더 쌍이면 폴더를 넣습니다.

```bash
# 한 줄이라도 나오면 그 경로는 보류(미커밋). 폴더째 옮기면 미추적(??) 파일도 같이 옮겨지니 포함해서 본다
git -C /Users/sr/obsidian/sr-labs status --porcelain --untracked-files=all -- \
  "$PROJECT_PATH/docs/{file}" "$PROJECT_PATH/docs/runbook"
```

걸린 항목은 계획표에 `보류(미커밋)` 로 적고 이동에서 뺍니다. 폴더 쌍에 걸리면 폴더째 보류하거나, 걸린 파일을 뺀 파일 쌍으로 나눠요. 나누면 원래 폴더가 비지 않으니 Step 5 정리 대상도 아닙니다. 사용자가 그 변경이 이번 작업의 것이라고 확인한 경우에만 이동에 넣습니다. `.gitignore` 에 걸린 파일은 이 명령에 나오지 않지만 폴더째 옮기면 같이 옮겨지므로, 아래 relink dry-run 의 `[dirty-move]` 로 함께 확인해요.

계획표와 함께 Step 4 링크 갱신의 dry-run 결과(고칠 파일 수, 수동 확인 항목)도 보여 줍니다. 스크립트는 `git mv` 전에도 돌릴 수 있어서, 사용자가 영향 범위를 보고 결정할 수 있어요. dry-run 이 `[dirty-move]` 를 내면 위 검사와 같게 그 항목을 보류합니다.

**사용자 확인을 받은 후 실행.**

### Step 3. 파일 이동 실행

`git mv` 는 대상 폴더가 없으면 실패합니다. 옮길 파일이 들어갈 폴더만 직전에 만들어요. 백업 사본은 만들지 않고 git 을 안전망으로 씁니다(#8607 D4).

```bash
# git mv로 이동 (히스토리 보존)
mkdir -p "/Users/sr/obsidian/sr-labs/$PROJECT_PATH/docs/{subfolder}"
git -C /Users/sr/obsidian/sr-labs mv \
  "$PROJECT_PATH/docs/{file}" \
  "$PROJECT_PATH/docs/{subfolder}/{file}"
```

폴더 통째 이동 (예: `runbook/` → `operations/`). `operations/` 가 이미 있으면 폴더째 옮기지 말고 파일 단위로 옮깁니다:
```bash
git -C /Users/sr/obsidian/sr-labs mv "$PROJECT_PATH/docs/runbook" "$PROJECT_PATH/docs/operations"
```

HTML 파일 이동 (`docs/kickoff/` 제외):
```bash
git -C /Users/sr/obsidian/sr-labs mv \
  "$PROJECT_PATH/docs/{file}.html" \
  "$PROJECT_PATH/diagrams/{file}.html"
```

### Step 4. 링크 업데이트

이동한 파일을 가리키는 링크를 **vault 전체**에서 고칩니다. 예전처럼 서비스 폴더 안에서만 `grep` 과 `perl` 로 치환하면 서비스 밖 참조(추적 파일 기준 32쌍)가 깨진 채 남고, 코드 블록이나 기록 속 평문 경로까지 바뀌어요(#8609). 링크 갱신은 플러그인의 `scripts/relink.py` 가 맡습니다.

```bash
# 플러그인 루트 해석. CLAUDE_PLUGIN_ROOT 가 없으면 설치 캐시에서 찾고, 못 찾으면 추측하지 말고 사용자에게 묻는다
ROOT="${CLAUDE_PLUGIN_ROOT:-}"
[ -n "$ROOT" ] && [ -f "$ROOT/skills/migrate/scripts/relink.py" ] || {
  ROOT="$(find "$HOME/.claude/plugins/cache" -path "*/sr-obsidian/*/skills/migrate/scripts/relink.py" 2>/dev/null | sort -V | tail -1)"
  ROOT="${ROOT%/skills/migrate/scripts/relink.py}"; }
[ -f "$ROOT/skills/migrate/scripts/relink.py" ] || echo "sr-obsidian 플러그인 루트를 찾지 못했습니다. 설치 경로를 알려 주세요."
RELINK="$ROOT/skills/migrate/scripts/relink.py"

# 이동 쌍: Step 2 계획표에서 보류를 뺀 전체를 "OLD<TAB>NEW" 한 줄씩 (vault 루트 기준)
# 폴더 쌍은 폴더째 옮긴 경우에만. 이미 있던 폴더로 합쳤다면 파일 쌍으로 적는다
MOVES="${TMPDIR:-/tmp}/migrate-moves.tsv"
printf '%s\t%s\n' "$PROJECT_PATH/docs/{file}" "$PROJECT_PATH/docs/{subfolder}/{file}" > "$MOVES"

python3 "$RELINK" --vault /Users/sr/obsidian/sr-labs --map "$MOVES"            # dry-run: 보고만
python3 "$RELINK" --vault /Users/sr/obsidian/sr-labs --map "$MOVES" --apply    # 결과 확인 후 적용
```

`--apply` 는 이동 맵 전체로 한 번만 돌립니다. 나눠서 돌리면 앞 실행이 고친 파일이 커밋 전까지 미커밋 파일이라, 뒤 실행이 그 파일을 `[dirty]` 로 보류해서 링크가 안 고쳐진 채 남아요. 같은 브랜치에서 migrate 와 archive 를 이어 돌릴 때도 같습니다. 나눠야 하면 사이에 커밋합니다.

relink 가 고치는 것:

- 위키링크와 임베드: 파일명형 `[[x]]`, 경로형 `[[20-areas/.../x]]`, 상대경로형 `[[../../x]]`, 표 안 `[[x\|표시명]]`, `#앵커`, frontmatter 안 링크
- markdown 링크: `[t](상대경로)`, `[t](<공백 경로>)`, 퍼센트 인코딩 경로
- canvas 파일 노드의 `file` 경로
- iframe `src="file:///Users/sr/obsidian/sr-labs/..."` 절대경로 (md, html)

링크마다 이동 전에 가리키던 파일을 구하고, 이동 후에도 같은 파일을 가리키도록 원래 형식을 유지해 고칩니다. 해석 규칙은 vault `_scripts/vault-review.py` 와 같은 Obsidian 기준이에요(파일명과 경로로만 해석, #8607 D6). 코드 블록 판정도 vault-review 의 fence 규칙과 같습니다. 같은 파일명이 여럿이라 파일명형 링크가 다른 파일로 붙게 되면 경로형으로 바꾸고 원래 텍스트를 표시명으로 남깁니다. 부분 경로형(`[[docs/x]]`)은 새 파일명이 vault 에서 유일하면 파일명형 `[[x]]` 로, 아니면 전체 경로로 고쳐요(D6 기본형은 파일명형). 이동 전부터 깨져 있던 링크는 건드리지 않습니다.

`== 수동 확인 ==` 에 나온 항목은 자동으로 고치지 않아요. 판단 기준 표대로 사용자에게 보고합니다.

### Step 5. 빈 폴더 정리

빈 표준 폴더를 일괄로 만들지 않습니다. 구조 표준이 "프로젝트에 없는 유형의 폴더는 만들지 않는다"고 정하고 있어요. 대신 이관으로 비게 된 원래 폴더를 치웁니다. git 은 빈 폴더를 추적하지 않아서 디스크에만 남고, 그대로 두면 audit B-1 에 계속 걸립니다.

```bash
# 비어 있을 때만 지워진다 (파일이 남아 있으면 rmdir 이 실패하고 폴더는 그대로)
rmdir "$PROJECT_PATH/docs/runbook"
```

### Step 6. 검증

이관 후 `sr-obsidian:audit` 재실행하여 모든 항목 통과 확인.

vault 에 `_scripts/vault-review.py` 가 있으면 이관 전후로 돌려서 A 범주 링크 finding 수가 늘지 않았는지도 봅니다. 늘었다면 새로 깨진 링크라서 커밋 전에 고쳐요.

### Step 7. 완료 보고

```
이관 완료:
  이동: {N}개 파일
  보류(미커밋): {N}건
  링크 업데이트: {N}개 파일 (서비스 밖 {N}개 포함)
  수동 확인: {N}건
  빈 폴더 정리: {N}개

sr-obsidian:audit 재실행 결과: ✅ 전체 통과
```

커밋할 때는 옮긴 파일과 relink 가 고친 파일만 경로를 지정해서 add 합니다. 공유 워킹트리라 `git add -A` 는 쓰지 않아요. 커밋 직전에 `git diff --cached --name-only` 로 목록을 눈으로 확인하고, 보류한 파일이나 `[dirty]` 파일이 섞였으면 빼냅니다.

## 판단 기준

| 상황 | 처리 |
|------|------|
| 이동 대상 파일 없음 | "이관할 파일 없음" 출력 후 종료 |
| `docs/kickoff/` 의 HTML | 옮기지 않음 (착수 보고 HTML 슬라이드 허용) |
| 유형 폴더가 기계적으로 정해지지 않음 | 후보와 근거를 계획표에 적고 사용자 선택 |
| relink `[plain]` 평문 경로 언급 | 코드 블록, 백틱, frontmatter `source` 같은 자유 텍스트. 문맥을 보고 고칠지 사용자와 정함. 60-logs 는 기록이라 두고 건수만 보고 (#8607 D6) |
| Step 2 검사에 걸린 이동 대상 | `보류(미커밋)`. 이동 맵에서 빼고, 폴더 쌍이면 폴더째 보류하거나 걸린 파일을 뺀 파일 쌍으로 나눔. 사용자가 이번 작업의 변경이라고 확인한 경우에만 포함 |
| relink `[dirty-move]` 이동 대상의 미커밋 변경 | 옮길 파일 자체에 미커밋 변경이 있거나 HEAD 에 없는 파일(미추적, 무시된 파일). git mv 전에 나오면 `보류(미커밋)` 로 빼고, git mv 뒤에 나오면 커밋 전에 사용자에게 보고해 이동을 되돌릴지(추적 파일은 `git mv NEW OLD`) 정함. 앞선 `--apply` 가 고친 옮긴 파일도 같은 모양으로 걸림. 이번 작업의 변경이라고 확인되면 `--include-dirty`. 그 전에는 이 파일 안의 링크를 relink 가 고치지 않음 |
| relink `[dirty]` 미커밋 파일 | 실행 전부터 미커밋 변경이 있어 건드리지 않은 파일. 다른 작업일 수도, 앞선 relink `--apply` 결과일 수도 있음. 앞선 relink 결과면 그 결과를 커밋한 뒤 다시 돌림(`--apply` 는 한 번만). 다른 작업이면 그 작업이 커밋된 뒤 다시 돌리거나, 사용자 확인 후 `--include-dirty` |
| relink `[folder-ref]` 폴더 경로 참조 | 이동으로 비는 폴더를 가리키는 Dataview `FROM "폴더"`, `dv.pages('"폴더"')`, Bases `file.inFolder("폴더")` 같은 참조와, dataviewjs 변수나 HTML 설정값 속 폴더 경로 문자열. 링크가 아니라서 깨져도 결과가 조용히 빌 뿐임. 표시된 새 위치로 고칠지 사용자와 정하고, 새 위치가 "하나로 정해지지 않음" 이면 쿼리를 어떻게 바꿀지 따로 정함. 60-logs 는 기록이라 건수만 보고 (#8607 D6) |
| relink `[report-only]` `.claude/` 파일 | 에이전트 설정이라 보고만 함. 사용자 확인 후 수동 수정 |
| relink `[html-rel]` 옮긴 HTML 의 상대경로 | 새 위치 기준으로 대상이 맞는지 확인 후 수동 수정 |
| relink `[unfixable]` | 수동 확인 필요 항목으로 보고 |
| 옮긴 HTML 에 페어드 MD 없음 | audit D-1 ❌. `20-areas/CLAUDE.md` 다이어그램 파일 패턴대로 MD 작성 제안 |
| migrate 후 audit 여전히 실패 | 실패 항목 재출력 후 추가 조치 안내 |
| 대상 경로 이미 존재 | 사용자에게 덮어쓰기 여부 확인 (relink 도 종료 코드 2로 멈춤) |
| relink `[충돌] NEW 폴더의 파일이 OLD 에서 온 것이 아닙니다` | 이미 있던 폴더로 합쳤거나 git mv 가 한 단계 더 넣은 경우. 실제 이동 경로를 확인해 파일 쌍으로 다시 실행 |
| `git mv` 충돌 | 충돌 파일 나열 후 수동 해결 요청 |
