# 뷰 고르기

그림은 보여 주려는 질문으로 고른다. 기본 세트는 component(구성)와 sequence(호출)의 2장이고, 질문이 더 있으면 더한다.

| 질문 | 뷰 | 스킬 | 소스 |
|---|---|---|---|
| 무엇으로 이뤄졌고 어떻게 이어지나 | component | `flowcast:flowcast` (또는 `flowcast:component`) | 흐름 문서 `## 구성 요소` 표 |
| 누가 누구를 어떤 순서로 부르나 (정상, 분기, 예외) | sequence | `flowcast:flowcast` (또는 `flowcast:sequence`) | 시나리오 노트 |
| 어느 존과 노드에 놓이고 어느 구간을 지나나 | topology | `flowcast:flowcast` (또는 `flowcast:topology`) | 흐름 문서 |
| 부품 하나가 움직이는 원리 (주소 변환, 스택, 회수) | mechanism | `flowcast:mechanism` | 진실 모델(`model.mjs`)과 1차 출처 |
| 흐름을 따라 상태나 위치가 계속 바뀌는 모습 | state-loop | `flowcast:state-loop` | 시나리오 정상 흐름 |

## 위임할 때

- component, sequence, topology 여러 장은 `flowcast:flowcast`에 한 번에 넘긴다. 소스 게이트를 통과하려면 흐름 문서와 시나리오가 먼저 vault에 있어야 한다.
- `out_dir`과 `vault_iframe`은 `{주제 폴더}/diagrams`의 절대경로다. `$(pwd)` 같은 셸 치환을 쓰지 않고 실제 경로를 적는다.
- sequence의 레인과 스텝 번호는 시나리오 노트와 같아야 한다. 분기와 예외가 그림에서 빠지지 않게 시나리오를 소스로 준다.
- mechanism과 state-loop는 `/flowcast` 팬아웃 대상이 아니라 각 스킬을 직접 부른다. 한 번에 한 장이다.

## flowcast에 없는 형태

아래는 flowcast 뷰로 아직 그릴 수 없어 vault 생성기로 만든 형태다. 같은 형태가 또 필요하면 [gap-log.md](gap-log.md)의 승격 판정을 따른다. 최신 상태는 vault `60-logs/visualization-gaps.md`가 정본이다.

| 키 | 형태 | 첫 사례의 생성기 |
|---|---|---|
| `stage-walkthrough` | 구성도 배치를 고정하고 구간마다 쓰이는 구성 요소만 켠 그림 여러 장 | `_scripts/excalidraw/jvm_startup_walkthrough.py` |
| `calltree` | 한 스레드 안 중첩 호출을 깊이로 보여 주는 콜스택 트리 | `_scripts/excalidraw/jvm_startup_views.py` |
| `flowchart` | 구간과 분기를 판단 노드로 잇는 순서도 | `_scripts/excalidraw/jvm_startup_views.py` |
