#!/usr/bin/env python3
"""
scan.py: sr-obsidian:archive 의 아카이브 대상 판정 (읽기 전용, #8609)

10-projects/ISS-*/ 를 돌며 허브와 step 을 읽어 아카이브 대상, 보류, 수동 확인으로 나눈다.
파일을 쓰지 않는다. 판정 결과를 보고 옮길지는 사람이 정한다.

판정 규칙 (#8607 D1, 규칙 정본은 vault 10-projects/CLAUDE.md, .claude/rules/step-frontmatter.md)
  허브 식별
    - ISS 폴더 루트의 .md 중 frontmatter type: issue 인 파일이 허브다.
    - 파일명 glob 으로 status 를 읽지 않는다. 같은 폴더의 WBS(type wbs, 레거시는 literature)도 status 를 가져서
      허브로 오인하면 WBS 의 status: in-progress 를 허브 값으로 읽는다.
  허브 종료
    - done, cancelled 가 종료 상태다. closed 는 폐기된 레거시 값이지만 #8610 이관 전까지 종료로 인정한다.
    - done 은 end-date, cancelled 는 cancelled-date 와 cancelled-reason 이 있어야 한다 (closed 는 면제).
  step 닫힘 (vault _scripts/detect-stale-hubs.py 의 step_closed 와 같은 규칙)
    - applicable: false (미적용), end-date 있음 (완료), status: cancelled 또는 cancelled-date 있음 (중단)
    - status 와 날짜가 어긋나면 날짜를 따른다. status: done 인데 end-date 가 없으면 닫히지 않은 step 이다.
  체크리스트
    - cancelled 허브는 체크리스트가 미완이어도 옮길 수 있다.
    - done 허브의 ## 체크리스트 에 - [ ] 가 남아 있으면 경고만 한다 (대상에서 빼지 않음).
  공유 워킹트리
    - 폴더 안에 미커밋 변경이 있으면 보류한다. 다른 세션이 쓰는 중일 수 있고 git mv 가 그 변경을 같이 옮긴다.

사용법 (vault 루트에서):
  python3 scan.py                 # 사람용 보고
  python3 scan.py --json          # JSON
  python3 scan.py --vault PATH    # vault 루트 지정 (기본: 현재 폴더)

종료 코드: 항상 0 (보고 도구)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ACTIVE_DIR = "10-projects"
CLOSED_HUB = {"done", "cancelled", "closed"}   # closed: #8610 이관 전 레거시 (#8607 D1)
LEGACY_HUB = {"closed"}
STEP_TYPES = {"incident-step", "wbs-step"}

FM_RE = re.compile(r"^---\r?\n(.*?)\r?\n---", re.S)
COMMENT_RE = re.compile(r"\s+#.*$")            # YAML 인라인 주석 (템플릿 주석이 노트에 남는 경우)
CHECKLIST_RE = re.compile(r"^##\s+체크리스트\s*$(.*?)(?=^##\s|\Z)", re.M | re.S)
UNCHECKED_RE = re.compile(r"^\s*[-*]\s+\[ \]", re.M)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def frontmatter(text: str) -> dict:
    """최상위 key: value 만 뽑는다. 값의 인라인 주석과 따옴표는 걷어낸다."""
    m = FM_RE.match(text)
    fm: dict = {}
    if not m:
        return fm
    for line in m.group(1).splitlines():
        if not line or line[0] in " \t-#":
            continue
        key, sep, val = line.partition(":")
        if sep:
            fm[key.strip()] = COMMENT_RE.sub("", val).strip().strip("'\"")
    return fm


def step_state(fm: dict) -> str:
    """na | done | cancelled | open. 날짜 필드가 status 보다 우선한다."""
    if fm.get("applicable", "").lower() == "false":
        return "na"
    if fm.get("end-date"):
        return "done"
    if fm.get("status", "").lower() == "cancelled" or fm.get("cancelled-date"):
        return "cancelled"
    return "open"


def dirty_paths(vault: Path, folder: Path):
    """폴더 안 미커밋 변경 경로 목록. git 을 못 쓰면 None."""
    try:
        out = subprocess.run(
            ["git", "-C", str(vault), "status", "--porcelain=v1", "-z", "--untracked-files=all", "--",
             str(folder.relative_to(vault))],
            capture_output=True, check=True).stdout.decode("utf-8", "replace")
    except Exception:
        return None
    paths, parts, i = [], out.split("\0"), 0
    while i < len(parts):
        entry = parts[i]
        i += 1
        if len(entry) < 4:
            continue
        paths.append(entry[3:])
        if entry[0] in "RC":   # rename, copy 는 원래 경로가 다음 항목으로 온다
            i += 1
    return paths


def scan(vault: Path) -> dict:
    result = {"targets": [], "held": [], "manual": [], "closure_candidates": [], "active_count": 0,
              "git_unavailable": False}
    base = vault / ACTIVE_DIR
    if not base.is_dir():
        return result
    for folder in sorted(p for p in base.glob("ISS-*") if p.is_dir()):
        hubs = [p for p in sorted(folder.glob("*.md")) if frontmatter(read_text(p)).get("type") == "issue"]
        if len(hubs) != 1:
            result["manual"].append({"folder": f"{ACTIVE_DIR}/{folder.name}",
                                     "reason": f"type: issue 허브 {len(hubs)}개"})
            continue
        hub = hubs[0]
        hub_text = read_text(hub)
        hub_fm = frontmatter(hub_text)
        status = hub_fm.get("status", "").lower()
        steps_dir = folder / "steps"
        steps = []
        if steps_dir.is_dir():
            for s in sorted(steps_dir.glob("*.md")):
                sfm = frontmatter(read_text(s))
                if sfm.get("type") in STEP_TYPES or s.name.startswith("step-"):
                    steps.append((s.name, sfm, step_state(sfm)))
        counts = {k: sum(1 for _, _, st in steps if st == k) for k in ("done", "cancelled", "na", "open")}
        entry = {
            "id": hub_fm.get("id") or "-".join(folder.name.split("-")[:2]),
            "folder": f"{ACTIVE_DIR}/{folder.name}",
            "hub": hub.stem,
            "hub_status": status or "(없음)",
            "steps": len(steps),
            "step_counts": counts,
            "reasons": [],
            "warnings": [],
        }

        if status not in CLOSED_HUB:
            result["active_count"] += 1
            if steps and counts["open"] == 0:
                # 종료는 사람이 선언한다 (#8607 D1). 여기서는 알리기만 한다.
                result["closure_candidates"].append(entry)
            continue

        for name, sfm, st in steps:
            if st == "open":
                shown = sfm.get("status") or "없음"
                note = ", end-date 없음" if shown == "done" else ""
                entry["reasons"].append(f"{name} 미종료 (status: {shown}{note})")
        if status == "done" and not hub_fm.get("end-date"):
            entry["reasons"].append("허브 end-date 없음 (done 선언에 필요)")
        if status == "cancelled":
            for key in ("cancelled-date", "cancelled-reason"):
                if not hub_fm.get(key):
                    entry["reasons"].append(f"허브 {key} 없음 (cancelled 선언에 필요)")
        if status in LEGACY_HUB:
            entry["warnings"].append("레거시 status closed (#8610 이관 대상, 종료로 인정)")
        if status == "done":
            m = CHECKLIST_RE.search(hub_text)
            unchecked = len(UNCHECKED_RE.findall(m.group(1))) if m else 0
            if unchecked:
                entry["warnings"].append(f"허브 체크리스트 미완 {unchecked}개")
        dirty = dirty_paths(vault, folder)
        if dirty is None:
            result["git_unavailable"] = True
        elif dirty:
            entry["reasons"].append(f"미커밋 변경 {len(dirty)}개 (다른 세션 작업일 수 있음): {', '.join(dirty[:3])}")

        (result["held"] if entry["reasons"] else result["targets"]).append(entry)
    return result


def fmt_counts(c: dict) -> str:
    if not any(c.values()):
        return "step 없음"
    parts = [f"완료 {c['done']}"]
    if c["cancelled"]:
        parts.append(f"중단 {c['cancelled']}")
    if c["na"]:
        parts.append(f"미적용 {c['na']}")
    if c["open"]:
        parts.append(f"미종료 {c['open']}")
    return ", ".join(parts)


def report(r: dict) -> None:
    if r["git_unavailable"]:
        print("[scan] git 상태를 읽지 못해 미커밋 변경 검사를 건너뛰었습니다. 옮기기 전에 git status 를 직접 확인하세요\n")
    print(f"아카이브 대상 ({len(r['targets'])}건)")
    for e in r["targets"]:
        print(f"  ✅ {e['id']} [{e['hub_status']}] {e['hub']} | {fmt_counts(e['step_counts'])}")
        for w in e["warnings"]:
            print(f"     ⚠️ {w}")
    print(f"\n보류 ({len(r['held'])}건)")
    for e in r["held"]:
        print(f"  ⏳ {e['id']} [{e['hub_status']}] {e['hub']}")
        for why in e["reasons"]:
            print(f"     - {why}")
    if r["manual"]:
        print(f"\n수동 확인 ({len(r['manual'])}건)")
        for e in r["manual"]:
            print(f"  ?? {e['folder']} | {e['reason']}")
    if r["closure_candidates"]:
        print(f"\n참고: step 은 모두 닫혔는데 허브가 종료 선언 전 ({len(r['closure_candidates'])}건, 아카이브 대상 아님)")
        for e in r["closure_candidates"]:
            print(f"  - {e['id']} [{e['hub_status']}] {e['hub']} | {fmt_counts(e['step_counts'])}")
        print("  종료는 사람이 선언합니다 (sr-obsidian:iss 종료 절차)")
    print(f"\n진행 중(종료 선언 전) 허브 {r['active_count']}건은 스캔만 했습니다")
    if not r["targets"]:
        print("\n아카이브할 ISS 없음")


def main() -> int:
    ap = argparse.ArgumentParser(description="ISS 아카이브 대상 판정 (읽기 전용)")
    ap.add_argument("--vault", default=".", help="vault 루트 (기본: 현재 폴더)")
    ap.add_argument("--json", action="store_true", help="JSON 출력")
    args = ap.parse_args()
    vault = Path(args.vault).resolve()
    r = scan(vault)
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        report(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
