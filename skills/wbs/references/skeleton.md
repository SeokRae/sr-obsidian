# /wbs skeleton — WBS 골격 생성

## 처리 순서

1. init 결과(유형, 프로젝트명, 도메인 목록, 세부 분리 Phase, 외부 어댑터)로 골격 생성
2. `Glob`으로 대상 경로 확인
3. **Write** `wbs.md` — 프론트매터 + 개요 테이블 + DataviewJS 간트차트 + Phase 링크 테이블
4. **Write** `phases/phase-N.md` × 8 — 각 Phase 골격
5. 세부 분리 Phase가 있으면 추가:
   - **Write** `phases/phase-{idx}.md` — step 목록 대시보드
   - **Write** `phases/phase-{idx}-{content}/step-NN-{desc}.md` × N

## wbs.md 프론트매터

```yaml
---
type: wbs
project: {프로젝트명}
project-type: {유형}
wbs-status: skeleton
created: {YYYY-MM-DD}
start-date: {시작일}
end-date: {종료일}
team: {팀 구성 요약}
domains: [{도메인1}, {도메인2}]
tags: [wbs, {유형}]
---
```

## DataviewJS 간트차트 (Architecture A)

```dataviewjs
await dv.view("_scripts/gantt/gantt-a", {
  rows: [
    { id: "1", label: "1. 프로젝트 준비", start: "YYYY-MM-DD", effort: N, group: "prep", type: "phase", link: "phase-1", phaseFile: "10-projects/{서비스}/phases/phase-1.md" },
    // phase-summary + task 그룹은 반드시 전용 그룹으로 분리 (prep 혼재 금지)
    // 세부 분리 시 phaseFiles: [...] 배열 사용
  ],
  groupColor: {
    prep: "var(--color-cyan)", dev: "var(--color-blue)", test: "var(--color-yellow)",
    deploy: "var(--color-green)", stable: "var(--color-green)", mgmt: "var(--text-faint)",
  },
  colorLegend: [
    { color: "var(--color-cyan)", label: "준비·분석·설계" },
    { color: "var(--color-blue)", label: "개발" },
    { color: "var(--color-yellow)", label: "테스트" },
    { color: "var(--color-green)", label: "배포·안정화" },
    { color: "var(--text-faint)", label: "프로젝트 관리" },
  ],
});
```

**외부 어댑터 2개 이상** → `dev` 대신 `dev-{약칭}` 복수 group.  
**세부 분리 Phase** → `phase-summary` + 전용 그룹, `phaseFiles: [...]` 배열.  
상세 스키마: `[[gantt-design-tokens]]` 참조.

## 유형별 8단계 Phase 구성

| Phase | api-backend | web-fullstack 추가 | mobile-app 추가 | batch-data 추가 |
|-------|------------|-------------------|----------------|----------------|
| 1. 준비 | 계획 / 환경 세팅 | — | — | — |
| 2. 요구사항 | 비즈니스 / 비기능 | — | — | — |
| 3. 설계 | 아키텍처 / DB / API | + UI/UX | + 화면 | + 배치 잡 |
| 4. 개발 | 환경 / 도메인 / DB / 외부연동 | + QA 테스트 페이지 | — | + 스케줄링 |
| 5. 테스트 | 단위 / 통합 / 성능 / UAT | — | + 디바이스 | — |
| 6. 배포 | 준비 / 수행 | — | — | — |
| 7. 안정화 | 모니터링 / 인수인계 | — | — | — |
| 8. 관리 | 주간보고 / 리스크 | — | — | — |

## 세부 분리 Phase 전용 그룹

| Phase | 그룹명 | 색상 |
|-------|-------|------|
| 1 | `setup` | `var(--color-cyan)` |
| 2 | `req` | `var(--color-cyan)` |
| 3 | `design` | `var(--color-cyan)` |
| 4 | `dev` | `var(--color-blue)` |
| 5 | `test-detail` | `var(--color-yellow)` |
| 6 | `deploy-detail` | `var(--color-green)` |
| 인프라 | `infra` | `var(--color-orange)` |

> Phase 1·2·3은 기본 `prep` 그룹. 두 개 이상 분리 시 각각 전용 그룹 필수.
