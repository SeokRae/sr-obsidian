---
name: daily
description: >
  오늘 데일리 노트 생성·갱신 — GitHub Issue → 브랜치 → 노트 작성 → PR 자동화. 파일이 이미 있으면 갱신 모드로 전환.
  Do NOT use for 주간보고(목~수) → sr-obsidian:weekly.
  Do NOT use for 주말 회고·KPI 검토 → sr-obsidian:retro.
  Keywords: 데일리, daily, 오늘 노트, 일일 노트, 작업 로그, 갱신
allowed-tools: Bash, Read, Glob, Write, Edit
---

# 데일리 노트 생성·갱신 워크플로우

## 사용법

```
/daily             # 오늘 날짜 기준 생성 or 갱신
/daily 2026-04-01  # 특정 날짜 지정 (YYYY-MM-DD)
```

## 공통 규칙

- 날짜: `$ARGUMENTS` 있으면 해당 날짜, 없으면 오늘. 파일 경로 `60-logs/daily/{YYYY}/{MM}/{YYYY-MM-DD}.md`
- 파일이 **없으면 생성 모드, 있으면 갱신 모드** (기존 파일을 덮어쓰지 않는다)
- Issue·Branch·Commit·PR: [git-workflow](../../references/git-workflow.md) 표준 절차.
  **당일 데일리 이슈는 재사용** — `"{YYYY-MM-DD} 데일리 in:title"` 오픈 이슈 조회 후 있으면 그 번호 사용, 없을 때만 생성.
  하루 여러 번 실행돼도 이슈 1개로 수렴하고, PR `Closes #{N}`로 자동 종료된다 (open 누수 차단).
- **제외 규칙** (오픈 이슈 조회·이월 공통): 데일리 노트 자체 이슈(`docs: YYYY-MM-DD 데일리 노트 작성/갱신` 패턴),
  제목에 `(standing)` 마커가 있는 상시 이슈. 둘 다 이월·목표·미완 작업 섹션에서 제외 (이월 누적 방지)
- 날짜 형식 오류·gh 인증 실패 시 오류 출력 후 중단

---

## 갱신 모드

### G1. 오픈 이슈 + 하위 작업 추출

```bash
python3 _scripts/daily/collect.py open-issues
```

**종료 후보 감지**: '열려 있음'과 '실제 미완료'는 다르다 — 완료됐는데 종료 신호만 누락된 이슈를 분리 표시한다.

- **GH 이슈**: 머지된 PR이 `#N`을 참조하면 `⚠️ 종료 후보`

  ```bash
  for N in {오픈이슈번호들}; do
    M=$(gh pr list --repo SeokRae/knowledge-labs --state merged \
          --search "$N in:body" --json number --jq '.[0].number' 2>/dev/null)
    [ -n "$M" ] && echo "#$N ⚠️ 종료 후보 (머지 PR #$M 참조·미종료)"
  done
  ```

- **ISS 이슈(vault)**: `10-projects/ISS-*/steps/` 전부 `end-date` 세팅인데 hub `status`가 `done`/`closed`가 아니면 `⚠️ 종료 후보`

출력을 `{OPEN_ISSUES_WITH_STEPS}`로 저장 (종료 후보는 상단 분리).

### G2. 브랜치

현재 브랜치가 `feature/*-daily-{YYYY-MM-DD}` 형식이면 그대로 사용.
아니면 git-workflow 절차로 당일 갱신 이슈 재사용·생성 후 `feature/{N}-daily-{YYYY-MM-DD}-update` 분기.

### G3. 미완 작업 섹션 갱신

**절대 전체 교체 금지.** 기존 이슈 항목의 상세 sub-bullet(주제/목적/문제현황/해결방안/미결 등)은 반드시 보존한다.
G1 결과에서 **신규 이슈만** 추출해 `## 미완 작업 (GitHub Issues)` 섹션 첫 항목으로 Edit 삽입. 신규가 없으면 건너뜀.

### G3.5. 작업 로그 자동 제안

작업 로그 섹션이 `- [ ]` placeholder일 때만 실행 — 기존 기록이 있으면 보존하고 건너뜀.
소스는 **그날 머지된 PR 전량** (로컬 `git log --since`는 체크아웃·pull 상태에 좌우되므로 사용 금지). KST 경계 명시:

```bash
gh pr list --repo SeokRae/knowledge-labs --state merged \
  --search "merged:{YYYY-MM-DD}T00:00:00+09:00..{YYYY-MM-DD}T23:59:59+09:00" \
  --limit 100 --json number,title \
  --jq '.[] | select(.title | test("데일리 노트|ingest") | not) | "- [x] \(.title) (PR #\(.number))"'
```

출력 각 줄로 placeholder를 Edit 교체. 머지 PR 없으면 건너뜀.

### G4~G5. 마무리

git-workflow 절차로 커밋(`docs: {YYYY-MM-DD} 데일리 노트 갱신 (#{N})`)·Push 후 완료 출력 (파일·브랜치).

---

## 생성 모드

### 1. 전일 데이터 수집

직전 노트: 같은 달 폴더에서 오늘 이전 최신 파일, 없으면 이전 달 폴더 확인. 파일명 날짜를 `{PREV_DATE}`로.

```bash
python3 _scripts/daily/collect.py carryover "{PREV_NOTE_PATH}"        # 이월 항목 + 최근 30개 노트 이월 횟수 태그
YESTERDAY=$(date -j -v-1d -f "%Y-%m-%d" "{YYYY-MM-DD}" "+%Y-%m-%d")
python3 _scripts/daily/collect.py done-prs "{PREV_DATE}" "$YESTERDAY" # 직전~어제 머지 PR (KST 경계, 데일리·ingest 제외)
```

→ `{CARRIED_ITEMS}` (없으면 빈 문자열), `{PREV_DONE_PRS}` (없으면 `- (없음)`).
직전 노트가 금요일이면 주말 머지분까지 자연 포함된다.

### 2. 오늘 목표 자동 제안

`{CARRIED_ITEMS}`에서 이월 횟수 상위 2개 → `{GOAL_ITEMS}` (없으면 `- [ ]`).
`⚠️ 재검토` 태그 항목엔 `(재검토 or 폐쇄 결정)` 주석 추가. 동률이면 최신 이슈 우선.

### 3. Issue·Branch

git-workflow 절차 — 제목 `docs: {YYYY-MM-DD} 데일리 노트 작성`, 브랜치 `feature/{N}-daily-{YYYY-MM-DD}`.

### 4. 노트 작성

[template.md](references/template.md) 형식으로 Write. 섹션 구성 규칙(리마인드 생략 조건 포함)도 같은 파일 참조.
오픈 이슈 조회는 G1과 동일하게 `collect.py open-issues` 실행.

### 5~7. 마무리

git-workflow 절차로 커밋·Push·PR 생성 후, Obsidian에서 열기(실패해도 무시):

```bash
obsidian open path="60-logs/daily/{YYYY}/{MM}/{YYYY-MM-DD}.md" vault=sr-labs 2>/dev/null || true
```

완료 출력: Issue·Branch·PR·파일 경로.

---

## Wiki Harvest (자동 트리거)

완료 출력 후 자동 실행 — [wiki-harvest](../../references/wiki-harvest.md) 공통 절차, 스캔 범위 = **오늘 날짜**.

## validator 품질 지표

생성·갱신 후 자동 측정되는 내용 수준 지표 — [validator-metrics.md](references/validator-metrics.md) 참조 (스킬 동작을 막지 않음).
