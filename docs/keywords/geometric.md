# `[geometric]`

The `[geometric]` section controls the external geomeTRIC optimizer backend
selected with `[optimize] lib=geometric`.

## Keywords

### `coordsys`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `tric` |
| Used by | geomeTRIC coordinate system |

Coordinate system passed to geomeTRIC.

### `trust`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.1` |
| Used by | geomeTRIC trust radius |

Initial trust radius.

### `tmax`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.3` |
| Used by | geomeTRIC trust radius |

Maximum trust radius.

### `convergence_set`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `GAU` |
| Used by | geomeTRIC convergence preset |

Convergence preset passed to geomeTRIC.

### `prefix`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `geometric` |
| Used by | geomeTRIC artifact names |

File prefix for geomeTRIC output artifacts.

### `hessian`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `never` |
| Used by | geomeTRIC Hessian option |

Hessian option passed to geomeTRIC.

### `irc_direction`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `forward` |
| Used by | IRC |

IRC direction for geomeTRIC-driven IRC workflows.

### `constraints_file`

| Field | Value |
| --- | --- |
| Type | string |
| Default | empty |
| Used by | constrained optimization |

Path to a geomeTRIC constraints file.

### `enforce`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.0` |
| Used by | constrained optimization |

Constraint enforcement strength.

### `conmethod`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `0` |
| Used by | constrained optimization |

Constraint method selector.
