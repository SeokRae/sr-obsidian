---
name: study
description: >
  챕터 literature 노트 분석 → permanent 노트 추출. 읽은 챕터에서 핵심 개념을 식별하고,
  기존 permanent 노트와 중복 체크 후 새 permanent 노트를 생성하고 학습 메모를 채운다.
  "학습", "읽기", "독서", "개념 추출", "permanent 생성", "챕터 정리", "study" 요청 시 사용.
  Keywords: 학습, 읽기, 독서, 개념 추출, permanent 생성, 학습 메모, study, literature, 챕터
allowed-tools: Read, Glob, Write, Edit, Bash
---

# sr-obsidian:study — 챕터 분석 및 Permanent 노트 추출

## 사용법

```
/sr-obsidian:study @"30-resources/{카테고리}/{주제}/{책}/ch{NN}-{제목}.md"
```

## 2-Phase 워크플로우

### Phase 1: analyze (READ-ONLY)

`$ARGUMENTS` 로 받은 챕터 literature 노트를 분석한다. **파일 수정 없음.**

**수행 순서**:

1. 챕터 파일 전문 `Read`
2. `30-resources/{카테고리}/{주제}/*.md` `Glob` → 기존 permanent 노트 목록 수집
3. **(Obsidian CLI 보강)** 태그 기반 관련 노트 검색:
   ```bash
   obsidian tags name="{주제 태그}" vault=sr-labs 2>/dev/null || true
   obsidian search query="{핵심 키워드}" path="30-resources" vault=sr-labs limit=10 2>/dev/null || true
   ```
   > CLI 실패 시 Glob 결과만으로 진행 (graceful fallback)
4. 기존 permanent 노트 중 챕터와 관련성 높은 것 `Read` → 중복 여부 확인
5. `50-moc/` 내 관련 MOC 파일 확인 (`Glob "50-moc/*{주제}*"`)
6. 핵심 개념 식별 → 추출 후보 목록 생성
7. 챕터 `## 학습 메모` 섹션 초안 생성

**출력 형식**:

---

### 📚 챕터 분석: {파일명}

**기존 permanent 노트** (`30-resources/{카테고리}/{주제}/`):
| 파일명 | 관련성 |
|--------|--------|
| `[[노트 제목]]` | 높음/중간/낮음 |

---

### 🔍 추출 후보

| # | claim-style 제목 (후보) | 중복 | 근거 (챕터 내 증거) |
|---|------------------------|------|-------------------|
| 1 | {제목} | 없음 / `[[기존 노트]]`와 중복 | 챕터 내 핵심 문장 |
| 2 | ... | ... | ... |

> 중복 판단 기준: 기존 permanent 노트와 claim이 실질적으로 동일한 경우 "중복"으로 표시.
> 기존 노트를 보강할 수 있는 새 관점이 있으면 "확장 가능"으로 표시.

---

### 📝 학습 메모 초안

```markdown
## 학습 메모

### 핵심 개념
- {개념 1}: {한 줄 설명}

### 질문
- {이해 안 된 부분 또는 더 탐구할 질문}

### 연결
- `[[{연결할 permanent 노트}]]` — {연결 이유}
```

---

**다음 단계**: 생성할 후보 번호를 알려주세요. (예: "1, 3 생성" 또는 "전체 생성")

---

### Phase 2: extract (WRITE)

사용자가 후보 번호를 승인하면 실행한다.

**수행 순서**:

1. **승인된 후보별** permanent 노트 `Write` → `30-resources/{카테고리}/{주제}/{claim-style 제목}.md`
   - 기존 파일이 있으면 덮어쓰기 금지 — 사용자에게 확인 요청
2. **챕터 파일** `## 학습 메모` 섹션 `Edit` → Phase 1에서 생성한 초안으로 채움
3. **Fan-out (역링크 삽입)** — 새 노트와 관련 있는 기존 permanent 노트에 백링크 추가:
   1. 새 노트의 `tags`·제목 키워드로 `Grep`·`Glob` 검색 → 기존 `type:permanent` 후보 최대 10개 탐색
   2. 후보 목록을 제목 + 연결 근거와 함께 사용자에게 제시
   3. 사용자가 승인한 후보의 `## 관련 메모` 섹션에 `- [[새 노트 제목]]` 라인 `Edit`으로 삽입
   4. 연결할 MOC 후보도 함께 제시 (MOC 갱신은 사용자 판단)
4. **MOC 갱신 안내** — 직접 수정하지 않음 (섹션 위치는 사용자가 판단)
5. **Ingest Log** 기록:
   ```bash
   printf '\n## [%s] study | {챕터 제목} (permanent) → {N}개\n{생성된 파일 경로 목록}\n' \
     "$(date +%Y-%m-%d)" >> 60-logs/ingest-log.md
   ```
6. **Obsidian CLI** 로 생성된 노트 열기:
   ```bash
   obsidian open path="30-resources/{카테고리}/{주제}/{파일명}.md" vault=sr-labs 2>/dev/null || true
   ```

## Permanent 노트 생성 형식

```markdown
---
type: permanent
created: {YYYY-MM-DD}
tags: [{주제 태그}]
---

# {claim-style 제목}

← [[{관련 MOC}]]

## 아이디어

{핵심 주장 2~4문장. 코드 예시 포함 가능.}

## 근거

- {사실적 근거 bullet}
- {구체적 참조 (API, 스펙, 챕터)}

## 개념 확장

{주변 개념과의 연결, 트레이드오프, 실전 적용}

## 면접 포인트

**예상 질문**: {이 개념에서 면접관이 물어볼 법한 질문 1~2개}
**핵심 답변**: {한 줄 요약}
**함정**: {헷갈리기 쉬운 포인트}
**비교**:
| | {A} | {B} |
|--|--|--|
| {기준} | {A 특성} | {B 특성} |

## 관련 메모

- [[{관련 permanent 노트}]]
- [[{원본 챕터 파일명}]]
```

## 판단 기준

| 상황 | 처리 |
|------|------|
| 완전히 새로운 개념 | 새 permanent 노트 생성 |
| 기존 노트와 동일한 claim | 중복 — 생성 건너뜀 (사용자에게 알림) |
| 기존 노트에 추가할 관점 | "확장 가능" 표시 — 사용자가 직접 편집 |
| 구현 세부사항·예제 코드 | permanent 노트보다 챕터 학습 메모에 기록 |
