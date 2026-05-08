# Properties (Frontmatter) Reference

YAML frontmatter는 노트 최상단에 위치:

```yaml
---
type: permanent
created: 2025-05-08
tags:
  - tech
  - payment
aliases:
  - 대체 이름
cssclasses:
  - wide-page
status: active
rating: 4.5
completed: false
due: 2025-06-01T14:30:00
---
```

## Property 타입

| 타입 | 예시 |
|------|------|
| Text | `title: 제목` |
| Number | `rating: 4.5` |
| Checkbox | `completed: true` |
| Date | `created: 2025-05-08` |
| Date & Time | `due: 2025-05-08T14:30:00` |
| List | `tags: [one, two]` 또는 YAML 목록 |
| Links | `related: "[[다른 노트]]"` |

## 기본 Properties

- `tags` — 검색·그래프 뷰에서 사용되는 레이블
- `aliases` — 링크 자동완성에 사용되는 대체 노트명
- `cssclasses` — 읽기/편집 뷰에 적용될 CSS 클래스

## sr-labs 공통 type 값

| type | 설명 |
|------|------|
| `fleeting` | 00-inbox/ 임시 메모 |
| `permanent` | 30-resources/ 영구 노트 |
| `literature` | 문헌/챕터 노트 |
| `daily` | 데일리 로그 |
| `weekly` | 주간보고 |
| `retro` | 주말 회고 |
| `issue` | ISS 허브 |
| `incident-step` | 인시던트 step |
| `wbs` | WBS 대시보드 |
| `wbs-step` | WBS step |
| `meeting` | 회의록 |
| `diagram` | HTML 다이어그램 페어드 MD |
| `adr` | 아키텍처 결정 기록 |
| `config` | 실제 설정값 기록 |
| `wiki-term` | Wiki 용어 페이지 |

## 태그 규칙

```markdown
#태그
#중첩/태그
#태그-하이픈
#태그_밑줄
```

허용 문자: 모든 언어의 문자, 숫자(첫 글자 제외), 밑줄 `_`, 하이픈 `-`, 슬래시 `/`.

frontmatter에서:

```yaml
---
tags:
  - tech
  - payment/stripe
---
```
