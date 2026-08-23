from __future__ import annotations

import json

import pytest

from src.utils import decode_condition, summarize_report_sequence, summarize_trials


STIMULUS = {"left_orientation_deg": -60.0, "right_orientation_deg": 60.0}
KEYS = {"f": "left_tilt", "j": "right_tilt", "space": "mixed"}


def test_decode_condition_swaps_only_color_orientation_mapping() -> None:
    first = decode_condition("red_left_cyan_right", STIMULUS)
    second = decode_condition("red_right_cyan_left", STIMULUS)
    assert (first.red_orientation_deg, first.cyan_orientation_deg) == (-60.0, 60.0)
    assert (second.red_orientation_deg, second.cyan_orientation_deg) == (60.0, -60.0)


def test_report_summary_collapses_duplicates_and_tracks_mixed_intervals() -> None:
    result = summarize_report_sequence(
        ["f", "f", "space", "j", "f"],
        [1.0, 1.2, 2.0, 3.5, 5.0],
        KEYS,
        10.0,
    )
    assert result["report_count"] == 5
    assert result["unique_state_count"] == 4
    assert result["alternation_count"] == 2
    assert result["alternation_rate_per_min"] == pytest.approx(12.0)
    intervals = json.loads(result["dominance_intervals_json"])
    assert [item["state"] for item in intervals] == ["left_tilt", "mixed", "right_tilt"]
    assert result["outcome"] == "reported"


def test_no_report_is_retained_without_imputation() -> None:
    result = summarize_report_sequence([], [], KEYS, 120.0)
    assert result["outcome"] == "no_report"
    assert result["report_count"] == 0
    assert result["alternation_rate_per_min"] == 0.0


def test_session_summary_uses_exposure_time() -> None:
    result = summarize_trials(
        [
            {"report_count": 4, "alternation_count": 2, "rivalry_duration_s": 120.0},
            {"report_count": 5, "alternation_count": 3, "rivalry_duration_s": 120.0},
        ]
    )
    assert result == {"report_count": 9, "alternation_count": 5, "alternation_rate": 1.25}
