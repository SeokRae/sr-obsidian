# validator 품질 지표 (내용 수준 측정)

생성·갱신 완료 후 `note_validator.py`가 아래 지표를 측정해 `evolution_log.jsonl`에 기록한다.
**스킬 동작을 막지 않는다** — 측정·기록만 한다.

| 지표 | 측정 방법 | 목표값 |
|------|----------|--------|
| `goal_item_count` | `## 목표` 섹션의 `- [` 항목 수 | 1 이상 |
| `goal_issue_linked` | 목표 항목 중 `#NNN` 포함 비율 (0.0~1.0) | 0.5 이상 |
| `log_real_items` | 작업 로그에서 placeholder(`- [ ]` 단독 1줄) 제외 후 항목 수 | 1 이상 |
| `completion_rate` | 갱신 모드: 전날 `[ ]` 중 오늘 `[x]`로 전환된 비율 | 0.3 이상 |
| `carryover_reduction` | 전날 이월 수 - 오늘 이월 수 (음수 = 이월 증가) | 양수 권장 |
