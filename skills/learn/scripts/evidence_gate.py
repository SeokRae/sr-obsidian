#!/usr/bin/env python3
"""
evidence_gate.py: sr-obsidian:learn 출처 대조 관문의 빈 근거 칸 검사 (읽기 전용, #300)

마크다운 표의 마지막 칸이 비어 있는 행을 찾는다. 시나리오 노트와 흐름 문서는 표마다
마지막 열이 근거나 연결 칸이라, 그 칸이 비면 관문을 통과하지 못한다.
칸 값이 출처와 맞는지는 보지 않는다. 그 대조는 learn-verifier 에이전트가 한다.

사용법:
  python3 evidence_gate.py "{시나리오 초안}.md"

종료 코드: 빈 칸이 없으면 0, 있으면 1
"""
import re
import sys

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
