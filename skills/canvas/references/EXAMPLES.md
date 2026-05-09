# JSON Canvas 완성 예시

## 예시 1: ISS 인시던트 타임라인

3단계 인시던트 흐름 (발생 → 대응 → 완료):

```json
{
  "nodes": [
    {
      "id": "aa11bb22cc33dd44",
      "type": "text",
      "text": "## 인시던트 발생\n2025-05-01 14:30\n결제 오류 급증",
      "x": 0,
      "y": 100,
      "width": 280,
      "height": 120,
      "color": "1"
    },
    {
      "id": "bb22cc33dd44ee55",
      "type": "text",
      "text": "## 원인 파악\n14:45\nStripe webhook 누락 확인",
      "x": 350,
      "y": 100,
      "width": 280,
      "height": 120,
      "color": "3"
    },
    {
      "id": "cc33dd44ee55ff66",
      "type": "text",
      "text": "## 조치 완료\n15:20\nwebhook 재처리 + 모니터링",
      "x": 700,
      "y": 100,
      "width": 280,
      "height": 120,
      "color": "4"
    },
    {
      "id": "dd44ee55ff66aa77",
      "type": "file",
      "file": "10-projects/ISS-042-결제오류/ISS-042 허브.md",
      "x": 350,
      "y": 300,
      "width": 280,
      "height": 200
    }
  ],
  "edges": [
    {
      "id": "ee55ff66aa77bb88",
      "fromNode": "aa11bb22cc33dd44",
      "fromSide": "right",
      "toNode": "bb22cc33dd44ee55",
      "toSide": "left"
    },
    {
      "id": "ff66aa77bb88cc99",
      "fromNode": "bb22cc33dd44ee55",
      "fromSide": "right",
      "toNode": "cc33dd44ee55ff66",
      "toSide": "left"
    },
    {
      "id": "aa77bb88cc99dd00",
      "fromNode": "bb22cc33dd44ee55",
      "fromSide": "bottom",
      "toNode": "dd44ee55ff66aa77",
      "toSide": "top",
      "label": "상세 기록"
    }
  ]
}
```

---

## 예시 2: 서비스 의존관계 맵

결제 서비스 레이어 구조:

```json
{
  "nodes": [
    {
      "id": "1a2b3c4d5e6f7a8b",
      "type": "group",
      "label": "결제 레이어",
      "x": -50,
      "y": -50,
      "width": 700,
      "height": 300,
      "color": "5"
    },
    {
      "id": "2b3c4d5e6f7a8b9c",
      "type": "text",
      "text": "untact\n비대면 결제",
      "x": 0,
      "y": 0,
      "width": 200,
      "height": 80
    },
    {
      "id": "3c4d5e6f7a8b9c0d",
      "type": "text",
      "text": "psp-service\nStripe 연동",
      "x": 250,
      "y": 0,
      "width": 200,
      "height": 80
    },
    {
      "id": "4d5e6f7a8b9c0d1e",
      "type": "text",
      "text": "npg-core\nNICE 연동",
      "x": 500,
      "y": 0,
      "width": 150,
      "height": 80
    },
    {
      "id": "5e6f7a8b9c0d1e2f",
      "type": "text",
      "text": "Stripe\n외부 PG",
      "x": 250,
      "y": 200,
      "width": 200,
      "height": 80,
      "color": "2"
    },
    {
      "id": "6f7a8b9c0d1e2f3a",
      "type": "text",
      "text": "NICE\n외부 PG",
      "x": 500,
      "y": 200,
      "width": 150,
      "height": 80,
      "color": "2"
    }
  ],
  "edges": [
    {
      "id": "7a8b9c0d1e2f3a4b",
      "fromNode": "2b3c4d5e6f7a8b9c",
      "fromSide": "right",
      "toNode": "3c4d5e6f7a8b9c0d",
      "toSide": "left",
      "label": "결제 요청"
    },
    {
      "id": "8b9c0d1e2f3a4b5c",
      "fromNode": "2b3c4d5e6f7a8b9c",
      "fromSide": "right",
      "toNode": "4d5e6f7a8b9c0d1e",
      "toSide": "left"
    },
    {
      "id": "9c0d1e2f3a4b5c6d",
      "fromNode": "3c4d5e6f7a8b9c0d",
      "fromSide": "bottom",
      "toNode": "5e6f7a8b9c0d1e2f",
      "toSide": "top"
    },
    {
      "id": "0d1e2f3a4b5c6d7e",
      "fromNode": "4d5e6f7a8b9c0d1e",
      "fromSide": "bottom",
      "toNode": "6f7a8b9c0d1e2f3a",
      "toSide": "top"
    }
  ]
}
```

---

## 예시 3: 마인드맵 (주제 분기)

```json
{
  "nodes": [
    {
      "id": "a1a1a1a1a1a1a1a1",
      "type": "text",
      "text": "**결제 시스템**",
      "x": 300,
      "y": 200,
      "width": 200,
      "height": 80,
      "color": "5"
    },
    {
      "id": "b2b2b2b2b2b2b2b2",
      "type": "text",
      "text": "PG 연동",
      "x": 0,
      "y": 0,
      "width": 180,
      "height": 70
    },
    {
      "id": "c3c3c3c3c3c3c3c3",
      "type": "text",
      "text": "정산",
      "x": 600,
      "y": 0,
      "width": 180,
      "height": 70
    },
    {
      "id": "d4d4d4d4d4d4d4d4",
      "type": "text",
      "text": "취소/환불",
      "x": 0,
      "y": 400,
      "width": 180,
      "height": 70
    },
    {
      "id": "e5e5e5e5e5e5e5e5",
      "type": "text",
      "text": "모니터링",
      "x": 600,
      "y": 400,
      "width": 180,
      "height": 70
    }
  ],
  "edges": [
    {
      "id": "f6f6f6f6f6f6f6f6",
      "fromNode": "a1a1a1a1a1a1a1a1",
      "fromSide": "left",
      "toNode": "b2b2b2b2b2b2b2b2",
      "toSide": "right"
    },
    {
      "id": "a7a7a7a7a7a7a7a7",
      "fromNode": "a1a1a1a1a1a1a1a1",
      "fromSide": "right",
      "toNode": "c3c3c3c3c3c3c3c3",
      "toSide": "left"
    },
    {
      "id": "b8b8b8b8b8b8b8b8",
      "fromNode": "a1a1a1a1a1a1a1a1",
      "fromSide": "left",
      "toNode": "d4d4d4d4d4d4d4d4",
      "toSide": "right"
    },
    {
      "id": "c9c9c9c9c9c9c9c9",
      "fromNode": "a1a1a1a1a1a1a1a1",
      "fromSide": "right",
      "toNode": "e5e5e5e5e5e5e5e5",
      "toSide": "left"
    }
  ]
}
```
