---
name: iss
description: >
  ISS 인시던트/이슈 전체 구조 자동 생성 — hub + WBS + steps/ + comms/.
  파트너 문의·운영 이슈·인시던트 대응을 시작할 때 사용.
  Do NOT use for non-ISS project/knowledge initialization (use sr-obsidian:scaffold or sr-obsidian:hub).
  Keywords: iss, 이슈, 인시던트, 문의 대응, ISS 생성, issue create, incident
allowed-tools: Read, Write, Bash, Grep, Glob
---

# sr-obsidian:iss — ISS 구조 자동 생성

파트너 문의·운영 이슈·인시던트를 시작할 때 ISS 전체 디렉토리 구조를 한 번에 생성한다.

## ⚡ 속도 최적화 (필수)

**목표: 전체 실행 2분 이내**

| 규칙 | 세부 |
|------|------|
| 파일 병렬 Write | Step 5의 모든 파일(hub + WBS + steps + comms)을 **단일 응답에서 Write 도구 동시 호출** — 파일 간 의존 없음 |
| 관련 이슈 Read 최소화 | related-iss 추가 시 **hub 파일 1개만** 읽기 — steps/comms 개별 파일 읽기 금지 |
| AskUserQuestion 최소화 | 대화 맥락에서 title·slug·steps 충분히 파악했으면 질문 없이 진행 |
| humanize 논블로킹 | outbound comms 포함 시 전체 파일 Write 완료 후 `/humanize` 별도 호출 — 파일 쓰기 전 호출 금지 |

## 생성 구조

```
10-projects/ISS-{NNN}-{slug}/
├── ISS-{NNN} {title}.md      ← hub (tpl-issue 기반)
├── ISS-{NNN} WBS.md           ← gantt-b Gantt
├── comms/                     ← 외부 질의·답변 원문 (파트너/Stripe 등)
│   └── YYYY-MM-DD {주제}.md
└── steps/
    ├── step-01-{slug}.md      ← 발생/발견
    └── step-NN-{slug}.md      ← 조치/후속
```

> **comms/ 규칙**: 파트너·외부 질의 원문은 반드시 ISS/comms/ 에서 관리.
> FT comms/는 FT 자체 내부 커뮤니케이션 전용 — ISS에서 파생된 외부 질의는 FT comms/ 금지.
> FT timeline에서 참조할 때는 ISS 경유 링크 사용: `[[ISS-{NNN} {title}|ISS-{NNN}]] → [[질의 파일|요약]]`

## 실행 절차

### Step 1. 다음 ISS 번호 확인

```bash
ls 10-projects/ | grep ISS && ls 40-archives/ | grep ISS
```

→ 가장 높은 번호 + 1 = 다음 ISS 번호 (3자리 zero-padding)

### Step 2. 사용자에게 확인할 정보

인자로 받거나 대화에서 파악:

| 항목 | 설명 | 예시 |
|------|------|------|
| `title` | 이슈 제목 (한글 가능) | `자비스앤빌런즈 NICEPAY 빌링 문의 대응` |
| `slug` | 디렉토리명용 kebab-case | `nicepay-billing-partner-inquiry` |
| `source` | 발생 출처 | `개인` / `github` / `회의` / `파트너` |
| `related-ft` | 연관 FT ID (있으면) | `FT-002` |
| `steps` | 단계 목록 (제목 + section) | 아래 참조 |

steps 항목이 없으면 이슈 내용 기반으로 자동 추론.

**section 유효값** (gantt-b 표시 기준):
`발생` | `발견` | `조사` | `원인 분석` | `조치` | `후속`

### Step 3. GitHub Issue 생성

```bash
gh issue create \
  --repo SeokRae/knowledge-labs \
  --title "ISS-{NNN}: {title}" \
  --body "..."
```

body 포함 항목: 설명, 체크리스트(steps 기반), 관련 FT

### Step 4. Feature 브랜치 생성

```bash
git checkout -b feature/{gh-issue-번호}-iss-{NNN}-{slug}
```

### Step 5. 파일 생성

**병렬 Write (필수)**: hub · WBS · 모든 steps · comms 를 **단일 응답에서 동시 Write** — 파일 간 의존 없으므로 순차 실행 금지

#### hub: `ISS-{NNN} {title}.md`

````markdown
---
type: issue
id: ISS-{NNN}
created: {today}
tags: [issue]
status: open
source: {source}
assignee: SeokRae
due:
effort:
github: SeokRae/knowledge-labs#{gh-issue-번호}
related-ft: {related-ft}
description: {한 줄 설명}
---

# ISS-{NNN} {title}

← [[이슈 트래킹 MOC]]

## 설명

{이슈 배경 및 목적}

## 진행 현황

> 한눈에 보는 요약. **단계 표는 `steps/` frontmatter 기반 자동 갱신**(step 상태·완료일 바뀌면 노트 열 때 반영). **안건 표는 수동 갱신** — 결정이 확정되면 옮긴다.

### 단계 진행 (자동)

```dataviewjs
const S = { done: "✅ 완료", "in-progress": "🔄 진행중", ready: "⏳ 대기" };
const steps = dv.pages()
  .where(p => p.incident == "ISS-{NNN}" && p.step)
  .sort(p => p.step, 'asc');
dv.table(
  ["#", "구분", "단계", "상태", "완료일"],
  steps.map(p => [p.step, p.section, p.file.link, S[p.status] ?? p.status, p["end-date"] ?? "—"])
);
```

### 안건 해결 / 미결 (수동)

> 이슈에서 다루는 안건을 결정 상태별로 정리. 회신·결정이 확정되면 ⏳ → ✅ 로 옮긴다. (안건 없으면 섹션 생략 가능)

| 안건 | 상태 | 결론/담당 |
|------|------|-----------|
| {핵심 안건} | ✅ 확정 / ⏳ 미결 | {결론 또는 담당 부서} |

> **다음 액션**: ① {구체적인 다음 액션}

## 체크리스트

{steps 기반 체크리스트}

## 내부 공유

> 실시간 현황 공유용 — 사업부·비기술 담당자 대상. 업데이트 시 날짜 갱신.
> **금지**: 내부 이슈 ID(ISS-번호), 기술 식별자(payauthz ID 등) 직접 노출.

**[{인시던트 유형}] 현황 ({today} 업데이트)**

**현상**
{한두 문장 서술. 코드·ID 없이 현상만}

**원인**
{한두 문장 서술형. 기술 용어는 풀어서}

**영향**
- {결제수단, 금액, 가맹점 등 — 필요 시}

**처리 결과**
{현재까지 완료된 조치 서술}. {미결 사항 및 다음 단계 서술}.

---

## 보고용 서머리

> **작성 기준 — STAR**
> 1. S(상황)·T(과제)·A(행동)·R(결과) 순서 — 면접·평가 보고에 바로 사용할 밀도
> 2. 각 항목 1~3줄 — 세부 내용(트랜잭션 ID·원문·JSON)은 step 파일에
> 3. 진행 중 이슈는 R에 "(진행 중)" 표기, 미결은 STAR 밖 별도 항목
> 4. **내부 이슈 ID(ISS-번호, FT-번호) 금지** — "이전에도 동일 패턴 발생 이력이 있다" 형식으로 서술
> 5. **기술 식별자(payauthz ID 등) 직접 노출 금지** — step 파일에서 관리
> 6. 대상 독자: 사업부·비기술 담당자도 맥락 파악 가능한 서술 수준 유지

■ S — Situation

{어떤 서비스에서, 어떤 현상이, 왜 문제였는지 — 서술형}

■ T — Task

{해결해야 할 과제와 제약 조건 — 서술형}

■ A — Action

{구체적으로 수행한 분석·수정·테스트 — 서술형. 진행 중이면 마지막에 "(진행 중)"}

■ R — Result

{정량 결과·효과 — 서술형. 진행 중이면 "(진행 중)"}

■ 미결

① {구체적인 다음 액션}

## 프레젠테이션 요약

### SS1 개요

개념 정의: {인시던트 유형을 기술 용어로 한 줄 정의}
발생일: {YYYY-MM-DD}
심각도: {상·중·하}
영향 범위: {서비스·가맹점·결제 수단 등}

### SS2 본론

원인 분석: {근본 원인 1~3줄}
조치 내용: {핵심 대응 행위 요약}

### SS3 결론

재발방지: {구조적 개선사항 한 줄}
시사점: {"~를 통해 ~를 달성한다" 형태}

## 진행 기록

- {today} — 이슈 생성

## 관련 메모

- [[ISS-{NNN} WBS]]
- [[steps/step-01-...]]
````

> **내부 공유 · 보고용 서머리 작성 시 주의**
> - 내부 공유: 실시간 현황 공유용. 날짜 갱신하며 업데이트. 내부 ID·기술 식별자 미포함.
> - 보고용 서머리: 이슈 종료 후 회고·면접용. STAR 구조, 서술형, 내부 ID 없이 작성.

#### WBS: `ISS-{NNN} WBS.md`

````markdown
---
type: literature
created: {today}
start-date: {today}
tags: [timeline, dataviewjs, incident]
status: in-progress
related-issue: ISS-{NNN}
---

# ISS-{NNN} WBS

← [[ISS-{NNN} {title}]]

> **동적 렌더링**: `steps/` 폴더의 `incident-step` 파일 frontmatter 기반으로 자동 생성.

---

```dataviewjs
await dv.view("_scripts/gantt/gantt-b");
```

---

## 관련 메모

- [[ISS-{NNN} {title}]]
````

#### steps: `steps/step-{NN}-{slug}.md`

각 step마다 생성:

```markdown
---
type: incident-step
incident: ISS-{NNN}
step: {N}
section: {section}     # 발생|발견|조사|원인 분석|조치|후속
star-target: {S|T|A|R} # 이 step이 뒷받침하는 STAR 항목 (S=발생/발견, T=조사/원인분석, A=조치, R=후속)
title: {step 제목}
start-date: {today}    # 미래 step은 비워둠
end-date:
status: {done|in-progress|ready}
---

# {step 제목}

## 상황

{이 단계에서 일어난 일}

## 확인 내용

## 대응

## 완료 조건

- [ ] {완료 기준}

---

← [[ISS-{NNN} WBS]]
```

#### comms: `comms/YYYY-MM-DD-{slug}.md`

외부 질의·답변이 발생했을 때 생성:

```markdown
---
type: incident-step
incident: ISS-{NNN}
date: YYYY-MM-DD
direction: outbound | inbound | both
from: {발신자}
to: {수신자}
summary: {한 줄 요약}
---

# YYYY-MM-DD — {제목}

← [[../ISS-{NNN} WBS]]

## 원문 ({발신자} → {수신자}, {채널}, {날짜})

> (원문 blockquote)

## 분석 / 요약
```

> **outbound 영문 메시지 humanize 검토 (필수)**
> outbound comm 에 영문 메시지가 포함되면 파일 저장 전 `/humanize` 스킬로 검토한다.
> 1. 영문 초안 작성 완료
> 2. `/humanize` 호출 → 윤문 결과 확인 (AI 패턴·수동태·em dash 제거)
> 3. 수정 반영 후 파일 저장
> inbound 수신 메시지는 검토 불필요 (원문 보존 원칙).

**규칙**:
- `start-date`: 완료된 step은 실제 날짜, 미래 step은 비워둠
- `end-date`: 체크리스트 전부 `- [x]` 완료 시만 입력
- `status` 유효값: `ready` (착수 전) / `in-progress` / `done` — `pending` 사용 금지 (린터 차단)
- 파일명: `step-{NN}-{kebab-slug}.md` (두 자리 zero-padding, 한글 사용)
- step 번호 = 실제 작업 선후 관계 (파일 생성 순서 아님)

### Step 6. Ingest Log

파일 생성(hub·WBS·steps) 완료 후 `60-logs/ingest-log.md` 말미에 1개 항목 append:

```bash
printf '\n## [%s] iss | ISS-{NNN} {title} (issue) → {N}개\n- 10-projects/ISS-{NNN}-{slug}/ISS-{NNN} {title}.md\n- 10-projects/ISS-{NNN}-{slug}/ISS-{NNN} WBS.md\n- (steps/ 파일 목록)\n' "$(date +%Y-%m-%d)" >> 60-logs/ingest-log.md
```

### Step 7. 커밋

```bash
git add 10-projects/ISS-{NNN}-{slug}/
git commit -m "docs: ISS-{NNN} {title} 구조 생성 (#{gh-issue-번호})"
```

## 이슈 유형별 기본 steps

### 파트너 문의 대응

| step | section | star-target | 제목 |
|------|---------|-------------|------|
| 01 | 발생 | S | 문의 수신 및 내용 분석 |
| 02 | 조치 | A | 내부/외부 확인 사항 처리 |
| 03 | 후속 | R | 파트너 답변 발송 |

### 운영 인시던트

| step | section | star-target | 제목 |
|------|---------|-------------|------|
| 01 | 발생 | S | 장애 발생 인지 |
| 02 | 발견 | S | 원인 탐색 |
| 03 | 원인 분석 | T | 근본 원인 확인 |
| 04 | 조치 | A | 긴급 조치 실행 |
| 05 | 후속 | R | 재발 방지 및 모니터링 |

### 외부 요청 대응 (API 연동 등)

| step | section | star-target | 제목 |
|------|---------|-------------|------|
| 01 | 발생 | S | 요청 수신 및 분석 |
| 02 | 조사 | T | 스펙/환경 확인 |
| 03 | 조치 | A | 구현 또는 가이드 제공 |
| 04 | 후속 | R | 확인 완료 및 종료 |

## 완료 후 안내

- Obsidian에서 `ISS-{NNN} WBS.md` 열어 gantt-b 렌더링 확인
- step 진행 시마다 `start-date` / 완료 시 `end-date` 채울 것
- 이슈 종료 시: `10-projects/` → `40-archives/`로 폴더 이동 후 PR

## 판단 기준

| 상황 | 처리 |
|------|------|
| ISS 번호 중복 | `10-projects/ISS-*/` + `40-archives/ISS-*/` 중 최대 번호 + 1 재계산 |
| 관련 FT 있음 | hub 파일에 `related-ft:` 필드 추가, FT ↔ ISS 양방향 링크 |
| steps/ 비어 있음 | 이슈 유형별 기본 steps 표에서 자동 생성 |
| 파트너 문의인지 내부 이슈인지 불명확 | "파트너 문의인가요, 내부 운영 이슈인가요?" 질문 |
| comms/ 필요 여부 불명확 | 외부 파트너 문의 포함 시 comms/ 생성, 내부 이슈면 선택 |
