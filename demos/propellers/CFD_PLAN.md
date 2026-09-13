# Propeller optimization plan and recorded pilot

## Recorded result

A five-iteration FUN3D 14.2 CPU smoke test completed on GCP. Its wall velocities matched angular velocity crossed with radius.
A longer request reached 956 iterations before a 600-second cutoff. Its force history remained finite.
Neither run establishes converged propeller performance. A later AFLR3 prism-layer mesh completed and passed independent positive-volume checks. Near-wall resolution and mesh sensitivity remain unqualified. No aerodynamic optimum, wake animation, or acoustic prediction is delivered here.
The cloud worker was stopped after the pilot and log-recovery sessions. Cloud configuration, licensed executables, and solver outputs are not part of this public folder.

## Provisional conditions

Use nominal diameter 0.2032 m. The exploratory speed is 15,810 RPM from the published Scorpion 7 x 4 test chart.
That chart does not validate the different eight-inch model. The chosen advance ratios are 0.2, 0.4, and 0.6.
Their speeds are 10.7088, 21.4176, and 32.1264 m/s, calculated from J = U/(nD).
Dry air at 288.15 K and 101,325 Pa is an assumed pilot condition. Set mission thrust, speed, motor power, and noise limits before optimization.

## Execution sequence

1. Replay the selected native graph and validate the bore, hub faces, spinner clearance, diameter, connectivity, and mesh topology.
2. Export millimetres explicitly. Convert to metres and map native (x,y,z) to CFD (z,x,y). Verify this proper rotation and all dimensions.
3. Generate a boundary-layer volume mesh. Inspect cell quality, surface error, y-plus, and domain extent. Retain failed trials.
4. Run a sub-minute rotating-frame solver check. Verify every wall velocity and the thrust/torque sign before scaling the run.
5. Converge each baseline, then establish mesh and domain sensitivity. Compare efficiency at matched thrust and operating condition.
6. Parameterize chord, twist, camber, sweep, and loop-shape controls within each topology. Keep mounting constraints fixed.
7. Verify adjoint gradients against finite differences for a small set of controls. Use a finite-difference trust-region search if the chosen solver lacks a verified adjoint path.
8. Evaluate finalists with a verified unsteady rotating-grid model and a suitable acoustic method such as FW-H. Check timestep, sampling duration, and observer placement.
9. Render time-resolved vorticity or Q-criterion from actual unsteady output. Report efficiency, thrust, power, and noise as a Pareto comparison.

Use the solver capabilities actually installed. The pilot used CPU FUN3D 14.2; GPU noninertial support was introduced in FUN3D 14.3.
Solver startup and finite forces are smoke evidence. They do not substitute for numerical convergence or validation.
The reference performance discussion is a plan, not a claim that unusual loop shapes are efficient or quiet.

## Public sources

- [Scorpion SII-2212-1400KV](https://www.scorpionsystem.com/catalog/clearance/motor_1/sii_-_airplane_motor/SII-2212-1400KV/)
- [Motor test chart](https://www.scorpionsystem.com/files/i2,913_data_chart.pdf)
- [FUN3D manual](https://fun3d.larc.nasa.gov/papers/FUN3D_INTG_Manual-14.3.pdf)
- [FUN3D release history](https://fun3d.larc.nasa.gov/chapter-1.html)
- [DAFoam UAV propeller example](https://dafoam.github.io/user-guide-uav-prop.html)
- [NASA Mobius propeller study](https://ntrs.nasa.gov/citations/20010088092)

## Marine separation

Ship-scale marine concepts require water properties, shaft speed, advance speed, immersion, and cavitation conditions.
Do not apply the aircraft pilot RPM or air conditions to the marine screw. Establish its mechanical shaft interface before analysis.
