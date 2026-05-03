---
name: wbs
description: >
  서비스 개발 WBS를 상태 머신 기반으로 생성·관리. 신규 프로젝트 WBS 작성, Phase 구성,
  진행 현황 업데이트, Excel 변환 안내. "WBS 만들어줘", "Phase 추가", "WBS 작성", "wbs" 요청 시 사용.
  Keywords: wbs, WBS, phase, 간트, Gantt, 진행 현황, 작업 분류, 상태 머신
allowed-tools: Read, Write, Glob, Edit
---

# sr-obsidian:wbs — WBS 생성·관리

서비스 개발 WBS를 상태 머신 기반으로 안내한다.  
신규 WBS 생성(init→skeleton→detail→review→export)과 기존 WBS 관리(Phase 추가·진행 현황 갱신) 모두 처리한다.

## 대상 경로

| 컨텍스트 | 경로 | 설명 |
|---------|------|------|
| 프로젝트 (20-areas) | `20-areas/payment/{project-id}/` | 서비스 개발 장기 프로젝트 |
| 인시던트 (10-projects) | `10-projects/ISS-{NNN}-{slug}/` | ISS 인시던트·단기 이슈 |

## 산출물 구조

```
{base}/
├── {name} WBS.md               ← 대시보드: 간트차트 + 개요 + Phase 링크 테이블
└── phases/
    ├── phase-1.md ~ phase-8.md ← Phase별 섹션 + task 체크리스트
    ├── phase-{idx}.md          ← (세부 분리) step 목록 대시보드
    └── phase-{idx}-{content}/
        └── step-{NN}-{desc}.md ← type: wbs-step 자기완결 문서
```

**역할 분리:**
- `WBS.md` — DataviewJS 간트차트 + 개요 테이블 + Phase 링크 테이블
- `phase-N.md` — `##` 섹션 + `- [ ]` task (체크박스가 진행률 집계 원천)
- `step-NN-*.md` — 외부 협력·승인 절차가 있는 세부 분리 Phase 전용 (ITSM 등)

---

## 상태 머신

| status | 동작 | 레퍼런스 |
|--------|------|---------|
| `init` | 프로젝트 정보 9개 항목 수집 | `references/init.md` |
| `skeleton` | 대시보드 + phase 파일 골격 생성 | `references/skeleton.md` |
| `detail` | Task 4속성 상세화 | `references/detail.md` |
| `review` | 5가지 품질 점검 | `references/review.md` |
| `export` | Excel 변환 명령 안내 | `references/export.md` |

`wbs-status`가 없으면 `init`으로 시작.

## 허용 도구

| 단계 | 허용 도구 |
|------|---------|
| init | — |
| skeleton | `Glob`, `Write` |
| detail | `Read`, `Glob`, `Write` |
| review | `Read`, `Glob` |
| export | `Read` |

**기존 파일 Edit 금지** — skeleton/detail 단계에서 Write만 허용.

---

## 실행 절차

### Step 1. 대상 확인

사용자 메시지에서 경로 파악. 없으면 질문:
```
어느 프로젝트의 WBS인가요?
- 20-areas 서비스 프로젝트 → 경로: 20-areas/payment/{project-id}/
- ISS 인시던트 → 경로: 10-projects/ISS-{NNN}-{slug}/
```

### Step 2. 현재 상태 확인

```bash
# WBS 파일 존재 여부
Glob: "{base}/**WBS.md"
```

WBS 파일이 없으면 → `init` 시작  
있으면 → 프론트매터 `wbs-status` 값으로 다음 단계 판별

### Step 3. 상태별 처리

`wbs-status` 값에 따라 해당 레퍼런스 파일의 절차를 따른다:

- `init` (또는 없음) → `references/init.md` 실행
- `skeleton` → `references/skeleton.md` 실행
- `detail` → `references/detail.md` 실행
- `review` → `references/review.md` 실행
- `export` → `references/export.md` 실행

---

## 기존 WBS 관리 모드

WBS가 이미 완성된 프로젝트에서 관리 작업이 필요할 때:

### Phase 추가

```bash
# 현재 phases/ 확인
Glob: "{base}/phases/*.md"
```

Phase 행 패턴:
```markdown
| Phase {N} | {제목} | {status} | {start} ~ {end} |
```

status 유효값: `ready` / `in-progress` / `done`

### 진행 현황 갱신

step 파일 status 집계:
```bash
Glob: "{base}/phases/**/*.md"
```
각 step의 `status` frontmatter 기반으로 Phase 진행률 테이블 갱신.

### 미결 사항 관리

`## 미결 사항` 섹션에 체크박스로 추가:
```markdown
- [ ] {항목} — 기한: {YYYY-MM-DD}
```
