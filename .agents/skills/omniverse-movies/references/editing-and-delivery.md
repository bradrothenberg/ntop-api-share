# Editing, retention, and delivery

## Frame and source discipline

Keep output clocks separate from source clocks. Store output frame, presentation
time, simulation time, source index, camera, stress visibility, and context
opacity in a capture manifest. Do not derive chart time from a different clock.
Treat a five-second hold, a 1X test, and a .25X replay as explicit storyboard
segments. Keep speed labels visible for their agreed full interval.

Use supplied original logos and outros. Do not rebuild an existing animation
with an approximate font. Load brand fonts before charts or title images render.
Keep references to licensed fonts rather than copying them into a shared skill.

For grids, render enough pixels for the final cell size. Do not use those small
renders for a full-screen winner close-up. Keep a suitable full-resolution native
winner source. Match pose, camera, crop, lighting, and stress scale at the point
where the winner leaves its cell. Do not dissolve two large misaligned models
into a confusing double exposure. Preview the transition before full encoding.

## Small edits using saved captures

Inspect frames and manifests before promising reuse. A saved USD scene is not
a saved no-overlay frame. A flattened stress image cannot reveal hidden physical
materials without another source. If the required captures do not exist and the
user forbids new rendering, report that limitation and preserve the current film.

Existing native frames may support a title patch or re-composition. Keep camera
registration and source timing exact. Disclose differences in old capture quality
when relevant. Do not recolor stress pixels into invented material geometry.

When the user asks to keep the rest exactly the same, prefer stream-copying
unchanged encoded sections. Verify the cut is a suitable keyframe. With FFmpeg,
check frame timing and decode after concatenation; changing timestamp offsets
can introduce a gap. Use absolute forward-slash paths inside concat lists on
Windows. Avoid re-encoding the entire movie for a small opening change.

Use `scripts/verify_movie.py` with `--reference` and `--unchanged-from-frame`
to compare the decoded remainder pixel-for-pixel. This comparison applies to
videos with aligned output frames. Retimed edits need an explicit source map.

From this skill's directory, use an explicit expected output contract. This
example checks a 10-second, 60 fps movie; replace every value with the agreed
contract and use real absolute paths:

```powershell
uv run python scripts/verify_movie.py "D:/project/final.mp4" --ffmpeg "C:/tools/ffmpeg.exe" --fps 60 --frames 600 --width 1920 --height 1080 --report "D:/project/final-audit.json"
```

For an unchanged tail, append `--reference "D:/project/previous.mp4"` and
`--unchanged-from-frame 120` using the actual first unchanged frame. Both movies
must have the same expected frame count, dimensions, and clock. The helper
records decode logs and per-frame hashes next to its JSON report. A nonzero
exit code is a failed check. It does not check audio or replace visual review.

## Final checks and retained artifacts

- Decode the complete file, including every tail segment. Confirm duration,
  frame count, dimensions, frame rate, and continuous presentation timestamps.
- Inspect encoded boundary frames and continuous samples for motion cadence,
  flicker, missing assets, smoke timing, label timing, clipping, and camera jumps.
- Check that charts and current values match recorded poses. Verify FEA legend,
  case scope, source geometry, and comparison values against saved results.
- Preserve the approved storyboard, source contract, final movie, capture
  settings, frame/source hashes, audit result, and representative review frames.
- Keep reusable source frames or lossless masters when space permits. Tell the
  user before deleting sources needed for anticipated edits. Do not delete active
  caches, models, or other tasks' captures because they appear old.

Return a local absolute path and a useful preview or file link. Do not claim
delivery from an upload URL alone. External uploads need finalization and a
readable receipt. Use the user's authorized destination; never hardcode a DM
from this landing-gear project. Do not publish native model data implicitly when
the user asked only for a video.
