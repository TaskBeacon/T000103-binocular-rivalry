# Assets

This task generates its red/cyan sinusoidal gratings, fusion frame, and fixation target at runtime with PsychoPy primitives and NumPy arrays. No external media assets are required.

The human profile requires red-cyan anaglyph glasses with the red filter over the left eye and cyan filter over the right eye. Sites using a different filter order must document that deviation with the participant metadata and should calibrate `task.rivalry_stimulus.red_gain` and `cyan_gain` for their display.
