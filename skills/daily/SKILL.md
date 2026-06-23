---
name: daily
description: 오늘 데일리 노트를 생성한다. GitHub Issue → Feature 브랜치 → 노트 작성 → 커밋 → PR 전 과정 자동화. 파일이 이미 있으면 갱신 모드(미완 이슈 갱신)로 전환. Keywords: 데일리, daily, 오늘 노트, 일일 노트, 작업 로그, 갱신.
allowed-tools: Bash, Read, Glob, Write, Edit
---

# 데일리 노트 생성·갱신 워크플로우

## 사용법

```
/daily          # 오늘 날짜 기준 데일리 노트 생성 or 갱신
/daily 2026-04-01  # 특정 날짜 지정 (YYYY-MM-DD)
```

## 워크플로우

### Step 0: 날짜 계산

- `$ARGUMENTS`가 있으면 해당 날짜 사용 (형식: `YYYY-MM-DD`)
- 없으면 오늘 날짜 사용: `date +%Y-%m-%d`
- 요일 계산: `date -j -f "%Y-%m-%d" "{날짜}" +%a` (예: Mon, Tue, Wed, Thu, Fri, Sat, Sun)
- 연/월 추출: `YYYY`, `MM` (예: 2026, 04)
- 파일 경로: `60-logs/daily/{YYYY}/{MM}/{YYYY-MM-DD}.md`

### Step 1: 모드 결정

`60-logs/daily/{YYYY}/{MM}/{YYYY-MM-DD}.md` 존재 여부 확인:

- **없으면** → **생성 모드** (Step 1.5 → Step 2 진행)
- **있으면** → **갱신 모드** (Step G1 진행)

---

## 갱신 모드 (파일이 이미 존재할 때)

### Step G1: 오픈 이슈 조회 + 하위 작업 추출

오늘 갱신용으로 생성한 이슈(데일리 노트 자체 이슈), `docs: YYYY-MM-DD 데일리 노트 작성/갱신` 패턴의 이슈, 제목에 `(standing)` 마커가 있는 상시 이슈는 모두 제외한다.

각 이슈의 본문에서 `## 범위`, `## 작업 범위`, `## 작업 내용`, `## 변경사항`, `## 구현 내용`, `## 체크리스트`, `## Changes`, `## 산출물` 섹션의 bullet 항목을 추출해 계층형 sub-bullet으로 출력한다.

```python
python3 - <<'PYEOF'
import subprocess, json, re

TARGET_SECTIONS = {
    '범위', '작업 범위', '작업 내용', '변경사항', '구현 내용',
    '체크리스트', 'Changes', '산출물'
}
DAILY_SKIP = re.compile(r'^docs: \d{4}-\d{2}-\d{2} 데일리 노트')
STANDING_SKIP = re.compile(r'\(standing\)')  # 완료 불가한 상시 이슈는 미완 작업에서 제외

result = subprocess.run(
    ['gh', 'issue', 'list', '--repo', 'SeokRae/knowledge-labs',
     '--state', 'open', '--limit', '20', '--json', 'number,title'],
    capture_output=True, text=True
)
issues = json.loads(result.stdout)

for issue in issues:
    num = issue['number']
    title = issue['title']
    if DAILY_SKIP.match(title) or STANDING_SKIP.search(title):
        continue
    print(f"- [ ] #{num} — {title}")

    body_result = subprocess.run(
        ['gh', 'issue', 'view', str(num), '--repo', 'SeokRae/knowledge-labs',
         '--json', 'body'],
        capture_output=True, text=True
    )
    body = json.loads(body_result.stdout).get('body', '')

    in_section = False
    in_code = False
    for line in body.splitlines():
        if line.strip().startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        h = re.match(r'^## (.+)', line)
        if h:
            in_section = h.group(1).strip() in TARGET_SECTIONS
        elif in_section:
            stripped = line.strip()
            if re.match(r'^[-*] ', stripped) or re.match(r'^- \[', stripped):
                print(f"  {stripped}")
PYEOF
```

결과를 `{OPEN_ISSUES_WITH_STEPS}`로 저장한다.

### Step G2: 브랜치 확인

```bash
git branch --show-current
```

- 현재 브랜치가 `feature/*-daily-{YYYY-MM-DD}` 형식이면 → 그대로 사용
- 아니면 → 새 Issue + 브랜치 생성 후 진행

  ```bash
  gh issue create --repo SeokRae/knowledge-labs \
    --title "docs: {YYYY-MM-DD} 데일리 노트 갱신" \
    --body "- 미완 작업(GitHub Issues) 섹션 갱신\n- 파일: 60-logs/daily/{YYYY}/{MM}/{YYYY-MM-DD}.md"
  git checkout -b feature/{ISSUE_NUMBER}-daily-{YYYY-MM-DD}-update
  ```

### Step G3: 미완 작업 섹션 업데이트

**절대 전체 교체 금지.** 기존 이슈 항목의 상세 sub-bullet(주제/목적/문제현황/해결방안/미결 등)은 반드시 보존한다.

처리 방식:
1. Step G1 결과에서 **신규 이슈**(기존 섹션에 없는 번호)만 추출
2. 신규 이슈를 `## 미완 작업 (GitHub Issues)` 섹션의 **첫 번째 항목으로 삽입** (Edit 사용)
3. 기존 항목은 상세 sub-bullet 포함 그대로 유지

신규 이슈가 없으면 이 단계를 건너뛴다.

### Step G3.5: 오늘 git 커밋 → 작업 로그 자동 제안

작업 로그 섹션이 `- [ ]` placeholder 상태일 때만 실행한다. 이미 기록이 있으면 건너뛴다.

```bash
# 오늘 자정 이후 커밋 수집 (merge 커밋 제외)
git -C /Users/sr/obsidian/sr-labs log \
  --since="$(date +%Y-%m-%d) 00:00:00" \
  --oneline --no-merges 2>/dev/null | head -10
```

출력된 커밋 메시지에서 `#NNNN` PR 번호를 추출해 아래 형식으로 변환,
작업 로그 섹션의 `- [ ]` placeholder 한 줄을 **Edit로 교체**한다.

```
- [x] {커밋 메시지 요약} (PR #{번호})
```

제외 패턴: `docs: {YYYY-MM-DD} 데일리 노트` (데일리 노트 자체 커밋)
커밋이 없으면 이 단계를 건너뛴다.

### Step G4: 커밋 & Push

```bash
git add 60-logs/daily/{YYYY}/{MM}/{YYYY-MM-DD}.md
git commit -m "docs: {YYYY-MM-DD} 데일리 노트 갱신 (#{ISSUE_NUMBER})"
git push origin {현재_브랜치}
```

### Step G5: 완료 출력

```
✅ {YYYY-MM-DD} 데일리 노트 갱신 완료

파일  : 60-logs/daily/{YYYY}/{MM}/{YYYY-MM-DD}.md
Branch: {브랜치명}
```

---

## 생성 모드

### Step 1.5: 직전 노트 기반 전일 데이터 수집 (이월 + 완료 PR)

같은 달 폴더에서 오늘 이전 파일 중 가장 최근 파일을 찾는다:

```bash
ls 60-logs/daily/{YYYY}/{MM}/*.md 2>/dev/null \
  | grep -v "{YYYY-MM-DD}" | sort | tail -1
```

없으면 이전 달 폴더도 확인:

```bash
PREV_YM=$(date -j -f "%Y-%m-%d" "{YYYY-MM-DD}" -v-1m "+%Y/%m")
ls 60-logs/daily/$PREV_YM/*.md 2>/dev/null | sort | tail -1
```

이전 노트가 있으면 `## 목표`, `## 작업 로그`, `## 미완 작업` 섹션에서 `^- \[ \]` 항목을 추출한다.
단, `docs: YYYY-MM-DD 데일리 노트 작성/갱신` 패턴의 이슈와 제목에 `(standing)` 마커가 있는 상시 이슈는 이월하지 않는다.

추출 후 **최근 30개 데일리 노트에서 이슈별 이월 횟수를 카운트**해 각 항목에 태그를 붙인다:

```python
python3 - <<'EOF'
import re, glob

text = open("{PREV_NOTE_PATH}").read()
sections = ["목표", "작업 로그", "미완 작업 (GitHub Issues)"]
DAILY_SKIP = re.compile(r'— docs: \d{4}-\d{2}-\d{2} 데일리 노트')
STANDING_SKIP = re.compile(r'\(standing\)')  # 완료 불가한 상시 이슈는 이월·카운트 제외
results = []
current = None
for line in text.splitlines():
    h = re.match(r'^## (.+)', line)
    if h:
        current = h.group(1)
    elif current and any(s in current for s in sections):
        if line.startswith("- [ ]") and not DAILY_SKIP.search(line) and not STANDING_SKIP.search(line):
            results.append(line)

# 최근 30개 노트에서 이슈별 등장 횟수 카운트
recent_files = sorted(glob.glob("60-logs/daily/**/*.md", recursive=True))[-30:]
issue_counts = {}
for f in recent_files:
    try:
        content = open(f).read()
    except:
        continue
    for line in content.splitlines():
        if line.startswith("- [ ]") and not DAILY_SKIP.search(line) and not STANDING_SKIP.search(line):
            for num in re.findall(r'#(\d+)', line):
                issue_counts[num] = issue_counts.get(num, 0) + 1

# 이월 횟수 태그 추가
for item in results:
    nums = re.findall(r'#(\d+)', item)
    count = max((issue_counts.get(n, 0) for n in nums), default=0)
    if count >= 3:
        print(f"{item} ({count}회 이월) ⚠️ 재검토")
    elif count >= 1:
        print(f"{item} ({count}회 이월)")
    else:
        print(item)
EOF
```

추출 결과를 `{CARRIED_ITEMS}`로 저장한다. 없으면 빈 문자열.
직전 노트 파일명의 날짜를 `{PREV_DATE}`로 둔다.

**직전 노트~어제 완료 PR 집계** (`{PREV_DONE_PRS}`):

직전 노트 날짜(`{PREV_DATE}`)부터 어제(오늘 전날)까지 머지된 PR을 집계한다.
오늘 머지분은 "오늘 작업"이므로 제외하고, 데일리 노트·ingest 자동 기록 PR도 회고 대상이 아니므로 제외한다.
GitHub `merged:` 검색은 UTC 기준이므로 KST(`+09:00`) 시간대를 명시해 날짜 경계를 맞춘다.

```bash
YESTERDAY=$(date -j -v-1d -f "%Y-%m-%d" "{YYYY-MM-DD}" "+%Y-%m-%d")
gh pr list --repo SeokRae/knowledge-labs --state merged \
  --search "merged:{PREV_DATE}T00:00:00+09:00..${YESTERDAY}T23:59:59+09:00" \
  --json number,title --jq '
  .[] | select(.title | test("데일리 노트|\\(ingest\\)") | not)
  | "- [x] \(.title) (PR #\(.number))"'
```

출력을 `{PREV_DONE_PRS}`로 저장한다. 비어 있으면 `- (없음)`.
직전 노트가 금요일이면 주말 머지분까지 포함된다(merged 범위 = PREV_DATE ~ 어제).

### Step 1.6: 오늘 목표 자동 제안

`{CARRIED_ITEMS}` 에서 이월 횟수 내림차순 상위 2개를 선택해 `{GOAL_ITEMS}`로 저장한다.
이월 항목이 없으면 `{GOAL_ITEMS}` = `- [ ]` (빈 항목).

선택 규칙:
- 이월 횟수 파싱: `(\d+)회 이월` 패턴
- `⚠️ 재검토` 태그 항목 → 제목 뒤에 `(재검토 or 폐쇄 결정)` 주석 추가
- 상위 2개 초과 시 나머지는 `{GOAL_ITEMS}`에서 제외 (미완 작업 섹션엔 전부 포함)
- 이월 횟수가 동일하면 이슈 번호 내림차순(최신 이슈 우선)

### Step 2: GitHub Issue 생성

```bash
gh issue create \
  --repo SeokRae/knowledge-labs \
  --title "docs: {YYYY-MM-DD} 데일리 노트 작성" \
  --body "## Summary\n- {YYYY-MM-DD} ({요일}) 데일리 노트 생성\n- 파일: \`60-logs/daily/{YYYY}/{MM}/{YYYY-MM-DD}.md\`"
```

반환된 Issue 번호를 `{ISSUE_NUMBER}`로 저장한다.

### Step 3: Feature 브랜치 생성

현재 브랜치를 `{PREV_BRANCH}`로 저장한 뒤 새 브랜치로 전환:

```bash
git checkout -b feature/{ISSUE_NUMBER}-daily-{YYYY-MM-DD}
```

### Step 3.5: 오픈 이슈 + 하위 작업 조회

Step G1과 동일한 Python 스크립트를 실행해 `{OPEN_ISSUES_WITH_STEPS}`를 생성한다.
갱신용 이슈(오늘 데일리 노트 작성 이슈)는 제외한다.

### Step 4: 데일리 노트 작성

아래 형식으로 `60-logs/daily/{YYYY}/{MM}/{YYYY-MM-DD}.md` 를 Write한다.
`{YYYY-MM-DD}`, `{요일}` 은 실제 값으로 치환한다.

`## 전일 리마인드` 섹션은 `### ✅ 어제 완료`(`{PREV_DONE_PRS}`) + `### ⏭ 이어서 할 일`(`{CARRIED_ITEMS}`)로 구성한다.
직전 노트가 아예 없으면 섹션 전체를 생략하고, 한쪽 데이터만 비면 그 하위만 `- (없음)`으로 둔다.
`{OPEN_ISSUES}` 자리에는 `{OPEN_ISSUES_WITH_STEPS}` (이슈 제목 + 계층형 sub-bullet) 를 삽입한다.

```markdown
---
type: daily
created: {YYYY-MM-DD}
tags: [daily]
description: 날짜별 작업 로그 — 할 일, 배운 것, 회고
---

# {YYYY-MM-DD} ({요일})

## 전일 리마인드

> [[{PREV_DATE}]] 기준 — 완료 PR 자동 집계 + 미완 이월

### ✅ 어제 완료

{PREV_DONE_PRS}

### ⏭ 이어서 할 일

{CARRIED_ITEMS}

## 목표

{GOAL_ITEMS}

## Inbox — 오늘 포착한 것

> **구조**: 주제 / 목적 / 핵심 내용·지적사항 / 해결 방안 / 제약사항·미결
> 단순 운영 태스크는 제목 한 줄만 유지 가능

- [ ] [[이슈 링크]] 제목
  - **주제**: 무엇에 관한 내용인지 (날짜·출처 포함)
  - **목적**: 왜 이 작업/회의가 필요한지
  - **핵심 내용 / 지적사항**
    - ① 항목별로 번호 목록으로 세분화
    - ② 각 항목은 원인·영향까지 한 줄로
  - **해결 방안**: 결정된 대응 방향 (근거 포함)
  - **제약사항 / 미결**
    - 각 미결 항목 — 왜 미결인지 한 줄 설명

## 작업 로그

> **ISS 작업**: ISS 허브를 부모로, 하위 step/comms를 서브 블렛으로 작성
> `- [x] [[ISS 허브]] 작업 요약 (PR #번호)`
>   `- [[step-NN-파일명]] 또는 [[comms/파일명]] 변경 내용`
> **독립 노트** (wiki·permanent 등): `- [x] [[노트]] 작업 내용 (PR #번호)`
> 미완료 항목도 `- [ ]`로 진행 중 작업 기록 가능

- [ ]

## 미완 작업 (GitHub Issues)

> 오픈 이슈 기준 — {YYYY-MM-DD}
> **미완료** `- [ ]`: 이슈 제목 + sub-bullet (범위·작업 항목)
> **완료** `- [x]`: 이슈 제목 한 줄만 — sub-bullet 제거 (상세는 작업 로그에)

{OPEN_ISSUES}

## 진행 중 WBS / 이슈

\`\`\`dataview
TABLE
  default(wbs-status, status) AS "상태",
  dateformat(file.mtime, "MM-dd") AS "최종수정"
FROM ""
WHERE file.folder != "_templates"
AND (
  (type = "wbs" AND wbs-status != "export")
  OR (type = "issue" AND status = "in-progress")
)
SORT type ASC, file.mtime DESC
\`\`\`

## 현재 작업 중 노트

\`\`\`dataview
TABLE
  file.link AS "노트",
  default(status, "-") AS "status",
  dateformat(file.mtime, "MM-dd HH:mm") AS "수정"
FROM ""
WHERE file.folder != "_templates"
AND file.name != "{YYYY-MM-DD}"
AND file.mtime >= date("{YYYY-MM-DD}")
AND file.mtime < date("{YYYY-MM-DD}") + dur(1 day)
AND (
  status = "in-progress"
  OR contains(file.tags, "#wip")
)
SORT file.mtime DESC
\`\`\`

## 처리할 것

inbox에서 프로젝트/영역/리소스로 이동할 메모:

-

## 오늘 작업한 노트

\`\`\`dataview
TABLE
  dateformat(file.ctime, "HH:mm") AS "생성",
  dateformat(file.mtime, "HH:mm") AS "수정",
  type
FROM ""
WHERE file.ctime >= date("{YYYY-MM-DD}") AND file.ctime < date("{YYYY-MM-DD}") + dur(1 day)
AND file.folder != "_templates"
AND file.name != "{YYYY-MM-DD}"
SORT file.ctime ASC
\`\`\`

## 회고

오늘 배운 것, 연결된 아이디어:

```

### Step 5: 커밋

```bash
git add 60-logs/daily/{YYYY}/{MM}/{YYYY-MM-DD}.md
git commit -m "docs: {YYYY-MM-DD} 데일리 노트 작성 (#{ISSUE_NUMBER})"
```

### Step 6: Push & PR 생성

```bash
git push -u origin feature/{ISSUE_NUMBER}-daily-{YYYY-MM-DD}

gh pr create \
  --repo SeokRae/knowledge-labs \
  --title "docs: {YYYY-MM-DD} 데일리 노트 작성" \
  --body "## Summary\n- {YYYY-MM-DD} ({요일}) 데일리 노트 생성\n\nCloses #{ISSUE_NUMBER}"
```

### Step 7: Obsidian에서 열기

Obsidian CLI가 사용 가능하면 생성된 노트를 Obsidian에서 바로 연다.

```bash
obsidian open path="60-logs/daily/{YYYY}/{MM}/{YYYY-MM-DD}.md" vault=sr-labs 2>/dev/null || true
```

> CLI 실패(Obsidian 미실행 등)해도 워크플로우에 영향 없음 — 무시하고 진행.

### Step 8: 완료 출력

```
✅ {YYYY-MM-DD} 데일리 노트 생성 완료

Issue : SeokRae/knowledge-labs#{ISSUE_NUMBER}
Branch: feature/{ISSUE_NUMBER}-daily-{YYYY-MM-DD}
PR    : SeokRae/knowledge-labs#{PR_NUMBER}
파일  : 60-logs/daily/{YYYY}/{MM}/{YYYY-MM-DD}.md
```

## Wiki Harvest (자동 트리거)

완료 출력 후 자동 실행. 회의록이 없거나 후보가 없으면 전체 생략.

1. **오늘 날짜 기준 회의록 스캔**
   ```bash
   find 20-areas -path "*/meetings/*.md" | xargs grep -l "{YYYY-MM-DD}" 2>/dev/null || true
   ls 20-areas/meetings/*{YYYY-MM-DD}*.md 2>/dev/null || true
   ```

2. **미처리 여부 확인** — `60-logs/ingest-log.md` 에서 해당 파일 경로 검색
   - 기록 없으면 → 미처리로 간주

3. **미처리 파일이 있으면 wiki 후보 추출** (Read 후 Grep)
   - **볼드 용어**: `\*\*Term\*\*` 패턴
   - Dangling wikilink: `\[\[링크\]\]`
   - H2/H3 개념 제목
   - 기존 `wiki-term: true` 노트와 중복이면 제외

4. **후보 제시 (1개 이상일 때만)**
   ```
   📎 미처리 회의록 N개 | wiki 후보: "용어A", "용어B" ...
   wiki 페이지 만들까요? [y/스킵]
   ```
   - `y` → `sr-obsidian:wiki scan {파일경로}` 호출
   - `스킵` / 후보 없음 / 회의록 없음 → 종료

## 판단 기준

| 상황 | 처리 |
|------|------|
| 파일이 이미 존재 | 갱신 모드로 전환 (덮어쓰지 않음) |
| 이전 데일리 노트 없음 | `## 전일 리마인드` 섹션 전체 생략 |
| 직전~어제 머지 PR 없음 | `### ✅ 어제 완료` = `- (없음)` |
| 이전 노트에 미완 항목 없음 | `### ⏭ 이어서 할 일` = `- (없음)` (어제 완료는 유지) |
| `docs: YYYY-MM-DD 데일리 노트 작성/갱신` 이슈 | 이월 및 미완 작업 섹션에서 제외 (이월 누적 방지) |
| 제목에 `(standing)` 마커가 있는 상시 이슈 | 이월·목표·미완 작업 섹션에서 제외 (완료 불가 이슈의 이월 누적 방지) |
| 날짜 형식 오류 | 오류 메시지 출력 후 중단 |
| gh 인증 실패 | 오류 메시지 출력 후 중단 |
| 이월 횟수 0회 | 횟수 태그 생략 (원본 항목 그대로 유지) |
| glob 실패 (daily 폴더 없음) | 이월 횟수 카운트 건너뜀, 항목만 출력 |
| 작업 로그에 기존 기록 있음 (G3.5) | placeholder 교체 건너뜀 — 기존 기록 보존 |
| 이월 항목 없음 (Step 1.6) | `{GOAL_ITEMS}` = `- [ ]` (빈 항목 유지) |

## validator 품질 지표 (내용 수준 측정)

생성·갱신 완료 후 `note_validator.py` 가 아래 **추가 지표**를 측정해 `evolution_log.jsonl`에 기록한다.
이 지표들은 **스킬 동작을 막지 않는다** — 측정·기록만 한다.

| 지표 | 측정 방법 | 목표값 |
|------|----------|--------|
| `goal_item_count` | `## 목표` 섹션의 `- [` 항목 수 | 1 이상 |
| `goal_issue_linked` | 목표 항목 중 `#NNN` 포함 비율 (0.0~1.0) | 0.5 이상 |
| `log_real_items` | 작업 로그에서 placeholder(`- [ ]` 단독 1줄) 제외 후 항목 수 | 1 이상 |
| `completion_rate` | 갱신 모드: 전날 `[ ]` 중 오늘 `[x]`로 전환된 비율 | 0.3 이상 |
| `carryover_reduction` | 전날 이월 수 - 오늘 이월 수 (음수 = 이월 증가) | 양수 권장 |
