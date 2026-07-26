---
name: retro
description: >
  주간 회고 작성 자동화 (주말, 월~금 사이클) — 이번주 작업 수집 + KPI·오픈 이슈 검토 → 초안 확인 → Issue → PR 자동화.
  Do NOT use for 목~수 주간보고 → sr-obsidian:weekly.
  Do NOT use for 당일 데일리 노트 → sr-obsidian:daily.
  Keywords: 주간 회고, retro, 회고, 이번주 회고, 주말 회고, 월~금 정리, KPI 검토, 이슈 검토
allowed-tools: Bash, Read, Glob, Write, Edit
---

# 주간 회고 생성 워크플로우

> **CLI 전제**: `obsidian version`으로 앱 연결 확인 후 진행. 상세 명령은 `obsidian-cli` 스킬 참조.

## 사용법

```
/retro             # 오늘 기준 이번주(월~금) 회고
/retro 2026-W15    # 특정 ISO 주차 지정
```

`/retro`는 주말에 월~금 검토·성찰 목적, `/weekly`는 목~수 업무 보고 목적.

## Phase 1: scan (READ-ONLY — 파일 수정 없음)

1. **주차 계산** — 이번주 월요일 기준 ISO 주차(`YYYY-WNN`)와 월~금 날짜 5개 산출
2. **데일리 파일 확인** — `obsidian files folder="60-logs/daily/YYYY/MM"`에서 해당 주 날짜 파일만 필터 (없는 날은 건너뜀)
3. **작업 수집** — 날짜별로 반복 (`tasks`는 `file=날짜` 단위만 가능):
   ```bash
   obsidian tasks file="$DATE" done verbose format=json
   obsidian tasks file="$DATE" todo verbose format=json
   ```
   `## 미완 작업` 섹션 항목도 todo로 수집됨. JSON `file` 필드로 날짜 역추적.
4. **KPI 수집** — `obsidian read file="YYYY-kpi"` → 과제·가중치·목표 파악, 이번주 완료 작업을 과제별 매핑 (ISS·FT·dqr 키워드)
5. **이월 분석** — 가장 최근 회고(없으면 weekly)의 `## 다음주 이월`과 이번주 미완료 대조.
   유사 항목을 그룹으로 묶어 **원인-해결** 구조로 분석. **3회 이상 이월 → "재검토 필요" 플래그.**

초안을 [format.md](references/format.md)의 **초안 출력 형식**으로 표시하고 종료:
> 수정할 내용이 있으면 알려주세요. 확인되면 "저장" 입력 시 회고 파일을 작성합니다.

## Phase 2: write (사용자 "저장" 확인 후)

1. **중복 확인** — `60-logs/retro/{YYYY-WNN} 주간회고.md` 존재 시 경고 후 덮어쓸지 확인
2. **Issue + Branch** — [git-workflow](../../references/git-workflow.md) 표준 절차:
   제목 `docs: {YYYY-WNN} 주간 회고 작성`, 브랜치 `feature/{N}-retro-{YYYY-WNN}`
3. **파일 생성** — [format.md](references/format.md)의 **파일 형식** 기준:
   ```bash
   obsidian create path="60-logs/retro/{YYYY-WNN} 주간회고.md" template="tpl-retro" overwrite
   obsidian property:set name="week" value="{YYYY-WNN}" path="60-logs/retro/{YYYY-WNN} 주간회고.md"
   ```
   템플릿 없으면 Write로 직접 작성
4. **커밋 & PR** — git-workflow 커밋·PR 단계, 커밋 `docs: {YYYY-WNN} 주간 회고 작성 (#{N})`
5. **완료 출력** — Issue·Branch·PR·파일 경로

## 판단 기준

| 상황 | 처리 |
|------|------|
| KPI 파일 없음 | KPI 섹션 생략, 나머지 진행 |
| 완료 0개 / 미완료 0개 | 완료율 0%(이월만 정리) / 100%(인사이트만 작성) |
| 미완료 분석 수정 요청 | 해당 그룹만 반영 후 재출력 |

## Wiki Harvest (자동 트리거)

Phase 2 완료 후 자동 실행 — [wiki-harvest](../../references/wiki-harvest.md) 공통 절차, 스캔 범위 = **해당 주 월~금**.
종료 후 메타 진화 루프로 진행.

## 메타 진화 루프

Phase 2 완료 후 자동 실행: `.claude/evolution/evolution_log.jsonl`에 `sr-obsidian:daily` 이벤트가 누적돼 있으면
`/meta sr-obsidian:daily` 를 호출해 주 1회 진화 루프를 돌린다. 로그가 없으면 건너뜀.
