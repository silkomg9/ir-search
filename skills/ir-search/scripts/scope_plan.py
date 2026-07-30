#!/usr/bin/env python3
"""Resolve an explicit, auditable ir-search source scope.

The planner is intentionally network-free and standard-library-only.  It does
not turn candidate sources into crawlers.  Its only job is to make the user's
requested scope, omissions, manual work, and cost estimate explicit before a
survey starts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = 1
PRESETS = (
    "quick",
    "focused",
    "recommended",
    "all_registered",
    "all_known",
    "custom",
)

# ``registered`` means an adapter exists in this repository.  ``candidate``
# means that the official source is useful but has no verified adapter yet.
# Candidate sources always remain manual, including in a custom scope.
SOURCE_REGISTRY: tuple[dict[str, Any], ...] = (
    {
        "id": "kstartup",
        "label": "K-Startup",
        "availability": "registered",
        "execution_mode": "automated",
        "triggers": (),
        "requests": (10, 80),
        "seconds": (60, 180),
    },
    {
        "id": "bizinfo",
        "label": "기업마당",
        "availability": "registered",
        "execution_mode": "automated",
        "triggers": (),
        "requests": (20, 120),
        "seconds": (60, 240),
    },
    {
        "id": "nipa",
        "label": "정보통신산업진흥원(NIPA)",
        "availability": "registered",
        "execution_mode": "automated",
        "triggers": ("ai", "ict", "software", "cloud", "data"),
        "requests": (2, 30),
        "seconds": (15, 90),
    },
    {
        "id": "kocca",
        "label": "한국콘텐츠진흥원(KOCCA)",
        "availability": "registered",
        "execution_mode": "automated",
        "triggers": ("content", "media", "culture"),
        "requests": (2, 40),
        "seconds": (15, 120),
    },
    {
        "id": "smtech",
        "label": "SMTECH",
        "availability": "registered",
        "execution_mode": "automated",
        "triggers": ("rnd", "research", "technology"),
        "requests": (2, 30),
        "seconds": (15, 90),
    },
    {
        "id": "iris",
        "label": "범부처통합연구지원시스템(IRIS)",
        "availability": "candidate",
        "execution_mode": "manual",
        "triggers": ("rnd", "research", "technology"),
        "requests": (0, 0),
        "seconds": (120, 600),
    },
    {
        "id": "iitp",
        "label": "정보통신기획평가원(IITP)",
        "availability": "candidate",
        "execution_mode": "manual",
        "triggers": ("ai", "ict", "software", "rnd", "research"),
        "requests": (0, 0),
        "seconds": (120, 480),
    },
    {
        "id": "nia",
        "label": "한국지능정보사회진흥원(NIA)",
        "availability": "candidate",
        "execution_mode": "manual",
        "triggers": ("ai", "data", "ict"),
        "requests": (0, 0),
        "seconds": (120, 480),
    },
    {
        "id": "kiat",
        "label": "한국산업기술진흥원(KIAT)",
        "availability": "candidate",
        "execution_mode": "manual",
        "triggers": ("rnd", "research", "technology", "manufacturing"),
        "requests": (0, 0),
        "seconds": (120, 480),
    },
    {
        "id": "exportvoucher",
        "label": "수출지원기반활용사업(수출바우처)",
        "availability": "candidate",
        "execution_mode": "manual",
        "triggers": ("export", "global"),
        "requests": (0, 0),
        "seconds": (120, 360),
    },
    {
        "id": "ccei",
        "label": "창조경제혁신센터",
        "availability": "candidate",
        "execution_mode": "manual",
        "triggers": ("startup", "space", "mentoring"),
        "requests": (0, 0),
        "seconds": (120, 480),
    },
    {
        "id": "regional_portal",
        "label": "프로필 지역 TP·경제진흥원·지자체 포털",
        "availability": "candidate",
        "execution_mode": "manual",
        "triggers": (),
        "requires_province": True,
        "requests": (0, 0),
        "seconds": (180, 900),
    },
)

REGISTRY_BY_ID = {source["id"]: source for source in SOURCE_REGISTRY}
REGISTERED_IDS = tuple(
    source["id"] for source in SOURCE_REGISTRY if source["availability"] == "registered"
)


class ScopePlanError(ValueError):
    """Raised when a requested source scope is ambiguous or invalid."""


def _split_values(values: Iterable[str] | None) -> tuple[str, ...]:
    result: list[str] = []
    for raw in values or ():
        for value in raw.split(","):
            normalized = value.strip().lower()
            if normalized and normalized not in result:
                result.append(normalized)
    return tuple(result)


def _profile_applies(source: dict[str, Any], needs: set[str], province: str | None) -> bool:
    if source.get("requires_province") and not province:
        return False
    triggers = set(source.get("triggers", ()))
    return not triggers or bool(triggers & needs)


def _selected_ids(
    preset: str,
    requested_ids: tuple[str, ...],
    needs: set[str],
    province: str | None,
) -> set[str]:
    if preset == "quick":
        return {"kstartup"}
    if preset in {"focused", "custom"}:
        return set(requested_ids)
    if preset == "all_registered":
        return set(REGISTERED_IDS)
    if preset == "all_known":
        return {
            source["id"]
            for source in SOURCE_REGISTRY
            if not source.get("requires_province") or province
        }

    selected = {"kstartup", "bizinfo"}
    for source in SOURCE_REGISTRY:
        if (
            source["availability"] == "registered"
            and source["id"] not in selected
            and _profile_applies(source, needs, province)
        ):
            selected.add(source["id"])
    return selected


def resolve_scope(
    preset: str = "recommended",
    source_ids: Iterable[str] | None = None,
    *,
    needs: Iterable[str] | None = None,
    province: str | None = None,
) -> dict[str, Any]:
    """Return the canonical source-scope plan used by CLI and tests."""

    if preset not in PRESETS:
        raise ScopePlanError(f"unknown preset: {preset}")

    requested_ids = _split_values(source_ids)
    unknown = sorted(set(requested_ids) - set(REGISTRY_BY_ID))
    if unknown:
        raise ScopePlanError("unknown source id(s): " + ", ".join(unknown))
    if preset == "focused" and len(requested_ids) != 1:
        raise ScopePlanError("focused requires exactly one --source")
    if preset == "custom" and not requested_ids:
        raise ScopePlanError("custom requires at least one --source")
    if preset not in {"focused", "custom"} and requested_ids:
        raise ScopePlanError(f"{preset} does not accept --source; use focused or custom")

    normalized_needs = set(_split_values(needs))
    normalized_province = province.strip() if province and province.strip() else None
    selected = _selected_ids(preset, requested_ids, normalized_needs, normalized_province)

    source_states: list[dict[str, Any]] = []
    for source in SOURCE_REGISTRY:
        source_id = source["id"]
        applicable = _profile_applies(source, normalized_needs, normalized_province)
        if source_id in selected:
            selection_status = "selected"
            if source["availability"] == "candidate":
                reason = "명시 선택됨; 검증된 자동 어댑터가 없어 수동 확인"
            else:
                reason = "선택 범위에 포함"
        elif not applicable:
            selection_status = "not_applicable"
            reason = "현재 프로필 트리거와 일치하지 않음"
        else:
            selection_status = "omitted_by_user"
            reason = "현재 선택 범위에서 제외"

        source_states.append(
            {
                "source_id": source_id,
                "label": source["label"],
                "selection_status": selection_status,
                "execution_mode": source["execution_mode"],
                "availability_status": source["availability"],
                "reason": reason,
                "estimated_requests": {
                    "min": source["requests"][0] if selection_status == "selected" else 0,
                    "max": source["requests"][1] if selection_status == "selected" else 0,
                },
                "estimated_duration_seconds": {
                    "min": source["seconds"][0] if selection_status == "selected" else 0,
                    "max": source["seconds"][1] if selection_status == "selected" else 0,
                },
            }
        )

    selected_states = [
        state for state in source_states if state["selection_status"] == "selected"
    ]
    manual_count = sum(state["execution_mode"] == "manual" for state in selected_states)
    estimate = {
        "requests": {
            "min": sum(state["estimated_requests"]["min"] for state in selected_states),
            "max": sum(state["estimated_requests"]["max"] for state in selected_states),
        },
        "duration_seconds": {
            "min": sum(
                state["estimated_duration_seconds"]["min"] for state in selected_states
            ),
            "max": sum(
                state["estimated_duration_seconds"]["max"] for state in selected_states
            ),
        },
        "model_tokens": 0,
    }

    fingerprint_payload = {
        "schema_version": SCHEMA_VERSION,
        "domain": "ir-search",
        "preset": preset,
        "selected_source_ids": [
            state["source_id"] for state in selected_states
        ],
        "needs": sorted(normalized_needs),
        "province": normalized_province,
        "manual_source_ids": [
            state["source_id"]
            for state in selected_states
            if state["execution_mode"] == "manual"
        ],
    }
    canonical = json.dumps(
        fingerprint_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "domain": "ir-search",
        "requested": {
            "preset": preset,
            "source_ids": list(requested_ids),
            "needs": sorted(normalized_needs),
            "province": normalized_province,
        },
        "scope_fingerprint": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "coverage_claim": "manual_required" if manual_count else "selected_scope_ready",
        "counts": {
            "universe": len(source_states),
            "selected": len(selected_states),
            "automated": len(selected_states) - manual_count,
            "manual": manual_count,
            "omitted": sum(
                state["selection_status"] == "omitted_by_user" for state in source_states
            ),
            "not_applicable": sum(
                state["selection_status"] == "not_applicable" for state in source_states
            ),
        },
        "estimate": estimate,
        "sources": source_states,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ir-search 범위 계획만 생성합니다. 네트워크·LLM 호출은 하지 않습니다."
    )
    parser.add_argument("--preset", choices=PRESETS, default="recommended")
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="focused/custom에서 사용할 source id. 반복 또는 쉼표 구분 가능",
    )
    parser.add_argument("--need", action="append", default=[], help="프로필 필요 태그")
    parser.add_argument("--province", help="지역 소스 적용 판단용 시/도")
    parser.add_argument("--list-sources", action="store_true")
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--compact", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.list_sources:
        payload: Any = {
            "schema_version": SCHEMA_VERSION,
            "domain": "ir-search",
            "sources": SOURCE_REGISTRY,
        }
    else:
        try:
            payload = resolve_scope(
                args.preset,
                args.source,
                needs=args.need,
                province=args.province,
            )
        except ScopePlanError as exc:
            _parser().error(str(exc))

    rendered = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        indent=None if args.compact else 2,
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
