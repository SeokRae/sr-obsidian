---
name: radar
description: >
  외부 웹에서 주제(기본: Claude Code · AI 에이전트) 최신 정보를 수집해 ① 60-logs/radar/ 날짜별 수집 로그 ② 30-resources/ wiki-term 노트 2갈래로 누적. "레이더", "radar", "동향 수집", "최신 정보 수집", "claude code 동향" 요청 시 사용.
  Do NOT use for 단일 URL 클리핑 → sr-obsidian:defuddle.
  Do NOT use for wiki 품질·연결 검사 → sr-obsidian:lint-wiki.
  Do NOT use for vault 내부 노트 용어 추출 → sr-obsidian:wiki scan.
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

## 링크 규칙 (#8607 D6)

radar가 `[[ ]]`를 쓰는 모든 자리에 적용합니다: 미리보기의 갱신 목록, 수집 로그 본문과 `## 위키 반영`, wiki-term 노트의 MOC 역링크와 `## 관련 메모`, fan-out 역링크, MOC 등재, wiki-index 행, ingest-log 기록.

- **형식은 `[[{파일명}|{용어명}]]`**: 파일명은 대상 노트의 실제 파일명에서 `.md`를 뺀 값이에요. radar 노트는 파일명이 영문 slug이고 H1이 한글 용어명이라 둘이 거의 늘 다릅니다. 예: `[[block-reads-outside-working-dirs|작업 디렉토리 밖 읽기 차단]]`
- **H1 제목이나 `aliases`로 링크 금지**: Obsidian은 파일명과 경로로만 링크를 해석해요. `[[작업 디렉토리 밖 읽기 차단]]`처럼 제목이나 alias를 대상으로 쓰면 미해소로 남습니다. 제목이나 alias로 노트를 찾았더라도 링크는 그 노트의 파일명으로 겁니다. `WIKI_DIR` 노트는 Phase 1 Step 1에서 짝지어 둔 파일명을 쓰고, 그 밖의 노트는 Glob이나 grep으로 실제 파일 경로를 확인해요.
- **표 셀 안에서는 `\|`**: `| [[{파일명}\|{용어명}]] |`로 씁니다. 이스케이프하지 않은 파이프는 표 구분자로 읽혀 링크가 색인되지 않아요.
- **같은 파일명이 둘 이상이면 경로형**: `[[{vault 기준 경로(.md 제외)}|{표시명}]]`. 날짜 로그 `{TODAY}.md`는 데일리 노트와 파일명이 같아서 항상 경로형으로 겁니다.
- **선행 링크 금지**: 커밋 시점에 없는 노트에는 `[[ ]]`를 걸지 않아요. 로그 전용 항목, 승격하지 않은 후보, 하루 5건 한도로 다음 회차에 넘긴 후보는 평문으로 적습니다. MOC 역링크도 실재하는 MOC에만 겁니다.
- **커밋 전 해소 확인**: Phase 2 Step 4를 마치면 [obsidian-markdown](../../references/obsidian-markdown.md)의 `링크 해소 확인`을 이번 회차에 쓰거나 고친 파일에 돌려 `미해소 0건`을 확인해요.

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

기존 wiki-term 노트마다 파일명(`.md` 제외), H1 제목, aliases, 출처 URL을 짝지어 메모해 둡니다. Step 3 대조에 쓰고, Phase 2에서 링크를 걸 때는 이 파일명을 대상으로 써요(§링크 규칙).

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
- [[{파일명}|{용어명}]] ← {무엇이 바뀜} ({url})

**로그 전용** (K건)
- {항목} ({url})

> 진행할 항목을 선택하세요. (예: "1,2 + 갱신 전체" / "전체" / "로그만")
```

**`--dry-run`이면 여기서 종료.** 스케줄러 자동 실행 시에는 승인 없이 "전체"로 진행한다 (§자동 실행 모드).

---

## Phase 2: 파일링 (WRITE)

### Step 1. GitHub Issue + 브랜치

[git-workflow](../../references/git-workflow.md) 표준 절차 적용 —
제목 `docs: radar {TOPIC} 수집 — {TODAY}`, 브랜치 `feature/{issue번호}-radar-{TODAY}`.
git 명령은 `git -C "$VAULT"` 로 실행.

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
- 신규: [[{파일명}|{용어명}]]
- 갱신: [[{파일명}|{용어명}]]
```

자료가 없는 범위 섹션은 `- (신규 없음)` 으로 남긴다.
본문 항목에서 wiki-term 노트를 가리킬 때도 `[[{파일명}|{용어명}]]`로 씁니다. `## 위키 반영`에는 Step 3에서 실제로 만들거나 고친 노트만 적고, 승격하지 않은 항목은 넣지 않아요(§링크 규칙).

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

← [[Claude Code MOC]]
```

MOC 역링크는 실재하는 MOC 파일명으로 겁니다. 기본 주제는 `50-moc/Claude Code MOC.md`이고, 주제를 바꿨는데 맞는 MOC가 없으면 이 줄을 생략해요.

**갱신** — 기존 노트 Read 후, 변경분만 해당 섹션에 Edit 추가하고 `source:`에 새 URL 보강.

**Fan-out**: 관련 노트의 `## 관련 메모`에 새 노트를 `[[{새 노트 파일명}|{용어명}]]`으로 삽입해 위키 그래프를 잇습니다. 새 노트의 `## 관련 메모`에 기존 노트를 적을 때도 그 노트의 파일명으로 걸고, H1 제목을 옮겨 적지 않아요(§링크 규칙).

### Step 4. 인덱스 + ingest-log 갱신

- `50-moc/wiki-index.md` 정적 테이블에 신규 노트 행 추가. 해당 섹션의 기존 열 구성을 따르고, 용어 열은 `[[{파일명}\|{용어명}]]`로 씁니다.
- `60-logs/ingest-log.md` 말미에 append:

```
## [{TODAY}] radar | {TOPIC}
- 로그: [[60-logs/radar/{YYYY}/{MM}/{TODAY}|{TODAY} radar 로그]]
- 신규: [[{파일명1}|{용어명1}]], [[{파일명2}|{용어명2}]]
- 갱신: [[{파일명3}|{용어명3}]]
- 출처: {N}건 웹 수집
```

**링크 해소 확인**: 커밋 전에 [obsidian-markdown](../../references/obsidian-markdown.md)의 `링크 해소 확인`을 돌립니다. 대상은 Step 2~4에서 쓰거나 고친 파일 전부(날짜 로그, 신규와 갱신 wiki-term 노트, fan-out한 관련 노트, 등재한 MOC 파일, `wiki-index.md`, `ingest-log.md`)의 절대 경로예요. `미해소 0건`이 아니면 §링크 규칙대로 고친 뒤 다시 돌리고, 통과해야 Step 5로 갑니다. `검증 불가`(exit 2)는 링크 문제가 아니니 노트는 두고 vault 경로와 파일 인자를 바로잡아 다시 돌려요.

### Step 5. 커밋 + PR

[git-workflow](../../references/git-workflow.md) 표준 절차의 커밋·PR 단계 적용 —
커밋 `docs: radar {TOPIC} 수집 {TODAY} (#{issue번호})`, PR body `Closes #{issue번호}`.

### Step 6. 완료 출력

**종료 게이트**: `git -C "$VAULT" status --short` 가 비어있지 않으면(Step 2~4에서 쓴 파일이 아직 미커밋) 완료로 보고하지 않고 Step 5로 돌아가 커밋·PR까지 마친다.

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
- 실패(네트워크·gh·git) 시에도 **이미 Write한 파일은 반드시 커밋·PR까지 완료**한 뒤 원인을 보고한다 — 파일만 남기고 중단 금지. 이전 회차 미커밋 잔여가 있으면 이번 회차분과 함께 정리한다.

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
