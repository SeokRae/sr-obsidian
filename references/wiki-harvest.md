# Wiki Harvest (공통 후처리)

daily·weekly·retro 완료 출력 후 자동 실행. 회의록이 없거나 후보가 없으면 전체 생략.

**스캔 범위** (호출 스킬별): daily = 오늘 날짜 · weekly = 해당 주 목~수 · retro = 해당 주 월~금

1. **범위 내 회의록 스캔** — `20-areas/**/meetings/*.md` 중 frontmatter `created:`가 범위 안인 파일

   ```bash
   find 20-areas -path "*/meetings/*.md" | while read f; do
     created=$(grep "^created:" "$f" | head -1 | awk '{print $2}')
     [[ "$created" >= "{시작일}" && "$created" <= "{종료일}" ]] && echo "$f"
   done 2>/dev/null || true
   ```

2. **미처리 확인** — `60-logs/ingest-log.md`에 해당 파일 경로 기록이 없으면 미처리로 간주

3. **wiki 후보 추출** (미처리 파일 Read 후) — 볼드 용어(`**Term**`), dangling `[[링크]]`, H2/H3 개념 제목. 기존 `wiki-term: true` 노트와 중복이면 제외

4. **후보 제시** (1개 이상일 때만)

   ```
   📎 미처리 회의록 N개 | wiki 후보: "용어A", "용어B" ...
   wiki 페이지 만들까요? [y/스킵]
   ```

   - `y` → `sr-obsidian:wiki scan {파일경로}` 호출
   - `스킵` / 후보 없음 / 회의록 없음 → 종료 (weekly·retro는 다음 단계로 진행)
