---
name: retro
description: 주간 회고 작성 자동화. 주말에 실행 — obsidian-cli로 이번주 월~금 작업 수집 + KPI·오픈 이슈 진행 상태 검토 → 초안 확인 → Issue → Branch → Write → Commit → PR 자동화. Keywords: 주간 회고, retro, 회고, 이번주 회고, 주말 회고, 월~금 정리, KPI 검토, 이슈 검토, weekly retro.
allowed-tools: Bash, Read, Glob, Write, Edit
---

# 주간 회고 생성 워크플로우

> **CLI 전제**: `obsidian version` 으로 앱 연결 확인 후 진행.
> CLI 상세 명령은 `obsidian-cli` 스킬 참조.

## 사용법

```
/retro             # 오늘 날짜 기준 이번주(월~금) 회고
/retro 2026-W15    # 특정 ISO 주차 지정
```

> **주간 회고 vs 주간보고**
> - `/retro`: 주말에 **월~금** — KPI·오픈 이슈 진행 상태 검토 + 성찰 목적
> - `/weekly`: **목~수** 사이클 — 업무 보고 목적

## 2-Phase 워크플로우

### Phase 1: scan (READ-ONLY)

**파일 수정 없음.**

**수행 순서**:

1. **연결 확인 + 주차 계산**
   ```bash
   obsidian version   # 앱 연결 확인
   python3 -c "
   from datetime import date, timedelta
   today = date.today()
   mon = today - timedelta(days=today.weekday())
   iso = mon.isocalendar()
   week = f'{iso[0]}-W{iso[1]:02d}'
   print(week)
   for i in range(5):
       d = mon + timedelta(days=i)
       print(d.strftime('%Y-%m-%d'))
   "
   ```

2. **데일리 파일 존재 확인**
   ```bash
   obsidian files folder="60-logs/daily/YYYY/MM"
   # 출력된 목록에서 해당 주 날짜(YYYY-MM-DD) 파일만 필터
   ```

3. **작업 수집 — obsidian tasks 사용**
   ```bash
   # 날짜별 완료/미완료 작업 JSON 수집
   for DATE in YYYY-MM-DD ...; do
     obsidian tasks file="$DATE" done verbose format=json
     obsidian tasks file="$DATE" todo verbose format=json
   done
   ```
   - JSON `file` 필드로 날짜 역추적 가능
   - 데일리 노트가 없는 날짜는 건너뜀
   - `## 미완 작업` 섹션 항목도 todo로 수집됨

4. **KPI 진행 현황 수집**
   ```bash
   obsidian read file="YYYY-kpi"
   # 과제명, 가중치, 목표건수, 기간, 현재 적용건수 파악
   # 이번주 완료 작업 → KPI 과제별 매핑 (ISS·FT·dqr 키워드 기준)
   ```

5. **이월 분석 + 분류**
   ```bash
   obsidian files folder="60-logs/retro"
   obsidian read file="<가장 최근 회고>"   # 없으면 weekly 참조
   ```
   - `## 다음주 이월` 항목과 이번주 미완료 대조
   - 유사 항목을 그룹으로 묶고 그룹별 **원인-해결** 구조로 분석
   - 3회 이상 이월 → "재검토 필요" 플래그

**출력 형식**:

---

### 📋 YYYY-WNN 주간 회고 초안 (M/D(월) ~ M/D(금))

**이번주 완료율**: {완료수}/{전체수} ({완료율}%)

**이번주 요약 (초안)**:
> {핵심 내용 한 줄}

---

**📊 KPI 진행 현황**

| # | 과제명 | 가중치 | 적용/목표 | 경과일/목표일 | 이번주 기여 | 상태 |
|---|--------|--------|----------|------------|-----------|------|
| 1 | {과제명} | 35% | N/7 | N/183일 | {완료 항목 또는 —} | 🚧/⏸/✅ |
| 2 | {과제명} | 30% | N/3 | N/183일 | {완료 항목 또는 —} | |
| 3 | {과제명} | 20% | N/2+TBD | N/214일 | {완료 항목 또는 —} | |
| 4 | {과제명} | 15% | N/3 | N/183일 | {완료 항목 또는 —} | |

---

**🗂 오픈 이슈 현황**

| 이슈 | 우선순위 | 이번주 진행 | 블로커 | 이월 |
|------|--------|-----------|--------|------|
| ISS-NNN {제목} | 🔴 최우선 | {진행 내용 또는 없음} | {블로커 또는 —} | N회차 |

---

**📝 이번주 완료**

{N}. **{프로젝트명}**
   - N-1. ✅ {완료 항목} → PR #{번호}

---

**📊 날짜별 브레이크다운**

| 날짜 | 완료 | 미완료 | 대표 작업 |
|------|------|--------|---------|
| M/D(월) | N | N | {한 줄} |
| ... | | | |

---

**⬜ 미완료 분석** ({N}개)

> 항목별 원인-해결 구조로 작성. 유사 항목은 그룹으로 묶는다.

### {그룹 제목} ({관련 이슈/항목})

- **원인**: {왜 부족했는지 — 의존성, 우선순위, 컨텍스트 등}
- **해결**: {구체적 액션 플랜 — 누가, 언제, 무엇을}

### {그룹 제목} ({관련 이슈/항목})

- **원인**: ...
- **해결**: ...

**완료율**: {완료수}/{전체수} ({완료율}%)

---

**다음주 이월 초안**

- [ ] {미완료 항목 — 이월 횟수}

---

수정할 내용이 있으면 알려주세요.
확인이 되면 `"저장"` 입력 시 회고 파일을 작성합니다.

---

### Phase 2: write (WRITE)

사용자가 "저장" 또는 내용 수정 확인 후 실행한다.

**수행 순서**:

1. **파일 중복 확인**
   ```bash
   obsidian files folder="60-logs/retro"
   # YYYY-WNN 주간회고.md 존재 여부 확인
   # 존재하면: 경고 후 덮어쓸지 확인 (overwrite 플래그)
   ```

2. **GitHub Issue 생성**
   ```bash
   gh issue create \
     --repo SeokRae/knowledge-labs \
     --title "docs: {YYYY-WNN} 주간 회고 작성" \
     --body "## Summary\n- {YYYY-WNN} ({시작일}~{종료일}) 주간 회고 작성\n- 파일: \`60-logs/retro/{YYYY-WNN} 주간회고.md\`"
   ```

3. **Feature 브랜치 생성**
   ```bash
   git checkout main
   git checkout -b feature/{ISSUE_NUMBER}-retro-{YYYY-WNN}
   ```

4. **회고 파일 생성**
   ```bash
   # 템플릿으로 파일 골격 생성
   obsidian create \
     path="60-logs/retro/{YYYY-WNN} 주간회고.md" \
     template="tpl-retro" \
     overwrite

   # frontmatter 보완
   obsidian property:set name="week" value="{YYYY-WNN}" \
     path="60-logs/retro/{YYYY-WNN} 주간회고.md"
   ```
   - 템플릿 없는 경우: Write 툴로 전체 내용 직접 작성

5. **커밋 & PR**
   ```bash
   git add "60-logs/retro/{YYYY-WNN} 주간회고.md"
   git commit -m "docs: {YYYY-WNN} 주간 회고 작성 (#{ISSUE_NUMBER})"
   git push -u origin feature/{ISSUE_NUMBER}-retro-{YYYY-WNN}
   gh pr create \
     --repo SeokRae/knowledge-labs \
     --title "docs: {YYYY-WNN} 주간 회고 작성" \
     --body "Closes #{ISSUE_NUMBER}"
   ```

6. **완료 출력**
   ```
   ✅ {YYYY-WNN} 주간 회고 작성 완료

   Issue : SeokRae/knowledge-labs#{ISSUE_NUMBER}
   Branch: feature/{ISSUE_NUMBER}-retro-{YYYY-WNN}
   PR    : SeokRae/knowledge-labs#{PR_NUMBER}
   파일  : 60-logs/retro/{YYYY-WNN} 주간회고.md
   ```

## 회고 파일 형식

```markdown
---
type: retro
created: {TODAY}
tags: [retro, weekly]
week: {YYYY-WNN}
description: 주간 회고 — KPI·이슈 진행 상태 검토, 이번주 완료·미완료 분석, 다음주 이월
---

# {YYYY-WNN} 주간 회고 ({시작 M/D(월)}~{종료 M/D(금)})

← [[주간보고 MOC]]

## 이번주 요약

> {핵심 내용 한 줄}

---

## KPI 진행 현황

> 기준: [[60-logs/kpi/{YYYY}-kpi]]

| # | 과제명 | 가중치 | 적용/목표 | 경과일/목표일 | 이번주 기여 | 상태 |
|---|--------|--------|----------|------------|-----------|------|
| 1 | {과제명} | 35% | N/7 | N/183일 | {완료 항목 또는 —} | 🚧 |
| 2 | {과제명} | 30% | N/3 | N/183일 | — | ⏸ |
| 3 | {과제명} | 20% | N/2+TBD | N/214일 | {완료 항목 또는 —} | 🚧 |
| 4 | {과제명} | 15% | N/3 | N/183일 | — | ⏸ |

---

## 오픈 이슈 현황

| 이슈 | 우선순위 | 이번주 진행 | 블로커 | 이월 |
|------|--------|-----------|--------|------|
| ISS-NNN {제목} | 🔴 | {진행 내용} | {블로커 또는 —} | N회차 |

---

## 이번주 완료

1. **{프로젝트명}**
   - 1-1. ✅ {완료 항목} → PR #{번호}

---

## 미완료 분석

### 완료율

{N}/{전체} ({%}%)

### {그룹 제목} ({관련 이슈/항목})

- **원인**: {왜 부족했는지}
- **해결**: {구체적 액션 플랜}

---

## 다음주 이월

- [ ] {항목 — N회 이월}
```

## 판단 기준

| 상황 | 처리 |
|------|------|
| Obsidian 앱 미실행 | `obsidian version` 오류 → 앱 실행 후 재시도 안내 |
| 데일리 노트 없는 날 | `obsidian files` 목록에 없으면 건너뜀 |
| KPI 파일 없음 | KPI 섹션 생략, 나머지 진행 |
| 회고 파일 이미 존재 | 경고 후 확인 — `overwrite` 사용 또는 중단 |
| 완료 항목 0개 | 완료율 0%, 이월 항목만 정리 |
| 동일 항목 3회 이상 이월 | "재검토 필요" 플래그 |
| 미완료 0개 | 완료율 100%, 인사이트 섹션만 작성 |
| 미완료 분석 수정 | 사용자가 원인·해결 내용 수정 요청 시 해당 그룹만 반영 후 재출력 |
