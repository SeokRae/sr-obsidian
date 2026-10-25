# 시각화 갭 기록

flowcast로 그리지 못한 형태와 flowcast에서 찾은 결함을 vault `60-logs/visualization-gaps.md`(type `log`, append-only)에 남긴다. 새 뷰는 같은 형태가 두 번째로 필요할 때 flowcast로 승격하고, 결함은 바로 고치게 한다. 한 번 쓰고 마는 형태까지 flowcast에 넣으면 스킬이 불어나고, 기록이 없으면 같은 우회를 매번 다시 만든다.

## 행 형식

```
| {YYYY-MM-DD} | {키} | {뷰 또는 결함} | {주제} | {부족했던 것} | {한 일} | {위치} | {open, promoted, fixed 중 하나} |
```

- **키**: 주제가 아니라 그림의 형태를 kebab-case 영문으로 쓴다. 같은 형태면 주제가 달라도 같은 키다. 새 키를 만들기 전에 기존 키를 먼저 본다.
- **종류**: `뷰`는 flowcast에 없는 그림 형태, `결함`은 flowcast 렌더러, 스킬 규칙, 예제의 잘못이다.
- **위치**: 우회한 vault 생성기 경로, 또는 반영한 flowcast Issue 번호.
- **상태**: `open`(vault에서 우회), `promoted`(flowcast에 반영), `fixed`(결함 반영).
- 기존 행은 고치지 않는다. 상태가 바뀌면 같은 키로 새 행을 덧붙인다.
- 갭이 없었으면 `| {날짜} | - | - | {주제} | 갭 없음 | - | - | - |` 한 행.

## 판정

```bash
GAP=60-logs/visualization-gaps.md
grep -c "| {키} |" "$GAP"          # 0이면 첫 사례
grep "| {키} |" "$GAP" | tail -1   # 최신 상태
```

| 상황 | 남길 행 | 제안 |
|---|---|---|
| 새 키(0건) | `open` 행 | 없음 |
| 같은 키, 최신 `open` | `open` 행(두 번째 사례) | flowcast 승격 Issue |
| 같은 키, 최신 `promoted` | 갭 아님. flowcast 스킬로 그린다 | 없음 |
| flowcast 결함, 규칙 결함 | `결함` 행 | 바로 flowcast Issue |

## flowcast Issue 제안

승인을 받은 뒤 `SeokRae/flowcast`에 만든다. 본문에는 키, 사례 목록(날짜, 주제, vault 생성기 경로), 필요한 형태, 입력 데이터의 모양을 적는다. flowcast는 public 저장소라 회사 코드, 실 데이터, 외부 소스 원문을 싣지 않는다. 반영되면 다음 learn 실행이나 직접 기록으로 `promoted` 또는 `fixed` 행을 덧붙인다.
