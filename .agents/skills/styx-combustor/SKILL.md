---
name: styx-combustor
description: Design and simulate native nTop combustors and couple them to rotating engine flow in STYX. Use for liquid-fuel combustion, liner and injector studies, combustion controls, or engine coupling with saved numerical evidence.
---

# Native combustor design and simulation

Use the user's native geometry, operating inputs and requested physical model.
Keep design choices, numerical verification and hardware validation separate.
For the Jet20 study, first read [references/jet20.md](references/jet20.md).
That reference records reusable findings and the limits of the source study.

## Design basis

Identify the engine revision, native body identities, units and shaft axis.
Trace inlet total pressure and temperature, outlet pressure, fuel rate and
fuel temperature to saved inputs. Record assumptions separately.
Keep liner holes, injectors, cooling passages and service connections explicit.
Check both native and reconstructed gas at every fuel and ignition source.
Use measured clearances and connected passages. A display mesh is not proof
that a flow passage is open or a pressure boundary is sealed.

Preserve delivered notebooks. Put design changes in a separate revision.
Keep native custom-block input contracts and source hashes. Save authored
notebooks with their sections and blocks collapsed, leaving the root open.
Do not change fuel rate, hole sizes or boundary pressures only to force ignition.
When a design trade is requested, vary documented inputs and retain each result.

## Select the calculation's scope

- A source-cell test checks liquid exchange and chemistry budgets.
- A stationary combustor checks spatial transport in its native geometry.
  Prescribed compressor-delivery reservoirs do not demonstrate compressor work.
- A full engine must solve the compressor, combustor and turbine together.
  Retain moving native blades, wall torque and work, and conservative transfer.
  A prescribed pressure rise, work map or rotating display does not supply this evidence.

Retain the requested model scope. Use a smaller calculation to diagnose a
failure, but label it as a component result. Do not substitute its success
for a full-engine result.

## Numerical workflow

Start from the current SPEC and accepted checkpoint chain. Check processes
before launching a solver. Use one local GPU solver at a time and `uv` for Python.
Keep local pilots bounded. An initial sub-minute pilot checks the execution
path; it is not an accuracy study. Change only the scale setting when scaling.
Cloud runtime needs a current allowance; a previous allowance may have expired.

Check native blade material, tip gaps and gas connectivity before interpreting
pressure rise. Use independent sample seeds and rotor phases. Refining only
known failed points can hide errors elsewhere. Full-body refinement can exceed
memory before flow starts; measure tree capacity before allocating cut volumes.
Native scalar values are not necessarily signed distances. Use their signs
for geometry, and do not assume a scalar magnitude bounds distance to a surface.

Keep separate gas pockets separate during small-cell merging. Measure how
conservative grouping changes the initial temperature field. Coarse grouping
can mix a hot liner with cold feed air before the first physical time step.
Retain mass, energy, elemental, liquid-wall and liquid-exit budgets.
Store chemical heat and external ignition energy as separate quantities.
Compare reconstructed volume change with rigid-wall pressure work. Global
conservation alone does not establish correct cell temperature or rotor power.
If testing swept-volume pressure work, retain its geometric correction ledger.
Keep that numerical comparison separate from shaft-work qualification.

Check the complete startup gas field. A hot liner with a cold turbine at
full shaft speed is a different experiment from a hot operating start.
Use recorded station states for an explicitly labelled initialization study.
Record the spatial mapping and added initial inventory. Apply it only at time
zero; never maintain station pressures or reheat an accepted continuation.
Changed initialization identities require separate cases and checked restarts.

Use a documented mechanism and property ranges. In Jet20, keep the retained
n-dodecane mechanism and liquid parcel model unless a new model is authorized.
Assess transport, source splitting and outer coupling intervals separately.
Keep failed numerical comparisons. Do not loosen a threshold after seeing
the result or select an unqualified performance implementation silently.
Replay saved source failures before changing the engine settings. Low-temperature
trace species can need tighter ODE tolerances. Measure their effect on the
same source input, retain budgets, and then test the change in the native case.

## Evidence for combustion

First verify that fuel and oxygen are consumed and products form. Recompute
the species inventory independently from saved states and boundary/source ledgers.
Check chemical heat against that conversion. A hot initial field is not ignition.

For sustained burning, remove external ignition support and continue fuel flow.
Run a matched fuel-off branch from the same gas and liquid state. Preserve its
original cutoff through every restart. Use the same interval schedule.
Measure initial-gas replacement and whether the solution remains dependent on
the hot start. Positive heat release at one time is not a sustained result.

An origin label started at a restart labels all gas then present, including
cold feed air. It is not automatically a hot-gas tracer. Gas inventory divided
by gross outflow is a timescale, not a measured residence-time distribution.
Report the label start time, inlet labeling and budget with each conclusion.

If external air dominates the domain inventory, also measure replacement in
the liner and turbine. Bind the labelled region to recorded native grid
centers and design inputs. Check that conversion preserves every physical
state array. A regional label can leave the burner while remaining elsewhere
in the domain; report local fractions and total inventory separately.
Compare source chemistry, transport, moving-body flow and a native interval
before using the observer in a longer study. Fold the inert label back into
physical nitrogen in chemical inventories. Do not count relabelling as a reaction.

The initial fuel inventory also bounds interpretation. Net fuel disappearance
in excess of all fuel initially present proves some injected fuel converted.
That bound does not identify its heat contribution or prove sustained burning.

Initial CO, hydrogen and radicals can also release chemical energy. For a
hot start, compare the independently recovered reaction enthalpy with the
initial mixture's complete-oxidation potential at a fixed reference temperature.
Use the same mechanism and verify all boundary compositions. Keep this chemical
inventory quantity separate from integrated heat, sensible energy and power.
An excess can bound the contribution from new fuel. A zero lower bound does
not mean no injected fuel reacted. It means this bound cannot separate it.

For engine acceptance, also measure compressor absolute total-pressure rise,
mass flow, rotor torque times shaft speed and the energy balance. Check their
space/time sensitivity. Keep prescribed-speed operation separate from free-spool operation.

## Records and display

Each accepted record needs physical time, input and code hashes, numerical
settings, boundary conditions, source inventories and restart identity.
Do not load a checkpoint onto changed geometry without a verified state-transfer method.
Preserve partial and failed records. Freeze modules used by an active job.
For a partial-run inventory audit, require a closed failure record and an
exact match between checkpoint time and the last accepted trace. Label the
audit as partial. A passing inventory does not make the stopped run complete.

Publish actual saved fields with their physical clocks and rotor phase.
Keep component, full-engine and numerical-study cases distinct. A playback
sequence can compress time but must not invent fields or chemical flames.
Archive compact receipts and source versions. Link large native assets rather
than duplicating them. Report exactly which checks passed and which remain open.
