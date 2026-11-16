# Result files and restart

## `result_format`

OpenQP 1.3.1 writes saved results as JSON. The 1.4 release candidate uses
a standalone `.npz` file by default. To write standalone JSON, set
`input(result_format=json)` to the `.oqp` input. The accepted values for
`input.result_format` are `npz` and `json`.

## Workflow status

With `guess(save_mol=true)`, the release candidate records the final
workflow status in both NPZ and JSON after the calculation driver returns.
The saved `workflow` object contains these fields.

- `workflow.completed` is `true` for a completed calculation and `false` for
  an incomplete one.
- `workflow.status` is `completed` or `incomplete` in the final result.
- `workflow.reasons` lists recorded reasons for an incomplete calculation,
  such as reaching the geometry optimization iteration limit.

An older file without `workflow` metadata leaves its completion status
undetermined. See [Calculation logs](calculation-logs.md#termination-status)
for the corresponding log messages.

## Restart

For a calculation that saves molecular data for restart, use
`guess(save_mol=true)`. To use the saved state as the initial guess, supply
the full filename in `guess(type=json,file="water.npz")`. The `json` guess
type also accepts a standalone `.json` result. For a legacy result stored as
a JSON manifest with a separate NPZ file, supply the manifest path and keep
both files together.

An explicitly supplied restart file must exist and contain a valid result.
Keep the corresponding result file until the restart has been checked. See the
[1.3 quickstart](https://www.openqp.org/manual/quickstart/) for the general
`.oqp` calculation workflow.

### Numerical Hessian and NAC checkpoints

Numerical Hessian and nonadiabatic coupling calculations save the full molecular
orbital data that their displaced calculations need. The child calculations
read the actual checkpoint written by the parent, including its NPZ or JSON
extension and any geometry index. Child inputs preserve explicit zero and
false values from the parent configuration.

### NAMD restart continuity

If the electronic-state overlap used for norm-preserving interpolation (NPI)
loses rank, propagation stops before advancing that step or replacing the
last accepted checkpoint.

**Development preview.** The analytic NAMD candidate uses checkpoint schema 9
and trajectory schema 8 to retain the electronic continuation state,
including analytic coupling history and warm-start data. An explicit restart
from an older checkpoint schema stops with an incompatibility error and
preserves the old checkpoint and trajectory files. Use a separate output
name for a fresh trajectory so the original files remain available.
Native continuation checks and the final release format are pending.
