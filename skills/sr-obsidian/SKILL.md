---
name: sr-obsidian
description: >
  sr-obsidian 플러그인 진입점 — 신규 프로젝트 초기화(init→hub→wbs→history) 또는
  기존 프로젝트 관리(audit→migrate→hub/wbs 갱신) 전체 워크플로우를 오케스트레이션.
  "/sr-obsidian" 단독 호출, "새 프로젝트 시작", "obsidian 프로젝트", "프로젝트 구조 잡아줘",
  "프로젝트 관리", "어떤 스킬 써야 해" 언급 시 사용.
  Keywords: sr-obsidian, obsidian, 프로젝트 시작, 신규 프로젝트, 프로젝트 관리, 워크플로우
allowed-tools: Read, Bash
---

# sr-obsidian — 워크플로우 진입점

sr-obsidian 플러그인의 시작점. 상황을 파악하고 첫 번째 스킬을 즉시 실행한다.

## 스킬 목록

**지식 사이클 (Zettelkasten)**

| 스킬 | 목적 |
|------|------|
| `sr-obsidian:capture` | Fleeting 노트 포착 — 키워드만, 00-inbox/ |
| `sr-obsidian:defuddle` | URL → 마크다운 웹 클리핑, 00-inbox/ 저장 |
| `sr-obsidian:study` | 챕터 분석 → permanent 노트 추출 |
| `sr-obsidian:wiki` | LLM Wiki 용어 페이지 생성 (scan/create/index 모드) |
| `sr-obsidian:lint-wiki` | permanent 노트 4종 품질 검사 (orphan·dangling·MOC·섹션) |
| `sr-obsidian:radar` | 외부 웹 최신 정보 수집 → wiki-term 누적 (60-logs/radar/ + 30-resources/) |

**프로젝트·인시던트 사이클**

| 스킬 | 목적 |
|------|------|
| `sr-obsidian:iss` | ISS 인시던트/이슈 전체 구조 생성 (hub + WBS + steps/ + comms/) |
| `sr-obsidian:scaffold` | 프로젝트 폴더 구조 전체 생성 |
| `sr-obsidian:hub` | 허브 노트(`프로젝트 현황.md`) 생성·갱신 |
| `sr-obsidian:wbs` | WBS 생성·Phase 추가·진행 현황 갱신 |
| `sr-obsidian:history` | ADR 생성, 의사결정 로그, 회의록 |
| `sr-obsidian:handover` | 누적 기록 종합 → 인수인계·경위 문서 (ISS/FT/서비스) |

**시간 기반 로그**

| 스킬 | 목적 |
|------|------|
| `sr-obsidian:daily` | 데일리 노트 생성·갱신 (GitHub Issue → PR 자동화) |
| `sr-obsidian:weekly` | 주간보고 작성 (목~수 사이클, step 계층 형식) |
| `sr-obsidian:retro` | 주간 회고 작성 (월~금, KPI·오픈 이슈 검토) |

**검색**

| 스킬 | 목적 |
|------|------|
| `sr-obsidian:search` | 자연어 쿼리로 vault 전체 검색 — 파일 목록 + 스니펫 반환 |

**공통 후처리**

| 스킬 | 목적 |
|------|------|
| `sr-obsidian:visualize` | MD → HTML 시각화, `diagrams/` 저장 |
| `sr-obsidian:canvas` | .canvas 파일 생성·편집 (ISS 타임라인, 의존관계 맵) |
| `sr-obsidian:obsidian-bases` | .base 파일 생성·편집 (ISS/FT 추적 대시보드) |
| `sr-obsidian:audit` | 폴더·파일 구조 검증 |
| `sr-obsidian:migrate` | 비표준 파일을 표준 위치로 이관 |
| `sr-obsidian:archive` | 완료 ISS 일괄 스캔 → 40-archives/ 이동 |

---

## 상황별 실행 흐름

### 🆕 신규 프로젝트

```
sr-obsidian:scaffold → 폴더 구조 생성 (허브·WBS·docs·diagrams)
      ↓
sr-obsidian:hub      → 허브 노트 생성
      ↓
sr-obsidian:wbs      → WBS 초기화
      ↓
sr-obsidian:history  → ADR 디렉토리 준비 (선택)
```

### 🔄 기존 프로젝트 관리

```
sr-obsidian:audit    → 구조 이상 여부 먼저 점검
      ↓ (이슈 발견 시)
sr-obsidian:migrate  → 비표준 파일 이관
      ↓
sr-obsidian:hub      → 허브 노트 링크·KPI 갱신
sr-obsidian:wbs      → WBS 진행 현황 갱신
sr-obsidian:history  → ADR 추가
```

### 📖 지식 사이클

```
sr-obsidian:capture    → fleeting 포착 (00-inbox/) — 직접 입력
sr-obsidian:defuddle   → URL 웹 클리핑 (00-inbox/) — URL 입력
      ↓
sr-obsidian:study      → permanent 노트 추출
      ↓ (용어 발견 시)
sr-obsidian:wiki       → wiki-term 페이지 생성
      ↓ (주 1회)
sr-obsidian:lint-wiki  → orphan·dangling·MOC·섹션 품질 검사
```

### 📅 시간 기반 로그

```
sr-obsidian:daily    → 오늘 데일리 노트 생성 or 갱신
      ↓ (주말)
sr-obsidian:retro    → 주간 회고 (월~금, KPI·이슈 검토)
      ↓ (수요일)
sr-obsidian:weekly   → 주간보고 (목~수 사이클, 업무 보고)
```

### 📊 시각화

```
sr-obsidian:visualize  → MD → HTML 변환 → diagrams/ 저장 → 허브 링크 연결
```

---

## 실행 방법

**1. 상황 파악** — 대화 컨텍스트에서 아래를 확인한다:

- 프로젝트 경로 언급 여부 (`20-areas/payment/{서비스}` 등)
- 폴더가 이미 존재하는지 (`ls` 또는 `obsidian files` 명령)
- 사용자가 언급한 목적 (신규 vs 관리 vs 시각화)

불명확하면 한 번만 질문:
> "신규 프로젝트인가요, 기존 프로젝트 관리인가요? 프로젝트 경로도 알려주세요."

**2. 첫 스킬 즉시 호출** — 상황이 파악되면 망설이지 말고 첫 번째 스킬을 Skill 도구로 호출한다.

**3. 단계 완료 후 안내** — 각 스킬 완료 시 다음 단계를 1줄로 안내하고, 이어서 진행할지 묻는다.

---

> **참고**: 스킬별 상세 동작은 각 `sr-obsidian:{name}` 스킬에 정의되어 있음.
> 이 스킬은 어떤 스킬을 언제 쓸지 결정하고 시작하는 오케스트레이터 역할.

---

## 참고 문서

노트를 생성·편집하는 스킬(`wiki`·`study`·`visualize`·`canvas`·`obsidian-bases` 등)이
Obsidian Flavored Markdown 문법을 확인해야 할 때 아래 참조 문서를 읽는다.

| 문서 | 내용 |
|------|------|
| [obsidian-markdown](../../references/obsidian-markdown.md) | wikilink·embed·태그·주석·Dataview·Mermaid 문법 총괄 |
| [CALLOUTS](../../references/CALLOUTS.md) | 콜아웃(`> [!note]`) 타입·접기 문법 |
| [EMBEDS](../../references/EMBEDS.md) | 파일·섹션·블록 임베드 문법 |
| [PROPERTIES](../../references/PROPERTIES.md) | 프론트매터 속성 타입·표기 규칙 |
