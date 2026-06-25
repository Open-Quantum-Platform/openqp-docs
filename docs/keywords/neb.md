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
