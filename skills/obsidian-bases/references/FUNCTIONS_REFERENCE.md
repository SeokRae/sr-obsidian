# Functions Reference

## 전역 함수

| 함수 | 반환 타입 | 설명 |
|------|----------|------|
| `date(text)` | Date | 문자열을 Date로 변환 |
| `duration(text)` | Duration | 문자열을 Duration으로 변환 (예: `"3 days"`) |
| `now()` | Date | 현재 날짜+시각 |
| `today()` | Date | 오늘 날짜 (시각 없음) |
| `if(cond, a, b)` | any | cond가 참이면 a, 거짓이면 b |
| `min(a, b)` | any | 최솟값 |
| `max(a, b)` | any | 최댓값 |
| `number(value)` | Number | 숫자로 변환 |
| `link(file)` | Link | 파일을 Link로 변환 |
| `list(...)` | List | 값 목록 생성 |
| `file(path)` | File | 경로를 File로 변환 |
| `image(url)` | Image | URL을 Image로 변환 |
| `icon(name)` | Icon | Lucide 아이콘 |
| `html(text)` | HTML | HTML 문자열 렌더링 |
| `escapeHTML(text)` | String | HTML 이스케이프 |
| `isTruthy(value)` | Boolean | falsy 값 검사 |
| `isType(value, type)` | Boolean | 타입 검사 |
| `toString(value)` | String | 문자열 변환 |

## Date 함수

### 필드

| 필드 | 설명 |
|------|------|
| `.year` | 연도 |
| `.month` | 월 (1-12) |
| `.day` | 일 |
| `.hour` | 시 |
| `.minute` | 분 |
| `.second` | 초 |
| `.millisecond` | 밀리초 |

### 함수

| 함수 | 설명 |
|------|------|
| `date(text)` | 문자열 → Date |
| `format(date, pattern)` | 날짜 포맷 (예: `"YYYY-MM-DD"`) |
| `time(date)` | 시각 부분 추출 |
| `relative(date)` | 상대 시간 (예: "3일 전") |
| `isEmpty(date)` | null/undefined 검사 |

## Duration 타입

날짜 - 날짜 = Duration. 주의: Duration을 직접 숫자로 사용하지 말 것.

```yaml
# ❌ 잘못된 예
expression: "today() - created"          # Duration, 숫자 아님

# ✅ 올바른 예
expression: "(today() - created).days"   # Duration에서 days 추출
```

### Duration 필드

| 필드 | 설명 |
|------|------|
| `.days` | 일 수 |
| `.hours` | 시간 수 |
| `.minutes` | 분 수 |
| `.seconds` | 초 수 |
| `.milliseconds` | 밀리초 수 |

### 날짜 연산

```yaml
# 날짜에 기간 더하기/빼기
expression: "created + duration('7 days')"
expression: "due - duration('1 day')"
```

지원 단위: `milliseconds`, `seconds`, `minutes`, `hours`, `days`, `weeks`, `months`, `years`

## String 함수

| 함수 | 설명 |
|------|------|
| `.length` | 문자열 길이 |
| `upper(str)` | 대문자 |
| `lower(str)` | 소문자 |
| `trim(str)` | 앞뒤 공백 제거 |
| `slice(str, start, end)` | 부분 문자열 |
| `split(str, delimiter)` | 분리 → List |
| `join(list, delimiter)` | List → 문자열 |
| `replace(str, search, replacement)` | 치환 |
| `contains(str, search)` | 포함 여부 |
| `startsWith(str, prefix)` | 시작 확인 |
| `endsWith(str, suffix)` | 끝 확인 |
| `padStart(str, length, char)` | 앞 패딩 |
| `padEnd(str, length, char)` | 뒤 패딩 |
| `repeat(str, count)` | 반복 |

## Number 함수

| 함수 | 설명 |
|------|------|
| `abs(n)` | 절댓값 |
| `ceil(n)` | 올림 |
| `floor(n)` | 내림 |
| `round(n, decimals?)` | 반올림 |
| `toFixed(n, decimals)` | 소수점 고정 |

## List 함수

| 함수 | 설명 |
|------|------|
| `.length` | 목록 길이 |
| `first(list)` | 첫 번째 항목 |
| `last(list)` | 마지막 항목 |
| `filter(list, fn)` | 필터 (람다: `item => ...`) |
| `map(list, fn)` | 변환 (람다: `item => ...`) |
| `reduce(list, fn, init)` | 집계 (람다: `(acc, item) => ...`) |
| `sort(list, fn?)` | 정렬 |
| `reverse(list)` | 역순 |
| `unique(list)` | 중복 제거 |
| `flatten(list)` | 중첩 평탄화 |
| `includes(list, value)` | 포함 여부 |
| `indexOf(list, value)` | 인덱스 |
| `slice(list, start, end)` | 부분 목록 |

## File 함수

| 함수 | 설명 |
|------|------|
| `asLink(file)` | File → Link |
| `hasLink(file, link)` | 특정 링크 포함 여부 |
| `hasTag(file, tag)` | 태그 포함 여부 |
| `hasProperty(file, property)` | 속성 포함 여부 |
| `inFolder(file, folder)` | 폴더 내 여부 |

## Link 함수

| 함수 | 설명 |
|------|------|
| `asFile(link)` | Link → File |
| `linksTo(link, file)` | 특정 파일로의 링크 여부 |

## Object 함수

| 함수 | 설명 |
|------|------|
| `isEmpty(obj)` | 비어 있음 여부 |
| `keys(obj)` | 키 목록 |
| `values(obj)` | 값 목록 |

## 정규식 함수

| 함수 | 설명 |
|------|------|
| `matches(str, pattern)` | 정규식 매치 여부 |
