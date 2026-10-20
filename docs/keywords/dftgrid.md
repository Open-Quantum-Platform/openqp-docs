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
| `auto` (default) | `SG2` while `rad_npts` and `ang_npts` keep their defaults (`96` and `302`); the unpruned `rad_npts` × `ang_npts` grid as soon as either is changed. |
| `SG0`, `SG1`, `SG2`, `SG3` | The named pruned preset. |
| `none` | The unpruned `rad_npts` × `ang_npts` grid at every radius. `off`, `false`, `no` and an empty value (`pruned=` in `.inp` input) mean the same. |

A pruned preset defines its own radial and angular grids, so `rad_npts` and
`ang_npts` are not used for the atoms the preset covers. With the default,
setting the grid size is therefore enough to obtain that grid:

```text
rks/bhhlyp/6-31g* dftgrid(rad_npts=128,ang_npts=590)
```

runs the unpruned 128 × 590 grid, and an input without grid keywords runs
`SG2`. An explicit preset together with a non-default `rad_npts` or
`ang_npts` runs the preset; for a DFT input the input checker then issues a warning that names
the values that are not used. An unknown `pruned` value is an input error.
The resolved value (`SG2`, another preset, or `none`) is written back into the
configuration, so the printed and saved configuration state the grid that was
used.

Before this default was introduced, `pruned` defaulted to `SG2`, and an input
that set only `rad_npts` and `ang_npts` ran on the `SG2` grid. To reproduce
such a result, add `pruned=SG2`. Some regression examples set `pruned=none`
so that their reference numbers do not depend on a pruning scheme.

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

## Fractional-derivative ingredient ξ^α (experimental)

These keywords replace the kinetic-energy density τ of a meta-GGA functional
by the fractional-derivative ingredient ξ^α of Leonov, Gerasimov *et al.*
(WIREs Comput. Mol. Sci. Perspective, 2026):
ξ^α = ½ Σ_k f_k |D^α φ_k|², where D^α χ is the directional Caputo derivative of
each basis function integrated along the line from its own centre. ξ^1 = τ and
ξ^0⁻ = n/2 exactly. The underlying functional is not re-parametrised, so the
energies are not those of the named functional; the feature exists to build and
test new ingredient-based functionals. It is implemented for single-point
HF/DFT energies only (no gradients, Hessians, TDDFT/response or properties).
ξ^α has no distance screening (its kernel decays algebraically), so the first
XC build evaluates every shell at every grid point; with `[scf] xc_phi_cache`
it is evaluated once per geometry.

### `xi_mode`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `0` |
| Used by | meta-GGA XC build |

`0` leaves the functional unchanged; `1` feeds ξ^α to the functional in place of τ.

### `xi_alpha`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `1.0` |
| Used by | ξ^α kernel |

Fractional order α ≤ 1. `1.0` reproduces τ exactly; `0.0` with `xi_p=0`
reproduces n/2; negative values are fractional integrals.

### `xi_p`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `-1` |
| Used by | ξ^α kernel |

Integer order of the inner derivative: `1` (vector ingredient, 0 < α ≤ 1),
`0` (scalar ingredient, α ≤ 0) or `-1` to choose automatically from α. The
two branches differ at α = 0 (ξ^0⁺ ≠ ξ^0⁻).

### `xi_scale`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `0` |
| Used by | ξ^α kernel |

`0` integrates along the path normalised to [0, 1] (the definition of the
Perspective); `1` multiplies D^α χ by |r − R|^(p−α), the Caputo derivative in
physical path length, which makes ξ^α dimensionally consistent with the
uniform-gas form n^(1+2α/3).

### `xi_cutoff`

| Field | Value |
| --- | --- |
| Type | float (bohr) |
| Default | `0.0` |
| Used by | ξ^α build |

If positive, D^α χ of a shell is set to zero at grid points farther than this
distance from the shell centre, which restores distance screening at the price
of an approximation. `0` is exact. For benzene (6-31G, ξ^0.5) 15 bohr changes
the energy by less than 1e-10 Eh and 10 bohr by about 1e-6 Eh; for separated
molecules the neglected tails can amount to mEh (see the OpenQP pull request
#469 for the measurements).
