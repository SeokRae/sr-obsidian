#!/usr/bin/env python3
"""레이아웃 유형별 와이어프레임 (.excalidraw.md) 생성기.

입력
  --specs  : 대표 페이지 레이아웃 명세 폴더 (references/spec-schema.md 형식, *.json)
  --pages  : 유형(type)이 붙은 routes.py 결과 (앱 어댑터의 분류 규칙이 type 을 단다)
  --config : 앱 어댑터 config.json (app, frontmatter, wireframe 절: types, representative, extra)
출력
  기본       : --out 한 파일(.excalidraw.md)에 모든 화면, --svg 미리보기 한 장
  --split-dir: 화면 한 장을 파일 하나({split-dir}/{app}-{순번}-{명세 이름}.excalidraw.md)로 쓰고,
               --out 에는 목록 노트(.md: 유형, 화면 수, 대표, 링크, 같은 유형 화면)를 쓴다.
               --svg 는 미리보기 SVG 를 둘 폴더다.

usage: python3 -I build_wireframes.py --exdraw <vault>/_scripts/excalidraw --config c.json --specs specs/
                                      --pages pages.json --out x.excalidraw.md --svg x.svg --rev <커밋>
"""
import argparse
import collections
import datetime
import glob
import json
import os
import sys

ap = argparse.ArgumentParser()
for k in ("exdraw", "config", "specs", "pages", "out", "svg", "rev"):
    ap.add_argument("--" + k, required=True)
ap.add_argument("--split-dir", default=None)
A = ap.parse_args()
sys.path.insert(0, A.exdraw)
import exdraw  # noqa: E402

CFG = json.load(open(A.config, encoding="utf-8"))
WF = CFG["wireframe"]
APP, SPECS, PAGES, OUT_MD, OUT_SVG, REV = CFG["app"], A.specs, A.pages, A.out, A.svg, A.rev

INK, MUTE, PH, ACC, LINE = "#343a40", "#868e96", "#f1f3f5", "#e9ecef", "#dee2e6"
ANN = "#7048e8"
TONE = {"info": ("#e7f5ff", "#1971c2"), "warn": ("#fff4e6", "#e8590c"),
        "error": ("#fff5f5", "#e03131"), "ok": ("#ebfbee", "#2f9e44")}
PW, GUT, PAD = 760, 250, 14

TYPES = collections.OrderedDict((t, n) for t, n in WF["types"])
REPRESENTATIVE = WF["representative"]  # 유형 id -> 대표 라우트
EXTRA = WF.get("extra", [])            # 유형에서 크게 벗어나 따로 그릴 라우트

B = exdraw.Builder("wf")
E = []


# ------------------------------------------------------------------ 기본 도형
def tw(s, size):
    return sum(size * (1.0 if ord(ch) > 0x1100 else 0.58) for ch in s)


def wrap(s, size, width):
    out, cur = [], ""
    for word in str(s).split(" "):
        cand = (cur + " " + word).strip()
        if tw(cand, size) <= width or not cur:
            cur = cand
        else:
            out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out or [""]


def fit(s, size, width):
    s = str(s)
    if tw(s, size) <= width:
        return s
    while s and tw(s + "…", size) > width:
        s = s[:-1]
    return s + "…"


def T(x, y, s, size=13, color=INK):
    E.append(B.text(x, y, s, size=size, stroke=color))


def R(x, y, w, h, fill="#ffffff", stroke=MUTE, sw=1, rounded=False, dashed=False):
    E.append(B.rect(x, y, w, h, fill=fill, stroke=stroke, strokeWidth=sw,
                    roundness={"type": 3} if rounded else None,
                    strokeStyle="dashed" if dashed else "solid"))


def under(idx, fn):
    """fn이 그린 요소를 idx 위치로 옮겨, 이미 그린 내용 아래에 깔리게 한다."""
    n = len(E)
    fn()
    moved = E[n:]
    del E[n:]
    E[idx:idx] = moved


def C(cx, y, s, size=12, color=INK):
    E.append(B.label(cx, y, s, size=size, stroke=color))


# ------------------------------------------------------------------ 주석 거터
class Gutter:
    def __init__(self, x):
        self.x, self.last = x, -1e9

    def add(self, by, bx_right, text):
        y = max(by, self.last + 18)
        E.append(B.line(bx_right + 4, by + 8, [(0, 0), (self.x - bx_right - 10, y - by)],
                        stroke="#d0bfff", strokeWidth=1, strokeStyle="dotted"))
        T(self.x, y, fit(text, 11, GUT - 20), size=11, color=ANN)
        self.last = y


# ------------------------------------------------------------------ 블록 렌더
def blk(b, x, y, w, g):
    """블록 하나를 그리고 높이를 돌려준다."""
    t = b.get("type")
    h = {"header": hdr, "tabs": tabs, "banner": banner, "card": card, "row": row, "fields": fields,
         "buttons": buttons, "table": table, "kv": kv, "chart": chart, "diagram": diagram, "code": code,
         "list": lst, "grid": grid, "stats": stats, "text": text}.get(t, unknown)(b, x, y, w, g)
    if b.get("ann"):
        g.add(y, x + w, b["ann"])
    return h


def stack(blocks, x, y, w, g, gap=10):
    cy = y
    for b in blocks or []:
        cy += blk(b, x, cy, w, g) + gap
    return cy - y - (gap if blocks else 0)


def hdr(b, x, y, w, g):
    T(x, y, fit(b.get("title", ""), 22, w), size=22)
    if b.get("subtitle"):
        lines = wrap(b["subtitle"], 12, w)[:2]
        T(x, y + 32, "\n".join(lines), size=12, color=MUTE)
        return 32 + 16 * len(lines)
    return 30


def tabs(b, x, y, w, g):
    cx = x
    act = b.get("active", 0)
    for i, it in enumerate(b.get("items", [])):
        s = fit(it, 12, 150)
        bw = tw(s, 12) + 22
        if cx + bw > x + w:
            T(cx, y + 6, "…", size=12, color=MUTE)
            break
        R(cx, y, bw, 26, fill=ACC if i == act else "#ffffff", stroke=INK if i == act else MUTE, rounded=True)
        C(cx + bw / 2, y + 6, s, size=12)
        cx += bw + 6
    return 26


def banner(b, x, y, w, g):
    fill, stroke = TONE.get(b.get("tone", "info"), TONE["info"])
    lines = wrap(b.get("text", ""), 12, w - 24)[:3]
    h = 14 + 16 * len(lines)
    R(x, y, w, h, fill=fill, stroke=stroke, rounded=True)
    T(x + 12, y + 7, "\n".join(lines), size=12, color=stroke)
    return h


def card(b, x, y, w, g):
    title = b.get("title", "")
    if b.get("collapsed") and not b.get("children"):
        R(x, y, w, 34, rounded=True)
        T(x + 12, y + 9, "▸ " + fit(title, 13, w - 40), size=13)
        return 34
    if b.get("collapsed"):
        title = "▸ " + title  # 접힌 카드: 펼치기 전 요약 줄을 children 으로 그린다
    idx = len(E)
    inner = stack(b.get("children"), x + PAD, y + 40, w - 2 * PAD, g) if b.get("children") else 0
    h = 40 + inner + (PAD if b.get("children") else 0)
    under(idx, lambda: R(x, y, w, h, rounded=True))
    tx = x + 12
    if b.get("badge"):
        s = fit(b["badge"], 11, 90)
        bw = tw(s, 11) + 14
        R(tx, y + 10, bw, 18, stroke=INK, rounded=True)
        C(tx + bw / 2, y + 12, s, size=11)
        tx += bw + 8
    T(tx, y + 10, fit(title, 14, x + w - tx - 10), size=14)
    return h


def row(b, x, y, w, g):
    ch = b.get("children") or []
    if not ch:
        return 0
    ws = b.get("weights") or [1] * len(ch)
    gap = 12
    avail = w - gap * (len(ch) - 1)
    cx, hmax = x, 0
    for c, wt in zip(ch, ws):
        cw = avail * wt / sum(ws)
        hmax = max(hmax, blk(c, cx, y, cw, g))
        cx += cw + gap
    return hmax


def control(it, x, y, w):
    k, v = it.get("kind", "input"), it.get("value")
    if k == "more":
        T(x, y + 4, it.get("label", ""), size=12, color=MUTE)
        return 22
    if k in ("radio", "checkbox"):
        mark = "◯" if k == "radio" else "☐"
        T(x, y + 4, fit(f"{mark} {it.get('label', '')}" + (f"  ({v})" if v else ""), 12, w), size=12)
        return 22
    T(x, y, fit(it.get("label", ""), 11, w), size=11, color=MUTE)
    hh = 52 if k == "textarea" else 26
    R(x, y + 16, w, hh)
    ph = v or {"select": "선택 ▾", "date": "YYYY-MM-DD"}.get(k, "")
    if ph:
        T(x + 8, y + 22, fit(str(ph) + (" ▾" if k == "select" and v else ""), 11, w - 16), size=11, color=MUTE)
    return 16 + hh + 4


def fields(b, x, y, w, g):
    items = b.get("items", [])
    cols = 2 if w >= 480 else 1
    cw = (w - 16 * (cols - 1)) / cols
    cy, h = y, 0
    for i in range(0, len(items), cols):
        rh = 0
        for j, it in enumerate(items[i:i + cols]):
            rh = max(rh, control(it, x + j * (cw + 16), cy, cw))
        cy += rh + 6
    return cy - y - 6 if items else 0


def buttons(b, x, y, w, g):
    cx = x
    for it in b.get("items", []):
        s = fit(it.get("label", ""), 12, 180)
        bw = tw(s, 12) + 26
        if cx + bw > x + w:
            break
        R(cx, y, bw, 28, fill="#ced4da" if it.get("primary") else ACC, stroke=INK, rounded=True)
        C(cx + bw / 2, y + 7, s, size=12)
        cx += bw + 8
    return 28


def table(b, x, y, w, g):
    cols = b.get("columns", []) or ["…"]
    n = min(int(b.get("rows", 3) or 3), 5)
    show = cols[:max(1, int(w // 90))]
    cw = w / len(show)
    R(x, y, w, 26 + n * 22, stroke=MUTE)
    E.append(B.rect(x, y, w, 26, fill=ACC, stroke=MUTE, strokeWidth=1))
    for i, c in enumerate(show):
        lab = c if i < len(show) - 1 or len(show) == len(cols) else f"{c} 외 {len(cols) - len(show)}"
        T(x + i * cw + 6, y + 6, fit(lab, 11, cw - 10), size=11)
    for r in range(n):
        ry = y + 26 + r * 22
        if r:
            E.append(B.line(x, ry, [(0, 0), (w, 0)], stroke=LINE, strokeWidth=1))
        for i in range(len(show)):
            E.append(B.rect(x + i * cw + 6, ry + 8, min(cw - 16, 60), 6, fill=PH, stroke=PH, strokeWidth=1))
    return 26 + n * 22


def kv(b, x, y, w, g):
    keys = b.get("keys", [])[:10]
    kw = min(220, w * 0.4)
    for i, k in enumerate(keys):
        ry = y + i * 22
        E.append(B.line(x, ry + 21, [(0, 0), (w, 0)], stroke=LINE, strokeWidth=1))
        T(x + 4, ry + 4, fit(k, 11, kw - 8), size=11, color=MUTE)
        E.append(B.rect(x + kw, ry + 8, min(w - kw - 8, 120), 6, fill=PH, stroke=PH, strokeWidth=1))
    return 22 * len(keys)


def ph_box(b, x, y, w, h, label, dashed=False):
    R(x, y, w, h, fill=PH, dashed=dashed)
    C(x + w / 2, y + h / 2 - 8, fit(label, 12, w - 20), size=12, color=MUTE)


def chart(b, x, y, w, g):
    h = 130
    R(x, y, w, h, fill="#ffffff")
    pts = [(0, 80), (w * .15, 60), (w * .3, 70), (w * .45, 35), (w * .6, 50), (w * .75, 25), (w - 30, 40)]
    E.append(B.line(x + 15, y + 20, pts, stroke="#adb5bd", strokeWidth=2))
    T(x + 10, y + h - 20, fit("차트: " + b.get("label", ""), 11, w - 20), size=11, color=MUTE)
    return h


def diagram(b, x, y, w, g):
    h = 120
    R(x, y, w, h, fill="#ffffff", dashed=True)
    bw = min(90, (w - 80) / 3)
    for i in range(3):
        bx = x + 20 + i * (bw + 30)
        R(bx, y + 30, bw, 34, fill=PH, rounded=True)
        if i < 2:
            E.append(B.arrow(bx + bw + 2, y + 47, [(0, 0), (26, 0)], stroke=MUTE, strokeWidth=1))
    T(x + 10, y + h - 22, fit("흐름도: " + b.get("label", ""), 11, w - 20), size=11, color=MUTE)
    return h


def code(b, x, y, w, g):
    ph_box(b, x, y, w, 70, "{ … }  " + b.get("label", ""), dashed=True)
    return 70


def lst(b, x, y, w, g):
    items = b.get("items", [])[:8]
    for i, it in enumerate(items):
        T(x, y + i * 20, fit("• " + str(it), 12, w), size=12)
    return 20 * len(items)


def grid(b, x, y, w, g):
    items = b.get("items", [])[:12]
    cols = max(1, min(int(b.get("cols", 3) or 3), 4))
    cw = (w - 8 * (cols - 1)) / cols
    for i, it in enumerate(items):
        r, c = divmod(i, cols)
        R(x + c * (cw + 8), y + r * 58, cw, 50, rounded=True)
        C(x + c * (cw + 8) + cw / 2, y + r * 58 + 17, fit(it, 12, cw - 12), size=12)
    rows = (len(items) + cols - 1) // cols
    return rows * 58 - 8 if items else 0


def stats(b, x, y, w, g):
    items = b.get("items", [])[:6] or [{"label": "…"}]
    cw = (w - 8 * (len(items) - 1)) / len(items)
    for i, it in enumerate(items):
        bx = x + i * (cw + 8)
        R(bx, y, cw, 54, rounded=True)
        T(bx + 8, y + 6, fit(it.get("label", ""), 11, cw - 14), size=11, color=MUTE)
        T(bx + 8, y + 24, fit(str(it.get("value", "000")), 18, cw - 14), size=18)
    return 54


def text(b, x, y, w, g):
    lines = wrap(b.get("text", ""), 12, w)[:4]
    T(x, y, "\n".join(lines), size=12, color=MUTE)
    return 16 * len(lines)


def unknown(b, x, y, w, g):
    ph_box(b, x, y, w, 40, f"({b.get('type')})")
    return 40


# ------------------------------------------------------------------ 페이지 프레임
def page(spec, x, y, caption, members):
    """caption: 위 제목줄, members: 같은 유형 라우트 목록. 차지한 높이를 돌려준다."""
    T(x, y, caption, size=20)
    T(x, y + 28, f"{spec['route']}   {spec.get('file', '')}", size=12, color=MUTE)
    fy = y + 54
    g = Gutter(x + PW + 40)
    T(g.x, fy - 20, "컴포넌트", size=11, color=ANN)
    inner_y = fy + 26 + 34 + 16
    idx = len(E)
    body = stack(spec.get("blocks"), x + 20, inner_y, PW - 40, g, gap=12)
    fh = 26 + 34 + 16 + body + 24
    under(idx, lambda: R(x, fy, PW, fh, stroke=INK, sw=2))
    R(x, fy, PW, 26, fill=ACC, stroke=INK)
    for i in range(3):
        E.append(B.ellipse(x + 10 + i * 16, fy + 8, 10, 10, fill="#adb5bd", stroke=MUTE, strokeWidth=1))
    R(x + 1, fy + 27, PW - 2, 34, fill=PH, stroke=PH)
    T(x + 16, fy + 36, "공통 헤더 (별도 '공통 헤더' 그림 참조)", size=11, color=MUTE)
    cy = fy + fh + 14
    if spec.get("notes"):
        T(x, cy, "메모", size=12, color=MUTE)
        lines = []
        for n in spec["notes"][:5]:
            lines += wrap("- " + n, 12, PW + GUT)
        T(x, cy + 18, "\n".join(lines), size=12, color=INK)
        cy += 18 + 16 * len(lines) + 8
    if members is not None:
        T(x, cy, f"이 와이어프레임으로 보는 화면 {len(members)}개", size=12, color="#1971c2")
        lines = wrap(", ".join(members), 12, PW + GUT)
        T(x, cy + 18, "\n".join(lines), size=12, color=INK)
        cy += 18 + 16 * len(lines)
    return cy - y


# ------------------------------------------------------------------ 배치
specs = {}
for p in glob.glob(os.path.join(SPECS, "*.json")):
    s = json.load(open(p, encoding="utf-8"))
    s["_name"] = os.path.splitext(os.path.basename(p))[0]
    specs[s["route"]] = s
pages = json.load(open(PAGES, encoding="utf-8"))
by_type = collections.defaultdict(list)
for o in pages:
    by_type[o["type"]].append(o["route"])

slots = []  # (spec, caption, members, slug, 유형 id)
if "(공통)" in specs:
    slots.append((specs["(공통)"], "공통 헤더 (모든 화면 위)", None, f"00-{specs['(공통)']['_name']}", "-"))
for k, (tid, name) in enumerate(TYPES.items(), 1):
    r = REPRESENTATIVE[tid]
    if r in specs:
        slots.append((specs[r], f"{tid} {name}  | 대표 {r}", by_type[tid], f"{k:02d}-{tid}-{specs[r]['_name']}", tid))
for k, r in enumerate(EXTRA, 1):
    if r in specs:
        t = next(o["type"] for o in pages if o["route"] == r)
        slots.append((specs[r], f"따로 그린 화면 ({t})  | {r}", None, f"x{k:02d}-{specs[r]['_name']}", t))

n_routes = len(pages)
n_skip = sum(1 for o in pages if o.get("type") not in TYPES)
FM = CFG.get("frontmatter", {})
TODAY = datetime.date.today().isoformat()
DESC_ALL = (f"라우트 {n_routes}개를 레이아웃 유형 {len(TYPES)}개로 묶고 유형별 대표 페이지와 "
            f"따로 그릴 화면 {len(EXTRA)}장을 실제 JSX 순서대로 그림. {REV} 기준")
missing = [REPRESENTATIVE[t] for t in TYPES if REPRESENTATIVE[t] not in specs] + [r for r in EXTRA if r not in specs]


def fm(desc):
    return ["type: diagram", f"created: {TODAY}"] + ([f"project: {FM['project']}"] if FM.get("project") else []) \
        + [f"description: {desc}"]


def legend(y):
    T(0, y, "보라색 글씨는 그 영역을 그리는 React 컴포넌트, '(실행 뒤)'는 요청 실행 뒤에만 보이는 영역.", size=15, color=MUTE)


if not A.split_dir:
    # ---- 합본: 한 파일에 4열로
    T(0, -200, f"{APP} 화면 와이어프레임 (레이아웃 유형별)", size=34)
    T(0, -150, f"기준: {APP} {REV}. 라우트 {n_routes}개(화면 없는 {n_skip}개 제외)를 레이아웃 유형 {len(TYPES)}개로 묶고, "
      f"유형마다 대표 페이지 1장을 실제 JSX 순서대로 그렸다. 유형에서 크게 벗어나는 화면 {len(EXTRA)}장은 따로 그렸다.",
      size=15, color=MUTE)
    legend(-122)
    NCOL = 4
    SW = PW + GUT + 140
    col_y = [0] * NCOL
    for spec, cap, mem, _, _ in slots:
        c = min(range(NCOL), key=lambda i: col_y[i])
        col_y[c] += page(spec, c * SW, col_y[c], cap, mem) + 120
    scn = exdraw.scene(E)
    exdraw.save(OUT_MD, scn, tags=FM.get("tags", []) + ["wireframe"], extra_frontmatter=fm(f"{APP} 화면 와이어프레임. {DESC_ALL}"))
    print(exdraw.to_svg(scn, OUT_SVG), "slots", len(slots), "missing", missing)
    sys.exit(0)

# ---- 분리: 화면 한 장 = 파일 하나, 목록 노트 하나
os.makedirs(A.split_dir, exist_ok=True)
os.makedirs(OUT_SVG, exist_ok=True)
# vault 안에서 다른 앱의 같은 이름 파일과 겹치지 않게 앱 이름을 앞에 붙인다
slots = [(sp, cap, mem, f"{APP}-{slug}", tid) for sp, cap, mem, slug, tid in slots]
for spec, cap, mem, slug, tid in slots:
    E.clear()
    B = exdraw.Builder("wf")  # noqa: F811  파일마다 id 를 새로 매긴다
    T(0, -86, f"{APP} {REV}", size=13, color=MUTE)
    legend(-62)
    page(spec, 0, 0, cap, mem)
    scn = exdraw.scene(E)
    exdraw.save(os.path.join(A.split_dir, slug + ".excalidraw.md"), scn,
                tags=FM.get("tags", []) + ["wireframe"],
                extra_frontmatter=fm(f"{APP} 와이어프레임: {cap.replace('  |', ',')}. {REV} 기준"))
    exdraw.to_svg(scn, os.path.join(OUT_SVG, slug + ".svg"))

fold = os.path.basename(os.path.normpath(A.split_dir))
title = os.path.splitext(os.path.basename(OUT_MD))[0]
link = lambda slug, text: f"[[{slug}.excalidraw\\|{text}]]"  # noqa: E731  표 안이라 별칭 구분자를 \| 로 쓴다
rows, details = [], []
for spec, cap, mem, slug, tid in slots:
    if tid == "-" and mem is None and spec["route"] == "(공통)":
        rows.append(f"| - | 공통 헤더 | 모든 화면 | - | {link(slug, '열기')} |")
    elif mem is not None:
        rows.append(f"| {tid} | {TYPES[tid]} | {len(mem)} | `{spec['route']}` | {link(slug, '열기')} |")
        details.append(f"> [!note]- {tid} {TYPES[tid]} ({len(mem)}개)\n" + "\n".join(f"> - `{r}`" for r in mem))
    else:
        rows.append(f"| {tid} (따로) | {spec.get('title', '')} | 1 | `{spec['route']}` | {link(slug, '열기')} |")
body = f"""---
{chr(10).join(fm(f"{APP} 화면 와이어프레임 목록. {DESC_ALL}. 화면 한 장이 파일 하나"))}
tags: [{", ".join(FM.get("tags", []) + ["wireframe"])}]
---

# {APP} 화면 와이어프레임

> [!summary]
> {APP} {REV} 기준. 라우트 {n_routes}개(화면 없는 {n_skip}개 제외)를 레이아웃 유형 {len(TYPES)}개로 묶었습니다.
> 유형마다 대표 페이지 1장을 그렸고, 유형에서 크게 벗어나는 화면 {len(EXTRA)}장은 따로 그렸습니다. 그림은 `{fold}/` 에 한 장씩 있어요.

| 유형 | 이름 | 화면 수 | 대표 | 와이어프레임 |
|---|---|---|---|---|
{chr(10).join(rows)}

## 유형별 화면 목록

{chr(10).join(d + chr(10) for d in details)}
"""
open(OUT_MD, "w", encoding="utf-8").write(body)
print("split", len(slots), "->", A.split_dir, "| index", OUT_MD, "| missing", missing)
