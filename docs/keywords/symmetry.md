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
