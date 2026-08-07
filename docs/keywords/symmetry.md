# `[symmetry]`

The `[symmetry]` section controls point-group metadata and optional experimental
symmetry reductions. Labeling can be useful even when integral or response
reductions are disabled.

!!! note "Detection is on by default"

    `enabled` defaults to `true`. Detection and labeling are active unless you
    turn them off. The two *reduction* keywords —
    [`use_integral_symmetry`](#use_integral_symmetry) and
    [`use_response_symmetry`](#use_response_symmetry) — remain `False` by
    default, so the geometry is not reoriented, the full integral list is still
    used, and ground-state energies are unchanged.

    Detection is **not** purely cosmetic, though. The detected irreps are what
    let the excited-state solver reach every symmetry block, so excited-state
    results can differ from a run with detection off — and where they do, the
    difference is a correction. See
    [Molecular symmetry](../workflows/symmetry.md).

## Keywords

### `enabled`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `true` |
| Values | `false`, `true`, `auto` |
| Used by | symmetry detection |

Controls symmetry detection. When on, OpenQP detects the point group and its
Abelian subgroup, labels orbitals, states and normal modes, and makes the
per-pair irrep table available to the excited-state solver.

What it does **not** do: it does not reorient the molecule and does not reduce
the integral list. Those follow `use_integral_symmetry` only.

Set `enabled=false` to restore the pre-detection behavior — no labels, no irrep
table, and the excited-state trial vectors chosen purely by orbital-energy gap
(see [Molecular symmetry](../workflows/symmetry.md) for why that can matter).

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

Prints the molecular-orbital symmetry table. This is a **display** control
only: setting it to `False` suppresses the printed table but does not disable
the orbital irreps themselves, which the excited-state solver needs regardless.

### `label_states`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `True` |
| Used by | response-state labeling |

Labels excited states by symmetry where possible. When `[tdhf] multiplicity` is
set, the labels are reported as spin-resolved terms (`1A1`, `3B2`, ...) rather
than bare irreps.

### `label_modes`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `True` |
| Used by | vibrational-mode labeling |

Labels vibrational modes by symmetry where possible. The labels appear as a
`Symmetry` column in the printed frequency table:

```
   Mode  Symmetry     Frequency(cm-1)      IR(km/mol)        Raman(activity)
      1        a1           2043.11         0.492662           104.268372
      2        a1           4488.55         1.622292           558.762685
      3        b2           4790.80         0.866146           220.085777
```

The column is present whenever mode labels could be assigned, including for a
Hessian restored with `[hess] read=true`.

### `use_integral_symmetry`

| Field | Value |
| --- | --- |
| Type | string/boolean-like |
| Default | `False` |
| Used by | integral symmetry reduction |

Enables petite-list/skeleton-Fock style reductions. The checker marks this as
experimental and recommends validating against a C1 reference run.

**This is the keyword that reorients the molecule** into the symmetry standard
orientation. Turning symmetry detection on does not.

Accepts `true` for the Abelian subgroup (machine-exact) or `full` for the
complete point group (a larger reduction, accurate to roughly 1e-7).

!!! warning "`full` is declined for DFT"

    The `full` tier reduces the two-electron integrals over the complete point
    group, while the exchange-correlation grid necessarily stays on the Abelian
    operations — Lebedev angular grids are not invariant under C3/C6 rotations.
    The two halves would then reduce over different groups, which is a measured
    error of about 3e-04 Hartree.

    When a functional is set, OpenQP therefore falls back to the exact Abelian
    tier and says so in the symmetry log block. You still get the reduction,
    just the tier that is exact. Remove the `[input] functional` if you need
    the full group — OpenQP selects DFT with `method=hf` *plus* a functional,
    so `method=hf` alone is not what distinguishes the two.

The fallback is never silent: if the reduction is requested but does not engage
for any reason, the log states that the run used the full (C1) integral list.

### `use_response_symmetry`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | response solver symmetry reduction |

Enables irrep-blocked response updates — the experimental projection that
confines Davidson residuals to a single irrep. The checker marks this as
experimental and recommends validating excitation energies against an unblocked
run.

This is **separate** from the symmetry-block coverage of the initial trial
vectors, which is not experimental and follows detection alone. The symmetry log
block distinguishes the two:

| `response blocking` | Meaning |
| --- | --- |
| `pair_table_staged` | Irrep table built for trial-vector coverage; the residual projection is **off** |
| `active` | The experimental residual projection is running |

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
