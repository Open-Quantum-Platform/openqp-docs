# NAMD Coupling Schemes

A named `scheme` fixes the four coupled choices that define one
surface-hopping treatment. This avoids combinations that do not correspond to
the intended comparison.

| `scheme` | `tdc` | `rescale` | `thrshe` | `frustrated` |
| --- | --- | --- | --- | --- |
| `BaeckAn` | `baeck_an` | `isotropic` | `0.015936` Ha | `none` |
| `Overlap` | `npi` | `isotropic` | `0.015936` Ha | `none` |
| `TDC_NAC` | `npi` | `hop_analytic_nac` | `0.367493` Ha | `reflect` |
| `NAC` | `analytic` | `analytic_nac` | `0.367493` Ha | `reflect` |

The two gap limits correspond to 10 kcal mol⁻¹ and 10 eV, respectively.
`TDC_NAC` is the default recommendation on a supported MRSF route.

## `scheme=custom`

Use `custom` only when none of the four named methods represents the intended
calculation. All four low-level choices are then required:

```text
namd(S1,scheme=custom,tdc=npi,rescale=isotropic,
     thrshe=0.367493,frustrated=reflect)
```

Do not combine a named scheme with `tdc`, `rescale`, `thrshe`, or
`frustrated`; OpenQP rejects the ambiguous input.

## `tdc`

| Value | Electronic-amplitude propagation |
| --- | --- |
| `fd` | Antisymmetric finite-difference overlap expression. |
| `npi` | Norm-preserving interpolation of the phase-aligned state-overlap matrix. |
| `analytic` | Analytic MRSF derivative-coupling vectors contracted with nuclear velocity. |
| `baeck_an` | Lagged time-dependent Baeck--An estimate from three consecutive energy gaps. |

`npi` is the principal overlap-based choice. `analytic` requires same-spin
singlet MRSF states from a two-SOMO ROHF/ROKS triplet reference and SCF and
response convergence thresholds no larger than `1e-8`.

Exact determinant-factorized state-overlap evaluation is a fixed preceding
operation: it constructs the many-electron overlap matrix from consecutive
molecular orbitals. `tdc=npi` then converts that matrix into a norm-preserving
time-derivative coupling. NPI is therefore not TLF, and there is no separate
NAMD option for choosing an approximate TLF order.

The Baeck--An coupling at the central point is based on

\[
|\tau_{ij}^{\mathrm{BA}}|=\frac12\sqrt{
\frac{\mathrm d^2\Delta E_{ij}/\mathrm dt^2}{\Delta E_{ij}}}.
\]

It is applied one nuclear step after the centred curvature becomes available.
The magnitude uses the sign of the phase-tracked overlap TDC. A nonpositive
radicand, zero gap, or gap above `ba_gap_max` gives zero for that pair. The
first interval and an interval after discontinuous history use overlap NPI as
a warm-up value.

## `rescale`

| Value | Velocity adjustment after an accepted hop |
| --- | --- |
| `isotropic` | Scale all velocity components. |
| `analytic_nac` | Use the analytic derivative-coupling direction already evaluated for all pairs. |
| `hop_analytic_nac` | Evaluate the active--candidate analytic vector only after a hop candidate is selected. |
| `auto` | Use hop-triggered analytic NAC on a supported route and isotropic adjustment otherwise. |

`rescale` concerns a physical surface hop. The numerical energy correction in
cases B and D is separately documented under
[NAMD Numerical Continuity](md-continuity.md).

## Analytic-NAC Evaluation Controls

These `[md]` keywords tune how the analytic MRSF derivative coupling is
evaluated for `TDC_NAC`, `NAC` and `nacme_check=analytic`. They require an
engine build containing
[OpenQP PR #547](https://github.com/Open-Quantum-Platform/openqp/pull/547);
earlier engines read the environment variables named below instead, which
current engines ignore with an input-check warning.

### `hop_nac_pairs`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `selected` |
| Values | `selected`, `all` |
| Used by | `rescale=hop_analytic_nac` |

`selected` evaluates the analytic vector only for the active--candidate pair
when a hop is attempted; `all` evaluates every state pair at that step, which
reproduces runs made before 2026-09-08 (the published uracil `TDC_NAC`
ensembles). The hop direction is the same pair's vector either way. Formerly
`OQP_NAMD_HOP_NAC_PAIRS`.

```text
namd(S1,scheme=TDC_NAC,hop_nac_pairs=all) md(nstep=400,dt=0.5)
```

### `nac_fuse_gradient`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | MRSF gradients when an analytic NAC is needed in the same step |

Solve the MRSF gradient z-vector together with the all-pair analytic-NAC
adjoint equations and reuse the resulting NACs, instead of two separate
response solves. Formerly `OQP_MRSF_NAC_ZV_FUSE_GRADIENT`.

### `nac_zv_predictor`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `off` |
| Values | `off`, `transport`, `linear`, `transport_approx`, `linear_approx` |
| Used by | ROHF analytic-NAC z-vector solve across MD steps |

Predict the NAC z-vector from previous steps: `transport` carries the last
solution into the current orbital basis, `linear` also extrapolates from the
two previous steps. Both only supply the initial guess, so the NAC is
unchanged to solver tolerance. The `*_approx` modes use the prediction **as
the solution** between exact solves, which changes the NACs and the hops;
use them only with [`nac_zv_exact_every`](#nac_zv_predictor-parameters) and
after checking against exact runs. Formerly `OQP_MRSF_NAC_ZV_PREDICTOR`.

#### `nac_zv_predictor` parameters

| Keyword | Default | Meaning | Formerly |
| --- | --- | --- | --- |
| `nac_zv_eta` | `1.0` | linear-extrapolation weight, clamped to `[0, 2]` | `OQP_MRSF_NAC_ZV_ETA` |
| `nac_zv_max_disp` | `0.25` bohr | RMS displacement per atom above which no prediction is used | `OQP_MRSF_NAC_ZV_MAX_DISP` |
| `nac_zv_exact_every` | `0` | `*_approx`: force an exact solve every N steps (`0` = never) | `OQP_MRSF_NAC_ZV_EXACT_EVERY` |
| `nac_zv_warmup_exact` | `0` | exact solves before the approximation is used (`0` = 1, or 2 for `linear*`) | `OQP_MRSF_NAC_ZV_WARMUP_EXACT` |
| `nac_zv_overlap_min` | `0.5` | minimum MO and state overlap for accepting a transported guess | `OQP_MRSF_NAC_ZV_OVERLAP_MIN` |

## `thrshe`

Positive maximum state-energy gap in Hartree for a hop attempt. Default:
`0.367493` Ha (10 eV). A named scheme supplies its own value.

## `frustrated`

For a directional hop with insufficient kinetic energy, `none` leaves the
velocity unchanged and `reflect` reverses its component along the analytic
derivative-coupling vector. Default low-level value: `reflect`.

## Decoherence

| Keyword | Default | Meaning |
| --- | --- | --- |
| `decoherence` | `edc` | Energy-based decoherence; `off` disables it. |
| `edc_c` | `0.1` Ha | Constant in the energy-based decoherence rate. |
| `substep` | `50000` | Electronic-amplitude integration substeps per nuclear step. |

## Optional Trivial-Crossing Following

`trivial=False` is the default. `trivial=True` enables overlap-triggered root
following with `trivial_thresh=0.5`. This is a method-specific approximation,
not part of standard FSSH and not one of the four numerical-continuity cases.

## QM/MM Scope

QM/MM NAMD supports `TDC_NAC` and `NAC` for a QM region without link atoms
under the frozen-embedding-field QM-region NAC approximation. The analytic
vector omits embedding-operator and MM-coordinate derivatives, and hop
rescaling changes QM velocities only. See [NAC](nac.md) before using this
approximation in a production calculation.
