---
name: archive
description: >
  10-projects/ISS-*/ 에서 frontmatter type: issue 허브를 스캔해 종료 조건(hub done|cancelled, 레거시 closed 포함 + 모든 step 이 완료, 중단, 미적용 중 하나)을 충족한 ISS를 40-archives/로 일괄 이동하고, 옛 경로를 가리키던 링크와 canvas 노드를 새 경로로 고친다. ISS 아카이브 작업 시작 시 사용.
  Do NOT use for 진행 중 ISS.
  Do NOT use for 아카이브된 ISS 재오픈 → 재오픈하지 않는다, sr-obsidian:iss 후속 ISS 절차.
  Do NOT use for docs/ 구조 이관·재구성 → sr-obsidian:migrate.
  Keywords: archive, 아카이브, ISS 완료, 이슈 정리, iss archive, 완료 이동
allowed-tools: Read, Write, Bash, Grep, Glob
---

# sr-obsidian:archive — 완료 ISS 일괄 아카이브

## Phase 1: 스캔 (읽기 전용)

판정은 플러그인의 `skills/archive/scripts/scan.py`로 합니다. vault 루트에서 실행해요.
플러그인 루트는 migrate 스킬과 같은 방식으로 찾습니다. 셸 상태는 Bash 호출 사이에 이어지지 않으니 4-3에서도 이 해석을 앞에 붙여요.

```bash
# 플러그인 루트 해석. CLAUDE_PLUGIN_ROOT 가 없으면 설치 캐시에서 찾고, 못 찾으면 추측하지 말고 사용자에게 묻는다
ROOT="${CLAUDE_PLUGIN_ROOT:-}"
[ -n "$ROOT" ] && [ -f "$ROOT/skills/archive/scripts/scan.py" ] || {
  ROOT="$(find "$HOME/.claude/plugins/cache" -path "*/sr-obsidian/*/skills/archive/scripts/scan.py" 2>/dev/null | sort -V | tail -1)"
  ROOT="${ROOT%/skills/archive/scripts/scan.py}"; }
[ -f "$ROOT/skills/archive/scripts/scan.py" ] || echo "sr-obsidian 플러그인 루트를 찾지 못했습니다. 설치 경로를 알려 주세요."

python3 "$ROOT/skills/archive/scripts/scan.py"          # 사람용 보고
python3 "$ROOT/skills/archive/scripts/scan.py" --json   # JSON
```

**허브 식별**: ISS 폴더 루트의 `.md` 중 frontmatter `type: issue`인 파일이 허브입니다. 파일명 glob(`ISS-*/ISS-*.md`)으로 `status:`를 grep하지 않아요. 같은 폴더의 `ISS-NNN WBS.md`(type `wbs`, 레거시는 `literature`)도 `status: in-progress`를 가져서 허브로 오인됩니다 (#8607 D5).

**완료 기준** (모두 충족해야 아카이브 대상, #8607 D1):
1. 허브 `status: done` 또는 `cancelled`. 레거시 `closed`는 #8610 이관 전까지 종료로 인정
2. 종료 필드: `done`은 `end-date`, `cancelled`는 `cancelled-date`와 `cancelled-reason` (`closed`는 면제)
3. `steps/`의 모든 step이 닫힘. 닫힘은 셋 중 하나입니다
   - 완료: `end-date` 있음
   - 중단: `status: cancelled` 또는 `cancelled-date` 있음
   - 미적용: `applicable: false`
   - status와 날짜가 어긋나면 날짜를 따릅니다. `status: done`인데 `end-date`가 없으면 닫히지 않은 step이에요
4. 폴더 안에 미커밋 변경이 없음 (공유 워킹트리의 다른 세션 작업을 `git mv`로 같이 옮기지 않게)

steps/가 없는 ISS는 1, 2, 4만으로 판단합니다.

**체크리스트**: `cancelled` 허브는 체크리스트가 미완이어도 옮길 수 있습니다. `done` 허브의 `## 체크리스트`에 `- [ ]`가 남아 있으면 경고만 띄우고 대상에서 빼지 않아요.

## Phase 2: 결과 보고

`scan.py` 출력을 그대로 보여줍니다.

```
아카이브 대상 (N건)
  ✅ ISS-051 [done] ISS-051 paypro PSP ITSM step 의존성 교정 | 완료 4, 중단 1
     ⚠️ 허브 체크리스트 미완 1개

보류 (N건)
  ⏳ ISS-0YY [cancelled] ISS-0YY ...
     - step-03-....md 미종료 (status: in-progress)
     - 허브 cancelled-reason 없음 (cancelled 선언에 필요)

참고: step 은 모두 닫혔는데 허브가 종료 선언 전 (N건, 아카이브 대상 아님)
```

대상이 0건이면 "아카이브할 ISS 없음" 출력 후 종료.

보류 건을 이 스킬이 대신 닫지 않습니다. 끝나지 않은 step을 `done`으로 바꾸거나 `end-date`를 채워 대상으로 만들지 말고, sr-obsidian:iss "종료 절차"로 안내해요 (#8607 D1).

## Phase 3: 사용자 확인

목록 출력 후 사용자 확인을 받는다.

> "위 N건을 40-archives/로 이동합니다. 진행할까요?"

## Phase 4: 실행 (확인 후)

sr-harness 워크플로우 준수.

### 4-1. Issue + Branch

[git-workflow](../../references/git-workflow.md) 표준 절차 적용 —
제목 `chore: 완료 ISS 일괄 아카이브 (N건)` (body에 대상 ISS 목록), 브랜치 `feature/{ISSUE_NUM}-archive-iss-batch`.

### 4-2. git mv (대상 ISS 각각)
```bash
git mv "10-projects/ISS-{NNN}-{slug}" "40-archives/ISS-{NNN}-{slug}"
```

### 4-3. 옛 경로 링크 치환 (#8607 D6)

폴더를 옮기면 옛 경로를 적은 링크가 깨집니다. 경로형 위키링크(`[[10-projects/ISS-.../파일|...]]`, 임베드 포함), `.canvas`의 파일 노드(JSON `"file"` 값), iframe 같은 `file://` 절대경로가 대상이에요. ISS 폴더 안의 `ISS-NNN-overview.canvas`도 노드가 vault 루트 기준 경로라 같이 고쳐야 합니다.

migrate 스킬의 링크 갱신 엔진(`relink.py`)을 씁니다. 기본은 dry-run이고, 옮긴 폴더 전부를 한 번에 넘겨요.

```bash
RELINK="$ROOT/skills/migrate/scripts/relink.py"   # ROOT 는 Phase 1 과 같은 방식으로 해석
python3 "$RELINK" --vault . \
  --move "10-projects/ISS-{NNN}-{slug}" "40-archives/ISS-{NNN}-{slug}" \
  --move "10-projects/ISS-{MMM}-{slug}" "40-archives/ISS-{MMM}-{slug}"
# 링크 갱신 목록을 확인한 뒤 같은 인자에 --apply 를 붙여 다시 실행
```

- 다른 세션의 미커밋 변경이 있는 파일은 엔진이 고치지 않고 "수동 확인"으로 보고합니다. 그 파일은 손대지 말고 PR 본문에 남겨요 (공유 워킹트리, 스크립트 수정으로 남의 미커밋 내용을 잃은 사고가 있었음)
- 60-logs의 평문 경로 언급(ingest-log 파일 목록 등)은 기록이라 고치지 않습니다. 위키링크만 고쳐요
- 엔진 파일이 없으면 손으로 `sed` 치환하지 말고 중단한 뒤 사용자에게 알립니다
- `[folder-ref]`: Dataview `FROM`, `dv.pages`, Bases `inFolder`처럼 옮긴 ISS 폴더 경로를 문자열로 참조하는 곳입니다. 엔진이 고치지 않으니 표시된 새 경로로 사람이 고쳐요. 고치지 않으면 쿼리가 오류 없이 비어 버립니다(60-logs 기록은 건수만 PR 본문에 남김)
- `[dirty-move]`: 옮기는 폴더 안 파일에 미커밋 변경이 있습니다. 그 ISS는 이동을 보류하거나 `git mv`를 되돌리고, 변경 주인이 커밋한 뒤 다시 실행해요

스테이징은 경로를 지정해서 합니다. `git add -A`는 쓰지 않아요.

```bash
git add -- {relink 가 "링크 갱신" 목록에 적은 파일들}
git diff --cached --name-only   # 옮긴 폴더와 위 파일만 있는지 눈으로 확인
```

### 4-4. Commit → PR → Merge

[git-workflow](../../references/git-workflow.md) 커밋·PR·**머지까지** 수행 —
커밋 `chore: 완료 ISS 일괄 아카이브 (#{ISSUE_NUM})`, 머지 후 main pull.

## 판단 기준

| 상황 | 처리 |
|------|------|
| step 중 미종료(착수 전, 진행 중)가 있음 | 보류. 이 스킬이 step을 닫지 않고 sr-obsidian:iss 종료 절차로 안내 |
| `status: done`인데 `end-date` 없는 step | 보류. 이 스킬이 고치지 않음. 사람이 완료 근거를 확인해 `end-date`를 채우거나, 근거가 없으면 sr-obsidian:iss 종료 절차로 닫음 |
| 허브 in-progress/ready인데 step이 모두 닫힘 | 대상 아님. "참고" 목록으로만 알림, 종료는 사람이 선언 |
| 허브 done/cancelled인데 종료 필드 없음 | 보류. 허브에 `end-date` 또는 `cancelled-date` + `cancelled-reason`을 채운 뒤 재실행 |
| cancelled 허브, 체크리스트 미완 | 대상 (중단 이슈는 체크리스트 미완이어도 이동 가능) |
| done 허브, 체크리스트 미완 | 대상이되 경고 표시, Phase 3에서 사용자가 판단 |
| steps/ 없는 ISS | 허브 종료 상태와 종료 필드만으로 판단 |
| `type: issue` 허브가 0개이거나 2개 이상 | 수동 확인 |
| 폴더 안 미커밋 변경 | 보류. 다른 세션 작업일 수 있음 |
| relink `[folder-ref]` 보고 | 새 경로로 사람이 수정 (Dataview, Bases 폴더 쿼리가 조용히 비는 것 방지) |
| relink `[dirty-move]` 보고 | 그 ISS 이동 보류 또는 되돌림 |
| 아카이브 대상 0건 | "아카이브할 ISS 없음" 출력 후 종료 |
| 이미 아카이브된 ISS에 새 건 | 40-archives → 10-projects로 되돌리지 않음. 조치가 필요하면 sr-obsidian:iss 후속 ISS, 정보성이면 원본 comms/에 추가 (#8607 D2) |
