---
name: obsidian-bases
description: >
  Obsidian .base 파일 생성·편집 — YAML 데이터베이스 뷰로 vault 노트를 필터·정렬·집계. ISS 추적 대시보드, FT 현황 목록, step 진행 현황, 독서 목록 요청 시 사용.
  Do NOT use for DataviewJS 동적 쿼리·일회성 표 (Dataview 코드 블록 사용).
  Do NOT use for WBS·Phase·Gantt 관리 → sr-obsidian:wbs.
  Do NOT use for 공간 배치 맵·마인드맵 → sr-obsidian:canvas.
  Do NOT use for MD→HTML 시각화 → sr-obsidian:visualize.
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
5. **뷰 설정** — table / cards / list / map 중 선택, `order`로 컬럼 지정
6. **저장 위치** — 허브 노트 근처 또는 `50-moc/`
7. **검증** — Troubleshooting 섹션 확인

## 스키마

`filters`/`formulas`/`summaries`는 이름→값 **맵**, `properties`도 속성참조→표시설정 **맵**이다(리스트 아님). 컬럼 순서·표시는 각 view의 `order:` 리스트가 담당한다.

```yaml
filters:
  and:
    - 'type == "permanent"'

formulas:
  age: "(today() - created).days"

properties:
  file.name:
    displayName: 이름
  type:
    displayName: 타입
  created:
    displayName: 생성일
  formula.age:
    displayName: 경과일

views:
  - type: table
    name: 전체 목록
    order:
      - file.name
      - type
      - created
      - formula.age
```

## 필터 문법

`and`/`or`/`not` 키가 **표현식 문자열**(또는 중첩 필터 객체) 리스트를 직접 갖는다 — property/operator/value로 쪼갠 객체가 아니다. 표현식 안의 문자열 리터럴은 큰따옴표, 표현식 전체는 작은따옴표로 감싼다(`'status != "done"'`).

### AND / OR 복합

```yaml
filters:
  and:
    - 'type == "issue"'
    - 'status != "done"'
```

### OR / NOT 중첩

```yaml
filters:
  or:
    - file.hasTag("archived")
    - and:
        - file.hasTag("book")
        - file.hasLink("Textbook")
    - not:
        - file.inFolder("Required Reading")
```

### 연산자·함수

| 표현 | 의미 |
|------|------|
| `==` `!=` `>` `<` `>=` `<=` | 비교 (숫자·날짜·문자열) |
| `file.hasTag("x")` | 태그 포함 |
| `file.hasLink("Y")` | 링크 포함 |
| `file.hasProperty("z")` | 속성 존재 |
| `file.inFolder("path")` | 폴더 내부 |
| `str.contains("x")` / `str.startsWith("x")` / `str.endsWith("x")` | 문자열 포함·시작·끝 |
| `str.isEmpty()` / `list.isEmpty()` | 비어있음 |

## Properties

**맵**이다 — key는 속성 참조(무접두=note, `file.`=파일 속성, `formula.`=수식), value는 표시 설정.

```yaml
properties:
  status:
    displayName: Status
  file.ext:
    displayName: Extension
  formula.formatted_price:
    displayName: "Price"
```

### 속성 접두 규칙

무접두 = note(frontmatter) 속성(`status` 또는 `note.status`, 특수문자 포함 시 `note["가격"]`). `file.` = 파일 자체 속성. `formula.` = `formulas:`에 정의한 수식 참조.

### 파일 속성 (file.*)

| 속성 | 설명 |
|------|------|
| `file.name` | 파일명 |
| `file.path` | vault 루트 기준 경로 |
| `file.folder` | 상위 폴더 경로 |
| `file.ext` | 파일 확장자 |
| `file.size` | 파일 크기 (bytes) |
| `file.ctime` | 생성 시각 |
| `file.mtime` | 수정 시각 |
| `file.tags` | 파일 내 모든 태그 |
| `file.links` | 아웃바운드 링크 (frontmatter 포함) |
| `file.backlinks` | 인바운드 링크 — 성능 무거움, 가능하면 `file.links` 역방향 조회로 대체 |
| `file.properties` | 파일의 모든 속성 객체 |

### 컬럼 표시·순서

`properties`는 표시 설정만 담당하고, 실제 노출·순서는 view 내부 `order:` 리스트가 결정한다:

```yaml
views:
  - type: table
    order:
      - file.name
      - status
      - formula.age
```

## 수식 (formulas)

평면 맵 — `이름: '식'`. 참조할 때는 `formula.이름`.

```yaml
formulas:
  age: "(today() - created).days"
  진행률: "if(total > 0, round(done / total * 100), 0)"
```

`this` 키워드로 현재 파일 자신의 속성 참조 가능 (`this.status`).

전체 함수 목록 → [FUNCTIONS_REFERENCE.md](references/FUNCTIONS_REFERENCE.md)

## 뷰 타입

table(기본) / cards / list / map 4종. map은 Maps 커뮤니티 플러그인 필요.

```yaml
views:
  - type: table
    name: 전체 목록
  - type: cards
    name: 카드 보기
  - type: list
    name: 목록 보기
```

## 집계 (Summaries)

**두 층위**가 있다 — top-level은 재사용할 커스텀 집계식 정의(`values`가 해당 컬럼의 전체 값 리스트), view 내부는 컬럼별로 어떤 집계를 보여줄지 매핑.

```yaml
summaries:
  customAverage: "values.mean().round(3)"

views:
  - type: table
    summaries:
      formula.ppu: Average
      file.name: Filled
```

내장 집계 이름(전체 타입): `Empty` `Filled` `Unique`
숫자: `Average` `Max` `Min` `Median` `Range` `Stddev` `Sum`
날짜: `Earliest` `Latest` `Range`
체크박스: `Checked` `Unchecked`

## sr-labs 예시

### ISS 현황 대시보드

```yaml
filters:
  and:
    - 'type == "issue"'
    - 'status != "closed"'

properties:
  file.name:
    displayName: 파일명
  id:
    displayName: ID
  status:
    displayName: 상태
  created:
    displayName: 생성일

views:
  - type: table
    name: 진행 중 ISS
    order:
      - file.name
      - id
      - status
      - created
    summaries:
      file.name: Filled
```

### FT 기능 추적

```yaml
filters:
  and:
    - 'type == "wbs-step"'
    - file.inFolder("20-areas/payment")

formulas:
  완료율: "if(total > 0, round(done / total * 100), 0)"

properties:
  file.name:
    displayName: 파일명
  status:
    displayName: 상태
  start-date:
    displayName: 시작일
  end-date:
    displayName: 종료일
  formula.완료율:
    displayName: 완료율

views:
  - type: table
    name: WBS Step 현황
    order:
      - file.name
      - status
      - start-date
      - end-date
      - formula.완료율
```

## Bases 임베드

다른 노트에서 `.base` 파일 임베드:

```markdown
![[ISS 현황.base]]
```

## YAML 따옴표 규칙

- 표현식 문자열 전체는 작은따옴표, 그 안의 문자열 리터럴은 큰따옴표: `'status != "done"'`
- 값에 특수문자 포함 시 따옴표: `"in-progress"`
- 수식은 항상 따옴표: `"(today() - created).days"`

## Troubleshooting

| 증상 | 원인 | 해결 |
|------|------|------|
| 필터가 파싱 안 됨 | `property`/`operator`/`value` 객체형 문법 사용(구 스키마) | `and:`/`or:`/`not:` 키에 표현식 문자열로 작성 |
| 필터가 아무것도 반환 안 함 | property 이름 오타 | frontmatter 필드명 정확히 확인 |
| 수식 오류 | Duration 연산 혼동 | 날짜 - 날짜 = Duration, `.days`로 숫자 추출 |
| null 오류 | 빈 속성 미처리 | `if(isEmpty(field), 0, field)` 패턴 사용 |
| 정의되지 않은 수식 | `formulas:`에 없는 이름 참조 | `formula.이름` 참조와 `formulas:` 키 이름 일치 확인 |
| 표시 컬럼이 하나도 안 보임 | `properties`만 정의하고 `order` 누락 | view 내부 `order:` 리스트에 표시할 속성 명시 |

## 판단 기준

| 상황 | 처리 |
|------|------|
| 단순 일회성 조회 | Dataview 쿼리 블록으로 충분, .base 불필요 |
| DataviewJS 로직 필요 | DataviewJS 코드 블록 사용 |
| 저장 위치 불명확 | 해당 서비스 허브 근처 또는 50-moc/ |
| 기존 .base 파일 수정 | Read → Edit (Write로 전체 재작성 금지) |

## 참조

- [Obsidian Bases](https://obsidian.md/help/bases) — syntax·functions 하위 페이지 포함
