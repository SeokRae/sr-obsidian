---
name: transcript
description: >
  Clova Note/Caret 등 AI 회의 전사(주로 영문)를 국문 번역+STT 보정한 뒤 구조화 회의록까지 생성.
  원본은 60-logs/meetings-raw/에 verbatim 보존, 번역은 STT 불확실 구간을 표기하며 보정, 최종 회의록은
  20-areas/{서비스}/meetings/ 또는 20-areas/meetings/(공통)에 작성. "회의록 번역해줘", "전사 번역",
  "Clova 노트 정리", "Caret 회의록", "영문 회의록 국문화", "전사 보정" 요청 시 사용.
  Do NOT use for 이미 한국어로 정리된 내용의 구조화만 필요할 때 → sr-obsidian:history.
  Do NOT use for URL 웹 클리핑 → sr-obsidian:defuddle.
  Do NOT use for 구조화 없는 빠른 포착 → sr-obsidian:capture.
  Keywords: 회의록, 전사, transcript, Clova, Caret, STT, 번역, 국문화, verbatim, meeting raw
allowed-tools: Read, Glob, Write, Bash, Edit
---

# sr-obsidian:transcript — 회의 전사 번역·보정·회의록화

AI 회의 전사 원본(주로 영문)을 3단계로 처리한다: ① verbatim 보존 ② 번역+STT 보정 ③ 구조화 회의록.
각 단계 산출물은 서로 역링크되어 번역 대조·근거 추적이 가능해야 한다.

## 산출물 구조

```
60-logs/meetings-raw/{YYYY}/{MM}/
├── {YYYY-MM-DD} {주제}-en.md   ← 원어 verbatim (수정·의역 금지)
└── {YYYY-MM-DD} {주제}-ko.md   ← 국문 번역 + STT 보정 표기

20-areas/{서비스}/meetings/ 또는 20-areas/meetings/(공통)
└── {YYYY-MM-DD} {주제}.md      ← 구조화 회의록 (안건·결정·액션아이템)
```

원어가 이미 한국어 단일 언어면 `-en`/`-ko` 분리 없이 언어 접미사를 생략한 raw 파일 1개만 만들고 Step 3으로 바로 넘어간다.

## Step 1. 원본 수신 및 메타데이터 확인

`$ARGUMENTS`에서 파일 경로 또는 붙여넣은 전사 텍스트를 확인한다. 누락된 정보는 사용자에게 질문한다:

- 회의 날짜(`YYYY-MM-DD`), 주제(짧은 제목)
- source(예: "Clova Note AI 전사", "Caret 전사"), duration
- 회의 성격(`meeting-type`: 파트너/내부/정기 등)
- 저장 위치: 특정 서비스(`20-areas/{서비스}/meetings/`) vs 공통(`20-areas/meetings/`)

## Step 2. 원본 verbatim 저장

`60-logs/meetings-raw/{YYYY}/{MM}/{YYYY-MM-DD} {주제}-en.md`로 Write. **내용을 절대 수정·의역하지 않는다** — 화자 라벨, 타임스탬프, 오탈자까지 원본 그대로.

```markdown
---
type: meeting
date: {YYYY-MM-DD}
title: {주제} (원본, 영문)
meeting-type: {파트너 | 내부 | 정기 등}
source: {Clova Note AI 전사 등} (영문 원본, 미가공)
duration: {N분 N초}
tags: [meeting, source-transcript, {관련 서비스/키워드}]
created: {YYYY-MM-DD}
aliases: [{YYYY-MM-DD} {주제}-en]
---

# {주제} (원본, 영문)

← [[{YYYY-MM-DD} {주제}-ko|국문 번역]] · [[{YYYY-MM-DD} {주제}|구조화 회의록]]

> {source} 그대로. 번역·가공 없이 원본을 보존한다. 국문 번역 대조가 필요할 때 이 파일을 기준으로 확인한다.

---

{전사 원문 verbatim}

---

*출처: {전사 도구/경로} · 원본 verbatim 보존 ({오늘 날짜} vault 편입)*
```

## Step 3. 번역 + STT 보정

`60-logs/meetings-raw/{YYYY}/{MM}/{YYYY-MM-DD} {주제}-ko.md`로 Write. 화자 구분(`참석자 N` 등)과 타임스탬프는 원본 그대로 유지하며 자연스러운 국문으로 옮긴다.

- STT 인식 자체가 불명확한 구간: `[STT 불명확]`
- 오인식으로 추정되는 단어: `[STT 오인식 추정: {원문 표현}]` — 원문 단서를 남겨 검증 가능하게 한다
- 발화 내용의 사실관계·뉘앙스를 임의로 보정하거나 매끄럽게 다듬지 않는다 — 어색해도 원발화 그대로 옮기고, 명백한 STT 인식 오류만 표기

frontmatter·헤더는 Step 2와 동일 패턴으로 `-ko` 버전에 맞게 조정하고, `title`에 "(raw 전사)", `source`에 "(영→국문 번역)" 등을 표기. 참석자 실명이 발화 중 언급되면 여기서는 매핑하지 않고 원 라벨(참석자1 등)을 유지 — 실명 매핑(추정)은 Step 4 구조화 회의록에서만 다룬다.

## Step 4. 구조화 회의록

저장 위치는 Step 1에서 확인한 서비스 폴더 또는 공통(`20-areas/meetings/`). 파일명 `{YYYY-MM-DD} {주제}.md`.

```markdown
---
type: meeting
created: {YYYY-MM-DD}
project: {project-id 또는 생략(공통)}
tags: [meeting, {관련 서비스/키워드}]
meeting-type: {파트너 | 내부 | 정기 등}
attendees: []
description: {회의 핵심 주제 한 줄 요약}
---

# {YYYY-MM-DD} {주제}

← [[{project-id} 프로젝트 현황]]  (서비스 폴더일 때만)
→ [[{YYYY-MM-DD} {주제}-ko|국문 번역(raw)]] · [[{YYYY-MM-DD} {주제}-en|영문 원본]]

> {회의 배경과 핵심 주제 2~3줄 요약}. 원본은 {source}({소요시간}).

## 참석자

- {이름 또는 "참석자N"} — {소속/역할, 불확실하면 "(추정)" 표기}

> ⚠️ 화자 매핑은 전사록 내 호칭 단서로 추정한 것으로, 확정 정보가 아니면 이 경고를 유지한다.

## 안건

1. {안건}

## 논의 내용

### {N}. {안건 제목}

{배경, 쟁점, 검토한 대안, 비용/제약, 결론을 안건별로 서술. 원문 근거가 필요하면 -ko 파일 타임스탬프 참조 가능}

## 결정 사항

- {결정}

## 액션 아이템

- [ ] {액션} — 담당: {이름}, 기한: {YYYY-MM-DD}

## 미결

- {회의 중 확정되지 않은 사항}

## 관련 메모

- [[{YYYY-MM-DD} {주제}-ko|국문 번역(raw)]] — 원문 전체 번역, STT 불명확 구간 표기
- [[{YYYY-MM-DD} {주제}-en|영문 원본]] — verbatim 보존, 번역 대조용
- {관련 기존 노트 — ISS·서비스 히스토리 등}
```

## Step 5. 허브 연결 (서비스 폴더인 경우만)

특정 서비스 폴더에 저장했다면 `sr-obsidian:hub`로 해당 서비스 허브의 `## 📋 문서` 섹션에 링크 추가를 안내한다. 공통(`20-areas/meetings/`)이면 생략.

## Step 6. Git 워크플로우

[git-workflow](../../references/git-workflow.md) 절차를 따른다 — 이슈 제목 `docs: {주제} 회의록`, 브랜치 `feature/{N}-meeting-{slug}`, 커밋 1개에 원본(-en)·번역(-ko)·구조화 회의록 3개 파일을 함께 포함한다. 커밋 prefix `docs:`.

## 판단 기준

| 상황 | 처리 |
|------|------|
| 원어가 이미 한국어 단일 언어 | `-en`/`-ko` 분리 생략, raw 파일 1개(언어 접미사 없음) 저장 후 Step 4로 직행 |
| 전사가 매우 길어 한 번에 처리 어려움 | 구간을 나눠 순차 처리하되 원본 무결성(파일 1개로 통합) 유지 |
| 참석자 실명 불명확 | "참석자N" 라벨 유지 + Step 4에 "(추정)" 표기 및 경고 callout 필수 |
| 저장 위치(서비스 vs 공통) 불명확 | 사용자에게 질문 후 대기 — 추정 금지 |
| 동일 날짜·주제 raw 파일 이미 존재 | 덮어쓰기 전 사용자에게 확인 |
| 프로젝트 폴더(`meetings/`) 미존재 | Write로 경로 포함 생성 (Obsidian이 자동 생성) — 서비스 폴더 자체가 없으면 sr-obsidian:hub 먼저 안내 |
