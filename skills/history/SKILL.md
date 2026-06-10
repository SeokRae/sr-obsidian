---
name: history
description: >
  프로젝트 의사결정 히스토리 관리 — ADR 생성, 의사결정 로그, 회의록, 아키텍처 분석 기록.
  대화 중 기술 선택 고민이 오갔다면 사용자가 명시적으로 요청하지 않아도 ADR 작성을 먼저 제안한다.
  "ADR 만들어줘", "ADR 추가", "기술 고민 문서화", "왜 이걸 선택했는지 남겨줘", "의사결정 기록",
  "결정 이유 문서", "회의록 작성", "히스토리" 요청 시 사용.
  Keywords: adr, ADR, 의사결정, 기술 고민, 선택지, 트레이드오프, architecture decision, decision log, 회의록, meeting, history, 아키텍처 결정
allowed-tools: Read, Glob, Write, Bash, Edit
---

# sr-obsidian:history — 프로젝트 히스토리 관리

프로젝트의 의사결정 흔적(ADR, 의사결정 로그, 회의록, 아키텍처 분석)을 체계적으로 기록한다.
나중에 "왜 이걸 선택했지?"라는 질문에 답할 수 있게 하는 것이 목적이다.

> 구 `sr-obsidian:adr` 스킬은 이 스킬로 통합되었다. ADR 단독 생성도 여기서 처리한다.

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

> ADR 저장 경로는 **항상 `docs/adr/`** 로 통일한다(구 adr 스킬의 `{project}/adr/` 경로는 사용하지 않는다).

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

**Phase 0 — 대화에서 자동 추출 (구 adr 스킬 흡수):**
`$ARGUMENTS`가 있으면 힌트로 사용하고, 없으면 현재 대화에서 아래를 추출해 사용자 확인을 먼저 받는다.

1. **문제 상황** — 왜 결정이 필요했는가
2. **검토한 선택지** — 고민했던 옵션들 (2개 이상)
3. **결정** — 무엇을 선택했는가
4. **이유** — 선택의 근거 (기술적 제약, 성능, 유지보수 등)
5. **트레이드오프** — 선택하지 않은 옵션의 장점 / 선택한 옵션의 단점
6. **프로젝트** — `20-areas/` 하위 어느 폴더에 넣을지

> 대화에서 기술 선택 고민이 오갔다면 사용자가 명시적으로 요청하지 않아도 ADR 작성을 먼저 제안한다.

**다음 ADR 번호 확인:**
```bash
ls "20-areas/{...}/{project-id}/docs/adr/" | grep "adr-" | tail -1
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

## 판단 기준

| 상황 | 처리 |
|------|------|
| ADR 번호 중복 | `docs/adr/` 내 최대 번호 + 1 재계산 |
| 프로젝트 폴더 미존재 | sr-obsidian:scaffold 또는 sr-obsidian:hub 먼저 실행 안내 |
| 기존 ADR superseded | 기존 ADR에 `superseded-by: ADR-{N}` 필드 추가 + 신규 ADR에 `supersedes: ADR-{M}` 추가 |
| 회의 참석자 불명확 | 알려진 참석자만 기록, 추정 금지 |
| docs/adr·docs/architecture 폴더 없음 | Write로 폴더 경로 포함해서 파일 생성 (Obsidian이 자동 생성) |
