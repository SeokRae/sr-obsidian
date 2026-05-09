---
name: canvas
description: >
  Obsidian .canvas 파일 생성 및 편집 스킬.
  노드(텍스트·파일·링크·그룹)와 엣지로 구성된 JSON Canvas 형식을 사용한다.
  ISS 타임라인, 서비스 의존관계 맵, 아키텍처 다이어그램, 마인드맵 요청 시 사용.
  Do NOT use for HTML diagrams (use sr-obsidian:visualize instead).
  Do NOT use for Mermaid diagrams (embed in standard .md notes).
  Keywords: canvas, json-canvas, 캔버스, 마인드맵, 의존관계, 다이어그램, 아키텍처 맵
allowed-tools: Read, Write, Edit
---

# sr-obsidian:canvas — Canvas 파일 생성

Obsidian `.canvas` 파일은 JSON Canvas Spec 1.0 형식이다.
최상위 구조: `{"nodes": [...], "edges": [...]}` — 다른 키는 없음.

## 워크플로우

### 신규 Canvas 생성

1. **목적 파악** — 무엇을 시각화하는가 (타임라인·의존관계·마인드맵 등)
2. **저장 위치 결정**:
   - 서비스 다이어그램: `20-areas/{서비스}/diagrams/{이름}.canvas`
   - ISS 관련: `10-projects/{ISS-번호}/{이름}.canvas`
3. **노드 배치 계획** — 좌표 체계: x는 오른쪽이 증가, y는 아래가 증가
4. **JSON 작성** — 노드 → 엣지 순서로 작성
5. **검증** — 아래 Validation Checklist 통과 확인
6. **Write로 저장**

### 기존 Canvas 편집

1. Read로 현재 JSON 읽기
2. 변경할 노드/엣지 파악
3. Edit으로 변경 (파일 전체 재작성 금지, 변경 부분만 Edit)
4. ID 중복 없는지 확인

## 노드

### 공통 속성

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | string | 16자리 소문자 16진수 (고유) |
| `type` | string | `"text"` \| `"file"` \| `"link"` \| `"group"` |
| `x` | number | 좌상단 x 좌표 |
| `y` | number | 좌상단 y 좌표 |
| `width` | number | 노드 너비 |
| `height` | number | 노드 높이 |
| `color` | string | (선택) 색상 |

### 텍스트 노드

```json
{
  "id": "a1b2c3d4e5f6a7b8",
  "type": "text",
  "text": "결제 요청\n금액 검증",
  "x": 0,
  "y": 0,
  "width": 250,
  "height": 100
}
```

> **주의**: 줄바꿈은 `\n` 사용. `\\n`은 `\`와 `n` 문자로 렌더링된다.

### 파일 노드 (vault 내 파일 연결)

```json
{
  "id": "b2c3d4e5f6a7b8c9",
  "type": "file",
  "file": "20-areas/payment/psp/psp 프로젝트 현황.md",
  "x": 300,
  "y": 0,
  "width": 400,
  "height": 300
}
```

subpath로 특정 헤딩 지정: `"subpath": "#아키텍처"`

### 링크 노드 (외부 URL)

```json
{
  "id": "c3d4e5f6a7b8c9d0",
  "type": "link",
  "url": "https://stripe.com/docs",
  "x": 700,
  "y": 0,
  "width": 400,
  "height": 200
}
```

### 그룹 노드 (컨테이너)

```json
{
  "id": "d4e5f6a7b8c9d0e1",
  "type": "group",
  "label": "결제 레이어",
  "x": -50,
  "y": -50,
  "width": 600,
  "height": 400,
  "background": "20-areas/payment/diagrams/bg.png",
  "backgroundStyle": "cover"
}
```

## 엣지

```json
{
  "id": "e5f6a7b8c9d0e1f2",
  "fromNode": "a1b2c3d4e5f6a7b8",
  "fromSide": "right",
  "toNode": "b2c3d4e5f6a7b8c9",
  "toSide": "left",
  "label": "승인 요청",
  "color": "4"
}
```

| 필드 | 설명 |
|------|------|
| `fromSide` / `toSide` | `"top"` \| `"right"` \| `"bottom"` \| `"left"` |
| `label` | (선택) 엣지 레이블 |
| `color` | (선택) 색상 |
| `fromEnd` / `toEnd` | (선택) `"none"` \| `"arrow"` |

## 색상

`canvasColor` 타입: 프리셋 `"1"`~`"6"` 또는 hex `"#FF0000"`.

| 값 | 색상 |
|----|------|
| `"1"` | 빨간색 |
| `"2"` | 주황색 |
| `"3"` | 노란색 |
| `"4"` | 초록색 |
| `"5"` | 파란색 |
| `"6"` | 보라색 |

## ID 생성

16자리 소문자 16진수. Bash로 생성:
```bash
openssl rand -hex 8
```

## 레이아웃 가이드라인

| 요소 | 권장 크기 |
|------|----------|
| 텍스트 노드 | 250×100 (최소) |
| 파일 노드 | 400×300 |
| 링크 노드 | 400×200 |
| 그룹 노드 | 내부 노드보다 100px 여유 |
| 노드 간 간격 | 최소 50px |

좌표 원점(0,0)에서 오른쪽·아래로 배치. 그룹은 내부 노드보다 먼저 JSON에 배치 (렌더링 순서).

## Validation Checklist

저장 전 반드시 확인:

- [ ] 모든 `id`가 16자리 소문자 16진수
- [ ] `id` 중복 없음 (노드 + 엣지 전체)
- [ ] `fromNode` / `toNode`가 실존하는 노드 `id`를 참조
- [ ] 줄바꿈이 `\n` (이스케이프) — 리터럴 줄바꿈 없음
- [ ] `file` 노드의 경로가 vault 루트 기준 상대경로
- [ ] JSON 최상위는 `{"nodes": [...], "edges": [...]}` 만
- [ ] 그룹 노드가 JSON에서 내부 노드보다 먼저 위치
- [ ] 파일 확장자가 `.canvas`

## 완성 예시

ISS 타임라인과 서비스 의존관계 맵 → [EXAMPLES.md](references/EXAMPLES.md)

## 참조

- [JSON Canvas Spec 1.0](https://jsoncanvas.org)
- [Obsidian Canvas](https://help.obsidian.md/plugins/canvas)
