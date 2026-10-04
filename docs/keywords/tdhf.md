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

`.oqp`:

```text
mrsf(nstate=5)/bhhlyp/6-31g*
geom="h2o.xyz"
```

Python:

```python
from oqp.openqp import OpenQP

job = OpenQP("mrsf_keywords")
job.molecule(geometry="water", charge=0)
job.theory.mrsf(functional="bhhlyp", basis="6-31g*", nstate=5)
```

Legacy `.inp`:

```ini
[input]
method=tdhf

[scf]
type=rohf
multiplicity=3

[tdhf]
type=mrsf
nstate=5
```

## Keywords

### `type`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `rpa` |
| Values | `rpa`, `tda`, `sf`, `mrsf`, `umrsf`, `qmrsf_dk`, `mrsf_ekt_ip`, `mrsf_ekt_ea` |
| Used by | response model selection |

Selects the response model. Use `mrsf` for production MRSF-TDDFT workflows.
`sf` selects ordinary spin-flip TDDFT, and `umrsf` selects the unrestricted
MRSF response model for energies and analytic nuclear gradients
(`runtype=grad`, `optimize`, `meci`, `mecp`, and `tci`) with supported
functionals. See [MRSF-TDDFT](../workflows/mrsf-tddft.md) for UMRSF gradient
restrictions. `qmrsf_dk` selects the quintet-reference dressed-kernel
method described in [QMRSF-DK](../workflows/qmrsf-dk.md). The legacy
`mrsf_ekt_ip` and `mrsf_ekt_ea` values are
energy-only; the current EKT workflow should use `[input] runtype=ekt`,
`[tdhf] type=mrsf`, and the `[ekt]` section.

MRSF workflows require an ROHF reference in the current code path. SF-TDDFT
accepts an ROHF or a UHF reference; the UHF path covers energies and gradient
workflows, while numerical Hessians still require ROHF (see
[SF-TDDFT](../workflows/sf-tddft.md)). NAC, NAMD and SOC require `type=mrsf`
regardless of the reference.
UMRSF-TDDFT requires a UHF reference. QMRSF-DK requires a quintet
(`[scf] multiplicity=5`) ROHF/ROKS reference and `[input] runtype=energy`.

### `nstate`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `1` |
| Used by | number of response roots |

Number of excited states to compute. It must be at least as large as the highest
state requested by gradients, optimizations, NACME, SOC, Hessians, or EKT.

### `nstate_s`, `nstate_t`

| Field | Value |
| --- | --- |
| Type | integer |
| Defaults | `0`, `0` |
| Used by | unequal singlet/triplet SOC spaces |

Optional numbers of singlet and triplet roots for SOC. Zero means to use
`nstate` for that common count. In a `.oqp` file, do not set these
internal selectors directly; write `soc(ns=3,nt=5)`. Both counts must be
provided together, and that form must not be combined with route `nstate`.

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
For conventional RPA/TDA (`type=rpa` or `tda`) on a closed-shell RHF reference,
only `multiplicity=1` is accepted: the response always contains the Coulomb
term and the singlet exchange-correlation kernel, so a triplet request would
reproduce the singlet roots. The input checker rejects `multiplicity=3`. For
triplet states use `type=mrsf` (ROHF) or `type=umrsf` (UHF) with a triplet
reference and set `[tdhf] multiplicity=3` as well: the reference multiplicity
does not select the response multiplicity, which defaults to `1`.
For SOC, do not set this as a single target multiplicity; the SOC workflow
computes singlet and triplet response roots internally.

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

Convergence threshold for Z-vector equations. The TDDFT, SF-TDDFT, MRSF-TDDFT and
UMRSF-TDDFT solvers stop when the Euclidean norm of the Z-vector residual is below
`sqrt(zvconv)`, so the default `1.0e-6` bounds the residual by `1.0e-3`. Lower it
(for example `1.0e-10`) when gradients are compared with finite differences.

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

### `tlf` (legacy internal name)

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `0` (exact) |
| Used by | MRSF state-overlap minor determinants |

This internal keyword remains in `[tdhf]` because the state-overlap minor
evaluation was historically implemented in the TDHF/MRSF response code. It is
not a TDDFT excitation-energy setting and is not a user-selectable NAMD method.
Only `tlf=0` is supported; nonzero TLF orders are rejected.

The setting selects how the MRSF state overlap between consecutive geometries,
`<Psi_I(t-dt)|Psi_J(t)>`, is evaluated. The reference determinant is shared, so
the overlap factorizes into a contraction of the response amplitudes with three
classes of minor determinants of the MO overlap matrix: `s_ij` one-hole
occupied minors, `s_ab` particle minors, and `s_ia` mixed minors. `tlf` selects
the treatment of `s_ij` and `s_ab`; `s_ia` is always exact.

| Internal value | Minors | Notes |
| --- | --- | --- |
| `0` (`notlf`, `exact`) | Exact Gaussian-elimination minors, no truncation | Invariant to orbital rotations between steps. This is *not* the zeroth-order TLF(0) of the paper, which is not implemented. |

The truncated Leibniz formula assumes the MOs of consecutive steps are nearly
orthonormal, i.e. that the MO overlap matrix is close to diagonal. When
near-degenerate doubly occupied orbitals rotate into each other within one
nuclear step -- a 45-degree mixing of two occupied orbitals has been observed in
hot uracil trajectories -- the diagonal MO overlaps fall to about 0.7 and a
truncated TLF treatment can return a collapsed state overlap (diagonal elements
around 0.3-0.4) even though
the SCF solution and the MRSF surfaces are continuous. Norm-preserving
interpolation then turns that collapse into a large spurious time-derivative
coupling.

The exact minors are invariant to such rotations, and for molecules the size of
uracil (30 occupied alpha orbitals, 6-31G*) they cost the same wall time as the
previous truncated implementation. For large systems where the `nvir^2`
particle minors dominate, the
recommended route is Jacobi's complementary-minor identity -- all one- and
two-hole minors from one LU factorization of the occupied block -- rather than
truncation.

The state-overlap section of the log states which evaluation was used
(`state-overlap minors: exact minor determinants (tlf=0, default; ...)` or
`TLF(n) truncated-Leibniz minors; ...`). NAMD additionally warns when every
column norm of the retained state overlap falls below 0.5.

### `hfscale`, `cam_alpha`, `cam_beta`, `cam_mu`

| Field | Value |
| --- | --- |
| Type | float |
| Defaults | `-1.0`, `-1.0`, `-1.0`, `-1.0` |
| Used by | response functional parameter overrides |

Override exact-exchange and CAM/range-separated parameters for response
calculations. Negative values mean use the selected functional defaults.

For `type=qmrsf_dk` these set the exchange carried by the dressed kernel,
independently of the reference. With a global hybrid the kernel uses
`hfscale`; with a range-separated reference it uses
`cam_alpha*K + cam_beta*K(erf(cam_mu*r)/r)`, and any of the three that is left
negative is inherited from `[dftgrid]`.

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

### `resp_cutoff`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `auto` (follows `perf`; `1e-8` baseline) |
| Used by | MRSF-TDDFT — response 2e-integral cutoff |

2e-integral cutoff for the MRSF response build. `1e-8` is exact to ≪ µeV;
looser values (e.g. `1e-6`) trade a few µeV for speed. Never tighter than the
SCF integral cutoff. See [Performance](../performance.md).

### `fp32`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `auto` (follows `perf`; no preset enables it) |
| Values | `on`, `off`, `auto` |
| Used by | MRSF-TDDFT — single-precision response digestion |

Single-precision MRSF response Fock digestion. Non-reproducible and can flip
near-degenerate states; net-slower than FP64 on CPU. Opt-in only.

### `zv_warmstart`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `auto` (follows `perf`; on at `perf` ≥ 1) |
| Values | `on`, `off`, `auto` |
| Used by | MRSF-TDDFT gradients — z-vector (CPHF) warm-start |

Reuse the previous geometry step's z-vector as the CG/GMRES initial guess
(exact; the solve still converges to the same tolerance). Most effective across
many nearby geometries (optimization, MD).

### XC response cache memory

TDDFT TDA/RPA Davidson, RHF/SF/MRSF Z-vector and RHF/UHF/ROHF CPHF
calculations reuse fixed-reference LDA/GGA XC values and derivatives. The
remaining space stores pruned atomic-orbital (AO) values and spatial derivatives
on the integration grid. Every trial density is contracted anew. AO values here
are basis-function values, not two-electron integrals.

The MRSF nuclear gradient shares AO values and their spatial derivatives between
its fixed-grid, moving-grid and ground-state XC sweeps. Changing the density
invalidates reference XC data while preserving reusable AO data. Gradient
consumers still compute their reference XC derivatives and density contractions.
Absolute grid coordinates are restored for moving-grid derivatives. Meta-GGA
response paths reuse AO blocks and recompute the reference XC data.

The current MRSF Davidson sigma has no repeated semilocal XC integration; this
cache does not add an XC term to its response equations. The preceding Davidson
buffer reuse and contiguous reductions apply independently.

Set the memory limit with the environment variable
`OQP_XC_RESPONSE_CACHE_MB` (MiB, default `256`); `0` disables storage:

```sh
OQP_XC_RESPONSE_CACHE_MB=256 OQP_XC_TIMING=1 openqp h2o.inp
```

The retained-cache limit applies to each active solver/grid cache on each MPI
rank, shared by its OpenMP threads. It does not limit total process memory,
temporary integration buffers, or the sum of independently owned caches.
Blocks that do not fit are recomputed; they are never treated as zero. The
cache does not change numerical thresholds, grid or precision. The `perf`
preset does not select this memory limit.

Geometry, basis data, grid points/weights and AO screening settings invalidate
AO data. Reference density or orbitals, occupations, functional revision and XC
derivative order additionally invalidate reference XC data. Solver-owned caches
are released when their owner returns, including early returns.

`OQP_XC_TIMING=1` adds `[XCCACHE]` lines with retained bytes, AO block hits and
XC block hits. Compare `0`, a small partial-cache limit, and `256` on the same
calculation to measure the useful limit for a given system. The engine's
`examples/response_cache/` directory provides MRSF, TDA and RPA gradient inputs.
