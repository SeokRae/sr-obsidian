# ISS 템플릿 (hub · WBS · summary · steps · comms)

`sr-obsidian:iss` Step 5(파일 생성)에서 사용하는 전체 템플릿.
플레이스홀더(`{NNN}`, `{title}`, `{today}` 등)는 실제 값으로 치환한다.

## hub: `ISS-{NNN} {title}.md`

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

## WBS: `ISS-{NNN} WBS.md`

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

## summary: `ISS-{NNN} summary.md`

인시던트의 **히스토리(맥락·흐름)를 서사로 파악**하기 위한 노트. hub의 `보고용 서머리`(STAR, 종료 후 보고용 압축)와 목적이 다르다 — 이건 **진행 중** 흐름 파악용이다. 생성 시엔 배경 seed만 채우고, steps/comms가 쌓이면 아래 **요약 노트 갱신** 절차로 이어 붙인다.

```markdown
---
type: summary
incident: ISS-{NNN}
created: {today}
updated: {today}
tags: [summary, incident, history]
related-issue: ISS-{NNN}
---

# ISS-{NNN} 요약 (히스토리)

← [[ISS-{NNN} {title}]]

> **목적**: 이 인시던트가 어떤 배경에서 시작돼 어떻게 흘러왔고 지금 어디까지 왔는지 **서사로 파악**한다.
> steps/·comms/·진행 기록이 쌓일 때마다 갱신한다. **완료/미완 체크가 아니라 맥락·흐름을 서술**한다.

## 배경

{왜 이 이슈가 시작됐는지 — 발생/발견 국면의 맥락. 생성 시 step-01 기준 seed 작성}

## 경과 (시간순 서사)

{steps·comms를 시간순으로 엮은 내러티브. 각 국면을 "무엇이 있었고 → 무엇을 확인했고 → 어디로 갔는지" 로 잇는다. 생성 시엔 placeholder}

- {today} — 이슈 생성, 대응 착수 전

## 현재 상태

{지금 어디까지 왔고 다음은 무엇인지. 진행 중이면 열린 스레드·다음 방향 명시. 생성 시엔 "이슈 생성 단계"}

## 관련 메모

- [[ISS-{NNN} {title}]]
- [[ISS-{NNN} WBS]]
```

> **생성 시엔 `## 배경`만 step-01 기준으로 seed**하고, `## 경과`·`## 현재 상태`는 placeholder로 둔다. 히스토리 축적은 아래 절차가 담당한다.

## steps: `steps/step-{NN}-{slug}.md`

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

## comms: `comms/YYYY-MM-DD-{slug}.md`

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
