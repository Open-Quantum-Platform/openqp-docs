# `[optimize]`

The `[optimize]` section selects the optimization backend, target states, and
convergence thresholds for geometry and reaction-path workflows.

!!! note "Two input surfaces"

    Concise `.oqp` geometry drivers always use the native OpenQP engine and do
    not accept `lib`, `optimizer`, `step_size`, `step_tol`, or `mep_maxit`.
    Those five keys remain documented here for traditional sectioned `.inp`
    files and the compatible Python workflow API.

In Python scripts, use `job.workflow.optimize(...)` for the optimization runtype, common
optimization options, and backend options. For example,
`job.workflow.optimize(istate=0, coordsys="tric")` uses the native default and routes
`coordsys` to the native optimizer backend while keeping state and convergence
options in `[optimize]`. The lower-level `job.optimize(...)` section helper
remains available for existing scripts.

## Keywords

### `lib`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `oqp` |
| Values | `oqp`, `geometric`, `scipy` |
| Used by | optimizer backend selection |

Traditional `.inp` and Python API backend selector. The native `oqp` backend
supports `optimize`, `ts`, `meci`, `mecp`, `tci`, `neb`, `irc`, and `mep`.
geomeTRIC supports `optimize`, `meci`, `mecp`, `ts`, `irc`, and `neb`; it is
retained chiefly as an optional constrained-optimization escape hatch. SciPy is
a legacy backend for `optimize`, `meci`, `mecp`, and `mep`.

DL-FIND is not a current user-facing optimizer backend.

### `optimizer`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `bfgs` |
| Values | `bfgs`, `cg`, `l-bfgs-b`, `newton-cg` |
| Used by | SciPy backend |

Selects the SciPy optimizer when `lib=scipy`.

### `maxit`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `30` |
| Used by | optimization iterations |

Maximum number of geometry steps.

### `istate`, `jstate`, `kstate`

| Field | Value |
| --- | --- |
| Type | integer |
| Defaults | `1`, `2`, `3` |
| Used by | state-specific and crossing searches |

Target state indices. HF/DFT ground-state optimization uses `istate=0`.
TDHF/MRSF state-specific workflows use positive state indices. MECI uses
`istate` and `jstate`; TCI uses all three and requires `istate < jstate <
kstate`.

### `imult`, `jmult`

| Field | Value |
| --- | --- |
| Type | integer |
| Defaults | `1`, `3` |
| Used by | MECP multiplicities |

Multiplicity labels for MECP-style crossing searches. MECP requires different
values.

### `energy_shift`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `1.0e-6` |
| Used by | optimization convergence |

Energy-change convergence threshold.

### `energy_gap`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `1.0e-5` |
| Used by | crossing-point convergence |

Target energy-gap threshold for crossing searches.

### `meci_search`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `penalty` |
| Values | `penalty`, `ubp`, `hybrid` |
| Used by | MECI search algorithm |

Selects the MECI search strategy.

### `pen_sigma`, `pen_alpha`, `pen_incre`

| Field | Value |
| --- | --- |
| Type | float |
| Defaults | `1.0`, `0.0`, `1.0` |
| Used by | penalty-function crossing searches |

Penalty-function parameters for MECI and related crossing workflows.

### `gap_weight`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `1.0` |
| Used by | crossing-search objective |

Weight applied to the energy-gap term.

### `rmsd_grad`, `max_grad`

| Field | Value |
| --- | --- |
| Type | float |
| Defaults | `1.0e-4`, `3.0e-4` |
| Used by | gradient convergence |

RMS and maximum gradient convergence thresholds.

### `rmsd_step`, `max_step`

| Field | Value |
| --- | --- |
| Type | float |
| Defaults | `1.0e-3`, `2.0e-3` |
| Used by | step convergence |

RMS and maximum geometry-step convergence thresholds.

### `step_size`, `step_tol`

| Field | Value |
| --- | --- |
| Type | float |
| Defaults | `0.1`, `1.0e-2` |
| Used by | SciPy/lightweight optimization paths |

Step-size controls used by legacy optimization paths.

These are SciPy-backend compatibility keys for traditional `.inp` files and
the Python API. They are not accepted in concise `.oqp` geometry drivers.

### `mep_maxit`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `10` |
| Used by | MEP workflow |

Maximum number of MEP iterations.

This is a legacy SciPy MEP key and is not accepted in concise `.oqp`. Use
`mep(points=N,step=...)`; `points` lowers to the native `maxit` limit and
`step` lowers to [`[oqp] mep_step`](oqp.md#mep_step).

### `init_scf`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | geometry-step SCF handling |

Requests initial SCF cycles during geometry steps.
