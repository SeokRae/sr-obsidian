---
name: migrate
description: >
  비표준 프로젝트 구조를 표준으로 이관. docs/ 직하 파일 → 하위폴더, HTML → diagrams/ 이동.
  "구조 정리", "파일 이동", "migrate", "docs 재구성" 요청 시 사용.
  Keywords: migrate, 이관, 파일 이동, 구조 정리, 재구성
allowed-tools: Read, Write, Bash, Edit
---

# sr-obsidian:migrate — 구조 이관

`sr-obsidian:audit` 결과를 기반으로 비표준 파일·폴더를 표준 위치로 이동한다.

## 실행 절차

### Step 1. audit 결과 확인

`sr-obsidian:audit` 를 먼저 실행하거나 현재 구조를 스캔:

```bash
find "20-areas/payment/{project-id}" -maxdepth 3 | sort
```

### Step 2. 이관 계획 생성

파일별로 이동 계획을 테이블로 제시:

| 현재 위치 | 이동 위치 | 사유 |
|-----------|-----------|------|
| `docs/01-component.md` | `docs/specs/01-component.md` | specs/ 분류 |
| `docs/analysis.md` | `docs/architecture/analysis.md` | architecture/ 분류 |
| `docs/report.html` | `diagrams/report.html` | HTML → diagrams/ |

**사용자 확인을 받은 후 실행.**

### Step 3. 파일 이동 실행

```bash
# git mv로 이동 (히스토리 보존)
git -C /Users/sr/obsidian/sr-labs mv \
  "20-areas/payment/{project-id}/docs/{file}" \
  "20-areas/payment/{project-id}/docs/{subfolder}/{file}"
```

HTML 파일 이동:
```bash
git -C /Users/sr/obsidian/sr-labs mv \
  "20-areas/payment/{project-id}/docs/{file}.html" \
  "20-areas/payment/{project-id}/diagrams/{file}.html"
```

### Step 4. 링크 업데이트

이동된 파일을 참조하는 모든 노트의 링크 경로 업데이트:

```bash
# 이동된 파일명으로 역참조 검색
grep -rl "{old-path}" "20-areas/payment/{project-id}/"
```

각 파일에서 경로 수정 (perl 사용):
```bash
perl -pi -e 's|{old-path}|{new-path}|g' {참조파일}
```

iframe src 절대경로도 함께 수정.

### Step 5. 누락 폴더 생성

표준 폴더 중 없는 것 생성:
```bash
for dir in specs architecture adr reports runbook config; do
  mkdir -p "20-areas/payment/{project-id}/docs/$dir"
done
```

### Step 6. 검증

이관 후 `sr-obsidian:audit` 재실행하여 모든 항목 통과 확인.

### Step 7. 완료 보고

```
이관 완료:
  이동: {N}개 파일
  링크 업데이트: {N}개 파일
  폴더 생성: {N}개

sr-obsidian:audit 재실행 결과: ✅ 전체 통과
```
