---
name: hub
description: >
  프로젝트 허브 노트({project-id} 프로젝트 현황.md) 생성·링크·KPI·상태 관리.
  "허브 업데이트", "현황 노트", "프로젝트 현황 정리" 요청 시 사용.
  Do NOT use for new project folder creation (use sr-obsidian:scaffold first).
  Do NOT use for ISS incident structure (use sr-obsidian:iss).
  Do NOT use for WBS Phase·step 상태머신·진행 현황 생성·관리 (use sr-obsidian:wbs — hub는 프로젝트 허브 노트·링크·KPI 관리, wbs는 WBS Phase·step 상태머신).
  Do NOT use for 누적 기록의 사후 종합 인수인계·경위 문서 (use sr-obsidian:handover — hub는 현재 상태 스냅샷·링크·KPI 관리, handover는 축적된 기록의 경위 서사 복원).
  Keywords: hub, 허브, 프로젝트 현황, KPI, ISS 링크, 다이어그램 링크
allowed-tools: Read, Write, Bash, Edit
---

# sr-obsidian:hub — 허브 노트 관리

`{project-id} 프로젝트 현황.md` 파일의 생성·링크 최신화·KPI 반영을 담당한다.

## 허브 노트 역할

허브 노트는 프로젝트의 **단일 진입점**:

| 섹션 | 내용 | 갱신 주기 |
|------|------|----------|
| 🔗 바로가기 | WBS·docs·diagrams 링크 | 파일 추가 시 |
| 📌 개요 | 목적·기간·관련 시스템 | Phase 전환 시 |
| 📊 프레젠테이션 요약 | §1개요·§2본론·§3결론 | 보고 전 |
| 📐 다이어그램 | diagrams/ HTML iframe | 다이어그램 추가 시 |
| 🔗 관련 ISS | ISS 인시던트 링크 | ISS 발생 시 |
| 📋 문서 | docs/ 주요 파일 링크 | 문서 추가 시 |

## 실행 절차

### Step 1. 현재 허브 노트 읽기

```bash
# 허브 노트 경로
cat "20-areas/payment/{project-id}/{project-id} 프로젝트 현황.md"
```

### Step 2. 요청 유형 판별

| 요청 | 처리 |
|------|------|
| 허브 신규 생성 | sr-obsidian:scaffold 실행 후 이 스킬로 보강 |
| 링크 최신화 | Step 3 → docs·diagrams 파일 스캔 후 업데이트 |
| KPI 반영 | Step 4 → 프레젠테이션 요약 섹션 보강 |
| ISS 연결 | Step 5 → 관련 ISS 섹션 추가 |
| 상태 변경 | frontmatter `status` 필드 업데이트 |

### Step 3. 링크 최신화

**docs/ 스캔:**
```bash
find "20-areas/payment/{project-id}/docs" -name "*.md" | sort
```

**diagrams/ 스캔:**
```bash
find "20-areas/payment/{project-id}/diagrams" -name "*.html" | sort
```

각 파일을 `## 📋 문서` 테이블과 `## 📐 다이어그램` 섹션에 반영.

다이어그램 iframe 패턴:
```html
<iframe src="file:///Users/sr/obsidian/sr-labs/20-areas/payment/{project-id}/diagrams/{file}.html"
        width="100%" height="900" style="border:none;border-radius:8px;"></iframe>
```

### Step 4. 프레젠테이션 요약 (§1·§2·§3)

`20-areas/CLAUDE.md` 규칙에 따라 작성:
- `phase: draft` → §1만 작성, §2·§3은 `(미결)`
- §2·§3는 해당 Phase 진입 시 보완
- 각 항목 한 줄~두 줄 제한
- 허브 노트에 있는 내용만 사용 — 추정 금지

### Step 5. ISS 연결

ISS 링크 패턴:
```markdown
- [[10-projects/ISS-{NNN}-{slug}/ISS-{NNN} {title}|ISS-{NNN}]] — {한 줄 설명}
```

### Step 6. 완료 보고

변경된 섹션 목록과 업데이트 내용을 요약해서 보고.

## 판단 기준

| 상황 | 처리 |
|------|------|
| 허브 파일 미발견 | 서비스명 확인 후 `20-areas/payment/{서비스}/{서비스} 프로젝트 현황.md` 경로 안내 |
| `diagrams/` 폴더 없음 | 섹션 추가 없이 진행, diagrams/ 생성 시 sr-obsidian:visualize 안내 |
| KPI 섹션 비어 있음 | 빈 테이블로 유지, 추정값 채우지 않음 |
| 새 프로젝트 폴더 자체가 없음 | sr-obsidian:scaffold 먼저 실행 안내 |
| ISS 번호 찾기 불명확 | `10-projects/ISS-*/` Glob으로 목록 제시 후 선택 |
