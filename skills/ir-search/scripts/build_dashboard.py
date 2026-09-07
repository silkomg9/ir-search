#!/usr/bin/env python3
"""build_dashboard.py — 조사 결과를 HTML 대시보드 한 파일로 만든다.

표준 라이브러리만 사용한다 (네트워크·LLM 호출 없음).

두 가지 일을 한다:

1) 부트스트랩: 크롤 jsonl → dashboard.json 초안
   python3 build_dashboard.py bootstrap kstartup_all.jsonl [bizinfo.jsonl ...] \
       --target "○○" --date 2026-09-07 --profile ir-search-profile.md \
       --channels "K-Startup" --region 제주 경기 -o dashboard.json
   → open[] 에 kind=grant, score=null, fit=null 로 넣는다 (판정 전 = 화면에 '미평가').
     Claude가 판정을 채운 뒤 build 한다. 이미 dashboard.json이 있으면 --merge 로
     기존 판정(score/fit/warn/sum/cat/region/eligibility, 섹션 배정)을 보존한다.

2) 빌드: dashboard.json + templates/dashboard.html → dashboard.html
   python3 build_dashboard.py build dashboard.json -o dashboard.html

형식은 references/dashboard_schema.md 참조.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "templates" / "dashboard.html"

# 크롤 jsonl → open[] 필드 매핑 (소스별 키 이름 차이 흡수)
ID_KEYS = ("pbancSn", "id", "source_id", "bidNtceNo", "pblancId")
TITLE_KEYS = ("title", "n", "bidNtceNm", "pblancNm")
ORG_KEYS = ("org", "agency", "ntceInsttNm", "excInsttNm", "jrsdInsttNm")
DUE_KEYS = ("deadline", "due", "end", "bidClseDt", "reqstEndDe")
START_KEYS = ("start", "begin", "reqstBeginDe")
CAT_KEYS = ("category", "cat", "pldirSportRealmLclasCodeNm")
URL_KEYS = ("url", "link", "detail_url")
SOURCE_KEYS = ("source",)


def _first(rec: dict, keys: tuple[str, ...], default=None):
    for k in keys:
        v = rec.get(k)
        if v not in (None, ""):
            return v
    return default


def _norm_date(v) -> str | None:
    """'2026-09-15', '2026.09.15', '20260915', '2026-09-15 16:00' → 'YYYY-MM-DD'."""
    if not v:
        return None
    s = str(v).strip()
    m = re.search(r"(\d{4})[.\-/]?(\d{1,2})[.\-/]?(\d{1,2})", s)
    if not m:
        return None
    y, mo, d = (int(x) for x in m.groups())
    try:
        return dt.date(y, mo, d).isoformat()
    except ValueError:
        return None


def _norm_time(v) -> str | None:
    if not v:
        return None
    m = re.search(r"(\d{1,2}):(\d{2})", str(v))
    return f"{int(m.group(1)):02d}:{m.group(2)}" if m else None


def _read_jsonl(path: Path) -> list[dict]:
    out = []
    with path.open(encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                out.append(json.loads(ln))
            except json.JSONDecodeError as e:  # 한 줄 깨져도 나머지는 살린다
                print(f"[build_dashboard] WARN {path.name}: 깨진 줄 건너뜀 ({e})", file=sys.stderr)
    return out


def _guess_source(path: Path, rec: dict) -> str:
    s = _first(rec, SOURCE_KEYS)
    if s:
        return str(s)
    name = path.stem.lower()
    for key in ("kstartup", "bizinfo", "nipa", "kocca", "smtech", "g2b"):
        if key in name:
            return key
    return name


def _guess_kind(source: str, rec: dict) -> str:
    if rec.get("kind") in ("bid", "grant"):
        return rec["kind"]
    return "bid" if source in ("g2b", "narajangter", "s2b") else "grant"


def record_to_open(rec: dict, source: str) -> dict:
    kind = _guess_kind(source, rec)
    title = str(_first(rec, TITLE_KEYS, "제목 불명"))
    item = {
        "kind": kind,
        "id": str(_first(rec, ID_KEYS, "")),
        "source": source,
        "n": title,
        "org": str(_first(rec, ORG_KEYS, "불명")),
        "cat": str(_first(rec, CAT_KEYS, "") or ""),
        "due": _norm_date(_first(rec, DUE_KEYS)),
        "dueT": _norm_time(_first(rec, DUE_KEYS)),
        "budget": rec.get("budget") if isinstance(rec.get("budget"), (int, float)) else None,
        "bl": rec.get("bl"),
        "method": rec.get("method"),
        "region": rec.get("region"),  # 지역 제한 공고면 지역 이름 (예: "경기"), 아니면 null
        "sum": rec.get("sum") or title,
        "fit": rec.get("fit"),
        "warn": rec.get("warn"),
        "score": rec.get("score"),
        "eligibility": rec.get("eligibility"),
        "url": str(_first(rec, URL_KEYS, "")),
    }
    if rec.get("start"):
        item["start"] = _norm_date(rec.get("start"))
    return item


JUDGMENT_KEYS = ("sum", "fit", "warn", "score", "cat", "region", "eligibility",
                 "budget", "bl", "method", "dueT")


def _key(o: dict) -> str:
    return f"{o.get('source')}::{o.get('id')}" if o.get("id") else f"{o.get('source')}::{o.get('n')}"


def _profile_summary(profile_path: Path | None) -> tuple[str, str | None, str | None]:
    """ir-search-profile.md → (요약 한 문장, 대상 이름, 소재지)."""
    if not profile_path or not profile_path.exists():
        return "", None, None
    text = profile_path.read_text(encoding="utf-8")
    fields = {}
    for m in re.finditer(r"^- ([^:：]+)[:：]\s*(.+)$", text, re.M):
        fields[m.group(1).strip()] = m.group(2).strip()
    target = fields.get("대상")
    region = None
    if fields.get("소재지"):
        region = re.split(r"[\s(（]", fields["소재지"], maxsplit=1)[0] or None
    parts = []
    for k in ("사업 형태", "소재지", "필요한 것", "주력 용역 분야"):
        v = fields.get(k)
        if v and not v.startswith("<"):
            parts.append(f"{k} {v}")
    summary = (f"{target} — " if target and not target.startswith("<") else "") + " · ".join(parts)
    if target and target.startswith("<"):
        target = None
    if region and region.startswith("<"):
        region = None
    return (summary + "을(를) 기준으로 지원사업·수주 공고를 조사하고 적합도를 산정함") if parts else "", target, region


def cmd_bootstrap(a: argparse.Namespace) -> int:
    summary, prof_target, prof_region = _profile_summary(Path(a.profile) if a.profile else None)
    target = a.target or prof_target or "프로젝트"
    regions = list(a.region) if a.region else ([prof_region] if prof_region else [])

    items: list[dict] = []
    channels: list[str] = list(a.channels or [])
    for p in a.jsonl:
        path = Path(p)
        if not path.exists():
            print(f"[build_dashboard] ERROR 파일 없음: {path}", file=sys.stderr)
            return 1
        recs = _read_jsonl(path)
        src = _guess_source(path, recs[0]) if recs else path.stem
        for r in recs:
            items.append(record_to_open(r, _guess_source(path, r)))
        if not a.channels:
            channels.append({"kstartup": "K-Startup", "bizinfo": "기업마당", "nipa": "NIPA",
                             "kocca": "KOCCA", "smtech": "SMTECH", "g2b": "나라장터"}.get(src, src))
        print(f"[build_dashboard] {path.name}: {len(recs)}건 (source={src})", file=sys.stderr)

    # 중복 제거 (같은 source::id)
    seen: dict[str, dict] = {}
    for it in items:
        seen.setdefault(_key(it), it)
    items = list(seen.values())

    data = {
        "meta": {
            "target": target,
            "date": a.date or dt.date.today().isoformat(),
            "eyebrow": a.eyebrow or "Business Opportunity Scan",
            "profile_summary": summary,
            "regions": regions,
            "channels": list(dict.fromkeys(channels)),
            "counts": None,
            "scope_fingerprint": a.scope_fingerprint,
            "report_path": a.report_path,
        },
        "open": items,
        "roadmap": [],
        "reframe": [],
        "excluded": [],
        "conclusion": None,
        "notes": [],
    }

    out = Path(a.out)
    if a.merge and out.exists():
        old = json.loads(out.read_text(encoding="utf-8"))
        old_open = {_key(o): o for o in old.get("open", [])}
        moved = set()
        for sec in ("roadmap", "reframe", "excluded"):
            for o in old.get(sec, []):
                moved.add(_key(o))
        kept = 0
        merged_open = []
        for it in items:
            k = _key(it)
            if k in moved:            # 이전에 다른 섹션으로 배정된 건은 open에서 제외
                continue
            if k in old_open:
                for jk in JUDGMENT_KEYS:
                    if old_open[k].get(jk) not in (None, "", False) or jk == "sum":
                        it[jk] = old_open[k].get(jk, it.get(jk))
                kept += 1
            merged_open.append(it)
        data["open"] = merged_open
        for sec in ("roadmap", "reframe", "excluded"):
            data[sec] = old.get(sec, [])
        data["conclusion"] = old.get("conclusion")
        data["notes"] = old.get("notes", [])
        for mk in ("eyebrow", "profile_summary", "regions", "channels", "report_path", "scope_fingerprint"):
            if old.get("meta", {}).get(mk) and not getattr(a, mk.replace("profile_summary", "profile"), None):
                data["meta"][mk] = old["meta"][mk]
        print(f"[build_dashboard] merge: 판정 보존 {kept}건, 타 섹션 {len(moved)}건 유지", file=sys.stderr)

    out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[build_dashboard] saved: {out} (open {len(data['open'])}건)", file=sys.stderr)
    return 0


def cmd_build(a: argparse.Namespace) -> int:
    data_path = Path(a.data)
    tpl_path = Path(a.template) if a.template else TEMPLATE
    if not data_path.exists():
        print(f"[build_dashboard] ERROR 데이터 없음: {data_path}", file=sys.stderr)
        return 1
    if not tpl_path.exists():
        print(f"[build_dashboard] ERROR 템플릿 없음: {tpl_path}", file=sys.stderr)
        return 1
    data = json.loads(data_path.read_text(encoding="utf-8"))
    problems = validate(data)
    for p in problems:
        print(f"[build_dashboard] WARN {p}", file=sys.stderr)
    if problems and a.strict:
        return 2

    meta = data["meta"]
    title = f"{meta.get('target','프로젝트')} 사업 탐색 대시보드 · {meta.get('date','')}"
    # </script> 가 데이터에 들어 있어도 스크립트가 끊기지 않게 이스케이프
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = tpl_path.read_text(encoding="utf-8")
    if "__DATA_JSON__" not in html:
        print("[build_dashboard] ERROR 템플릿에 __DATA_JSON__ 자리표시자가 없음", file=sys.stderr)
        return 1
    html = html.replace("__TITLE__", title).replace("__DATA_JSON__", payload)
    out = Path(a.out)
    out.write_text(html, encoding="utf-8", newline="\n")
    print(f"[build_dashboard] saved: {out} ({len(html):,} bytes, open {len(data.get('open',[]))}건)", file=sys.stderr)
    return 0


def validate(data: dict) -> list[str]:
    probs = []
    meta = data.get("meta") or {}
    if not meta.get("target"):
        probs.append("meta.target 비어 있음")
    if not _norm_date(meta.get("date")):
        probs.append("meta.date 형식 오류 (YYYY-MM-DD)")
    for i, o in enumerate(data.get("open", [])):
        where = f"open[{i}] '{str(o.get('n',''))[:30]}'"
        if o.get("kind") not in ("bid", "grant"):
            probs.append(f"{where}: kind 는 bid/grant 여야 함")
        if not o.get("url"):
            probs.append(f"{where}: url 없음")
        if o.get("due") and not _norm_date(o["due"]):
            probs.append(f"{where}: due 형식 오류")
        s = o.get("score")
        if s is not None and not (isinstance(s, int) and 0 <= s <= 100):
            probs.append(f"{where}: score 는 0~100 정수 또는 null")
    for sec in ("roadmap", "reframe", "excluded"):
        for i, o in enumerate(data.get(sec, [])):
            if o.get("kind") not in ("bid", "grant"):
                probs.append(f"{sec}[{i}]: kind 는 bid/grant 여야 함")
            if not o.get("n"):
                probs.append(f"{sec}[{i}]: n(사업명) 없음")
    return probs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("bootstrap", help="크롤 jsonl → dashboard.json 초안")
    b.add_argument("jsonl", nargs="+", help="크롤 결과 jsonl (여러 개 가능)")
    b.add_argument("--target", help="프로필 대상 이름 (없으면 --profile에서 읽음)")
    b.add_argument("--date", help="기준일 YYYY-MM-DD (기본 오늘)")
    b.add_argument("--profile", help="ir-search-profile.md 경로")
    b.add_argument("--region", nargs="*", help="지역 한정 칩 라벨들 (예: --region 제주 경기)")
    b.add_argument("--channels", nargs="*", help="수집 채널 표시 이름들")
    b.add_argument("--eyebrow", help="헤더 위 라벨")
    b.add_argument("--scope-fingerprint", dest="scope_fingerprint")
    b.add_argument("--report-path", dest="report_path")
    b.add_argument("--merge", action="store_true", help="기존 dashboard.json의 판정을 보존하며 갱신")
    b.add_argument("-o", "--out", default="dashboard.json")
    b.set_defaults(fn=cmd_bootstrap)

    c = sub.add_parser("build", help="dashboard.json → dashboard.html")
    c.add_argument("data", help="dashboard.json")
    c.add_argument("--template", help=f"템플릿 경로 (기본 {TEMPLATE})")
    c.add_argument("--strict", action="store_true", help="검증 경고가 있으면 실패(exit 2)")
    c.add_argument("-o", "--out", default="dashboard.html")
    c.set_defaults(fn=cmd_build)

    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
