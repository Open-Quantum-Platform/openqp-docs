# `md()`, `namd()`, and `[md]`

`md(...)` owns the nuclear propagation controls. Used alone, it runs
ground-state gas-phase Born--Oppenheimer molecular dynamics (BOMD). Adding
`namd(...)` changes the electronic dynamics to excited-state fewest-switches
surface hopping (FSSH). Adding `qmmm(...)` applies the corresponding QM/MM
Hamiltonian and force model; it does not select the electronic state.

| Concise input | Dynamics |
| --- | --- |
| `md(...)` | ground-state gas-phase BOMD |
| `md(...) qmmm(...)` | ground-state QM/MM MD |
| `namd(...) md(...)` | excited-state gas-phase NAMD |
| `namd(...) md(...) qmmm(...)` | excited-state QM/MM NAMD |

## Dynamics Backend Selection

OpenQP has two nuclear-propagation implementations. The input describes the
physical system; the program selects the implementation from that information
rather than asking the user to repeat it with an independent backend keyword.

| Physical system | Selected implementation | Rule |
| --- | --- | --- |
| Ground-state all-QM gas phase, `md(...)` without `qmmm(...)` | native OpenQP velocity Verlet | The molecule is finite and has no MM topology. |
| Ground-state QM/MM, including `cutoff=NoCutoff` | OpenMM `QMMM_MD` | OpenMM supplies the MM force field, constraints, thermostat, and integration. |
| Periodic QM/MM, `cutoff=PME`, `Ewald`, or `CutoffPeriodic` | OpenMM `QMMM_MD` | Periodic dynamics always requires OpenMM. |
| Gas-phase NAMD | native OpenQP NAMD propagator | Surface hopping and momentum adjustment are performed by the NAMD driver. |
| QM/MM NAMD | native OpenQP NAMD propagator with OpenMM MM forces | OpenMM evaluates the MM part, while the NAMD driver propagates the nuclei and electronic amplitudes. |
| Finite spherical containment, `droplet(...)` | native OpenQP NAMD propagator | This special nonperiodic boundary is currently connected to NAMD only. |

Thus, the normal condensed-phase and QM/MM route uses OpenMM, and periodic
systems cannot select the native gas-phase integrator. The native ground-state
driver is retained for all-QM gas-phase BOMD. A ground-state QM/MM calculation
with the finite spherical boundary is not yet connected; requesting
`droplet(...)` with `md(...)` is rejected rather than silently selecting the
wrong implementation.

Sectioned legacy input stores both common and NAMD-specific controls under
`[md]`. For excited-state dynamics, use an all-electron MRSF-TDDFT theory block
(`method=tdhf`, `[tdhf] type=mrsf`). See the
[SOC-NAMD-QMMM workflow](../workflows/soc-namd-qmmm.md) for complete decks and
theory.

!!! note "Available in OpenQP 1.3.0"
    NAMD, verification policies, packed trajectory/restart records, and the SOC
    trajectory/restart extensions are included in OpenQP 1.3.0.

!!! note "Policy terminology and legacy aliases"
    Use `nacme_policy*` and `nve_policy*` in `.oqp`, Python, and sectioned
    `.inp` input. The former `nacme_gate*` and `nve_gate*` spellings remain
    accepted as compatibility aliases, but new inputs and documentation should
    use `policy`. Do not specify both spellings for the same setting.

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

## Quick Start

Ground-state gas-phase BOMD:

```text
dft/pbe0/def2-svp
md(S0,nstep=400,dt=0.5,ensemble=nve,temperature=300,velocity=maxwell)
geom="molecule.xyz"
```

Gas-phase FSSH on MRSF-TDDFT states, starting from a specified geometry and
velocity file:

`.oqp`:

```text
mrsf(nstate=5)/bhhlyp/6-31g*
namd(S1,scheme=TDC_NAC)
md(dt=0.5,nstep=400,velocity="molecule.vel")
scf(conv=1e-8) tdhf(conv=1e-8)
geom="molecule.xyz"
```

Here `dt=0.5` fs and `nstep=400` give a total propagation time of 200 fs:

\[
t_{\mathrm{total}} = n_{\mathrm{step}}\,\Delta t.
\]

The geometry and velocity files form one initial condition and must list atoms
in the same order. `TDC_NAC` is the principal and recommended treatment: state
overlaps provide the time-derivative coupling for electronic propagation, and
an analytic derivative-coupling vector determines the momentum-adjustment
direction only when a hop is selected. See [`velocity`](#velocity) for the file
format, units, unit conversion, and preparation of Maxwell--Boltzmann or
externally sampled velocities.

Python:

```python
from oqp.openqp import OpenQP

job = OpenQP("molecule_namd")
job.molecule("molecule.xyz")
job.theory.mrsf(functional="bhhlyp", basis="6-31g*", nstate=5)
job.settings.scf(conv=1e-8)
job.settings.tdhf(conv=1e-8)
job.workflow.md(dt=0.5, nstep=400, velocity="molecule.vel")
job.workflow.namd(init_state="S1", scheme="TDC_NAC")
mol = job.run()
```

For sectioned legacy `.inp` input, write the corresponding low-level `[md]`
keywords directly; see [Legacy `.inp`](../input-file.md).

## Choose One `scheme`

The propagation coupling and the momentum adjustment at a hop are separate
choices. The following combinations reproduce the four representative
treatments commonly compared for MRSF NAMD. The two finite values of `thrshe`
are expressed in Hartree: 10 kcal mol⁻¹ is `0.015936`, whereas the
10 eV numerical ceiling is `0.367493`.

| `scheme` | Electronic propagation | Hop rescaling | Gap limit | Frustrated hop |
| --- | --- | --- | --- | --- |
| `BaeckAn` | Baeck--An energy-curvature approximation | isotropic | 10 kcal mol⁻¹ | unchanged |
| `Overlap` | norm-preserving interpolation of overlaps | isotropic | 10 kcal mol⁻¹ | unchanged |
| `TDC_NAC` | norm-preserving interpolation of overlaps | selected-pair analytic NAC direction | 10 eV | reflected along the NAC direction |
| `NAC` | velocity-contracted analytic NAC | analytic NAC direction | 10 eV | reflected along the NAC direction |

After the MRSF method specification, choose exactly one of the following
concise `.oqp` NAMD requests:

```text
# Baeck–An
namd(S1,scheme=BaeckAn) md(dt=0.5,nstep=400,velocity="molecule.vel")

# Overlap TDC
namd(S1,scheme=Overlap) md(dt=0.5,nstep=400,velocity="molecule.vel")

# NAC-guided TDC reversal
namd(S1,scheme=TDC_NAC) md(dt=0.5,nstep=400,velocity="molecule.vel")

# Full NAC
namd(S1,scheme=NAC) md(dt=0.5,nstep=400,velocity="molecule.vel")
```

`scheme` selects the complete surface-hopping treatment: electronic
propagation, hop rescaling, the gap limit, and frustrated-hop treatment. It is
required in concise `.oqp` and Python input. Do not add `tdc`, `rescale`,
`thrshe`, or `frustrated` to a named scheme.

### `scheme` (`.oqp` and Python API)

| Field | Value |
| --- | --- |
| Type | string |
| Default | none; required |
| Values | `BaeckAn`, `Overlap`, `TDC_NAC`, `NAC`, `custom` |
| Used by | complete Table-1 surface-hopping treatment selection |

`TDC_NAC` is the principal OpenQP scheme for supported gas-phase, same-spin
singlet MRSF dynamics. `NAC` has the same model restriction. Both require SCF
and MRSF response convergence thresholds of at most `1e-8`. `Overlap` is the
simple overlap/isotropic scheme. `BaeckAn` is intended for a defined comparison
with the Baeck--An approximation.

For `TDC_NAC` or `NAC`, use for example:

```text
mrsf(nstate=4)/bhhlyp/6-31g* scf(conv=1e-8) tdhf(conv=1e-8)
```

`TDC_NAC` and `NAC` do not apply to SOC-NAMD or QM/MM NAMD. Those calculations
must use a physically defined `custom` scheme. See
[NAMD Advanced Controls](md-advanced.md) for the four expanded low-level
keywords and supported examples.

## Essential Options

Most calculations need only these options.

| Option | Default | When to set it |
| --- | --- | --- |
| `nstep` | `100` | Set the trajectory length together with `dt`. |
| `dt` | `0.5` fs | Change only after checking nuclear-time-step convergence. |
| `velocity` | `maxwell` | Use `zero` or a velocity-file path for a specified initial condition. |
| `temperature` | `300.0` K | Temperature for Maxwell--Boltzmann velocity generation and, with `ensemble=nvt`, the thermostat target. |
| `seed` | `0` → local `YYYYMMDD` | Set explicitly for reproducible trajectory ensembles. |
| `rng_stream` | `1` | Give each trajectory an independent counter-RNG stream. |
| `ensemble` | `nve` | Choose `nve` or `nvt`; NVT uses Langevin dynamics. |
| `friction` | `1.0` ps⁻¹ | Langevin friction, used only with `ensemble=nvt`. |
| `scheme` (`namd()` only) | none; required | Write `scheme=TDC_NAC` for the principal treatment on its supported route. |
| `active` (`namd()` only) | `1` | Select the initial state when a physical state label is not supplied. |
| `decoherence` | `edc` | Usually retain EDC; use `off` only for a controlled comparison. |
| `nve_policy` | `warn` | Monitor total-energy behavior without terminating the trajectory. |
| `soc` | `False` | Enable spin-adiabatic or MCH-basis SOC-NAMD. |
| `soc_basis` | `adiabatic` | Select `mch` for the current recommended production SOC force path. |

!!! info "Advanced controls are documented separately"
    Custom schemes, NACME comparison, strict NVE criteria, SCF/reference
    continuity, discontinuity correction, local continuation, and SOC
    diagnostic controls are collected in
    [NAMD Advanced Controls](md-advanced.md). Do not copy them into a standard
    input unless that specific treatment or diagnostic is required.

## Standard Keyword Reference

### `nstep`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `100` |
| Used by | nuclear propagation |

Number of nuclear (velocity-Verlet) steps. The requested propagation time is
`nstep * dt`; there is no separate `total_time` keyword. For example,
`nstep=400` and `dt=0.5` request 200 fs.

### `dt`

| Field | Value |
| --- | --- |
| Type | float (fs) |
| Default | `0.5` |
| Used by | nuclear propagation |

Nuclear timestep in femtoseconds. Choose `dt` together with `nstep`, so that
both the time resolution and total propagation time are explicit.

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

## Advanced Electronic-Propagation Controls

### `substep`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `50000` |
| Used by | electronic propagation |

Number of electronic-amplitude integration sub-steps per nuclear step. This is
not the number of nuclear steps and does not change the total propagation time.

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

## Advanced Custom-Scheme Keyword Reference

The following four keywords are not independent routine choices in concise
input. A named `scheme` fixes all four. Use them directly only with
`scheme=custom`, or in sectioned legacy `[md]` input.

### `thrshe`

!!! note "Advanced custom-scheme control"
    In concise `.oqp` and Python input, set this option only with
    `scheme=custom`, together with explicit `tdc`, `rescale`, and `frustrated`.
    A named scheme supplies all four values itself. Sectioned `.inp` input
    continues to state the low-level `[md]` controls directly.

| Field | Value |
| --- | --- |
| Type | float (Ha) |
| Default | `0.367493` (10 eV) |
| Used by | energy-gap condition for attempted hops |

Maximum state-energy gap for an attempted hop. The default 10 eV ceiling
excludes only exceptionally large-gap hop candidates. Set a smaller positive
value in Hartree when the selected surface-hopping protocol defines a tighter
restriction; the `BaeckAn` and `Overlap` schemes use 10 kcal mol⁻¹
(`0.015936` Hartree).

### `tdc`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `npi` |
| Values | `fd`, `npi`, `analytic`, `baeck_an` |
| Used by | time-derivative couplings |

Time-derivative coupling scheme. `fd` uses the finite-difference
(Hammes-Schiffer--Tully) overlap form. `npi` uses norm-preserving interpolation
of the phase-aligned state-overlap matrix. `analytic` contracts each analytic
MRSF derivative-coupling vector with the nuclear velocity. The analytic route
is available for same-spin singlet MRSF states built from a two-SOMO
ROHF/ROKS triplet reference; the SCF and response convergence thresholds must
both be at most `1e-8`.

`baeck_an` propagates the electronic amplitudes with the lagged
time-dependent Baeck-An (TD-BA) coupling instead of the overlap TDC. From the
adiabatic gap `dE_ij(t)`, the magnitude at the centre of three consecutive
energy points is

\[
\left|\tau^{\mathrm{BA}}_{ij}(t_n)\right|
=\frac{1}{2}\sqrt{
\frac{\mathrm d^2 \Delta E_{ij}(t_n)/\mathrm dt^2}
     {\Delta E_{ij}(t_n)}}.
\]

A pair is set to zero when the radicand is nonpositive, the centre gap is zero,
or the centre gap exceeds [`ba_gap_max`](#ba_gap_max).

**The coupling is one nuclear step lagged.** The centred curvature at `t_n`
becomes available only after the energies at `t_(n+1)` have been evaluated, so
causal dynamics applies it during the electronic propagation at `t_(n+1)`. It
is not an instantaneous Baeck-An coupling.

Energies alone do not fix the wavefunction gauge, so the magnitude takes the
pairwise sign of the phase-tracked, centred overlap TDC; a pair whose overlap
sign is exactly indeterminate is set to zero. The first interval, and any
interval following a discontinuous history, fall back to the overlap NPI TDC as
a warm-up value. Dense trajectory records distinguish the two sources:

| `tdc_source` | Meaning |
| --- | --- |
| `1` | Overlap NPI warm-up |
| `3` | Lagged Baeck-An magnitude with overlap-transported sign |

Scope: same-spin FSSH only. It supplies no `3N` coupling vector and therefore no
direction-specific momentum adjustment, and it makes no claim to supply a Berry
phase or a signed electronic-state gauge. The one-step lag and the `ba_gap_max`
pair selection are part of the named approximation and must be preserved in
comparisons and restart signatures. Pair it with `rescale=isotropic` to test the
approximate electronic coupling without adding an analytic NAC-vector
calculation at a hop.

### `rescale`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `auto` |
| Values | `auto`, `isotropic`, `analytic_nac`, `hop_analytic_nac` |
| Used by | velocity adjustment after a successful or frustrated hop |

Select the direction used to adjust the nuclear velocity while conserving the
total energy at a surface hop. `isotropic` scales all velocity components.
`analytic_nac` uses the analytic derivative-coupling vector already evaluated
for every state pair. `hop_analytic_nac` evaluates only the active--candidate
pair when a hop is selected. `auto` chooses `hop_analytic_nac` for a supported
gas-phase, same-spin singlet MRSF calculation with sufficiently converged SCF
and response states, and otherwise uses `isotropic`.

Consequently, the low-level defaults `tdc=npi,rescale=auto` implement the
recommended `TDC_NAC` treatment on its supported route: overlap TDC propagates
the amplitudes, while analytic NAC is evaluated only for the selected hop.

The `tdc` and `rescale` choices are independent. For example,
`tdc=npi,rescale=auto` propagates the electronic amplitudes from state overlaps
and evaluates an analytic derivative-coupling vector only for a selected hop.
`tdc=analytic,rescale=analytic_nac` uses analytic derivative couplings for both
electronic propagation and directional velocity adjustment.

### `frustrated`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `reflect` |
| Values | `none`, `reflect` |
| Used by | frustrated directional hops |

Choose the treatment when the available kinetic energy is insufficient for a
hop whose velocity adjustment uses an analytic derivative-coupling direction.
`none` leaves the velocity unchanged. `reflect` reverses its component along
the derivative-coupling vector.

## Advanced State-Following Controls

### `trivial`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | trivial-crossing handling |

Enable trivial- (weakly avoided) crossing detection and diabatic following, so
the active surface tracks state character through sharp crossings instead of
hopping. This is an opt-in heuristic rather than part of standard FSSH; leave
it off unless the chosen protocol has been validated with it.

### `trivial_thresh`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.5` |
| Used by | trivial-crossing handling |

State-overlap threshold that flags a trivial crossing. Only used when
`trivial=True`.

## Advanced Electronic-Structure Continuity and Energy-Discontinuity Treatment

### `mo_reuse`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `True` |
| Used by | SCF initial guess after the first nuclear step |

Reuse the converged orbitals from the preceding geometry as the initial guess
for the next SCF calculation. This helps retain the same two-SOMO triplet
reference along an MRSF trajectory. When disabled, each step uses the configured
standalone SCF guess.

### `scf_guess_retry`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `True` |
| Used by | recovery from a failed continuation SCF calculation |

After an SCF calculation starting from the preceding-step orbitals fails,
attempt one fresh-guess calculation. A successful ordinary SCF step does not
invoke this retry.

### `scf_fail`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `escalate` |
| Values | `escalate`, `restart` |
| Used by | response to a failed continuation SCF calculation |

`escalate` retains the standard OpenQP sequence of increasingly robust SCF
convergers. `restart` instead recomputes the reference from a fresh guess with
SOSCF and treats that geometry as a discontinuous reference boundary: the
electronic coefficients are retained and no surface hop is attempted during
that step.

### `ref_follow`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `soscf` |
| Values | `off`, `soscf`, `diis_vshift` |
| Used by | continuity of the ROHF/ROKS two-SOMO reference |

Select the SCF procedure used after the initial step to retain the preceding
two-SOMO reference. `soscf` uses SOSCF. `diis_vshift` uses DIIS with a
0.2-Hartree level shift. `off` leaves reference continuity to the ordinary SCF
settings.

### `ref_switch_rescale`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `True` |
| Used by | total-energy treatment at a detected reference change |

When the SOMO-overlap criterion identifies a change of reference, adjust the
nuclear velocity isotropically so that the total energy is continuous across
the change. The event and energy adjustment are recorded separately from a
physical surface hop.

### `somo_tol`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `0.5` |
| Used by | detection of a two-SOMO reference change |

Minimum aligned overlap retained by the two-SOMO subspace. A smaller overlap
is recorded as a reference-change event.

### `disc_rescale`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `True` |
| Used by | residual numerical total-energy discontinuities |

After the finer nuclear integrations selected by `disc_substeps` are exhausted,
permit an isotropic numerical velocity adjustment when the electronic
calculation is converged and the target kinetic energy is positive. This
adjustment is recorded separately and is not a physical surface hop.

### `disc_tol`

| Field | Value |
| --- | --- |
| Type | float (Ha) |
| Default | `0.002` |
| Used by | detection of a numerical total-energy discontinuity |

Absolute pre-hop change in total energy that initiates finer nuclear
integration. It is a trigger for recalculation, not an upper bound on the final
numerical velocity adjustment.

### `disc_substeps`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `10` |
| Used by | finer nuclear integration after an energy discontinuity |

Maximum number of equal nuclear substeps used to repeat an interval whose
pre-hop energy change exceeds `disc_tol`. OpenQP tries progressively finer
partitions (`2`, `4`, `8`, and then the configured maximum when necessary).
Set `0` to disable this recalculation; when either `disc_rescale` or
`ref_switch_rescale` is enabled, at least two substeps are used.

## Initial Conditions

### `temperature`

| Field | Value |
| --- | --- |
| Type | float (K) |
| Default | `300.0` |
| Used by | initial velocities |

Temperature for Maxwell--Boltzmann initial velocities (used when
`velocity=maxwell`) and the target temperature when
`ensemble=nvt`. It is ignored for initialization when `velocity` is
`zero` or a file path, and when a restart or local continuation supplies
velocities from its checkpoint. Sectioned legacy input represents this public
value with `init_temp` and `thermostat_temperature`.

### `velocity`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `maxwell` |
| Values | `maxwell`, `zero`, *(file path)* |
| Used by | initial velocities |

Initial velocity source: `maxwell` samples a Maxwell--Boltzmann distribution at
`temperature`, `zero` starts from rest, or a file path reads velocities from a
file. `maxwell` is a classical distribution, not a vibrational Wigner sample.
Because `maxwell` is the default, omitting `velocity` generates an initial
300 K sample by default. This is also true for `ensemble=nve`: NVE means that
no thermostat exchanges heat after initialization, not that the initial
temperature is zero or that `temperature` is unnecessary.
One `.oqp` NAMD request uses one initial geometry; a Wigner ensemble must supply
one independently sampled geometry/velocity pair per trajectory.

#### Velocity-file format

A velocity file contains exactly one `vx vy vz` line per atom, in the same atom
order as the geometry. It has no atom labels, atom count, or comment line. The
components are Cartesian velocities in atomic units, bohr per atomic unit of
time, not momenta. For a six-atom geometry the file therefore has six lines:

```text
 1.2345678901234567e-04  -2.3456789012345678e-04   3.4567890123456789e-05
-4.5678901234567890e-05   5.6789012345678901e-05  -6.7890123456789012e-05
 7.8901234567890123e-05  -8.9012345678901234e-05   9.0123456789012345e-05
-1.0123456789012345e-04   1.1234567890123456e-04  -1.2345678901234567e-04
 1.3456789012345678e-04  -1.4567890123456789e-04   1.5678901234567890e-04
-1.6789012345678901e-04   1.7890123456789012e-04  -1.8901234567890123e-04
```

OpenQP reads the numerical array, requires `3N` values, reshapes it to
`(N, 3)`, and removes centre-of-mass translation. It does not remove overall
rotation. For an exact comparison among dynamics programs, prepare a velocity
set whose centre-of-mass velocity is already zero, use the same atomic masses,
and supply the same full-precision values to every program.

Common conversions to the velocity unit required by the file are:

```text
v [bohr / atomic unit of time] = 0.0457102876725563 * v [angstrom / fs]
v [bohr / atomic unit of time] = v [bohr / fs] / 41.341374575751
```

Do not copy velocities from a trajectory file without checking its units.

#### Preparing a velocity file

For a Wigner or other vibrationally sampled ensemble, export each sampled
geometry together with its paired velocity, convert the velocity components to
atomic units, remove centre-of-mass translation consistently, and write one
`.vel` file per trajectory. Do not combine a Wigner-sampled geometry with an
independently generated Maxwell--Boltzmann velocity unless that is the intended
initial-condition distribution.

For a classical Maxwell--Boltzmann initial condition, OpenQP can generate the
velocity internally with
`md(velocity=maxwell,temperature=300,seed=SEED,rng_stream=TRAJECTORY_ID)`. To create a
portable file before running any dynamics program, place one atomic mass in
dalton per line in `molecule.mass`, in geometry order, and run:

```python
import numpy as np

temperature = 300.0
seed = 20260929

kb_hartree_per_k = 3.166811563e-6
amu_to_electron_mass = 1822.888486209

mass_au = np.loadtxt("molecule.mass", dtype=float) * amu_to_electron_mass
rng = np.random.default_rng(seed)
sigma = np.sqrt(kb_hartree_per_k * temperature / mass_au)
velocity = rng.normal(size=(mass_au.size, 3)) * sigma[:, None]

# Remove centre-of-mass translation in the same mass-weighted form used by OpenQP.
velocity -= np.sum(mass_au[:, None] * velocity, axis=0) / np.sum(mass_au)

np.savetxt("molecule.vel", velocity, fmt="%.16e")
```

This NumPy example defines a reproducible Maxwell--Boltzmann sample, but its
random sequence is not the OpenQP counter-based sequence. Use the generated
file, rather than regenerating the velocity independently, when two programs
must start from exactly the same initial condition.

### `seed`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `0` (resolved once to the local date as `YYYYMMDD`) |
| Used by | trajectory counter-RNG |

Seed for the resident Fortran counter-RNG that draws Maxwell initial velocities
and hopping random numbers. The zero sentinel is resolved once when a run starts,
and the resulting integer is frozen in the generated restart manifest. Set an
explicit nonzero campaign seed for reproducible ensembles. A hopping
draw is a pure function of `(seed, rng_stream, physical MD step)`, so worker
scheduling and unrelated calls cannot shift the hopping sequence.

### `rng_stream`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `1` |
| Used by | initial velocities and hopping counter-RNG |

Non-negative trajectory stream identifier. Use a distinct value for every
trajectory in one ensemble while keeping `seed` fixed as the campaign seed.
It separates both Maxwell initial velocities and hopping draws. The same
`(seed, rng_stream, step)` triple always gives the same full-precision uniform
value, which permits exact two-code replay. Do not reuse one stream for two
nominally independent trajectories.

## Advanced Diagnostic Criteria

### `first_hop_step`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `1` |
| Used by | active-state transitions and hopping RNG |

First physical nuclear step at which an active-state transition is permitted.
Step 0 is the initial electronic structure; step 1 has both endpoint structures
and therefore defines the first overlap/TLF2 interval. Electronic coefficients
and hop probabilities are propagated at every such interval, beginning at step
1. With the default `first_hop_step=1`, the first FSSH decision is also made at
step 1. If `first_hop_step=2` is selected explicitly, step 1 still propagates
the electronic coefficients but cannot change the active state, rescale the
velocity, or consume a hopping random number.

For a strict OpenQP/KNU comparison, use the same full-precision random tape and
the same `first_hop_step`; note that a code which labels the initial structure
as step 1 may call OpenQP's first interval “step 2.” Rounded values copied from
ordinary text output can change a hop when the probability lies close to the
random threshold.

### `nacme_check`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `off` |
| Values | `off`, `baeck_an`, `analytic` |
| Used by | independent NACME validation |

Enable an energy-only time-dependent Baeck–An (TD-BA) diagnostic alongside the
overlap/TLF coupling used by NAMD. With `baeck_an`, OpenQP uses three consecutive
energy points to evaluate the nonuniform central curvature of every energy gap.
It compares the resulting TD-BA coupling magnitude with the overlap-derived TDC
interpolated to the same central time and logs both matrices plus RMS and maximum
magnitude errors.

TD-BA does not use wavefunctions and therefore cannot check MO/root phase or the
signed NACME gauge. Treat it as an independent check of coupling magnitude and
peak location, not as an oracle or a replacement for TLF. It is based on a
two-state near-crossing approximation and may overestimate couplings, especially
outside its intended region. The current implementation supports same-spin
NAMD. SOC-NAMD records its full complex spin-adiabatic overlap and anti-Hermitian
TDC instead. An explicit non-`off` request through the Python workflow API is
rejected rather than silently ignored. `analytic` contracts each analytic
derivative-coupling vector with the nuclear velocity and compares that signed
quantity with the coupling used for electronic propagation. See the
[Baeck-An references](../references.md#nonadiabatic-dynamics).

### `ba_gap_max`

| Field | Value |
| --- | --- |
| Type | float (Ha) |
| Default | `0.0734986443513` (2 eV) |
| Used by | TD-Baeck–An NACME validation |

Maximum central energy gap included in the TD-BA diagnostic. Pairs above this
gap, or pairs without a positive TD-BA curvature radicand, are not evaluated by
the reference-comparison policy.

With `nacme_check=baeck_an` the setting is diagnostic only and does not modify
the overlap/TLF coupling, electronic propagation, or hopping probabilities. With
[`tdc=baeck_an`](#tdc) the same selection governs the coupling that is actually
propagated, so a pair above this gap contributes no electronic coupling at all.

### `nacme_policy`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `off` |
| Values | `off`, `warn`, `error` |
| Used by | MD NACME validation policy |

Policy applied to the common resident-Fortran NACME checks. The policy always
reports matrix invariants and reference-comparison metrics when a check is
enabled. `off` records diagnostics only, `warn` logs failed checks without
stopping dynamics, and `error` stops immediately for a finite-value or matrix
invariant failure and stops after `nacme_policy_consecutive` consecutive reference
failures.

The exact invariants are a zero diagonal and antisymmetry of both the MD TDC and
the supplied reference. TD-BA is compared by magnitude. With
`nacme_check=analytic`, the same policy compares the signed, phase-aligned
analytic NAC reference after contracting the derivative-coupling vector with
the nuclear velocity, `d_IJ . v`, at the matching time.

### `nacme_policy_invariant_tol`

| Field | Value |
| --- | --- |
| Type | float (au^-1) |
| Default | `1.0e-10` |
| Used by | diagonal and antisymmetry checks |

Absolute tolerance for exact NACME matrix invariants.

### `nacme_policy_abs_tol`

| Field | Value |
| --- | --- |
| Type | float (au^-1) |
| Default | `1.0e-4` |
| Used by | reference comparison |

Absolute component of the pair acceptance threshold.

### `nacme_policy_rel_tol`

| Field | Value |
| --- | --- |
| Type | float |
| Default | `1.0` |
| Used by | reference comparison |

Relative component of the pair acceptance threshold. Pair `IJ` passes when
`error <= nacme_policy_abs_tol + nacme_policy_rel_tol * abs(reference_IJ)`.
The deliberately broad default reflects that TD-BA is an approximation; choose
thresholds from a validated system before using `nacme_policy=error` for a
production campaign.

### `nacme_policy_consecutive`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `3` |
| Used by | `nacme_policy=error` |

Number of consecutive time points with at least one failed reference pair
required before aborting. A passing point resets the count. Exact invariant or
non-finite failures are not delayed.

### `nve_policy`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `warn` for NAMD |
| Values | `off`, `warn`, `error` |
| Used by | same-spin NVE/FSSH energy validation |

Validate the nominally microcanonical gas-phase or QM/MM
trajectory, including same-spin and SOC calculations.
The driver records total-energy drift from step zero, the change from the
previous step, the energy discontinuity at a successful hop or trivial state
change, and drift per femtosecond. `warn` prints the NVE table without stopping;
`error` records the failing point and then aborts for a failed transition-energy
check or after `nve_policy_consecutive` consecutive drift/step failures. The
restart checkpoint is not advanced past the rejected point.

This is a quantum-classical FSSH energy validation, not a claim that the
electronic subsystem alone is microcanonical. Decoherence, frustrated hops,
finite time steps, and electronic-structure convergence can contribute to
drift. NAMD drivers always own their velocity-Verlet propagation and do not
inherit `[qmmm] ensemble`; therefore the default remains `warn` even if that
unrelated ground-state QM/MM setting says `NVT` or `NPT`. The current
surface-hopping QM/MM driver uses OpenMM for forces but
performs its own velocity-Verlet + SHAKE/RATTLE propagation; the ground-state
[`[qmmm] ensemble`](qmmm.md#ensemble) NVT/NPT integrators do not control NAMD.

### `nve_policy_abs_tol`

| Field | Value |
| --- | --- |
| Type | float (Ha) |
| Default | `5.0e-3` |
| Used by | total drift from the initial energy |

### `nve_policy_step_tol`

| Field | Value |
| --- | --- |
| Type | float (Ha) |
| Default | `1.0e-3` |
| Used by | change in total energy between adjacent integration steps |

The comparison is made at every physical MD step, not between saved trajectory
records — `trajectory_interval` does not widen it. Calibrate the tolerance
against one integration step, or an `error` policy will be far more permissive
than intended once the automatic ~10 fs write cadence is resolved.

### `nve_policy_transition_tol`

| Field | Value |
| --- | --- |
| Type | float (Ha) |
| Default | `1.0e-6` |
| Used by | same-geometry energy discontinuity across a state change |

This local quantity is evaluated immediately before and after hop velocity
rescaling (or trivial state following), so it is a stricter check than ordinary
integrator drift.

### `nve_policy_consecutive`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `3` |
| Used by | `nve_policy=error` drift/step policy |

## Trajectory Output and Restart

### `trajectory_interval`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `1` (every nuclear step) |
| Used by | dense NAMD trajectory |

Positive values write every Nth MD step to the dense binary trajectory. Zero
chooses `round(10 fs / dt)`, with a minimum of one step. The final point and a
point that triggers either strict NACME or NVE validation is written even when
they are not on the regular interval.

### `trajectory_file`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `<project>.namd.trj` |
| Used by | dense NAMD trajectory |

Appendable, packed fixed-record binary trajectory for machine analysis. Numeric
values are stored directly rather than expanded as repeated decimal text, so it
is substantially more compact and faster to scan than a text trajectory holding
the same matrices. Every record contains coordinates, velocities, energies,
populations, complex electronic coefficients, hop decision and full-precision
random value, state overlap, overlap TDC, the active reference TDC/mask, policy
metrics, and root/phase tracking order, phase, matched overlap, and margin. It
also stores the NVE drift, step change, transition jump, drift rate, verdict,
and failure streak. SOC records additionally retain the complex spin-adiabatic
overlap and anti-Hermitian TDC as real/imaginary components plus the active
representation (`adiabatic` or `mch`). It is not an NPZ/ZIP archive: those formats cannot be
appended safely without rewriting the complete trajectory and cannot be
memory-mapped record by record. Compress a completed trajectory only as an
archival/post-processing step.

Read it without loading the complete trajectory into memory:

```python
from oqp.library.namd import read_namd_trajectory

header, trajectory = read_namd_trajectory("job.namd.trj")
print(trajectory["active"])
print(trajectory["overlap_tdc_au"][:, 0, 1])
```

The human-readable NACME validation table is written to the main log; no
separate tabulated NACME file is produced. On restart, OpenQP validates the
trajectory schema and calculation identity,
removes only records newer than the last atomic checkpoint, and appends the
continued trajectory. Committed records are not rewritten.

### `restart_interval`

| Field | Value |
| --- | --- |
| Type | integer |
| Default | `10` (every ten nuclear steps) |
| Used by | atomic NAMD checkpoint |

Positive values write the restart checkpoint every Nth step. Zero chooses
`round(10 fs / dt)`, with a minimum of one step. The final MD step is always
saved. Increasing the effective interval reduces checkpoint I/O but also
increases the maximum amount of accepted dynamics that must be recomputed after
an error. The generated restart input is written once because its contents do
not change between checkpoints.

### `restart_file`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `<project>.namd.restart.npz` |
| Used by | exact NAMD continuation |

Compressed, non-pickle numerical checkpoint containing coordinates, velocities,
acceleration, electronic coefficients, the previous electronic-structure tag
bundle required by MO/root/phase tracking, counter-RNG identity, NACME policy
streak, and TD-BA three-point history. SOC checkpoints additionally contain the
previous SOC eigensystem and singlet/triplet response vectors needed for the
next spin-adiabatic overlap. Their exact shapes, dtypes, and finite values are
validated before restoration. The file is written to a temporary file, flushed,
and atomically replaced.

### `restart`

| Field | Value |
| --- | --- |
| Type | boolean |
| Default | `False` |
| Used by | trajectory restart |

Restart the trajectory from a saved state.

Every canonical `.oqp` NAMD run also writes a directly runnable file named
`<project>.namd.restart.oqp` beside the main log. It preserves the original
request, resolves input-owned paths against the original input directory, and
adds `restart=true` plus explicit checkpoint and trajectory paths and freezes a
date-derived seed. Run this manifest to continue toward the original final `nstep`;
`nstep` is not interpreted as an additional number of steps. The manifest and
its NPZ numerical checkpoint must remain together. Deriving the manifest name
from the project/log stem prevents simultaneous trajectories in one output
directory from overwriting each other.

Restart, packed trajectory/checkpoint output, and NVE gating support all four
same-spin/SOC and gas-phase/QM/MM driver combinations. The independent TD-BA
NACME comparison remains same-spin only; SOC stores its complex overlap/TDC but
does not reinterpret TD-BA as a spin-adiabatic reference.

## Advanced Local Continuation with a Different Time Step

### `continuation_checkpoint`

| Field | Value |
| --- | --- |
| Type | string (file path) |
| Default | *(empty)* |
| Used by | source numerical state for a local continuation |

Start a new same-spin analytic-TDC NAMD calculation from an existing restart
checkpoint while writing new output files. This differs from `restart=true`:
ordinary restart appends the original calculation with the same time step,
whereas local continuation may reduce `dt` and keeps the source files
unchanged. `continuation_checkpoint` and `continuation_trajectory` are both
required, and `restart=true` must not be present.

### `continuation_trajectory`

| Field | Value |
| --- | --- |
| Type | string (file path) |
| Default | *(empty)* |
| Used by | source trajectory prefix for a local continuation |

Dense trajectory paired with `continuation_checkpoint`. OpenQP requires the
committed trajectory prefix to match the checkpoint step and calculation
identity. The child calculation must use unused trajectory, checkpoint, log,
and audit-file paths. In a continuation input, `nstep` is the absolute final
step index, not the number of additional steps. Local continuation currently
supports fixed-step, same-spin NAMD with `tdc=analytic`; the new `dt` cannot
exceed the original time step recorded in the continuation history.

Example:

```text
mrsf(nstate=2)/bhhlyp/sto-3g
namd(S1,scheme=NAC,
     continuation_checkpoint="source.npz",
     continuation_trajectory="source.trj",
     restart_file="child.npz")
md(nstep=3,dt=0.05,trajectory_file="child.trj")
scf(conv=1e-8) tdhf(conv=1e-8)
geom="molecule.xyz"
```

## Ensemble and Thermostat

### `ensemble`

| Field | Value |
| --- | --- |
| Type | string |
| Default | `nve` |
| Values | `nve`, `nvt` |
| Used by | nuclear propagation |

`nve` selects microcanonical propagation with no heat exchange after the
initial velocities are prepared. `nvt` selects canonical propagation with a
Langevin thermostat at `temperature` and with the damping set by `friction`.

NPT is a standard ensemble, but it is not yet available in OpenQP dynamics.
For QM/MM NPT, the pressure-control move must evaluate the QM/MM energy at each
trial box. The current ESPF-QM/MM driver does not provide that barostat-trial
energy and therefore rejects `ensemble=npt` instead of running an invalid NPT
trajectory. Its intended future public spelling is
`md(ensemble=npt,temperature=...,pressure=...,barostat_interval=...)`.

The older public spelling `thermostat=off|langevin` remains accepted for input
compatibility and is translated to `ensemble=nve|nvt`. New inputs should use
`ensemble`. Do not specify both spellings in a new input.

### `friction`

| Field | Value |
| --- | --- |
| Type | float (ps^-1) |
| Default | `1.0` |
| Used by | Langevin thermostat |

Positive Langevin friction coefficient. It is required to be finite and
strictly positive for `ensemble=nvt`. Sectioned legacy input calls this
`thermostat_friction`.

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
the spin-adiabatic path.

### `soc_du_dt_corr`

!!! warning "Advanced SOC force diagnostic"
    `soc_du_dt_corr`, `soc_tdc_grad_corr`, and `grad_wthr` are for examining
    the approximate spin-adiabatic force. They are not needed for the
    recommended `soc_basis=mch` calculation.

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
job.workflow.md(nstep=200, dt=0.5, temperature=300.0)
job.workflow.namd(
    scheme="custom", tdc="npi", rescale="isotropic",
    thrshe=0.367493, frustrated="reflect", soc=True, soc_basis="mch",
    init_state="S1",
)

mol = job.run()
```
