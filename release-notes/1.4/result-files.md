# Result files and restart

## `result_format`

The current 1.4 candidate writes JSON by default. Set
`input(result_format=npz)` in the `.oqp` input to select standalone NPZ.
Accepted values are `json` and `npz`. Earlier beta builds used NPZ by default.
Use the [saved-result reader](api/results.md#reading-saved-results) for both formats.

## Workflow status

The earlier beta added workflow metadata to saved results after the calculation
driver returned. The current 1.4 branch does not provide that saved-status
contract. When reading a beta result with a `workflow` object, interpret these
fields as follows.

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
[Quickstart](quickstart.md) for the general
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

The 1.4 checkpoint stores the MRSF Z-vector warm-start state in
restart schema 10. Trajectory files use schema 7. An incompatible checkpoint
schema is rejected before restoration. Keep the original checkpoint and its
matching trajectory together. Use new output filenames for a fresh trajectory.

The fixed-order option is `scf(fock_reproducible=true)`
(default `false`). It uses fixed OpenMP work assignments and accumulation
order in the native Fock and selected XC and gradient builders. Use the same
binary, OpenMP and BLAS thread counts, and calculation inputs throughout a
restart comparison. The tested NAMD path uses the native CPU engine with
finite-difference time-derivative couplings and isotropic velocity rescaling.
GPU-linked builds, external providers, and multiple MPI ranks are outside
the supported fixed-order path. The option does not promise identical results
across thread counts, builds, or platforms.

#### Ethylene restart example

Download the [ethylene input](ethylene-namd-restart.oqp) and
[geometry](ethylene-namd-restart.xyz) to the same directory. The input
starts on S2 with MRSF/BHHLYP/6-31G, explicitly selects Hückel and fixed-order
accumulation, and requests 800 steps of 0.125 fs. It writes a checkpoint
at each step.

To continue, keep an accepted checkpoint and the trajectory prefix through
that same step. Run the generated restart input with `restart=true` and the
matching checkpoint and trajectory paths. Keep `nstep=800` to finish at
100 fs. The 50 fs continuation starts from the checkpoint at step 400.

On Linux x86-64, the 1.4 candidate's uninterrupted 100 fs run and
continuation from 50 fs met the absolute restart tolerance of 10⁻¹¹
and the NVE energy criteria with two OpenMP threads and one BLAS thread.
In a separate check, a restart from 28.25 fs reproduced the hop at
28.375 fs. Both used a 0.125 fs step and reproduced earlier macOS
checks made with the same scientific input. These comparisons apply
to the stated input and settings on each platform.

In the separate macOS test at 0.25 fs, the restart met the continuity
tolerance. The adjacent-step energy change at 28.5 fs exceeded the
0.001 hartree acceptance limit, as it did with the engine predating
the checkpoint change.
