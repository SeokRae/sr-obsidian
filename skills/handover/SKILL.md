---
name: handover
description: >
  누적된 기록(steps·comms·ADR·설계문서·daily·PR)을 종합해 "요건이 어떻게 확정됐고, 어떻게 작업해왔고, 무엇을 고민했고, 지금 무엇이 남았는지"를 서사로 복원하는 인수인계 문서 생성.
  ISS-NNN · FT-NNN · 서비스 영역 셋 다 지원하며, 대상 폴더에 summary 노트로 남기고 Issue→Branch→PR까지 자동화.
  "인수인계", "인계 문서", "히스토리 정리", "그동안 어떻게 진행됐는지", "경위 정리", "이거 넘겨받아야 하는데", "배경 파악", "onboarding 문서", "handover" 요청 시 즉시 사용.
  후속 요청도 이 스킬 — "인계 문서 갱신", "다시 정리", "최근 것만 추가", "미결 항목만 다시".
  Do NOT use for ADR·회의록 등 결정 발생 시점의 단건 기록 (use sr-obsidian:history — handover는 축적된 기록의 사후 종합, history는 그 시점의 기록 생성).
  Do NOT use for 현재 상태 스냅샷·링크·KPI 갱신 (use sr-obsidian:hub — handover는 경위 서사, hub는 현황 스냅샷).
  Do NOT use for 노트 검색·목록 반환 (use sr-obsidian:search — handover는 종합 문서 생성, search는 검색 결과 반환).
  Do NOT use for 주간·일간 작업 집계 (use sr-obsidian:weekly / sr-obsidian:daily).
  Keywords: 인수인계, 인계, handover, 히스토리, 경위, 배경, 넘겨받다, 온보딩, summary, 그동안
allowed-tools: Bash, Read, Glob, Grep, Write, Edit, Agent
---

# 인수인계 문서 생성 워크플로우

## 사용법

```
/handover ISS-119            # 인시던트 1건
/handover FT-001             # 기능 1건 (서비스 중복 시 되물음)
/handover payment-psp        # 서비스 영역 전체
/handover 20-areas/payment/psp   # 경로 직접 지정
```

## 이 스킬이 만드는 것

`type: summary` 노트다. vault에는 이미 ISS 일부에 `ISS-NNN summary.md`(배경 → 경과 → 현재 상태)가 있고, 이 스킬은 **그 포맷을 그대로 쓴다**. 새 포맷을 만들면 같은 내용의 문서가 둘로 갈라져 갱신 주체가 어긋나기 때문이다. 인수인계에만 필요한 `## 인계 시 알아야 할 것` 섹션만 덧붙인다.

vault 커버리지가 갭이다 — ISS는 일부만 summary가 있고, FT·서비스 영역에는 아예 없다. 그 빈자리를 채우는 것이 이 스킬의 주 무대다.

## Phase 0: 컨텍스트 확인 (READ-ONLY)

1. 대상 폴더에 기존 summary 노트가 있는지 확인한다.

   ```bash
   ls {대상폴더}/*summary*.md 2>/dev/null
   ```

2. 실행 모드를 정한다.

| 상황 | 모드 | 처리 |
|------|------|------|
| summary 없음 | **초기 생성** | 전 범위 수집 → 신규 작성 |
| summary 있음 + 사용자가 갱신 요청 | **갱신** | 기존 본문을 **입력으로 읽고**, `updated` 이후 사건만 수집해 이어붙임. 기존 서술은 사실이 바뀐 경우에만 수정 |
| summary 있음 + 특정 섹션만 요청 | **부분 갱신** | 해당 축만 수집(예: 미결만 → `open-items`), 나머지 섹션은 손대지 않음 |

기존 summary를 통째로 다시 쓰지 않는 이유: 그 문서는 `sr-obsidian:iss` 등이 진행 중 갱신해온 살아있는 기록이고, 재생성하면 그동안 사람이 손으로 다듬은 맥락이 날아간다.

## Phase 1: 대상 판별 (READ-ONLY)

인자에서 대상 유형과 수집 범위(`scope`)를 산출한다.

| 유형 | 탐색 | scope |
|------|------|-------|
| `ISS-NNN` | `10-projects/ISS-NNN-*` → 없으면 `40-archives/ISS-NNN-*` | 해당 폴더 전체 (허브·WBS·`steps/`·`comms/`) |
| `FT-NNN` | `20-areas/*/*/features/FT-NNN *` · `20-areas/*/features/FT-NNN *` | 해당 FT 폴더 + `timeline.md` |
| 서비스 | `20-areas/{...}/{name}` (허브 `* 프로젝트 현황.md` 보유 폴더) | 서비스 루트 + `docs/` + `features/` + `phases/` + **링크된 ISS 폴더** |

```bash
cd /Users/sr/obsidian/sr-labs
ls -d 10-projects/ISS-119-* 40-archives/ISS-119-* 2>/dev/null
```

서비스 대상일 때 링크된 ISS는 허브 노트의 ISS 링크와 역참조로 찾는다.

```bash
grep -rl "{서비스 키워드}" 10-projects/ISS-*/ 40-archives/ISS-*/ --include="*.md" 2>/dev/null | sed 's|/[^/]*$||' | sort -u
```

**후보가 2개 이상이거나 0개면 진행하지 말고 되묻는다.** 엉뚱한 대상으로 문서를 만들면 인계받는 사람이 잘못된 배경을 사실로 학습한다.

## Phase 2: 수집 (READ-ONLY)

scope의 파일 수로 방식이 갈린다.

```bash
find {scope} -name "*.md" | wc -l
```

### 2-A. 30개 미만 — 인라인 수집

호출자가 직접 Read/Grep한다. 에이전트를 띄우는 왕복 비용이 이득을 넘는다.

### 2-B. 30개 이상 — `handover-collector` 3-way 팬아웃

서비스 영역은 문서·기능·연결 ISS를 합쳐 수백 개가 되어 한 컨텍스트에 담기지 않는다. 세 축을 한 응답에서 나란히 띄운다.

```
Agent(handover-collector, model: "opus", run_in_background: false) × 3
  - axis: timeline     — 무슨 일이 언제
  - axis: decisions    — 무엇을 고민했고 왜 그렇게 정했나 (미결 논의 포함)
  - axis: open-items   — 지금 남은 것·지뢰 (ready/in-progress step, applicable:false+na-reason, 미발송 draft)
```

**`run_in_background: false`로 띄운다.** Phase 3은 3축이 모두 있어야 시작할 수 있어 백그라운드로 겹칠 작업이 없다 — 이득이 없는 대신 수집기가 결과를 반환하지 않고 유휴 상태로 방치되는 실패 모드만 생긴다(sr-obsidian#153).

각 호출 프롬프트에 `scope`(경로 목록) · `axis` · `label`을 명시한다. 세 축은 서로 통신하지 않는다 — 같은 파일을 다른 축으로 읽을 뿐이라 교차 조율의 이득이 없고, 중복은 Phase 3에서 호출자가 해소한다.

**수집기가 빈 결과를 돌려주면 1회 재시도하고, 재실패 시 그 축을 버리지 말고 호출자가 인라인으로 직접 수집한다.** 축을 통째로 누락시키면 인계 문서에 구멍이 남는데, 실제 실패 사례(ISS-083, md 39개)에서 인라인으로 전량 복구가 가능했다. 인라인 대체가 물리적으로 불가능할 만큼 범위가 클 때만 축 없이 진행하고, 그 경우 **초안과 최종 문서에 누락을 명시한다**.

### 2-C. 공통 보강 — git·PR

두 방식 모두 마지막에 수행한다. vault 노트에 안 남은 작업이 커밋 메시지에는 남아 있다.

```bash
cd /Users/sr/obsidian/sr-labs && git log --oneline --grep="{label}" | head -50
gh pr list --repo SeokRae/knowledge-labs --state merged --search "{label}" --limit 30 \
  --json number,title,mergedAt --jq '.[] | "\(.mergedAt[0:10]) #\(.number) \(.title)"'
```

## Phase 3: 초안 제시 (READ-ONLY)

수집 결과를 종합해 초안을 출력한다. **서사 작성은 여기서 호출자가 직접 한다** — 수집기가 각자 쓰면 문서의 목소리가 세 개가 된다.

```
### 📋 {label} 인수인계 초안

**수집 범위**: 노트 {N}개 · 커밋 {N}건 · PR {N}건 | 방식: {인라인 | 팬아웃 3축}
**모드**: {초기 생성 | 갱신 | 부분 갱신}

--- 배경 ---
{왜 시작됐는지 2~4문장}

--- 경과 (시간순) ---
- {날짜} — {사건} ({근거 파일})
...

--- 검토한 선택지 ---
| 시점 | 결정/논의 | 대안 | 상태 |

--- 현재 상태 ---
{지금 어디까지 왔는지 2~3문장}

--- 인계 시 알아야 할 것 ---
| 항목 | 유형 | 상태·사유 | 출처 |

--- ⚠️ 근거 없는 구간 ---
- {기록이 비어 서술 못 한 부분}

출력 경로: {경로}
수정할 내용이 있으면 알려주세요. "저장" 입력 시 작성합니다.
```

`⚠️ 근거 없는 구간`이 비어 있어도 섹션은 남긴다. 이 문서를 읽는 사람이 "기록이 없어서 모르는 것"과 "확인해서 없는 것"을 구분해야 하기 때문이다.

## Phase 4: 작성 (WRITE)

사용자가 "저장" 또는 수정 확인 후 실행한다.

1. **출력 경로 결정**

| 대상 | 경로 |
|------|------|
| ISS | `{ISS폴더}/ISS-NNN summary.md` |
| FT | `{FT폴더}/FT-NNN summary.md` |
| 서비스 | `20-areas/{...}/{서비스}/{project-id} summary.md` |

   서비스는 형제 파일(`{project-id} WBS.md` · `{project-id} 프로젝트 현황.md`)의 명명을 따른다.

2. **Issue 생성**

   ```bash
   gh issue create --repo SeokRae/knowledge-labs \
     --title "docs: {label} 인수인계 문서 작성" \
     --body "## Summary
- {label} 누적 기록 종합 → 경위·결정·미결 정리
- 파일: \`{출력경로}\`"
   ```

3. **브랜치 생성** — main에서만 딴다. 직전 작업 브랜치에 머문 상태로 `-b` 하면 체인 분기가 된다.

   ```bash
   git checkout main && git pull origin main
   git branch --show-current      # main 확인 후에만 다음 줄 실행
   git checkout -b feature/{N}-handover-{label}
   ```

4. **노트 작성** — 아래 형식. 갱신 모드면 Edit로 해당 섹션만 손댄다.

5. **커밋 & PR**

   ```bash
   git add "{출력경로}"
   git diff --cached --name-only      # 의도한 파일만 staged 인지 확인
   git commit -m "docs: {label} 인수인계 문서 작성 (#{N})"
   git push -u origin feature/{N}-handover-{label}
   gh pr create --repo SeokRae/knowledge-labs \
     --title "docs: {label} 인수인계 문서 작성" --body "Closes #{N}"
   ```

6. **완료 출력** — Issue·Branch·PR·파일 경로, 그리고 근거 없는 구간 건수.

## 노트 형식

```markdown
---
type: summary
created: {최초 작성일}
updated: {TODAY}
tags: [summary, handover]
{incident: ISS-NNN | feature: FT-NNN | project: {project-id}}
---

# {label} 요약 (히스토리)

← [[{허브 노트}]]

> **목적**: 이 {인시던트|기능|프로젝트}가 어떤 배경에서 시작돼 어떻게 흘러왔고 지금 어디까지 왔는지 서사로 파악한다.
> 기록이 쌓일 때마다 갱신한다. 완료/미완 체크가 아니라 맥락·흐름을 서술한다.

## 배경

{왜 시작됐는지. 최초 요구가 무엇이었고 어떤 제약에서 출발했는지.}

## 요건 확정 경위

{초기 요구 → 변경 → 확정. 변경이 있었다면 무엇이 트리거였는지 근거와 함께.}

## 경과 (시간순 서사)

- {날짜} — {무엇을 했고 그 결과 무엇이 밝혀졌는지} ([[근거 노트]], PR #{번호})

## 검토한 선택지

| 시점 | 결정/논의 | 검토된 대안 | 근거 | 상태 |
|------|----------|-----------|------|------|
| | | | | 확정/미결/번복 |

## 현재 상태

{지금 어디까지 왔고 다음 액션이 무엇인지.}

## 인계 시 알아야 할 것

| 항목 | 유형 | 상태·사유 | 출처 |
|------|------|----------|------|

**기록이 없어 확인 못 한 것**
- {구간} — {왜 비었는지}

## 관련 메모

- [[허브]]
- [[WBS]]
```

## 근거 규칙

- 문서의 모든 사실 서술에는 되짚을 경로(노트 링크·PR 번호·파일 경로)가 붙어야 한다. 붙일 수 없으면 그 문장을 쓰지 않고 `기록이 없어 확인 못 한 것`으로 내린다.
- 외부 식별자(PR 번호, 파트너 키 `acct_*`·`settreport_*`, thread_ts, 거래 ID)는 **전체 값을 보존한다**. 인계받은 사람이 원본을 검색해 찾아가야 한다.
- 원문이 영문이면 국문 번역을 병기한다.
- 결정의 **이유**가 기록에 없으면 "이유 미기록"이라고 쓴다. 그럴듯한 이유를 지어 넣으면 인계받은 사람이 그 근거로 다음 결정을 내린다.
- 번복된 결정을 지우지 않는다. 무엇이 왜 뒤집혔는지가 인계에서 가장 값진 정보다.

## 판단 기준

| 상황 | 처리 |
|------|------|
| 대상 후보 2개 이상 / 0개 | 진행 중단, 사용자에게 되물음 |
| 기존 summary 존재 | 재생성 금지 — 읽어서 입력으로 쓰고 이어붙임 |
| 아카이브된 ISS | `40-archives/`에서 찾아 동일하게 처리, 최종 상태를 `현재 상태`에 명시 |
| step frontmatter 불일치 (status vs 날짜) | 날짜 필드 기준으로 판단, 불일치 사실을 출처에 병기 |
| `applicable: false` + `na-reason` | **누락 아님** — 미진행 사유로 `인계 시 알아야 할 것`에 기재 |
| 미발송 draft comm | 인계 항목으로 올림 (발송 주체가 사람인 경우가 많음) |
| 수집기 1개 실패 | 1회 재시도 → 재실패 시 **호출자가 그 축을 인라인 수집**. 범위가 커 인라인이 불가능할 때만 축 없이 진행하고 누락을 문서에 명시 |
| 기록이 수 년치 | 시간순 전량 나열 대신 국면(phase)으로 묶고, 국면마다 근거 노트를 단다 |
| 대상에 기록이 거의 없음 | 문서를 만들지 않고 "기록 부족" 보고 후 중단 — 빈 문서는 없는 것보다 나쁘다 |

## 테스트 시나리오

**정상 흐름 — 서비스 영역**
```
/handover payment-psp
→ Phase 0: summary 없음 → 초기 생성
→ Phase 1: 20-areas/payment/psp + 링크 ISS N개
→ Phase 2: 파일 30개↑ → collector 3축 병렬
→ Phase 3: 초안 + 근거 없는 구간 2건 제시
→ "저장" → Issue → 브랜치 → payment-psp summary.md → PR
```

**에러 흐름 — 대상 모호**
```
/handover FT-001
→ Phase 1: FIE·npg-core 두 곳에 FT-001 존재
→ 진행 중단, 어느 서비스인지 되물음
```

**에러 흐름 — 수집기 실패**
```
/handover ISS-064
→ decisions 축이 빈 결과 → 1회 재시도 → 재실패
→ 호출자가 decisions 축을 인라인 수집 (steps 본문·comms 선택지 논의 직접 Read)
→ 3축 모두 채워 초안 작성, 초안 머리말에 "방식: 팬아웃 2축 + 인라인 1축" 명시
```
