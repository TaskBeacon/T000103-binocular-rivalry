# Task Plot Review

## Evidence Match

- PASS: Task title, construct, two counterbalanced color-to-orientation mappings, and three trial phases match `taskbeacon.yaml`, configuration, README, and task logic audit.
- PASS: Both rows show 2 s alignment, a fixed 120 s rivalry-report window, and a 2 s fixation ITI in the implemented order.
- PASS: The response mapping is exact: F for left tilt, J for right tilt, and Space for mixed perception.
- PASS: Alignment and report screens preserve the same physical red/cyan cross-hatched display within each condition; the diagram does not imply that the stimulus itself alternates.
- PASS: The opposing grating orientations, circular aperture, central fixation, and achromatic fusion ring match the implemented stimulus structure.

## Visual Quality

- PASS: Final 1536 x 1024 image is a 24-bit RGB PNG with readable text at normal preview size.
- PASS: Two rows, three screens per row, arrows, timings, and condition labels are aligned and non-overlapping.
- PASS: Screen snapshots use consistent scale and aspect ratio; no stimulus or screen is clipped.
- PASS: The title and `Construct:` subtitle fit inside the reserved white header band without touching the timeline.
- PASS: The borderless TaskBeacon lockup is legible at top right and does not overlap the title.
- PASS: No people, equipment, invented phases, feedback, reward, or decorative scene appears.

## README Embed

- PASS: `README.md` embeds `![Task Flow](task_flow.png)` immediately under `## 2. Task Flow`.
- PASS: Raw and final assets are saved at the required paths.

## Decision

Accepted after four image-generation rounds. Round 2 removed the dark vignette and clarified row counterbalancing; round 3 corrected the stimuli to opposing superimposed orientations; round 4 expanded the header-safe area to prevent subtitle overlap.
