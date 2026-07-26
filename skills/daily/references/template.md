# 데일리 노트 템플릿

`60-logs/daily/{YYYY}/{MM}/{YYYY-MM-DD}.md` 에 Write할 전체 형식.
`{YYYY-MM-DD}`, `{요일}` 등 플레이스홀더는 실제 값으로 치환한다.

## 섹션 구성 규칙

- `## 전일 리마인드`: `### ✅ 어제 완료`(`{PREV_DONE_PRS}`) + `### ⏭ 이어서 할 일`(`{CARRIED_ITEMS}`)로 구성.
  직전 노트가 아예 없으면 섹션 전체 생략, 한쪽 데이터만 비면 그 하위만 `- (없음)`.
- `{OPEN_ISSUES}` 자리에는 `{OPEN_ISSUES_WITH_STEPS}`(이슈 제목 + 계층형 sub-bullet) 삽입.

## 템플릿

````markdown
---
type: daily
created: {YYYY-MM-DD}
tags: [daily]
description: 날짜별 작업 로그 — 할 일, 배운 것, 회고
---

# {YYYY-MM-DD} ({요일})

## 전일 리마인드

> [[{PREV_DATE}]] 기준 — 완료 PR 자동 집계 + 미완 이월

### ✅ 어제 완료

{PREV_DONE_PRS}

### ⏭ 이어서 할 일

{CARRIED_ITEMS}

## 목표

{GOAL_ITEMS}

## Inbox — 오늘 포착한 것

> **구조**: 주제 / 목적 / 핵심 내용·지적사항 / 해결 방안 / 제약사항·미결
> 단순 운영 태스크는 제목 한 줄만 유지 가능

- [ ] [[이슈 링크]] 제목
  - **주제**: 무엇에 관한 내용인지 (날짜·출처 포함)
  - **목적**: 왜 이 작업/회의가 필요한지
  - **핵심 내용 / 지적사항**
    - ① 항목별로 번호 목록으로 세분화
    - ② 각 항목은 원인·영향까지 한 줄로
  - **해결 방안**: 결정된 대응 방향 (근거 포함)
  - **제약사항 / 미결**
    - 각 미결 항목 — 왜 미결인지 한 줄 설명

## 작업 로그

> **ISS 작업**: ISS 허브를 부모로, 하위 step/comms를 서브 블렛으로 작성
> `- [x] [[ISS 허브]] 작업 요약 (PR #번호)`
>   `- [[step-NN-파일명]] 또는 [[comms/파일명]] 변경 내용`
> **독립 노트** (wiki·permanent 등): `- [x] [[노트]] 작업 내용 (PR #번호)`
> 미완료 항목도 `- [ ]`로 진행 중 작업 기록 가능

- [ ]

## 미완 작업 (GitHub Issues)

> 오픈 이슈 기준 — {YYYY-MM-DD}
> **미완료** `- [ ]`: 이슈 제목 + sub-bullet (범위·작업 항목)
> **완료** `- [x]`: 이슈 제목 한 줄만 — sub-bullet 제거 (상세는 작업 로그에)

{OPEN_ISSUES}

## 진행 중 WBS / 이슈

```dataview
TABLE
  default(wbs-status, status) AS "상태",
  dateformat(file.mtime, "MM-dd") AS "최종수정"
FROM ""
WHERE file.folder != "_templates"
AND (
  (type = "wbs" AND wbs-status != "export")
  OR (type = "issue" AND status = "in-progress")
)
SORT type ASC, file.mtime DESC
```

## 현재 작업 중 노트

```dataview
TABLE
  file.link AS "노트",
  default(status, "-") AS "status",
  dateformat(file.mtime, "MM-dd HH:mm") AS "수정"
FROM ""
WHERE file.folder != "_templates"
AND file.name != "{YYYY-MM-DD}"
AND file.mtime >= date("{YYYY-MM-DD}")
AND file.mtime < date("{YYYY-MM-DD}") + dur(1 day)
AND (
  status = "in-progress"
  OR contains(file.tags, "#wip")
)
SORT file.mtime DESC
```

## 처리할 것

inbox에서 프로젝트/영역/리소스로 이동할 메모:

-

## 오늘 작업한 노트

```dataview
TABLE
  dateformat(file.ctime, "HH:mm") AS "생성",
  dateformat(file.mtime, "HH:mm") AS "수정",
  type
FROM ""
WHERE file.ctime >= date("{YYYY-MM-DD}") AND file.ctime < date("{YYYY-MM-DD}") + dur(1 day)
AND file.folder != "_templates"
AND file.name != "{YYYY-MM-DD}"
SORT file.ctime ASC
```

## 회고

오늘 배운 것, 연결된 아이디어:

````
