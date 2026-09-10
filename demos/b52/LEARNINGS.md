# Recorded lessons

This is an edited record of prior work. Its native results apply to those recorded revisions.
Local machine paths and omitted artifact links were removed for this public handoff.
Historical tool and artifact names below describe the source work. Use README.md for the runnable commands and files in this checkout.

# R7: fair nose blend

Remove the small underside shoulder reported on R6. Preserve the rounded tip
and the accepted cockpit and fuselage. Keep earlier revisions intact.

Measure the R5 and R6 meridian curvature first. Use those measurements to
choose a geometric correction. Verify native field values and matched nose
renders. Remeasure silhouette agreement and update the HTML report.

Use existing verified native block schemas and provide the corresponding
Notebook API recipe. Validate the saved graph with nTop Automate. No fresh
Notebook API readback is claimed unless a live console becomes available.

Completed revision: B52F_Fair_Nose_Blend.ntop. The old scalar blend caused
two underside curvature sign changes. The revised cap has a quadratic
centerline and radial-growth correction. A constrained profile fit removes
the reversal while retaining the regular circular pole.

The pole radius is 54.997712 mm. The local correction ends at X = 122.076123
mm. The accepted R5 field applies exactly aft of that station. The cockpit
and all 18 window outline curves retain their existing definitions.

Native field verification: 257/257 checks pass. Maximum absolute error is
0.266430 micrometres. The companion notebook contains the exact final
geometry nodes and literals. The editable delivery has 152 variables and
eight collapsed sections. Its complete API recipe contains 409 variables.

An independent 856-sample check from X = 3.085 to 121.930 mm finds no
underside curvature reversal. R6 has two. Matched native nose renders show
the shoulder removed. The report provides a before-and-after toggle.

Updated geometric silhouette IoU: plan 99.650007%, side 99.392976%, front
99.145622%. These compare against the selected public B-52F artist model.
R5, R6, and the original input notebook are unchanged by hash verification.

Notebook SHA-256:
90177520b17f02a1d2292a71c8456122097d3131ed0b446faf1c1d76d509fcc1

Report: B52F_Fair_Nose_Blend_Report.html. Desktop/mobile theme and toggle
checks pass. Task-owned GUI PID 38164 was started at
2026-09-10T13:46:51.2964591-04:00. Verify ownership before any future use.
