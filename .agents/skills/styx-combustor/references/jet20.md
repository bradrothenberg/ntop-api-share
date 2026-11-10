# Recorded Jet20 combustion lessons

The source study used a separate STYX research implementation and native nTop
engine geometry. This package contains workflow instructions only. It does not
include that solver, its branch, model assets, run data, or active-job details.
Obtain an authorized compatible implementation before trying to reproduce it.

## Component versus engine evidence

The recorded stationary combustor used prescribed compressor-delivery reservoirs.
Independent species inventories established fuel and oxygen consumption and
product formation. The matched fuel-off branch also continued to react.
This did not establish sustained burning independent of the initial hot gas.
It did not establish compressor work or sustained full-engine combustion.

Full-engine pilots retained moving native blades and conservative transfer.
Short accepted intervals checked execution and budgets. They did not establish
operating performance. Coarse geometry missed native-solid witnesses. Finer
complete-domain refinement exceeded its allocation guard before flow advanced.
Measure geometry coverage and memory demand before increasing run duration.

## Reusable failure checks

- Check gas connectivity, thin blades, tip gaps, independent seeds, and rotor phases.
- Keep prescribed inlet reservoirs separate from a solved compressor pressure rise.
- Check cold downstream initialization before interpreting hot-start failures.
- Replay failed chemistry inputs before changing operating conditions.
- Retain mass, elemental, energy, ignition, liquid-wall, and liquid-exit ledgers.
- Preserve the fuel-off cutoff through the complete restart chain.
- A restart origin label marks all gas then present, including cold feed gas.
- Compare local tracer replacement with total inventory and species conversion.
- Check initial-mixture oxidation potential before attributing heat to new fuel.
- Global conservation does not establish correct temperature or moving-wall work.

Read the active project's specification, process state, and latest closed receipts
before resuming work. Old run names or resource allowances are not current authority.
Keep component results, numerical pilots, failed comparisons, and engine acceptance
separate. No new native or solver execution was performed for this publication.
