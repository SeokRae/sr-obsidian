---
name: audit
description: >
  프로젝트 문서 구조 검증. 표준 폴더·파일 존재 여부, HTML/MD 혼재, 링크 무결성 체크.
  "구조 확인", "docs 점검", "audit" 요청 시 사용.
  Keywords: audit, 구조 검증, 폴더 점검, 링크 확인, HTML 혼재
allowed-tools: Read, Bash
---

# sr-obsidian:audit — 프로젝트 구조 검증

프로젝트 폴더가 표준 구조를 충족하는지 체크리스트로 검증한다.

## 실행 절차

### Step 1. 대상 프로젝트 확인

```bash
PROJECT_PATH="20-areas/payment/{project-id}"
ls "$PROJECT_PATH"
```

### Step 2. 체크리스트 실행

각 항목을 순서대로 확인하고 결과를 `✅ / ❌ / ⚠️` 로 표기.

#### A. 핵심 파일

```bash
# 허브 노트
ls "$PROJECT_PATH"/*.md | grep "프로젝트 현황"

# WBS
ls "$PROJECT_PATH"/*.md | grep "WBS"
```

| # | 항목 | 결과 |
|---|------|------|
| A-1 | 허브 노트 (`{project-id} 프로젝트 현황.md`) 존재 | |
| A-2 | WBS (`{project-id} WBS.md`) 존재 | |

#### B. docs/ 하위 폴더

```bash
for dir in specs architecture adr reports runbook config; do
  [ -d "$PROJECT_PATH/docs/$dir" ] && echo "✅ $dir" || echo "❌ $dir"
done
```

| # | 폴더 | 결과 |
|---|------|------|
| B-1 | `docs/specs/` | |
| B-2 | `docs/architecture/` | |
| B-3 | `docs/adr/` | |
| B-4 | `docs/reports/` | |
| B-5 | `docs/runbook/` | |
| B-6 | `docs/config/` | |

#### C. docs/ 직하 파일 혼재 검출

```bash
# docs/ 직하에 MD/HTML 파일이 있으면 안 됨
find "$PROJECT_PATH/docs" -maxdepth 1 -type f \( -name "*.md" -o -name "*.html" \)
```

| # | 항목 | 결과 |
|---|------|------|
| C-1 | `docs/` 직하에 MD/HTML 없음 | |

#### D. diagrams/ 무결성

```bash
# HTML 파일마다 페어드 MD 존재 확인
for html in "$PROJECT_PATH/diagrams"/*.html; do
  md="${html%.html}.md"
  [ -f "$md" ] && echo "✅ $(basename $html)" || echo "❌ missing MD: $(basename $html)"
done
```

| # | 항목 | 결과 |
|---|------|------|
| D-1 | `diagrams/` 내 HTML마다 페어드 MD 존재 | |
| D-2 | `docs/` 에 HTML 파일 없음 | |

#### E. 히스토리

```bash
ls "$PROJECT_PATH/docs/adr/" 2>/dev/null | wc -l
ls "$PROJECT_PATH/meetings/" 2>/dev/null | wc -l
```

| # | 항목 | 결과 |
|---|------|------|
| E-1 | `docs/adr/` 에 ADR 파일 존재 (없으면 ⚠️) | |
| E-2 | `meetings/` 존재 (없으면 ⚠️) | |

### Step 3. 결과 요약

```
✅ 통과: {N}개
❌ 실패: {N}개 → sr-obsidian:migrate 로 해결 가능
⚠️ 경고: {N}개 → 선택적 보완

실패 항목:
  - {항목}: {조치 방법}
```

실패 항목이 있으면 `sr-obsidian:migrate` 실행을 제안.
