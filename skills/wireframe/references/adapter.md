# 앱 어댑터 형식

앱마다 다른 것(메뉴를 어디서 읽는지, 유형을 어떻게 나누는지, 어느 페이지가 대표인지)은 vault 의
`_scripts/wireframe/{app}/` 에 둔다. 스킬의 `scripts/` 는 어느 앱에나 같은 일만 한다.

```
_scripts/wireframe/{app}/
  config.json     # 아래 형식
  menu.sh         # 메뉴 트리 덤프 → menu.json (아래 형식). 메뉴가 없는 앱은 생략
  classify.py     # pages.json 에 type 을 다는 분류 규칙 (usage: python3 -I classify.py pages.json)
  specs/*.json    # 대표 페이지 레이아웃 명세 (spec-schema.md). 다시 그릴 때 재사용
```

기준 예시는 vault `_scripts/wireframe/nicepay-qa/` 다.

## config.json

```json
{
  "app": "nicepay-qa",
  "repo": "~/IdeaProjects/nicepay-qa",
  "src": "qa/frontend/src",
  "router": "App.tsx",
  "base_url": "https://…/payment-v2/qa",
  "out_dir": "20-areas/payment/untact-qa/diagrams",
  "frontmatter": {"project": "payment-untact-qa", "tags": ["untact-qa"]},
  "sitemap": {
    "note": "qa-app-sitemap",
    "collapse_tabs": {"spec": "/spec/:docId"},
    "outside_groups": [{"label": "진입, 공통", "exact": ["/", "/login"]},
                       {"label": "가이드", "suffix": ["/guide"]},
                       {"label": "결과", "contains": ["/result"]}],
    "rest_label": "상세, 하위 화면"
  },
  "wireframe": {
    "note": "qa-app-wireframes",
    "types": [["T1", "API 요청 폼과 응답"], ["T2", "…"]],
    "representative": {"T1": "/nicepay/cancel"},
    "extra": ["/admin/reports/monitor"]
  }
}
```

| 키 | 뜻 |
|---|---|
| `repo`, `src`, `router` | 코드 위치. `routes.py --src {repo}/{src} --router {router}` |
| `base_url` | 배포 화면 대조에 쓰는 주소. 없으면 대조 단계를 건너뛰고 그렇게 보고한다 |
| `out_dir` | 노트를 쓸 vault 폴더 |
| `sitemap.collapse_tabs` | 항목이 많은 탭을 화면 하나로 접는다 (탭 id → 대표 경로) |
| `sitemap.outside_groups` | 메뉴 밖 라우트를 묶는 규칙. `exact`, `suffix`, `contains` 중 먼저 맞는 묶음에 넣는다 |
| `wireframe.note` | 와이어프레임 목록 노트 이름. 화면별 파일은 같은 이름의 하위 폴더에 `{app}-{순번}-{명세 이름}.excalidraw.md` 로 쓴다 |
| `wireframe.types` | 유형 id 와 이름, 그리는 순서. classify.py 의 id 와 같아야 한다 |
| `wireframe.representative` | 유형마다 그릴 대표 라우트 하나 |
| `wireframe.extra` | 유형에서 크게 벗어나 따로 그릴 라우트 |

## menu.json

```json
[{"id": "untact", "label": "비대면 v1",
  "sections": [{"label": "점검 도구",
                "cards": [{"title": "통합테스트", "risk": "live",
                           "items": [{"title": "검증 화면 열기", "to": "/nicepay/payment/verify", "risk": null}]}]}]}]
```

`risk` 는 `live`(실결제) | `write`(쓰기) | null. 사이트맵이 테두리 색으로 구분한다.
메뉴 정의가 TypeScript 상수면 Deno(`--no-check --unstable-sloppy-imports`)로 그 파일만 실행해 덤프한다(nicepay-qa `menu.sh` 참고).
