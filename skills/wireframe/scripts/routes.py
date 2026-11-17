#!/usr/bin/env python3
"""React Router 라우트 → 페이지 파일 → JSX 부품 목록을 뽑는다.

라우터 파일에서 `<Route path="..." element={<Comp ...` 와 `lazy(() => import('./...'))`,
`import Comp from './...'` 를 읽어 라우트마다 페이지 파일을 찾고, 그 파일과 같은 트리의
로컬 하위 컴포넌트(1단계, components/ 제외)가 쓰는 JSX 태그를 센다.

usage: python3 -I routes.py --src <src 절대경로> --router <src 기준 라우터 파일> --out pages.json
출력: [{route, comp, file, lines, tags}]  (tags: {JSX 태그: 횟수})
"""
import argparse
import collections
import json
import os
import re

ap = argparse.ArgumentParser()
ap.add_argument("--src", required=True)
ap.add_argument("--router", default="App.tsx")
ap.add_argument("--out", required=True)
a = ap.parse_args()

SRC = os.path.expanduser(a.src)
app = open(os.path.join(SRC, a.router), encoding="utf-8").read()
imp = {}
for m in re.finditer(r"const (\w+)\s*=\s*lazy\(\(\) => import\('\./([^']+)'\)\)", app):
    imp[m[1]] = m[2]
for m in re.finditer(r"import (\w+) from '\./([^']+)'", app):
    imp[m[1]] = m[2]
routes = [(m[1], m[2], imp.get(m[2]))
          for m in re.finditer(r'<Route\s+path="([^"]+)"\s+element=\{<(\w+)', app)]


def tags(path, depth=0, seen=None):
    seen = seen if seen is not None else set()
    if not path or path in seen or not os.path.exists(path):
        return collections.Counter()
    seen.add(path)
    s = open(path, encoding="utf-8").read()
    c = collections.Counter(re.findall(r"<([A-Z]\w+)", s))
    if depth < 1:
        for m in re.finditer(r"import (?:\{[^}]*\}|\w+)[^;]*from '(\.{1,2}/[^']+)'", s):
            p = os.path.normpath(os.path.join(os.path.dirname(path), m[1]))
            for ext in ("", ".tsx", "/index.tsx"):
                q = p + ext
                if os.path.exists(q) and q.endswith(".tsx") and "/components/" not in q:
                    c += tags(q, depth + 1, seen)
    return c


out = []
for r, comp, f in routes:
    p = os.path.join(SRC, f) if f else None
    lines = len(open(p, encoding="utf-8").read().splitlines()) if p and os.path.exists(p) else 0
    out.append({"route": r, "comp": comp, "file": f, "lines": lines, "tags": dict(tags(p))})
json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"routes {len(out)} | no file {sum(1 for o in out if not o['file'])} -> {a.out}")
