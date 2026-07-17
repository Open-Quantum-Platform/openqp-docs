# `[dftb]`

The `[dftb]` section configures OpenQP's **DFTB method** (density-functional
tight binding) — a first-class electronic-structure method on the same footing
as HF, DFT, and MRSF-TDDFT, selected with
[`[input] method=dftb`](input.md#method). It provides ground-state DFTB2, the
long-range-corrected LC-DFTB2 reference, and the SF/MRSF-TDDFTB excited-state
response with analytic gradients, delivering the same runtypes as the
all-electron methods — energies, gradients, geometry optimization, MECI
searches, NACME, spin-orbit coupling, and surface-hopping dynamics — at
tight-binding cost. See the DFTB method manuals for complete decks:
[ground-state DFTB](../workflows/dftb.md), [TD-DFTB](../workflows/tddftb.md),
and [MRSF-TDDFTB](../workflows/mrsf-tddftb.md).

!!! warning "External library and development preview"
    The DFTB method is implemented by **OpenQP-DFTB**, a **separate, optional
    library** (`libopenqp_dftb_c`, repository
    [`openqp-dftb`](https://github.com/Open-Quantum-Platform/openqp-dftb)) loaded
    in-process through a `ctypes` adapter; it is not linked into `liboqp`. Build
    it from the [`openqp-dftb`](https://github.com/Open-Quantum-Platform/openqp-dftb)
    repository and point [`library_path`](#library_path) at the resulting
    `libopenqp_dftb_c`, or build OpenQP with `-DENABLE_OPENQP_DFTB=ON`. A published
    `pip install openqp-dftb` wheel is planned but not yet on PyPI, so the pip form
    is not available today. The integration is tracked in OpenQP PR
    [#266](https://github.com/Open-Quantum-Platform/openqp/pull/266) and is not
    part of OpenQP 1.2.0.

## Background

DFTB replaces the all-electron two-electron integrals with atom-resolved
transition charges and short atom-pair kernels, so the SF/MRSF response is
evaluated in a compact transition-charge representation rather than from
four-center electron-repulsion integrals. The high-spin reference is a
restricted open-shell (ROKS) DFTB determinant with common spatial orbitals; the
mixed-reference singlet/triplet CSF construction is applied at the response
level exactly as in all-electron MRSF-TDDFT. Because the electronic problem is
minimal-basis, MRSF-level photochemistry becomes practical for large
chromophores, molecular aggregates, and long trajectories. See
[References](../references.md) for the DFTB, LC-DFTB, and MRSF-TDDFT theory.

The choice of response type is driven either by [`type`](#type) or, when
`type=auto`, by [`[tdhf] type`](tdhf.md#type): `mrsf` selects MRSF-TDDFTB, `sf`
selects SF-TDDFTB, `tda`/`rpa` selects ordinary TDDFTB, and a plain
energy/gradient run with no excited state requested runs a ground-state DFTB2
energy.

## Minimal DFTB Example

Ground-state DFTB2 energy:

```ini
[input]
runtype=energy
method=dftb
basis=sto-3g
functional=

[dftb]
type=ground
parameter_path=/path/to/params
```

MRSF-TDDFTB excited-state gradient:

```ini
[input]
runtype=grad
method=dftb
basis=sto-3g
functional=

[tdhf]
type=mrsf
nstate=3

[dftb]
type=mrsf
parameter_path=/path/to/params

[properties]
grad=2
```

`grad=2` targets the first excited singlet `S1`. MRSF relabels its lowest
singlet response root as `S0` (root 1), so `[properties] grad` and
`[optimize] istate` are 1-based over the MRSF manifold — an `S0` gradient uses
`grad=1`. See the
[MRSF-TDDFTB workflow](../workflows/mrsf-tddftb.md#state-labels).

`parameter_path` accepts either a single combined `.opdftb` parameter file or a
directory of Slater–Koster `<El>-<El>.skf` files. It may be left empty with a
current openqp-dftb wheel: the bundled OB2W0PT3 set (official shell-resolved
`spinw.txt` included) is then resolved automatically — see
[`parameter_path`](#parameter_path). `basis` is a placeholder for
the DFTB method (the Slater–Koster minimal basis is used regardless of its
value), but a value must be present to satisfy the generic input checker.

## Python API

OpenQP provides one explicit helper for each DFTB calculation family:

| Calculation family | Helper |
| --- | --- |
| Ground-state SCC-DFTB | `job.ground_dftb(...)` |
| Conventional TD-DFTB | `job.tddftb(...)` |
| SF-TDDFTB | `job.sf_tddftb(...)` |
| MRSF-TDDFTB | `job.mrsf_tddftb(...)` |

The same helpers are available through `job.theory`. They accept the usual
`nstate`, `parameter_path`, and `[dftb]` keyword arguments, then combine with
`job.workflow.energy()`, `.gradient(...)`, `.optimize(...)`, or another
compatible workflow. For example:

```python
from oqp.openqp import OpenQP

job = OpenQP(project="h2o_tddftb")
job.molecule("h2o.xyz", charge=0)
job.tddftb(nstate=3, state_to_state_spectrum=True)
job.workflow.energy()
job.run()
```

The general `job.dftb(response_type=...)` builder remains available. For
backward compatibility its omitted `response_type` still selects MRSF-TDDFTB;
use the explicit helpers in new scripts when the calculation family should be
immediately visible.

## Keywords

### `backend`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `native` |
| Values | `native`, `probe` |
| Used by | library selection |

`native` loads the standalone `libopenqp_dftb_c` shared library in-process
(recommended). `probe` is an explicit developer fallback that shells out to the
state-gradient executable; it supports **only energy and gradient** runs. It does
not support QM/MM electrostatic embedding, and — because the NACME, SOC, and NAMD
workflows need the native state-overlap and SOC-matrix entry points —
`backend=probe` cannot drive those. Use `backend=native` for anything beyond a
plain energy/gradient.

### `type`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `auto` |
| Values | `auto`, `ground`, `dftb`, `dftb0`, `ground_noscc`, `noscc`, `tddftb`, `tda`, `sf`, `sftddftb`, `sf-tddftb`, `mrsf`, `mrsftddftb`, `mrsf-tddftb` |
| Used by | response-method selection |

Selects the DFTB response family. `auto` derives it from the workflow and
[`[tdhf] type`](tdhf.md#type), defaulting to a ground-state DFTB energy when no
excited state is requested.

### `print_level`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `1` |
| Values | `0`, `1`, `2` |
| Used by | native SCC, response, and gradient progress logging |

Controls structured progress from the native OpenQP-DFTB kernels. Level `0`
is quiet, level `1` records stage and completion summaries, and level `2` adds
iteration-level residuals. OpenQP captures the native output and places it in
the normal calculation log; temporary trace settings and file-descriptor state
are restored after every native call.

Structured progress is an optional native-library capability. An older ABI-1,
ABI-2, or ABI-3 library that does not advertise it remains usable: OpenQP logs
that the requested trace is unavailable instead of enabling an unsafe hook.

### `state_to_state_spectrum`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `True` |
| Used by | excited-state energy calculations |

Requests all upward root-pair oscillator strengths for TD-DFTB, SF-TDDFTB, and
MRSF-TDDFTB energy calculations. Historical ground/first-root transition
values are preserved; additional excited-state pairs use the unrelaxed
TDA/state-interaction density approximation. Set this to `False` to suppress
the table.

The all-pair spectrum is also an optional native-library capability. OpenQP
reports it as unavailable when the loaded library predates that capability,
without rejecting the otherwise supported calculation.

### `model`

| Field | Value |
| --- | --- |
| Type | string |
| Default | *(empty)* |
| Values | `dtcam-tb` |
| Used by | published operator presets (native backend only) |

Applies a complete, published operator preset, resolved inside openqp-dftb
(single source of truth, so inputs cannot drift from the paper). `dtcam-tb`
selects the DTCAM-TB operator: reference LC erf(0, 0.04, 0.30 a₀⁻¹) with an
LC ground state, independent response LC (0, 1.0125, 0.2625 a₀⁻¹), official
OB2 spin-W at strengths (1.00, 0.6375), SPC channels (1.025, 0.25, 0.2625),
response-only on-site pp −0.0125 Eₕ, and the fixed numerical protocol
(Broyden 0.35 with history 12 and max step 1.0, SCC tolerance 1e-8 and
budget 4000, Davidson response, Z-vector analytic gradients).

A preset is all-inclusive: the input checker rejects combining `model=` with
any operator key or with the preset-fixed numerical keys (`scc_mixer`,
`scc_mixing`, `scc_history`, `scc_max_step`, `scc_tolerance`,
`max_scc_iterations`, `response_solver`, `zvector`). Keys the preset does not
fix — `nstate`, `response_tolerance`, `response_max_iterations`,
`response_max_subspace`, `parameter_path`, … — remain tunable. Omit `model=`
to tune the operator manually.

### `parameter_path`

| Field | Value |
| --- | --- |
| Type | string |
| Default | *(empty — resolves the bundled set)* |
| Used by | Slater–Koster parameters |

Path to a `.opdftb` parameter file or an SKF directory. When empty, the
resolution order is the `OPENQP_DFTB_PARAMETER_PATH` environment variable,
then the parameter set bundled with the installed openqp-dftb wheel
(`OB2W0PT3`: an H/C/N/O/S OB2 reparametrization at ω = 0.3 a₀⁻¹ with the
official shell-resolved `spinw.txt` alongside, which the spin-polarization
W kernels require). An explicitly supplied path always wins and is never
second-guessed. The input checker reports an error only when no source —
explicit, environment, or bundled — is resolvable.

### `library_path`

| Field | Value |
| --- | --- |
| Type | string |
| Default | *(empty)* |
| Used by | explicit `libopenqp_dftb_c` location |

Overrides library discovery. The search order is `library_path` →
`OPENQP_DFTB_LIBRARY` → the pip-installed `openqp-dftb` package →
`$OPENQP_ROOT/lib` → `PATH`.

### `executable`

| Field | Value |
| --- | --- |
| Type | string |
| Default | *(empty)* |
| Used by | `backend=probe` fallback executable |

### `timeout`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `300` |
| Used by | `backend=probe` subprocess wall-clock limit (seconds) |

Per-call wall-clock limit, in seconds, for each `backend=probe` state-gradient
subprocess; must be positive. Ignored by `backend=native`, which runs in-process
and spawns no subprocess.

### SCC (ground-state self-consistent charge) keywords

| Keyword | Type | Default | Meaning |
| --- | --- | --- | --- |
| `scc_tolerance` | float | `1.0e-8` | SCC charge convergence tolerance |
| `scc_mixer` | string | `auto` | charge mixer (`auto`, `linear`, `anderson`, `broyden`, `diis`, `trust`/`trah`) |
| `scc_mixing` | float | `0.35` | linear/damping mixing factor |
| `scc_history` | int | `12` | mixer history length |
| `scc_max_step` | float | `0.5` | maximum charge step |
| `max_scc_iterations` | int | `1200` | maximum SCC iterations |

### Response (Davidson) keywords

| Keyword | Type | Default | Meaning |
| --- | --- | --- | --- |
| `response_tolerance` | float | `1.0e-6` | response residual tolerance |
| `response_max_iterations` | int | `50` | maximum Davidson iterations |
| `response_max_subspace` | int | `100` | maximum Davidson subspace size |
| `response_solver` | string | `auto` | `auto`, `dense`, or `davidson` |
| `zvector` | bool | `True` | use the Z-vector (interchange) analytic-gradient fast path |
| `spin_complete` | bool | `True` | spin-adapted CSF construction (MRSF) vs. bare SOMO-pair CSFs |
| `reference_multiplicity` | int | `0` | high-spin reference multiplicity (`0` = auto) |
| `target_multiplicity` | int | `1` | response manifold (`1` singlets, `3` triplets) |

### Long-range / spin-pairing keywords

| Keyword | Type | Default | Meaning |
| --- | --- | --- | --- |
| `lc_gamma` | string | `yukawa` | long-range kernel: `yukawa` (LC-DFTB2 Yukawa–Slater) or `erf` (erf$(\omega R)/R$) |
| `lc_ground_state` | bool | `False` | include LC long-range exchange in the ROKS reference |
| `omega` | float | `0.3` | range-separation parameter of the response kernel (a.u.$^{-1}$) |
| `cam_alpha` | float | `0.0` | short-range exchange-like weight |
| `cam_beta` | float | `1.0` | long-range exchange-like weight |
| `spc` | float | `0.5` | MRSF spin-pairing scale applied to all channels. `-1` inherits the resolved CAM exchange fraction; every other value must be `>= 0` (the input checker rejects negatives other than `-1`, so `-999` is **not** valid here). |
| `spc_coco`, `spc_ovov`, `spc_coov` | float | inherit | Per-channel overrides (CO×CO, OV×OV, CO×OV) that split the single `spc`. Reachable only through the standalone `libopenqp_dftb_c` / probe interface, not the PyOQP `[dftb]` surface; each defaults to inheriting the resolved exchange fraction. |
| `mrsf_shift_oo`, `mrsf_shift_co`, `mrsf_shift_ov`, `mrsf_shift_cv` | float | `0.0` | optional diagnostic diagonal shifts (Hartree) by CSF class |

!!! note "erf-tuned kernel"
    The combination `lc_gamma=erf`, `omega=0.25`, `cam_beta=1.2` is the
    *erf-tuned* response operator that reproduces the MRSF-TDDFT relative
    ordering of near-degenerate bright/dark states. The `cam_beta>1`
    over-correction makes the LC ground-state SCC harder to converge; use a
    robust mixer (`scc_mixer=trust`).

### QM/MM and SOC

DFTB QM/MM uses Mulliken-monopole electrostatic embedding: the MM potential
enters the SCC Hamiltonian directly (no ESPF grid fitting), and the analytic
gradient carries the coupling. Activate it with
[`[input] qmmm_flag=true`](input.md#qmmm_flag) and the [`[qmmm]`](qmmm.md)
section; the legacy `split` embedding is not supported. One-center spin-orbit
coupling reads per-element `soc Z l xi` records from the parameter file. See the
[MRSF-TDDFTB workflow](../workflows/mrsf-tddftb.md).
