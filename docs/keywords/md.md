# `[md]`

The `[md]` section controls nonadiabatic molecular dynamics (`runtype=namd`):
Tully fewest-switches surface hopping (FSSH) on MRSF states, optionally
with spin-orbit-coupled intersystem crossing (SOC-NAMD) and ESPF QM/MM
embedding. It is used together with [`[input] runtype=namd`](input.md#runtype)
and an MRSF theory block — either all-electron MRSF-TDDFT (`method=tdhf`,
`[tdhf] type=mrsf`) or the [MRSF-TDDFTB](../workflows/mrsf-tddftb.md) backend
(`method=dftb`, `[dftb] type=mrsf`), which share the same FSSH driver — and, for
embedded dynamics, the [`[qmmm]`](qmmm.md) section. See the
[SOC-NAMD-QMMM workflow](../workflows/soc-namd-qmmm.md) for complete decks and
theory.

!!! warning "Development preview"
    This section documents the NAMD implementation branch in
    OpenQP PR [#205](https://github.com/Open-Quantum-Platform/openqp/pull/205).
    It is not part of OpenQP 1.2.0; `runtype=namd` requires that source branch
    or a later release.

## Background

Surface-hopping dynamics propagates classical nuclei on one active
Born-Oppenheimer (or spin-adiabatic) potential energy surface while the
electronic amplitudes evolve; stochastic hops between surfaces reproduce
nonadiabatic transitions. OpenQP implements FSSH on MRSF-TDDFT states with
energy-based decoherence (EDC), time-derivative couplings, and trivial-crossing
following. Enabling `soc=true` extends the dynamics to the spin-adiabatic
manifold so intersystem crossing (ISC) between singlet and triplet MRSF states
is described (SOC-NAMD). Enabling [`[input] qmmm_flag=true`](input.md#qmmm_flag)
embeds the MRSF-TDDFT QM region in an OpenMM MM environment via the ESPF
operator.

## Minimal NAMD Example

Gas-phase FSSH on MRSF-TDDFT states:

`.oqp`:

```text
mrsf(nstate=5)/bhhlyp/6-31g*
namd(S1,nstep=200,dt=0.5,init_temp=300.0)
geom="molecule.xyz"
```

Python:

```python
from oqp.openqp import OpenQP

job = OpenQP("molecule_namd")
job.molecule("molecule.xyz")
job.theory.mrsf(functional="bhhlyp", basis="6-31g*", nstate=5)
job.workflow.namd(init_state="S1", nstep=200, dt=0.5, init_temp=300.0)
mol = job.run()
```

Legacy `.inp`:

```ini
[input]
runtype    = namd
method     = tdhf
functional = bhhlyp
basis      = 6-31g*
system     = molecule.xyz

[scf]
type         = rohf
multiplicity = 3

[tdhf]
type   = mrsf
nstate = 5

[md]
active    = 2
nstep     = 200
dt        = 0.5
init_temp = 300.0
```

## Core Dynamics Keywords

### `nstep`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `100` |
| Used by | nuclear propagation |

Number of nuclear (velocity-Verlet) steps.

### `dt`

| Field | Value |
| --- | --- |
| Type | float (fs) |
| Default | `0.5` |
| Used by | nuclear propagation |

Nuclear timestep in femtoseconds.

### `active`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `1` |
| Used by | initial active surface |

Initial active state (1-based). For plain FSSH this indexes the MRSF states
(`1 <= active <= [tdhf] nstate`). For SOC-NAMD it indexes the spin-adiabatic
manifold (`1 <= active <= ns + 3*nt`; see [`soc`](#soc)). For SOC runs,
[`init_state`](#init_state) can override `active` by MCH character.

### `substep`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `200` |
| Used by | electronic propagation |

Number of electronic sub-steps integrated per nuclear step.

### `decoherence`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `edc` |
| Values | `edc`, `off` |
| Used by | electronic propagation |

Decoherence correction. `edc` applies the energy-based decoherence correction
(EDC) of Granucci & Persico (see
[References](../references.md#nonadiabatic-dynamics)), the SHARC default; `off`
disables it. Energy-based decoherence is recommended for surface hopping.

### `edc_c`

| Field | Value |
| --- | --- |
| Type | float (Ha) |
| Default | `0.1` |
| Used by | EDC decoherence |

The EDC constant `C` (in Hartree) in the energy-based decoherence rate. Only
used when `decoherence=edc`.

### `thrshe`

| Field | Value |
| --- | --- |
| Type | float (Ha) |
| Default | `1.0e9` |
| Used by | hop gating |

Energy-gap gate for hops: a hop is blocked when the state gap exceeds `thrshe`.
The large default effectively disables the gate. **Set `thrshe=0.1` for
SOC-NAMD** to block spurious large-gap hops to S0 at the Franck-Condon geometry.

### `tdc`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `fd` |
| Values | `fd` (`npi` pending) |
| Used by | time-derivative couplings |

Time-derivative coupling scheme. `fd` uses the finite-difference (Hammes-Schiffer
/ Tully) overlap form. The norm-preserving interpolation (`npi`) option is
pending.

### `trivial`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `True` |
| Used by | trivial-crossing handling |

Enable trivial- (weakly avoided) crossing detection and diabatic following, so
the active surface tracks state character through sharp crossings instead of
hopping.

### `trivial_thresh`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.5` |
| Used by | trivial-crossing handling |

State-overlap threshold that flags a trivial crossing. Only used when
`trivial=True`.

## Initial Conditions

### `init_temp`

| Field | Value |
| --- | --- |
| Type | float (K) |
| Default | `300.0` |
| Used by | initial velocities |

Temperature for Maxwell-Boltzmann initial velocities (used when
`velocity=maxwell`).

### `velocity`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `maxwell` |
| Values | `maxwell`, `zero`, *(file path)* |
| Used by | initial velocities |

Initial velocity source: `maxwell` samples a Maxwell-Boltzmann distribution at
`init_temp`, `zero` starts from rest, or a file path reads velocities from a
file.

### `seed`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `1` |
| Used by | random-number generator |

Seed for the RNG that draws initial velocities and hopping random numbers. Fix
it for reproducible trajectories.

### `restart`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | trajectory restart |

Restart the trajectory from a saved state.

## SOC-NAMD (Intersystem Crossing)

### `soc`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | SOC-NAMD dispatch |

Enable SOC-NAMD: surface hopping on the **spin-adiabatic** manifold so
intersystem crossing between MRSF singlet and triplet states is described. When
`soc=true`, the manifold has `ns + 3*nt` states (`ns` singlets and `nt` triplets,
each triplet contributing three `Ms` sublevels, with `ns = nt = [tdhf] nstate`).
Combined with [`[input] qmmm_flag=true`](input.md#qmmm_flag), this selects an
SOC-QM/MM driver; [`soc_basis`](#soc_basis) chooses between the spin-adiabatic
and MCH-basis variants (see the
[dispatch table](../workflows/soc-namd-qmmm.md#how-the-driver-is-selected)).

### `soc_basis`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `adiabatic` |
| Values | `adiabatic`, `mch` |
| Used by | SOC-NAMD propagation and force basis |

Selects the SOC-NAMD representation.

| Value | Meaning |
| --- | --- |
| `adiabatic` | Propagate on spin-adiabatic SOC eigenstates and use the weighted-MCH diagonal gradient controlled by [`grad_wthr`](#grad_wthr). |
| `mch` | Propagate in the spin-pure MCH basis with exact active-root MCH gradients. With QM/MM, this selects `NAMD_SOC_MCH_QMMM`. |

The `mch` basis is the recommended production mode from the current validation
work because it avoids the approximate weighted-gradient force used by the
spin-adiabatic path.

### `soc_du_dt_corr`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | spin-adiabatic SOC-NAMD force correction |

For `soc_basis=adiabatic`, add a finite-difference `dU/dt` force correction to
the weighted-MCH diagonal gradient. This is a diagnostic/validation option for
the spin-adiabatic force path and is ignored by the MCH-basis driver.

### `soc_tdc_grad_corr`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | spin-adiabatic SOC-NAMD force correction |

For `soc_basis=adiabatic`, add an approximate MCH time-derivative-coupling
projected gradient correction. It can be combined with
[`soc_du_dt_corr`](#soc_du_dt_corr) for force-basis testing, and is ignored by
the MCH-basis driver.

### `grad_wthr`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.001` |
| Used by | SOC-NAMD active-surface force |

Weight threshold for the spin-adiabatic weighted-MCH diagonal gradient. Only
the spin-pure (MCH) components whose weight in the active spin-adiabatic state
exceeds `grad_wthr` contribute to the active-surface force (the three `Ms`
sublevels of a triplet share a summed weight). A small value keeps the force
continuous across regions of strong spin mixing.

### `init_state`

| Field | Value |
| --- | --- |
| Type | string |
| Default | *(empty)* |
| Used by | SOC-NAMD initial surface |

Start SOC-NAMD on the spin-adiabatic state whose dominant character matches this
MCH label (`S0`, `S1`, `T0`, `T1`, ...). MRSF labels are zero-based within
each spin manifold in concise `.oqp`, so `T0` is the first triplet and `T1` is
the second. Historical sectioned `.inp` and Python configurations used `T1`
for the first triplet; that spelling remains a compatibility alias there, and
`T0` is also accepted unambiguously. When empty, the initial surface is taken
from the [`active`](#active) index. `init_state` overrides `active` for SOC runs.

### `econs`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | SOC-NAMD energy conservation |

Rescale velocities each step to conserve the total energy. This is a temporary
stabilizer (band-aid) for residual drift of the spin-adiabatic weighted-MCH
diagonal gradient; leave it off unless a trajectory shows systematic energy
drift.

## Adaptive Timestep

### `dt_adaptive`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | nuclear propagation |

Shrink the timestep automatically when atoms move fast or the surface is stiff,
down to `dt_min`.

### `dt_min`

| Field | Value |
| --- | --- |
| Type | float (fs) |
| Default | `0.05` |
| Used by | adaptive timestep |

Minimum timestep for the adaptive scheme. Only used when `dt_adaptive=True`.

### `dx_max`

| Field | Value |
| --- | --- |
| Type | float (bohr) |
| Default | `0.02` |
| Used by | adaptive timestep |

Maximum per-step atomic displacement used as the adaptive-timestep criterion.
Only used when `dt_adaptive=True`.

## Notes

- **NAMD requires MRSF-TDDFT.** The input checker accepts `runtype=namd` only
  with [`[input] method=tdhf`](input.md#method) and
  [`[tdhf] type=mrsf`](tdhf.md#type).
- **Active-state range.** For plain FSSH, `1 <= active <= [tdhf] nstate`. For
  SOC-NAMD (`soc=true`), the spin-adiabatic manifold has `ns + 3*nt` states, so
  `1 <= active <= ns + 3*nt` (with `ns = nt = [tdhf] nstate`).
- **SOC-only keywords.** [`soc_basis`](#soc_basis), [`soc_du_dt_corr`](#soc_du_dt_corr),
  [`soc_tdc_grad_corr`](#soc_tdc_grad_corr), [`grad_wthr`](#grad_wthr),
  [`init_state`](#init_state), and [`econs`](#econs) apply only when
  `soc=true`. `init_state` overrides `active`; `econs` is a temporary
  stabilizer.
- **QM/MM dynamics.** Combine `[md]` with [`[qmmm]`](qmmm.md) and
  `[input] qmmm_flag=true` for embedded dynamics; see the
  [SOC-NAMD-QMMM workflow](../workflows/soc-namd-qmmm.md).

## Python API

In the compact `OpenQP` Python API,
[`job.workflow.namd(...)`](../python-scripting.md#qmmm-and-nonadiabatic-dynamics)
selects the surface-hopping run (`runtype=namd`) and sets `[md]` keywords; it
requires an MRSF-TDDFT theory. Pass `soc=True` (with an optional `soc_basis`) for
SOC-NAMD, and combine with [`job.qmmm(...)`](qmmm.md#python-api) for QM/MM
dynamics.

```python
from oqp.openqp import OpenQP

job = OpenQP("gas_socnamd", silent=1)
job.molecule(geometry="water", charge=0)
job.theory.mrsf(functional="bhhlyp", basis="6-31g*", nstate=3)

# SOC-NAMD (intersystem crossing); drop soc=... for internal-conversion FSSH
job.workflow.namd(soc=True, soc_basis="mch", nstep=200, dt=0.5,
                  init_state="S1", thrshe=0.1, init_temp=300.0)

mol = job.run()
```
