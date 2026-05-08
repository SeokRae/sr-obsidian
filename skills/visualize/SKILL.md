---
name: visualize
description: >
  프로젝트 문서(MD)를 HTML 시각화로 변환하여 diagrams/에 저장하고 페어드 MD + 허브 링크까지 연결.
  "시각화", "HTML로 만들어줘", "다이어그램 생성", "슬라이드 만들어줘" 요청 시 사용.
  Keywords: visualize, html, diagram, 시각화, 슬라이드, 보고서 HTML, 다이어그램
allowed-tools: Read, Write, Bash, Edit
---

# sr-obsidian:visualize — HTML 시각화 생성

MD 문서를 `claude-visualize:visualize` 스킬로 HTML로 변환하고
Obsidian vault 규칙(diagrams/ 저장, 페어드 MD, 허브 링크)에 맞게 후처리한다.

## 문서 계층 원칙

```
docs/reports/{report}.md          ← 소스 MD (전체 내용·분석·미결 포함)
    ↓ 내용 선별
diagrams/{report}.html            ← 전체 시각화
    ↓ 보고용 선별
diagrams/{report}-delivery.html   ← 전달본 (보고·킥오프 등)
```

- MD = 소스 오브 트루스 — 모든 내용을 여기에 먼저 작성
- HTML = MD에서 파생 — `diagrams/` 에만 위치
- `docs/` 에 HTML 파일 금지

## 실행 절차

### Step 1. 소스 문서 확인

```bash
# 시각화할 소스 MD 읽기
cat "20-areas/payment/{project-id}/docs/{subfolder}/{file}.md"
```

### Step 2. 시각화 유형 선택

`claude-visualize:visualize` 유형 기준:

| 유형 | 적합한 프로젝트 문서 |
|------|---------------------|
| `report` | 구축 보고서, 분석 문서, ADR 모음 |
| `deck` | 킥오프·착수 보고서, 경영진 보고 |
| `timeline` | Phase 상세, 로드맵, WBS 요약 |
| `dashboard` | KPI 현황, Phase 진행률, 운영 상태 |
| `flow` | 인터페이스 흐름, 서비스 연동도 |
| `topology` | 인프라 토폴로지, 서비스 메시 |
| `comparison` | Before/After, 아키텍처 옵션 비교 |
| `mockup` | UI 화면 설계, "화면 그려줘" 요청 — A/B 탭 전환 단일 HTML |

### Step 3. HTML 생성 또는 수정

**대상 파일 존재 여부 먼저 확인:**

```bash
ls "20-areas/payment/{project-id}/diagrams/{file}.html" 2>/dev/null && echo "EXISTS" || echo "NEW"
```

**기존 파일인 경우 (개선·업데이트) — Edit-first:**
1. Read로 기존 HTML 전체 읽기
2. 변경이 필요한 부분만 식별 (노드 좌표, 엣지 경로, 색상, 텍스트)
3. Edit 도구로 해당 부분만 교체 — Write 전체 재작성 금지
4. 수정 줄 수가 50줄 이상이면 bash-runner 서브에이전트에 위임

**신규 파일인 경우 — Write:**

`claude-visualize:visualize` 스킬을 호출하여 HTML 생성:

- 소스 MD 내용을 기반으로 시각화
- **출력 파일명**: `diagrams/{project-id}-{report-type}.html`
  - 예: `diagrams/payment-psp-킥오프-보고서.html`
  - 전달본: `diagrams/payment-psp-킥오프-delivery.html`

**절대경로** 사용:
```
/Users/sr/obsidian/sr-labs/20-areas/payment/{project-id}/diagrams/{file}.html
```

### Step 4. 페어드 MD 생성

HTML 파일과 같은 이름의 MD 파일을 `diagrams/` 에 생성:

```markdown
---
type: diagram
created: {YYYY-MM-DD}
html: diagrams/{file}.html
source: docs/{subfolder}/{source}.md
tags: [diagram, {project-id}]
---

# {제목}

← [[{project-id} 프로젝트 현황]]

<iframe src="file:///Users/sr/obsidian/sr-labs/20-areas/payment/{project-id}/diagrams/{file}.html"
        width="100%" height="{height}" style="border:none;border-radius:8px;"></iframe>

## 개요

{시각화 목적 한 줄}

## 섹션 구성

| 섹션 | 내용 |
|------|------|
| {섹션명} | {내용 요약} |
```

**iframe height 기준:**
- deck/report (full slides): `height="900"`
- timeline (37 steps ≈ 3000px SVG): `height="3400"`
- dashboard: `height="700"`
- topology: `height="800"`
- mockup: `height="900"`

### Step 5. 허브 노트 연결

허브 노트(`{project-id} 프로젝트 현황.md`)의 `## 📐 다이어그램` 섹션에 링크 추가:

```markdown
- [[diagrams/{file}|{제목}]] — {한 줄 설명}
```

또는 `sr-obsidian:hub` 스킬로 위임.

### Step 6. 완료 보고 + 자체 평가

```
✅ HTML 생성/수정: diagrams/{file}.html
✅ 페어드 MD: diagrams/{file}.md
✅ 허브 링크: {project-id} 프로젝트 현황.md ## 📐 다이어그램 추가

Obsidian에서 바로 확인:
  [[diagrams/{file}]]
```

**자체 평가 (완료 보고 후 반드시 수행):**

| 항목 | 확인 | 비고 |
|------|------|------|
| 기존 파일 개선 시 Edit 사용 | ✅/❌ | Write 전체 재작성 여부 |
| 변경 줄 수 최소화 | ✅/❌ | 실제 변경 줄 수 기록 |
| 출력 토큰 한도 위험 여부 | ✅/❌ | 500줄↑ Write 시 서브에이전트 사용 |
| 소요 시간 적정 여부 | ✅/❌ | 10분 초과 시 원인 기록 |

개선점이 있으면 `~/.claude/rules/corrections.md` 또는 프로젝트 memory에 기록한다.
