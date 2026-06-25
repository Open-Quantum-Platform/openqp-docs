# `[oqp]`

The `[oqp]` section controls the native OpenQP optimizer selected with
`[optimize] lib=oqp`.

## Keywords

### `coordsys`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `tric` |
| Used by | native optimizer coordinates |

Coordinate system for the native optimizer. Examples use `tric` and `auto`.

### `trust`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.2` |
| Used by | optimizer trust radius |

Initial trust radius.

### `trust_max`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.5` |
| Used by | optimizer trust radius |

Maximum trust radius.

### `follow`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `0` |
| Used by | mode following |

Mode-following selector for transition-state style steps.

### `spring`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.05` |
| Used by | NEB |

NEB spring constant.

### `climb`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `True` |
| Used by | NEB |

Enables climbing-image NEB behavior.

### `fmax`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `2.0e-3` |
| Used by | NEB convergence |

NEB force threshold.

### `climb_fmax`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.05` |
| Used by | climbing-image NEB |

Force threshold for the climbing image.

### `neb_dt`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.5` |
| Used by | NEB propagation |

NEB integration step.

### `maxmove`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.2` |
| Used by | NEB image updates |

Maximum NEB image displacement per step.

### `opt_ends`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `True` |
| Used by | NEB endpoints |

Optimizes NEB endpoints when true.

### `end_fmax`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `1.0e-3` |
| Used by | NEB endpoint convergence |

Endpoint force threshold.

### `irc_step`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.1` |
| Used by | IRC |

IRC step size.

### `irc_direction`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `forward` |
| Used by | IRC |

IRC direction.

### `mep_step`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.1` |
| Used by | MEP |

MEP step size.
