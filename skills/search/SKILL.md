---
name: search
description: >
  sr-labs vault를 자연어 쿼리로 검색. "X 찾아줘", "Y 관련 이슈 있어?", "Z 어디서 다뤘지?",
  "ISS-XXX 어떻게 됐어", "FT-XXX 관련 노트" 같은 표현에서 즉시 실행.
  키워드·필드명·이슈번호·도메인 용어 등 어떤 형태의 쿼리든 받아 관련 노트 목록과
  맥락 스니펫을 vault 영역별로 그룹화하여 반환. 60-logs(데일리·주간보고)는 기본 제외.
  Do NOT use for wiki 용어 페이지 질의·생성 (use sr-obsidian:wiki — search는 vault 전체 노트 검색, wiki query는 wiki-term 우선 질의·답변 파일링).
  Keywords: 찾아줘, 검색, 어디, 있어, 관련, 이슈 찾기, 노트 찾기, search, 조회, 어디서 다뤘
allowed-tools: Bash, Read
---

# sr-obsidian:search — vault 자연어 검색

## Step 1: 키워드 추출

쿼리에서 핵심 검색어를 추출한다. 불필요한 조사·동사("찾아줘", "관련", "어디서", "있어")는 제거.

| 입력 예시 | 추출 키워드 |
|-----------|------------|
| `payment_reference 관련 이슈 찾아줘` | `payment_reference` |
| `ISS-032 어떻게 됐어` | `ISS-032` |
| `결제 실패 어디서 논의했지` | `결제.*실패` 또는 두 단어 OR |
| `stripe sandbox 테스트 결과` | `stripe`, `sandbox` |
| `FT-015 진행 상황` | `FT-015` |

여러 키워드는 각각 `-e` 옵션으로 OR 검색한다.

## Step 2: 검색 실행

```bash
VAULT="/Users/sr/obsidian/sr-labs"

# 기본: 60-logs, _templates, _attachments 제외
rg -l -i \
  -e "{키워드1}" \
  [-e "{키워드2}"] \
  --glob "*.md" \
  --glob "!60-logs/**" \
  --glob "!_templates/**" \
  --glob "!_attachments/**" \
  "$VAULT" 2>/dev/null

# --logs 요청 시: 60-logs 포함
rg -l -i \
  -e "{키워드}" \
  --glob "*.md" \
  --glob "!_templates/**" \
  --glob "!_attachments/**" \
  "$VAULT" 2>/dev/null
```

파일 목록 확보 후 각 파일에서 키워드 주변 컨텍스트(앞뒤 1줄) 추출:

```bash
rg -i --no-heading -C 1 "{키워드}" "{파일경로}" 2>/dev/null | head -10
```

## Step 3: 결과 그룹화 및 출력

아래 순서로 영역별 그룹화:

1. `00-inbox/` — Inbox 메모
2. `10-projects/` — 진행 중 인시던트 (ISS-*)
3. `20-areas/` — 서비스 영역
4. `30-resources/` — 리소스·도메인 지식
5. `40-archives/` — 아카이브
6. `60-logs/` — 로그 (--logs 요청 시만 표시)

### 출력 형식

```
## 검색 결과: {쿼리} ({총 N건})

### {영역명} ({N건})

**{vault 상대 경로}**
> {매칭 줄 + 앞뒤 1줄 스니펫}

**{vault 상대 경로}**
> {스니펫}
```

- 결과 없음: `'{쿼리}' 관련 노트를 찾지 못했습니다. 다른 키워드로 시도해보세요.`
- 결과 30건 초과: 영역별 상위 5건만 표시 + `더 좁은 키워드로 재검색을 권장합니다.`

## 옵션 인식

쿼리에서 다음 패턴을 감지해 동작 조정:

| 패턴 | 동작 |
|------|------|
| `--logs` 또는 `데일리 포함` | 60-logs 검색 포함 |
| `--area payment` 또는 `payment 폴더에서` | `20-areas/payment/` 만 검색 |
| `--type issue` 또는 `이슈 노트만` | 프론트매터 `type: issue` 파일만 |
| `ISS-\d+` 패턴 | `10-projects/` + `40-archives/` 우선 검색 |
