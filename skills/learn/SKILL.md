---
name: learn
description: >
  개념이나 코드를 받아 내부 동작을 1차 출처(명세, 고정 태그 소스의 파일:줄, 실행 관측)로 조사하고 스텝마다 대조한 뒤, 흐름 문서, 시나리오 노트, flowcast 그림 세트, 읽는 순서를 vault에 만든다. 못 그린 형태는 시각화 갭 기록에 남긴다. "동작 방식 학습", "내부 동작을 그림으로 이해하고 싶어", "이 코드가 안에서 어떻게 도는지", "호출 흐름 따라가기", "learn" 요청 시 사용.
  Do NOT use for 책 챕터 literature 분석 → sr-obsidian:study.
  Do NOT use for 이미 있는 MD 문서의 HTML 변환 → sr-obsidian:visualize.
  Do NOT use for 용어 하나의 정의 페이지 → sr-obsidian:wiki.
  Do NOT use for 출처 조사 없이 그림만 → flowcast:flowcast.
  Keywords: 동작 방식, 내부 동작, 동작 원리, 호출 흐름, 소스 대조, 흐름 문서, 시나리오, learn, how it works
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Skill, WebFetch
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

## Phase 1: 조사와 대조 (READ-ONLY)

**vault 파일 수정 없음.** 받은 소스, 실행 로그, 예제 프로젝트, 시나리오 초안은 모두 세션 스크래치패드(없으면 `$TMPDIR/learn-{slug}/`)에만 쓴다.

1. **입력 판별**: 개념 | 코드. 트리거 하나(호출 한 번, 명령 한 번, 요청 한 번)로 좁힌다. "스프링 동작 방식"처럼 큰 주제는 트리거 단위로 쪼개 표로 제안하고 하나를 고르게 한다.
2. **대상 버전 고정**: 구현과 버전(JDK 빌드 태그, 라이브러리 버전, 커널 버전, RFC 번호)을 확정한다. 코드 입력이면 빌드 파일에서 읽는다. 확정할 수 없으면 진행하지 않고 묻는다. 버전이 바뀌면 흐름이 바뀐다.
3. **중복 확인**: `30-resources`, `20-areas`를 주제어와 클래스, 함수 이름으로 Grep한다. 겹치는 노트마다 처리안(새로 | 확장 | 링크만)을 정한다. 버전이 다른 기존 노트는 덮어쓰지 않고, 새 노트에서 버전 차이를 적고 링크한다.
4. **근거 수집**: 근거 칸에는 아래 셋만 쓴다. 요약 글과 블로그는 단서로만 쓰고 근거 칸에 넣지 않는다.

   | 종류 | 예 | 근거 칸 표기 |
   |---|---|---|
   | 실행 관측 | 스택 트레이스, 로그, `-Xlog`, `strace`, 디버거 | `관측(스택 #3)`처럼 무엇의 몇 번째인지 |
   | 소스 | 고정 태그의 파일과 줄 | `threads.cpp:662` (태그는 frontmatter `source`에 한 번) |
   | 명세 | JVMS, RFC, JSR의 절 | `JVMS 5.5`, `RFC 9293 3.5` |

   - **실행할 수 있으면 관측이 뼈대다.** 학습용 예제를 스크래치패드에 새로 만들어 트리거를 한 번 실행하고, 관측으로 호출 순서를 먼저 잡은 뒤 소스로 스텝마다 파일:줄을 단다. 소스만 읽고 순서를 정하면 순서가 틀린다(JVM 구동 학습에서 스텝 8과 9가 뒤바뀌었다). 예제에 회사 코드나 실 데이터를 쓰지 않는다.
   - **대역으로 관측할 때는 대역의 계약부터 확인한다.** 실제 구현 대신 기록용 대역(가짜 매니저, 스텁 서버)을 쓰면, 대역이 실제 구현과 같은 계약을 따르는지 소스로 먼저 본다. 계약이 다르면 관측이 반대로 나온다(Spring 트랜잭션 학습에서 기록용 매니저의 트랜잭션 객체가 `SmartTransactionObject`가 아니라 E3가 롤백 대신 커밋으로 관측됐다).
   - 관측을 못 하면 순서의 근거를 호출 지점의 파일:줄이나 명세 절로 단다. 어느 쪽도 없으면 `[확인 필요]`.
   - **외부 소스 원문은 커밋하지 않는다.** 라이선스가 다른 소스(OpenJDK, 리눅스 커널, 외부 라이브러리)는 고정 태그로 스크래치패드에 받아(`git clone --depth 1 --branch {tag}`, raw 파일, `*-sources.jar`) 읽기만 한다. 노트에는 고정 태그 URL, 파일:줄, 함수 이름, 그 줄이 하는 일을 우리 말로 쓴 요약만 남긴다. 받은 코드는 실행하지 않는다.
5. **시나리오 초안**: [scenario.md](references/scenario.md) 틀로 레인, 전제, 정상 흐름, 분기(B), 예외(E), 미결을 채운다.
6. **출처 대조 관문**: 아래를 모두 만족하기 전에는 flowcast 스킬을 호출하지 않는다.
   - 모든 스텝의 근거 칸이 출처로 채워졌거나 `[확인 필요]`다. 아래 검사가 `0건`이어야 한다.
   - 관측이 있으면 정상 흐름의 순서가 관측 순서와 같다.
   - 분기마다 "갈라지는 스텝"을 정상 흐름 스텝의 조건문과 하나씩 대조했다. 분기 조건이 바꾸는 `if`를 소스에서 모두 찾아 적는다(Spring 트랜잭션 학습에서 B2를 9, 10, 23으로만 적었다가 시퀀스를 그리며 12, 22, 24~26도 갈라짐을 찾았다).
   - 처음 이해와 출처가 다른 스텝은 시나리오 `## 출처 대조 결과` 표에 남겼다(없으면 "대조로 바뀐 것 없음").

   ```bash
   python3 - "{시나리오 초안}.md" <<'EOF'
   import re, sys
   bad = []
   for i, line in enumerate(open(sys.argv[1], encoding="utf-8"), 1):
       s = line.strip()
       if not s.startswith("|") or re.fullmatch(r"\|[\s:|-]+\|", s):
           continue
       cells = [c.strip() for c in re.split(r"(?<!\\)\|", s)[1:-1]]
       if cells and cells[-1] == "":
           bad.append(i)
   print("빈 근거 칸:", bad or "0건")
   sys.exit(1 if bad else 0)
   EOF
   ```

7. **뷰 계획**: [view-map.md](references/view-map.md)의 질문 대 뷰 표로 2장 이상 고른다. flowcast로 못 그리는 형태는 갭 후보로 적는다.
8. **보고와 확인**: 아래 형식으로 보여 주고, 확인을 받은 뒤에만 Phase 2로 간다.

```
### 학습 계획: {주제}

대상: {구현} {버전, 태그} | 입력: 개념 | 코드({경로})
기존 노트: | 파일 | 관계 | 처리안 |
근거: 관측 {무엇을 어떻게}, 소스 {태그, 파일 n개}, 명세 {절}
시나리오 초안: 정상 N스텝(구간 M개), 분기 n, 예외 n, [확인 필요] n (전체 표 또는 구간별 요약 + 스크래치패드 경로)
출처 대조 결과: | 스텝 | 처음 이해 | 출처가 보여 준 것 | 근거 |
빈 근거 칸: 0건
뷰 계획: | 그림 | 뷰 | 스킬 | 소스 |
갭 후보: {키} 또는 없음
만들 파일: {경로 목록}

진행할까요?
```

## Phase 2: 작성 (WRITE)

사용자가 확인하면 실행한다.

1. **git**: [git-workflow.md](../../references/git-workflow.md) 절차. 제목 `docs: {주제} 동작방식 학습 자료`, 브랜치 `feature/{N}-learn-{slug}`.
2. **시나리오 노트**: Phase 1 초안을 Write한다. Phase 1 뒤에 고친 스텝이 있으면 관문 검사를 다시 돌린다.
3. **흐름 문서**: [flow-doc.md](references/flow-doc.md) 틀. 요약 콜아웃 다음에 `## 읽는 순서`를 둔다.
4. **그림**: [view-map.md](references/view-map.md)대로 flowcast 스킬에 위임한다. component, sequence, topology는 `flowcast:flowcast`로 한 번에 넘기고, mechanism과 state-loop는 각 스킬을 직접 부른다. `out_dir`과 `vault_iframe`은 `{주제 폴더}/diagrams`의 절대경로다. sequence의 소스는 시나리오 노트다. 대상 `diagrams/`에 다른 주제의 flowcast `_workspace/`가 있으면 오케스트레이터가 그것을 `_workspace_prev/`로 옮기므로, 이때는 뷰 스킬(`flowcast:component`, `flowcast:sequence`)을 한 장씩 직접 부른다. `render.py`는 HTML만 만든다. 페어드 MD는 같은 폴더의 기존 페어드 MD 형식을 따라 직접 쓰고, 표의 근거 줄 번호를 소스와 다시 대조한다. 페어드 MD에 `type: diagram`, `source:`가 있는지 확인하고, 그림 수와 이름을 흐름 문서 `## 파생 다이어그램`과 맞춘다.
5. **갭 기록**: [gap-log.md](references/gap-log.md)대로 `60-logs/visualization-gaps.md`에 행을 append한다. 갭이 없으면 "갭 없음" 행. 같은 키가 이미 있으면 flowcast 승격 Issue를, flowcast 결함과 규칙 결함은 바로 flowcast Issue를 제안한다. 둘 다 승인 후 만든다.
6. **Fan-out과 MOC**: 새 노트의 태그와 키워드로 기존 permanent 후보(최대 10개)와 MOC를 찾아 근거와 함께 보여 준다. 승인한 후보의 `## 관련 메모`에 `- [[{새 노트 파일명}]]`을, 승인한 MOC에 링크를 Edit으로 넣는다. 링크는 H1이 아니라 파일명 기준이다([obsidian-markdown](../../references/obsidian-markdown.md) 링크 대상 규칙).
7. **Ingest Log**:
   ```bash
   printf '\n## [%s] learn | {주제} → 노트 2, 그림 {N}\n{만든 파일 경로 목록}\n' "$(date +%Y-%m-%d)" >> 60-logs/ingest-log.md
   ```
8. **검사와 PR**: 만든 노트를 `python3 _scripts/note_validator.py {경로...}`로 검사하고, 관문 검사를 시나리오 노트에 한 번 더 돌린다. 만든 경로만 명시해 add하고(`git add -A` 금지) `git diff --cached --name-only`로 확인한 뒤 커밋, PR(`Closes #N`).

## 하지 않는 것

- 출처 대조 전에 그리기. 그림이 먼저 나오면 틀린 흐름이 그림에 굳는다.
- 외부 소스 원문, 회사 코드, 실 데이터를 노트나 flowcast(public 저장소) Issue에 싣기.
- 대화형 문답 학습. 이 스킬은 검증된 자료 세트까지 만든다.
- flowcast 저장소를 직접 고치기. 갭과 결함은 Issue 제안까지다.
