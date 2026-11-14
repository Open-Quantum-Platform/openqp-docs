# `[dftgrid]`

The `[dftgrid]` section controls DFT quadrature and optional overrides for
hybrid or range-separated functional parameters. Most users should leave these
defaults unchanged unless reproducing a benchmark or testing a functional.

## Keywords

### `hfscale`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `-1.0` |
| Used by | exact-exchange scale override |

Overrides the Hartree-Fock exchange fraction. Negative values mean that OpenQP
uses the value associated with the selected functional.

### `cam_flag`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | range-separated functional setup |

Enables explicit CAM/range-separated parameter handling.

### `cam_alpha`, `cam_beta`, `cam_mu`

| Field | Value |
| --- | --- |
| Type | float |
| Defaults | `-1.0`, `-1.0`, `-1.0` |
| Used by | CAM/range-separated functional setup |

Override the CAM alpha, beta, and mu parameters. Negative values mean that
OpenQP uses the selected functional default.

### `rad_type`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `ta` |
| Used by | radial quadrature |

Selects the radial grid family.

### `rad_npts`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `96` |
| Used by | radial quadrature |

Sets the number of radial points. With the default `pruned=auto`, a value
other than `96` selects the unpruned `rad_npts` × `ang_npts` grid; see
[`pruned`](#pruned).

### `ang_npts`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `302` |
| Used by | angular quadrature |

Sets the number of angular grid points. With the default `pruned=auto`, a
value other than `302` selects the unpruned `rad_npts` × `ang_npts` grid; see
[`pruned`](#pruned).

### `partfun`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `ssf` |
| Used by | molecular grid partitioning |

Selects the partition function used to assign atomic grid weights.

### `pruned`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `auto` |
| Used by | pruned DFT grids |

Selects the atomic quadrature grid. Accepted values:

| Value | Grid |
| --- | --- |
| `auto` (default) | `AG3` while `rad_npts` and `ang_npts` keep their defaults (`96` and `302`); the unpruned `rad_npts` × `ang_npts` grid as soon as either is changed. |
| `SG0`, `SG1`, `SG2`, `SG3` | The named pruned preset. |
| `AG1`, `AG2`, `AG3`, `AG4` | Choose the radial and angular quadrature from the molecular XC integrand. |
| `none` | The unpruned `rad_npts` × `ang_npts` grid at every radius. `off`, `false`, `no` and an empty value (`pruned=` in `.inp` input) mean the same. |

A pruned preset defines its own radial and angular grids, so `rad_npts` and
`ang_npts` are not used for the atoms the preset covers. With the default,
setting the grid size is therefore enough to obtain that grid:

```text
rks/bhhlyp/6-31g* dftgrid(rad_npts=128,ang_npts=590)
```

runs the unpruned 128 × 590 grid, and an input without grid keywords runs
`AG3` for both GGA and meta-GGA functionals. An explicit preset together with a non-default `rad_npts` or
`ang_npts` runs the preset; for a DFT input the input checker then issues a warning that names
the values that are not used. An unknown `pruned` value is an input error.
The resolved value (`AG3`, another preset, or `none`) is written back into the
configuration, so the printed and saved configuration state the grid that was
used.

To reproduce an earlier calculation, use the grid recorded in its log,
for example `dftgrid(pruned=SG2)` or `dftgrid(pruned=SG3)`. To request an
unpruned grid with the schema point counts, use `pruned=none`.

#### Adaptive grids

AG3 is the automatic choice. Use `dftgrid(pruned=AG1)`,
`dftgrid(pruned=AG2)`, or `dftgrid(pruned=AG4)` to request a different budget.
The estimated XC integration budgets per atom are:

| Preset | Budget (Eh per atom) |
|---|---:|
| `AG1` | 1 × 10⁻⁵ |
| `AG2` | 3 × 10⁻⁶ |
| `AG3` | 1 × 10⁻⁶ |
| `AG4` | 3 × 10⁻⁷ |

The SCF starts on a coarse grid. It uses the SCF density to estimate an
adaptive allocation before converging on the resulting grid. Subsequent
response and gradient calculations reuse the allocation. During a geometry
sequence, moving an atom more than 0.2 Å from the allocation geometry
triggers a new allocation. A grid change can introduce a small discontinuity
in the energy and gradient. Numerical Hessian calculations reuse the
reference geometry’s radial and angular orders for all displacements,
while rebuilding the point positions and weights at each displaced geometry.
The output reports the estimated radial and angular XC integration errors,
the number of grid points, and the number of points evaluated during
estimation. The budgets are estimates for XC quadrature. Other observables,
including nuclear gradients and excitation energies, require their own
grid convergence checks.

### `grid_ao_pruned`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `True` |
| Used by | AO grid pruning |

Enables AO screening on grid points.

### `grid_ao_threshold`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `1.0e-15` |
| Used by | AO grid pruning |

AO values below this threshold can be treated as negligible during grid pruning.

### `grid_ao_sparsity_ratio`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.9` |
| Used by | AO grid pruning |

Controls the sparsity threshold used by AO grid pruning.
