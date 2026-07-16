# `[dftb]`

The `[dftb]` section configures the optional **OpenQP-DFTB** backend, a
density-functional tight-binding engine that provides ground-state DFTB2, the
long-range-corrected LC-DFTB2 reference, and the SF/MRSF-TDDFTB excited-state
response with analytic gradients. It is activated by
[`[input] method=dftb`](input.md#method) and delivers the same runtypes as the
all-electron methods — energies, gradients, geometry optimization, MECI
searches, NACME, spin-orbit coupling, and surface-hopping dynamics — at
tight-binding cost. See the [MRSF-TDDFTB workflow](../workflows/mrsf-tddftb.md)
for complete decks.

!!! warning "External library and development preview"
    OpenQP-DFTB is a **separate, optional library** (`libopenqp_dftb_c`,
    repository
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
grad=1
```

`parameter_path` accepts either a single combined `.opdftb` parameter file or a
directory of Slater–Koster `<El>-<El>.skf` files. `basis` is a placeholder for
the DFTB backend (the Slater–Koster minimal basis is used regardless of its
value), but a value must be present to satisfy the generic input checker.

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

### `parameter_path`

| Field | Value |
| --- | --- |
| Type | string |
| Default | *(empty)* |
| Used by | Slater–Koster parameters (required) |

Path to a `.opdftb` parameter file or an SKF directory.

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
