#!/usr/bin/env python3
"""
relink.py: sr-obsidian:migrate 의 링크 갱신 엔진 (#8609)

파일을 옮긴 뒤 vault 전체에서 그 파일을 가리키던 링크를 새 경로로 고친다.
예전 migrate 는 서비스 폴더 안에서만 문자열 치환을 해서 서비스 밖 참조가 깨진 채 남았다.
기본은 dry-run(보고만)이고 --apply 일 때만 파일을 쓴다.
백업 사본은 만들지 않는다. 안전망은 git 이다 (#8607 D4).

고치는 링크 형식
  - 위키링크와 임베드 (본문, frontmatter): [[x]] [[x|표시명]] [[x\\|표시명]] [[x#앵커]] ![[x]]
  - markdown 링크: [t](상대경로) [t](/vault 루트 기준) [t](<공백 있는 경로>), 퍼센트 인코딩 포함
  - canvas 파일 노드: {"type": "file", "file": "vault 루트 기준 경로"}
  - file:// 절대경로: iframe src 같은 file://{vault}/경로 (md, html)

판정 규칙 (#8607 D6, 해석 규칙은 vault _scripts/vault-review.py 와 같다. #8608 에서 Obsidian 실측으로 맞춘 규칙)
  - [[X]] 는 파일명과 경로로만 해석한다. H1 제목이나 aliases 로는 해석하지 않는다.
  - 경로형은 전체 경로 또는 경로 접미사가 맞아야 한다. ./ ../ 는 출처 폴더 기준, 루트 위로 넘치면 루트에서 멈춘다.
  - 같은 파일명이 여럿이면 출처와 같은 폴더, 출처 폴더 하위, 가장 짧은 경로 순으로 하나를 고른다.
  - markdown 링크는 출처 파일 기준 상대경로(또는 / 로 시작하면 vault 루트 기준)로 해석한다.
  - 코드 블록 판정도 vault-review.py strip_fences 와 같다 (여는 fence 와 같은 인용 깊이, 같은 문자,
    같거나 긴 길이, info string 없는 줄에서만 닫힘).
  링크마다 "이동 전에 가리키던 파일"을 구하고, 이동 후에도 같은 파일(옮겼으면 새 경로)을 가리키는지 본다.
  달라지면 원래 형식(파일명형, 상대경로형, 경로형)을 유지해 대상만 고친다. 그 형식으로 풀리지 않으면
  vault 루트 기준 전체 경로로 쓴다. 파일명형을 경로형으로 바꿀 때 표시명이 없으면 원래 텍스트를 표시명으로 붙인다.
  부분 경로형(docs/x 처럼 전체 경로가 아닌 경로형)은 새 위치의 파일명이 vault 에서 유일하면 파일명형으로,
  아니면 전체 경로로 쓴다 (#8607 D6: 파일명형이 기본, 같은 파일명이 여럿일 때만 경로형).
  이동 전부터 깨져 있던 링크는 건드리지 않는다.

고치지 않고 보고만 하는 것
  - [dirty] 이 스크립트 실행 전부터 미커밋 변경이 있는 파일. 다른 작업일 수도, 앞선 relink --apply 결과일 수도 있다
    (공유 워킹트리. --include-dirty 로 해제)
  - [dirty-move] 이동 대상 파일 자체에 미커밋 변경이 있음. git mv 전이면 OLD 의 git status,
    후면 NEW 의 작업트리 변경, 인덱스 내용이 HEAD 의 OLD 와 다름, 미추적(??)을 본다. HEAD 에 없는 파일
    (미추적, 무시된 파일)도 여기 든다. 폴더째 옮기면 이런 파일도 같이 옮겨지기 때문이다.
    이 파일 안의 링크도 고치지 않는다 (--include-dirty 로 해제)
  - [report-only] .claude/ 아래 파일 (Obsidian 이 색인하지 않는 에이전트 설정)
  - [plain] 링크 문법이 아닌 평문 경로 언급 (코드 블록, 백틱, frontmatter source 같은 자유 텍스트)
  - [folder-ref] 이동으로 비는 폴더의 경로 참조 (Dataview FROM "폴더", dv.pages('"폴더"'),
    Bases file.inFolder("폴더") 등). 쿼리 결과가 조용히 비게 되니 사람이 고친다
    60-logs/ 의 평문 언급과 폴더 경로 언급은 기록이라 건수만 센다 (#8607 D6)
  - [html-rel] 옮긴 HTML 안의 상대경로 src, href

사용법 (vault 루트 기준 경로):
  python3 relink.py --vault /path/to/vault --move OLD NEW [--move OLD NEW ...]
  python3 relink.py --vault /path/to/vault --map moves.tsv          # 한 줄에 "OLD<TAB>NEW", # 주석
  python3 relink.py ... --apply                                      # 실제로 쓴다
  OLD, NEW 가 폴더면 안의 파일 전체로 펼친다. git mv 전(OLD 존재)과 후(NEW 존재) 어느 쪽에서 돌려도 된다.
  폴더 쌍은 폴더째 옮긴 경우에만 쓴다. 이미 있던 폴더로 합쳤다면 git mv 뒤에는 원래 있던 파일과
  옮겨 온 파일을 구분할 수 없으니 파일 쌍으로 적는다.
  --apply 는 이동 쌍 전체를 한 맵에 넣고 한 번만 돌린다. 나눠서 돌리면 앞 실행이 고친 파일이 커밋 전까지
  미커밋 파일이라 뒤 실행에서 [dirty] 로 보류된다. 나눌 때는 사이에 커밋한다.

종료 코드: 0 정상, 1 사용법 오류, 2 이동 쌍 충돌(OLD 와 NEW 가 둘 다 있거나 둘 다 없음)
"""
from __future__ import annotations

import argparse
import json
import os
import posixpath
import re
import subprocess
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote, unquote

SKIP_DIRS = {"_backups", "node_modules"}          # 링크 대상으로도, 출처로도 보지 않는다 (#8607 D4)
REPORT_ONLY_DOT_DIRS = {".claude"}                 # 점 폴더 중 보고만 하는 곳 (링크 해석 인덱스에는 넣지 않는다)
SKIP_SUBDIRS = {".claude/worktrees"}               # 에이전트 worktree 는 vault 사본이라 아예 보지 않는다
LINK_EXT = {".md", ".canvas", ".html", ".htm"}     # 링크를 고치는 파일
MENTION_EXT = LINK_EXT | {".base"}                 # 평문 언급을 찾는 파일
LOG_PREFIX = "60-logs/"

WIKI = re.compile(r"(!?)\[\[([^\[\]\n]+?)\]\]")
MD_LINK = re.compile(
    r"(?<!\\)!?\[[^\]\n]*\]\(\s*"
    r"(?:<(?P<angle>[^>\n]+)>|(?P<raw>(?:[^()\s]|\([^()\s]*\))+))"
    r"(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)")
CANVAS_FILE = re.compile(r'("file"\s*:\s*)("(?:[^"\\]|\\.)*")')
INLINE_CODE = re.compile(r"`[^`\n]+`")
FENCE = re.compile(r"^((?:\s{0,3}>)*)\s{0,3}(`{3,}|~{3,})(.*)$")   # vault-review.py FENCE 와 같다
URL_SCHEME = re.compile(r"^[a-z][a-z0-9+.\-]*:", re.IGNORECASE)
BAD_PERCENT = re.compile(r"%(?![0-9A-Fa-f]{2})")
PCT = re.compile(r"%[0-9A-Fa-f]{2}")
HTML_REL_REF = re.compile(r"""\b(?:src|href)\s*=\s*["']([^"'#][^"']*)["']""", re.IGNORECASE)


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


# ── 해석 ────────────────────────────────────────────────────────
def obsidian_pick(cands: list, src: str) -> str:
    """같은 파일명 후보 중 Obsidian 이 고르는 파일. vault _scripts/vault-review.py 의 obsidian_pick 과 같다.
    출처와 같은 폴더, 출처 폴더 하위(가장 짧은 경로), 그 밖에서 가장 짧은 경로 순이고,
    길이가 같으면 출처 폴더와 공통 경로가 긴 쪽을 고른다."""
    sdir = posixpath.dirname(src)
    same = sorted(c for c in cands if posixpath.dirname(c) == sdir)
    if same:
        return same[0]
    sparts = sdir.split("/") if sdir else []

    def common(c):
        cparts = posixpath.dirname(c).split("/")
        k = 0
        while k < min(len(sparts), len(cparts)) and sparts[k] == cparts[k]:
            k += 1
        return k

    if sdir:
        sub = [c for c in cands if c.startswith(sdir + "/")]
        if sub:
            return min(sub, key=lambda c: (len(c), -common(c), c))
    return min(cands, key=lambda c: (len(c), -common(c), c))


def wiki_target_path(link: str, src_rel: str) -> str:
    """./ ../ 는 출처 폴더 기준으로 풀고 루트 위로 넘치는 ../ 는 루트에서 멈춘다 (vault-review.py 와 같다)."""
    t = nfc(link.strip().replace("\\", "/"))
    if not (t.startswith("./") or t.startswith("../")):
        return t.lstrip("/")
    joined = posixpath.normpath(posixpath.join(posixpath.dirname(src_rel), t))
    while joined.startswith("../"):
        joined = joined[3:]
    return joined


class Index:
    """vault 파일 목록 인덱스. 키는 NFC 소문자."""

    def __init__(self, rels):
        self.files = {}                    # 소문자 상대경로 → 상대경로
        self.md_paths = {}                 # 소문자 상대경로(.md 제외) → 상대경로
        self.stems = defaultdict(list)     # 소문자 md 파일명(.md 제외) → [상대경로]
        self.names = defaultdict(list)     # 소문자 파일명(확장자 포함) → [상대경로]
        for rel in rels:
            low = rel.lower()
            self.files[low] = rel
            name = posixpath.basename(rel)
            self.names[name.lower()].append(rel)
            if low.endswith(".md"):
                self.md_paths[low[:-3]] = rel
                self.stems[name[:-3].lower()].append(rel)

    def resolve_wiki(self, link: str, src_rel: str):
        tl = wiki_target_path(link, src_rel).lower()
        if not tl or tl == ".":
            return None
        if "/" not in tl:
            cands = self.stems.get(tl[:-3] if tl.endswith(".md") else tl, []) or self.names.get(tl, [])
        else:
            base = tl[:-3] if tl.endswith(".md") else tl
            if base in self.md_paths:
                return self.md_paths[base]
            if tl in self.files:
                return self.files[tl]
            cands = [v for k, v in self.md_paths.items() if k.endswith("/" + base)]
            if not cands:
                cands = [v for k, v in self.files.items() if k.endswith("/" + tl)]
        if not cands:
            return None
        return cands[0] if len(cands) == 1 else obsidian_pick(cands, src_rel)

    def resolve_md(self, decoded: str, src_rel: str):
        if decoded.startswith("/"):
            cand = decoded.lstrip("/")
        else:
            cand = posixpath.normpath(posixpath.join(posixpath.dirname(src_rel), decoded))
            if cand.startswith("../"):
                return None
        low = cand.lower()
        return self.files.get(low) or self.files.get(low + ".md")

    def exact(self, rel: str):
        return self.files.get(rel.lower())


# ── 파일과 이동 쌍 ─────────────────────────────────────────────
def walk_vault(vault: Path):
    """(NFC 상대경로, 디스크 상대경로, 보고 전용 여부). 점 폴더는 .claude 만 보고 전용으로 넣는다."""
    out = []
    for root, dirs, files in os.walk(vault):
        rroot = Path(root).relative_to(vault).as_posix()
        top = rroot.split("/", 1)[0] if rroot != "." else ""
        keep = []
        for d in dirs:
            if d in SKIP_DIRS:
                continue
            if d.startswith(".") and not (rroot == "." and d in REPORT_ONLY_DOT_DIRS):
                continue
            if (d if rroot == "." else f"{rroot}/{d}") in SKIP_SUBDIRS:
                continue
            keep.append(d)
        dirs[:] = keep
        report_only = top in REPORT_ONLY_DOT_DIRS
        for f in files:
            if f.startswith("."):
                continue
            disk = f if rroot == "." else f"{rroot}/{f}"
            out.append((nfc(disk), disk, report_only))
    return out


def to_rel(vault: Path, p: str) -> str:
    p = nfc(p.strip())
    if os.path.isabs(p):
        p = os.path.relpath(p, vault)
    p = posixpath.normpath(p.replace("\\", "/"))
    if p.startswith("../") or p == "..":
        raise ValueError(f"vault 밖 경로: {p}")
    return p


def git_tracked(vault: Path):
    """({HEAD 에 있던 파일: blob id}, 지금 인덱스에 있는 파일 집합). vault 기준 NFC 상대경로. git 을 못 쓰면 None."""
    try:
        head = subprocess.run(["git", "-C", str(vault), "ls-tree", "-r", "-z", "HEAD"],
                              capture_output=True, check=True).stdout.decode("utf-8", "replace")
        index = subprocess.run(["git", "-C", str(vault), "ls-files", "-z"],
                               capture_output=True, check=True).stdout.decode("utf-8", "replace")
    except Exception:
        return None
    blobs = {}
    for rec in head.split("\0"):
        if "\t" in rec:
            meta, path = rec.split("\t", 1)             # "<mode> <type> <object>\t<path>"
            blobs[nfc(path)] = meta.split(" ")[2]
    return blobs, {nfc(p) for p in index.split("\0") if p}


def expand_moves(vault: Path, pairs, disk_by_rel: dict, tracked=None):
    """폴더 쌍을 파일 쌍으로 펼치고, 이동 전과 후 어느 상태인지 파일마다 판정한다."""
    moves = {}
    errors = []
    lower_disk = {k.lower(): k for k in disk_by_rel}
    def under(base):
        prefix = base.lower() + "/"
        return [rel for low, rel in lower_disk.items() if low.startswith(prefix)]

    for old, new in pairs:
        old_dir = (vault / old).is_dir()
        new_dir = (vault / new).is_dir()
        old_files = under(old) if old_dir else []
        if old_files:                                   # git mv 전: OLD 폴더 기준으로 펼친다
            for rel in old_files:
                moves[rel] = f"{new}/{rel[len(old) + 1:]}"
            continue
        if new_dir and (old_dir or not (vault / old).exists()):
            new_files = under(new)                      # git mv 후: NEW 폴더 기준 (OLD 는 없거나 빈 폴더)
            for rel in new_files:
                derived = f"{old}/{rel[len(new) + 1:]}"
                if tracked and derived not in tracked[0] and (rel in tracked[0] or rel in tracked[1]):
                    # 추적 파일인데 HEAD 의 OLD 자리에 없다: 이미 있던 폴더로 합쳤거나,
                    # NEW 가 먼저 있어서 git mv 가 NEW 아래로 한 단계 더 넣은 경우다
                    errors.append(f"NEW 폴더의 파일이 OLD 에서 온 것이 아닙니다. 실제 이동 경로를 파일 쌍으로 적어 주세요: {rel}")
                    continue
                moves[derived] = rel
            if not new_files:
                errors.append(f"빈 폴더라 옮길 파일이 없습니다: {old} -> {new}")
            continue
        if old_dir:
            errors.append(f"빈 폴더라 옮길 파일이 없습니다: {old} -> {new}")
            continue
        if new_dir:
            errors.append(f"NEW 가 이미 있는 폴더입니다. 파일은 NEW 에 파일 경로 전체를 적습니다: {old} -> {new}")
            continue
        moves[old] = new
    state = {}
    for old, new in moves.items():
        has_old = old.lower() in lower_disk
        has_new = new.lower() in lower_disk
        if has_old and has_new and old.lower() != new.lower():
            errors.append(f"OLD 와 NEW 가 둘 다 있습니다 (덮어쓰기 여부는 사용자 확인): {old} -> {new}")
        elif not has_old and not has_new:
            errors.append(f"OLD 와 NEW 가 둘 다 없습니다: {old} -> {new}")
        else:
            state[old] = "pre" if has_old else "post"
    return moves, state, errors


def git_status(vault: Path):
    """실행 전부터 미커밋 변경이 있는 파일. {NFC 상대경로: (XY, 인덱스 blob id 또는 None)}.
    porcelain v2 라 변경 없는 쪽은 "." 이고, 미추적은 "??" 로 적는다. rename, copy 의 원래 경로도 넣는다.
    git 을 못 쓰면 None."""
    try:
        prefix = subprocess.run(["git", "-C", str(vault), "rev-parse", "--show-prefix"],
                                capture_output=True, check=True).stdout.decode("utf-8").strip()
        out = subprocess.run(
            ["git", "-C", str(vault), "status", "--porcelain=v2", "-z", "--untracked-files=all"],
            capture_output=True, check=True).stdout.decode("utf-8", "replace")
    except Exception:
        return None
    prefix = nfc(prefix)
    status = {}
    parts = out.split("\0")
    i = 0
    while i < len(parts):
        entry = parts[i]
        i += 1
        kind = entry[:1]
        if kind == "1":                                 # 1 XY sub mH mI mW hH hI path
            f = entry.split(" ", 8)
            rows = [(f[8], f[1], f[7])]
        elif kind == "2":                               # 2 XY sub mH mI mW hH hI Xscore path, 다음 항목이 원래 경로
            f = entry.split(" ", 9)
            rows = [(f[9], f[1], f[7])]
            if i < len(parts):
                rows.append((parts[i], f[1], None))
                i += 1
        elif kind == "u":                               # 충돌 중인 파일
            f = entry.split(" ", 10)
            rows = [(f[10], f[1], None)]
        elif kind in ("?", "!"):
            rows = [(entry[2:], kind * 2, None)]
        else:
            continue
        for path, xy, blob in rows:
            path = nfc(path)
            if path.startswith(prefix):
                status[path[len(prefix):]] = (xy, blob)
    return status


def move_dirt(moves: dict, state: dict, head: dict, status: dict) -> dict:
    """이동 대상 파일 자체에 걸린 미커밋 변경. {OLD: 사유}.
    폴더째 옮기면 미추적, 무시된 파일과 다른 세션이 고치던 파일도 같이 옮겨지므로 파일마다 본다."""
    out = {}
    for old, new in moves.items():
        if state.get(old) == "pre":
            if old not in head:
                out[old] = "HEAD 에 없는 파일 (미추적 또는 무시된 파일)"
            elif old in status:
                out[old] = f"git status {status[old][0]}"
            continue
        ent = status.get(new)
        if ent is None:
            if new not in head:
                out[old] = "HEAD 에 없는 파일 (미추적 또는 무시된 파일)"
            continue                                    # 이동까지 커밋됐고 그 뒤 변경 없음
        xy, blob = ent
        if xy in ("??", "!!") or xy[1] != ".":
            out[old] = f"옮긴 뒤 git status {xy}"
        elif blob != head.get(old):
            out[old] = f"옮긴 뒤 git status {xy}, 인덱스 내용이 HEAD 의 OLD 와 다름"
    return out


# ── 텍스트 도우미 ───────────────────────────────────────────────
def code_ranges(text: str):
    """펜스 코드 블록과 인라인 코드의 (시작, 끝) 목록. 여기 안의 링크 모양은 고치지 않는다.
    fence 규칙은 vault _scripts/vault-review.py 의 strip_fences 와 같다 (#8608 에서 교정한 규칙).
    backtick fence 는 info 에 backtick 이 있으면 fence 가 아니고, 여는 fence 와 인용 깊이가 같고
    문자가 같고 길이가 같거나 길고 info string 이 없는 줄에서만 닫힌다. 안 닫히면 파일 끝까지 코드다."""
    ranges = []
    pos = 0
    open_at = None
    fence = None                                        # (인용 깊이, 문자, 길이)
    for line in text.split("\n"):
        end = min(pos + len(line) + 1, len(text))       # 줄바꿈 포함
        m = FENCE.match(line)
        if fence is None:
            if m and not (m.group(2)[0] == "`" and "`" in m.group(3)):
                open_at, fence = pos, (m.group(1).count(">"), m.group(2)[0], len(m.group(2)))
        elif (m and m.group(1).count(">") == fence[0] and m.group(2)[0] == fence[1]
                and len(m.group(2)) >= fence[2] and not m.group(3).strip()):
            ranges.append((open_at, end))
            fence = None
        pos = end
    if fence is not None:
        ranges.append((open_at, len(text)))
    for m in INLINE_CODE.finditer(text):
        if not any(a <= m.start() < b for a, b in ranges):
            ranges.append((m.start(), m.end()))
    return ranges


def inside(pos: int, ranges) -> bool:
    return any(a <= pos < b for a, b in ranges)


def line_no(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def in_table_row(text: str, pos: int) -> bool:
    ls = text.rfind("\n", 0, pos) + 1
    return text[ls:pos].lstrip().startswith("|")


def encode_like(original: str, new: str) -> str:
    """markdown 링크, file:// 경로를 원래 인코딩 방식에 맞춰 쓴다."""
    if PCT.search(original):
        if any(ord(c) > 127 for c in original):
            return new.replace(" ", "%20")               # 공백만 인코딩하던 경로
        return quote(new, safe="/()!*'~-._")              # 전부 인코딩하던 경로
    return new.replace(" ", "%20") if " " in new else new


def drop_md(path: str, keep_md: bool) -> str:
    return path if keep_md or not path.lower().endswith(".md") else path[:-3]


def relative(target: str, src_rel: str) -> str:
    p = posixpath.relpath(target, posixpath.dirname(src_rel) or ".")
    return p if p.startswith("../") else "./" + p


# ── 본체 ────────────────────────────────────────────────────────
class Relinker:
    def __init__(self, vault: Path, moves: dict, state: dict, file_roots, status, head, include_dirty: bool):
        self.vault = vault
        self.moves = moves
        self.moves_low = {k.lower(): v for k, v in moves.items()}
        roots = sorted({r.rstrip("/") for r in file_roots}, key=len, reverse=True)
        self.file_uri = re.compile(r"file://(?:" + "|".join(map(re.escape, roots)) + r")/([^\"'<>\s]+)")
        self.dirty = set(status) if status is not None else set()
        # git 상태를 못 읽으면 이동 대상 판정도 못 한다 (main 이 따로 알린다)
        self.move_dirt = move_dirt(moves, state, head, status) if status is not None and head is not None else {}
        self.mine = {k for pair in moves.items() for k in pair}
        self.include_dirty = include_dirty
        entries = walk_vault(vault)
        cur_disk = {rel: disk for rel, disk, _ in entries}
        self.report_only = {rel for rel, _, ro in entries if ro}
        # 이동 전 상태 인덱스: 이미 옮긴 파일은 OLD 자리에 있다고 본다
        post_to_old = {moves[o].lower(): o for o, s in state.items() if s == "post"}
        pre_rels = []
        self.disk_of = {}                  # 이동 전 상대경로 → 지금 디스크 상대경로
        for rel, disk in cur_disk.items():
            old = post_to_old.get(rel.lower())
            pre = old if old else rel
            pre_rels.append(pre)
            self.disk_of[pre] = disk
        indexed = [r for r in pre_rels if r not in self.report_only]
        self.pre = Index(indexed)
        self.post = Index([self.moved(r) for r in indexed])
        # 이름이 옮기는 파일과 다른 링크는 이동 전후 해석이 같으므로 건너뛴다 (출처를 옮긴 경우는 전부 본다)
        self.hot = set()
        for pair in moves.items():
            for p in pair:
                name = posixpath.basename(p).lower()
                self.hot.add(name)
                if name.endswith(".md"):
                    self.hot.add(name[:-3])
        stems = sorted({posixpath.splitext(posixpath.basename(o))[0] for o in moves}, key=len, reverse=True)
        self.stem_re = re.compile("|".join(map(re.escape, stems))) if stems else None
        self.folder_moves = self.emptied_folders(pre_rels)
        self.changes = defaultdict(list)   # 이동 전 출처 → [(줄, 원문, 새 문자열)]
        self.new_text = {}
        self.manual = []                   # (종류, 출처, 설명)
        self.log_mentions = 0
        self.log_folder_refs = 0
        self.unreadable = []

    def emptied_folders(self, pre_rels):
        """이동으로 파일이 하나도 남지 않는 폴더와 그 새 위치. [(OLD 폴더, NEW 폴더 또는 None)].
        폴더 쌍이든, 파일 쌍으로 폴더를 비운 경우든 같다. 하위 폴더는 상위 폴더 경로가 접두어로 잡으니 뺀다.
        옮긴 파일이 폴더 안 상대 위치를 유지한 채 한 폴더로 갔을 때만 새 위치를 정한다."""
        leaving = defaultdict(list)
        for old, new in self.moves.items():
            d = posixpath.dirname(old)
            while d:
                if not new.lower().startswith(d.lower() + "/"):
                    leaving[d].append((old, new))
                d = posixpath.dirname(d)
        total = defaultdict(int)
        for rel in pre_rels:
            d = posixpath.dirname(rel)
            while d:
                if d in leaving:
                    total[d] += 1
                d = posixpath.dirname(d)
        emptied = {d for d, pairs in leaving.items() if len(pairs) == total[d]}
        out = []
        for d in sorted(emptied):
            if posixpath.dirname(d) in emptied:
                continue
            dests = set()
            for old, new in leaving[d]:
                rest = old[len(d):]                     # "/하위/경로"
                dests.add(new[:-len(rest)] if new.endswith(rest) else None)
            out.append((d, dests.pop() if len(dests) == 1 else None))
        return out

    def moved(self, rel: str) -> str:
        return self.moves_low.get(rel.lower(), rel)

    def unique_name(self, rel: str) -> bool:
        """이동 후 vault 에 이 파일명(md 는 .md 뺀 이름)이 하나뿐인가."""
        name = posixpath.basename(rel).lower()
        if name.endswith(".md"):
            return len(self.post.stems.get(name[:-3], [])) == 1
        return len(self.post.names.get(name, [])) == 1

    def cold(self, target: str, src_pre: str) -> bool:
        if self.moved(src_pre) != src_pre:
            return False
        last = posixpath.basename(target.replace("\\", "/")).lower()
        return last not in self.hot

    # 위키링크
    def fix_wiki(self, text, src_pre, src_post, spans, edits):
        for m in WIKI.finditer(text):
            if inside(m.start(), spans):
                continue
            inner = m.group(2)
            tm = re.match(r"([^|#]*)(.*)", inner, re.S)
            target_raw, rest = tm.group(1), tm.group(2)
            if target_raw.endswith("\\"):
                target_raw, rest = target_raw[:-1], "\\" + rest
            target = target_raw.strip()
            if not target or self.cold(target, src_pre):
                continue
            was = self.pre.resolve_wiki(target, src_pre)
            if not was:
                continue                                    # 이동 전부터 깨진 링크
            want = self.moved(was)
            if self.post.resolve_wiki(target, src_post) == want:
                continue
            keep_md = target.lower().endswith(".md")
            lead = "/" if target.startswith("/") else ""
            full = lead + drop_md(want, keep_md)
            name_form = drop_md(posixpath.basename(want), keep_md)
            if target.startswith(("./", "../")):
                forms = [relative(drop_md(want, keep_md), src_post), full]
            elif "/" not in target:
                forms = [name_form, full]
            elif drop_md(wiki_target_path(target, src_pre).lower(), False) == drop_md(was.lower(), False):
                forms = [full]                              # 전체 경로형은 형식 유지
            else:
                # 부분 경로형: 새 파일명이 유일하면 파일명형(D6 기본형), 아니면 전체 경로
                forms = ([name_form] if self.unique_name(want) else []) + [full]
            chosen = next((f for f in forms if self.post.resolve_wiki(f, src_post) == want), None)
            if chosen is None:
                self.manual.append(("unfixable", src_pre, f"L{line_no(text, m.start())} {m.group(0)} -> {want}"))
                continue
            new_inner = chosen + rest
            if "/" not in target and "/" in chosen and "|" not in rest:
                sep = "\\|" if in_table_row(text, m.start()) else "|"
                new_inner = chosen + rest + sep + target      # 파일명형을 경로형으로 바꾸면 원래 텍스트를 표시명으로
            new = f"{m.group(1)}[[{new_inner}]]"
            edits.append((m.start(), m.end(), m.group(0), new))

    # markdown 링크
    def fix_md(self, text, src_pre, src_post, spans, edits):
        for m in MD_LINK.finditer(text):
            if inside(m.start(), spans):
                continue
            grp = "angle" if m.group("angle") else "raw"
            raw = m.group(grp)
            if URL_SCHEME.match(raw) or raw.startswith("#") or BAD_PERCENT.search(raw):
                continue
            path_part, frag = (raw.split("#", 1) + [None])[:2]
            decoded = nfc(unquote(path_part))
            if not decoded or self.cold(decoded, src_pre):
                continue
            was = self.pre.resolve_md(decoded, src_pre)
            if not was:
                continue
            want = self.moved(was)
            if self.post.resolve_md(decoded, src_post) == want:
                continue
            keep_md = decoded.lower().endswith(".md") or not was.lower().endswith(".md")
            target = drop_md(want, keep_md)
            new_path = "/" + target if decoded.startswith("/") else posixpath.relpath(
                target, posixpath.dirname(src_post) or ".")
            new_raw = new_path if grp == "angle" else encode_like(path_part, new_path)
            if frag is not None:
                new_raw += "#" + frag
            s, e = m.span(grp)
            edits.append((s, e, raw, new_raw))

    # file:// 절대경로
    def fix_file_uri(self, text, spans, edits):
        for m in self.file_uri.finditer(text):
            if spans and inside(m.start(), spans):
                continue
            raw = m.group(1)
            if raw.endswith(")") and "(" not in raw:
                raw = raw[:-1]
            path_part = re.split(r"[#?]", raw, maxsplit=1)[0]
            tail = raw[len(path_part):]
            was = self.pre.exact(nfc(unquote(path_part)))
            if not was or self.moved(was) == was:
                continue
            new_raw = encode_like(path_part, self.moved(was)) + tail
            s = m.start(1)
            edits.append((s, s + len(raw), raw, new_raw))

    # canvas 파일 노드
    def fix_canvas(self, text, edits):
        for m in CANVAS_FILE.finditer(text):
            try:
                val = json.loads(m.group(2))
            except ValueError:
                continue
            if not isinstance(val, str):
                continue
            was = self.pre.exact(nfc(val))
            if not was or self.moved(was) == was:
                continue
            new = json.dumps(self.moved(was), ensure_ascii="\\u" in m.group(2))
            s, e = m.span(2)
            edits.append((s, e, m.group(2), new))

    # 평문 언급 (보고만)
    def mentions(self, text, src_pre, covered):
        found = []
        if not self.stem_re:
            return found
        present = set(self.stem_re.findall(text))
        if not present:
            return found
        for old, new in self.moves.items():
            if posixpath.splitext(posixpath.basename(old))[0] not in present:
                continue
            needles = {old, drop_md(old, False)}
            svc_root = None
            for anchor in ("/docs/", "/diagrams/"):
                k = old.rfind(anchor)
                if k != -1:
                    svc_root = old[:k]
                    tail = old[k + 1:]
                    if src_pre.startswith(svc_root + "/"):
                        needles |= {tail, drop_md(tail, False)}
                    break
            for nd in sorted(needles, key=len, reverse=True):
                if len(nd) < 6:
                    continue
                for mm in re.finditer(re.escape(nd), text):
                    a = mm.start()
                    if any(s <= a < e for s, e in covered):
                        continue
                    prev = text[a - 1] if a else ""
                    nxt = text[mm.end()] if mm.end() < len(text) else ""
                    if (prev and (prev.isalnum() or prev in "-_")) or (nxt and (nxt.isalnum() or nxt in "-_")):
                        continue                              # 더 긴 경로의 일부
                    covered.append((a, mm.end()))
                    found.append((line_no(text, a), nd, new))
        return found

    # 폴더 경로 참조 (보고만). 파일 언급 뒤에 돌려서 파일 경로의 앞부분으로 다시 잡지 않는다
    def folder_mentions(self, text, covered):
        found = []
        for d, dest in self.folder_moves:
            if d not in text:
                continue
            for mm in re.finditer(re.escape(d), text):
                a, e = mm.span()
                if any(s <= a < t for s, t in covered):
                    continue
                prev = text[a - 1] if a else ""
                nxt = text[e:e + 2]
                if prev and (prev.isalnum() or prev in "-_"):
                    continue                              # 더 긴 이름의 일부
                if nxt[:1] and (nxt[0].isalnum() or nxt[0] in "-_" or (nxt[0] == "." and nxt[1:].isalnum())):
                    continue                              # 이름이 더 이어지거나 같은 이름의 파일 (x.md)
                sub = re.match(r"/[^\s\"'`()\[\]|<>]*", text[e:])
                sub = sub.group(0).rstrip("/") if sub else ""
                covered.append((a, e + len(sub)))
                found.append((line_no(text, a), d + sub, dest + sub if dest else None))
        return sorted(found, key=lambda f: f[0])

    def run(self):
        for src_pre, disk in sorted(self.disk_of.items()):
            ext = posixpath.splitext(src_pre)[1].lower()
            if ext not in MENTION_EXT:
                continue
            try:
                with open(self.vault / disk, encoding="utf-8", newline="") as fh:
                    text = fh.read()
            except (UnicodeDecodeError, OSError):
                self.unreadable.append(src_pre)
                continue
            src_post = self.moved(src_pre)
            edits = []
            if ext == ".md":
                spans = code_ranges(text)
                self.fix_wiki(text, src_pre, src_post, spans, edits)
                self.fix_md(text, src_pre, src_post, spans, edits)
                self.fix_file_uri(text, spans, edits)
            elif ext in (".html", ".htm"):
                self.fix_file_uri(text, [], edits)
                if src_pre != src_post:
                    for m in HTML_REL_REF.finditer(text):
                        ref = m.group(1)
                        if not URL_SCHEME.match(ref) and not ref.startswith(("/", "data:")):
                            self.manual.append(("html-rel", src_pre,
                                                f"L{line_no(text, m.start())} 옮긴 HTML 의 상대경로 참조 {ref}"))
            elif ext == ".canvas":
                self.fix_canvas(text, edits)
            covered = [(s, e) for s, e, _, _ in edits]
            if ext == ".md":
                covered += [m.span() for m in WIKI.finditer(text)] + [m.span() for m in MD_LINK.finditer(text)]
            for ln, nd, new in self.mentions(text, src_pre, covered):
                if src_pre.startswith(LOG_PREFIX):
                    self.log_mentions += 1
                else:
                    self.manual.append(("plain", src_pre, f"L{ln} 평문 경로 언급 `{nd}` (새 위치: {new})"))
            for ln, ref, new in self.folder_mentions(text, covered):
                if src_pre.startswith(LOG_PREFIX):
                    self.log_folder_refs += 1
                else:
                    where = new if new else "하나로 정해지지 않음. 여러 폴더로 나뉘었거나 이름이 바뀜"
                    self.manual.append(("folder-ref", src_pre, f"L{ln} 폴더 경로 참조 `{ref}` (새 위치: {where})"))
            if not edits:
                continue
            edits.sort()
            out, last = [], 0
            for s, e, old, new in edits:
                if s < last:
                    continue                                  # 겹치는 매치는 앞의 것만
                out.append(text[last:s] + new)
                last = e
                self.changes[src_pre].append((line_no(text, s), old, new))
            out.append(text[last:])
            self.new_text[src_pre] = "".join(out)

    def blocked(self, src_pre: str):
        if src_pre in self.report_only:
            return "report-only"
        if self.include_dirty:
            return None
        if src_pre in self.move_dirt:
            return "dirty-move"
        disk = nfc(self.disk_of[src_pre])
        if disk in self.dirty and disk not in self.mine and src_pre not in self.mine:
            return "dirty"
        return None

    def apply(self):
        written = []
        for src_pre, text in self.new_text.items():
            if self.blocked(src_pre):
                continue
            with open(self.vault / self.disk_of[src_pre], "w", encoding="utf-8", newline="") as fh:
                fh.write(text)
            written.append(self.disk_of[src_pre])
        return written


def main():
    ap = argparse.ArgumentParser(description="migrate 이동 후 vault 전체 링크 갱신 (기본 dry-run)")
    ap.add_argument("--vault", required=True, help="vault 루트 (git 저장소 루트)")
    ap.add_argument("--move", nargs=2, action="append", metavar=("OLD", "NEW"), default=[])
    ap.add_argument("--map", help='이동 쌍 파일. 한 줄에 "OLD<TAB>NEW"')
    ap.add_argument("--apply", action="store_true", help="파일을 실제로 고친다")
    ap.add_argument("--include-dirty", action="store_true",
                    help="실행 전부터 미커밋 변경이 있던 파일([dirty], [dirty-move])도 고친다 "
                         "(공유 워킹트리에서는 사용자 확인 뒤에만 쓴다)")
    ap.add_argument("--file-root", help="file:// 링크의 vault 절대경로 (기본: --vault 의 절대경로)")
    args = ap.parse_args()

    vault = Path(args.vault).resolve()
    if not vault.is_dir():
        print(f"vault 폴더가 없습니다: {vault}", file=sys.stderr)
        return 1
    pairs = [tuple(p) for p in args.move]
    if args.map:
        for ln in Path(args.map).read_text(encoding="utf-8").splitlines():
            if ln.strip() and not ln.lstrip().startswith("#"):
                cols = ln.split("\t")
                if len(cols) != 2:
                    print(f"--map 형식 오류 (탭 하나로 OLD, NEW 구분): {ln}", file=sys.stderr)
                    return 1
                pairs.append((cols[0], cols[1]))
    if not pairs:
        print("이동 쌍이 없습니다 (--move 또는 --map)", file=sys.stderr)
        return 1
    try:
        pairs = [(to_rel(vault, o), to_rel(vault, n)) for o, n in pairs]
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1

    disk_rels = {rel: disk for rel, disk, _ in walk_vault(vault)}
    tracked = git_tracked(vault)
    moves, state, errors = expand_moves(vault, pairs, disk_rels, tracked)
    if errors:
        for e in errors:
            print(f"[충돌] {e}", file=sys.stderr)
        return 2

    status = git_status(vault)
    # 심볼릭 링크로 연 vault 도 잡도록 입력 경로와 실제 경로를 둘 다 본다
    roots = [args.file_root] if args.file_root else [os.path.abspath(args.vault), str(vault)]
    rl = Relinker(vault, moves, state, roots, status, tracked[0] if tracked else None, args.include_dirty)
    rl.run()

    mode = "apply" if args.apply else "dry-run"
    n_pre = sum(1 for s in state.values() if s == "pre")
    held_moves = f", 미커밋 변경이 걸린 이동 {len(rl.move_dirt)}건 [dirty-move]" if rl.move_dirt else ""
    print(f"[relink] 모드 {mode} | 이동 {len(moves)}건 (git mv 전 {n_pre}, 후 {len(moves) - n_pre}){held_moves}")
    if status is None or tracked is None:
        print("[relink] git 상태를 읽지 못해 미커밋 파일 보호와 이동 대상 검사를 적용하지 못했습니다")
    fixable = {k: v for k, v in rl.changes.items() if not rl.blocked(k)}
    print(f"\n== 링크 갱신: 파일 {len(fixable)}개, 링크 {sum(len(v) for v in fixable.values())}개 ==")
    for src in sorted(fixable):
        print(rl.disk_of[src])
        for ln, old, new in fixable[src]:
            print(f"  L{ln}  {old}  ->  {new}")

    held = {k: v for k, v in rl.changes.items() if rl.blocked(k)}
    manual = []
    for old in sorted(rl.move_dirt):
        # 원인은 단정하지 않는다. 다른 세션 작업, 커밋된 적 없는 새 파일, 앞선 relink --apply 결과 모두 같은 모양이다
        tail = "" if args.include_dirty else " (이 파일 안의 링크는 고치지 않음)"
        manual.append(("dirty-move", old, f"이동 {old} -> {moves[old]}: {rl.move_dirt[old]}{tail}"))
    manual += rl.manual
    whys = {
        # 원인을 단정하지 않는다. 다른 세션 작업일 수도, 앞선 relink --apply 결과일 수도 있다
        "dirty": "실행 전부터 미커밋 변경이 있는 파일이라 건드리지 않음. 다른 작업이거나 앞선 relink 결과일 수 있음",
        "dirty-move": "이동 대상에 미커밋 변경이 있어 건드리지 않음",
        "report-only": ".claude/ 는 보고만 함",
    }
    for src in sorted(held):
        for ln, old, new in held[src]:
            manual.append((rl.blocked(src), src, f"L{ln} {old} -> {new} ({whys[rl.blocked(src)]})"))
    print(f"\n== 수동 확인: {len(manual)}건 ==")
    for kind, src, desc in manual:
        print(f"  [{kind}] {rl.disk_of.get(src, src)}  {desc}")
    if rl.log_mentions:
        print(f"  [60-logs] 평문 경로 언급 {rl.log_mentions}건은 기록이라 두었습니다 (#8607 D6)")
    if rl.log_folder_refs:
        print(f"  [60-logs] 폴더 경로 언급 {rl.log_folder_refs}건은 기록이라 두었습니다 (#8607 D6)")
    for src in rl.unreadable:
        print(f"  [unreadable] {src}  UTF-8 로 읽지 못해 건너뜀")

    if args.apply:
        written = rl.apply()
        print(f"\n[relink] {len(written)}개 파일을 고쳤습니다. git diff 로 확인한 뒤 경로를 지정해 add 하세요")
    else:
        print("\n[relink] dry-run 이라 아무 파일도 고치지 않았습니다. 확인 후 --apply 로 다시 실행하세요")
    return 0


if __name__ == "__main__":
    sys.exit(main())
