---
name: iss
description: >
  ISS 인시던트/이슈 전체 구조 자동 생성 — hub + WBS + summary + steps/ + comms/. 파트너 문의·운영 이슈·인시던트 대응을 시작할 때 사용.
  Do NOT use for 비-ISS 프로젝트·지식 초기화 → sr-obsidian:scaffold / sr-obsidian:hub.
  Keywords: iss, 이슈, 인시던트, 문의 대응, ISS 생성, issue create, incident
allowed-tools: Read, Write, Bash, Grep, Glob
---

# sr-obsidian:iss — ISS 구조 자동 생성

파트너 문의·운영 이슈·인시던트를 시작할 때 ISS 전체 디렉토리 구조를 한 번에 생성한다.

## ⚡ 속도 (필수)

- Step 5의 모든 파일(hub·WBS·summary·steps·comms)은 **단일 응답에서 병렬 Write** — 파일 간 의존 없음, 순차 금지
- 다른 ISS를 링크하거나 `related-iss`를 추가할 때는 대상 허브 파일 1개만 읽어 실제 파일명(basename)을 확인하고, 파일명을 확인했으며 대화 맥락이 충분하면 질문 없이 진행 (아래 "다른 ISS 링크")
- outbound comms의 `/humanize` 검토는 전체 파일 Write 완료 후 별도 호출 (논블로킹)

## 생성 구조

```
10-projects/ISS-{NNN}-{slug}/
├── ISS-{NNN} {title}.md      ← hub
├── ISS-{NNN} WBS.md           ← gantt-b Gantt
├── ISS-{NNN} summary.md       ← 히스토리 요약 (steps·comms 엮어 갱신)
├── comms/                     ← 외부 질의·답변 원문
│   └── YYYY-MM-DD {주제}.md
└── steps/
    └── step-NN-{slug}.md
```

> **comms/ 경계 규칙**: 파트너·외부 질의 원문은 반드시 ISS/comms/ 에서 관리.
> FT comms/는 FT 내부 커뮤니케이션 전용 — ISS에서 파생된 외부 질의는 FT comms/ 금지.
> FT timeline에서 참조 시 ISS 경유 링크: `[[ISS-{NNN} {title}|ISS-{NNN}]] → [[질의 파일|요약]]`

## 실행 절차

### Step 0. 기존 ISS와 이어지는 건인지 확인

새 건이 기존 ISS를 잇는다면 원본 위치부터 봅니다(아래 "다른 ISS 링크"의 `find` 명령). 원본이 `40-archives/`에 있으면 아래 "후속 ISS" 절차를 따르고, 재오픈은 하지 않아요 (#8607 D2).

### Step 1. 다음 ISS 번호

`10-projects/ISS-*` + `40-archives/ISS-*` 중 최대 번호 + 1 (3자리 zero-padding).

### Step 2. 정보 확인

인자 또는 대화에서 파악 — `title`, `slug`(kebab-case), `source`(개인/github/회의/파트너), `related-ft`, `steps`.
steps 미지정이면 이슈 내용 기반 자동 추론 (유형별 기본 steps는 [templates.md](references/templates.md) 참조).
**section 유효값**: `발생` | `발견` | `조사` | `원인 분석` | `조치` | `후속`

### Step 3~4. Issue + Branch

[git-workflow](../../references/git-workflow.md) 표준 절차 —
제목 `ISS-{NNN}: {title}` (body에 설명·steps 체크리스트·관련 FT), 브랜치 `feature/{N}-iss-{NNN}-{slug}`.

### Step 5. 파일 생성 (병렬 Write)

[templates.md](references/templates.md)의 hub·WBS·summary·steps·comms 템플릿으로 전 파일을 **단일 응답에서 동시 Write**.

핵심 규칙 (상세는 templates.md):
- 허브 `status` 유효값: `ready` | `in-progress` | `done` | `cancelled`. `open`, `closed`는 쓰지 않습니다 (#8607 D1)
  - 종료 전 값은 step에서 계산해요. step 중 하나라도 `start-date`가 있거나 step이 없으면 `in-progress`, 전부 착수 전이면 `ready`입니다
  - 새 ISS는 발생 시점에 첫 step이 이미 착수된 것으로 봅니다. step-01에 `start-date: {생성일}`, `status: in-progress`를 채우므로 생성 시 허브는 항상 `in-progress`예요. 나머지 step은 `start-date`를 비우고 `ready`입니다
  - `done`, `cancelled`는 사람이 종료를 선언할 때만 씁니다 (아래 "종료 절차")
- step `status` 유효값: `ready`/`in-progress`/`done`, 종료 때만 `cancelled`. `pending` 금지 (린터 차단)
- `end-date`는 체크리스트 전부 `- [x]`일 때만 입력, 미래 step은 `start-date` 비움
- WBS 링크(`[[ISS-{NNN} WBS]]`)는 WBS 파일이 있을 때만 겁니다. 없는 노트에 선행 링크를 걸지 않아요 (#8607 D6, templates.md "링크 플레이스홀더")
- summary는 생성 시 `## 배경`만 step-01 기준 seed, 나머지는 placeholder
- outbound comm에 영문 메시지 포함 시 저장 전 `/humanize` 검토 필수 (inbound는 원문 보존)

### Step 6. Ingest Log

```bash
printf '\n## [%s] iss | ISS-{NNN} {title} (issue) → {N}개\n- 10-projects/ISS-{NNN}-{slug}/ISS-{NNN} {title}.md\n- 10-projects/ISS-{NNN}-{slug}/ISS-{NNN} WBS.md\n- 10-projects/ISS-{NNN}-{slug}/ISS-{NNN} summary.md\n- (steps/ 파일 목록)\n' "$(date +%Y-%m-%d)" >> 60-logs/ingest-log.md
```

### Step 7. 커밋

git-workflow 절차 — 커밋 `docs: ISS-{NNN} {title} 구조 생성 (#{N})`.

## 완료 후 안내

- Obsidian에서 `ISS-{NNN} WBS.md` 열어 gantt-b 렌더링 확인
- step 진행 시 `start-date`, 완료 시 `end-date` 채울 것
- 허브가 `ready`인데 step에 `start-date`를 채우면(첫 step 착수) 허브 `status`도 `in-progress`로 같이 올립니다. 한쪽만 커밋하면 린터(`lint-frontmatter.py`)가 계산값 불일치로 커밋을 막거나 경고해요 (#8607 D1)
- 이슈 종료는 아래 "종료 절차"로 선언한 뒤 `40-archives/`로 이동 (→ sr-obsidian:archive)

## 다른 ISS 링크 (#8607 D6)

Obsidian은 파일명(basename)과 경로로만 링크를 풉니다. H1 제목이나 ISS 번호만 적은 `[[ISS-083]]`은 풀리지 않아요.

1. 대상 허브를 찾습니다. 허브는 폴더 루트의 frontmatter `type: issue` 파일이에요. 셸 glob 대신 `find`를 써요. zsh는 `10-projects`, `40-archives` 중 한쪽 glob만 비어도 명령 전체를 실패시킵니다

   ```bash
   find 10-projects 40-archives -maxdepth 2 -type f -path '*/ISS-{NNN}-*/*.md' -exec grep -l '^type: issue' {} + 2>/dev/null
   ```

2. 찾은 파일의 basename(확장자 제외)으로 `[[{허브 파일명}|ISS-{NNN}]]`을 씁니다. 표 셀 안이면 `[[{허브 파일명}\|ISS-{NNN}]]`처럼 파이프를 이스케이프해요
3. frontmatter `related-iss`에는 링크가 아니라 ID 목록을 적습니다 (`related-iss: [ISS-{NNN}]`, #8607 D5)
4. 허브를 찾지 못하면 링크를 걸지 말고 평문 `ISS-{NNN}`으로 둔 뒤 사용자에게 확인합니다

## 후속 ISS (아카이브된 원본, #8607 D2)

아카이브된 ISS는 다시 열지 않습니다. `40-archives/` 폴더를 `10-projects/`로 되돌리지 않고, 원본 허브 `status`를 바꾸지 않으며, 원본 `steps/`에 새 step을 더하지도 않아요.

| 새 건의 성격 | 처리 |
|------|------|
| 우리 쪽 조치가 필요함 | 후속 ISS를 새로 만든다 (아래 1~3) |
| 정보성 (회신 확인, 종결 통보, FYI) | 원본 `40-archives/ISS-{원본}-*/comms/`에 comms 템플릿(`type: incident-comm`, 역링크는 `{back-link}` 규칙)으로 추가만 한다. 허브 `status`와 steps는 그대로 둔다 |

후속 ISS 만들기:
1. Step 1~5로 새 ISS를 만들고, 새 허브 frontmatter에 `related-iss: [ISS-{원본}]`을 적습니다. 새 허브 `## 관련 메모`에는 원본을 `[[{원본 허브 파일명}|ISS-{원본}]]`으로 겁니다 (위 "다른 ISS 링크")
2. 원본 아카이브 허브(`type: issue` 파일) 본문 맨 끝에 한 줄을 덧붙입니다. 파일명은 Step 5에서 실제로 쓴 후속 허브의 basename이에요

   ```markdown
   > 후속: [[{후속 허브 파일명}|ISS-{NNN}]] ({today})
   ```

3. 원본 허브에서는 이 한 줄 말고 frontmatter를 포함해 아무것도 고치지 않습니다. 이 줄은 후속 ISS 생성과 같은 커밋에 싣습니다

## 종료 절차 (#8607 D1)

종료는 사람이 선언합니다. 사용자가 종료, 완료 처리, 중단을 명시했을 때만 진행하고, step이 전부 끝났다는 이유만으로 허브를 `done`으로 바꾸지 않아요.

1. **종료 유형 확인**: `done`(목표 달성) 또는 `cancelled`(중단). `cancelled`는 사유가 필요하니 대화에 없으면 한 번 묻습니다
2. **남은 step 닫기**: 각 step frontmatter를 날짜 기준으로 판단합니다

   | step 상태 | 처리 |
   |------|------|
   | `end-date` 있음 (완료) | 그대로 둔다 |
   | `start-date` 없음 (착수 전) | `applicable: false` + `na-reason: {사유}`. `start-date`, `end-date`는 비워 둔다 |
   | `start-date` 있음, `end-date` 없음 (착수했지만 미완) | `status: cancelled` + `cancelled-date: {today}` + `cancelled-reason: {사유}`. `start-date`는 남기고 `end-date`는 비워 둔다 |

   **끝나지 않은 step을 `done`으로 적지 않습니다.** `end-date`를 채우거나 체크리스트를 체크해서 완료처럼 보이게 만들지도 않아요. `status: done`인데 `end-date`가 없는 step은 완료 근거를 확인해 `end-date`를 채우고, 근거가 없으면 `start-date` 유무에 따라 위 표대로 닫습니다
3. **허브 종료 선언**: `done`이면 `status: done` + `end-date: {today}`, `cancelled`면 `status: cancelled` + `cancelled-date: {today}` + `cancelled-reason: {사유}`
4. **summary 갱신**: `## 현재 상태`를 종료 상태로 갱신 (아래 요약 노트 갱신 절차 4번)
5. **아카이브**: 커밋 후 sr-obsidian:archive로 옮깁니다. `cancelled`는 체크리스트가 미완이어도 옮길 수 있어요

## 요약 노트 생성·갱신 (히스토리 축적)

**트리거**: 새 step/comms 작성 후, 또는 사용자가 특정 ISS를 지정해 "갱신/요약 갱신" 요청 시.
summary.md가 **없으면 backfill 생성, 있으면 갱신** — 요약 없이 발행된 기존 ISS도 이 경로로 소급 생성.

1. summary.md 없으면 templates.md의 summary 템플릿으로 먼저 생성
2. `steps/*.md` + `comms/*.md` + hub `## 진행 기록` 전체 Read
3. 시간순으로 `## 배경`·`## 경과`를 재구성 — 각 국면을 "무엇이 있었고 → 무엇을 확인했고 → 어디로 갔는지"로 잇는다
4. `## 현재 상태`를 최신 국면 기준 갱신 (종료된 ISS면 "종료 — {결말 요약}")
5. frontmatter `updated:` 갱신

**원칙**: 완료/미완 tally 금지 — **왜·어떻게·어디까지**를 서사로 서술. 원문 복붙 금지 (원문은 step/comms 소유).

## 판단 기준

| 상황 | 처리 |
|------|------|
| 관련 FT 있음 | hub에 `related-ft:` 필드 + FT ↔ ISS 양방향 링크 |
| 새 건의 원본 ISS가 `40-archives/`에 있음 | 재오픈 금지. 조치가 필요하면 후속 ISS, 정보성이면 원본 comms/에 추가 (#8607 D2) |
| 원본 ISS가 `10-projects/`에서 진행 중 | 후속 ISS 절차 대상 아님. 원본에 step, comms를 더할지 새 ISS로 뗄지 판단이 서지 않으면 질문 1회 |
| `ready` 허브의 step에 `start-date`를 처음 채움 | 같은 수정에서 허브 `status`를 `in-progress`로 갱신 |
| 종료 요청 | "종료 절차". 착수 전 step은 `applicable: false`, 착수한 step은 `cancelled`, 미완 step을 `done`으로 적지 않음 |
| 기존 ISS에 summary, step, comms 추가 | WBS 파일 존재 확인 후 링크 (없으면 허브로 역링크) |
| steps/ 미지정 | templates.md의 유형별 기본 steps에서 자동 생성 |
| 파트너 문의 vs 내부 이슈 불명확 | 질문 1회 |
| comms/ 필요 불명확 | 외부 파트너 문의 포함 시 생성, 내부 이슈면 선택 |
