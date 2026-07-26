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
- related-iss 추가 시 hub 파일 1개만 읽기, 대화 맥락이 충분하면 질문 없이 진행
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
- `status` 유효값: `ready`/`in-progress`/`done` — `pending` 금지 (린터 차단)
- `end-date`는 체크리스트 전부 `- [x]`일 때만 입력, 미래 step은 `start-date` 비움
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
- 이슈 종료 시 `40-archives/`로 이동 (→ sr-obsidian:archive)

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
| steps/ 미지정 | templates.md의 유형별 기본 steps에서 자동 생성 |
| 파트너 문의 vs 내부 이슈 불명확 | 질문 1회 |
| comms/ 필요 불명확 | 외부 파트너 문의 포함 시 생성, 내부 이슈면 선택 |
