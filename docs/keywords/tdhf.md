# `[tdhf]`

The `[tdhf]` section controls TDHF, TDDFT, spin-flip TDDFT, MRSF-TDDFT, and
UMRSF-TDDFT response calculations. Use `[input] method=tdhf` to activate these
workflows.

## Background

MRSF-TDDFT is OpenQP's main multistate response method. It starts from an
open-shell high-spin reference, builds spin-flip response spaces, and mixes the
reference density information so target states are less affected by ordinary
spin-flip spin contamination. In practice this makes the same response
machinery useful for multiconfigurational ground-state surfaces, excited-state
surfaces, conical-intersection work, gradients, NACME, SOC, and MRSF-EKT. See
[References](../references.md#mrsf-tddft) for the original theory papers and
recent overview articles.

## Minimal MRSF-TDDFT Example

```ini
[input]
method=tdhf

[scf]
type=rohf
multiplicity=3

[tdhf]
type=mrsf
nstate=5
multiplicity=1
```

The same setup in Python keeps the native section names visible:

```python
from oqp.openqp import OpenQP

job = OpenQP("mrsf_keywords")
job.molecule(geometry="water", charge=0, multiplicity=3)
job.theory("mrsf-tddft", functional="bhhlyp", basis="6-31g*", nstate=5)
job.workflow.tdhf.multiplicity = 1
```

## Keywords

### `type`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `rpa` |
| Values | `rpa`, `tda`, `sf`, `mrsf`, `umrsf`, `mrsf_ekt_ip`, `mrsf_ekt_ea` |
| Used by | response model selection |

Selects the response model. Use `mrsf` for production MRSF-TDDFT workflows.
`sf` selects ordinary spin-flip TDDFT, and `umrsf` selects the unrestricted
MRSF energy path. The legacy `mrsf_ekt_ip` and `mrsf_ekt_ea` values are
energy-only; the current EKT workflow should use `[input] runtype=ekt`,
`[tdhf] type=mrsf`, and the `[ekt]` section.

MRSF and SF workflows require an ROHF reference in the current code path.
UMRSF-TDDFT requires a UHF reference.

### `nstate`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `1` |
| Used by | number of response roots |

Number of excited states to compute. It must be at least as large as the highest
state requested by gradients, optimizations, NACME, SOC, Hessians, or EKT.

### `target`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `1` |
| Used by | target-state workflows |

Target response state for workflows that read a single TDHF/MRSF state.

### `multiplicity`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `1` |
| Used by | response-state spin selection |

Requested response-state multiplicity. For MRSF-TDDFT, this is the target spin
multiplicity after spin flip, not necessarily the same as the high-spin ROHF
reference multiplicity.

### `maxit`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `50` |
| Used by | Davidson/response solver |

Maximum number of response-solver iterations.

### `conv`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `1.0e-6` |
| Used by | response convergence |

Convergence threshold for the response solver.

### `nvdav`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `50` |
| Used by | Davidson subspace |

Maximum Davidson subspace dimension. The input checker warns when `nvdav` is
smaller than `nstate`.

### `maxit_zv`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `50` |
| Used by | Z-vector solver |

Maximum number of Z-vector iterations for gradient/property workflows.

### `zvconv`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `1.0e-6` |
| Used by | Z-vector convergence |

Convergence threshold for Z-vector equations.

### `z_solver`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `0` |
| Values | `0`, `1`, `2`, `3` |
| Used by | Z-vector linear solver |

Selects the Z-vector solver. In the source comments, `0` is CG, `1` is legacy
GMRES, `2` is MINRES, and `3` is AUTO.

### `gmres_dim`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `50` |
| Used by | GMRES Z-vector solver |

Subspace dimension for GMRES when that solver is selected.

### `tlf`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `2` |
| Used by | response-model internals |

Response-model selector used by the native TDHF/MRSF implementation.

### `hfscale`, `cam_alpha`, `cam_beta`, `cam_mu`

| Field | Value |
| --- | --- |
| Type | float |
| Defaults | `-1.0`, `-1.0`, `-1.0`, `-1.0` |
| Used by | response functional parameter overrides |

Override exact-exchange and CAM/range-separated parameters for response
calculations. Negative values mean use the selected functional defaults.

### `spc_coco`, `spc_ovov`, `spc_coov`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `-1.0` |
| Used by | spin-purification correction parameters |

Advanced MRSF/SF response parameters. Leave negative unless following a specific
validated protocol.

### `conf_threshold`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `5.0e-2` |
| Used by | configuration analysis/output |

Threshold for reporting or using response configurations.

### `ixcore`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `-1` |
| Used by | core-level response workflows |

Core-orbital selector for core-level response calculations such as X-ray
absorption workflows.
