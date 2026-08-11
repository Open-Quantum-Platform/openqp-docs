# `[symmetry]`

The `[symmetry]` section controls point-group metadata and optional experimental
symmetry reductions. Labeling can be useful even when integral or response
reductions are disabled.

## Keywords

### `enabled`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `false` |
| Values | `false`, `true`, `auto` |
| Used by | symmetry detection |

Controls symmetry detection. Use `auto` or `true` when symmetry metadata is
desired.

### `point_group`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `auto` |
| Used by | requested point group |

Requested point group, or `auto` for automatic detection.

### `subgroup`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `auto` |
| Used by | Abelian subgroup selection |

Requested Abelian subgroup, or `auto` for automatic choice.

### `label_mo`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `True` |
| Used by | MO labeling |

Labels molecular orbitals by symmetry where possible.

### `label_states`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `True` |
| Used by | response-state labeling |

Labels excited states by symmetry where possible.

### `label_modes`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `True` |
| Used by | vibrational-mode labeling |

Labels vibrational modes by symmetry where possible.

### `use_integral_symmetry`

| Field | Value |
| --- | --- |
| Type | string/boolean-like |
| Default | `False` |
| Used by | integral symmetry reduction |

Enables petite-list/skeleton-Fock style reductions. The checker marks this as
experimental and recommends validating against a C1 reference run.

Accepted values are `false`, `true` and `full`. `true` selects the Abelian
subgroup; `full` requests the complete point group.

#### What the reduction covers

Enabling this keyword reduces two separate parts of the calculation:

* **The two-electron integral list.** Symmetry-equivalent shell quartets are
  computed once and reweighted, and the resulting skeleton Fock matrix is
  projected back.
* **The exchange–correlation quadrature.** Grid slices belonging to
  symmetry-equivalent atoms are computed for one representative atom per orbit
  and scaled by the size of that orbit; the images are skipped.

The XC reduction engages only when the molecule actually has an orbit to
exploit — that is, when at least one atom is a symmetry image of another. For a
C1 molecule, or a geometry in which every atom sits on a special position, every
atom is its own orbit, so nothing is skipped and the reduction reports itself
inactive rather than doing identity work.

The XC reduction is **not compatible with the cross-iteration Φ cache**. When it
engages, `[scf] xc_phi_cache` is disabled automatically for that run: a cached
grid block built under the reduction would otherwise be replayed unreduced and
give a silently wrong `E_xc`.

#### Geometry and run types

Enabling the reduction **reorients the molecule** into the symmetry standard
orientation, and all outputs — geometry, gradients, orbitals — are reported in
that frame.

The reduction is applied only to `runtype = energy` and `runtype = grad`. Other
run types (optimisation, numerical Hessian, NEB, MEP, properties) are excluded,
because they either displace the geometry themselves or consume an externally
supplied one, and a per-step frame change would be assembled inconsistently.

#### `full` with a functional

`use_integral_symmetry = full` is declined for any run that sets `[input]
functional`, and the exact Abelian tier is used instead. The two halves of the
Fock matrix would otherwise reduce over different groups: Lebedev angular grids
are invariant under the axis-aligned octahedral operations but not under C3 or
C6, so the XC half can only ever be Abelian-symmetric while the JK half would be
forced symmetric under the full group. The mismatch is a measured error rather
than a rounding difference. The log states when this fallback happens; it is not
silent.

Hartree–Fock runs are unaffected and may use `full`.

### `use_response_symmetry`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | response solver symmetry reduction |

Enables irrep-blocked response updates. The checker marks this as experimental
and recommends validating excitation energies against an unblocked run.

### `tolerance`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `1.0e-5` |
| Used by | symmetry detection |

Geometry tolerance for symmetry detection. Must be positive.

### `strict`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | requested/detected group matching |

Requires stricter agreement between requested and detected symmetry labels.
