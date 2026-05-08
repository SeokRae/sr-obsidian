---
name: obsidian-bases
description: >
  Obsidian .base 파일 생성 및 편집 스킬.
  YAML 기반 데이터베이스 뷰로 vault 노트를 필터·정렬·집계한다.
  ISS 추적 대시보드, FT 현황 목록, step 진행 현황, 독서 목록 등 요청 시 사용.
  Do NOT use for dynamic queries requiring DataviewJS (use Dataview code blocks instead).
  Do NOT use for one-off table views — add a Dataview query to the note instead.
  Keywords: bases, .base, 데이터베이스, ISS 추적, FT 현황, 대시보드, 필터, 집계
allowed-tools: Read, Write, Edit
---

# sr-obsidian:obsidian-bases — Bases 파일 생성

Obsidian `.base` 파일은 YAML 형식의 데이터베이스 뷰다.
커뮤니티 플러그인 불필요 — Obsidian 코어 기능.

## 워크플로우

1. **목적 파악** — 어떤 노트 집합을 어떻게 보여줄 것인가
2. **범위 결정** — `filters`로 대상 폴더·태그·type 지정
3. **필드 선택** — 표시할 frontmatter 필드 결정
4. **수식 추가** — 계산이 필요한 필드 `formulas`로 정의
5. **뷰 설정** — table / cards / list 중 선택
6. **저장 위치** — 허브 노트 근처 또는 `50-moc/`
7. **검증** — Troubleshooting 섹션 확인

## 스키마

```yaml
filters:
  type: and                        # and | or | not
  filters:
    - property: type
      operator: is
      value: "permanent"

formulas:
  age:
    expression: "today() - created"

properties:
  - property: file.name
    visible: true
  - property: type
    visible: true
  - property: created
    visible: true
  - property: age
    formula: age
    visible: true

summaries:
  - property: file.name
    formula: count

views:
  - type: table
    name: 전체 목록
```

## 필터 문법

### 단일 필터

```yaml
filters:
  property: type
  operator: is
  value: "permanent"
```

### AND / OR 복합 필터

```yaml
filters:
  type: and
  filters:
    - property: type
      operator: is
      value: "issue"
    - property: status
      operator: is not
      value: "done"
```

### NOT 필터

```yaml
filters:
  type: not
  filter:
    property: tags
    operator: contains
    value: "archived"
```

### 필터 연산자 목록

| 연산자 | 의미 |
|--------|------|
| `is` | 같음 |
| `is not` | 다름 |
| `contains` | 포함 |
| `does not contain` | 미포함 |
| `starts with` | 시작 |
| `ends with` | 끝 |
| `exists` | 속성 있음 |
| `does not exist` | 속성 없음 |
| `is greater than` | 초과 (숫자/날짜) |
| `is less than` | 미만 (숫자/날짜) |
| `is on or after` | 이후 날짜 |
| `is on or before` | 이전 날짜 |
| `is between` | 범위 |

## Properties

### 노트 속성 (frontmatter 필드)

```yaml
properties:
  - property: status
    visible: true
  - property: created
    visible: true
```

### 파일 속성 (자동 제공)

| 속성 | 설명 |
|------|------|
| `file.name` | 파일명 (확장자 제외) |
| `file.path` | vault 루트 기준 경로 |
| `file.folder` | 상위 폴더 경로 |
| `file.extension` | 파일 확장자 |
| `file.size` | 파일 크기 (bytes) |
| `file.created` | 생성 시각 |
| `file.modified` | 수정 시각 |
| `file.tags` | 모든 태그 목록 |
| `file.outlinks` | 아웃바운드 링크 |
| `file.inlinks` | 인바운드 링크 |

### 수식 속성

```yaml
formulas:
  진행률:
    expression: "round(done / total * 100)"
  경과일:
    expression: "today() - created"
```

`this` 키워드로 현재 파일 자신의 속성 참조 가능.

전체 함수 목록 → [FUNCTIONS_REFERENCE.md](references/FUNCTIONS_REFERENCE.md)

## 뷰 타입

### Table 뷰 (기본)

```yaml
views:
  - type: table
    name: 전체 목록
```

### Cards 뷰

```yaml
views:
  - type: cards
    name: 카드 보기
    cover: image
```

### List 뷰

```yaml
views:
  - type: list
    name: 목록 보기
```

## 집계 (Summaries)

```yaml
summaries:
  - property: file.name
    formula: count
  - property: rating
    formula: average
```

지원 집계: `count`, `count-unique`, `sum`, `average`, `min`, `max`, `range`, `median`, `earliest`, `latest`, `percent-checked`, `percent-unchecked`

## sr-labs 예시

### ISS 현황 대시보드

```yaml
filters:
  type: and
  filters:
    - property: type
      operator: is
      value: "issue"
    - property: status
      operator: is not
      value: "closed"

properties:
  - property: file.name
    visible: true
  - property: id
    visible: true
  - property: status
    visible: true
  - property: created
    visible: true

summaries:
  - property: file.name
    formula: count

views:
  - type: table
    name: 진행 중 ISS
```

### FT 기능 추적

```yaml
filters:
  type: and
  filters:
    - property: type
      operator: is
      value: "wbs-step"
    - property: file.folder
      operator: starts with
      value: "20-areas/payment"

formulas:
  완료율:
    expression: "if(total > 0, round(done / total * 100), 0)"

properties:
  - property: file.name
    visible: true
  - property: status
    visible: true
  - property: start-date
    visible: true
  - property: end-date
    visible: true
  - property: 완료율
    formula: 완료율
    visible: true

views:
  - type: table
    name: WBS Step 현황
```

## Bases 임베드

다른 노트에서 `.base` 파일 임베드:

```markdown
![[ISS 현황.base]]
```

## YAML 따옴표 규칙

- `value`에 특수문자 포함 시 따옴표 필요: `value: "in-progress"`
- 수식 문자열은 항상 따옴표: `expression: "today() - created"`

## Troubleshooting

| 증상 | 원인 | 해결 |
|------|------|------|
| 필터가 아무것도 반환 안 함 | property 이름 오타 | frontmatter 필드명 정확히 확인 |
| 수식 오류 | Duration 연산 혼동 | 날짜 - 날짜 = Duration, Duration.days로 숫자 추출 |
| null 오류 | 빈 속성 미처리 | `if(isEmpty(field), 0, field)` 패턴 사용 |
| 정의되지 않은 수식 | `formulas:`에 없는 이름 참조 | `properties`의 `formula:` 값과 `formulas:` 키 이름 일치 확인 |

## 판단 기준

| 상황 | 처리 |
|------|------|
| 단순 일회성 조회 | Dataview 쿼리 블록으로 충분, .base 불필요 |
| DataviewJS 로직 필요 | DataviewJS 코드 블록 사용 |
| 저장 위치 불명확 | 해당 서비스 허브 근처 또는 50-moc/ |
| 기존 .base 파일 수정 | Read → Edit (Write로 전체 재작성 금지) |

## 참조

- [Obsidian Bases](https://help.obsidian.md/bases)
