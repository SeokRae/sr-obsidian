# /wbs detail — Task 상세화

## 처리 순서

1. Read: `wbs.md` + `phases/phase-N.md` + step 파일 전체
2. 각 phase 파일 `##` 섹션에 `- [ ]` Task 추가
3. 모든 Task에 4속성:

```markdown
- [ ] {Task명}
  - **담당자**: {역할}
  - **기간**: {0.5~3일}
  - **산출물**: {결과물}
  - **의존성**: {선행 Task명 또는 없음}
```

4. 세부 분리 Phase step 파일: skeleton 골격에 실제 내용 추가 (Write로 덮어쓰기)
   - `## 체크리스트`: 단계별 구체적 항목
   - `## 요청 문서 / 결과 기록`: ITSM 양식·결과값 테이블
   - step 파일은 단독으로 열어도 맥락이 완전해야 함 (자기완결)

## Task 작성 기준

- **담당자**: 역할명 (`PM`, `Backend Developer`, `DBA`, `QA Engineer`)
- **기간**: 0.5일 단위 (0.5~3) — 3일 초과 시 분해
- **산출물**: 구체적 파일·문서·결과물
- **의존성**: "없음" 또는 선행 Task명

## 출력 형식

```markdown
## /wbs detail 결과

### Phase별 상세화 내용
{phase 파일별 task 목록 일부}

### 요약
- 총 Task 수: N개
- Phase별 Task 수: {Phase1: N, ...}

### 다음 단계
`wbs-status`를 `review`로 업데이트한 뒤 `/wbs`를 재실행하세요.
```
