from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from psyflow.sim.contracts import Action, Feedback, Observation, SessionInfo


@dataclass
class TaskSamplerResponder:
    continue_key: str = "space"
    left_key: str = "f"
    right_key: str = "j"
    mixed_key: str = "space"
    rt_s: float = 0.05

    def __post_init__(self) -> None:
        self._rng: Any = None

    def start_session(self, session: SessionInfo, rng: Any) -> None:
        self._rng = rng

    def on_feedback(self, fb: Feedback) -> None:
        return None

    def end_session(self) -> None:
        self._rng = None

    def act(self, obs: Observation) -> Action:
        keys = [str(key) for key in list(obs.valid_keys or [])]
        if not keys:
            return Action(key=None, rt_s=None, meta={"source": "binocular_rivalry_sampler", "reason": "no_valid_keys"})
        phase = str(getattr(obs, "phase", "") or "")
        factors = dict(getattr(obs, "task_factors", {}) or {})
        stage = str(factors.get("stage", phase))
        if stage in {"instruction", "alignment_check", "practice_instruction", "block_break", "good_bye"}:
            key = self.continue_key if self.continue_key in keys else keys[0]
            return Action(key=key, rt_s=float(self.rt_s), meta={"source": "binocular_rivalry_sampler"})
        if stage == "practice_rivalry":
            key = self.mixed_key if self.mixed_key in keys else keys[0]
            return Action(key=key, rt_s=float(self.rt_s), meta={"source": "binocular_rivalry_sampler", "state": "mixed"})
        if stage == "rivalry_report":
            raw_trial_id = getattr(obs, "trial_id", 0)
            trial_id = int(raw_trial_id) if str(raw_trial_id).isdigit() else 0
            preferred = self.left_key if trial_id % 2 else self.right_key
            key = preferred if preferred in keys else keys[0]
            return Action(key=key, rt_s=float(self.rt_s), meta={"source": "binocular_rivalry_sampler", "state": "dominant"})
        key = self.continue_key if self.continue_key in keys else keys[0]
        return Action(key=key, rt_s=float(self.rt_s), meta={"source": "binocular_rivalry_sampler"})
