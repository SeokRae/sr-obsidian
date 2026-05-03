---
name: init
description: >
  Obsidian 프로젝트 폴더 구조 초기화. 새 프로젝트 시작 시 허브·WBS·docs·diagrams 구조를 한 번에 생성.
  Keywords: init, 프로젝트 생성, 폴더 구조, 새 프로젝트, project init
allowed-tools: Read, Write, Bash, Edit
---

# sr-obsidian:init — 프로젝트 폴더 구조 초기화

새 프로젝트 폴더 전체 구조(허브·WBS·docs 6개 하위폴더·diagrams)를 한 번에 생성한다.

## 실행 절차

### Step 1. 대상 경로 확인

사용자 메시지에서 파악하거나 질문:

| 항목 | 예시 |
|------|------|
| `project-id` | `payment-npg-core` |
| `project-name` | `NPG Core` |
| `base-path` | `20-areas/payment/npg-core/` |
| `start-date` | `2026-05-01` |
| `description` | 프로젝트 한 줄 설명 |

### Step 2. 디렉토리 생성

```bash
base="20-areas/payment/{project-id}"
mkdir -p "$base/docs/specs"
mkdir -p "$base/docs/architecture"
mkdir -p "$base/docs/adr"
mkdir -p "$base/docs/reports"
mkdir -p "$base/docs/runbook"
mkdir -p "$base/docs/config"
mkdir -p "$base/diagrams"
mkdir -p "$base/features"
mkdir -p "$base/phases"
mkdir -p "$base/meetings"
```

### Step 3. 허브 노트 생성

파일: `{base-path}/{project-id} 프로젝트 현황.md`

```markdown
---
type: project
created: {YYYY-MM-DD}
tags: [project, {project-id}]
project-id: {project-id}
status: active
start-date: {start-date}
end-date:
description: {description}
---

# {project-id} 프로젝트 현황

> {description}

← [[이슈 트래킹 MOC]] | 📊 [[{project-id} WBS]]

---

## 🔗 바로가기

- 📊 [[{project-id} WBS]] · features/ · docs/ · diagrams/

## 📌 개요

- **목적**: (미결)
- **기간**: {start-date} ~

## 📊 프레젠테이션 요약

### §1 개요
- **개념 정의**: (미결)
- **기능 범위**: (미결)
- **관련 시스템**: (미결)

### §2 본론
- **핵심 요구사항**: (미결)
- **주요 제약**: (미결)

### §3 결론
- **기대효과**: (미결)
- **시사점**: (미결)

## 📐 다이어그램

(diagrams/ 파일 추가 후 링크 연결)

## 🔗 관련 ISS

(연관 ISS 발생 시 추가)

## 📋 문서

| 구분 | 파일 |
|------|------|
| 보고서 | (추가 예정) |
| 설계 | (추가 예정) |
```

### Step 4. WBS 노트 생성

파일: `{base-path}/{project-id} WBS.md`

```markdown
---
type: wbs
project: {project-id}
wbs-status: active
created: {YYYY-MM-DD}
updated: {YYYY-MM-DD}
start-date: {start-date}
end-date:
tags: [wbs, {project-id}]
---

# {project-id} WBS

← [[{project-id} 프로젝트 현황]]

---

## 프로젝트 개요

| 항목 | 값 |
|------|-----|
| 프로젝트명 | {project-name} ({project-id}) |
| 목적 | (미결) |
| 기간 | {start-date} ~ (미결) |

---

## Phase 진행 현황

| Phase | 제목 | 상태 | 기간 |
|-------|------|------|------|
| Phase 0 | 준비 | ready | - |

---

## 미결 사항

- [ ] Phase 계획 수립
```

### Step 5. 완료 보고

```
✅ 생성 완료: {base-path}
  ├── {project-id} 프로젝트 현황.md
  ├── {project-id} WBS.md
  ├── docs/specs/, architecture/, adr/, reports/, runbook/, config/
  ├── diagrams/
  ├── features/, phases/, meetings/

다음 단계:
  - sr-obsidian:hub  → 허브 노트 내용 보강
  - sr-obsidian:audit → 구조 검증
```
