---
name: lint-wiki
description: >
  LLM Wiki 품질 검사. Phase 1(스크립트 구조 검사) + Phase 2(LLM 의미론적 검사) 2단계.
  구조 검사: Orphan, Dangling link, MOC 미연결, 관련 메모 섹션 부재.
  의미론적 검사: 페이지 간 모순, stale 주장, prose 언급 개념, data gap, 신규 소스 제안.
  결과를 60-logs/lint-reports/YYYY-MM-DD.md 로 저장.
  Do NOT use for project structure audit (use sr-obsidian:audit — audit covers 20-areas/ project folders).
  Do NOT use for creating/querying wiki term pages (use sr-obsidian:wiki — wiki는 용어 페이지 생성·질의, lint-wiki는 orphan·dangling·moc 품질 검사).
  Do NOT use for 외부 웹 최신 정보 수집·동향 누적 (use sr-obsidian:radar — lint-wiki는 내부 wiki 품질·연결 검사, radar는 외부 웹 수집·누적).
  Keywords: lint, wiki, orphan, dangling, moc, 품질, 검사, 연결 없음, 모순, stale
allowed-tools: Bash, Read, Glob
---

# sr-obsidian:lint-wiki — LLM Wiki 품질 검사

> **참조**: [Karpathy — LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
> "Lint: 모순, stale 주장, orphan 페이지, 페이지 없는 개념, missing cross-reference, data gap을 주기적으로 점검한다."

`type:permanent` 노트에서 **구조적 이슈(Phase 1)** 와 **의미론적 이슈(Phase 2)** 를 탐지하고 리포트를 생성한다.

---

## Phase 1: 구조 검사 (스크립트)

### 검사 항목

| 코드 | 항목 | 판단 기준 |
|------|------|----------|
| (a) | **Orphan** | `type:permanent`인데 vault 내 어떤 파일도 `[[이 노트]]`로 링크하지 않음 |
| (b) | **Dangling link** | `[[title]]`이 vault에 존재하지 않는 파일을 가리킴 |
| (c) | **MOC 미연결** | `type:permanent`인데 `50-moc/` 어디서도 참조되지 않음 |
| (d) | **섹션 부재** | `type:permanent`인데 `## 관련 메모` 섹션이 없음 |

### 실행 방법

```bash
python3 _scripts/lint-wiki.py
# 특정 vault 지정
python3 _scripts/lint-wiki.py --vault /Users/sr/obsidian/sr-labs
```

### 작업 흐름

1. 스크립트 실행 (약 5~10초 소요)
2. stdout 요약 확인 — 항목별 건수 출력
3. 리포트 파일 Read: `60-logs/lint-reports/YYYY-MM-DD.md`
4. 이슈가 있으면 우선순위 제안:
   - **(d) 섹션 부재** → 즉시 수정 가능
   - **(a) Orphan** → 역링크 삽입 또는 MOC 추가
   - **(b) Dangling** → 링크 오타 수정 또는 대상 노트 생성
   - **(c) MOC 미연결** → 해당 MOC에 `[[노트]]` 추가

---

## Phase 2: LLM 의미론적 검사

Phase 1 리포트를 읽은 뒤 LLM이 직접 노트를 읽어 구조 검사로는 탐지할 수 없는 이슈를 탐지한다.

### 검사 항목

| 코드 | 항목 | 탐지 방법 |
|------|------|----------|
| (e) | **페이지 간 모순** | 동일 개념을 다루는 노트 간 정의·수치·결론이 충돌하는 경우 |
| (f) | **Stale 주장** | 최신 ingest-log 기준으로 새 소스가 기존 주장을 대체했는데 반영되지 않은 경우 |
| (g) | **페이지 없는 개념** | prose에서 반복 언급되지만 `[[링크]]`도 없고 wiki-term 페이지도 없는 개념 |
| (h) | **Data gap** | 중요 토픽인데 depth가 얕거나 출처가 1개뿐인 경우 |

### 실행 절차

1. `60-logs/lint-reports/YYYY-MM-DD.md` 읽기 (Phase 1 결과)
2. Phase 1에서 이슈가 많은 카테고리의 노트 상위 10개 `Read`
3. 추가로 `60-logs/ingest-log.md` 최근 10개 항목 확인 (새 소스 파악)
4. 아래 4종 탐지:

**(e) 모순 탐지**
- 동일 태그·aliases를 가진 노트 쌍 비교
- 수치(숫자+단위), 순서, 정의 문장이 다르면 모순 후보로 기록

**(f) Stale 주장 탐지**
- ingest-log 최근 항목의 주제와 기존 wiki-term 페이지 내용 비교
- 새 소스 날짜 > 기존 노트 `created` 날짜이고 내용이 충돌하면 stale 후보

**g) 페이지 없는 개념 탐지**
- 읽은 노트의 본문에서 **볼드** 또는 반복 등장(3회 이상) 단어 추출
- `[[링크]]` 없고 wiki-term 페이지도 없으면 후보 목록 추가

**h) Data gap 탐지**
- 노트 길이 < 300자이거나 `## 관련 메모` 링크가 1개 이하인 wiki-term 노트
- "이 토픽을 더 깊이 다룰 출처를 찾아볼 것" 메시지 생성

### 출력 형식

```markdown
## Phase 2 의미론적 Lint — {YYYY-MM-DD}

### (e) 페이지 간 모순
| 노트 A | 노트 B | 충돌 내용 |
|--------|--------|----------|
| [[X]] | [[Y]] | X: "..." vs Y: "..." |

### (f) Stale 주장
| 노트 | stale 내용 | 최신 소스 |
|------|-----------|----------|
| [[X]] | "..." | [[최신 ingest 항목]] |

### (g) 페이지 없는 개념 후보
- {개념A} — [[출처 노트]], [[출처 노트2]]에서 반복 등장
- {개념B} — ...

> `/sr-obsidian:wiki create "{개념A}"` 로 바로 생성 가능

### (h) Data gap
| 노트 | 문제 | 권장 액션 |
|------|------|---------|
| [[X]] | 길이 200자, 출처 0개 | 관련 자료 추가 ingest 권장 |
```

---

## 판단 기준

| 상황 | 처리 |
|------|------|
| Phase 1 이슈 0건 | Phase 2로 바로 진행 |
| Phase 2 이슈 0건 | "✅ Wiki 상태 양호" 출력 후 종료 |
| (a) orphan이 많음 | `sr-obsidian:study` fan-out 단계 점검 |
| (b) dangling이 많음 | 노트 제목 변경 이력 확인, 링크 일괄 수정 |
| (c) MOC 미연결이 많음 | 해당 주제 MOC 파일 갱신 권장 |
| (d) 섹션 부재가 많음 | 기존 노트 일괄 보강 또는 template 강제 |
| (e) 모순 발견 | 최신 소스 기준으로 정정, 오래된 노트 업데이트 |
| (f) stale 많음 | ingest 주기 단축 또는 wiki 자동 갱신 검토 |
| (g) 페이지 없는 개념 많음 | `sr-obsidian:wiki scan` 실행 후 일괄 생성 |
| (h) data gap 많음 | 관련 자료 추가 ingest 권장 |

## 주기 권장

- **주 1회** — Phase 1 + Phase 2 전체 실행
- Phase 1만: 빠른 구조 점검 시 (`python3 _scripts/lint-wiki.py` 단독 실행)
- `sr-obsidian:audit` 이후, `/retro` 또는 `/weekly` 실행 전에 같이 돌리면 효율적
