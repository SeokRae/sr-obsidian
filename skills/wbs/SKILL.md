---
name: wbs
description: >
  Obsidian 프로젝트 WBS 생성·Phase 관리·Gantt 연동.
  "WBS 만들어줘", "Phase 추가", "진행 현황 업데이트" 요청 시 사용.
  Keywords: wbs, WBS, phase, 간트, Gantt, 진행 현황, 작업 분류
allowed-tools: Read, Write, Bash, Edit
---

# sr-obsidian:wbs — WBS 관리

`{project-id} WBS.md` 파일의 생성·Phase 구성·진행 현황 관리를 담당한다.

## WBS 파일 역할

| 섹션 | 내용 |
|------|------|
| 프로젝트 개요 | 목적·기간·KPI·관련 ISS |
| KPI 산출물 연계 | 산출물별 담당 Phase 매핑 |
| Phase 진행 현황 | Phase 목록·상태·기간 테이블 |
| Gantt (DataviewJS) | step frontmatter 자동 집계 |
| 미결 사항 | 결정 필요 항목 |

## 실행 절차

### Step 1. 현재 WBS 읽기

```bash
cat "20-areas/payment/{project-id}/{project-id} WBS.md"
```

### Step 2. 요청 유형 판별

| 요청 | 처리 |
|------|------|
| WBS 신규 생성 | sr-obsidian:init 실행 후 이 스킬로 보강 |
| Phase 추가 | Step 3 |
| 진행 현황 업데이트 | Step 4 |
| Gantt 연동 확인 | Step 5 |

### Step 3. Phase 추가

Phase 행 패턴:

```markdown
| Phase {N} | {제목} | {status} | {start-date} ~ {end-date} |
```

status 유효값: `ready` / `in-progress` / `done`

Phase 폴더 생성:
```bash
mkdir -p "20-areas/payment/{project-id}/phases/phase-{N}"
```

### Step 4. 진행 현황 업데이트

phases/ 하위 step 파일에서 status 집계:
```bash
grep -r "^status:" "20-areas/payment/{project-id}/phases/" | sort
```

Phase 진행 현황 테이블 갱신.

### Step 5. Gantt DataviewJS 블록

`_scripts/gantt/CLAUDE.md` 의 Gantt-C 패턴을 참조하여 DataviewJS 블록 삽입.

wbs-step frontmatter 자동 집계 — `wbs.md` 직접 수정 불필요.

### Step 6. 미결 사항 관리

결정이 필요한 항목은 `## 미결 사항`에 체크박스로 추가:
```markdown
- [ ] {항목} — 기한: {YYYY-MM-DD}
```

완료 시 `- [x]` 로 체크.
