# `[properties]`

The `[properties]` section requests properties and selects state indices for
gradient-like workflows.

## Keywords

### `scf_prop`

| Field | Value |
| --- | --- |
| Type | comma-separated string list |
| Default | `el_mom,mulliken` |
| Values | `el_mom`, `mulliken`, `nmr` |
| Used by | SCF property driver |

Requests SCF properties. Add `nmr` for nuclear magnetic shielding:

```ini
[properties]
scf_prop=nmr
```

### `nmr_gauge`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `cgo` |
| Values | `cgo`, `giao` |
| Used by | NMR shielding |

Selects the NMR gauge formulation. `cgo` is the common-gauge-origin formulation
and is limited to closed-shell RHF in the input checker. Use `giao` for
open-shell UHF/ROHF NMR shielding where supported.

### `td_prop`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | response-state property placeholder |

Requests TD properties. The current input checker warns that this is not part of
the documented production surface.

### `grad`

| Field | Value |
| --- | --- |
| Type | integer list |
| Default | `0` |
| Used by | `runtype=grad` and state-specific gradients |

Selects gradient states. HF/DFT gradients use state `0`. Ordinary TDHF/TDDFT
state `1` is the first excited state. SF-TDDFT and MRSF-TDDFT state `1` is the
lowest spin-flip/MRSF target state, which can be the multiconfigurational ground
state. In Python, prefer `job.workflow.gradient(state=...)`; it maps to this
input-file keyword.

Example:

```ini
[input]
runtype=grad
method=tdhf

[properties]
grad=3
```

### `nac`

| Field | Value |
| --- | --- |
| Type | string |
| Default | empty |
| Used by | legacy NAC/property requests |

Legacy property-level NAC request. The current NAC and NACME workflows should
prefer the `[nac] states` keyword.

### `export`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | data export |

Requests export of selected computed data where supported.

### `title`

| Field | Value |
| --- | --- |
| Type | string |
| Default | empty |
| Used by | output labeling |

Optional output title.

### `back_door`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | developer/debug paths |

Developer/debug option. Leave false for production calculations.
