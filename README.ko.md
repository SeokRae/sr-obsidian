# sr-obsidian

> Obsidian 프로젝트 문서 관리를 위한 Claude Code 플러그인 — 허브·WBS·히스토리·폴더 구조를 일관된 패턴으로 관리합니다.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Plugin-blueviolet)](https://claude.ai/code)
[![Status](https://img.shields.io/badge/Status-Early%20Stage-orange)](.)

> [English](./README.md) | 한국어

---

## 배경

Obsidian에서 프로젝트 문서를 관리할 때 항상 같은 패턴이 반복됩니다:

- 새 프로젝트마다 동일한 폴더 구조(허브, WBS, docs/, diagrams/)를 수동으로 생성
- 파일이 추가될수록 허브 노트 링크가 깨지고 방치됨
- 아키텍처 결정이 여러 노트에 흩어져 ADR 추적 불가
- HTML 시각화 파일이 잘못된 위치에 저장되어 Obsidian iframe이 깨짐

sr-obsidian은 실전 검증된 문서 관리 패턴을 스킬로 추상화하여 vault 내 모든 프로젝트에 일관되게 적용합니다.

---

## 문서 계층 원칙

```
docs/reports/{보고서}.md      ← 소스 오브 트루스 (전체 내용·분석·미결 포함)
        ↓ 내용 선별
diagrams/{보고서}.html         ← 전체 시각화 (sr-obsidian:visualize)
        ↓ 보고용 선별
diagrams/{보고서}-delivery.html ← 전달본 (보고·킥오프 등)
```

---

## 스킬 목록

| 스킬 | 호출 | 용도 |
|------|------|------|
| **sr-obsidian** | `/sr-obsidian` | **워크플로우 진입점** — 상황 파악 후 첫 번째 스킬 즉시 호출 |
| capture | `sr-obsidian:capture` | Fleeting 노트 포착 — 키워드만 기록, 00-inbox/ 저장 |
| study | `sr-obsidian:study` | 챕터 literature 노트 → permanent 노트 추출 (2-phase: 분석 → 생성) |
| wiki | `sr-obsidian:wiki` | LLM Wiki 용어 페이지 생성 — scan / create / index 모드 |
| init | `sr-obsidian:init` | 제텔카스텐 프로젝트 초기화 — book / area / vault 모드 |
| iss | `sr-obsidian:iss` | ISS 인시던트/이슈 전체 구조 생성 (hub + WBS + steps/ + comms/) |
| hub | `sr-obsidian:hub` | 허브 노트 링크·KPI·ISS 참조 관리 |
| wbs | `sr-obsidian:wbs` | WBS Phase 구성·진행 현황 관리 |
| history | `sr-obsidian:history` | ADR 생성·의사결정 로그·회의록 기록 |
| visualize | `sr-obsidian:visualize` | MD → HTML 시각화 (claude-visualize 래핑) + diagrams/ 저장·페어드 MD·허브 링크 |
| audit | `sr-obsidian:audit` | 표준 구조 대비 검증 |
| migrate | `sr-obsidian:migrate` | 비표준 파일을 표준 위치로 이관 |

---

## 표준 폴더 구조

```
{project}/
├── {project-id} 프로젝트 현황.md   ← 허브 (sr-obsidian:hub)
├── {project-id} WBS.md             ← WBS (sr-obsidian:wbs)
│
├── docs/
│   ├── specs/        ← 컴포넌트 역할, 인터페이스, 요구사항
│   ├── architecture/ ← 아키텍처 분석, 전문가 리뷰, 제약 분석
│   ├── adr/          ← Architecture Decision Records (sr-obsidian:history)
│   ├── reports/      ← 보고서 소스 MD
│   ├── runbook/      ← 운영 절차 (Phase 5+)
│   └── config/       ← 인프라·환경 설정 기록
│
├── diagrams/         ← HTML 전용 (sr-obsidian:visualize 출력)
├── features/         ← FT-xxx 기능 개발 폴더
├── phases/           ← Phase step 파일
└── meetings/         ← 회의록 (sr-obsidian:history)
```

---

## 설치

```bash
# 마켓플레이스 등록
claude plugins marketplace add SeokRae/sr-obsidian

# 설치
claude plugins install sr-obsidian
```

Claude Code 재시작 후 확인:

```bash
claude plugins list
#   ❯ sr-obsidian@sr-obsidian
#     Version: 0.1.0
#     Scope: user
#     Status: ✔ enabled
```

---

## 기여

[CONTRIBUTING.md](./CONTRIBUTING.md) 참고.

## 라이선스

MIT © SeokRae
