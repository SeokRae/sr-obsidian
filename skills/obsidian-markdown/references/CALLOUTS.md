# Callouts Reference

## 기본 콜아웃

```markdown
> [!note]
> 노트 콜아웃.

> [!info] 커스텀 제목
> 제목을 직접 지정할 수 있다.

> [!tip] 제목만
```

## 접이식 콜아웃

```markdown
> [!faq]- 기본 접힘
> 펼치기 전까지 숨겨진다.

> [!faq]+ 기본 펼침
> 접을 수 있지만 기본은 펼쳐져 있다.
```

## 중첩 콜아웃

```markdown
> [!question] 외부 콜아웃
> > [!note] 내부 콜아웃
> > 중첩 내용
```

## 지원 타입 목록

| 타입 | 별칭 | 색상 / 아이콘 |
|------|------|--------------|
| `note` | — | 파란색, 연필 |
| `abstract` | `summary`, `tldr` | 청록색, 클립보드 |
| `info` | — | 파란색, 정보 |
| `todo` | — | 파란색, 체크박스 |
| `tip` | `hint`, `important` | 시안, 불꽃 |
| `success` | `check`, `done` | 초록색, 체크마크 |
| `question` | `help`, `faq` | 노란색, 물음표 |
| `warning` | `caution`, `attention` | 주황색, 경고 |
| `failure` | `fail`, `missing` | 빨간색, X |
| `danger` | `error` | 빨간색, 번개 |
| `bug` | — | 빨간색, 버그 |
| `example` | — | 보라색, 목록 |
| `quote` | `cite` | 회색, 인용 |

## 커스텀 콜아웃 (CSS)

```css
.callout[data-callout="custom-type"] {
  --callout-color: 255, 0, 0;
  --callout-icon: lucide-alert-circle;
}
```
