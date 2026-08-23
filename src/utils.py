from __future__ import annotations

import json
import statistics
from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class RivalryCondition:
    label: str
    red_orientation_deg: float
    cyan_orientation_deg: float


def decode_condition(label: str, stimulus_config: dict[str, Any]) -> RivalryCondition:
    left = float(stimulus_config["left_orientation_deg"])
    right = float(stimulus_config["right_orientation_deg"])
    if label == "red_left_cyan_right":
        return RivalryCondition(label=label, red_orientation_deg=left, cyan_orientation_deg=right)
    if label == "red_right_cyan_left":
        return RivalryCondition(label=label, red_orientation_deg=right, cyan_orientation_deg=left)
    raise ValueError(f"Unknown binocular-rivalry condition: {label!r}")


def _paired_reports(
    responses: Iterable[Any],
    response_times: Iterable[Any],
    key_to_state: dict[str, str],
) -> list[tuple[str, float]]:
    paired: list[tuple[str, float]] = []
    for key, raw_time in zip(responses, response_times):
        state = key_to_state.get(str(key))
        if state is None:
            continue
        try:
            time_s = float(raw_time)
        except (TypeError, ValueError):
            continue
        if time_s < 0:
            continue
        paired.append((state, time_s))
    paired.sort(key=lambda item: item[1])
    return paired


def clean_report_sequence(
    responses: Iterable[Any],
    response_times: Iterable[Any],
    key_to_state: dict[str, str],
) -> list[tuple[str, float]]:
    cleaned: list[tuple[str, float]] = []
    for state, time_s in _paired_reports(responses, response_times, key_to_state):
        if cleaned and cleaned[-1][0] == state:
            continue
        cleaned.append((state, time_s))
    return cleaned


def summarize_report_sequence(
    responses: Iterable[Any],
    response_times: Iterable[Any],
    key_to_state: dict[str, str],
    trial_duration_s: float,
) -> dict[str, Any]:
    raw_keys = [str(value) for value in responses]
    raw_times = [float(value) for value in response_times]
    cleaned = clean_report_sequence(raw_keys, raw_times, key_to_state)
    intervals = [
        {"state": state, "onset_s": onset, "offset_s": next_onset, "duration_s": next_onset - onset}
        for (state, onset), (_, next_onset) in zip(cleaned, cleaned[1:])
        if next_onset > onset
    ]

    durations: dict[str, list[float]] = {"left_tilt": [], "right_tilt": [], "mixed": []}
    for interval in intervals:
        durations[interval["state"]].append(float(interval["duration_s"]))

    alternations = 0
    previous_dominant: str | None = None
    for state, _ in cleaned:
        if state == "mixed":
            continue
        if previous_dominant is not None and state != previous_dominant:
            alternations += 1
        previous_dominant = state

    analyzable_time = sum(item["duration_s"] for item in intervals)
    state_time = {state: sum(values) for state, values in durations.items()}
    predominance = {
        state: (value / analyzable_time if analyzable_time > 0 else 0.0)
        for state, value in state_time.items()
    }
    medians = {
        state: (statistics.median(values) if values else None)
        for state, values in durations.items()
    }
    duration_minutes = max(float(trial_duration_s), 0.0) / 60.0
    return {
        "report_count": len(raw_keys),
        "unique_state_count": len(cleaned),
        "report_sequence_json": json.dumps(raw_keys, ensure_ascii=False),
        "response_times_json": json.dumps(raw_times, ensure_ascii=False),
        "clean_sequence_json": json.dumps(cleaned, ensure_ascii=False),
        "dominance_intervals_json": json.dumps(intervals, ensure_ascii=False),
        "alternation_count": alternations,
        "alternation_rate_per_min": alternations / duration_minutes if duration_minutes > 0 else 0.0,
        "analyzable_time_s": analyzable_time,
        "left_predominance": predominance["left_tilt"],
        "right_predominance": predominance["right_tilt"],
        "mixed_fraction": predominance["mixed"],
        "median_left_dominance_s": medians["left_tilt"],
        "median_right_dominance_s": medians["right_tilt"],
        "median_mixed_s": medians["mixed"],
        "outcome": "reported" if raw_keys else "no_report",
    }


def summarize_trials(rows: Iterable[dict[str, Any]]) -> dict[str, float | int]:
    data = list(rows)
    report_count = sum(int(row.get("report_count", 0) or 0) for row in data)
    alternation_count = sum(int(row.get("alternation_count", 0) or 0) for row in data)
    total_duration_s = sum(float(row.get("rivalry_duration_s", 0.0) or 0.0) for row in data)
    duration_minutes = total_duration_s / 60.0
    return {
        "report_count": report_count,
        "alternation_count": alternation_count,
        "alternation_rate": alternation_count / duration_minutes if duration_minutes > 0 else 0.0,
    }
