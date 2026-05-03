---
name: lint-wiki
description: >
  LLM Wiki 품질 검사. permanent 노트 4종 이슈 탐지:
  (a) Orphan, (b) Dangling link, (c) MOC 미연결, (d) 관련 메모 섹션 부재.
  결과를 60-logs/lint-reports/YYYY-MM-DD.md 로 저장.
  Keywords: lint, wiki, orphan, dangling, moc, 품질, 검사, 연결 없음
allowed-tools: Bash, Read, Glob
---

# sr-obsidian:lint-wiki — LLM Wiki 품질 검사

Karpathy LLM Wiki 패턴의 주기적 Lint 대응.
`type:permanent` 노트에서 4종 품질 이슈를 탐지하고 리포트를 생성한다.

## 검사 항목

| 코드 | 항목 | 판단 기준 |
|------|------|----------|
| (a) | **Orphan** | `type:permanent`인데 vault 내 어떤 파일도 `[[이 노트]]`로 링크하지 않음 |
| (b) | **Dangling link** | `[[title]]`이 vault에 존재하지 않는 파일을 가리킴 |
| (c) | **MOC 미연결** | `type:permanent`인데 `50-moc/` 어디서도 참조되지 않음 |
| (d) | **섹션 부재** | `type:permanent`인데 `## 관련 메모` 섹션이 없음 |

## 실행 방법

```bash
python3 _scripts/lint-wiki.py
```

선택적으로 특정 vault 지정:

```bash
python3 _scripts/lint-wiki.py --vault /Users/sr/obsidian/sr-labs
```

## 작업 흐름

1. 위 명령어 실행 (약 5~10초 소요)
2. stdout 요약 확인 — 항목별 건수 출력
3. 리포트 파일 Read: `60-logs/lint-reports/YYYY-MM-DD.md`
4. 이슈가 있으면 우선순위 제안:
   - **(d) 섹션 부재** → 해당 노트에 `## 관련 메모` 섹션 추가 (즉시 수정 가능)
   - **(a) Orphan** → 관련 노트에서 역링크 삽입 또는 MOC에 추가
   - **(b) Dangling** → 링크 오타 수정 또는 대상 노트 생성
   - **(c) MOC 미연결** → 해당 MOC에 `[[노트]]` 추가

## 판단 기준

| 상황 | 처리 |
|------|------|
| 이슈 0건 | "✅ Wiki 상태 양호" 출력 후 종료 |
| (a) orphan이 많음 | `sr-obsidian:study` 또는 `sr-obsidian:audit` fan-out 단계 점검 |
| (b) dangling이 많음 | 노트 제목 변경 이력 확인, 링크 일괄 수정 |
| (c) MOC 미연결이 많음 | 해당 주제 MOC 파일 갱신 권장 |
| (d) 섹션 부재가 많음 | 기존 노트 일괄 보강 또는 template 강제 |

## 주기 권장

- **주 1회** — `sr-obsidian:lint-wiki` 실행 후 리포트 확인
- `sr-obsidian:audit` 이후, `/retro` 또는 `/weekly` 실행 전에 같이 돌리면 효율적
