---
name: wiki
description: >
  LLM Wiki 용어 페이지 생성·질의·인덱스 관리.
  scan(폴더 스캔으로 후보 추출), create(직접 용어 지정), query(wiki-first 질의 + 답변 파일링), index(인덱스 재생성) 4가지 모드.
  type:permanent + wiki-term:true 프론트매터로 기존 lint-wiki·Dataview 인프라와 호환.
  "wiki", "용어", "위키", "glossary", "용어 페이지", "wiki 만들어줘", "wiki에서 찾아줘" 요청 시 사용.
  Do NOT use for non-wiki permanent notes from literature/study (use sr-obsidian:study).
  Do NOT use for wiki 품질·연결 검사 (use sr-obsidian:lint-wiki — wiki는 용어 생성·질의, lint-wiki는 orphan·dangling·moc 품질 검사).
  Do NOT use for 외부 웹 최신 정보 수집·동향 누적 (use sr-obsidian:radar — wiki는 vault 내부 노트 용어 추출·질의, radar는 외부 웹 수집·누적).
  Keywords: wiki, 용어, 위키, glossary, term, wiki-term, 용어 페이지, query, 질의
allowed-tools: Read, Glob, Grep, Write, Edit, Bash
---

# sr-obsidian:wiki — 용어 Wiki 페이지 생성·질의

> **참조**: [Karpathy — LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
> "LLM이 persistent wiki를 점진적으로 구축·유지한다. 지식은 매 쿼리마다 재발견되지 않고 한 번 컴파일된 뒤 축적된다."

## 사용법

```
/sr-obsidian:wiki scan 30-resources/tech/concurrency/   # 폴더 스캔으로 wiki 후보 추출
/sr-obsidian:wiki create "Token Bucket"                  # 직접 용어 지정
/sr-obsidian:wiki query "토큰 버킷과 리키 버킷의 차이는?"  # wiki-first 질의 + 답변 파일링
/sr-obsidian:wiki index                                  # wiki-index.md 정적 테이블 재생성
```

## 핵심 원칙

- wiki 페이지 = `type: permanent` + `wiki-term: true` — 기존 인프라 재사용
- **저장 위치는 `30-resources/{카테고리}/{주제}/` 고정** — `20-areas/`에 wiki-term 노트 생성 금지
- lint-wiki 4종 검사(orphan, dangling, MOC, 섹션) 모두 적용
- Phase 1은 READ-ONLY, Phase 2부터 파일 수정
- **모든 생성·수정 후 ingest-log에 기록** (형식: `## [YYYY-MM-DD] wiki | {용어명}`)

### wiki-term 판단 기준

| 조건 | 처리 |
|------|------|
| 기술사 4유형(technology/architecture/principle/metric)으로 정의 가능 | wiki-term → `30-resources/{카테고리}/{주제}/` |
| vault 고유 컨텍스트(워크플로우·가이드·현황·운영 절차) | `20-areas/` 유지, `wiki-term: true` 부여 금지 |

---

## 모드 1: `scan` — 폴더 스캔으로 후보 추출

### Phase 1: 스캔 (READ-ONLY)

1. 대상 폴더의 `type: permanent` 노트 전체 `Read`
2. 기존 `wiki-term: true` 노트 확인: `Grep "wiki-term: true" 30-resources/ 20-areas/`
3. 용어 후보 추출 (신호 강도 순):
   - **Dangling wikilink**: `[[링크]]`인데 실제 파일 없는 것
   - **볼드 용어**: `**Term**` 또는 `**용어(영문)**` 패턴
   - **H2/H3 개념명**: 섹션 제목이 개념·약어인 것
   - **반복 태그**: 2개 이상 노트에 등장하는 태그
4. 기존 wiki-term 노트와 중복 체크

**출력 형식**:

---

### 🔍 Wiki 용어 후보 — {대상 경로}

| # | 용어 후보 | 출처 노트 | 상태 | 신호 |
|---|----------|----------|------|------|
| 1 | {용어명} | [[출처 노트]] | 신규 / 기존 | dangling / 볼드 / 섹션 / 태그 |

> 생성할 번호를 선택하세요. (예: "1,3,4" / "전체")
> 기존 노트에 wiki-term 태깅만 원하면 "태깅: {번호}" 입력

---

### Phase 2: 생성 (WRITE)

1. **GitHub Issue 생성**
   ```bash
   gh issue create --repo SeokRae/knowledge-labs \
     --title "docs: wiki-term {용어} 추가" \
     --body "wiki-term 페이지 생성 — /wiki scan 결과"
   ```
2. **Branch 생성** (반드시 main에서)
   ```bash
   git checkout main && git pull origin main
   git checkout -b feature/{issue번호}-wiki-{용어-slug}
   ```
3. **선택된 용어별 처리**:
   - **신규**: Obsidian CLI로 템플릿 적용 후 내용 편집
     ```bash
     obsidian create path="30-resources/{카테고리}/{파일명}.md" template="tpl-wiki-term"
     ```
     → 생성된 파일 `Read` → `Edit`으로 4유형 섹션 채우기 (`technology` / `architecture` / `principle` / `metric`)
   - **태깅만**: 기존 노트 프론트매터에 `wiki-term: true` 추가 `Edit`
4. **Fan-out**: 출처 노트의 `## 관련 메모`에 역링크 삽입
5. **wiki-index.md** 정적 테이블 새 행 추가
6. **Ingest Log** 기록:
   ```
   ## [YYYY-MM-DD] wiki | {용어명}
   - 생성: [[{파일경로}]]
   - 출처: [[{출처 노트}]]
   - 유형: {technology|architecture|principle|metric}
   ```
7. **커밋 + PR**:
   ```bash
   git add -A
   git commit -m "docs: wiki-term {용어} 추가 (#{issue번호})"
   git push -u origin HEAD
   gh pr create --title "docs: wiki-term {용어} 추가" --body "Closes #{issue번호}"
   ```

---

## 모드 2: `create` — 직접 용어 지정

### Phase 1: 리서치 (READ-ONLY)

1. vault 내 관련 노트 검색:
   ```bash
   obsidian search query="{용어}" path="30-resources" vault=sr-labs limit=10 2>/dev/null || true
   ```
2. 관련 노트 `Read` → 기존 설명·맥락 파악
3. 중복 wiki-term 노트 확인
4. **유형 판별**:
   ```
   1. "비교하시오" / "{A}와 {B}" 패턴?     → architecture
   2. 지표·공식·계산이 핵심?               → metric
   3. 동작 원리·메커니즘·흐름이 핵심?       → principle
   4. 그 외 H/W·S/W 기술·개념 단독 설명?   → technology (기본값)
   ```
5. wiki 페이지 초안 출력

### Phase 2: 생성 (WRITE)

scan Phase 2와 동일한 순서로 진행 (`obsidian create` → Read → Edit → fan-out → wiki-index → log → PR).

---

## 모드 3: `query` — wiki-first 질의 + 답변 파일링

Karpathy: *"좋은 답변은 새 wiki 페이지로 저장되어야 한다. 탐구 결과가 chat 히스토리로 사라지지 않게 한다."*

### Phase 1: wiki-first 검색 (READ-ONLY)

1. **index 스캔**: `50-moc/wiki-index.md` 먼저 읽어 관련 페이지 후보 파악
2. **관련 페이지 Read**: 후보 wiki-term 노트 + permanent 노트 읽기
3. **답변 합성**: 읽은 내용 기반으로 답변 초안 작성 (wiki 내 출처 인용 필수)
4. **파일링 여부 판단**:
   - 새로운 비교·분석·연결이 포함된 답변 → 파일링 권장
   - 단순 사실 확인 → 파일링 불필요

**출력 형식**:

---

### 💡 Wiki 답변 — {질문}

{답변 내용 (wiki 페이지 인용 포함)}

> 출처: [[{페이지A}]], [[{페이지B}]]

**이 답변을 wiki 페이지로 저장할까요?** (y/n)
> 저장하면: `30-resources/{카테고리}/{제목}.md` 로 `type: permanent` + `wiki-term: true` 파일 생성

---

### Phase 2: 파일링 (WRITE, 사용자 승인 시)

scan Phase 2와 동일하되, 출처는 "query 답변"으로 기록:
```
## [YYYY-MM-DD] wiki | {제목}
- 생성: [[{파일경로}]]
- 출처: query — "{원래 질문}"
- 유형: {answer-type}
```

---

## 모드 4: `index` — 인덱스 재생성

`wiki-term: true` 노트 전체를 스캔해서 `50-moc/wiki-index.md`의 정적 테이블을 재생성한다.

```bash
grep -rl "wiki-term: true" /Users/sr/obsidian/sr-labs/30-resources \
  /Users/sr/obsidian/sr-labs/20-areas 2>/dev/null
```

수집된 노트를 폴더별로 정렬 → 정적 테이블 재작성 → 커밋.

**테이블 형식** (Karpathy index.md 스타일 — 링크·한줄요약·메타 포함):

| 용어 | 유형 | 한줄 정의 | 카테고리 | 생성일 |
|------|------|----------|---------|--------|
| [[Token-Bucket]] | technology | 버킷에 토큰을 채워 요청 속도를 제한하는 알고리즘 | rate-limit | 2026-01-01 |

---

## Wiki 페이지 생성 형식 (`tpl-wiki-term`) — 기술사 답변 패턴

**4유형 × 3섹션** 구조. 유형은 Phase 1에서 자동 판별.

### 공통 프론트매터

```markdown
---
type: permanent
wiki-term: true
answer-type: {technology|architecture|principle|metric}
created: {YYYY-MM-DD}
tags: [{주제}, wiki-term]
aliases: [{영문 약어}, {한국어 풀네임}]
---

# {용어명}

> **한 줄 정의**: {한 문장}

← [[{관련 MOC}]]
```

### technology 형식 (기본값)

```
**1. {특성1}, {용어명} 개요**
가. {배경/역할}, {용어명}의 정의
나. {용어명}의 특성 (표)

**2. {용어명}의 구조와 구성요소**
가. 구성도 (ASCII art)
나. 구성요소 (표)

**3. {용어명}의 발전방향**
AS-IS / TO-BE / 효과 (표)
"끝"
```

### architecture 형식

```
**1. {배경키워드}, {용어명} 개요**
가. 정의 / 나. 종류 (표)

**2. {A}와 {B}의 비교**
가. 구성도 (ASCII) / 나. 비교표 (구분·A·B)

**3. 도입 시 고려사항** (성능·보안·비용)
"끝"
```

### principle 형식

```
**1. {적용 효과}, {용어명} 개요**
가. 정의 / 나. 유형 (표)

**2. {용어명}의 동작 방식**
가. 개념도 (ASCII) / 나. 세부 동작 (표)

**3. {용어명}의 적용 사례** (표)
"끝"
```

### metric 형식

```
**1. {측정 목적}, {용어명} 개요**
가. 지표 정의 (표) / 나. 중요성

**2. 개념 및 계산법**
가. 개념도 (ASCII) / 나. 계산 공식

**3. {용어명}의 활용** (표)
"끝"
```

**파일명 규칙**: 용어명 그대로. 영문 약어 대문자, 한국어 설명은 kebab-case.
예: `KYC-고객확인제도.md`, `DNAT.md`, `Token-Bucket.md`

---

## 판단 기준

| 상황 | 처리 |
|------|------|
| 이미 wiki-term 노트 존재 | 스킵 (중복 생성 금지) |
| thesis-style 노트가 해당 용어 커버 | "태깅만" 옵션 제안 |
| 용어가 너무 세부적 (1개 노트에서만 등장) | "하위 개념" 표시 — 사용자 판단 |
| 용어가 여러 노트에 걸쳐 등장 | 우선 생성 권장 |
| query 답변이 비교·분석·새 연결 포함 | wiki 페이지로 파일링 권장 |
| query 답변이 단순 사실 확인 | 파일링 불필요, 답변만 제공 |
