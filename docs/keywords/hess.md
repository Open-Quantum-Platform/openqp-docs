# `[hess]`

The `[hess]` section controls Hessian, frequency, and thermochemistry
workflows.

## Keywords

### `type`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `numerical` |
| Values | `numerical`, `analytical` |
| Used by | Hessian dispatch |

Selects numerical finite-difference or native analytical Hessian dispatch.
Analytical Hessians are validated for supported HF/DFT ground-state cases. The
input checker requests `type=numerical` when the method, state, or basis is
outside the analytical path.

### `state`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `0` |
| Used by | Hessian target state |

HF/DFT Hessians use state `0`. TDHF-family Hessian workflows use positive
excited-state indices.

### `dx`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.01` |
| Used by | numerical Hessian displacement |

Finite-difference step size for numerical Hessians.

### `nproc`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `1` |
| Used by | numerical Hessian workers |

Worker count for numerical Hessian calculations. Must be at least `1`.

### `read`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | Hessian restart/input |

Reads an existing Hessian where the workflow supports it.

### `restart`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | numerical Hessian restart |

Continues an interrupted numerical Hessian workflow.

### `temperature`

| Field | Value |
| --- | --- |
| Type | float list |
| Default | `298.15` |
| Used by | thermochemistry |

Temperature or temperatures, in Kelvin, for thermochemical analysis. Values must
be positive.

### `clean`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | temporary Hessian files |

Removes temporary Hessian files where supported.
