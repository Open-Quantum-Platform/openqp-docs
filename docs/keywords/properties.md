# `[properties]`

The `[properties]` section requests properties and selects state indices for
gradient-like workflows.

## Keywords

### `scf_prop`

| Field | Value |
| --- | --- |
| Type | comma-separated string list |
| Default | empty (no SCF properties) |
| Values | `el_mom`, `mulliken`, `lowdin`, `resp`, `nmr`, `acid` |
| Used by | SCF property driver |

Requests SCF properties. Properties are **opt-in**: a property is computed only
when listed here, and only requested properties are written to the JSON
reference and regression-tested. Available analyses:

- `el_mom` — electric dipole (and moments); the dipole (a.u.) is exposed as
  `dipole` in `get_results()`.
- `mulliken` / `lowdin` — Mulliken / Löwdin atomic partial charges, exposed as
  `mulliken_charges` / `lowdin_charges`.
- `resp` — RESP/ESP-fitted atomic charges, exposed as `resp_charges`.
- `nmr` — isotropic NMR shielding (`nmr_shielding`).
- `acid` — ACID and induced-current-density cubes. Built from the GIAO
  magnetic density response, so it requires `nmr` as well and
  `nmr_gauge=giao`, and must be listed after `nmr`. See
  [ACID Current-Density Maps](../workflows/acid.md).

```ini
[properties]
scf_prop=el_mom,mulliken,lowdin,resp
```

!!! note "Behavior change"
    `scf_prop` previously defaulted to `el_mom,mulliken`. It now defaults to
    empty so population/moment analysis runs only on request and properties are
    not added to every reference. Request them explicitly to restore the old
    output.

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

### `acid_spacing`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.2` |
| Units | bohr |
| Used by | `scf_prop=acid` |

Grid spacing of the ACID and current-density cubes. Must be finite and
positive. The cube size grows as the cube of the inverse spacing, so coarsen
this for a quick look at a large molecule.

### `acid_padding`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `5.0` |
| Units | bohr |
| Used by | `scf_prop=acid` |

Padding added around the molecular bounding box for the ACID cube grid. Must be
finite and non-negative.

```ini
[properties]
scf_prop=nmr,acid
nmr_gauge=giao
acid_spacing=0.5
acid_padding=3.0
```

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
state. UMRSF-TDDFT numbers its roots the same way, within the response manifold
selected by `[tdhf] multiplicity`: with `multiplicity=1`, state `1` is S0 and
state `2` is S1; with `multiplicity=3`, state `1` is the lowest triplet response
root. In Python, prefer `job.workflow.gradient(state=...)`; it maps to this
input-file keyword.

Example:

```ini
[input]
runtype=grad
method=tdhf

[properties]
grad=3
```

### `grad_s` / `grad_t`

| Field | Value |
| --- | --- |
| Type | integer list |
| Default | empty |
| Used by | `runtype=grad`, `prop`, `data` with MRSF or UMRSF response |

Gradient states of one spin ladder each: `grad_s` names singlet response roots
and `grad_t` triplet ones, numbered like `grad` for MRSF (root `1` is S0 or T0,
root `2` is S1 or T1). Naming the ladder that `[tdhf] multiplicity` does not
select makes the run solve that second ladder from the same reference and
publish both. A run that solves both ladders converges `[tdhf] nstate_s` /
`nstate_t` roots on each (falling back to `nstate`); a run that solves one
ladder keeps `nstate`.

Without `soc`, `grad` keeps describing the configured ladder when that ladder's
own selector is empty, so `grad=2` with `grad_t=1` asks for S1 and T0. Its
default `0` (the internal reference, not a state) is not carried over, so
`grad_t=1` alone asks for T0 only and the configured ladder publishes energies
only. With `soc=true`, `grad` is not read and must stay at its default; only
`grad_s` and `grad_t` select gradients, and a ladder with an empty selector
gets none.

The input checker refuses these keys with any other runtype (they would be
dropped), outside `method=tdhf` with `[tdhf] type=mrsf` or `umrsf` (the second
ladder is reached by switching `[tdhf] multiplicity`, which the DFTB/xTB
backends do not read), with roots below `1` or entries that are not integers,
with a root above its ladder's state count, and with `runtype=soc`, which
computes no gradients.

```ini
[input]
runtype=grad
method=tdhf

[tdhf]
type=mrsf
nstate=3

[properties]
grad_s=2
grad_t=1
```

### `soc`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | `runtype=prop`, `runtype=data` |

Adds the MRSF spin-orbit coupling step to a properties or data run: the run
solves both the singlet and the triplet ladder, publishes the energies and the
requested gradients of each, and couples them. It has the same requirements as
the standalone [`runtype=soc`](../workflows/soc.md) (`method=tdhf`,
`[tdhf] type=mrsf`, a triplet ROHF reference, `[tdhf] multiplicity` 1 or 3,
`[tdhf] ixcore` unset, and `ispher=false` or `soc_2e=0` for the two-electron
term). `runtype=soc` stays the standalone entry point and `[md] soc` the one
inside surface hopping.

With `soc=true`:

- gradients are selected by `grad_s` / `grad_t`, never by `grad`;
- `nac=nacme` (only with `runtype=prop`) publishes one coupling matrix per
  ladder, each against that ladder's own previous step; `nac=nac` is refused,
  and so is `nac=nacme` with `runtype=data`, which has no previous-step overlap;
- DFTB/xTB are refused; use `runtype=soc` for tight-binding spin-orbit
  coupling.

```ini
[input]
runtype=prop
method=tdhf
functional=bhhlyp
basis=6-31G*
ispher=false

[scf]
type=rohf
multiplicity=3

[tdhf]
type=mrsf
nstate=2

[properties]
soc=true
nac=nacme
export=true
grad_s=2
grad_t=2
```

Runnable example:
[`examples/SOC/H2O_BHHLYP_MRSF_PROP_SOC.inp`](https://github.com/Open-Quantum-Platform/openqp/blob/main/examples/SOC/H2O_BHHLYP_MRSF_PROP_SOC.inp)
and its `.oqp` companion, where `prop(S1)` lowers to `grad_s=2` and the
triplet ladder is named with `properties(soc=true, grad_t=2)`. `prop()` takes
one target state; the other ladder is always named through `grad_s`/`grad_t`.
In Python the keyword is reached through the schema proxies, e.g.
`job.settings.properties(soc=True, grad_t=2)` (a list is written as `"2,3"`).

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

Requests export of selected computed data where supported. Files are written
next to the log, prefixed with `title.` when [`title`](#title) is set:
`energies`, `grad_<i>`, `nacme`, `dcme`, `nac_<i>_<j>`.

A run that publishes two spin ladders (`soc=true`, or a `grad_s`/`grad_t`
request for the ladder `[tdhf] multiplicity` does not select) labels each
file with its ladder instead: `energies_s` / `energies_t`, `grad_s_<i>` /
`grad_t_<i>`, `nacme_s` / `nacme_t`, `dcme_s` / `dcme_t`. A run with one
ladder keeps the unlabelled names.

With `soc=true` the run also writes `socme`: one row per singlet, triplet and
Ms triple, in the order of the singlet-triplet table the SOC step prints in the
log (`ns * nt * 3` rows).

| Column | Meaning |
| --- | --- |
| `S_index` | singlet state, zero-based like its label (`0` is S0) |
| `T_index` | triplet state, zero-based like its label (`0` is T0) |
| `Ms` | triplet component, `-1`, `0`, `+1` |
| `Re`, `Im` | merged one- plus two-electron coupling, cm⁻¹ |
| `Absolute` | modulus of the coupling, cm⁻¹ |

`Re` and `Im` carry the arbitrary phase of each response root, which can flip
between runs; only `Absolute` is invariant.

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
