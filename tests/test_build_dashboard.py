"""build_dashboard.py contract tests (network-free).

bootstrap(jsonl → dashboard.json), build(json → html), validate, --merge 보존.
"""
import json

import pytest


@pytest.fixture(scope="module")
def bd():
    from conftest import load_script

    return load_script("build_dashboard")


KSTARTUP_ROWS = [
    {"pbancSn": "1001", "category": "사업화", "dday": "D-3", "title": "A 사업 모집공고",
     "org": "기관A", "start": "2026-09-01", "deadline": "2026-09-10",
     "url": "https://www.k-startup.go.kr/x?pbancSn=1001"},
    {"pbancSn": "1002", "category": "글로벌", "dday": "D-20", "title": "B 사업 </script> 포함 제목",
     "org": "기관B", "start": "2026-09-01", "deadline": "2026.09.27",
     "url": "https://www.k-startup.go.kr/x?pbancSn=1002"},
    {"pbancSn": "1001", "category": "사업화", "title": "A 사업 모집공고 (중복)", "org": "기관A",
     "deadline": "2026-09-10", "url": "https://www.k-startup.go.kr/x?pbancSn=1001"},
]


def _write_jsonl(path, rows):
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")


def test_bootstrap_maps_fields_dedups_and_marks_unscored(bd, tmp_path):
    src = tmp_path / "kstartup_all.jsonl"
    _write_jsonl(src, KSTARTUP_ROWS)
    out = tmp_path / "dashboard.json"
    rc = bd.main(["bootstrap", str(src), "--target", "테스트", "--date", "2026-09-07",
                  "--region", "제주", "경기", "-o", str(out)])
    assert rc == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["meta"]["target"] == "테스트"
    assert data["meta"]["regions"] == ["제주", "경기"]
    assert data["meta"]["channels"] == ["K-Startup"]
    assert len(data["open"]) == 2  # pbancSn 1001 중복 제거
    first = data["open"][0]
    assert first == {
        "kind": "grant", "id": "1001", "source": "kstartup", "n": "A 사업 모집공고",
        "org": "기관A", "cat": "사업화", "due": "2026-09-10", "dueT": None, "budget": None,
        "bl": None, "method": None, "region": None, "sum": "A 사업 모집공고", "fit": None,
        "warn": None, "score": None, "eligibility": None,
        "url": "https://www.k-startup.go.kr/x?pbancSn=1001", "start": "2026-09-01",
    }
    assert data["open"][1]["due"] == "2026-09-27"  # 점 구분 날짜 정규화
    assert data["roadmap"] == [] and data["reframe"] == [] and data["excluded"] == []


def test_build_injects_data_and_escapes_script_terminator(bd, tmp_path):
    src = tmp_path / "kstartup_all.jsonl"
    _write_jsonl(src, KSTARTUP_ROWS)
    data_path = tmp_path / "dashboard.json"
    assert bd.main(["bootstrap", str(src), "--target", "테스트", "--date", "2026-09-07", "-o", str(data_path)]) == 0
    html_path = tmp_path / "dashboard.html"
    assert bd.main(["build", str(data_path), "-o", str(html_path)]) == 0
    html = html_path.read_text(encoding="utf-8")
    assert "__DATA_JSON__" not in html and "__TITLE__" not in html
    assert "<title>테스트 사업 탐색 대시보드 · 2026-09-07</title>" in html
    assert '"n": "A 사업 모집공고"' in html or '"n":"A 사업 모집공고"' in html
    # 데이터 안의 </script> 가 스크립트 블록을 끊지 않아야 한다
    assert html.count("</script>") == 1
    assert "<\\/script>" in html


def test_validate_reports_bad_kind_score_and_date(bd):
    data = {
        "meta": {"target": "", "date": "2026/9/x"},
        "open": [{"kind": "grant", "n": "ok", "url": "u", "due": "2026-09-10", "score": 50},
                 {"kind": "wat", "n": "bad kind", "url": "", "due": "not-a-date", "score": 120}],
        "roadmap": [{"kind": "bid"}],
    }
    probs = bd.validate(data)
    joined = "\n".join(probs)
    assert "meta.target" in joined
    assert "meta.date" in joined
    assert "kind 는 bid/grant" in joined
    assert "url 없음" in joined
    assert "due 형식 오류" in joined
    assert "score 는 0~100" in joined
    assert "roadmap[0]: n(사업명) 없음" in joined


def test_build_strict_fails_on_validation_problems(bd, tmp_path):
    data_path = tmp_path / "bad.json"
    data_path.write_text(json.dumps({"meta": {"target": "", "date": "2026-09-07"}, "open": []}), encoding="utf-8")
    assert bd.main(["build", str(data_path), "--strict", "-o", str(tmp_path / "o.html")]) == 2
    assert bd.main(["build", str(data_path), "-o", str(tmp_path / "o.html")]) == 0  # 경고만


def test_merge_keeps_judgments_and_section_moves(bd, tmp_path):
    src = tmp_path / "kstartup_all.jsonl"
    _write_jsonl(src, KSTARTUP_ROWS[:2])
    out = tmp_path / "dashboard.json"
    assert bd.main(["bootstrap", str(src), "--target", "테스트", "--date", "2026-09-07", "-o", str(out)]) == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    # Claude가 판정을 기록한 상태를 흉내낸다: 1001은 A그룹(점수), 1002는 B그룹으로 이동
    data["open"][0].update({"score": 88, "fit": "<b class='kw'>(자격)</b> 충족", "region": "제주", "sum": "요약"})
    moved = data["open"].pop(1)
    data["roadmap"].append({"kind": "grant", "id": moved["id"], "source": "kstartup", "n": moved["n"],
                            "org": moved["org"], "when": "법인 설립 후", "size": None, "score": 70, "point": "경로"})
    data["conclusion"] = "<b class='h'>결론</b>"
    out.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    # 재크롤: 1001·1002 그대로 + 신규 1003
    _write_jsonl(src, KSTARTUP_ROWS[:2] + [{"pbancSn": "1003", "category": "인력", "title": "C 신규",
                                             "org": "기관C", "deadline": "2026-10-01", "url": "https://x/1003"}])
    assert bd.main(["bootstrap", str(src), "--target", "테스트", "--date", "2026-09-14", "--merge", "-o", str(out)]) == 0
    merged = json.loads(out.read_text(encoding="utf-8"))
    ids = [o["id"] for o in merged["open"]]
    assert ids == ["1001", "1003"]                      # 1002는 roadmap으로 간 상태 유지
    kept = merged["open"][0]
    assert kept["score"] == 88 and kept["region"] == "제주" and kept["sum"] == "요약"
    assert merged["open"][1]["score"] is None            # 신규는 미평가
    assert merged["roadmap"][0]["id"] == "1002"
    assert merged["conclusion"] == "<b class='h'>결론</b>"
    assert merged["meta"]["date"] == "2026-09-14"


def test_profile_summary_reads_template_fields_and_skips_placeholders(bd, tmp_path):
    prof = tmp_path / "ir-search-profile.md"
    prof.write_text(
        "# ir-search 프로필\n- 대상: 리사 (AI 교육)\n- 사업 형태: 법인 3년차\n- 소재지: 경기 (이전 가능: 없음)\n"
        "- 임직원 수: <예: 30명>\n- 주력 용역 분야: 교육운영\n", encoding="utf-8")
    summary, target, region = bd._profile_summary(prof)
    assert target == "리사 (AI 교육)"
    assert region == "경기"
    assert "법인 3년차" in summary and "교육운영" in summary and "<예:" not in summary
