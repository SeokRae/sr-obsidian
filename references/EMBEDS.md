# Embeds Reference

## 노트 임베드

```markdown
![[파일명]]
![[파일명#헤딩]]
![[파일명#^block-id]]
![[폴더/경로/파일명]]      같은 파일명이 여럿일 때
```

임베드 대상도 링크와 같이 H1 제목이 아니라 실제 파일명(`.md` 제외)이나 vault 기준 경로입니다. 자세한 규칙은 [obsidian-markdown](obsidian-markdown.md)의 `링크 대상 규칙`을 따라요.

## 이미지 임베드

```markdown
![[이미지.png]]
![[이미지.png|640x480]]    너비 x 높이
![[이미지.png|300]]        너비만 지정 (비율 유지)
```

## 외부 이미지

```markdown
![대체 텍스트](https://example.com/image.png)
![대체 텍스트|300](https://example.com/image.png)
```

## 오디오 임베드

```markdown
![[audio.mp3]]
![[audio.ogg]]
```

## PDF 임베드

```markdown
![[문서.pdf]]
![[문서.pdf#page=3]]
![[문서.pdf#height=400]]
```

## 목록 임베드

```markdown
![[파일명#^list-id]]
```

목록에 블록 ID 정의:

```markdown
- 항목 1
- 항목 2
- 항목 3

^list-id
```

## 검색 결과 임베드

````markdown
```query
tag:#project status:done
```
````

## HTML iframe (Obsidian 로컬 파일)

`![[.html]]`은 동작하지 않음. 로컬 HTML 다이어그램은 iframe 사용:

```html
<iframe src="file:///Users/sr/obsidian/sr-labs/{상대경로}.html"
        width="100%" height="3400" style="border:none;border-radius:8px;"></iframe>
```

height 기준: 시퀀스 다이어그램 37 steps ≈ 3000px SVG → `height="3400"` 권장.
