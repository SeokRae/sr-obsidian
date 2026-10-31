---
name: learn
description: >
  개념이나 코드를 받아 내부 동작을 1차 출처(명세, 고정 태그 소스의 파일:줄, 실행 관측)로 조사하고 스텝마다 대조한 뒤, 흐름 문서, 시나리오 노트, flowcast 그림 세트, 읽는 순서를 vault에 만든다. 못 그린 형태는 시각화 갭 기록에 남긴다. "동작 방식 학습", "내부 동작을 그림으로 이해하고 싶어", "이 코드가 안에서 어떻게 도는지", "호출 흐름 따라가기", "learn" 요청 시 사용.
  Do NOT use for 책 챕터 literature 분석 → sr-obsidian:study.
  Do NOT use for 이미 있는 MD 문서의 HTML 변환 → sr-obsidian:visualize.
  Do NOT use for 용어 하나의 정의 페이지 → sr-obsidian:wiki.
  Do NOT use for 출처 조사 없이 그림만 → flowcast:flowcast.
  Keywords: 동작 방식, 내부 동작, 동작 원리, 호출 흐름, 소스 대조, 흐름 문서, 시나리오, learn, how it works
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Skill, WebFetch, Agent, SendMessage
---

# sr-obsidian:learn (동작 방식 학습 자료 세트)

개념이나 코드 하나의 내부 동작을 1차 출처로 조사하고, 출처와 대조한 흐름을 그림으로 옮겨 vault에 학습 자료 세트로 남긴다. 기준점은 vault의 `30-resources/tech/java/JVM 구동방식.md`, `JVM 구동 시나리오.md`와 그 그림들이다.

## 사용법

```
/sr-obsidian:learn "Spring @Transactional 메서드 호출 한 번이 커밋되기까지 (spring-tx 6.1.13)"
/sr-obsidian:learn @"{코드 경로}" "save() 한 번이 DB에 닿기까지"
```

## 산출물

| 산출물 | type | 위치 | 틀 |
|---|---|---|---|
| 흐름 문서 | permanent | `30-resources/{카테고리}/{주제}/{주제} 동작방식.md` | [flow-doc.md](references/flow-doc.md) |
| 시나리오 노트 | literature | 같은 폴더 `{주제} 시나리오.md` | [scenario.md](references/scenario.md) |
| 그림 2장 이상 | diagram | 같은 폴더 `diagrams/` (HTML + 페어드 MD) | [view-map.md](references/view-map.md), flowcast 스킬 |
| 갭 기록 행 | log | `60-logs/visualization-gaps.md` | [gap-log.md](references/gap-log.md) |

서비스 코드의 흐름이면 `20-areas/{서비스}/docs/` 아래를 제안하고 사용자에게 확인한다.

## 팀

조사, 작성, 출처 대조를 서로 다른 에이전트가 맡고, 리드(이 스킬을 실행하는 세션)가 아래 시점에 하나씩 띄웁니다. 근거 칸을 채운 쪽이 그 근거를 다시 대조하면 같은 맥락의 착오를 그대로 지나치기 때문이에요. 작업 폴더와 공유 파일 형식은 [team.md](references/team.md)에 있습니다.

| 이름 | subagent_type | 맡는 일 | 띄우는 때 |
|---|---|---|---|
| `learn-researcher` | `sr-obsidian:learn-researcher` | 중복 확인, 근거 수집 → `research.md`, `sources.md` | Phase 1의 3 |
| `learn-writer` | `sr-obsidian:learn-writer` | 시나리오 초안, vault 노트, 페어드 MD, 불일치 수정 | Phase 1의 5. 이후 `SendMessage`로 깨움 |
| `learn-verifier` | `sr-obsidian:learn-verifier` | 관문과 재관문의 근거 칸 대조 | Phase 1의 6. 재관문은 `SendMessage`로 깨움 |

- 띄우는 형식은 `Agent(name: "{이름}", subagent_type: "{subagent_type}", run_in_background: true, prompt: ...)`입니다. 프롬프트에는 각 정의의 `## 입력` 필드를 채우고, `lead: main`과 `skill_dir`(이 스킬의 Base directory)를 함께 넣어요.
- verifier는 fork가 아닌 새 에이전트로 띄웁니다. 프롬프트에 `research.md`, 조사 요약, 작성 의도를 넣지 않습니다.
- 불일치는 verifier가 writer에게 `SendMessage`로 바로 돌려보내고, 되돌림은 최대 2회예요. 그 사이 도착하는 회차 알림은 리드가 처리할 일이 아닙니다. 그래도 남으면 verifier가 리드에게 미해결로 보고하고 리드가 사용자에게 올립니다.
- 사용자 확인(Phase 1 학습 계획, Phase 2 Issue 제안, fan-out과 MOC 승인)은 리드만 받습니다. 서브에이전트는 사용자에게 묻지 못해요.
- researcher도 이름을 붙여 띄웁니다. verifier의 기대값만으로 못 고치는 칸이 나오면 writer가 보충 조사를 요청해 깨우기 때문이에요. flowcast 위임은 되돌림이 없어 지금처럼 리드가 스킬로 부릅니다.
- 한 세션에서 learn은 한 번에 하나만 돌립니다. 같은 이름으로 다시 띄우면 나중 쪽이 이름을 가져가요.
- 기다리던 보고가 오지 않으면 `ListAgents`로 상태를 보고 `{ws}/verify-log.md`를 읽습니다.

## Phase 1: 조사와 대조 (READ-ONLY)

**vault 파일 수정 없음.** 받은 소스, 실행 로그, 예제 프로젝트, 시나리오 초안은 모두 작업 폴더 `{ws}`(세션 스크래치패드의 `learn-{slug}/`, 없으면 `$TMPDIR/learn-{slug}/`)에만 씁니다.

1. **입력 판별**: 개념 | 코드. 트리거 하나(호출 한 번, 명령 한 번, 요청 한 번)로 좁힌다. "스프링 동작 방식"처럼 큰 주제는 트리거 단위로 쪼개 표로 제안하고 하나를 고르게 한다.
2. **대상 버전 고정**: 구현과 버전(JDK 빌드 태그, 라이브러리 버전, 커널 버전, RFC 번호)을 확정한다. 코드 입력이면 빌드 파일에서 읽는다. 확정할 수 없으면 진행하지 않고 묻는다. 버전이 바뀌면 흐름이 바뀐다.
3. **중복 확인** (`learn-researcher`): `topic`, `target`, `input`, `ws`, `vault`를 넘겨 띄웁니다. researcher가 `30-resources`, `20-areas`를 주제어와 클래스, 함수 이름으로 Grep해 겹치는 노트마다 처리안(새로 | 확장 | 링크만)을 적어요. 버전이 다른 기존 노트는 덮어쓰지 않고, 새 노트에서 버전 차이를 적고 링크한다.
4. **근거 수집** (`learn-researcher`, 3과 같은 호출): 근거 칸에는 실행 관측, 고정 태그 소스의 파일:줄, 명세 절 셋만 씁니다. 요약 글과 블로그는 단서로만 써요. 실행할 수 있으면 관측이 순서의 뼈대이고, 외부 소스 원문은 `{ws}`에만 받고 실행하지 않습니다. 세부 규칙은 researcher 정의에 있어요. `[learn-research] 버전 확인 필요`가 오면 사용자에게 묻고 답을 `SendMessage`로 넘깁니다.
5. **시나리오 초안** (`learn-writer`): `[learn-research] 조사 완료`가 오면 `mode: draft`로 띄웁니다. writer가 [scenario.md](references/scenario.md) 틀로 `{ws}/scenario-draft.md`를 써요.
6. **출처 대조 관문** (`learn-verifier`): `[learn-write] 초안 완료`가 오면 새 에이전트로 띄웁니다. 넘기는 건 `gate: 관문`, `targets: {ws}/scenario-draft.md`, `sources: {ws}/sources.md`, `ws`, `skill_dir`, `writer: learn-writer`, `lead: main`뿐이에요. 통과 조건은 아래와 같습니다.
   - 모든 근거 칸이 출처로 채워졌거나 `[확인 필요]`다(`scripts/evidence_gate.py` 0건).
   - 근거 칸마다 고정 출처를 다시 열어 같은 행의 주장과 맞는지 확인했다.
   - 관측이 있으면 정상 흐름의 순서가 관측 순서와 같다.
   - 분기마다 조건이 바꾸는 `if`를 소스에서 모두 찾아 갈라지는 스텝과 대조했다.
   - 처음 이해와 출처가 다른 스텝이 `## 출처 대조 결과`에 있다(없으면 "대조로 바뀐 것 없음").

   `[learn-verify] 관문 통과`가 오기 전에는 flowcast 스킬을 호출하지 않습니다. `미해결`이나 `검증 불가`가 오면 그 표를 8의 보고에 넣어 사용자에게 처리를 물어요.
7. **뷰 계획**: [view-map.md](references/view-map.md)의 질문 대 뷰 표로 2장 이상 고릅니다. flowcast로 못 그리는 형태는 갭 후보로 적어요. verifier를 기다리는 동안 해도 됩니다.
8. **보고와 확인**: 아래 형식으로 보여 주고, 확인을 받은 뒤에만 Phase 2로 간다.

```
### 학습 계획: {주제}

대상: {구현} {버전, 태그} | 입력: 개념 | 코드({경로})
기존 노트: | 파일 | 관계 | 처리안 |
근거: 관측 {무엇을 어떻게}, 소스 {태그, 파일 n개}, 명세 {절}
시나리오 초안: 정상 N스텝(구간 M개), 분기 n, 예외 n, [확인 필요] n (전체 표 또는 구간별 요약 + 스크래치패드 경로)
출처 대조 결과: | 스텝 | 처음 이해 | 출처가 보여 준 것 | 근거 |
빈 근거 칸: 0건
검증: 관문 {n}회차 통과, 고친 칸 {n}, 검증 불가 {n}, 기록 {ws}/verify-log.md
뷰 계획: | 그림 | 뷰 | 스킬 | 소스 |
갭 후보: {키} 또는 없음
만들 파일: {경로 목록}

진행할까요?
```

## Phase 2: 작성 (WRITE)

사용자가 확인하면 실행한다.

1. **git**: [git-workflow.md](../../references/git-workflow.md) 절차. 제목 `docs: {주제} 동작방식 학습 자료`, 브랜치 `feature/{N}-learn-{slug}`.
2. **시나리오 노트** (`learn-writer`): `SendMessage(to: "learn-writer")`로 `mode: vault`, `dir`(주제 폴더 절대경로), `names`, `feedback`(8에서 사용자가 고치라고 한 것)을 넘깁니다. writer가 초안을 vault로 옮겨요. 완료 보고의 `Phase 1 뒤 바뀐 스텝`이 비어 있지 않으면, 그리기 전에 시나리오 노트만 대상으로 verifier에게 `gate: 재관문`을 먼저 요청하고 통과를 기다립니다.
3. **흐름 문서** (`learn-writer`, 2와 같은 메시지): [flow-doc.md](references/flow-doc.md) 틀. 요약 콜아웃 다음에 `## 읽는 순서`를 둔다.
4. **그림**: [view-map.md](references/view-map.md)대로 flowcast 스킬에 위임한다. component, sequence, topology는 `flowcast:flowcast`로 한 번에 넘기고, mechanism과 state-loop는 각 스킬을 직접 부른다. `out_dir`과 `vault_iframe`은 `{주제 폴더}/diagrams`의 절대경로다. sequence의 소스는 시나리오 노트다. 대상 `diagrams/`에 다른 주제의 flowcast `_workspace/`가 있으면 오케스트레이터가 그것을 `_workspace_prev/`로 옮기므로, 이때는 뷰 스킬(`flowcast:component`, `flowcast:sequence`)을 한 장씩 직접 부른다. `render.py`는 HTML만 만든다. 페어드 MD는 `SendMessage(to: "learn-writer")`로 `mode: paired`, `html`(렌더된 HTML 경로), `sample`(같은 폴더의 기존 페어드 MD, 없으면 기준점 `30-resources/tech/java/diagrams/`의 것)을 넘겨 writer가 씁니다. 리드는 페어드 MD에 `type: diagram`, `source:`가 있는지, 그림 수와 이름이 흐름 문서 `## 파생 다이어그램`과 맞는지 확인해요.
5. **재관문** (`learn-verifier`): `[learn-write] 페어드 MD 완료`가 오면 `SendMessage(to: "learn-verifier")`로 `gate: 재관문`과 `targets`(시나리오 노트, 흐름 문서, 페어드 MD의 vault 절대경로)를 넘깁니다. 되돌림 규칙은 관문과 같아요. 통과 보고가 `그림 영향 있음`이면 그 그림을 4대로 다시 렌더하고 writer에게 페어드 MD 갱신을 맡긴 뒤 재관문을 한 번 더 요청합니다. 재관문 통과 전에는 커밋하지 않습니다.
6. **갭 기록**: [gap-log.md](references/gap-log.md)대로 `60-logs/visualization-gaps.md`에 행을 append한다. 갭이 없으면 "갭 없음" 행. 같은 키가 이미 있으면 flowcast 승격 Issue를, flowcast 결함과 규칙 결함은 바로 flowcast Issue를 제안한다. 둘 다 승인 후 만든다.
7. **Fan-out과 MOC**: 새 노트의 태그와 키워드로 기존 permanent 후보(최대 10개)와 MOC를 찾아 근거와 함께 보여 준다. 승인한 후보의 `## 관련 메모`에 `- [[{새 노트 파일명}]]`을, 승인한 MOC에 링크를 Edit으로 넣는다. 링크는 H1이 아니라 파일명 기준이다([obsidian-markdown](../../references/obsidian-markdown.md) 링크 대상 규칙).
8. **Ingest Log**:
   ```bash
   printf '\n## [%s] learn | {주제} → 노트 2, 그림 {N}\n{만든 파일 경로 목록}\n' "$(date +%Y-%m-%d)" >> 60-logs/ingest-log.md
   ```
9. **검사와 PR**: `{ws}/verify-log.md`의 회차 요약을 시나리오 노트 `## 검증 기록` 표와 PR 본문에 옮깁니다. 재관문 뒤에 쓰는 기록이라 대조 대상이 아니에요. 만든 노트를 `python3 _scripts/note_validator.py {경로...}`로 검사하고, `python3 "{skill_dir}/scripts/evidence_gate.py" "{시나리오 노트}"`를 한 번 더 돌립니다. 만든 경로만 명시해 add하고(`git add -A` 금지) `git diff --cached --name-only`로 확인한 뒤 커밋, PR(`Closes #N`).

## 하지 않는 것

- 출처 대조 전에 그리기. 그림이 먼저 나오면 틀린 흐름이 그림에 굳는다.
- 근거 칸을 채운 쪽(researcher, writer, 리드)이 관문 판정까지 하기. 판정은 조사 맥락을 받지 않은 `learn-verifier`가 합니다.
- 외부 소스 원문, 회사 코드, 실 데이터를 노트나 flowcast(public 저장소) Issue에 싣기.
- 대화형 문답 학습. 이 스킬은 검증된 자료 세트까지 만든다.
- flowcast 저장소를 직접 고치기. 갭과 결함은 Issue 제안까지다.
