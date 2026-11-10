# Native renders and optimization movies

Use this reference only when delivering geometry views or movies. Scientific acceptance and media completion are separate tasks.

## Truthful states and views

Replay actual saved coefficients in the admitted native notebook. Save the notebook before rendering. Use the native rendering tool or the installed `ntop-notebook-api` screenshot procedure. Keep a receipt mapping each image to the notebook, coefficient vector, camera, and state.

Pair each native state with its actual saved CFD fields. Do not synthesize intermediate shocks or reuse baseline flow for a changed shape. Distinguish trial evaluations, optimizer callbacks, returned designs, and finer-grid validation frames.

The successful inlet dashboard used native oblique and planform views, pressure recovery, mean outlet Mach, mean angle, and solver convergence. Axial Mach and density-gradient sections showed computed compression and shocks. An angled orthographic view can be labeled "Oblique"; planform remains "Planform".

Use fixed cameras, common model scale, true geometry, and consistent color ranges across a movie. Blue/red surface colors represent signed displacement from the declared baseline. Confirm the sign and units with samples.

Density-gradient numerical schlieren represents the saved density field's gradients, including compression. It is not an optical measurement. Weak or diffuse structures can reflect resolution, numerical dissipation, section placement, or the actual flow. Inspect those causes before changing the color scale. Do not add shocks that the solution does not contain.

## Cutout convention

The native inlet demo used a projected Mach-angle guide with `mu = asin(1/M_inf)` and a small rounded tip. It was a display trim on an open half-shell. A Mach angle is a characteristic angle; it is not a measured shock surface or a general shock-angle prediction.

Preserve that distinction in captions or companion provenance. Changing display geometry does not simulate a physical open inlet. If physical cutout performance is requested, create and validate the corresponding flow domain.

## Charts and presentation

Keep plotted histories, axes, units, legends, colorbars, and convergence evidence. Do not relabel the attained final value as the original optimization target. If the user wants a reference at the endpoint, label it "Final value" and retain the original targets in study metadata.

Use the user's requested layout and branding. For the completed separate inlet videos, geometry and convergence plots were above the two CFD fields. Combined comparison layouts used geometry, fields, then graphs in three rows. These are presentation choices, not constraints on future studies.

Use the installed nTop design skill when requested. This project overrode its background with `#F7F8FA` and retained Aeonik typography. Composite the official nTop logo **after all panels**, with a visible margin. Earlier versions hid it behind the field panel. Verify the logo in encoded frames, not only in source artwork.

If detailed footnotes are removed for social videos, preserve scientific scope and evidence in companion files. Exporting files does not authorize posting them.

## Encode and verify

For the requested 15-second versions, shorten saved-state holds. Preserve every saved state without interpolating fields. Label a final finer-grid validation state separately from optimizer iterations. Synchronize comparison videos by elapsed time without implying equal iteration counts.

Test a short encode first, then scale duration using the same settings. The local Windows FFmpeg build worked reliably with single-thread decoding/filtering/encoding, `libx264`, `yuv420p`, and fast-start MP4. Measure compatibility on another machine instead of assuming this workaround is necessary.

Verify the full decode, dimensions, frame count, duration, saved-state coverage, and first/middle/final frames. Check chart labels and the complete logo outline. Preserve the original movies, source frames, and export manifests when revising presentation.
