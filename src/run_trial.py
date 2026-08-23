from __future__ import annotations

from typing import Any

from psyflow import StimUnit, next_trial_id, set_trial_context

from .utils import decode_condition, summarize_report_sequence


def _set_context(
    unit: StimUnit,
    *,
    trial_id: int,
    block_id: str,
    condition_id: str,
    phase: str,
    deadline_s: float,
    valid_keys: list[str],
    factors: dict[str, Any],
    stim_id: str,
) -> None:
    set_trial_context(
        unit,
        trial_id=trial_id,
        phase=phase,
        deadline_s=float(deadline_s),
        valid_keys=list(valid_keys),
        block_id=block_id,
        condition_id=condition_id,
        task_factors={**factors, "stage": phase},
        stim_id=stim_id,
    )


def run_trial(
    win,
    kb,
    settings,
    condition,
    stim_bank,
    trigger_runtime,
    block_id=None,
    block_idx=None,
):
    condition_id = str(condition)
    spec = decode_condition(condition_id, dict(settings.rivalry_stimulus))
    trial_id = int(next_trial_id())
    block_name = str(block_id or "block_0")
    report_keys = {str(name): str(key) for name, key in dict(settings.report_keys).items()}
    valid_keys = [report_keys["left_tilt"], report_keys["right_tilt"], report_keys["mixed"]]
    factors = {
        "red_orientation_deg": spec.red_orientation_deg,
        "cyan_orientation_deg": spec.cyan_orientation_deg,
        "left_tilt_key": report_keys["left_tilt"],
        "right_tilt_key": report_keys["right_tilt"],
        "mixed_key": report_keys["mixed"],
        "block_idx": int(block_idx or 0),
    }
    data: dict[str, Any] = {
        "trial_id": trial_id,
        "block_id": block_name,
        "block_idx": int(block_idx or 0),
        "condition": condition_id,
        "condition_id": condition_id,
        **factors,
    }

    rivalry_stim = stim_bank.rebuild(
        "anaglyph_rivalry",
        red_orientation_deg=spec.red_orientation_deg,
        cyan_orientation_deg=spec.cyan_orientation_deg,
    )
    alignment_duration = float(settings.alignment_duration)
    alignment = StimUnit("alignment_fixation", win, kb, runtime=trigger_runtime).add_stim(rivalry_stim)
    _set_context(
        alignment,
        trial_id=trial_id,
        block_id=block_name,
        condition_id=condition_id,
        phase="alignment_fixation",
        deadline_s=alignment_duration,
        valid_keys=[],
        factors=factors,
        stim_id="anaglyph_rivalry_alignment",
    )
    alignment.show(
        duration=alignment_duration,
        onset_trigger=settings.triggers.get("alignment_fixation"),
    ).to_dict(data)

    rivalry_duration = float(settings.rivalry_duration)
    report = StimUnit("rivalry_report", win, kb, runtime=trigger_runtime).add_stim(rivalry_stim)
    _set_context(
        report,
        trial_id=trial_id,
        block_id=block_name,
        condition_id=condition_id,
        phase="rivalry_report",
        deadline_s=rivalry_duration,
        valid_keys=valid_keys,
        factors=factors,
        stim_id="anaglyph_rivalry",
    )
    report.capture_response(
        keys=valid_keys,
        duration=rivalry_duration,
        onset_trigger=settings.triggers.get(f"rivalry_{condition_id}"),
        response_trigger={
            report_keys["left_tilt"]: settings.triggers.get("report_left_tilt"),
            report_keys["right_tilt"]: settings.triggers.get("report_right_tilt"),
            report_keys["mixed"]: settings.triggers.get("report_mixed"),
        },
        timeout_trigger=settings.triggers.get("rivalry_no_report"),
        terminate_on_response=False,
        count_responses=True,
    ).to_dict(data)

    responses = list(report.get_state("responses", []) or [])
    response_times = list(report.get_state("response_times", []) or [])
    metrics = summarize_report_sequence(
        responses,
        response_times,
        {key: state for state, key in report_keys.items()},
        rivalry_duration,
    )
    data.update(metrics)
    data["rivalry_duration_s"] = rivalry_duration

    iti_duration = float(settings.iti_duration)
    iti = StimUnit("iti", win, kb, runtime=trigger_runtime).add_stim(stim_bank.get("fixation"))
    _set_context(
        iti,
        trial_id=trial_id,
        block_id=block_name,
        condition_id=condition_id,
        phase="iti",
        deadline_s=iti_duration,
        valid_keys=[],
        factors={**factors, "outcome": metrics["outcome"]},
        stim_id="fixation",
    )
    iti.show(duration=iti_duration, onset_trigger=settings.triggers.get("iti")).to_dict(data)
    return data
