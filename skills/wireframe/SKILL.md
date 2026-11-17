---
name: wireframe
description: >
  React SPA 코드에서 화면 목록을 뽑아 사이트맵 한 장과, 라우트를 레이아웃 유형으로 묶은 뒤 유형별 대표 페이지를 실제 JSX 순서대로 그린 와이어프레임(Excalidraw)을 vault에 만들고, 배포 화면과 구성을 대조한다. 지금 있는 화면을 그대로 옮기는 as-is 와이어프레임이다. "앱 화면 전체 그려줘", "화면 와이어프레임", "화면 사이트맵", "페이지 구성도", "wireframe" 요청 시 사용.
  Do NOT use for 개념, 코드의 내부 동작 흐름 → sr-obsidian:learn.
  Do NOT use for 이미 있는 MD 문서의 HTML 변환 → sr-obsidian:visualize.
  Do NOT use for 시퀀스, 구성도 같은 흐름도 → flowcast:flowcast.
  Keywords: 와이어프레임, 화면 구성, 사이트맵, 페이지 목록, 레이아웃, as-is 화면, wireframe, sitemap
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent, SendMessage
---

# sr-obsidian:wireframe (앱 화면 사이트맵과 와이어프레임)

앱 코드에서 화면 전체를 찾아 사이트맵으로 펼치고, 화면을 레이아웃 유형으로 묶어 유형마다 대표 페이지 한 장을 와이어프레임으로 그린다. 모든 화면을 1:1로 그리지 않는 대신, 모든 화면이 어느 와이어프레임에 해당하는지는 빠짐없이 적는다. 기준점은 vault의 `20-areas/payment/untact-qa/diagrams/qa-app-sitemap.excalidraw.md`, `qa-app-wireframes.md`(목록)와 `qa-app-wireframes/`(화면별)와 어댑터 `_scripts/wireframe/nicepay-qa/`다.

## 사용법

```
/sr-obsidian:wireframe nicepay-qa
/sr-obsidian:wireframe @"{앱 저장소 경로}"   # 어댑터가 없으면 Phase 1에서 만든다
```

## 산출물

| 산출물 | type | 위치 |
|---|---|---|
| 사이트맵 | diagram | `{out_dir}/{sitemap.note}.excalidraw.md` |
| 와이어프레임 목록 노트 (유형, 화면 수, 대표, 링크, 유형별 화면 목록) | diagram | `{out_dir}/{wireframe.note}.md` |
| 와이어프레임 (공통 헤더 + 유형별 대표 + 따로 그린 화면, 한 장에 파일 하나) | diagram | `{out_dir}/{wireframe.note}/{app}-{순번}-{명세 이름}.excalidraw.md` |
| 레이아웃 명세 | - | vault `_scripts/wireframe/{app}/specs/*.json` (다시 그릴 때 재사용) |

설정 키(`out_dir`, `note` 등)와 어댑터 구성은 [adapter.md](references/adapter.md), 명세 형식은 [spec-schema.md](references/spec-schema.md)에 있다.

## 꼭 지킬 것

실제로 틀렸던 것들이다(2026-11-17 nicepay-qa 작업).

1. **사이트맵은 와이어프레임이 아니다.** "화면을 그려 줘"를 메뉴 구조도로 대신하지 않는다. 범위를 줄였으면 보고 첫 줄에 줄인 범위를 적는다.
2. **접힘은 코드의 첫 방문 기본값으로 그린다.** 배포 화면은 사용자가 접고 편 상태를 저장해 두므로, 그 차이를 명세 오류로 고치지 않는다.
3. **실제 데이터 값은 명세, 결과 파일, 노트에 옮기지 않는다.** 배포 화면의 건수, 가맹점 이름, ID가 찍힌 캡처를 vault에 넣으려면 먼저 묻는다.
4. **배포 화면 대조는 데스크톱 너비에서만 한다.** 창이 좁으면 모바일 배치가 그려진다. `outline.js` 의 `narrow` 가 true 면 대조하지 않고 그렇게 보고한다.
5. **Obsidian Excalidraw 플러그인은 노트를 열면 다시 저장한다.** 커밋 뒤 생긴 diff는 `exdraw.load` 로 두 판의 요소를 비교해, 요소 수와 글자가 같고 `x`, `width`, 버전 필드만 다르면 플러그인 흔적으로 보고 되돌린다.

## 스크립트 루트

```bash
ROOT="${CLAUDE_PLUGIN_ROOT:-}"
[ -n "$ROOT" ] && [ -f "$ROOT/skills/wireframe/scripts/routes.py" ] || {
  ROOT="$(find "$HOME/.claude/plugins/cache" -path "*/sr-obsidian/*/skills/wireframe/scripts/routes.py" 2>/dev/null | sort -V | tail -1)"
  ROOT="${ROOT%/skills/wireframe/scripts/routes.py}"; }
[ -f "$ROOT/skills/wireframe/scripts/routes.py" ] || echo "sr-obsidian 플러그인 루트를 찾지 못했습니다. 설치 경로를 알려 주세요."
SD="$ROOT/skills/wireframe/scripts"; AD="_scripts/wireframe/{app}"; EX="_scripts/excalidraw"
```

렌더러는 vault의 `_scripts/excalidraw/exdraw.py` 를 `--exdraw` 로 받아 쓴다. vault 루트에서 실행한다.

## 팀

| 이름 | subagent_type | 맡는 일 | 띄우는 때 |
|---|---|---|---|
| `wireframe-spec-writer` | `sr-obsidian:wireframe-spec-writer` | 대표 페이지 JSX → 명세 JSON | Phase 2의 1. 2~4페이지씩 나눠 여러 개를 동시에 |
| `wireframe-verifier` | `sr-obsidian:wireframe-verifier` | 배포 화면 윤곽과 명세 대조 | Phase 2의 3. `base_url` 이 있을 때 |

- 프롬프트에는 각 정의의 `## 입력` 필드와 `skill_dir`(이 스킬의 Base directory)를 넣는다. 백그라운드로 띄우고 완료 알림을 기다린다.
- verifier는 새 에이전트로 띄우고, 명세를 쓴 맥락(코드 해석, writer 보고)을 넘기지 않는다.
- 사용자 확인은 리드만 받는다.

## Phase 1: 화면 목록과 분류 (READ-ONLY)

**vault 파일 수정 없음.** 중간 산출물은 작업 폴더 `{ws}`(세션 스크래치패드의 `wireframe-{app}/`)에만 쓴다.

1. **어댑터 확인**: `_scripts/wireframe/{app}/config.json` 이 있으면 읽는다. 없으면 [adapter.md](references/adapter.md) 형식으로 config 초안, 메뉴 덤프 방법, 분류 규칙 초안을 `{ws}` 에 만들고 5의 보고에 넣는다.
2. **버전 고정**: 앱 저장소의 브랜치와 커밋(`git -C {repo} log -1 --format='%h %cd'`)을 적는다. 이 값이 `--rev` 이고 그림 제목에 들어간다.
3. **화면 목록**: `menu.sh {ws}/menu.json`(있으면), `python3 -I $SD/routes.py --src {repo}/{src} --router {router} --out {ws}/pages.json`.
4. **유형 분류와 대표**: `python3 -I $AD/classify.py {ws}/pages.json`. 유형마다 화면 수와 경로를 세고, config 의 대표와 따로 그릴 화면이 아직 맞는지 본다. 기존 명세가 있으면 대표 페이지 파일이 명세 뒤에 바뀌었는지 `git -C {repo} log --since` 로 보고, 다시 쓸 명세만 고른다.
5. **보고와 확인**: 아래를 보여 주고 확인을 받은 뒤에만 Phase 2로 간다. 명세 작성이 서브에이전트 여러 개를 쓰는 단계라서다.

```
### 와이어프레임 계획: {app} ({브랜치} {커밋})

라우트 {n}개 | 메뉴 밖 {n}개 | 화면 없음 {n}개
| 유형 | 화면 수 | 대표 | 공통 골격 |
따로 그릴 화면: {경로, 사유(줄 수, 구성)}
명세: 재사용 {n} | 새로 씀 {n} (사유: 파일 변경, 새 유형)
배포 대조: {base_url} | 건너뜀(사유)
만들 파일: {out_dir}/{sitemap}.excalidraw.md, {wireframe}.excalidraw.md, $AD/specs/*.json

진행할까요?
```

## Phase 2: 명세, 렌더, 대조 (작업 폴더에서)

1. **명세 작성** (`wireframe-spec-writer`): 다시 쓸 페이지를 2~4개씩 묶어 동시에 띄운다. 출력은 `{ws}/specs/`. 재사용 명세는 `$AD/specs/` 에서 복사한다. 공통 헤더(`app-header.json`)도 한 인스턴스에 맡긴다.
2. **렌더와 눈 확인**:
   ```bash
   python3 -I $SD/build_sitemap.py --exdraw $EX --config $AD/config.json --menu {ws}/menu.json --pages {ws}/pages.json --out {ws}/sitemap.excalidraw.md --svg {ws}/sitemap.svg --rev "{브랜치} {커밋}"
   python3 -I $SD/build_wireframes.py --exdraw $EX --config $AD/config.json --specs {ws}/specs --pages {ws}/pages.json --out {ws}/{note}.md --svg {ws}/svg --split-dir {ws}/{note} --rev "{브랜치} {커밋}"
   rsvg-convert -w 1400 {ws}/svg/{파일}.svg -o {ws}/{파일}.png
   ```
   `--split-dir` 를 주면 화면 한 장을 파일 하나로 쓰고 `--out` 에 목록 노트를 쓴다. 빼면 한 파일에 모두 그린다(16장이면 보기 불편해서 기본은 분리). 화면 2~3장의 PNG를 열어 본다. 글자 겹침, 빈 카드, 잘린 문구가 있으면 명세나 렌더러를 고친다. 메뉴가 없는 앱은 사이트맵을 건너뛴다.
3. **배포 화면 대조** (`wireframe-verifier`): `specs`, `base_url`, `outline`(`$SD/outline.js`), `out`(`{ws}/verify.md`)을 넘긴다. 불일치는 리드가 명세에서 고치고 2를 다시 돌린다. 상태 차이는 고치지 않는다. 검증 불가(창 너비, 로그인)면 사용자에게 알리고 대조 없이 갈지 묻는다.
4. **보고**: 화면별 대조 결과 표, 고친 불일치, 대조 못 한 영역(실행 뒤, 스크롤 아래, 배포본 버전)을 보여 주고 vault에 쓸지 확인받는다.

## Phase 3: vault 쓰기

1. **git**: [git-workflow.md](../../references/git-workflow.md) 절차. 제목 `docs: {app} 화면 사이트맵과 와이어프레임`, 브랜치 `feature/{N}-{app}-wireframe`.
2. **명세 보관**: `{ws}/specs/*.json` 을 `$AD/specs/` 로 복사한다.
3. **노트**: Phase 2의 2 명령을 `--out {out_dir}/{note}.md --split-dir {out_dir}/{note}` 로 다시 돌린다. 예전 판의 파일 중 이번에 만들지 않은 것(대표가 바뀐 유형의 옛 파일, 합본 `{note}.excalidraw.md`)은 지우고, 그 파일을 가리키던 링크를 목록 노트로 고친다. `python3 _scripts/note_validator.py {경로...}` 로 검사하고 `obsidian open path="{경로}"` 로 연다.
4. **커밋과 PR**: 만든 경로만 스테이징 규칙대로 add 한다. PR 본문에 기준 커밋, 유형 수, 대조 결과 요약, 대조 못 한 영역을 적는다.

## 하지 않는 것

- to-be 화면(개편안) 설계. 이 스킬은 있는 화면을 옮긴다.
- 화면 119개를 한 장씩 손으로 그리기. 유형과 대표로 묶는다.
- 배포 화면에서 실행, 저장, 삭제 버튼 누르기. 로그인 정보 입력.
- 앱 저장소 수정.
