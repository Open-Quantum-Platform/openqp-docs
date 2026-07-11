# `[xtb]`

The `[xtb]` section configures the optional OpenQP-xTB backend, an LC-GFN1-xTB
tight-binding engine that plugs into the ordinary OpenQP workflow with
`[input] method=xtb`. It shares the tight-binding dispatch and the response
plumbing with the `[dftb]` backend, so ground-state, TDDFTB, SF, and MRSF
responses (and the SOC/NACME/NAMD workflows built on MRSF) run through the same
drivers; only the section name, the shared library, and a few GFN1 model
options differ.

## Background

xTB is a semiempirical tight-binding model. The OpenQP-xTB backend implements
the long-range-corrected GFN1 Hamiltonian (LC-GFN1) together with the
spin-flip/MRSF response used elsewhere in OpenQP, so an MRSF calculation can be
run on a GFN1 reference at a fraction of the cost of an all-electron MRSF-TDDFT
job. The backend is an external library (`libopenqp_xtb_c`); when it is not
installed, `method=xtb` inputs are parsed and validated but cannot execute.

Parameters are read from a converter-generated `.opxtb` file supplied through
`parameter_path`. Model options default to the full LC-GFN1 Hamiltonian
(`model=gfn1`, dispersion/halogen-bond/third-order terms on, `spin_scale=1.0`,
`lc_gamma=ok` with `omega=0.3`).

## Minimal Example

```ini
[input]
method=xtb
runtype=energy
basis=sto-3g
functional=

[scf]
type=rohf
multiplicity=3

[tdhf]
type=mrsf
nstate=3

[xtb]
backend=native
type=mrsf
parameter_path=gfn1.opxtb
lc_ground_state=true
```

Python style:

```python
from oqp.openqp import OpenQP

job = OpenQP("xtb_keywords")
job.molecule(geometry="water", charge=0, multiplicity=3)
job.xtb(
    response_type="mrsf",
    nstate=3,
    parameter_path="gfn1.opxtb",
    lc_ground_state=True,
)
```

`job.theory("xtb", ...)` selects the ground state by default; `job.xtb(...)`
and `job.theory.xtb(...)` default to the MRSF response. SOC and NAMD follow the
MRSF path with `job.workflow.soc(...)` / `job.workflow.namd(...)`, exactly as
for MRSF-TDDFT(B).

## Keywords

### `backend`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `native` |
| Values | `native` |
| Used by | xTB backend selection |

Selects the backend driver. Only the `native` in-process library is supported;
the DFTB-only `probe` executable is rejected for `[xtb]` because it cannot
publish the MO/response-vector tags the OpenQP drivers consume.

### `type`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `auto` |
| Values | `auto`, `ground`, `tddftb`, `sf`, `mrsf` |
| Used by | response method selection |

Response method the backend evaluates. `auto` derives the response from
`[tdhf] type`; set it explicitly to force a ground-state (`ground`), TDDFTB
(`tddftb`), spin-flip (`sf`), or MRSF (`mrsf`) run. The compact Python helper
canonicalizes the `tda`/`td-dftb` aliases onto `tddftb`.

### `parameter_path`

| Field | Value |
| --- | --- |
| Type | string |
| Default | *(empty)* |
| Used by | GFN1 parameter loading |

Path to the converter-generated `.opxtb` parameter file. May also be supplied
through the `OPENQP_XTB_PARAMETER_PATH` environment variable.

### `library_path`

| Field | Value |
| --- | --- |
| Type | string |
| Default | *(empty)* |
| Used by | shared-library resolution |

Optional explicit path to `libopenqp_xtb_c`. When empty, the backend resolves
the library from the installed `openqp_xtb` package or the
`OPENQP_XTB_LIBRARY` environment variable.

### `model`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `gfn1` |
| Values | `gfn1` |
| Used by | Hamiltonian model |

Selects the GFN model. Only `gfn1` is implemented; other spellings (e.g.
`gfn2`) are rejected by the input checker.

### `dispersion`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `True` |
| Used by | GFN1 dispersion term |

Enables the GFN1 dispersion correction.

### `halogen_bond`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `True` |
| Used by | GFN1 halogen-bond term |

Enables the GFN1 halogen-bond correction.

### `third_order`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `True` |
| Used by | GFN1 third-order SCC term |

Enables the third-order (charge-derivative) SCC contribution.

### `spin_scale`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `1.0` |
| Used by | spin-polarization scaling |

Scales the spin-polarization contribution. Must be greater than `0`.

### `lc_gamma`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `ok` |
| Values | `ok`, `yukawa`, `erf` |
| Used by | long-range-correction kernel |

Range-separation kernel for the long-range exchange. `ok` (the xTB default) is
accepted only for `[xtb]`; `yukawa` and `erf` are shared with `[dftb]`.

### `omega`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.3` |
| Used by | range-separation parameter |

Range-separation parameter for the LC kernel.

### `cam_alpha`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.0` |
| Used by | CAM short-range fraction |

Short-range exact-exchange fraction of the CAM-style partition.

### `cam_beta`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `1.0` |
| Used by | CAM long-range fraction |

Long-range exact-exchange fraction of the CAM-style partition.

### `lc_ground_state`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | ground-state SCC kernel |

Opt-in flag that applies the long-range-corrected GFN1 kernel to the
ground-state SCC as well, not only to the response. `true` selects the full
production LC-GFN1 reference the MRSF response is built on. Requires
`backend=native` (the DFTB `probe` executable cannot forward it).

### `zvector`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `True` |
| Used by | analytic excited-state gradient |

Uses the Z-vector path for the analytic state gradient. Requires
`backend=native`.

## SCC and Response Controls

The SCC solver and the excited-state response reader accept the same tuning
keys as `[dftb]`: `scc_tolerance`, `scc_mixer`, `scc_mixing`, `scc_history`,
`scc_max_step`, `max_scc_iterations` for the ground-state SCC, and
`response_tolerance`, `response_max_iterations`, `response_max_subspace`,
`response_solver` for the Davidson/GMRES response. The MRSF spin-pairing and
shift controls `spc`, `spc_coco`, `spc_ovov`, `spc_coov`,
`mrsf_shift_oo`/`_co`/`_ov`/`_cv`, `spin_complete`, `reference_multiplicity`,
and `target_multiplicity` mirror the `[tdhf]` MRSF options, and `timeout`
bounds a single backend call in seconds. Each of these keeps its `[dftb]`
default.
