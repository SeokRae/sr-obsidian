# /wbs export — Excel 변환

## 처리

1. Read: `wbs.md` 프론트매터(시작일 확인)
2. 변환 명령어 생성 및 안내

## 출력 형식

```markdown
## /wbs export 안내

### 변환 명령어
\`\`\`bash
cd /Users/sr/IdeaProjects/payment/manage/wbs-guidelines
python scripts/md-to-excel.py "{wbs.md 절대경로}" "{출력경로}/output.xlsx" {시작일 YYYY-MM-DD}
\`\`\`

### Excel 컬럼 구조
A: WBS Code | B: Level | C: Phase | D: Stage | E: Task Group
F: Task Name | G: Owner | H: Duration | I: Deliverable | J: Dependency
K: Start | L: End | M+: 날짜별 컬럼

### 변환 후 확인 사항
- [ ] 총 Task 수 일치 (phase 파일 합산 N개 ↔ Excel N행)
- [ ] 자동 스케줄링 (Start/End 날짜) 확인
- [ ] 의존성 기반 날짜 순서 확인
- [ ] WBS Code 체계 (1.1.1 형식) 확인
```
