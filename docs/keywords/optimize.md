# `[optimize]`

The `[optimize]` section selects the optimization backend, target states, and
convergence thresholds for geometry and reaction-path workflows.

In Python scripts, use `job.control(...)` for the optimization runtype, common
optimization options, and backend options. For example,
`job.control(runtype="optimize", lib="oqp", coordsys="tric")` routes
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

Selects the optimizer backend. The native `oqp` backend supports `optimize`,
`ts`, `meci`, `mecp`, `tci`, `neb`, `irc`, and `mep`. geomeTRIC supports
`optimize`, `meci`, `mecp`, `ts`, `irc`, and `neb`. SciPy is a legacy backend
for `optimize`, `meci`, `mecp`, and `mep`.

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

### `mep_maxit`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `10` |
| Used by | MEP workflow |

Maximum number of MEP iterations.

### `init_scf`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | geometry-step SCF handling |

Requests initial SCF cycles during geometry steps.
