# 레이아웃 명세 형식 (page spec JSON)

페이지 하나 = JSON 파일 하나. 화면에 **기본 상태로 처음 그려지는 모습**을 위에서 아래 순서로 적는다.
색, 아이콘, CSS는 적지 않는다. 배치와 요소의 종류, 실제 화면 문구만 적는다.
`scripts/build_wireframes.py` 가 이 형식을 읽어 그린다.

```json
{
  "route": "/nicepay/cancel",
  "type": "T1",
  "title": "취소",
  "file": "pages/nicepay/cancel/CancelPage.tsx",
  "layout": "single",
  "blocks": [ ...block ],
  "notes": ["그림에 담지 못한 사실 (최대 5줄, 6줄부터는 그려지지 않음)"]
}
```

- `route`: 라우터의 path 그대로. 공통 헤더는 `"(공통)"`, type `"-"`.
- `layout`: `single` | `two-col`. two-col 이면 blocks 안에서 `row` 로 좌우를 나눈다.

## block 종류

모든 block 은 선택 필드 `ann` 을 가질 수 있다. 그 영역을 그리는 React 컴포넌트 이름이다(예 `RequestConfigCard`). 렌더러가 그림 오른쪽 거터에 보라색으로 적는다.

| type | 필드 | 뜻 |
|---|---|---|
| `header` | `title`, `subtitle?` | 페이지 제목과 부제. 레이아웃이 그리는 제목이라도 첫 블록으로 적는다 |
| `tabs` | `items: [str]`, `active: int` | 모드 탭, 세그먼트, 토글 버튼 묶음 |
| `banner` | `text`, `tone: info\|warn\|error\|ok` | 안내, 경고, 판정 배너 |
| `card` | `title`, `badge?`, `children: [block]`, `collapsed?: bool` | 테두리 있는 묶음. 카드 부제는 `badge` 에 넣는다 |
| `row` | `children: [block]`, `weights?: [int]` | 가로 배치 (2~4칸) |
| `fields` | `items: [{label, kind, value?}]` | 입력 폼. kind 는 `input\|select\|radio\|checkbox\|textarea\|date\|more`. 8개 넘으면 앞 8개 + `{"label": "+N개 더", "kind": "more"}` |
| `buttons` | `items: [{label, primary?: bool}]` | 버튼 줄 |
| `table` | `columns: [str]`, `rows: int` | 표. 행 수는 예시용 3~5. 행 안의 버튼은 열로 만들지 않고 ann 에 적는다 |
| `kv` | `keys: [str]` | 키-값 표 (최대 10키) |
| `chart` | `label` | 차트 자리 |
| `diagram` | `label` | 흐름도, DAG, 시퀀스 다이어그램 자리 |
| `code` | `label` | JSON, 요청 원문, 마크다운 본문 자리 |
| `list` | `items: [str]` | 글머리 목록, 반복 행의 템플릿 (최대 8) |
| `grid` | `items: [str]`, `cols: int` | 타일 격자 (최대 12) |
| `stats` | `items: [{label, value?}]` | 숫자 타일 줄. value 는 자리표시(`000`, `—`)만, 실제 값 금지 |
| `text` | `text` | 짧은 설명 문단, 섹션 머리 |

## 규칙

1. **JSX 렌더 순서를 그대로 따른다.** 하위 컴포넌트가 큰 영역이면 그 파일도 열어 안쪽 구성을 적는다(1~2단계).
2. **문구는 화면에 보이는 기본 로케일 값이다.** i18n 키면 사전에서 값을 찾는다. 키가 곧 원문인 앱도 있다. 못 찾으면 키를 적고 notes 에 남긴다.
3. **공용 레이아웃(앱 헤더, 푸터)은 블록으로 적지 않는다.** 앱 헤더는 `(공통)` 명세 한 장으로 따로 쓴다. 하단 고정 액션 바의 버튼은 마지막 `buttons` 블록으로 적는다.
4. **접힘은 코드의 첫 방문 기본값으로 정한다.** 사용자가 접고 편 상태를 저장하는 훅(localStorage 등)이 있으면 그 기본값을 따른다. 기본 접힘 카드는 `collapsed: true` 로 두고, 접힌 채 보이는 요약 줄(환경 칩, 엔드포인트)만 children 에 넣는다. `<details>` 기반 선택 섹션도 닫힘이 기본이면 접힌 카드다.
5. **실행 뒤에만 보이는 영역도 적되 ann 끝에 ` (실행 뒤)` 를 붙인다.** 진입하자마자 자동 조회하는 화면은 응답 뒤 영역에 붙인다.
6. **값이 응답으로 정해지는 곳은 자리표시로 적는다.** 판정 문구, 건수, 가맹점 이름 같은 실제 데이터는 적지 않는다.
7. **블록은 최상위 기준 25개를 넘기지 않는다.** 반복 구조는 하나만 적고 notes 에 반복 수를 적는다.
8. **추측하지 않는다.** 코드에서 확인한 것만 적는다. 코드 분기로 고른 상태(예: 결제 성공 분기)는 notes 에 어떤 분기인지 적는다.
