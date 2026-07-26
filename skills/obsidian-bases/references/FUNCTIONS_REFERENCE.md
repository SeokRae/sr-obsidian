# Functions Reference

타입별 함수는 **메서드 호출형**이다 — `hasTag(file, tag)`가 아니라 `file.hasTag(tag)`. 값이 어떤 타입이든 그 값 뒤에 `.메서드(...)`를 붙인다.

## 속성 네임스페이스

무접두 = note(frontmatter) 속성. `file.` = 파일 자체 속성. `formula.` = `formulas:`에 정의한 수식. 특수문자 포함 속성명은 `note["가격"]` 형태.

## 연산자

| 연산자 | 의미 |
|--------|------|
| `==` `!=` | 같음 / 다름 |
| `>` `<` `>=` `<=` | 비교 (숫자·날짜) |

논리 결합(and/or/not)은 연산자가 아니라 `filters:` 블록의 `and:`/`or:`/`not:` 키로 표현한다 — SKILL.md 필터 문법 참고.

## 전역 함수

값에 붙이는 메서드가 아니라 단독으로 호출하는 함수.

| 함수 | 반환 타입 | 설명 |
|------|----------|------|
| `date(text)` | Date | 문자열을 Date로 변환 |
| `duration(text)` | Duration | 문자열을 Duration으로 변환 (예: `"7 days"`) |
| `now()` | Date | 현재 날짜+시각 |
| `today()` | Date | 오늘 날짜 (시각 없음) |
| `if(cond, a, b?)` | any | cond가 참이면 a, 거짓이면 b(생략 시 빈 값) |
| `min(a, b, ...)` | any | 최솟값 |
| `max(a, b, ...)` | any | 최댓값 |
| `number(value)` | Number | 숫자로 변환 |
| `link(path, display?)` | Link | 경로를 Link로 변환 |
| `list(element)` | List | 값을 List로 감싸거나 그대로 반환 |
| `file(path\|file\|url)` | File | File 객체 반환 |
| `image(path\|file\|url)` | Image | 렌더링 가능한 이미지 객체 |
| `icon(name)` | Icon | Lucide 아이콘 |
| `html(text)` | HTML | 렌더링 가능한 HTML 문자열 |
| `escapeHTML(html)` | String | HTML 특수문자 이스케이프 |
| `random()` | Number | 0~1 난수 |

## Any (타입 검사 — 모든 값에 적용)

| 메서드 | 설명 |
|--------|------|
| `.isTruthy()` | 값을 boolean으로 강제 변환 |
| `.isType(type)` | 타입 일치 검사 |
| `.toString()` | 문자열 표현 |

## Date

### 필드

| 필드 | 설명 |
|------|------|
| `.year` `.month` `.day` | 연/월/일 |
| `.hour` `.minute` `.second` `.millisecond` | 시/분/초/밀리초 |

### 메서드

| 메서드 | 설명 |
|--------|------|
| `.date()` | 시각 부분 제거 |
| `.format(pattern)` | Moment.js 패턴으로 포맷 (예: `"YYYY-MM-DD"`) |
| `.time()` | 시각 부분만 문자열로 추출 |
| `.relative()` | 상대 시간 (예: "3일 전") |
| `.isEmpty()` | 항상 false (Date는 빈 값 없음) |

## Duration

날짜 - 날짜 = Duration. **Duration을 직접 숫자로 쓰지 말 것** — 반드시 필드로 추출한다.

```yaml
# ❌ 잘못된 예
formulas:
  경과: "today() - created"          # Duration, 숫자 아님

# ✅ 올바른 예
formulas:
  경과: "(today() - created).days"   # Duration에서 days 추출
```

### 필드

| 필드 | 설명 |
|------|------|
| `.days` `.hours` `.minutes` `.seconds` `.milliseconds` | 각 단위 수 |

### 날짜 연산

```yaml
formulas:
  마감일: "created + duration('7 days')"
  하루전: "due - duration('1 day')"
```

지원 단위: `milliseconds` `seconds` `minutes` `hours` `days` `weeks` `months` `years`

## String

| 메서드 | 설명 |
|--------|------|
| `.length` | 문자열 길이 (필드, 호출 아님) |
| `.contains(value)` | 부분 문자열 포함 |
| `.containsAll(...values)` | 전부 포함 |
| `.containsAny(...values)` | 하나라도 포함 |
| `.startsWith(query)` | 시작 확인 |
| `.endsWith(query)` | 끝 확인 |
| `.isEmpty()` | 비어있음/없음 |
| `.lower()` | 소문자 변환 |
| `.title()` | 타이틀 케이스 변환 |
| `.trim()` | 앞뒤 공백 제거 |
| `.reverse()` | 문자열 뒤집기 |
| `.repeat(count)` | N회 반복 |
| `.slice(start, end?)` | 부분 문자열 |
| `.split(separator, n?)` | 분리 → List |
| `.replace(pattern, replacement)` | 치환 (정규식 가능) |

## Number

| 메서드 | 설명 |
|--------|------|
| `.abs()` | 절댓값 |
| `.ceil()` | 올림 |
| `.floor()` | 내림 |
| `.round(digits?)` | 반올림 |
| `.toFixed(precision)` | 소수점 고정 문자열 |
| `.isEmpty()` | 없음 검사 |

## List

`values`(summaries의 컬럼 전체 값)도 List로 다뤄진다.

| 메서드 | 설명 |
|--------|------|
| `.length` | 항목 수 (필드) |
| `.contains(value)` | 항목 포함 |
| `.containsAll(...values)` | 전부 포함 |
| `.containsAny(...values)` | 하나라도 포함 |
| `.isEmpty()` | 비어있음 |
| `.filter(value: Boolean)` | 조건 만족 항목만 (람다) |
| `.map(value: Any)` | 항목 변환 (람다) |
| `.reduce(expression, acc)` | 누적 집계 |
| `.sort()` | 오름차순 정렬 |
| `.reverse()` | 역순 |
| `.unique()` | 중복 제거 |
| `.flat()` | 중첩 평탄화 |
| `.join(separator)` | 문자열로 결합 |
| `.slice(start, end?)` | 부분 목록 |

### `values.*` — summaries 전용 집계

top-level `summaries:`의 커스텀 집계식에서 `values`는 해당 컬럼의 전체 값 리스트다. List 메서드를 그대로 쓸 수 있고, 통계용으로 `.mean()`이 확인됨:

```yaml
summaries:
  customAverage: "values.mean().round(3)"
```

대부분의 집계는 커스텀 식 없이 view 내부 `summaries:`의 **내장 이름**으로 충분하다 — `Empty` `Filled` `Unique` `Average` `Max` `Min` `Median` `Range` `Stddev` `Sum` `Earliest` `Latest` `Checked` `Unchecked` (SKILL.md 집계 섹션 참고). `values.reduce(...)` 같은 커스텀 식은 내장 이름으로 안 되는 경우에만 쓴다.

## File

| 속성/메서드 | 설명 |
|------|------|
| `.name` | 파일명 |
| `.basename` | 확장자 제외 파일명 |
| `.path` | vault 루트 기준 경로 |
| `.folder` | 상위 폴더 경로 |
| `.ext` | 확장자 |
| `.size` | 파일 크기 |
| `.ctime` / `.mtime` | 생성/수정 시각 |
| `.tags` | 파일 내 모든 태그 (본문+frontmatter) |
| `.links` | 아웃바운드 링크 (frontmatter 포함) |
| `.backlinks` | 인바운드 링크 — 성능 무거움, 가능하면 `.links` 역방향 조회로 대체 |
| `.embeds` | 노트 내 임베드 목록 |
| `.properties` | 파일의 모든 속성 객체 (vault 변경 시 자동 갱신 안 됨) |
| `.asLink(display?)` | File → Link |
| `.hasLink(otherFile)` | 특정 파일로의 링크 여부 |
| `.hasProperty(name)` | 속성 존재 여부 |
| `.hasTag(...values)` | 태그 포함 여부 |
| `.inFolder(folder)` | 폴더 내부 여부 |

## Object

| 메서드 | 설명 |
|--------|------|
| `.isEmpty()` | 속성 없음 |
| `.keys()` | 키 목록 |
| `.values()` | 값 목록 |

## 정규식

| 메서드 | 설명 |
|--------|------|
| `.matches(value)` | 정규식 매치 여부 (Regexp 값에 대해 호출) |

## 참조

- [Obsidian Bases functions](https://obsidian.md/help/bases/functions)
- [Obsidian Bases syntax](https://obsidian.md/help/bases/syntax)
