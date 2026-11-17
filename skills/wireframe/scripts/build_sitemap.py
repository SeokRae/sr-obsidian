#!/usr/bin/env python3
"""앱 화면 사이트맵 (.excalidraw.md) 생성기.

입력
  --menu   : 메뉴 트리 JSON  [{id, label, sections: [{label, cards: [{title, risk, items: [{title, to}]}]}]}]
             (앱 어댑터의 메뉴 덤프가 만든다. 형식은 references/adapter.md)
  --pages  : routes.py 결과 (라우트 목록으로 쓴다)
  --config : 앱 어댑터 config.json (app, frontmatter, sitemap 절)
출력
  --out .excalidraw.md, --svg .svg

usage: python3 -I build_sitemap.py --exdraw <vault>/_scripts/excalidraw --config c.json --menu m.json
                                   --pages pages.json --out x.excalidraw.md --svg x.svg --rev <커밋>
"""
import argparse
import collections
import datetime
import json
import re
import sys

ap = argparse.ArgumentParser()
for k in ("exdraw", "config", "menu", "pages", "out", "svg", "rev"):
    ap.add_argument("--" + k, required=True)
A = ap.parse_args()
sys.path.insert(0, A.exdraw)
import exdraw  # noqa: E402

CFG = json.load(open(A.config, encoding="utf-8"))
SM = CFG.get("sitemap", {})
APP, REV, OUT_MD, OUT_SVG = CFG["app"], A.rev, A.out, A.svg
tabs = json.load(open(A.menu, encoding="utf-8"))
routes = [o["route"] for o in json.load(open(A.pages, encoding="utf-8"))]

B = exdraw.Builder("sm")
E = []
INK, MUTE, PH = "#343a40", "#868e96", "#f8f9fa"
LIVE, WRITE, SHARED = "#e03131", "#e8590c", "#7048e8"
COLW, GAP = 400, 48


def norm(p):
    return p.split("?")[0].split("#")[0]


# ---- 경로별 등장 탭 (여러 탭에서 쓰는 화면 표시용)
tabs_of = collections.defaultdict(set)
for t in tabs:
    for s in t["sections"]:
        for c in s["cards"]:
            for i in c["items"]:
                tabs_of[norm(i["to"])].add(t["id"])
menu_paths = set(tabs_of)


def in_menu(r):
    rx = "^" + re.sub(r":[^/]+", "[^/]+", r.replace("*", ".*")) + "$"
    return any(re.match(rx, m) for m in menu_paths)


outside = [r for r in routes if not in_menu(r)]


def txt(x, y, s, size=13, color=INK):
    e = B.text(x, y, s, size=size, stroke=color)
    E.append(e)
    return e


def card(x, y, title, risk, entries):
    """entries: [(label, path, shared)] -> 카드 높이 반환"""
    compact = all(not lb for lb, _, _ in entries)
    step = 20 if compact else 36
    h = 34 + len(entries) * step + 6
    stroke = {"live": LIVE, "write": WRITE}.get(risk, MUTE)
    E.append(B.rect(x, y, COLW, h, fill="#ffffff", stroke=stroke,
                    strokeWidth=2 if risk else 1, roundness={"type": 3}))
    tx = x + 12
    if risk:
        badge = {"live": "실결제", "write": "쓰기"}[risk]
        E.append(B.rect(tx, y + 8, 46, 20, fill="#ffffff", stroke=stroke, strokeWidth=1,
                        roundness={"type": 3}))
        E.append(B.label(tx + 23, y + 10, badge, size=11, stroke=stroke))
        tx += 54
    txt(tx, y + 9, title, size=14)
    for k, (label, path, shared) in enumerate(entries):
        ey = y + 36 + k * step
        if label:
            txt(x + 14, ey, label, size=12)
        txt(x + 14, ey + (16 if label else 0), path + ("   ↔ 다른 탭에도 있음" if shared else ""),
            size=11, color=SHARED if shared else MUTE)
    return h


def column(x, y, header, sub, sections):
    """sections: [(label, [(title, risk, entries)])]"""
    E.append(B.rect(x, y, COLW, 58, fill="#e7f5ff", stroke=INK, strokeWidth=2))
    txt(x + 14, y + 8, header, size=20)
    txt(x + 14, y + 34, sub, size=12, color=MUTE)
    cy = y + 76
    for label, cards in sections:
        txt(x, cy, label, size=15, color="#1971c2")
        cy += 26
        for title, risk, entries in cards:
            cy += card(x, cy, title, risk, entries) + 10
        cy += 12
    return cy


# ---- 제목, 범례
n_menu = len(routes) - len(outside)
txt(0, -230, f"{APP} 화면 사이트맵", size=34)
txt(0, -180, f"기준: {APP} {REV}. 탭 > 섹션 > 카드 > 화면(경로) 순서. "
    "메뉴 정의와 라우터 코드에서 자동 생성.", size=15, color=MUTE)
txt(0, -152, f"App.tsx 라우트 {len(routes)}개 | 홈 메뉴에서 닿는 라우트 {n_menu}개 | 메뉴 밖 라우트 {len(outside)}개 "
    "(결과, 가이드, 상세 화면)", size=15)
lx = 0
for color, s in [(LIVE, "실결제 카드"), (WRITE, "쓰기 카드"), (SHARED, "↔ 같은 화면을 여러 탭에서 씀")]:
    E.append(B.rect(lx, -112, 28, 18, fill="#ffffff", stroke=color, strokeWidth=2))
    txt(lx + 36, -112, s, size=13, color=color)
    lx += 290
txt(lx, -112, "\"프리셋 N개\" = 같은 화면에 결제수단, 카드사 값만 바꿔 들어가는 항목 수", size=13, color=MUTE)

# ---- 탭 열
x = 0
max_y = 0
for t in tabs:
    if t["id"] in SM.get("collapse_tabs", {}):
        collapse_path = SM["collapse_tabs"][t["id"]]
        n_docs = sum(len(c["items"]) for s in t["sections"] for c in s["cards"])
        secs = [(s["label"], [(c["title"], c["risk"], [(f"항목 {len(c['items'])}개", collapse_path, False)])
                              for c in s["cards"]]) for s in t["sections"]]
        sub = f"한 화면({collapse_path})으로 접음, 항목 {n_docs}개"
    else:
        secs = []
        n_paths = set()
        for s in t["sections"]:
            cards = []
            for c in s["cards"]:
                g = collections.OrderedDict()
                for i in c["items"]:
                    g.setdefault(norm(i["to"]), []).append(i)
                entries = []
                for p, items in g.items():
                    n_paths.add(p)
                    label = items[0]["title"] if len(items) == 1 else f"프리셋 {len(items)}개 ({items[0]['title']} 등)"
                    entries.append((label, p, len(tabs_of[p]) > 1))
                cards.append((c["title"], c["risk"], entries))
            secs.append((s["label"], cards))
        sub = f"섹션 {len(secs)}개 | 화면 {len(n_paths)}개"
    max_y = max(max_y, column(x, 0, t["label"], sub, secs))
    x += COLW + GAP

# ---- 메뉴 밖 라우트 열
def _hit(rule, r):
    return (r in rule.get("exact", []) or any(r.endswith(x) for x in rule.get("suffix", []))
            or any(x in r for x in rule.get("contains", [])))


rules = SM.get("outside_groups", [])
rest = SM.get("rest_label", "기타 화면")
bucket = collections.OrderedDict((g["label"], []) for g in rules)
bucket[rest] = []
for r in outside:
    g = next((g["label"] for g in rules if _hit(g, r)), rest)
    bucket[g].append(r)
secs = [(k, [(k, None, [("", r, False) for r in v])]) for k, v in bucket.items() if v]
max_y = max(max_y, column(x, 0, "메뉴 밖 라우트", f"홈 카드로 가지 않는 화면 {len(outside)}개", secs))

scn = exdraw.scene(E)
FM = CFG.get("frontmatter", {})
exdraw.save(OUT_MD, scn, tags=FM.get("tags", []) + ["sitemap"], extra_frontmatter=[
    "type: diagram", f"created: {datetime.date.today().isoformat()}"]
    + ([f"project: {FM['project']}"] if FM.get("project") else []) + [
    f"description: {APP} 화면 사이트맵. 탭 {len(tabs)}개, 섹션, 카드, 화면 경로, 메뉴 밖 라우트 {len(outside)}개. {REV} 기준 코드에서 자동 생성",
])
print(exdraw.to_svg(scn, OUT_SVG), "outside", len(outside))
