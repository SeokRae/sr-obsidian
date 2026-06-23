---
name: defuddle
description: >
  URL에서 깔끔한 마크다운을 추출해 00-inbox/에 fleeting 노트로 저장한다.
  웹 페이지의 광고·네비게이션·클러터를 제거하고 핵심 본문만 보존.
  "URL 저장", "웹 클리핑", "이 페이지 메모해줘", "링크 캡처", "clip", "웹 페이지 보관" 요청 시 사용.
  Do NOT use for .md URLs (use WebFetch directly).
  Do NOT use for structured study/permanent notes (use sr-obsidian:study).
  Do NOT use for quick manual fleeting capture without a URL (use sr-obsidian:capture — capture는 수동 포착, defuddle는 URL 본문 추출).
  Do NOT use for 외부 웹 최신 정보 수집·동향 누적 (use sr-obsidian:radar — defuddle는 단일 URL 본문 추출, radar는 외부 웹 동향 수집·누적).
  Keywords: 웹 클리핑, URL 저장, clip, defuddle, 링크 캡처, 웹 보관, inbox
allowed-tools: Bash, Write, Read
---

# sr-obsidian:defuddle — 웹 클리핑

URL의 핵심 본문을 마크다운으로 추출해 `00-inbox/`에 fleeting 노트로 저장한다.
WebFetch 대신 사용 — 광고·네비게이션 제거로 토큰 절감.

## 사전 확인

defuddle CLI가 없으면 설치:
```bash
npm install -g defuddle
```

## 작업

1. **URL 수신** — `$ARGUMENTS`에서 URL 추출

2. **메타데이터 수집** (각각 별도 실행):
```bash
defuddle parse $URL -p title
defuddle parse $URL -p description
defuddle parse $URL -p domain
```

3. **본문 추출**:
```bash
defuddle parse $URL --md
```

4. **파일명 결정** — `{YYYY-MM-DD}-{slug}.md` 형식
   - title에서 slug 생성 (소문자, 공백→하이픈, 특수문자 제거)
   - 예: `2025-05-08-why-llms-hallucinate.md`

5. **`00-inbox/`에 저장** — Write로 생성:

```markdown
---
type: fleeting
created: YYYY-MM-DD
source: {원본 URL}
domain: {domain}
tags:
  - inbox
  - web-clip
---

# {title}

> {description}

{추출된 본문 마크다운}
```

6. **완료 안내**:
```
✅ 저장 완료: 00-inbox/{파일명}.md
다음 단계: /capture 또는 /study 로 승격 처리
```

## 판단 기준

| 상황 | 처리 |
|------|------|
| URL이 `.md`로 끝남 | WebFetch로 직접 읽기, defuddle 불필요 |
| defuddle 미설치 | `npm install -g defuddle` 안내 후 중단 |
| 추출 결과가 비어 있음 | WebFetch fallback으로 재시도 |
| 동일 URL 이미 저장됨 | `source:` 필드로 중복 검색 후 사용자에게 알림 |
| 제목 없음 | domain + 날짜로 파일명 생성 |
