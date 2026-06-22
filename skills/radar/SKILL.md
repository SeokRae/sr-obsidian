---
name: radar
description: >
  외부 웹에서 특정 주제(기본: Claude Code · AI 에이전트)의 최신 정보를 주기적으로 수집해
  vault 위키로 점진 누적한다. 웹 검색 → 기존 위키·ingest-log 대조로 신규 정보만 추출 →
  ① 60-logs/radar/ 날짜별 수집 로그(원본·출처·날짜) ② 30-resources/{카테고리}/ wiki-term 노트
  2갈래로 파일링. 기존 wiki·lint-wiki·Dataview·index 인프라와 완전 호환. 스케줄러로 매일 자동 실행 설계.
  "레이더", "radar", "최신 정보 수집", "동향 수집", "위키 업데이트", "claude code 동향" 요청 시 사용.
  Do NOT use for 단일 URL 클리핑 (use sr-obsidian:defuddle).
  Do NOT use for wiki 품질·연결 검사 (use sr-obsidian:lint-wiki).
  Do NOT use for vault 내부 노트로부터의 용어 추출 (use sr-obsidian:wiki scan — wiki는 내부 스캔, radar는 외부 웹 수집).
  Keywords: radar, 레이더, 동향 수집, 최신 정보, 위키 누적, claude code, agentic, 에이전트
allowed-tools: WebSearch, WebFetch, Bash, Read, Glob, Grep, Write, Edit
---

# sr-obsidian:radar — 외부 정보 레이더 (웹 수집 → 위키 누적)

> **참조**: [Karpathy — LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
> "지식은 매 쿼리마다 재발견되지 않고 한 번 컴파일된 뒤 축적된다."
>
> `wiki` 스킬이 **vault 내부 노트**에서 용어를 추출한다면, `radar`는 **외부 웹**에서 새 정보를
> 가져와 같은 위키 인프라(`wiki-term`, `ingest-log`, `wiki-index`)에 누적한다.

## 사용법

```
/sr-obsidian:radar                          # 기본 주제(Claude Code·AI 에이전트) 일일 수집
/sr-obsidian:radar "MCP 프로토콜"            # 주제 지정 수집
/sr-obsidian:radar --dry-run                # Phase 1만 (READ-ONLY, 미리보기)
```

## 핵심 원칙

- **신규만 누적**: 매 실행마다 기존 위키/로그를 먼저 읽고, 이미 있는 내용은 추가하지 않는다 (중복·노이즈 방지).
- **2갈래 파일링**: 원본은 날짜 로그(`60-logs/radar/`), 정제 지식은 wiki-term 노트(`30-resources/`).
- **출처·날짜 필수**: 모든 항목에 출처 URL과 수집 날짜 기록 — 신뢰성 + 중복 차단의 근거.
- **기존 인프라 재사용**: wiki-term 노트는 `type:permanent` + `wiki-term:true` — lint-wiki·Dataview·wiki-index 그대로 적용.
- **Phase 1 READ-ONLY**, Phase 2부터 WRITE.
- **vault 콘텐츠 PR은 `SeokRae/knowledge-labs`** 리포로 (플러그인 리포 `sr-obsidian` 아님).

## 변수

```bash
VAULT="/Users/sr/obsidian/sr-labs"
REPO="SeokRae/knowledge-labs"
TOPIC="${ARGUMENTS:-Claude Code · AI 에이전트}"
TODAY=$(date +%Y-%m-%d); YYYY=$(date +%Y); MM=$(date +%m)
LOG="$VAULT/60-logs/radar/$YYYY/$MM/$TODAY.md"
WIKI_DIR="$VAULT/30-resources/ai/claude-code"   # 카테고리/주제 — 주제 변경 시 조정
```

## 수집 범위 (기본 주제)

| 범위 | 검색 키워드 예시 | 권위 출처 |
|------|----------------|----------|
| Claude Code 기능·업데이트 | `Claude Code changelog`, `Claude Code new feature`, `slash command`, `hooks`, `MCP` | docs.claude.com, github releases |
| 에이전트 설계 패턴 | `agentic workflow`, `multi-agent`, `subagent`, `best practices agent` | anthropic engineering blog |
| 커뮤니티·생태계 | `Claude Code plugin`, `awesome claude code`, `open source agent tool` | github, 블로그·튜토리얼 |
| Anthropic 공식 발표 | `Anthropic announcement`, `Claude model release`, `API change` | anthropic.com/news, docs |

---

## Phase 1: 수집 + 대조 (READ-ONLY)

### Step 1. 기존 상태 로드 (중복 방지의 핵심)

```bash
# 이미 다룬 주제 — wiki-index + ingest-log + 최근 radar 로그
cat "$VAULT/50-moc/wiki-index.md" 2>/dev/null
tail -100 "$VAULT/60-logs/ingest-log.md" 2>/dev/null
ls "$VAULT/60-logs/radar/$YYYY/$MM/" 2>/dev/null
grep -rl "wiki-term: true" "$WIKI_DIR" 2>/dev/null
```

기존 wiki-term 노트 제목·aliases·출처 URL을 메모해 둔다 → Step 3 대조에 사용.

### Step 2. 웹 검색 (범위별)

각 범위마다 `WebSearch` 실행. 최신순 우선, **최근 1~2주** 신규 항목에 집중.
유망 결과는 `WebFetch`(또는 defuddle)로 본문 확인. 1차 출처(공식 docs·릴리즈·엔지니어링 블로그) 우선.

### Step 3. 신규 판정 + 분류

수집 항목을 기존 상태와 대조:

| 판정 | 처리 |
|------|------|
| 기존 wiki-term/로그에 이미 있음 | 스킵 |
| 기존 내용의 **갱신**(버전·변경) | 해당 wiki-term 노트 갱신 대상 |
| 완전 **신규 개념** | 새 wiki-term 노트 후보 |
| 위키화엔 약하지만 기록 가치 있음 | 날짜 로그에만 기록 |

각 신규 개념은 **유형 판별** (wiki 스킬과 동일):
`architecture`(A vs B 비교) / `metric`(지표·공식) / `principle`(동작 원리) / `technology`(기본값).

### Step 4. 미리보기 출력

```
### 📡 Radar — {TOPIC} ({TODAY})

**신규 wiki-term 후보** (N건)
| # | 용어 | 유형 | 한줄 정의 | 출처 |
|---|------|------|----------|------|
| 1 | {용어} | technology | {정의} | {url} |

**기존 노트 갱신** (M건)
- [[{노트}]] ← {무엇이 바뀜} ({url})

**로그 전용** (K건)
- {항목} ({url})

> 진행할 항목을 선택하세요. (예: "1,2 + 갱신 전체" / "전체" / "로그만")
```

**`--dry-run`이면 여기서 종료.** 스케줄러 자동 실행 시에는 승인 없이 "전체"로 진행한다 (§자동 실행 모드).

---

## Phase 2: 파일링 (WRITE)

### Step 1. GitHub Issue + 브랜치

```bash
gh issue create --repo "$REPO" \
  --title "docs: radar {TOPIC} 수집 — {TODAY}" \
  --body "radar 일일 수집: 신규 N건, 갱신 M건, 로그 K건"
git -C "$VAULT" checkout main && git -C "$VAULT" pull origin main
git -C "$VAULT" checkout -b "feature/{issue번호}-radar-{TODAY}"
```

### Step 2. ① 날짜별 수집 로그 작성 (원본 보존)

`60-logs/radar/{YYYY}/{MM}/{TODAY}.md` 를 Write:

```markdown
---
type: log
created: {TODAY}
source: radar
topic: {TOPIC}
tags: [radar, {주제-slug}]
---

# 📡 Radar 수집 — {TOPIC} ({TODAY})

## Claude Code 기능·업데이트
- **{제목}** — {1~2줄 요약} ([출처]({url}), {게시일})

## 에이전트 설계 패턴
- ...

## 커뮤니티·생태계
- ...

## Anthropic 공식 발표
- ...

## 위키 반영
- 신규: [[{wiki-term 노트}]]
- 갱신: [[{wiki-term 노트}]]
```

자료가 없는 범위 섹션은 `- (신규 없음)` 으로 남긴다.

### Step 3. ② wiki-term 노트 생성·갱신 (정제 지식)

**신규** — `30-resources/ai/claude-code/{용어-slug}.md` 를 `tpl-wiki-term` 형식으로 생성
(유형별 3섹션 구조는 `wiki` 스킬의 "Wiki 페이지 생성 형식" 참조). 프론트매터:

```markdown
---
type: permanent
wiki-term: true
answer-type: {technology|architecture|principle|metric}
created: {TODAY}
source: {원본 URL}          # radar 고유 — 외부 출처 추적
tags: [claude-code, wiki-term]
aliases: [{영문 약어}, {풀네임}]
---

# {용어명}

> **한 줄 정의**: {한 문장}

← [[AI 에이전트 MOC]]
```

**갱신** — 기존 노트 Read 후, 변경분만 해당 섹션에 Edit 추가하고 `source:`에 새 URL 보강.

**Fan-out**: 관련 노트의 `## 관련 메모`에 `[[역링크]]` 삽입 → 위키 그래프 연결.

### Step 4. 인덱스 + ingest-log 갱신

- `50-moc/wiki-index.md` 정적 테이블에 신규 노트 행 추가.
- `60-logs/ingest-log.md` 말미에 append:

```
## [{TODAY}] radar | {TOPIC}
- 로그: [[60-logs/radar/{YYYY}/{MM}/{TODAY}.md]]
- 신규: [[{노트1}]], [[{노트2}]]
- 갱신: [[{노트3}]]
- 출처: {N}건 웹 수집
```

### Step 5. 커밋 + PR

```bash
git -C "$VAULT" add -A
git -C "$VAULT" commit -m "docs: radar {TOPIC} 수집 {TODAY} (#{issue번호})"
git -C "$VAULT" push -u origin HEAD
gh pr create --repo "$REPO" \
  --title "docs: radar {TOPIC} 수집 — {TODAY}" --body "Closes #{issue번호}"
```

### Step 6. 완료 출력

```
✅ Radar 수집 완료 — {TOPIC} ({TODAY})
신규 wiki-term: N건 / 갱신: M건 / 로그: K건
PR: {url}
```

---

## 자동 실행 모드 (스케줄러)

스케줄러가 호출하면 사용자 승인 단계 없이 Phase 1 → Phase 2를 끝까지 진행한다. 규칙:

- 신규 후보가 **0건이면** 파일·PR을 만들지 않고 "오늘 신규 없음"만 보고 (빈 PR 금지).
- wiki-term 승격은 **신뢰 가능한 1차 출처**가 있을 때만. 출처 불명·추측성 정보는 로그에도 넣지 않는다.
- 하루 wiki-term 신규는 **최대 5건**으로 제한 (품질 우선, 나머지는 로그에 남겨 다음 회차 후보).
- 실패(네트워크·gh·git) 시 부분 결과를 로그로 남기고 원인을 보고한다.

### 사전 조건 (스케줄러 실행 환경)

| 필요 | 확인 |
|------|------|
| vault 폴더 접근 | `$VAULT` 경로 마운트/접근 가능 |
| git + gh 인증 | `gh auth status`, vault가 `$REPO` 클론본 |
| 웹 검색 | WebSearch 사용 가능 |

조건 미충족 시 작업을 중단하고 무엇이 빠졌는지 명확히 보고한다.

## 판단 기준

| 상황 | 처리 |
|------|------|
| 동일 URL이 기존 로그/노트의 `source:`에 있음 | 중복 — 스킵 |
| 검색 결과가 1차 출처 없이 블로그 추측뿐 | 로그에도 넣지 않음, "확인 필요"로만 메모 |
| 같은 개념이 여러 출처에 등장 | 가장 권위 있는 출처를 source로, 나머지는 본문 참고 링크 |
| wiki-term인지 단순 뉴스인지 모호 | 기술사 4유형으로 정의 가능하면 wiki-term, 아니면 로그 전용 |
| 주제가 기본값과 다름 (`$ARGUMENTS` 지정) | `WIKI_DIR` 카테고리/주제 경로를 그 주제에 맞게 조정 |
