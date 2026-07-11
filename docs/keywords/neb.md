# `[neb]`

The `[neb]` section defines the product endpoint and image count for nudged
elastic band calculations. Use it with `[input] runtype=neb`.

## Keywords

### `product`

| Field | Value |
| --- | --- |
| Type | string |
| Default | empty |
| Used by | NEB product endpoint |

Path to the product endpoint XYZ file. The reactant geometry comes from
`[input] system`; the product geometry comes from `product`.

Example:

```ini
[neb]
product=HCN_RHF-DFT_NEB_OQP_product.xyz
nimage=7
```

### `nimage`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `5` |
| Used by | NEB image count |

Number of NEB images. The input checker requires at least `3`.

The remaining `[neb]` keys belong to the geomeTRIC backend. Native OQP NEB
controls such as `spring`, boolean `climb`, and `fmax` live in [`[oqp]`](oqp.md).

### `k`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `1.0` |
| Used by | geomeTRIC NEB spring strength |

### `maxg`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.1` |
| Used by | geomeTRIC maximum-gradient convergence |

### `avgg`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.05` |
| Used by | geomeTRIC average-gradient convergence |

### `climb`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.5` |
| Used by | geomeTRIC climbing-image threshold |

This is distinct from the boolean [`[oqp] climb`](oqp.md#climb) used by native
NEB. The one-line driver routes `climb` according to `lib`.

### `align`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `True` |
| Used by | geomeTRIC image alignment |

### `optep`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | geomeTRIC endpoint optimization |

In `.oqp`, use `lib=geometric` with these six controls. Mixing them with native
`[oqp]` NEB controls is rejected.
