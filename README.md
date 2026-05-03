# sr-obsidian

Obsidian 프로젝트 문서 관리 Claude Code 플러그인.

PSP 프로젝트에서 검증된 문서 관리 패턴(허브·WBS·docs 구조·diagrams·히스토리)을
재사용 가능한 스킬로 추상화하여 vault 내 모든 프로젝트에 일관되게 적용한다.

## 스킬 목록

| 스킬 | 호출 | 용도 |
|------|------|------|
| init | `sr-obsidian:init` | 새 프로젝트 폴더 구조 + 허브 + WBS 생성 |
| hub | `sr-obsidian:hub` | 허브 노트 링크·KPI·상태 관리 |
| wbs | `sr-obsidian:wbs` | WBS Phase 구성·진행 현황 관리 |
| history | `sr-obsidian:history` | ADR·의사결정 로그·회의록 기록 |
| audit | `sr-obsidian:audit` | 프로젝트 구조 검증 |
| migrate | `sr-obsidian:migrate` | 비표준 구조 → 표준 이관 |

## 표준 폴더 구조

```
{project}/
├── {project-id} 프로젝트 현황.md    ← 허브 (sr-obsidian:hub)
├── {project-id} WBS.md              ← WBS (sr-obsidian:wbs)
│
├── docs/
│   ├── specs/        ← 설계 문서 (컴포넌트 역할, 인터페이스, 요구사항)
│   ├── architecture/ ← 아키텍처 분석, 전문가 리뷰, 제약 분석
│   ├── adr/          ← Architecture Decision Records (sr-obsidian:history)
│   ├── reports/      ← 보고서 소스 MD
│   ├── runbook/      ← 운영 절차 (Phase 5+)
│   └── config/       ← 인프라·환경 설정 기록
│
├── diagrams/         ← HTML 전용 (인터랙티브 시각화)
├── features/         ← FT-xxx 기능 개발 폴더
├── phases/           ← Phase step 파일
└── meetings/         ← 회의록 (sr-obsidian:history)
```

## 설치

```bash
# GitHub 레포 등록 후
claude plugins marketplace add SeokRae/sr-obsidian
claude plugins install sr-obsidian
```

## Reference Implementation

PSP 프로젝트 (`20-areas/payment/psp/`) 가 이 플러그인의 reference implementation.
