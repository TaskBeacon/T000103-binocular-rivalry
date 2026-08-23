# Parameter Mapping

## Mapping Table

| Parameter ID | Config Path | Implemented Value | Source Paper ID | Evidence (quote/figure/table) | Decision Type | Notes |
|---|---|---|---|---|---|---|
| `conditions` | `task.conditions` | `red_left_cyan_right`, `red_right_cyan_left` | `W1978904320` | Materials and Methods, Experiment 1: orientation, color, and eye assignment were randomized. | `adapted` | Anaglyph filter-eye assignment is fixed; color-orientation mapping is counterbalanced. |
| `condition_weights` | `task.condition_weights` | equal `1:1` | `W1978904320` | Experiment 1 used repeated presentations across grating mappings. | `adapted` | Each block contains both mappings once via PsyFlow balancing. |
| `total_blocks` | `task.total_blocks` | `2` | `W1978904320` | The source used multiple trials and scheduled breaks during an extended session. | `inferred` | Baseline TaskBeacon profile uses two four-minute blocks for tolerability. |
| `total_trials` | `task.total_trials` | `4` | `W1978904320` | Experiment 2 used repeated real-rivalry trials for each stimulus set. | `adapted` | Four trials provide two repetitions per mapping without adding a contrast manipulation. |
| `rivalry_duration` | `timing.rivalry_duration` | `120 s` | `W1978904320` | Materials and Methods, Experiment 1: each trial lasted 120 seconds. | `direct` | Human profile retains the cited measurement window. |
| `spatial_frequency` | `task.rivalry_stimulus.spatial_frequency_cpd` | `2 cycles/degree` | `W1978904320` | Experiment 1 sinusoidal gratings used 2 cycles/degree. | `direct` | Same for red and cyan channels. |
| `orientations` | `task.rivalry_stimulus.left_orientation_deg`, `right_orientation_deg` | `-60 deg`, `+60 deg` | `W1978904320` | Experiment 1 used opposing orientations of -60 and +60 degrees. | `direct` | Keys label perceived orientation rather than channel color. |
| `aperture_diameter` | `task.rivalry_stimulus.aperture_diameter_deg` | `8 deg` | `W1978904320`; `W2094802109` | Cited protocols used a central, fixated rivalry region with a surrounding alignment structure; reported sizes vary by protocol. | `inferred` | Sized for robust anaglyph rivalry at a 57-cm viewing distance. |
| `contrast` | `task.rivalry_stimulus.contrast` | `0.80` | `W1978904320` | Naber et al. explicitly varied grating contrast across a broad range. | `inferred` | High but submaximal contrast supports rivalry while leaving channel gain headroom. |
| `channel_gain` | `task.rivalry_stimulus.red_gain`, `cyan_gain` | `1.0`, `1.0` | `W1978904320` | The cited study calibrated monitor primaries and manipulated channel luminance. | `inferred` | Site-specific filter/display calibration is required; gains are explicit config values. |
| `fusion_frame` | `task.rivalry_stimulus.fusion_frame_span_deg` | `10 deg` | `W1978904320` | Experiment 1 surrounded the grating display with a high-frequency frame to stabilize fusion. | `adapted` | Implemented as an achromatic alternating-luminance frame visible through both filters. |
| `fixation` | `task.rivalry_stimulus.fixation_diameter_deg` | `0.25 deg` | `W1978904320`; `W2094802109` | Both protocols required central fixation during dichoptic stimulation. | `adapted` | Small achromatic bullseye remains visible to both eyes. |
| `report_keys` | `task.report_keys` | `F=left`, `J=right`, `space=mixed` | `W2094802109`; `W1978904320` | The studies used button reports of the dominant percept and explicitly analyzed intermediate or mixed percepts. | `adapted` | Discrete state-change reports preserve Python/Web keyboard parity. |
| `continuous_capture` | `rivalry_report.count_responses` | `true` | `W1995722596`; `W2094802109` | Real-time methods track the full sequence of spontaneous dominance changes during a constant display. | `direct` | Every valid event and timestamp is stored; the display remains on for the full window. |
| `alignment_duration` | `timing.alignment_duration` | `2 s` | `W1978904320` | The protocol used a fusion-supporting frame and head stabilization but did not specify this pretrial interval. | `inferred` | Brief stabilization period precedes each measurement window. |
| `practice_duration` | `timing.practice_duration` | `12 s` | `W1978904320` | Observers were trained to report dominance before extended measurements. | `inferred` | Short mechanism-complete practice confirms key mapping and hardware visibility. |
| `iti_duration` | `timing.iti_duration` | `2 s` | `W1978904320` | Source trials were separated by breaks; a precise short ITI was not specified. | `inferred` | Allows visual reset without materially extending the session. |
| `boundary_exclusion` | `src.utils.summarize_report_sequence` | exclude pre-first and post-last partial intervals from duration medians | `W1978904320` | Dominance durations are defined between report transitions. | `adapted` | Raw events remain stored; only incomplete boundary intervals are omitted from derived medians. |
| `trigger_codes` | `triggers.map` | `1-99` phase/event map | `W1995722596` | Real-time physiology requires time-aligned stimulus and percept events; numeric codes were setup-specific. | `inferred` | Unique codes separate stimulus mapping and each report state. |

Decision type values:

- `direct`
- `adapted`
- `inferred`
