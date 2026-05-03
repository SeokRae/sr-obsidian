---
name: init
description: >
  Obsidian 제텔카스텐 프로젝트 초기화. book(독서 노트), area(지식 영역), vault(PARA 구조 부트스트랩) 3가지 모드 지원.
  "새 책 시작", "독서 노트 만들어줘", "지식 영역 추가", "새 주제 공부 시작", "vault 초기화" 요청 시 사용.
  서비스 프로젝트(20-areas/) 폴더 초기화는 sr-obsidian:hub 사용.
  Keywords: init, 초기화, 제텔카스텐, zettelkasten, 독서노트, book, area, vault, 지식 영역, 공부 시작
allowed-tools: Read, Write, Bash, Edit
---

# sr-obsidian:init — 제텔카스텐 프로젝트 초기화

Obsidian vault에서 새 지식 프로젝트를 시작할 때 필요한 구조를 한 번에 만든다.

## 모드 선택

| 모드 | 설명 | 생성 위치 |
|------|------|----------|
| `book` | 독서 노트 프로젝트 | `30-resources/books/{slug}/` |
| `area` | 지식 영역 (기술·도메인·방법론 등) | `30-resources/{category}/{topic}/` |
| `vault` | vault 전체 PARA 구조 부트스트랩 | vault root |

> 서비스 프로젝트(20-areas/payment/{id}/) 초기화는 `sr-obsidian:hub` 사용.

모드가 명확하지 않으면 질문: "독서 노트인가요, 새 공부 영역인가요?"

---

## 📚 book — 독서 노트 프로젝트

### 정보 수집

| 항목 | 설명 | 예시 |
|------|------|------|
| `title` | 책 제목 | `Designing Data-Intensive Applications` |
| `slug` | 폴더명 (kebab-case) | `designing-data-intensive-applications` |
| `author` | 저자 | `Martin Kleppmann` |
| `description` | 한 줄 설명 | 분산 시스템 설계 원칙과 트레이드오프 |
| `chapters` | 챕터 목록 (선택) | ch01~ch12 제목 — 없으면 비워둠 |

### 폴더 생성

```bash
mkdir -p 30-resources/books/{slug}
```

### _index.md 생성

`30-resources/books/{slug}/_index.md`:
```markdown
---
type: literature
created: {YYYY-MM-DD}
tags: [books, {slug}]
status: reading
author: {author}
book-title: {title}
chapters-total: {N}
chapters-done: 0
---

# {title}

> {description}

← [[30-resources/books/_index|Books]]

## 개요

- **저자**: {author}
- **핵심 주제**: {description}
- **읽기 목적**: (미결)

## 챕터 목록

| 챕터 | 제목 | 상태 |
|------|------|------|
| ch01 | (제목) | ⬜ |

## 핵심 개념 (Permanent 노트)

(/study 스킬로 추출한 permanent 노트 링크)

## 관련 메모
```

### 챕터 파일 생성 (챕터 목록이 있을 때)

`30-resources/books/{slug}/ch{NN}-{slug}.md` — 각 챕터:
```markdown
---
type: literature
created: {YYYY-MM-DD}
tags: [books, {book-slug}]
book: {title}
chapter: {N}
chapter-title: {챕터 제목}
status: unread
---

# ch{NN} {챕터 제목}

← [[_index|{title}]]

## 핵심 논지

## 주요 개념

## 메모

## Permanent 노트 후보

- [ ] 
```

### 30-resources/books/_index.md 갱신

`## 목록` 섹션에 링크 추가:
```
- [[{slug}/_index|{title}]]
```

### 완료 안내

```
✅ 독서 노트 생성: 30-resources/books/{slug}/
  ├── _index.md
  └── ch{NN}-*.md ({N}개)

다음 단계:
  /study → 챕터 읽기 후 literature 노트 → permanent 노트 추출
```

---

## 🗂️ area — 지식 영역

### 정보 수집

| 항목 | 설명 | 유효값 |
|------|------|--------|
| `category` | 리소스 카테고리 | `tech` / `domain` / `methodology` / `career` / `tools` |
| `topic` | 주제 폴더명 (kebab-case) | `distributed-systems` |
| `title` | MOC 표시 이름 | `분산 시스템` |
| `description` | 한 줄 설명 | - |

### 폴더 생성

```bash
mkdir -p 30-resources/{category}/{topic}
```

### MOC 생성

`50-moc/{title} MOC.md`:
```markdown
---
type: moc
created: {YYYY-MM-DD}
tags: [{category}, moc, {topic}]
---

# {title} MOC

> {description}

← [[Home]] | [[00-index|전체 인덱스]]

## 핵심 개념

(permanent 노트 추가 시 링크 연결)

## 관련 영역

## 참고 자료
```

### 완료 안내

```
✅ 지식 영역 생성 완료
  30-resources/{category}/{topic}/  ← permanent 노트 저장 위치
  50-moc/{title} MOC.md            ← 진입점

다음 단계:
  /study   → 문헌 노트 → permanent 노트 추출 후 MOC에 링크 연결
  /wiki    → 용어 wiki 페이지 생성
  /capture → fleeting 메모 포착
```

---

## 🏗️ vault — PARA 구조 부트스트랩

빈 vault 또는 구조가 없는 상태에서 전체 PARA 폴더와 핵심 파일을 생성한다.

### 폴더 생성

```bash
mkdir -p 00-inbox
mkdir -p 10-projects
mkdir -p 20-areas/meetings
mkdir -p 30-resources/{tech,domain,methodology,career,tools,books}
mkdir -p 40-archives
mkdir -p 50-moc
mkdir -p 60-logs/{daily,weekly,retro}
mkdir -p _templates _scripts _attachments
```

### 핵심 파일 생성

| 파일 | 역할 |
|------|------|
| `50-moc/Home.md` | vault 진입점 |
| `50-moc/00-index.md` | permanent 노트 전체 카탈로그 (Dataview) |
| `50-moc/wiki-index.md` | wiki-term 카탈로그 (Dataview) |
| `60-logs/ingest-log.md` | ingest 로그 (append-only) |
| `30-resources/books/_index.md` | 독서 노트 목록 |

Home.md 기본 구조:
```markdown
---
type: moc
created: {YYYY-MM-DD}
tags: [home, moc]
---

# Home

## 빠른 진입

- [[00-index|전체 Permanent 노트]]
- [[wiki-index|Wiki 용어]]

## 영역

- 20-areas/ — 진행 중 프로젝트·서비스
- 30-resources/ — 지식 아카이브
- 10-projects/ — ISS 인시던트

## 최근 작업

(데일리 노트 링크)
```

---

## 공통: Ingest Log 기록

모든 모드에서 파일 생성 완료 후:

```bash
printf '\n## [%s] init | {모드} | {title} → {N}개\n' "$(date +%Y-%m-%d)" >> 60-logs/ingest-log.md
```
