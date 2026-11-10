# Native rendering details

## Runtime and capture

Inspect the installed Kit build and its bundled examples before using an API.
Import `omni.*` runtime services after the Kit application starts. Verify the
selected viewport, camera path, resolution, renderer, stage units, and up axis.
Stage opening alone does not prove that meshes, materials, and textures loaded.
Capture a small pilot and inspect its actual pixels and logs.

Use the native viewport capture API with rendering explicitly synchronized.
For a recorded simulation, stop timeline auto-play. Set each source pose,
flexible route, wheel angle, and display texture before waiting for rendered
updates. Do not capture immediately after a setter and assume the GPU caught up.
Read back the camera and record capture completion.

Clear conflicting authored time samples when setting a camera or transform
explicitly per output frame. USD time samples can override a newly set default.
Do not clear unrelated animation. Keep an explicit mapping from output time to
USD time codes, recorded motion, smoke state, and chart texture.

Evaluate rotations from the mechanism or use valid rigid interpolation. Do not
linearly interpolate matrix elements. Preserve wheel phase through speed changes.
For a stationary reverse-spin drop, do not invent aircraft translation.

## Camera continuity and scene scale

Keep focal length, film aperture, aspect ratio, camera pose, and target together.
Changing portrait/landscape output changes the crop. Match field of view at
branch and winner endpoints, not just nominal focal length. Assert the camera
actually used for capture. Check that the complete assembly stays in frame.

Check horizon and vertical direction in the environment. Use ground geometry
and correct texture scale to establish perspective. Keep exterior context at
credible apparent scale. Validate the reference camera before rendering a long
sequence. Do not alter mechanical geometry to hide a camera problem.

## Temporal quality

For continuous shots, preserve lighting, denoiser, and temporal history between
frames. Reset at a true cut or discontinuity. Broad resets every frame can cause
flashing in reflections and indirect lighting. Cold frames need a separate
warm-up; measure this instead of reporting cold-start cost as steady throughput.

In the local Kit 110.1.5 example, cold shots waited 64 rendered updates and
sequential frames waited four. These are measured starting points, not universal
requirements. Recheck on a different scene, GPU, renderer, or build.

Smoke is a timed visual effect unless a fluid simulation supplied it. Use solved
contact/slip to trigger it. Keep emission brief and verify first contact and
clearance in a continuous clip. Removing a mesh from the render index may be
necessary when simple visibility leaves stale transparent wisps. In the local
build, a narrow DLSS history reset on smoke removal avoided broad lighting resets.
Confirm the setting exists before applying it to another build.

Use actual result fields for stress. Assign transparency to context materials
separately so analyzed parts remain opaque. Verify this in an oblique close-up.
Use fixed lighting and a shared stress scale when comparing variants.

## Measure and distribute work

Benchmark the whole capture path and inspect its components. Repeated backward
seeks in a gzip motion file can cost more than rendering. Cache an identical
decoded record for frozen inspection frames or use an indexed uncompressed file.
Validate cached records by source hash. Keep geometry and loads unchanged.

Report resolution, renderer, settings, sample count, cold/steady distinction,
and whether encoding or I/O is included. Do not extrapolate a small grid panel
to 1080p or 4K without measuring it. Do not assume A100 or SPARK is faster or
compatible with RTX rendering because it is fast for compute.

For an authorized remote workstation, first check SSH, GPU, driver, disk space,
runtime, and a small native capture. Use an isolated job folder and absolute
portable asset paths or a resolved USD package. Use normal caches and licensing.
Never store passwords or private keys in a scene archive. Keep each worker's
runtime/cache local. Verify collected file hashes before editing.

Distribute independent shots or revisions. Starting a chunk in the middle of a
continuous shot can change temporal history; warm it from preceding frames and
inspect the seam. Do not compare images captured at different quality settings
as a hardware benchmark. Stop only verified task-owned processes when recovery
is required. Paid resources need the user's scope and budget authorization.
