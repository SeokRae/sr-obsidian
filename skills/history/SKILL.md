---
name: history
description: >
  프로젝트 의사결정 히스토리 관리 — ADR 생성, 의사결정 로그, 회의록 등록.
  "ADR 추가", "의사결정 기록", "회의록 작성", "히스토리" 요청 시 사용.
  Keywords: adr, ADR, 의사결정, decision log, 회의록, meeting, history, 아키텍처 결정
allowed-tools: Read, Write, Bash, Edit
---

# sr-obsidian:history — 프로젝트 히스토리 관리

프로젝트의 의사결정 흔적(ADR, 의사결정 로그, 회의록)을 체계적으로 기록한다.

## 히스토리 구성

```
{project}/
├── docs/adr/            ← 아키텍처 결정 기록 (ADR)
│   └── adr-{NNN}-{title}.md
├── docs/architecture/   ← 아키텍처 분석 (전문가 리뷰, 제약 분석)
│   └── analysis-{YYYY-MM-DD}.md
└── meetings/            ← 회의록
    └── {YYYY-MM-DD}-{주제}.md
```

## 실행 절차

### Step 1. 요청 유형 판별

| 요청 | 처리 |
|------|------|
| ADR 생성 | Step 2 |
| 의사결정 로그 추가 | Step 3 |
| 회의록 작성 | Step 4 |
| 아키텍처 분석 기록 | Step 5 |

---

### Step 2. ADR 생성

**다음 ADR 번호 확인:**
```bash
ls "20-areas/payment/{project-id}/docs/adr/" | grep "adr-" | tail -1
```

**파일명 패턴:** `adr-{NNN}-{decision-title-kebab}.md`

**ADR 템플릿:**
```markdown
---
type: adr
adr-number: {NNN}
title: {의사결정 제목}
status: accepted  # accepted | proposed | deprecated | superseded
created: {YYYY-MM-DD}
tags: [adr, {project-id}]
---

# ADR-{NNN}: {제목}

← [[{project-id} 프로젝트 현황]]

## 상태

`accepted` / `proposed` / `deprecated` / `superseded by ADR-{NNN}`

## 컨텍스트

어떤 상황에서 이 결정이 필요했는지 서술.

## 결정

무엇을 결정했는가.

## 근거

왜 이 결정을 내렸는가. 대안과 비교.

## 결과

이 결정으로 인한 기술적·운영적 영향.

## 미결

- [ ] (후속 확인 필요 항목)
```

**ADR status 유효값:**
- `proposed` — 검토 중
- `accepted` — 채택됨
- `deprecated` — 폐기됨
- `superseded` — 다른 ADR로 대체됨

---

### Step 3. 의사결정 로그

보고서 MD(`docs/reports/`)에 `## 의사결정 로그` 섹션이 있으면 항목 추가:

```markdown
| 번호 | 결정 내용 | 결정자 | 날짜 | 근거 | 상태 |
|------|----------|--------|------|------|------|
| D-{N} | {내용} | {담당자} | {YYYY-MM-DD} | {근거 요약} | 확정/보류/폐기 |
```

ADR이 있는 경우 `ADR-{NNN}` 링크 추가.

---

### Step 4. 회의록 작성

**파일 위치:** `20-areas/payment/{project-id}/meetings/` 또는 `20-areas/meetings/`

**파일명:** `{YYYY-MM-DD}-{주제-kebab}.md`

**템플릿:**
```markdown
---
type: meeting
created: {YYYY-MM-DD}
project: {project-id}
attendees: []
tags: [meeting, {project-id}]
---

# {YYYY-MM-DD} {주제}

← [[{project-id} 프로젝트 현황]]

## 참석자

- {이름} ({역할})

## 안건

1. {안건}

## 결정 사항

- {결정}

## 액션 아이템

- [ ] {액션} — 담당: {이름}, 기한: {YYYY-MM-DD}

## 미결

- {미결 항목}
```

---

### Step 5. 아키텍처 분석 기록

**파일 위치:** `docs/architecture/`

**파일명:** `analysis-{YYYY-MM-DD}.md` 또는 `{주제}-analysis.md`

전문가 리뷰, 제약 분석, 기술 검토 결과를 기록.
보안·성능·확장성 등 관점별 분석 포함.

---

### Step 6. 허브 노트 연결

신규 ADR·회의록 작성 후 `sr-obsidian:hub` 실행하여 허브 노트 `## 📋 문서` 섹션 업데이트.
