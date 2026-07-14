---
name: capture
description: >
  Fleeting 노트 포착 모드. 대화 중 실시간으로 키워드와 문맥만 빠르게 기록한다.
  구조화·해석·정리 없이 bullet 중심으로 00-inbox/ 에 초안 생성.
  "포착", "기록", "fleeting", "capture", "메모해줘", "나중에 볼게" 요청 시 사용.
  Do NOT use for structured study/permanent notes (use sr-obsidian:study).
  Do NOT use for URL web clipping (use sr-obsidian:defuddle).
  Do NOT use for ADR·의사결정 로그·회의록 등 구조화된 기록 (use sr-obsidian:history).
  Keywords: 포착, 기록, fleeting, capture, 키워드, 메모
allowed-tools: Glob, Write
---

# sr-obsidian:capture — Fleeting 노트 포착

## 규칙

- 구조화하거나 해석하지 않는다
- 키워드와 문맥만 기록한다
- 문장보다 bullet, 단어, 짧은 구절 우선
- 프론트매터만 채우고 내용은 최소화
- 판단·정리·방향 제시 금지

## 작업

1. `$ARGUMENTS`에서 핵심 키워드 1~3단어를 제목으로 정한다.
2. `00-inbox/{제목}.md` 파일명이 이미 존재하면 `00-inbox/{제목}-{YYYYMMDD-HHMM}.md` 로 대체한다.
3. **Issue/Branch 없이** `00-inbox/` 에 직접 Write한다. fleeting은 git 워크플로우 예외다.
4. 아래 형식으로 저장한다.

```markdown
---
type: fleeting
created: {오늘 날짜 YYYY-MM-DD}
tags: []
---

# {핵심 키워드 1~3단어}

- {bullet 1}
- {bullet 2}
- ...
```

5. 저장 완료 후 `60-logs/ingest-log.md` 말미에 아래 형식으로 1개 항목을 append한다.

```
## [YYYY-MM-DD] capture | {제목} (fleeting) → 1개
- 00-inbox/{파일명}.md
```

6. 아래 형식으로 출력한다.

```
✅ fleeting 저장 완료
파일: 00-inbox/{파일명}.md
다음 단계: sr-obsidian:study 또는 sr-obsidian:wiki 로 이어서 정리
```

## 판단 기준

| 상황 | 처리 |
|------|------|
| `$ARGUMENTS` 비어 있음 | 무엇을 기록할지 질문 후 대기 |
| 동일 제목 파일 이미 존재 | `{제목}-{YYYYMMDD-HHMM}.md` 로 파일명 변경 |
| URL이 인자로 전달됨 | sr-obsidian:defuddle 사용 안내 |
| 구조화·분석 요청 포함 | 구조화는 생략하고 bullet만 기록, 처리는 study/wiki로 위임 |
