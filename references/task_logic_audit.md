# Task Logic Audit

## 1. Paradigm Intent

- Task: Binocular Rivalry
- Primary construct: spontaneous alternation of visual awareness under interocular conflict
- Manipulated factors: color-to-orientation mapping (`red_left_cyan_right`, `red_right_cyan_left`); the eye/filter assignment remains fixed by the red-left/cyan-right glasses setup
- Dependent measures: report sequence, report timestamps, left-tilt and right-tilt dominance durations, mixed-percept durations, predominance fractions, and alternation rate
- Key citations: `W1978904320`, `W1995722596`, `W2094802109`, `W2027777783`
- Mechanistic background only: `W2095696274`

The canonical implementation is an attended, continuous-report rivalry task. It is not a detection or accuracy task. Two incompatible sinusoidal gratings are delivered dichoptically through red-cyan anaglyph glasses. The physical display remains constant while the participant reports spontaneous changes in the dominant percept.

## 2. Block/Trial Workflow

### Block Structure

- Total blocks: 2
- Trials per block: 2
- Total rivalry trials: 4
- Rivalry duration: 120 s per trial, following Naber et al. (2011), Experiment 1
- Randomization/counterbalancing: each block contains one `red_left_cyan_right` and one `red_right_cyan_left` trial in randomized order. This adapts the cited randomization of orientation, color, and eye assignment while keeping the physical filter-eye assignment fixed for anaglyph presentation.
- Condition weight policy: equal weights are defined in `task.condition_weights`; runtime resolution is delegated to `TaskSettings.resolve_condition_weights()`.
- Condition generation method: built-in `BlockUnit.generate_conditions(...)`; labels fully express the only experimental factor.
- Runtime-generated trial values: none. Grating geometry is deterministically realized from the condition label and config parameters.

Before the first block, the participant sees: (1) hardware and response instructions; (2) an anaglyph alignment/check screen; and (3) a short practice rivalry display. The practice is not included in the four analyzed trials.

### Trial State Machine

1. `alignment_fixation`
   - Onset trigger: `alignment_fixation`
   - Stimuli shown: achromatic fusion frame, central fixation target, and the two colored grating channels at low contrast
   - Duration: 2 s
   - Valid keys: none
   - Timeout behavior: advance after 2 s
   - Next state: `rivalry_report`
2. `rivalry_report`
   - Onset trigger: condition-specific `rivalry_red_left_cyan_right` or `rivalry_red_right_cyan_left`
   - Stimuli shown: spatially superimposed red and cyan sinusoidal gratings at opposing orientations, inside a circular aperture, plus the achromatic fusion frame and fixation target
   - Duration: fixed 120 s
   - Valid keys: `f` (left-tilted percept), `j` (right-tilted percept), `space` (mixed/patchwork percept)
   - Response behavior: every non-repeat keydown is retained with its time from rivalry onset; the display does not terminate on response
   - Timeout behavior: the fixed window closes normally; zero reports are retained as `no_report`
   - Next state: `iti`
3. `iti`
   - Onset trigger: `iti`
   - Stimuli shown: central fixation on the black background
   - Duration: 2 s
   - Valid keys: none
   - Timeout behavior: advance after 2 s
   - Next state: next trial or block break

## 3. Condition Semantics

- Condition ID: `red_left_cyan_right`
  - Participant-facing meaning: the red channel contains a grating tilted 60 degrees left of vertical; the cyan channel contains a grating tilted 60 degrees right of vertical.
  - Concrete stimulus realization: two 2-cycles/degree sinusoidal gratings, circularly windowed and spatially coincident behind a shared fusion frame.
  - Outcome rules: no correct outcome; reports label the currently dominant percept.
- Condition ID: `red_right_cyan_left`
  - Participant-facing meaning: the red channel contains the right-tilted grating and the cyan channel contains the left-tilted grating.
  - Concrete stimulus realization: identical geometry and luminance policy with the color-orientation mapping swapped.
  - Outcome rules: no correct outcome; reports label the currently dominant percept.

- Participant-facing text source: `config/*.yaml` stimulus definitions.
- Grating parameter source: `task.rivalry_stimulus` in config, consumed by `src/stimuli.py`.
- Localization strategy: instruction, calibration, break, and completion text can be replaced in config without changing trial code.

## 4. Response and Scoring Rules

- Response mapping: `f = left_tilt`, `j = right_tilt`, `space = mixed`.
- Response key source: `task.report_keys` in config.
- Missing-response policy: retain the trial with an empty report sequence and `outcome = no_report`; do not impute a percept.
- Correctness logic: not applicable because perceptual report has no externally correct answer.
- Reward/penalty updates: none.
- Running metrics: report count, unique-state transition count, alternation rate per minute, median left/right dominance duration, and predominance fractions. Consecutive duplicate reports are preserved raw but collapsed for derived intervals.
- Boundary rule: intervals before the first report and after the last report are excluded from median dominance-duration estimates because their true onset/offset is unknown. They remain auditable in raw stage timing.

## 5. Stimulus Layout Plan

- Screen name: `alignment_check`
  - Stimulus IDs shown together: `alignment_red_marker`, `alignment_cyan_marker`, `fusion_frame`, `fixation`, `alignment_text`
  - Layout anchors: red marker at `[-4, 0]`, cyan marker at `[4, 0]`, centered fusion frame and fixation, text below at `[0, -6]`
  - Size/spacing: markers at least 4 deg apart; text height 0.55 deg and wrap width 24 deg
  - Readability/overlap checks: markers remain inside the central 12-deg region; instruction text stays below the frame
  - Rationale: verifies that both color channels are visible through the intended filters before data collection.
- Screen name: `rivalry_report`
  - Stimulus IDs shown together: `anaglyph_rivalry`, `fusion_frame`, `fixation`
  - Layout anchors: all centered at `[0, 0]`
  - Size/spacing: grating aperture diameter 8 deg; fusion frame outer span 10 deg; central fixation diameter 0.25 deg
  - Readability/overlap checks: fusion frame stays outside the rivalrous aperture; fixation remains visible to both eyes; no response reminder text is shown during the 120-s measurement window
  - Rationale: the cited experiments use a central fixation point and a surrounding fusion aid for stable binocular alignment.

## 6. Trigger Plan

- `experiment_start`: 1
- `instruction`: 5
- `alignment_check`: 6
- `practice_rivalry`: 7
- `block_start`: 10
- `alignment_fixation`: 20
- `rivalry_red_left_cyan_right`: 31
- `rivalry_red_right_cyan_left`: 32
- `report_left_tilt`: 41
- `report_right_tilt`: 42
- `report_mixed`: 43
- `rivalry_no_report`: 44
- `iti`: 50
- `block_end`: 90
- `experiment_end`: 99

## 7. Architecture Decisions (Auditability)

- `main.py` runtime flow style: one explicit mode-aware flow with instruction, alignment/practice, block generation, trial execution, summaries, and final export.
- `utils.py` used: yes; only for condition decoding, response-sequence cleaning, dominance-interval derivation, and summary statistics.
- `stimuli.py` used: yes; only for the task-specific anaglyph grating composite and fusion frame, a PsychoPy stimulus type not available in YAML `StimBank`.
- Custom controller used: no.
- Framework extension: PsyFlow `StimUnit.capture_response(...)` receives a backward-compatible `count_responses` option so the public response runtime, triggers, timing, QA, and persistence continue to own continuous keyboard capture. The equivalent existing PsyFlow-Web option is completed so it retains response identities as well as timestamps.
- Legacy/backward-compatibility fallback logic required: no.

## 8. Inference Log

- Decision: use red-cyan anaglyph presentation as the default hardware path.
  - Why inference was required: cited protocols primarily used mirror stereoscopes or dual displays, while the requested task must be deployable with red-blue/red-cyan glasses or another dichoptic method.
  - Citation-supported rationale: the papers require dichoptic delivery but do not require a unique optical device; anaglyph separation preserves eye-specific incompatible images with inexpensive hardware.
- Decision: use an 8-deg circular aperture and a 10-deg fusion frame.
  - Why inference was required: cited protocols range from 1.8-deg gratings to 10-deg annuli and much larger motion displays.
  - Citation-supported rationale: 8 deg preserves the circular, fixated rivalry region while remaining practical at the configured 57-cm viewing distance.
- Decision: use equal nominal channel contrast with configurable `red_gain` and `cyan_gain`.
  - Why inference was required: filter transmission and monitor primaries vary across sites, so literature luminance values cannot be transferred exactly to an unknown display/glasses pair.
  - Citation-supported rationale: Naber et al. manipulated channel luminance and contrast and randomized color/orientation assignment; configurable gains plus mapping counterbalancing make the local hardware calibration explicit.
- Decision: use discrete change reports, including a mixed-state key, rather than joystick deflection or press-and-hold duration.
  - Why inference was required: standard keyboards are the shared input device for Python and Web deployments.
  - Citation-supported rationale: Knapen et al. used button reports; Naber et al. used both button and continuous joystick/held-key reports and explicitly treated intermediate percepts.
- Decision: run 2 blocks x 2 trials rather than the full 16-trial luminance/contrast manipulation.
  - Why inference was required: this TaskBeacon variant is a baseline spontaneous-alternation assay, not a contrast psychophysics study.
  - Citation-supported rationale: the canonical 120-s measurement window is retained, while the two mapping conditions provide counterbalancing without introducing a new scientific manipulation.
