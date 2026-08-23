from __future__ import annotations

import math
from typing import Any

import numpy as np
from psychopy import visual
from psychopy.visual.basevisual import BaseVisualStim


def _grating_channel(
    x_grid: np.ndarray,
    y_grid: np.ndarray,
    *,
    orientation_deg: float,
    spatial_frequency_cpd: float,
    contrast: float,
    gain: float,
) -> np.ndarray:
    normal_angle = math.radians(float(orientation_deg) + 90.0)
    axis = x_grid * math.cos(normal_angle) + y_grid * math.sin(normal_angle)
    wave = 0.5 + 0.5 * float(contrast) * np.sin(2.0 * math.pi * float(spatial_frequency_cpd) * axis)
    return np.clip(wave * float(gain), 0.0, 1.0)


class AnaglyphRivalryStim(BaseVisualStim):
    """Static red/cyan dichoptic gratings with an achromatic fusion lock."""

    def __init__(
        self,
        win,
        *,
        red_orientation_deg: float,
        cyan_orientation_deg: float,
        aperture_diameter_deg: float,
        spatial_frequency_cpd: float,
        contrast: float,
        red_gain: float,
        cyan_gain: float,
        texture_resolution: int,
        fusion_frame_span_deg: float,
        fusion_frame_width_deg: float,
        fixation_diameter_deg: float,
    ) -> None:
        super().__init__(win, units="deg", name="anaglyph_rivalry", autoLog=False)
        diameter = float(aperture_diameter_deg)
        resolution = max(128, int(texture_resolution))
        coords = np.linspace(-diameter / 2.0, diameter / 2.0, resolution)
        x_grid, y_grid = np.meshgrid(coords, coords)
        red = _grating_channel(
            x_grid,
            y_grid,
            orientation_deg=red_orientation_deg,
            spatial_frequency_cpd=spatial_frequency_cpd,
            contrast=contrast,
            gain=red_gain,
        )
        cyan = _grating_channel(
            x_grid,
            y_grid,
            orientation_deg=cyan_orientation_deg,
            spatial_frequency_cpd=spatial_frequency_cpd,
            contrast=contrast,
            gain=cyan_gain,
        )
        circular_mask = (x_grid**2 + y_grid**2) <= (diameter / 2.0) ** 2
        image = np.full((resolution, resolution, 3), -1.0, dtype=np.float32)
        image[..., 0][circular_mask] = -1.0 + 2.0 * red[circular_mask]
        image[..., 1][circular_mask] = -1.0 + 2.0 * cyan[circular_mask]
        image[..., 2][circular_mask] = -1.0 + 2.0 * cyan[circular_mask]
        self.image = visual.ImageStim(
            win,
            image=image,
            size=(diameter, diameter),
            units="deg",
            interpolate=True,
            autoLog=False,
        )

        span = float(fusion_frame_span_deg)
        width = float(fusion_frame_width_deg)
        count = 16
        cell = span / count
        colors = ("white", "#777777")
        self.frame_elements: list[Any] = []
        for index in range(count):
            offset = -span / 2.0 + cell * (index + 0.5)
            color = colors[index % 2]
            self.frame_elements.extend(
                [
                    visual.Rect(win, width=cell, height=width, pos=(offset, span / 2.0), fillColor=color, lineColor=color, units="deg", autoLog=False),
                    visual.Rect(win, width=cell, height=width, pos=(offset, -span / 2.0), fillColor=color, lineColor=color, units="deg", autoLog=False),
                    visual.Rect(win, width=width, height=cell, pos=(span / 2.0, offset), fillColor=color, lineColor=color, units="deg", autoLog=False),
                    visual.Rect(win, width=width, height=cell, pos=(-span / 2.0, offset), fillColor=color, lineColor=color, units="deg", autoLog=False),
                ]
            )
        fixation_diameter = float(fixation_diameter_deg)
        self.fixation_outer = visual.Circle(win, radius=fixation_diameter / 2.0, fillColor="white", lineColor="white", units="deg", autoLog=False)
        self.fixation_inner = visual.Circle(win, radius=fixation_diameter / 4.0, fillColor="black", lineColor="black", units="deg", autoLog=False)

    def draw(self) -> None:
        self.image.draw()
        for element in self.frame_elements:
            element.draw()
        self.fixation_outer.draw()
        self.fixation_inner.draw()


class AlignmentCheckStim(BaseVisualStim):
    def __init__(self, win, *, fusion_frame_span_deg: float, fusion_frame_width_deg: float) -> None:
        super().__init__(win, units="deg", name="alignment_check", autoLog=False)
        span = float(fusion_frame_span_deg)
        width = float(fusion_frame_width_deg)
        self.frame = visual.Rect(win, width=span, height=span, fillColor=None, lineColor="white", lineWidth=3, units="deg", autoLog=False)
        self.red_marker = visual.Circle(win, radius=0.65, pos=(-2.4, 0), fillColor="#FF0000", lineColor="#FF0000", units="deg", autoLog=False)
        self.cyan_marker = visual.Circle(win, radius=0.65, pos=(2.4, 0), fillColor="#00FFFF", lineColor="#00FFFF", units="deg", autoLog=False)
        self.vertical = visual.Rect(win, width=width, height=1.2, pos=(0, 0), fillColor="white", lineColor="white", units="deg", autoLog=False)
        self.horizontal = visual.Rect(win, width=1.2, height=width, pos=(0, 0), fillColor="white", lineColor="white", units="deg", autoLog=False)

    def draw(self) -> None:
        self.frame.draw()
        self.red_marker.draw()
        self.cyan_marker.draw()
        self.vertical.draw()
        self.horizontal.draw()


def register_binocular_stimuli(stim_bank: Any, settings: Any) -> None:
    params = dict(settings.rivalry_stimulus)

    @stim_bank.define("anaglyph_rivalry")
    def _rivalry_factory(win, red_orientation_deg=None, cyan_orientation_deg=None, **overrides):
        merged = dict(params)
        merged.update(overrides)
        red_orientation = merged.pop("left_orientation_deg") if red_orientation_deg is None else red_orientation_deg
        cyan_orientation = merged.pop("right_orientation_deg") if cyan_orientation_deg is None else cyan_orientation_deg
        merged.pop("left_orientation_deg", None)
        merged.pop("right_orientation_deg", None)
        return AnaglyphRivalryStim(
            win,
            red_orientation_deg=float(red_orientation),
            cyan_orientation_deg=float(cyan_orientation),
            **merged,
        )

    @stim_bank.define("alignment_check")
    def _alignment_factory(win, **overrides):
        merged = {
            "fusion_frame_span_deg": params["fusion_frame_span_deg"],
            "fusion_frame_width_deg": params["fusion_frame_width_deg"],
        }
        merged.update(overrides)
        return AlignmentCheckStim(win, **merged)
