# Molecular Dynamics

OpenQP uses three explicit input calls for dynamics:

- `md(...)` contains nuclear propagation, initial-condition, ensemble, and
  output settings.
- `namd(...)` adds excited-state propagation and surface hopping.
- `qmmm(...)` selects a QM/MM model. It does not replace either dynamics call.

Thus `md(...)` alone requests ground-state Born--Oppenheimer molecular
dynamics, while `namd(...) md(...)` requests nonadiabatic molecular dynamics
(NAMD). Add `qmmm(...)` to either form when a QM/MM calculation is intended.

These calls give four supported compositions: ground-state MD, ground-state
QM/MM MD, NAMD, and QM/MM NAMD.

## Dynamics Backend Selection

Gas-phase dynamics uses the native OpenQP integrator. Every QM/MM calculation,
periodic or not, propagates the complete system with OpenMM and evaluates the
QM forces with OpenQP. Periodicity is selected by the QM/MM electrostatics,
`qmmm(cutoff=PME)`, `Ewald`, or `CutoffPeriodic`, which require box vectors in
the PDB file; there is no separate periodic switch.

| Calculation | Input form | Dynamics backend |
| --- | --- | --- |
| Gas-phase ground-state dynamics | `md(...)` | native OpenQP |
| QM/MM ground-state dynamics | `md(...) qmmm(...)` | OpenMM with OpenQP QM forces |
| Gas-phase NAMD | `namd(...) md(...)` | native OpenQP |
| QM/MM NAMD | `namd(...) md(...) qmmm(...)` | OpenMM environment with OpenQP QM forces |

## Ownership of Dynamics Controls

`md(...)` owns every control of nuclear propagation: `nstep`, `dt`,
`velocity`, `temperature`, `ensemble`, `friction`, `seed`, `rng_stream`,
`mo_reuse`, and the output and continuation keywords `trajectory_file`,
`trajectory_interval`, `energy_file`, `restart_file`, `restart_interval`,
`restart`, `snapshot`, and `snapshot_interval`. `namd(...)` owns the electronic
treatment: the initial state, `scheme`, `continuity`, and the surface-hopping
controls. `qmmm(...)` owns the system partition and the MM model.

A control given in two places is rejected rather than resolved silently. For
example, `md(nstep=400) qmmm(n_steps=400)` and `md(dt=0.5) qmmm(timestep=0.5)`
are errors; keep nuclear propagation in `md(...)`. Older inputs that place
`nstep`, `dt`, and the other common controls inside `namd(...)`, or `n_steps`
and `timestep` inside `qmmm(...)` without `md(...)`, are still read.

`namd(...)` tightens the SCF and response convergence to `1e-8` unless
`scf(conv=...)` or `tdhf(conv=...,zvconv=...)` is given, because analytic
coupling vectors require converged states.

## Minimal Inputs

Ground-state gas-phase dynamics:

```text
bhhlyp/6-31g* geom="molecule.xyz"
md(nstep=400,dt=0.5,velocity="molecule.vel",ensemble=nve)
```

Gas-phase ground-state MD evaluates the ground-state energy and analytic
gradient at every geometry and propagates the nuclei with velocity Verlet.
`ensemble=nvt` adds a Langevin thermostat at `temperature` with `friction` in
ps⁻¹ (default `1.0`). It currently requires a single MPI rank (`--nompi`) and
writes no checkpoint; see [Initial Conditions and Restart](md-initial-restart.md)
for its output files.

Recommended MRSF-TDDFT NAMD:

```text
mrsf(nstate=4)/bhhlyp/6-31g* geom="molecule.xyz"
namd(S1,scheme=TDC_NAC,continuity=on)
md(nstep=400,dt=0.5,velocity="molecule.vel",ensemble=nve)
```

`continuity=on` is shown explicitly because it is part of the recommended
method definition. It is also the default and may be omitted after the input
has been established. The complete treatment is described in
[NAMD Numerical Continuity](md-continuity.md).

QM/MM NAMD:

```text
mrsf(nstate=4)/bhhlyp/6-31g* geom="system.xyz"
namd(S1,scheme=TDC_NAC,continuity=on)
md(nstep=400,dt=0.5,velocity="system.vel",ensemble=nve)
qmmm(pdb_file="system.pdb",forcefield_files="forcefield.xml",
     qm_atoms="0-12")
```

`TDC_NAC` and `NAC` are available for QM/MM NAMD under the documented
frozen-embedding-field QM-region NAC approximation and without link atoms.
See [NAC](nac.md) for its exact scope.

## Choose One NAMD `scheme`

Every concise `namd(...)` input requires one complete surface-hopping scheme.
The choice determines electronic-amplitude propagation, momentum-adjustment
direction, hop-gap ceiling, and the treatment of a frustrated directional hop.

| `scheme` | Electronic propagation | Successful-hop velocity adjustment | Hop-gap ceiling | Frustrated directional hop |
| --- | --- | --- | --- | --- |
| `BaeckAn` | lagged time-dependent Baeck--An coupling | isotropic | 10 kcal mol⁻¹ | unchanged |
| `Overlap` | overlap NPI TDC | isotropic | 10 kcal mol⁻¹ | unchanged |
| `TDC_NAC` | overlap NPI TDC | analytic NAC for the selected hop | 10 eV | reflect NAC-direction component |
| `NAC` | analytic NAC contracted with velocity | analytic NAC | 10 eV | reflect NAC-direction component |

`TDC_NAC` is the principal general setting: overlaps propagate the electronic
amplitudes, while the analytic derivative-coupling vector is evaluated for a
selected hop. `NAC` evaluates analytic couplings for electronic propagation as
well. Full definitions and `scheme=custom` are on
[NAMD Coupling Schemes](md-schemes.md).

## Essential Options

For a standard calculation, choose only the nuclear duration and initial
conditions, the ensemble, one named NAMD scheme, and the continuity treatment.
The defaults are suitable for a first input except for the system-dependent
trajectory length and, when reproducibility is required, the initial velocity
file or ensemble specification.

| Keyword | Default | Meaning |
| --- | --- | --- |
| `nstep` | `100` | Number of nuclear steps. |
| `dt` | `0.5` fs | Nuclear timestep. Total time is `nstep * dt`. |
| `velocity` | `maxwell` | `maxwell`, `zero`, or a velocity-file path. |
| `temperature` | `300.0` K | Maxwell--Boltzmann sampling temperature and NVT target. |
| `ensemble` | `nve` | Choose `nve` or `nvt`; `npt` is rejected (equilibrate the cell classically and start from a snapshot). |
| `scheme` | required by `namd()` | One of the four schemes above or `custom`. |
| `continuity` | `on` | Complete A--D numerical-continuity treatment; use `manual` only for individual controls. |

Use a state label such as `namd(S1,...)` to select the initial electronic
state. The lower-level `active` index is documented with the advanced controls.
Random streams and detailed velocity preparation are on
[Initial Conditions and Restart](md-initial-restart.md); decoherence and
electronic substeps are on [NAMD Coupling Schemes](md-schemes.md); energy and
coupling criteria are on [NAMD Diagnostics](md-diagnostics.md).

## Essential Definitions

### `nstep`

Positive integer number of nuclear steps. The requested propagation time is
`nstep * dt`; there is no separate `total_time` keyword.

### `dt`

Positive nuclear timestep in femtoseconds. Establish nuclear-time-step
convergence for the system and observable of interest.

### `continuity`

`on` is the default and applies the complete A--D numerical-continuity
treatment. Use `manual` only to reproduce or assess a specifically reported
variation. The four numerical situations and every manual control are defined
on [NAMD Numerical Continuity](md-continuity.md).

## Grouped Reference Pages

The remaining options are separated by scientific purpose:

| Page | Contents |
| --- | --- |
| [NAMD Coupling Schemes](md-schemes.md) | `scheme`, `tdc`, `rescale`, `thrshe`, `frustrated`, Baeck--An controls, and optional trivial-crossing following |
| [NAMD Numerical Continuity](md-continuity.md) | Analytic-NAC cases A--D, `continuity=on|manual`, SCF/reference controls, retained-state criterion, substepping, and numerical energy correction |
| [NAMD Diagnostics](md-diagnostics.md) | NACME comparison and NVE energy criteria, including which `error` policies can terminate a run |
| [Initial Conditions and Restart](md-initial-restart.md) | velocity files and units, temperature, random streams, output files of each driver, NAMD and QM/MM MD checkpoint restart, QM/MM phase-space snapshots, and local continuation |
| [Ensembles and experimental SOC-NAMD](md-ensemble-soc.md) | NVE/NVT/NPT, OpenMM restrictions, adaptive timestep, SOC development status, basis, initialization, and force diagnostics |
| [NAMD Advanced Controls](md-advanced.md) | compact index of rarely changed settings and links to the detailed group pages |

## Sectioned `.inp` Compatibility

The concise input above is recommended. Legacy sectioned input places the same
runtime settings in `[md]`; `temperature` and `friction` correspond to
`init_temp`/`thermostat_temperature` and `thermostat_friction` where required
by the legacy spelling. The scientific meaning and defaults are the same.

Legacy `nacme_gate*` and `nve_gate*` names are accepted as aliases for
`nacme_policy*` and `nve_policy*`. New inputs should use `policy`. Do not specify
both spellings for the same setting.

## Python API

The Python API uses the same concise calls and keyword names as `.oqp` input.
For reproducible trajectory ensembles, set `seed` and give each trajectory a
different `rng_stream`. Restart files bind all trajectory-changing controls,
including `scheme`, `continuity`, and the manual A--D settings.
