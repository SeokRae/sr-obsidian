---
name: weekly
description: >
  주간보고 작성 자동화 (목~수 사이클). 해당 주 데일리 노트를 수집·분석해 초안을 보여주고, 확인 후 Issue → Branch → Write → Commit → PR 전 과정 자동화.
  Do NOT use for weekend KPI/retrospective (use sr-obsidian:retro — retro covers Mon-Fri reflection).
  Keywords: 주간보고, weekly, 주간 리포트, 이번주 정리, 미완료 분석.
allowed-tools: Bash, Read, Glob, Write, Edit
---

# 주간보고 생성 워크플로우

## 사용법

```
/weekly            # 오늘 날짜 기준 이번주 자동 분석
/weekly 2026-W15   # 특정 주차 지정 (ISO YYYY-WNN)
```

## 2-Phase 워크플로우

### Phase 1: scan (READ-ONLY)

해당 주 데일리 노트를 수집·분석한다. **파일 수정 없음.**

**수행 순서**:

1. 주차 계산
   - `$ARGUMENTS`가 있으면 해당 ISO 주차 사용 (예: `2026-W15`)
   - 없으면 오늘 날짜 기준 주차 계산 (목~수 사이클):
     ```bash
     python3 -c "
     from datetime import date, timedelta
     today = date.today()
     # 목~수 사이클: 목(3)=0, 금(4)=1, 토(5)=2, 일(6)=3, 월(0)=4, 화(1)=5, 수(2)=6
     offset = (today.weekday() - 3) % 7
     thu = today - timedelta(days=offset)
     wed = thu + timedelta(days=6)
     # 주차 레이블은 종료 수요일(작성일) 기준 ISO 주차 사용 — 기존 파일 관행과 일치
     iso = wed.isocalendar()
     week = f'{iso[0]}-W{iso[1]:02d}'
     print(week)
     for i in range(7):
         d = thu + timedelta(days=i)
         if d.weekday() < 5:   # 평일만 (월~금)
             print(d.strftime('%Y-%m-%d'))
     "
     ```
   - 해당 사이클의 평일(목·금·월·화·수) 날짜 목록 생성

2. 데일리 노트 수집
   - 각 날짜 `60-logs/daily/YYYY/MM/YYYY-MM-DD.md` 존재 확인
   - 존재하는 파일만 Read

3. 작업 로그 파싱 — 각 파일의 `## 작업 로그` 섹션에서:
   - `- [x]` : 완료 항목 (PR 번호, 링크 포함)
   - `- [ ]` : 미완료 항목

4. 미완료 항목 이월 분석 + 분류
   - 직전 주간보고 파일(`60-logs/weekly/`) Glob → 가장 최근 파일 Read → `## 다음주 계획` 항목과 대조
   - 이전 주에도 미완료였던 항목 → 이월 횟수 표시
   - 미완료 항목별 분류 자동 제안:
     - `blocked` — 외부 의존성·대기 (답변 대기, 인프라, 승인)
     - `deferred` — 더 급한 일로 의도적 후순위 처리
     - `underestimated` — 예상보다 큰 작업으로 시간 부족
     - `distracted` — 예상외 인터럽트로 밀림
   - 동일 항목 3회 이상 이월 → "재검토 필요" 플래그 추가

5. 프로젝트별 그루핑

   **ISS 인시던트 항목** — step 파일을 읽어 step 기준으로 구성:
   - `10-projects/ISS-NNN-*/steps/step-*.md` Glob 후 각 파일의 frontmatter 확인
     - `title`, `status`(`done`/`in-progress`/`ready`), `start-date`, `end-date`
   - step 순서대로 나열, 각 step의 이번 주 완료·진행 항목을 데일리 로그와 매핑

   **비-ISS 항목** (FT-NNN, QA-NNN, dqr-*, 기타):
   - 데일리 로그 기준 완료/진행 항목 묶기

   상태 표기: ✅ done / 🚧 in-progress / ⏸ ready

**출력 형식**:

---

### 📋 YYYY-WNN 주간보고 초안 (M/D(요일) ~ M/D(요일))

**이번주 완료율**: {완료수}/{전체수} ({완료율}%)

**이번주 요약 (초안)**:
> {프로젝트별 핵심 완료·진행 내용 한 줄 나열 — 사용자 수정 가능}

---

**보고용 요약 초안**

```
N. **ISS-NNN {이슈명}**
   - step-01. ✅ {step 제목}                    ← 완료, 하위 없음
   - step-02. 🚧 {step 제목}                    ← 진행 중, 하위 작업 있음
     - ✅ {완료 항목} → PR #{번호}
     - [ ] {잔여 항목}
   - step-03. ⏸ {step 제목}                    ← 미착수, 하위 없음

N. **{비-ISS 프로젝트명}**
   - N-1. ✅ {완료 항목} → PR #{번호}
   - N-2. 🚧 {진행 중 항목}
```

**보고용 요약 step 계층 규칙**:
- ISS 항목은 반드시 step 기준으로 나열
- step 내에 이번 주 추적할 하위 작업(완료 PR, 진행 중 항목)이 있을 때만 계층 표기
- step이 설명만으로 충분하면(완료 또는 미착수이고 이번 주 진행 없음) step 한 줄
- FT, QA, dqr 등 step 구조가 없는 항목은 기존 flat 형식(N-1, N-2) 유지

---

**📊 날짜별 브레이크다운**

| 날짜 | 완료 | 미완료 | 대표 작업 |
|------|------|--------|---------|
| M/D(목) | N | N | {대표 작업 한 줄} |
| M/D(금) | N | N | {대표 작업 한 줄} |
| M/D(월) | N | N | {대표 작업 한 줄} |
| M/D(화) | N | N | {대표 작업 한 줄} |
| M/D(수) | N | N | {대표 작업 한 줄} |

---

**⬜ 미완료 분류** ({N}개)

| # | 항목 | 날짜 | 이월 | 분류 | 근거 |
|---|------|------|------|------|------|
| 1 | {항목} | M/D | N회차 | blocked | {한 줄 근거} |
| 2 | {항목} | M/D | 신규 | deferred | {한 줄 근거} |

> 분류 수정: `"1번 blocked→deferred"` 형식으로 알려주세요.

---

**다음주 계획 초안**

### {카테고리}
- [ ] {미완료 항목 — 이월 횟수 표시}

---

수정할 내용이 있으면 알려주세요.
확인이 되면 `"저장"` 입력 시 주간보고를 작성합니다.

---

### Phase 2: write (WRITE)

사용자가 "저장" 또는 내용 수정 확인 후 실행한다.

**수행 순서**:

1. 파일 중복 확인
   - `60-logs/weekly/{YYYY-WNN} 주간보고.md` 존재 여부 확인
   - **존재하면**: "이미 존재합니다" 경고 후 덮어쓸지 확인

2. GitHub Issue 생성
   ```bash
   gh issue create \
     --repo SeokRae/knowledge-labs \
     --title "docs: {YYYY-WNN} 주간보고 작성" \
     --body "## Summary\n- {YYYY-WNN} ({시작일}~{종료일}) 주간보고 작성\n- 파일: \`60-logs/weekly/{YYYY-WNN} 주간보고.md\`"
   ```

3. Feature 브랜치 생성 (main 기준)
   ```bash
   git checkout main
   git checkout -b feature/{ISSUE_NUMBER}-weekly-{YYYY-WNN}
   ```

4. 주간보고 파일 작성 — **weekly-planner 에이전트 위임**
   - `weekly-planner` 에이전트를 호출해 초안을 생성한다:
     ```
     Agent(weekly-planner, {week: "{YYYY-WNN}", goal: "{Phase 1 요약 한 줄}"})
     ```
   - 에이전트가 `60-logs/weekly/{YYYY-WNN} 주간보고.md` 파일을 생성하고 종료
   - 생성된 파일을 Read로 확인 → Phase 1 수집 데이터·사용자 수정사항 미반영 부분 보완

   > **에이전트 처리 불가 시 fallback**: 에이전트 오류 또는 파일 미생성 시
   > Phase 1 데이터를 직접 Write로 기록한다.

5. 커밋 & PR 생성
   ```bash
   git add "60-logs/weekly/{YYYY-WNN} 주간보고.md"
   git commit -m "docs: {YYYY-WNN} 주간보고 작성 (#{ISSUE_NUMBER})"
   git push -u origin feature/{ISSUE_NUMBER}-weekly-{YYYY-WNN}

   gh pr create \
     --repo SeokRae/knowledge-labs \
     --title "docs: {YYYY-WNN} 주간보고 작성" \
     --body "Closes #{ISSUE_NUMBER}"
   ```

6. 완료 출력
   ```
   ✅ {YYYY-WNN} 주간보고 작성 완료

   Issue : SeokRae/knowledge-labs#{ISSUE_NUMBER}
   Branch: feature/{ISSUE_NUMBER}-weekly-{YYYY-WNN}
   PR    : SeokRae/knowledge-labs#{PR_NUMBER}
   파일  : 60-logs/weekly/{YYYY-WNN} 주간보고.md
   처리  : agent ({에이전트 처리 항목 수}건) / 수동 ({수동 보완 항목 수}건)
   ```

## 주간보고 파일 형식

```markdown
---
type: weekly
created: {TODAY}
tags: [weekly]
week: {YYYY-WNN}
description: 주간보고 — 프로젝트별 진행 현황, 이번주 완료, 다음주 계획
---

# {YYYY-WNN} 주간보고 ({시작 M/D}~{종료 M/D})

← [[주간보고 MOC]]

## 이번주 요약

> {핵심 내용 한 줄 요약}

## 보고용 요약

1. **ISS-NNN {이슈명}**
   - step-01. ✅ {step 제목}
   - step-02. 🚧 {step 제목}
     - ✅ {완료 항목} → PR #{번호}
     - [ ] {잔여 항목}
   - step-03. ⏸ {step 제목}

2. **{비-ISS 프로젝트명}**
   - 2-1. ✅ {완료 항목} → PR #{번호}
   - 2-2. 🚧 {진행 중}

---

## 다음주 계획

### {카테고리} ({우선순위})

- [ ] {항목}

## 블로커

| 항목 | 원인 | 해결 방안 |
|------|------|---------|
| | | |

---

## 회고 ({TODAY} 작성)

### 완료율
{N}/{전체} ({%}%)

### 미완료 분석

| 항목 | 이월 | 분류 | 다음 액션 |
|------|------|------|---------|
| {항목} | N회차 | blocked | {액션} |

### 이번주 인사이트

-

### 다음주 이월

- [ ] {항목}
```

## 판단 기준

| 상황 | 처리 |
|------|------|
| 데일리 노트가 없는 날 | 건너뜀 (공휴일·부재) |
| 작업 로그가 비어있는 날 | 빈 날로 표시 |
| 주간보고 파일 이미 존재 | 경고 후 사용자 확인 — 덮어쓰거나 중단 |
| 완료 항목 0개 | 완료율 0% 출력, 이월 항목만 정리 |
| 동일 항목 3회 이상 이월 | "재검토 필요" 플래그 추가 |
| 미완료 0개 | 완료율 100% 출력 후 인사이트 섹션만 작성 |
| 미완료 분류 수정 | `"1번 blocked→deferred"` 형식으로 입력받아 반영 후 재출력 |
| ISS step 파일 없음 | 데일리 로그 기반 flat 형식으로 대체 |
| step 내 이번 주 진행 없음 | step 한 줄만 표기 (하위 생략) |
| ISS 이름과 실제 작업 범위 불일치 | 실제 작업 내용 기준으로 기재, 괄호로 원래 트리거 병기 |

## 메타 진화 루프

Phase 2 완료 출력 후 자동으로 실행한다.

1. evolution_log 현황 확인

   ```bash
   python3 -c "
   import json
   from pathlib import Path
   log = Path('/Users/sr/obsidian/sr-labs/.claude/evolution/evolution_log.jsonl')
   if log.exists():
       entries = [json.loads(l) for l in log.read_text().splitlines() if l.strip()]
       daily = [e for e in entries if e.get('skill') == 'sr-obsidian:daily']
       print(f'sr-obsidian:daily 누적: {len(daily)}개')
   else:
       print('evolution_log 없음 — 건너뜀')
   "
   ```

2. sr-obsidian:daily 진화 루프 실행

   ```
   /meta sr-obsidian:daily
   ```
