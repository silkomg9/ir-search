"""Explicit source-scope contract tests (network-free)."""

import json

import pytest


@pytest.fixture(scope="module")
def scope_plan():
    from conftest import load_script

    return load_script("scope_plan")


def _state(plan, source_id):
    return next(source for source in plan["sources"] if source["source_id"] == source_id)


def test_quick_selects_only_kstartup_and_keeps_omissions_visible(scope_plan):
    plan = scope_plan.resolve_scope("quick")

    assert plan["counts"]["selected"] == 1
    assert _state(plan, "kstartup")["selection_status"] == "selected"
    assert _state(plan, "bizinfo")["selection_status"] == "omitted_by_user"
    assert plan["estimate"]["model_tokens"] == 0
    assert plan["coverage_claim"] == "selected_scope_ready"


def test_focused_requires_exactly_one_explicit_source(scope_plan):
    with pytest.raises(scope_plan.ScopePlanError):
        scope_plan.resolve_scope("focused")
    with pytest.raises(scope_plan.ScopePlanError):
        scope_plan.resolve_scope("focused", ["kstartup", "bizinfo"])

    plan = scope_plan.resolve_scope("focused", ["bizinfo"])
    assert _state(plan, "bizinfo")["selection_status"] == "selected"


def test_recommended_adds_only_registered_profile_matches(scope_plan):
    plan = scope_plan.resolve_scope("recommended", needs=["ai", "content"])

    selected = {
        source["source_id"]
        for source in plan["sources"]
        if source["selection_status"] == "selected"
    }
    assert selected == {"kstartup", "bizinfo", "nipa", "kocca"}
    assert _state(plan, "iris")["execution_mode"] == "manual"
    assert _state(plan, "iris")["selection_status"] == "not_applicable"


def test_all_registered_never_silently_promotes_candidates(scope_plan):
    plan = scope_plan.resolve_scope("all_registered")

    selected = {
        source["source_id"]
        for source in plan["sources"]
        if source["selection_status"] == "selected"
    }
    assert selected == {"kstartup", "bizinfo", "nipa", "kocca", "smtech"}
    assert _state(plan, "iris")["availability_status"] == "candidate"
    assert _state(plan, "iris")["selection_status"] != "selected"


def test_all_known_includes_candidates_but_keeps_them_manual(scope_plan):
    plan = scope_plan.resolve_scope("all_known", province="서울")
    selected = {
        source["source_id"]
        for source in plan["sources"]
        if source["selection_status"] == "selected"
    }

    assert selected == {source["id"] for source in scope_plan.SOURCE_REGISTRY}
    assert _state(plan, "iris")["execution_mode"] == "manual"
    assert _state(plan, "iris")["availability_status"] == "candidate"
    assert plan["coverage_claim"] == "manual_required"
    assert plan["estimate"]["model_tokens"] == 0


def test_custom_candidate_is_explicitly_manual(scope_plan):
    plan = scope_plan.resolve_scope(
        "custom", ["kstartup", "iris", "regional_portal"], province="서울"
    )

    assert plan["coverage_claim"] == "manual_required"
    assert plan["counts"]["manual"] == 2
    assert _state(plan, "iris")["execution_mode"] == "manual"
    assert "자동 어댑터" in _state(plan, "iris")["reason"]


def test_fingerprint_is_stable_across_input_order(scope_plan):
    first = scope_plan.resolve_scope(
        "custom", ["iris", "kstartup"], needs=["rnd", "ai"], province="서울"
    )
    second = scope_plan.resolve_scope(
        "custom", ["kstartup", "iris"], needs=["ai", "rnd"], province="서울"
    )

    assert first["scope_fingerprint"] == second["scope_fingerprint"]


def test_regional_source_is_not_applicable_without_region(scope_plan):
    plan = scope_plan.resolve_scope("recommended")
    state = _state(plan, "regional_portal")

    assert state["selection_status"] == "not_applicable"
    assert state["estimated_requests"] == {"min": 0, "max": 0}


def test_cli_writes_a_machine_readable_plan(scope_plan, tmp_path):
    output = tmp_path / "scope-plan.json"

    assert scope_plan.main(
        [
            "--preset",
            "custom",
            "--source",
            "kstartup,iris",
            "--need",
            "rnd",
            "--compact",
            "-o",
            str(output),
        ]
    ) == 0

    plan = json.loads(output.read_text(encoding="utf-8"))
    assert plan["requested"]["preset"] == "custom"
    assert plan["estimate"]["model_tokens"] == 0
    assert _state(plan, "iris")["execution_mode"] == "manual"
