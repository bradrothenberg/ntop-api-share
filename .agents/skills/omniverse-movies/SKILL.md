---
name: omniverse-movies
description: Plan films with the user, then render and edit native NVIDIA Omniverse Kit movies from CAD assemblies, recorded simulations, and engineering results. Use for technical product films, mechanism demonstrations, revision comparisons, and edits to existing Omniverse movies.
---

# Omniverse movies

Deliver a film whose geometry, motion, analysis, and edit follow an agreed storyboard.
Use actual Omniverse Kit rendering when Omniverse is requested. A USD exported
from another renderer does not establish Omniverse rendering.

## Always storyboard with the user

**Always develop and review the storyboard together with the user before full rendering.**
This is an explicit user preference. Do not treat silence as approval.

1. Read the supplied references, existing edit, model, and prior decisions.
2. Ask only for missing decisions that affect the film. Useful choices include
   audience, duration, aspect ratio, playback speed, shot order, and the ending.
3. Propose a concrete storyboard with start/end times, camera framing, action,
   materials, analysis visibility, charts, text, and transitions for each shot.
4. Show representative thumbnails or a small animatic. Distinguish diagrams
   from real captures. Use existing frames when possible.
5. Save `STORYBOARD.md` inside the active project. Use the
   [storyboard template](assets/storyboard-template.md). Record which version
   the user accepted, their changes, and any remaining decisions.
6. Request review of that concrete plan. Continue independent asset checks
   while awaiting a required answer. Start full rendering after agreement.

For an edit to an approved film, review only the changed shots. A user's clear
edit instruction already supplies direction for that change. Update the local
storyboard without asking them to approve the same change again. Do not reopen
settled choices or replace the approved sequence with a new creative concept.
If a change has an unresolved consequence, show that specific consequence first.

Keep the storyboard local unless the user explicitly requests cloud storage.
Do not create a Google Drive document because the user says "save to the drive."

## Establish the source contract

Record the geometry revision and hashes, units, world axes, motion trace, result
case, camera, environment, runtime, and intended frame rate. Keep these distinct:

- Simulation time and recorded state.
- Presentation time, holds, repeats, and speed changes.
- USD time codes and display texture indices.
- Output frame numbers and encoded timestamps.

Derive poses and chart values from the same source time. Use the existing solver
or recorded trace. Do not invent forces, spring motion, stress, or new physics
to improve the shot. Identify a staged reset separately from simulated motion.
For nTop/Unlinked work, use their installed skills when authoring or changing
models. This movie skill does not authorize a new engineering study.

When showing FEA, verify that the result geometry matches the displayed part.
Keep source stress values unchanged. Use a visible legend, a common scale for
comparisons, and labels that distinguish static component cases from transient
assembly results. Record display clipping. Do not choose colors to imply an
improvement that the analysis did not establish.

## Prepare and prove the native pipeline

Read [native-rendering.md](references/native-rendering.md) for capture, camera,
temporal stability, remote execution, and performance guidance. Read
[local-example.md](references/local-example.md) for the recorded landing-gear workflow. Its external implementation is not bundled.

- Locate the installed Kit runtime and verify the active RTX renderer, GPU,
  extension versions, and usable cache paths. Use `uv` for Python operations.
- Use CLI/API capture. Do not use desktop automation to record a viewport.
- Preserve the native mechanical detail. Improve realism with materials,
  lights, environment scale, camera composition, and suitable render settings.
- Use licensed brand assets and fonts supplied or installed for the task.
  For an nTop film, use the available nTop design skill and actual brand fonts.
  Do not add slogans, titles, or outro text outside the agreed storyboard.
- Validate a short end-to-end pilot before scaling. Include contact or fast
  motion, any stress/transparency transition, and a camera cut when relevant.
  Inspect the encoded pilot, not only isolated raw frames.
- Measure cold startup and steady frame times separately, at the actual
  resolution and settings. Keep the production settings unchanged when scaling
  the proven pilot. Recheck if quality settings, hardware, or runtime change.

## Render and edit against the storyboard

Keep geometry, USD, source traces, textures, fonts or their references, camera
paths, and capture settings reproducible. Record per-frame source time, camera,
display state, frame hash, capture time, and intentional duplicate holds.

Keep temporal renderer history during a continuous shot. Reset it only when
required by a cut or discontinuity. Check moving reflections and smoke removal.
Check that a slow replay uses the correct source time at every output frame.
Increasing an encoder's fps does not create new native motion samples.

Use representative existing frames or lossless masters for revisions. If the
user permits an edit only when frames already exist, do not render new frames.
Check source geometry, pose, camera, timing, lighting, and display content before
reusing them. Disclose material differences between older captures and the
approved film rather than silently substituting an unrelated shot.

Read [editing-and-delivery.md](references/editing-and-delivery.md) for precise
cuts, grids, selective re-encoding, source retention, and delivery checks.
For comparisons, preserve actual per-revision geometry and data. Make simultaneous
or sequential playback explicit in the storyboard. Match camera framing across
the grid-to-winner transition. Keep the agreed point where context fades.

## Verify and deliver

Run [verify_movie.py](scripts/verify_movie.py) for full decode, dimensions,
frame count, frame rate, timestamps, and a file hash. It can compare an unchanged
tail against an earlier film. It does not verify engineering or visual quality.
Run it with `uv run`, the actual FFmpeg executable, and explicit expected values.

Inspect encoded frames at impact, labels, every edit boundary, transparency
changes, the winner close-up, retraction, and the outro. Review continuous clips
for flicker, motion cadence, and transitions. Do not claim a static contact sheet
proves temporal stability.

Deliver one clearly named final file, the local storyboard, and concise
verification/provenance records. Preserve earlier approved movies. Upload to
Slack or another destination only with the user's authorization and verified
destination. A past project's channel ID is not permission for a new project.
Do not upload the film until decode and visual checks pass.
