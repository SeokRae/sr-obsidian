---
name: weekly
description: >
  주간보고 작성 자동화 (목~수 사이클) — 해당 주 데일리 노트 수집·분석 → 초안 확인 → Issue → PR 자동화.
  Do NOT use for 주말 KPI·회고 → sr-obsidian:retro.
  Do NOT use for 당일 데일리 노트 → sr-obsidian:daily.
  Keywords: 주간보고, weekly, 주간 리포트, 이번주 정리, 미완료 분석
allowed-tools: Bash, Read, Glob, Write, Edit
---

# 주간보고 생성 워크플로우

## 사용법

```
/weekly            # 오늘 날짜 기준 이번주 자동 분석
/weekly 2026-W15   # 특정 주차 지정 (ISO YYYY-WNN)
```

## Phase 1: scan (READ-ONLY — 파일 수정 없음)

1. **주차 계산** — `$ARGUMENTS` 있으면 해당 주차, 없으면 목~수 사이클 계산.
   **주차 레이블은 종료 수요일 기준 ISO 주차** (기존 파일 관행과 일치):

   ```bash
   python3 -c "
   from datetime import date, timedelta
   today = date.today()
   offset = (today.weekday() - 3) % 7      # 목=0 … 수=6
   thu = today - timedelta(days=offset)
   wed = thu + timedelta(days=6)
   iso = wed.isocalendar()
   print(f'{iso[0]}-W{iso[1]:02d}')
   for i in range(7):
       d = thu + timedelta(days=i)
       if d.weekday() < 5: print(d.strftime('%Y-%m-%d'))
   "
   ```

2. **데일리 수집** — 각 날짜의 `60-logs/daily/YYYY/MM/YYYY-MM-DD.md` 중 존재하는 파일만 Read,
   `## 작업 로그` 섹션에서 `- [x]` 완료 / `- [ ]` 미완료 파싱

3. **이월 분석 + 분류** — 직전 주간보고의 `## 다음주 계획`과 대조해 이월 횟수 표시.
   미완료 분류 자동 제안: `blocked`(외부 의존) / `deferred`(의도적 후순위) / `underestimated`(예상보다 큰 작업) / `distracted`(인터럽트).
   **3회 이상 이월 → "재검토 필요" 플래그.**

4. **프로젝트별 그루핑** — **ISS는 step 기준**: `10-projects/ISS-NNN-*/steps/step-*.md` frontmatter(title·status·날짜)를
   읽어 step 순서대로 나열하고 이번 주 완료·진행 항목을 데일리 로그와 매핑. 비-ISS(FT·QA·dqr)는 flat 묶음.
   상태 표기: ✅ done / 🚧 in-progress / ⏸ ready

   **step 계층 규칙**: step 내에 이번 주 추적할 하위 작업이 있을 때만 계층 표기, 없으면 step 한 줄.

초안을 [format.md](references/format.md)의 **초안 출력 형식**으로 표시하고 종료:
> 수정할 내용이 있으면 알려주세요. (분류 수정: "1번 blocked→deferred") 확인되면 "저장" 입력 시 작성합니다.

## Phase 2: write (사용자 "저장" 확인 후)

1. **중복 확인** — `60-logs/weekly/{YYYY-WNN} 주간보고.md` 존재 시 경고 후 덮어쓸지 확인
2. **Issue + Branch** — [git-workflow](../../references/git-workflow.md) 표준 절차:
   제목 `docs: {YYYY-WNN} 주간보고 작성`, 브랜치 `feature/{N}-weekly-{YYYY-WNN}`
3. **파일 작성** — [format.md](references/format.md)의 **파일 형식** 기준, `weekly-planner` 에이전트에 위임:
   `Agent(weekly-planner, {week, goal})` → 생성 파일 Read 후 Phase 1 데이터·사용자 수정사항 보완.
   **에이전트 오류·파일 미생성 시 fallback**: Phase 1 데이터를 직접 Write.
4. **커밋 & PR** — git-workflow 커밋·PR 단계, 커밋 `docs: {YYYY-WNN} 주간보고 작성 (#{N})`
5. **완료 출력** — Issue·Branch·PR·파일 경로 + 처리 건수(agent/수동)

## 판단 기준

| 상황 | 처리 |
|------|------|
| 미완료 분류 수정 | `"1번 blocked→deferred"` 형식 입력 반영 후 재출력 |
| ISS step 파일 없음 | 데일리 로그 기반 flat 형식으로 대체 |
| ISS 이름과 실제 작업 범위 불일치 | 실제 작업 기준 기재, 괄호로 원래 트리거 병기 |
| 완료 0개 / 미완료 0개 | 완료율 0%(이월만 정리) / 100%(인사이트만 작성) |

## Wiki Harvest (자동 트리거)

Phase 2 완료 후 자동 실행 — [wiki-harvest](../../references/wiki-harvest.md) 공통 절차, 스캔 범위 = **해당 주 목~수**.
종료 후 메타 진화 루프로 진행.

## 메타 진화 루프

Phase 2 완료 후 자동 실행: `.claude/evolution/evolution_log.jsonl`에 `sr-obsidian:daily` 이벤트가 누적돼 있으면
`/meta sr-obsidian:daily` 를 호출한다. 로그가 없으면 건너뜀.
